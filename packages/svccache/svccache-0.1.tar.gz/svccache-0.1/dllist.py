"""
Doubly-linked list class.
"""

class DLL(object):
    """An indexed, doubly-linked list

    >>> l = DLL()
    >>> l
    []
    >>> l.push(1)
    >>> l.push(2)
    >>> l
    [2, 1]
    """
    def __init__(self):
        """
        >>> l = DLL()
        """
        self._first = None
        self._last = None
        self._index = {}
        self._size = 0

    def push(self, k):
        """Push k to the top of the list

        >>> l = DLL()
        >>> l.push(1)
        >>> l
        [1]
        >>> l.push(2)
        >>> l
        [2, 1]
        >>> l.push(3)
        >>> l
        [3, 2, 1]
        """
        if not self._first:
            # first item
            self._first = self._last = node = DLL.Node(k)
        elif self._first.value == k:
            # it's already at the top
            return
        else:
            try:
                self.delete(k) # in case we have it already
            except KeyError:
                pass
            self._first = node = self._first.insert_before(k)
        self._index[k] = node
        self._size += 1

    def delete(self, k):
        """
        >>> l = DLL()
        >>> l.push(1)
        >>> l.delete(1)
        >>> l
        []
        >>> l.push(1)
        >>> l.push(2)
        >>> l.push(3)
        >>> l
        [3, 2, 1]
        >>> l.delete(2)
        >>> l
        [3, 1]
        """
        self.deletenode(self._index[k])

    def deletenode(self, node):
        """
        >>> l = DLL()
        >>> l.push(1)
        >>> l
        [1]
        >>> l.size()
        1
        >>> l.deletenode(l._first)
        >>> l
        []
        >>> l.size()
        0
        >>> l._index
        {}
        >>> l._first
        """
        if self._last == node:
            self._last = node.previous
        if self._first == node:
            self._first = node.next
        node.pop()
        del self._index[node.value]
        self._size -= 1

    def pop(self):
        """
        >>> l = DLL()
        >>> l.push(1)
        >>> l.pop()
        1
        """
        k = self._last.value
        self.deletenode(self._last)
        return k

    def last(self):
        """
        >>> l = DLL()
        >>> l.last()
        """
        return self._last

    def first(self):
        """
        >>> l = DLL()
        >>> l.first()
        """
        return self._first

    def size(self):
        """
        >>> l = DLL()
        >>> l.size()
        0
        """
        return self._size

    def __iter__(self):
        """Return iterator object
        >>> l = DLL()
        >>> [x for x in l]
        []
        >>> for x in xrange(10): l.push(x)
        >>> [x for x in l]
        [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
        """
        return DLL.Iterator(self._first)

    def __str__(self):
        """Returns string representation of the list
        >>> l = DLL()
        >>> str(l)
        '[]'
        >>> for x in xrange(10): l.push(x)
        >>> str(l)
        '[9, 8, 7, 6, 5, 4, 3, 2, 1, 0]'
        """
        return '[' + ', '.join((str(x) for x in self)) + ']'

    def __repr__(self):
        """
        >>> l = DLL()
        >>> repr(l)
        '[]'
        """
        return str(self)

    class Node(object):
        """A doubly-linked list node
        """
        def __init__(self, value):
            """
            >>> n = DLL.Node(1)
            >>> n.value
            1
            >>> n.previous
            >>> n.next
            """
            self.value = value
            self.previous = None
            self.next = None

        def pop(self):
            """Pop self out of linked list. Returns node value.

            >>> n1 = DLL.Node(1)
            >>> n2 = n1.insert_before(2)
            >>> n1.pop()
            1
            >>> n1.previous
            >>> n2.next
            >>> n3 = n2.insert_before(3)
            >>> n4 = n3.insert_before(4)
            >>> n3.pop()
            3
            >>> n2.previous.value
            4
            >>> n4.next.value
            2
            """
            if self.previous:
                self.previous.next = self.next
            if self.next:
                self.next.previous = self.previous
            self.next = self.previous = None
            return self.value

        def insert_before(self, value):
            """Insert value before self. Returns new node object.

            >>> n1 = DLL.Node(1)
            >>> n2 = n1.insert_before(2)
            >>> n1.next
            >>> n1.previous.value
            2
            >>> n3 = n1.insert_before(3)
            >>> n1.previous.value
            3
            >>> n3.previous.value
            2
            >>> n3.next.value
            1
            >>> n2.next.value
            3
            """
            node = DLL.Node(value)
            if self.previous:
                self.previous.next = node
            node.previous = self.previous
            node.next = self
            self.previous = node
            return node

    class Iterator(object):
        """
        Iterator for the DLL

        >>> n1 = DLL.Node(1)
        >>> n2 = n1.insert_before(2)
        >>> n3 = n2.insert_before(3)
        >>> iter = DLL.Iterator(n3)
        >>> [n for n in iter]
        [3, 2, 1]
        """
        def __init__(self, first):
            self.current = first

        def __iter__(self):
            # required by iterator protocol
            return self

        def next(self):
            if not self.current:
                raise StopIteration
            value = self.current.value
            self.current = self.current.next
            return value
