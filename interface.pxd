cdef extern from "./rank.hpp":
    cdef cppclass Ranking:
        float rank
        int ID
        Ranking()
        Ranking(float, int)

cdef extern from "./minmaxheap.hpp" namespace "heap":
    cdef cppclass LimitedMaxHeap[T]:
        LimitedMaxHeap(int)
        void insert(T)
        T get_max()
        int size()