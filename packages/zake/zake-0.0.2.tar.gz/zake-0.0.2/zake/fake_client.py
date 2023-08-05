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
import os
import time

import six

from kazoo import exceptions as k_exceptions
from kazoo.handlers import threading as k_threading
from kazoo.protocol import paths as k_paths
from kazoo.protocol import states as k_states


def partition_path(path):
    path_pieces = [path]
    cur_path = path
    while True:
        (b_path, _a) = os.path.split(cur_path)
        if b_path == cur_path:
            path_pieces.append(b_path)
            break
        else:
            path_pieces.append(b_path)
            cur_path = b_path
    return sorted(set(path_pieces))


def _millitime():
    return int(round(time.time() * 1000.0))


def _make_cb(func, args, type=''):
    return k_states.Callback(type=type, func=func, args=args)


def _is_child(parent_path, child_path, only_direct=True):
    parent_pieces = [p for p in parent_path.split("/") if p]
    child_pieces = [p for p in child_path.split("/") if p]
    if len(child_pieces) <= len(parent_pieces):
        return False
    shared_pieces = child_pieces[0:len(parent_pieces)]
    if tuple(parent_pieces) != tuple(shared_pieces):
        return False
    if only_direct:
        return len(child_pieces) == len(parent_pieces) + 1
    return True


class _FakeStorage(object):
    """A place too place fake zookeeper paths + data"""

    def __init__(self, lock, paths=None):
        if paths:
            self._paths = dict(paths)
        else:
            self._paths = {}
        self.lock = lock

    @property
    def paths(self):
        with self.lock:
            return dict(self._paths)

    def pop(self, path):
        with self.lock:
            self._paths.pop(path)

    def __setitem__(self, path, value):
        with self.lock:
            self._paths[path] = value

    def __getitem__(self, path):
        with self.lock:
            return self._paths[path]

    def __contains__(self, path):
        with self.lock:
            return path in self._paths

    def get_children(self, path, only_direct=True):
        paths = {}
        with self.lock:
            for (k, v) in list(six.iteritems(self._paths)):
                if _is_child(path, k, only_direct=only_direct):
                    paths[k] = v
        return paths

    def get_parents(self, path):
        paths = {}
        with self.lock:
            for (k, v) in list(six.iteritems(self._paths)):
                if _is_child(k, path, only_direct=False):
                    paths[k] = v
        return paths


class FakeClient(object):
    """A fake mostly functional/good enough kazoo compat. client

    It can have its underlying storage mocked out (as well as exposes the
    listeners that are currently active and the watches that are currently
    active) so that said functionality can be examined & introspected by
    testing frameworks (while in use and after the fact).
    """

    def __init__(self, handler=None, storage=None):
        self._listeners = set()
        self._watches = collections.defaultdict(list)
        if handler:
            self.handler = handler
        else:
            self.handler = k_threading.SequentialThreadingHandler()
        if storage:
            self.storage = storage
        else:
            self.storage = _FakeStorage(lock=self.handler.rlock_object())
        self._lock = self.handler.rlock_object()
        self._connected = False
        self.expired = False

    def verify(self):
        if not self.connected:
            raise k_exceptions.ConnectionClosedError("Connection has been"
                                                     " closed")
        if self.expired:
            raise k_exceptions.SessionExpiredError()

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

    def create(self, path, value='', ephemeral=False, sequence=False):
        self.verify()
        path = k_paths.normpath(path)
        if sequence:
            raise NotImplementedError("Sequencing not currently supported")
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
                'created_on': _millitime(),
                'updated_on': _millitime(),
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
        path = k_paths.normpath(path)
        try:
            node = self.storage[path]
        except KeyError:
            raise k_exceptions.NoNodeError("No path %s" % (path))
        if watch:
            self._watches[path].append(watch)
        return (node['data'], self._make_znode(path, node))

    def start(self, timeout=None):
        with self._lock:
            if not self._connected:
                self.handler.start()
                self._connected = True
                self._fire_state_change(k_states.KazooState.CONNECTED)

    def _fire_state_change(self, state):
        for func in self._listeners:
            self.handler.dispatch_callback(_make_cb(func, [state]))

    def exists(self, path, watch=None):
        try:
            return self.get(path, watch=watch)[1]
        except k_exceptions.NoNodeError:
            return None

    def set(self, path, value, version=-1):
        self.verify()
        if not isinstance(path, basestring):
            raise TypeError("path must be a string")
        if not isinstance(value, bytes):
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
                self.storage[path]['version'] += 1
            except KeyError:
                raise k_exceptions.NoNodeError("No path %s" % (path))
            parents = sorted(six.iterkeys(self.storage.get_parents(path)))

        # Fire any attached watches.
        event = k_states.WatchedEvent(type=k_states.EventType.CHANGED,
                                      state=k_states.KeeperState.CONNECTED,
                                      path=path)
        self._fire_watches([path], event)
        event = k_states.WatchedEvent(type=k_states.EventType.CHILD,
                                      state=k_states.KeeperState.CONNECTED,
                                      path=path)
        self._fire_watches(parents, event)

    def get_children(self, path, watch=None, include_data=False):
        self.verify()

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

    def ensure_path(self, path):
        self.verify()
        path = k_paths.normpath(path)
        path_pieces = partition_path(path)
        for p in path_pieces:
            try:
                self.create(p)
            except k_exceptions.NodeExistsError:
                pass
