"move_nanmean auto-generated from template"

def move_nanmean(arr, int window, int axis=-1):
    """
    Moving window mean along the specified axis, ignoring NaNs.

    Parameters
    ----------
    arr : ndarray
        Input array.
    window : int
        The number of elements in the moving window.
    axis : int, optional
        The axis over which to perform the moving mean. By default the moving
        mean is taken over the last axis (axis=-1). An axis of None is not
        allowed.

    Returns
    -------
    y : ndarray
        The moving mean of the input array along the specified axis. The output
        has the same shape as the input.

    Examples
    --------
    >>> arr = np.array([1.0, 2.0, 3.0, 4.0])
    >>> bn.move_nanmean(arr, window=2)
    array([ nan,  1.5,  2.5,  3.5])

    """
    func, arr = move_nanmean_selector(arr, axis)
    return func(arr, window)

def move_nanmean_selector(arr, int axis):
    """
    Return move_nanmean function and array that matches `arr` and `axis`.

    Under the hood Bottleneck uses a separate Cython function for each
    combination of ndim, dtype, and axis. A lot of the overhead in
    bn.move_nanmean() is in checking that `axis` is within range, converting
    `arr` into an array (if it is not already an array), and selecting the
    function to use to calculate the moving mean.

    You can get rid of the overhead by doing all this before you, for example,
    enter an inner loop, by using this function.

    Parameters
    ----------
    arr : array_like
        Input array. If `arr` is not an array, a conversion is attempted.
    axis : {int, None}
        Axis along which the moving mean is to be computed.

    Returns
    -------
    func : function
        The moving nanmean function that matches the number of dimensions,
        dtype, and the axis along which you wish to find the mean.
    a : ndarray
        If the input array `arr` is not a ndarray, then `a` will contain the
        result of converting `arr` into a ndarray otherwise a view is
        returned.

    Examples
    --------
    Create a numpy array:

    >>> arr = np.array([1.0, 2.0, 3.0, 4.0])

    Obtain the function needed to determine the sum of `arr` along axis=0:

    >>> window, axis = 2, 0
    >>> func, a = bn.move.move_nanmean_selector(arr, axis)
    >>> func
    <function move_nanmean_1d_float64_axis0>

    Use the returned function and array to determine the moving mean:

    >>> func(a, window)
    array([ nan,  1.5,  2.5,  3.5])

    """
    cdef np.ndarray a
    if type(arr) is np.ndarray:
        a = arr
    else:
        a = np.array(arr, copy=False)
    cdef int ndim = PyArray_NDIM(a)
    cdef int dtype = PyArray_TYPE(a)
    if axis < 0:
        axis += ndim
    cdef tuple key = (ndim, dtype, axis)
    try:
        func = move_nanmean_dict[key]
    except KeyError:
        if (axis < 0) or (axis >= ndim):
            raise ValueError("axis(=%d) out of bounds" % axis)
        try:
            func = move_nanmean_slow_dict[axis]
        except KeyError:
            tup = (str(ndim), str(a.dtype), str(axis))
            raise TypeError("Unsupported ndim/dtype/axis (%s/%s/%s)." % tup)
    return func, a

@cython.boundscheck(False)
@cython.wraparound(False)
def move_nanmean_1d_float32_axis0(np.ndarray[np.float32_t, ndim=1] a,
                                  int window):
    "Moving mean of 1d array of dtype=float32 along axis=0 ignoring NaNs."
    cdef Py_ssize_t count = 0
    cdef double asum = 0, aold, ai
    cdef Py_ssize_t i0
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef np.npy_intp *dims = [n0]
    cdef np.ndarray[np.float32_t, ndim=1] y = PyArray_EMPTY(1, dims,
		NPY_float32, 0)
    if (window < 1) or (window > n0):
        raise ValueError(MOVE_WINDOW_ERR_MSG % (window, n0))

    for i0 in range(window - 1):
        ai = a[i0]
        if ai == ai:
            asum += ai
            count += 1
        y[i0] = NAN
    i0 = window - 1
    ai = a[i0]
    if ai == ai:
        asum += ai
        count += 1
    if count > 0:
       y[i0] = asum / count
    else:
       y[i0] = NAN
    for i0 in range(window, n0):
        ai = a[i0]
        if ai == ai:
            asum += ai
            count += 1
        aold = a[i0 - window]
        if aold == aold:
            asum -= aold
            count -= 1
        if count > 0:
            y[i0] = asum / count
        else:
            y[i0] = NAN

    return y

@cython.boundscheck(False)
@cython.wraparound(False)
def move_nanmean_1d_float64_axis0(np.ndarray[np.float64_t, ndim=1] a,
                                  int window):
    "Moving mean of 1d array of dtype=float64 along axis=0 ignoring NaNs."
    cdef Py_ssize_t count = 0
    cdef double asum = 0, aold, ai
    cdef Py_ssize_t i0
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef np.npy_intp *dims = [n0]
    cdef np.ndarray[np.float64_t, ndim=1] y = PyArray_EMPTY(1, dims,
		NPY_float64, 0)
    if (window < 1) or (window > n0):
        raise ValueError(MOVE_WINDOW_ERR_MSG % (window, n0))

    for i0 in range(window - 1):
        ai = a[i0]
        if ai == ai:
            asum += ai
            count += 1
        y[i0] = NAN
    i0 = window - 1
    ai = a[i0]
    if ai == ai:
        asum += ai
        count += 1
    if count > 0:
       y[i0] = asum / count
    else:
       y[i0] = NAN
    for i0 in range(window, n0):
        ai = a[i0]
        if ai == ai:
            asum += ai
            count += 1
        aold = a[i0 - window]
        if aold == aold:
            asum -= aold
            count -= 1
        if count > 0:
            y[i0] = asum / count
        else:
            y[i0] = NAN

    return y

@cython.boundscheck(False)
@cython.wraparound(False)
def move_nanmean_2d_float32_axis0(np.ndarray[np.float32_t, ndim=2] a,
                                  int window):
    "Moving mean of 2d array of dtype=float32 along axis=0 ignoring NaNs."
    cdef Py_ssize_t count = 0
    cdef double asum = 0, aold, ai
    cdef Py_ssize_t i0, i1
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    cdef np.npy_intp *dims = [n0, n1]
    cdef np.ndarray[np.float32_t, ndim=2] y = PyArray_EMPTY(2, dims,
		NPY_float32, 0)
    if (window < 1) or (window > n0):
        raise ValueError(MOVE_WINDOW_ERR_MSG % (window, n0))

    for i1 in range(n1):
        asum = 0
        count = 0
        for i0 in range(window - 1):
            ai = a[i0, i1]
            if ai == ai:
                asum += ai
                count += 1
            y[i0, i1] = NAN
        i0 = window - 1
        ai = a[i0, i1]
        if ai == ai:
            asum += ai
            count += 1
        if count > 0:
           y[i0, i1] = asum / count
        else:
           y[i0, i1] = NAN
        for i0 in range(window, n0):
            ai = a[i0, i1]
            if ai == ai:
                asum += ai
                count += 1
            aold = a[i0 - window, i1]
            if aold == aold:
                asum -= aold
                count -= 1
            if count > 0:
                y[i0, i1] = asum / count
            else:
                y[i0, i1] = NAN

    return y

@cython.boundscheck(False)
@cython.wraparound(False)
def move_nanmean_2d_float32_axis1(np.ndarray[np.float32_t, ndim=2] a,
                                  int window):
    "Moving mean of 2d array of dtype=float32 along axis=1 ignoring NaNs."
    cdef Py_ssize_t count = 0
    cdef double asum = 0, aold, ai
    cdef Py_ssize_t i0, i1
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    cdef np.npy_intp *dims = [n0, n1]
    cdef np.ndarray[np.float32_t, ndim=2] y = PyArray_EMPTY(2, dims,
		NPY_float32, 0)
    if (window < 1) or (window > n1):
        raise ValueError(MOVE_WINDOW_ERR_MSG % (window, n1))

    for i0 in range(n0):
        asum = 0
        count = 0
        for i1 in range(window - 1):
            ai = a[i0, i1]
            if ai == ai:
                asum += ai
                count += 1
            y[i0, i1] = NAN
        i1 = window - 1
        ai = a[i0, i1]
        if ai == ai:
            asum += ai
            count += 1
        if count > 0:
           y[i0, i1] = asum / count
        else:
           y[i0, i1] = NAN
        for i1 in range(window, n1):
            ai = a[i0, i1]
            if ai == ai:
                asum += ai
                count += 1
            aold = a[i0, i1 - window]
            if aold == aold:
                asum -= aold
                count -= 1
            if count > 0:
                y[i0, i1] = asum / count
            else:
                y[i0, i1] = NAN

    return y

@cython.boundscheck(False)
@cython.wraparound(False)
def move_nanmean_2d_float64_axis0(np.ndarray[np.float64_t, ndim=2] a,
                                  int window):
    "Moving mean of 2d array of dtype=float64 along axis=0 ignoring NaNs."
    cdef Py_ssize_t count = 0
    cdef double asum = 0, aold, ai
    cdef Py_ssize_t i0, i1
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    cdef np.npy_intp *dims = [n0, n1]
    cdef np.ndarray[np.float64_t, ndim=2] y = PyArray_EMPTY(2, dims,
		NPY_float64, 0)
    if (window < 1) or (window > n0):
        raise ValueError(MOVE_WINDOW_ERR_MSG % (window, n0))

    for i1 in range(n1):
        asum = 0
        count = 0
        for i0 in range(window - 1):
            ai = a[i0, i1]
            if ai == ai:
                asum += ai
                count += 1
            y[i0, i1] = NAN
        i0 = window - 1
        ai = a[i0, i1]
        if ai == ai:
            asum += ai
            count += 1
        if count > 0:
           y[i0, i1] = asum / count
        else:
           y[i0, i1] = NAN
        for i0 in range(window, n0):
            ai = a[i0, i1]
            if ai == ai:
                asum += ai
                count += 1
            aold = a[i0 - window, i1]
            if aold == aold:
                asum -= aold
                count -= 1
            if count > 0:
                y[i0, i1] = asum / count
            else:
                y[i0, i1] = NAN

    return y

@cython.boundscheck(False)
@cython.wraparound(False)
def move_nanmean_2d_float64_axis1(np.ndarray[np.float64_t, ndim=2] a,
                                  int window):
    "Moving mean of 2d array of dtype=float64 along axis=1 ignoring NaNs."
    cdef Py_ssize_t count = 0
    cdef double asum = 0, aold, ai
    cdef Py_ssize_t i0, i1
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    cdef np.npy_intp *dims = [n0, n1]
    cdef np.ndarray[np.float64_t, ndim=2] y = PyArray_EMPTY(2, dims,
		NPY_float64, 0)
    if (window < 1) or (window > n1):
        raise ValueError(MOVE_WINDOW_ERR_MSG % (window, n1))

    for i0 in range(n0):
        asum = 0
        count = 0
        for i1 in range(window - 1):
            ai = a[i0, i1]
            if ai == ai:
                asum += ai
                count += 1
            y[i0, i1] = NAN
        i1 = window - 1
        ai = a[i0, i1]
        if ai == ai:
            asum += ai
            count += 1
        if count > 0:
           y[i0, i1] = asum / count
        else:
           y[i0, i1] = NAN
        for i1 in range(window, n1):
            ai = a[i0, i1]
            if ai == ai:
                asum += ai
                count += 1
            aold = a[i0, i1 - window]
            if aold == aold:
                asum -= aold
                count -= 1
            if count > 0:
                y[i0, i1] = asum / count
            else:
                y[i0, i1] = NAN

    return y

@cython.boundscheck(False)
@cython.wraparound(False)
def move_nanmean_3d_float32_axis0(np.ndarray[np.float32_t, ndim=3] a,
                                  int window):
    "Moving mean of 3d array of dtype=float32 along axis=0 ignoring NaNs."
    cdef Py_ssize_t count = 0
    cdef double asum = 0, aold, ai
    cdef Py_ssize_t i0, i1, i2
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    cdef Py_ssize_t n2 = dim[2]
    cdef np.npy_intp *dims = [n0, n1, n2]
    cdef np.ndarray[np.float32_t, ndim=3] y = PyArray_EMPTY(3, dims,
		NPY_float32, 0)
    if (window < 1) or (window > n0):
        raise ValueError(MOVE_WINDOW_ERR_MSG % (window, n0))

    for i1 in range(n1):
        for i2 in range(n2):
            asum = 0
            count = 0
            for i0 in range(window - 1):
                ai = a[i0, i1, i2]
                if ai == ai:
                    asum += ai
                    count += 1
                y[i0, i1, i2] = NAN
            i0 = window - 1
            ai = a[i0, i1, i2]
            if ai == ai:
                asum += ai
                count += 1
            if count > 0:
               y[i0, i1, i2] = asum / count
            else:
               y[i0, i1, i2] = NAN
            for i0 in range(window, n0):
                ai = a[i0, i1, i2]
                if ai == ai:
                    asum += ai
                    count += 1
                aold = a[i0 - window, i1, i2]
                if aold == aold:
                    asum -= aold
                    count -= 1
                if count > 0:
                    y[i0, i1, i2] = asum / count
                else:
                    y[i0, i1, i2] = NAN

    return y

@cython.boundscheck(False)
@cython.wraparound(False)
def move_nanmean_3d_float32_axis1(np.ndarray[np.float32_t, ndim=3] a,
                                  int window):
    "Moving mean of 3d array of dtype=float32 along axis=1 ignoring NaNs."
    cdef Py_ssize_t count = 0
    cdef double asum = 0, aold, ai
    cdef Py_ssize_t i0, i1, i2
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    cdef Py_ssize_t n2 = dim[2]
    cdef np.npy_intp *dims = [n0, n1, n2]
    cdef np.ndarray[np.float32_t, ndim=3] y = PyArray_EMPTY(3, dims,
		NPY_float32, 0)
    if (window < 1) or (window > n1):
        raise ValueError(MOVE_WINDOW_ERR_MSG % (window, n1))

    for i0 in range(n0):
        for i2 in range(n2):
            asum = 0
            count = 0
            for i1 in range(window - 1):
                ai = a[i0, i1, i2]
                if ai == ai:
                    asum += ai
                    count += 1
                y[i0, i1, i2] = NAN
            i1 = window - 1
            ai = a[i0, i1, i2]
            if ai == ai:
                asum += ai
                count += 1
            if count > 0:
               y[i0, i1, i2] = asum / count
            else:
               y[i0, i1, i2] = NAN
            for i1 in range(window, n1):
                ai = a[i0, i1, i2]
                if ai == ai:
                    asum += ai
                    count += 1
                aold = a[i0, i1 - window, i2]
                if aold == aold:
                    asum -= aold
                    count -= 1
                if count > 0:
                    y[i0, i1, i2] = asum / count
                else:
                    y[i0, i1, i2] = NAN

    return y

@cython.boundscheck(False)
@cython.wraparound(False)
def move_nanmean_3d_float32_axis2(np.ndarray[np.float32_t, ndim=3] a,
                                  int window):
    "Moving mean of 3d array of dtype=float32 along axis=2 ignoring NaNs."
    cdef Py_ssize_t count = 0
    cdef double asum = 0, aold, ai
    cdef Py_ssize_t i0, i1, i2
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    cdef Py_ssize_t n2 = dim[2]
    cdef np.npy_intp *dims = [n0, n1, n2]
    cdef np.ndarray[np.float32_t, ndim=3] y = PyArray_EMPTY(3, dims,
		NPY_float32, 0)
    if (window < 1) or (window > n2):
        raise ValueError(MOVE_WINDOW_ERR_MSG % (window, n2))

    for i0 in range(n0):
        for i1 in range(n1):
            asum = 0
            count = 0
            for i2 in range(window - 1):
                ai = a[i0, i1, i2]
                if ai == ai:
                    asum += ai
                    count += 1
                y[i0, i1, i2] = NAN
            i2 = window - 1
            ai = a[i0, i1, i2]
            if ai == ai:
                asum += ai
                count += 1
            if count > 0:
               y[i0, i1, i2] = asum / count
            else:
               y[i0, i1, i2] = NAN
            for i2 in range(window, n2):
                ai = a[i0, i1, i2]
                if ai == ai:
                    asum += ai
                    count += 1
                aold = a[i0, i1, i2 - window]
                if aold == aold:
                    asum -= aold
                    count -= 1
                if count > 0:
                    y[i0, i1, i2] = asum / count
                else:
                    y[i0, i1, i2] = NAN

    return y

@cython.boundscheck(False)
@cython.wraparound(False)
def move_nanmean_3d_float64_axis0(np.ndarray[np.float64_t, ndim=3] a,
                                  int window):
    "Moving mean of 3d array of dtype=float64 along axis=0 ignoring NaNs."
    cdef Py_ssize_t count = 0
    cdef double asum = 0, aold, ai
    cdef Py_ssize_t i0, i1, i2
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    cdef Py_ssize_t n2 = dim[2]
    cdef np.npy_intp *dims = [n0, n1, n2]
    cdef np.ndarray[np.float64_t, ndim=3] y = PyArray_EMPTY(3, dims,
		NPY_float64, 0)
    if (window < 1) or (window > n0):
        raise ValueError(MOVE_WINDOW_ERR_MSG % (window, n0))

    for i1 in range(n1):
        for i2 in range(n2):
            asum = 0
            count = 0
            for i0 in range(window - 1):
                ai = a[i0, i1, i2]
                if ai == ai:
                    asum += ai
                    count += 1
                y[i0, i1, i2] = NAN
            i0 = window - 1
            ai = a[i0, i1, i2]
            if ai == ai:
                asum += ai
                count += 1
            if count > 0:
               y[i0, i1, i2] = asum / count
            else:
               y[i0, i1, i2] = NAN
            for i0 in range(window, n0):
                ai = a[i0, i1, i2]
                if ai == ai:
                    asum += ai
                    count += 1
                aold = a[i0 - window, i1, i2]
                if aold == aold:
                    asum -= aold
                    count -= 1
                if count > 0:
                    y[i0, i1, i2] = asum / count
                else:
                    y[i0, i1, i2] = NAN

    return y

@cython.boundscheck(False)
@cython.wraparound(False)
def move_nanmean_3d_float64_axis1(np.ndarray[np.float64_t, ndim=3] a,
                                  int window):
    "Moving mean of 3d array of dtype=float64 along axis=1 ignoring NaNs."
    cdef Py_ssize_t count = 0
    cdef double asum = 0, aold, ai
    cdef Py_ssize_t i0, i1, i2
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    cdef Py_ssize_t n2 = dim[2]
    cdef np.npy_intp *dims = [n0, n1, n2]
    cdef np.ndarray[np.float64_t, ndim=3] y = PyArray_EMPTY(3, dims,
		NPY_float64, 0)
    if (window < 1) or (window > n1):
        raise ValueError(MOVE_WINDOW_ERR_MSG % (window, n1))

    for i0 in range(n0):
        for i2 in range(n2):
            asum = 0
            count = 0
            for i1 in range(window - 1):
                ai = a[i0, i1, i2]
                if ai == ai:
                    asum += ai
                    count += 1
                y[i0, i1, i2] = NAN
            i1 = window - 1
            ai = a[i0, i1, i2]
            if ai == ai:
                asum += ai
                count += 1
            if count > 0:
               y[i0, i1, i2] = asum / count
            else:
               y[i0, i1, i2] = NAN
            for i1 in range(window, n1):
                ai = a[i0, i1, i2]
                if ai == ai:
                    asum += ai
                    count += 1
                aold = a[i0, i1 - window, i2]
                if aold == aold:
                    asum -= aold
                    count -= 1
                if count > 0:
                    y[i0, i1, i2] = asum / count
                else:
                    y[i0, i1, i2] = NAN

    return y

@cython.boundscheck(False)
@cython.wraparound(False)
def move_nanmean_3d_float64_axis2(np.ndarray[np.float64_t, ndim=3] a,
                                  int window):
    "Moving mean of 3d array of dtype=float64 along axis=2 ignoring NaNs."
    cdef Py_ssize_t count = 0
    cdef double asum = 0, aold, ai
    cdef Py_ssize_t i0, i1, i2
    cdef np.npy_intp *dim
    dim = PyArray_DIMS(a)
    cdef Py_ssize_t n0 = dim[0]
    cdef Py_ssize_t n1 = dim[1]
    cdef Py_ssize_t n2 = dim[2]
    cdef np.npy_intp *dims = [n0, n1, n2]
    cdef np.ndarray[np.float64_t, ndim=3] y = PyArray_EMPTY(3, dims,
		NPY_float64, 0)
    if (window < 1) or (window > n2):
        raise ValueError(MOVE_WINDOW_ERR_MSG % (window, n2))

    for i0 in range(n0):
        for i1 in range(n1):
            asum = 0
            count = 0
            for i2 in range(window - 1):
                ai = a[i0, i1, i2]
                if ai == ai:
                    asum += ai
                    count += 1
                y[i0, i1, i2] = NAN
            i2 = window - 1
            ai = a[i0, i1, i2]
            if ai == ai:
                asum += ai
                count += 1
            if count > 0:
               y[i0, i1, i2] = asum / count
            else:
               y[i0, i1, i2] = NAN
            for i2 in range(window, n2):
                ai = a[i0, i1, i2]
                if ai == ai:
                    asum += ai
                    count += 1
                aold = a[i0, i1, i2 - window]
                if aold == aold:
                    asum -= aold
                    count -= 1
                if count > 0:
                    y[i0, i1, i2] = asum / count
                else:
                    y[i0, i1, i2] = NAN

    return y

cdef dict move_nanmean_dict = {}
move_nanmean_dict[(1, NPY_int32, 0)] = move_mean_1d_int32_axis0
move_nanmean_dict[(1, NPY_int64, 0)] = move_mean_1d_int64_axis0
move_nanmean_dict[(2, NPY_int32, 0)] = move_mean_2d_int32_axis0
move_nanmean_dict[(2, NPY_int32, 1)] = move_mean_2d_int32_axis1
move_nanmean_dict[(2, NPY_int64, 0)] = move_mean_2d_int64_axis0
move_nanmean_dict[(2, NPY_int64, 1)] = move_mean_2d_int64_axis1
move_nanmean_dict[(3, NPY_int32, 0)] = move_mean_3d_int32_axis0
move_nanmean_dict[(3, NPY_int32, 1)] = move_mean_3d_int32_axis1
move_nanmean_dict[(3, NPY_int32, 2)] = move_mean_3d_int32_axis2
move_nanmean_dict[(3, NPY_int64, 0)] = move_mean_3d_int64_axis0
move_nanmean_dict[(3, NPY_int64, 1)] = move_mean_3d_int64_axis1
move_nanmean_dict[(3, NPY_int64, 2)] = move_mean_3d_int64_axis2
move_nanmean_dict[(1, NPY_float32, 0)] = move_nanmean_1d_float32_axis0
move_nanmean_dict[(1, NPY_float64, 0)] = move_nanmean_1d_float64_axis0
move_nanmean_dict[(2, NPY_float32, 0)] = move_nanmean_2d_float32_axis0
move_nanmean_dict[(2, NPY_float32, 1)] = move_nanmean_2d_float32_axis1
move_nanmean_dict[(2, NPY_float64, 0)] = move_nanmean_2d_float64_axis0
move_nanmean_dict[(2, NPY_float64, 1)] = move_nanmean_2d_float64_axis1
move_nanmean_dict[(3, NPY_float32, 0)] = move_nanmean_3d_float32_axis0
move_nanmean_dict[(3, NPY_float32, 1)] = move_nanmean_3d_float32_axis1
move_nanmean_dict[(3, NPY_float32, 2)] = move_nanmean_3d_float32_axis2
move_nanmean_dict[(3, NPY_float64, 0)] = move_nanmean_3d_float64_axis0
move_nanmean_dict[(3, NPY_float64, 1)] = move_nanmean_3d_float64_axis1
move_nanmean_dict[(3, NPY_float64, 2)] = move_nanmean_3d_float64_axis2

def move_nanmean_slow_axis0(arr, window):
    "Unaccelerated (slow) move_nanmean along axis 0."
    return bn.slow.move_nanmean(arr, window, axis=0)

def move_nanmean_slow_axis1(arr, window):
    "Unaccelerated (slow) move_nanmean along axis 1."
    return bn.slow.move_nanmean(arr, window, axis=1)

def move_nanmean_slow_axis2(arr, window):
    "Unaccelerated (slow) move_nanmean along axis 2."
    return bn.slow.move_nanmean(arr, window, axis=2)

def move_nanmean_slow_axis3(arr, window):
    "Unaccelerated (slow) move_nanmean along axis 3."
    return bn.slow.move_nanmean(arr, window, axis=3)

def move_nanmean_slow_axis4(arr, window):
    "Unaccelerated (slow) move_nanmean along axis 4."
    return bn.slow.move_nanmean(arr, window, axis=4)

def move_nanmean_slow_axis5(arr, window):
    "Unaccelerated (slow) move_nanmean along axis 5."
    return bn.slow.move_nanmean(arr, window, axis=5)

def move_nanmean_slow_axis6(arr, window):
    "Unaccelerated (slow) move_nanmean along axis 6."
    return bn.slow.move_nanmean(arr, window, axis=6)

def move_nanmean_slow_axis7(arr, window):
    "Unaccelerated (slow) move_nanmean along axis 7."
    return bn.slow.move_nanmean(arr, window, axis=7)

def move_nanmean_slow_axis8(arr, window):
    "Unaccelerated (slow) move_nanmean along axis 8."
    return bn.slow.move_nanmean(arr, window, axis=8)

def move_nanmean_slow_axis9(arr, window):
    "Unaccelerated (slow) move_nanmean along axis 9."
    return bn.slow.move_nanmean(arr, window, axis=9)

def move_nanmean_slow_axis10(arr, window):
    "Unaccelerated (slow) move_nanmean along axis 10."
    return bn.slow.move_nanmean(arr, window, axis=10)

def move_nanmean_slow_axis11(arr, window):
    "Unaccelerated (slow) move_nanmean along axis 11."
    return bn.slow.move_nanmean(arr, window, axis=11)

def move_nanmean_slow_axis12(arr, window):
    "Unaccelerated (slow) move_nanmean along axis 12."
    return bn.slow.move_nanmean(arr, window, axis=12)

def move_nanmean_slow_axis13(arr, window):
    "Unaccelerated (slow) move_nanmean along axis 13."
    return bn.slow.move_nanmean(arr, window, axis=13)

def move_nanmean_slow_axis14(arr, window):
    "Unaccelerated (slow) move_nanmean along axis 14."
    return bn.slow.move_nanmean(arr, window, axis=14)

def move_nanmean_slow_axis15(arr, window):
    "Unaccelerated (slow) move_nanmean along axis 15."
    return bn.slow.move_nanmean(arr, window, axis=15)

def move_nanmean_slow_axis16(arr, window):
    "Unaccelerated (slow) move_nanmean along axis 16."
    return bn.slow.move_nanmean(arr, window, axis=16)

def move_nanmean_slow_axis17(arr, window):
    "Unaccelerated (slow) move_nanmean along axis 17."
    return bn.slow.move_nanmean(arr, window, axis=17)

def move_nanmean_slow_axis18(arr, window):
    "Unaccelerated (slow) move_nanmean along axis 18."
    return bn.slow.move_nanmean(arr, window, axis=18)

def move_nanmean_slow_axis19(arr, window):
    "Unaccelerated (slow) move_nanmean along axis 19."
    return bn.slow.move_nanmean(arr, window, axis=19)

def move_nanmean_slow_axis20(arr, window):
    "Unaccelerated (slow) move_nanmean along axis 20."
    return bn.slow.move_nanmean(arr, window, axis=20)

def move_nanmean_slow_axis21(arr, window):
    "Unaccelerated (slow) move_nanmean along axis 21."
    return bn.slow.move_nanmean(arr, window, axis=21)

def move_nanmean_slow_axis22(arr, window):
    "Unaccelerated (slow) move_nanmean along axis 22."
    return bn.slow.move_nanmean(arr, window, axis=22)

def move_nanmean_slow_axis23(arr, window):
    "Unaccelerated (slow) move_nanmean along axis 23."
    return bn.slow.move_nanmean(arr, window, axis=23)

def move_nanmean_slow_axis24(arr, window):
    "Unaccelerated (slow) move_nanmean along axis 24."
    return bn.slow.move_nanmean(arr, window, axis=24)

def move_nanmean_slow_axis25(arr, window):
    "Unaccelerated (slow) move_nanmean along axis 25."
    return bn.slow.move_nanmean(arr, window, axis=25)

def move_nanmean_slow_axis26(arr, window):
    "Unaccelerated (slow) move_nanmean along axis 26."
    return bn.slow.move_nanmean(arr, window, axis=26)

def move_nanmean_slow_axis27(arr, window):
    "Unaccelerated (slow) move_nanmean along axis 27."
    return bn.slow.move_nanmean(arr, window, axis=27)

def move_nanmean_slow_axis28(arr, window):
    "Unaccelerated (slow) move_nanmean along axis 28."
    return bn.slow.move_nanmean(arr, window, axis=28)

def move_nanmean_slow_axis29(arr, window):
    "Unaccelerated (slow) move_nanmean along axis 29."
    return bn.slow.move_nanmean(arr, window, axis=29)

def move_nanmean_slow_axis30(arr, window):
    "Unaccelerated (slow) move_nanmean along axis 30."
    return bn.slow.move_nanmean(arr, window, axis=30)

def move_nanmean_slow_axis31(arr, window):
    "Unaccelerated (slow) move_nanmean along axis 31."
    return bn.slow.move_nanmean(arr, window, axis=31)

def move_nanmean_slow_axis32(arr, window):
    "Unaccelerated (slow) move_nanmean along axis 32."
    return bn.slow.move_nanmean(arr, window, axis=32)

def move_nanmean_slow_axisNone(arr, window):
    "Unaccelerated (slow) move_nanmean along axis None."
    return bn.slow.move_nanmean(arr, window, axis=None)


cdef dict move_nanmean_slow_dict = {}
move_nanmean_slow_dict[0] = move_nanmean_slow_axis0
move_nanmean_slow_dict[1] = move_nanmean_slow_axis1
move_nanmean_slow_dict[2] = move_nanmean_slow_axis2
move_nanmean_slow_dict[3] = move_nanmean_slow_axis3
move_nanmean_slow_dict[4] = move_nanmean_slow_axis4
move_nanmean_slow_dict[5] = move_nanmean_slow_axis5
move_nanmean_slow_dict[6] = move_nanmean_slow_axis6
move_nanmean_slow_dict[7] = move_nanmean_slow_axis7
move_nanmean_slow_dict[8] = move_nanmean_slow_axis8
move_nanmean_slow_dict[9] = move_nanmean_slow_axis9
move_nanmean_slow_dict[10] = move_nanmean_slow_axis10
move_nanmean_slow_dict[11] = move_nanmean_slow_axis11
move_nanmean_slow_dict[12] = move_nanmean_slow_axis12
move_nanmean_slow_dict[13] = move_nanmean_slow_axis13
move_nanmean_slow_dict[14] = move_nanmean_slow_axis14
move_nanmean_slow_dict[15] = move_nanmean_slow_axis15
move_nanmean_slow_dict[16] = move_nanmean_slow_axis16
move_nanmean_slow_dict[17] = move_nanmean_slow_axis17
move_nanmean_slow_dict[18] = move_nanmean_slow_axis18
move_nanmean_slow_dict[19] = move_nanmean_slow_axis19
move_nanmean_slow_dict[20] = move_nanmean_slow_axis20
move_nanmean_slow_dict[21] = move_nanmean_slow_axis21
move_nanmean_slow_dict[22] = move_nanmean_slow_axis22
move_nanmean_slow_dict[23] = move_nanmean_slow_axis23
move_nanmean_slow_dict[24] = move_nanmean_slow_axis24
move_nanmean_slow_dict[25] = move_nanmean_slow_axis25
move_nanmean_slow_dict[26] = move_nanmean_slow_axis26
move_nanmean_slow_dict[27] = move_nanmean_slow_axis27
move_nanmean_slow_dict[28] = move_nanmean_slow_axis28
move_nanmean_slow_dict[29] = move_nanmean_slow_axis29
move_nanmean_slow_dict[30] = move_nanmean_slow_axis30
move_nanmean_slow_dict[31] = move_nanmean_slow_axis31
move_nanmean_slow_dict[32] = move_nanmean_slow_axis32
move_nanmean_slow_dict[None] = move_nanmean_slow_axisNone