"""
LRU caches

- LRUCache: base class. No constraints. Will grow indefinitely.
- FixedSizeLRUCache: fixed number of entries in the cache.
- MemSizeLRUCache: fixed amount of memory (according to getsize)

Not thread safe. Could be made thread-save easily with a lock
but that's overhead, and if we're not using multi-threading
then why take the hit?
"""

import sys
import dllist

class LRUCache(object):
    def __init__(self, initial_cache=None):
        """
        >>> c = LRUCache()
        >>> c.stats()['size']
        0
        >>> c['key1'] = 'value1'
        >>> c.keys()
        ['key1']
        >>> c['key1']
        'value1'
        >>> del c['key1']
        """
        self._cache = initial_cache or {}
        self._size = 0
        self._hits = 0
        self._misses = 0
        self._order = dllist.DLL()

    def get(self, key):
        """
        >>> c = LRUCache()
        >>> c.get('toto')
        Traceback (most recent call last):
            ...
        KeyError: 'toto'
        >>> c.stats()['misses']
        1
        >>> c.put('toto', 'tata')
        >>> c.get('toto')
        'tata'
        >>> c.stats()['hits']
        1
        """
        try:
            value = self._cache[key]
            self._order.push(key)
            self._hits += 1
            return value
        except KeyError, e:
            self._misses += 1
            raise

    def put(self, key, value):
        """
        >>> c = LRUCache()
        >>> c.put(1, 'one')
        >>> c.get(1)
        'one'
        >>> c.size()
        1
        >>> c.put(2, 'two')
        >>> c.put(3, 'three')
        >>> c.put(4, 'four')
        >>> c.put(5, 'five')
        >>> c.get(5)
        'five'
        >>> c.size()
        5
        """
        self._cache[key] = value
        self._order.push(key)
        self._size += 1

    def delete(self, key):
        """
        >>> c = LRUCache()
        >>> c.put(1, 'one')
        >>> c.get(1)
        'one'
        >>> c.delete(1)
        >>> c.get(1)
        Traceback (most recent call last):
            ...
        KeyError: 1
        >>> c.delete(1)
        Traceback (most recent call last):
            ...
        KeyError: 1
        """
        del self._cache[key]
        self._order.delete(key)
        self._size -= 1

    def list(self):
        """
        >>> c = LRUCache()
        >>> c.put(1, 'one')
        >>> c.put(2, 'two')
        >>> sorted(c.list())
        [1, 2]
        """
        return self._cache.keys()

    def last(self):
        return self._order.last().value

    def size(self):
        """
        >>> c = LRUCache()
        >>> c.size()
        0
        """
        return self._size

    def stats(self):
        """
        >>> c = LRUCache()
        >>> sorted(c.stats().keys())
        ['hits', 'misses', 'size']
        """
        return {'size': self._size, 'hits': self._hits, 'misses': self._misses}

    # Mapping interface
    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        return self.put(key, value)

    def __delitem__(self, key):
        return self.delete(key)

    def keys(self):
        return self.list()


class MemSizeLRUCache(LRUCache):
    """A fixed memory size LRU cache.
    """
    def __init__(self, maxmem=64*1024):
        """
        >>> c = MemSizeLRUCache()
        """
        super(MemSizeLRUCache, self).__init__()
        self._maxmem = maxmem
        self._mem = 0

    def mem(self):
        """
        >>> c = MemSizeLRUCache()
        >>> c.mem()
        0
        """
        return self._mem

    def put(self, key, value):
        """
        >>> c = MemSizeLRUCache(maxmem=24*4)
        >>> c.put(1, 1)
        >>> c.mem() # 24-bytes per integer
        24
        >>> c.put(2, 2)
        >>> c.put(3, 3)
        >>> c.put(4, 4)
        >>> c.get(1)
        1
        >>> c.mem()
        96
        >>> c.size()
        4
        >>> c.put(5, 5)
        >>> c.size()
        4
        >>> c.get(2)
        Traceback (most recent call last):
            ...
        KeyError: 2
        """
        mem = sys.getsizeof(value)
        if self._mem + mem > self._maxmem:
            self.delete(self.last())
        LRUCache.put(self, key, (value, mem))
        self._mem += mem

    def get(self, key):
        (value, _mem) = LRUCache.get(self, key)
        return value

    def delete(self, key):
        """
        >>> c = MemSizeLRUCache()
        >>> c.put(1, 1)
        >>> c.mem()
        24
        >>> c.delete(1)
        >>> c.mem()
        0
        """
        (_value, mem) = LRUCache.get(self, key)
        self._mem -= mem
        LRUCache.delete(self, key)

class FixedSizeLRUCache(LRUCache):
    """LRU cache with maximum number of entries.
    """
    def __init__(self, maxsize=1024):
        super(FixedSizeLRUCache, self).__init__()
        self._maxsize = maxsize

    def put(self, key, value):
        """
        >>> c = FixedSizeLRUCache(maxsize=5)
        >>> c.put(1, 'one')
        >>> c.get(1)
        'one'
        >>> c.size()
        1
        >>> c.put(2, 'two')
        >>> c.put(3, 'three')
        >>> c.put(4, 'four')
        >>> c.put(5, 'five')
        >>> c.get(5)
        'five'
        >>> c.size()
        5
        >>> c.put(6, 'six')
        >>> c.size()
        5
        >>> c.get(1)
        Traceback (most recent call last):
            ...
        KeyError: 1
        >>> c.get(2)
        'two'
        >>> c.put(7, 'seven')
        >>> c.get(2)
        'two'
        >>> c.get(3)
        Traceback (most recent call last):
            ...
        KeyError: 3
        """
        # check if we're maxed out first
        if self.size() == self._maxsize:
            # need to kick something out...
            self.delete(self.last())
        LRUCache.put(self, key, value)

