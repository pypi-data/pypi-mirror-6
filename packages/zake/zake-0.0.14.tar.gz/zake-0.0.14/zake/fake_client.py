# -*- coding: utf-8 -*-

# vim: tabstop=4 shiftwidth=4 softtabstop=4

#    Copyright (C) 2013 Yahoo! Inc. All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import collections
import logging
import os
import time

import six

from kazoo import exceptions as k_exceptions
from kazoo.handlers import threading as k_threading
from kazoo.protocol import paths as k_paths
from kazoo.protocol import states as k_states

from zake import fake_storage as fs
from zake import utils
from zake import version

LOG = logging.getLogger(__name__)

# We provide a basic txn support (not as functional as zookeeper) and this
# was added in 3.4.0 so we will say we are 3.4.0 compat (until proven
# differently).
SERVER_VERSION = (3, 4, 0)


def _make_cb(func, args, type=''):
    return k_states.Callback(type=type, func=func, args=args)


class FakeClient(object):
    """A fake mostly functional/good enough kazoo compat. client

    It can have its underlying storage mocked out (as well as exposes the
    listeners that are currently active and the watches that are currently
    active) so that said functionality can be examined & introspected by
    testing frameworks (while in use and after the fact).
    """

    def __init__(self, handler=None, storage=None, server_version=None):
        self._listeners = set()
        self._watches = collections.defaultdict(list)
        if handler:
            self.handler = handler
        else:
            self.handler = k_threading.SequentialThreadingHandler()
        if storage is not None:
            self.storage = storage
        else:
            self.storage = fs.FakeStorage(lock=self.handler.rlock_object())
        self._lock = self.handler.rlock_object()
        self._connected = False
        if not server_version:
            self._server_version = SERVER_VERSION
        else:
            self._server_version = tuple(server_version)
            if not len(self._server_version):
                raise ValueError("Non-empty server version expected")
        self.expired = False
        self.logger = LOG

    def command(self, cmd=b'ruok'):
        self.verify()
        if cmd == 'ruok':
            return 'imok'
        if cmd == 'stat':
            server_version = ".".join([str(s) for s in SERVER_VERSION])
            return "\n".join(['Zake the fake version: %s' % (version.VERSION),
                              'Mimicked version: %s' % (server_version),
                              'Mode: standalone'])
        if cmd == "kill":
            self.stop()
        return ''

    def verify(self):
        if not self.connected:
            raise k_exceptions.ConnectionClosedError("Connection has been"
                                                     " closed")
        if self.expired:
            raise k_exceptions.SessionExpiredError("Expired")

    @property
    def timeout_exception(self):
        return IOError

    @property
    def watches(self):
        return self._watches

    @property
    def listeners(self):
        return self._listeners

    @property
    def connected(self):
        return self._connected

    def sync(self, path):
        self.verify()
        if not isinstance(path, six.string_types):
            raise TypeError("path must be a string")

    def server_version(self):
        self.verify()
        return self._server_version

    def flush(self):
        self.verify()

        # This puts an item into the callback queue, and waits until it gets
        # called, this is a cheap way of knowing that the queue has been
        # cycled over (as this item goes in on the bottom) and only when the
        # items ahead of this callback are finished will this get called.
        wait_for = self.handler.event_object()
        fired = False

        def flip():
            wait_for.set()

        while not wait_for.is_set():
            if not fired:
                self.handler.dispatch_callback(_make_cb(flip, []))
                fired = True
            time.sleep(0.001)

    def create(self, path, value=b"", acl=None,
               ephemeral=False, sequence=False):
        self.verify()
        if not isinstance(path, six.string_types):
            raise TypeError("path must be a string")
        if not isinstance(value, six.binary_type):
            raise TypeError("value must be a byte string")

        path = k_paths.normpath(path)
        if sequence:
            raise NotImplementedError("Sequencing not currently supported")
        if acl:
            raise NotImplementedError("ACL not currently supported")
        with self.storage.lock:
            if path in self.storage:
                raise k_exceptions.NodeExistsError("Node %s already there"
                                                   % path)
            parent_path = os.path.split(path)[0]
            if parent_path == path and path in self.storage:
                # This is "/" and it already exists.
                return
            elif parent_path == path:
                # This is "/" and it doesn't already exists.
                pass
            elif parent_path not in self.storage:
                raise k_exceptions.NoNodeError("No parent %s" % (parent_path))
            self.storage[path] = {
                # Kazoo clients expect in milliseconds
                'created_on': utils.millitime(),
                'updated_on': utils.millitime(),
                'version': 0,
                # Not supported for now...
                'aversion': -1,
                'cversion': -1,
                'data': value,
            }
            parents = sorted(six.iterkeys(self.storage.get_parents(path)))
        if not parents:
            return

        # Fire any attached watches.
        event = k_states.WatchedEvent(type=k_states.EventType.CREATED,
                                      state=k_states.KeeperState.CONNECTED,
                                      path=path)
        self._fire_watches([parents[-1]], event)
        event = k_states.WatchedEvent(type=k_states.EventType.CHILD,
                                      state=k_states.KeeperState.CONNECTED,
                                      path=path)
        self._fire_watches(parents[0:-1], event)
        return path

    def create_async(self, path, value=b"", acl=None,
                     ephemeral=False, sequence=False):
        return self._generate_async(self.create, path, value=value,
                                    acl=acl, ephemeral=ephemeral,
                                    sequence=sequence)

    def _make_znode(self, path, node):
        child_count = len(self.get_children(path))
        return k_states.ZnodeStat(czxid=-1,
                                  mzxid=-1,
                                  pzxid=-1,
                                  ctime=node['created_on'],
                                  mtime=node['updated_on'],
                                  version=node['version'],
                                  aversion=node['cversion'],
                                  cversion=node['aversion'],
                                  ephemeralOwner=-1,
                                  dataLength=len(node['data']),
                                  numChildren=child_count)

    def get(self, path, watch=None):
        self.verify()
        if not isinstance(path, six.string_types):
            raise TypeError("path must be a string")
        try:
            node = self.storage[path]
        except KeyError:
            raise k_exceptions.NoNodeError("No path %s" % (path))
        if watch:
            self._watches[path].append(watch)
        return (node['data'], self._make_znode(path, node))

    def get_async(self, path, watch=None):
        return self._generate_async(self.get, path, watch=watch)

    def start(self, timeout=None):
        with self._lock:
            if not self._connected:
                self.handler.start()
                self._connected = True
                self._fire_state_change(k_states.KazooState.CONNECTED)

    def _fire_state_change(self, state):
        for func in self._listeners:
            self.handler.dispatch_callback(_make_cb(func, [state]))

    def _generate_async(self, func, *args, **kwargs):
        async_result = self.handler.async_result()

        def run():
            try:
                result = func(*args, **kwargs)
                async_result.set(result)
                return result
            except Exception as exc:
                async_result.set_exception(exc)

        self.handler.dispatch_callback(_make_cb(run, []))
        return async_result

    def exists(self, path, watch=None):
        self.verify()
        if not isinstance(path, six.string_types):
            raise TypeError("path must be a string")

        try:
            return self.get(path, watch=watch)[1]
        except k_exceptions.NoNodeError:
            return None

    def exists_async(self, path, watch=None):
        return self._generate_async(self.exists, path, watch=watch)

    def set(self, path, value, version=-1):
        self.verify()
        if not isinstance(path, six.string_types):
            raise TypeError("path must be a string")
        if not isinstance(value, six.binary_type):
            raise TypeError("value must be a byte string")
        if not isinstance(version, int):
            raise TypeError("version must be an int")

        path = k_paths.normpath(path)
        with self.storage.lock:
            if version != -1:
                (_data, stat) = self.get(path)
                if stat and stat.version != version:
                    raise k_exceptions.BadVersionError("Version mismatch %s "
                                                       "!= %s" % (stat.version,
                                                                  version))
            try:
                self.storage[path]['data'] = value
                self.storage[path]['updated_on'] = utils.millitime()
                self.storage[path]['version'] += 1
            except KeyError:
                raise k_exceptions.NoNodeError("No path %s" % (path))
            parents = sorted(six.iterkeys(self.storage.get_parents(path)))
            (_data, stat) = self.get(path)

        # Fire any attached watches.
        event = k_states.WatchedEvent(type=k_states.EventType.CHANGED,
                                      state=k_states.KeeperState.CONNECTED,
                                      path=path)
        self._fire_watches([path], event)
        event = k_states.WatchedEvent(type=k_states.EventType.CHILD,
                                      state=k_states.KeeperState.CONNECTED,
                                      path=path)
        self._fire_watches(parents, event)
        return stat

    def set_async(self, path, value, version=-1):
        return self._generate_async(self.set, path, value, version=version)

    def get_children(self, path, watch=None, include_data=False):
        self.verify()
        if not isinstance(path, six.string_types):
            raise TypeError("path must be a string")

        def _clean(p):
            return p.strip("/")

        path = k_paths.normpath(path)
        paths = self.storage.get_children(path)
        if watch:
            self._watches[path].append(watch)
        if include_data:
            children_with_data = []
            for (p, data) in six.iteritems(paths):
                children_with_data.append(_clean(p[len(path):]), data)
            return children_with_data
        else:
            children = []
            for p in list(six.iterkeys(paths)):
                children.append(_clean(p[len(path):]))
            return children

    def get_children_async(self, path, watch=None, include_data=False):
        return self._generate_async(self.get_children, path, watch=watch, include_data=include_data)

    def stop(self):
        with self._lock:
            if not self._connected:
                return
            self._fire_state_change(k_states.KazooState.LOST)
            self.handler.stop()
            self._listeners.clear()
            self._watches.clear()
            self._connected = False

    def delete(self, path, recursive=False):
        self.verify()
        if not isinstance(path, six.string_types):
            raise TypeError("path must be a string")

        path = k_paths.normpath(path)
        with self.storage.lock:
            if path not in self.storage:
                raise k_exceptions.NoNodeError("No path %s" % (path))
            if recursive:
                paths = [path]
                for p in six.iterkeys(self.storage.get_children(path)):
                    paths.append(p)
            else:
                paths = [path]
            for p in reversed(sorted(paths)):
                self.storage.pop(p)
                event = k_states.WatchedEvent(
                    type=k_states.EventType.DELETED,
                    state=k_states.KeeperState.CONNECTED,
                    path=p)
                self._fire_watches([p], event)
            return True

    def delete_async(self, path, recursive=False):
        return self._generate_async(self.delete, path, recursive=recursive)

    def add_listener(self, listener):
        self._listeners.add(listener)

    def retry(self, func, *args, **kwargs):
        self.verify()
        return func(*args, **kwargs)

    def remove_listener(self, listener):
        self._listeners.discard(listener)

    def _fire_watches(self, paths, event):
        for p in reversed(sorted(set(paths))):
            watches = list(self._watches.pop(p, []))
            for w in watches:
                self.handler.dispatch_callback(_make_cb(w, [event]))

    def transaction(self):
        return FakeTransactionRequest(self)

    def ensure_path(self, path):
        self.verify()
        if not isinstance(path, six.string_types):
            raise TypeError("path must be a string")

        path = k_paths.normpath(path)
        path_pieces = utils.partition_path(path)
        for p in path_pieces:
            try:
                self.create(p)
            except k_exceptions.NodeExistsError:
                pass

    def close(self):
        self._connected = False


class FakeTransactionRequest(object):
    def __init__(self, client):
        self.client = client
        self.operations = []
        self.committed = False

    def delete(self, path, version=-1):
        self.operations.append((self.client.delete, [path, version]))

    def check(self, path, version):
        raise NotImplementedError("Check not currently supported")

    def set_data(self, path, value, version=-1):
        self.operations.append((self.client.set, [path, value, version]))

    def create(self, path, value=b"", acl=None, ephemeral=False,
               sequence=False):
        self.operations.append((self.client.create,
                                [path, value, acl, ephemeral, sequence]))

    def commit(self):
        if self.committed:
            raise ValueError('Transaction already committed')
        self.committed = True
        results = []
        with self.client.storage.lock:
            self.client.verify()
            for (f, args) in self.operations:
                results.append(f(*args))
            return results

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        if not any((type, value, tb)):
            self.commit()
