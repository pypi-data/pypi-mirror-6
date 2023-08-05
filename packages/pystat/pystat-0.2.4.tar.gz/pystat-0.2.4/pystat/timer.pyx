from libc.stdlib cimport malloc, free


cdef extern from "stdint.h" nogil:

    ctypedef unsigned int uint32_t
    ctypedef unsigned long uint64_t


cdef extern from "cm_quantile.h":

    ctypedef struct cm_quantile:
        pass


cdef extern from "cm_timer.h":

    ctypedef struct timer:
        uint64_t count
        double sum
        double squared_sum
        int finalized
        cm_quantile cm

    int init_timer(double eps, double *quantiles, uint32_t num_quants, timer *c_timer)
    int destroy_timer(timer *c_timer)

    int timer_add_sample(timer *c_timer, double sample)
    double timer_query(timer *c_timer, double quantile)
    uint64_t timer_count(timer *c_timer)
    double timer_min(timer *c_timer)
    double timer_mean(timer *c_timer)
    double timer_stddev(timer *c_timer)
    double timer_sum(timer *c_timer)
    double timer_squared_sum(timer *c_timer)
    double timer_max(timer *c_timer)


cdef class Timer(object):
    cdef timer *_c_timer
    cdef int _initialized
    cdef object _quantiles
    cdef double *_c_quantiles

    def __cinit__(self, double eps=0.01, object quantiles=None):
        self._initialized = -1
        # These are the quantiles we track
        self._quantiles = tuple(quantiles or [0.5, 0.95, 0.99])
        self._c_quantiles = <double *>malloc(sizeof(double) * len(self._quantiles))
        if self._c_quantiles is NULL:
            raise MemoryError("Can't allocate quantiles")
        for i in range(len(self._quantiles)):
            self._c_quantiles[i] = self._quantiles[i]
        self._c_timer = <timer *>malloc(sizeof(timer))
        if self._c_timer is NULL:
            raise MemoryError("Can't create timer struct")
        self._initialized = init_timer(eps, self._c_quantiles, 3, self._c_timer)
        assert self._initialized == 0

    def add(self, double sample):
        assert timer_add_sample(self._c_timer, sample) == 0
        return self

    def query(self, double quantile=0.95):
        if quantile not in self._quantiles:
            raise ValueError('Unknown quantile "{0!r}" given'.format(quantile))
        return timer_query(self._c_timer, quantile)

    def __int__(self):
        return int(self.sum)

    def __long__(self):
        return long(self.sum)

    def __float__(self):
        return float(self.sum)

    def __len__(self):
        return self.count

    def __iadd__(self, double sample):
        self.add(sample)
        return self

    def __cmp__(self, other):
        if self.sum < other.sum:
            return -1
        elif self.sum == other.sum:
            return 0
        else:
            return 1

    def __repr__(self):
        return ('<{0}(count={2.count}, mean={2.mean}) at {1}>'.
                format(self.__class__.__name__, hex(id(self)), self))

    property quantiles:

        def __get__(self):
            return self._quantiles

    property mean:

        def __get__(self):
            return timer_mean(self._c_timer)

    property stddev:

        def __get__(self):
            return timer_stddev(self._c_timer)

    property sum:

        def __get__(self):
            return timer_sum(self._c_timer)

    property count:

        def __get__(self):
            return timer_count(self._c_timer)

    property squared_sum:

        def __get__(self):
            return timer_squared_sum(self._c_timer)

    property min:

        def __get__(self):
            return timer_min(self._c_timer)

    property max:

        def __get__(self):
            return timer_max(self._c_timer)

    def __dealloc__(self):
        if self._c_timer is not NULL:
            if self._initialized == 0:
                destroy_timer(self._c_timer)
            free(self._c_timer)
        if self._c_quantiles is not NULL:
            free(self._c_quantiles)
