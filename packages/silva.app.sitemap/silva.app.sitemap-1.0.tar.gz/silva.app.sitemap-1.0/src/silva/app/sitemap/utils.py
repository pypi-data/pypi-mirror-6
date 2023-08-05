# -*- coding: utf-8 -*-
# Copyright (c) 2011-2012 Infrae. All rights reserved.
# See also LICENSE.txt


_marker = object()


class TupleMap(object):

    def __init__(self):
        self.clear()

    def clear(self):
        self._store = {}
        self._len = 0

    def add(self, key, value):
        store = self._store
        for piece in key:
            store = store.setdefault(piece, {})
        if None in store:
            # There is already a value in the store.
            raise KeyError(key)
        store[None] = value
        self._len += 1
        return value

    def remove(self, key):
        store = self._store
        components = []

        for piece in key:
            following = store.get(piece)
            if following is None:
                raise KeyError(piece)
            components.append((store, piece))
            store = following
        else:
            if None in store:
                del store[None]
            else:
                raise KeyError(None)
            while components:
                lstore, lkey = components.pop()
                if len(lstore[lkey]) > 0:
                    break
                del lstore[lkey]

    def remove_all(self, key):
        store = self._store
        parent = None
        for piece in key:
            following = store.get(piece)
            if following is None:
                raise KeyError(piece)
            parent = store
            store = following
        else:
            del parent[piece]

    def get(self, key, default=None, fallback=False):
        store = self._store
        default_index = 0
        index = 0

        for index, piece in enumerate(key):
            following = store.get(piece)

            if fallback:
                # Update default if fallback is on
                default_fallback = store.get(None)
                if default_fallback is not None:
                    default = default_fallback
                    default_index = index

            if following is None:
                # Not found, return default.
                return default, default_index

            store = following

        # Look for value or return default.
        value = store.get(None)
        if value is not None:
            return value, index + 1
        return default, default_index

    def list(self):
        result = []

        def walk(level):
            for piece, value in level.iteritems():
                if piece is None:
                    result.append(value)
                else:
                    walk(value)

        walk(self._store)
        return result

    def __getitem__(self, key):
        value = self.get(key, _marker)[0]
        if value is _marker:
            raise KeyError(key)
        return value

    def __len__(self):
        return self._len


# if __name__ == '__main__':

#     from pprint import pprint as pp

#     tm = TupleMap()
#     paths = ['/path/to/something', '/path/to/something/else', '/path/to/nothing']
#     for p in paths:
#         tm.add(p.split('/'), True)
#     pp(tm._store)

#     pp(tm.get('/path/to/something/else/to'.split('/'), fallback=True))
#     pp(tm.get('/path/to'.split('/'), fallback=True))

#     #tm.remove_all('/path/to/something'.split('/'))
#     #pp(tm._store)

