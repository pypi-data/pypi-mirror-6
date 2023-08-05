cimport cython


cdef extern from "stdint.h" nogil:

    ctypedef unsigned long uint64_t


def recreate_counter(object count):
    """Restore pickled counter."""
    cdef PlainCounter c = PlainCounter()
    c.load(count)
    return c


@cython.freelist(8)
cdef class PlainCounter(object):
    cdef uint64_t _count

    def __cinit__(self):
        self._count = 0

    def __init__(self, l=None):
        if l is not None:
            self.update(l)

    cpdef add(self):
        self._count += 1
        return self

    cpdef update(self, l):
        self._count += len(l)
        return self

    cpdef object dump(self):
        return self._count

    cpdef load(self, object count):
        self._count = count
        return self

    def union(self, PlainCounter other):
        """Return union of two counters."""
        cdef PlainCounter c = PlainCounter()
        c._count = self._count + other._count
        return c

    def __or__(self, PlainCounter other):
        return self.union(other)

    def __len__(self):
        cdef object count = self._count
        return count

    def __reduce__(self):
        return (recreate_counter, (self.dump(), ))

    def __repr__(self):
        return ('<{0}(count={2.count}) at {1}>'.
                format(self.__class__.__name__, hex(id(self)), self))

    property count:

        def __get__(self):
            return self._count
