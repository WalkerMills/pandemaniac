cimport interface

cdef class rank_heap:

    cdef interface.LimitedMaxHeap[interface.Ranking] *thisptr

    def __cinit__(self, int capacity):
        self.thisptr = new interface.LimitedMaxHeap[interface.Ranking](capacity)
    def __dealloc__(self):
        del self.thisptr

    def insert(self, float rank, int ID):
        cdef interface.Ranking new_rank = interface.Ranking(rank, ID)
        self.thisptr.insert(new_rank)

    def get_max(self):
        cdef interface.Ranking maximum = self.thisptr.get_max()
        return maximum.ID, maximum.rank

    def size(self):
        return self.thisptr.size()