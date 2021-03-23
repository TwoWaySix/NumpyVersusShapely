from cython cimport boundscheck, wraparound

@boundscheck(False)
@wraparound(False)
cpdef int cy_assign_polyid(long[:] pntids, long[:] pnt_assign_polyid, long polyid):
    cdef int i = 0
    
    for i in range(pntids.shape[0]):
        pnt_assign_polyid[pntids[i]] = polyid

    return 0