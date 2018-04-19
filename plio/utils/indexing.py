import warnings
import numpy as np

def is_dict_like(value):
    return hasattr(value, 'keys') and hasattr(value, '__getitem__')

def expanded_indexer(key, ndim):
    """Given a key for indexing an ndarray, return an equivalent key which is a
    tuple with length equal to the number of dimensions.
    The expansion is done by replacing all `Ellipsis` items with the right
    number of full slices and then padding the key with full slices so that it
    reaches the appropriate dimensionality.
    """
    if not isinstance(key, tuple):
        # numpy treats non-tuple keys equivalent to tuples of length 1
        key = (key,)
    new_key = []
    # handling Ellipsis right is a little tricky, see:
    # http://docs.scipy.org/doc/numpy/reference/arrays.indexing.html#advanced-indexing
    found_ellipsis = False
    for k in key:
        if k is Ellipsis:
            if not found_ellipsis:
                new_key.extend((ndim + 1 - len(key)) * [slice(None)])
                found_ellipsis = True
            else:
                new_key.append(slice(None))
        else:
            new_key.append(k)
    if len(new_key) > ndim:
        raise IndexError('too many indices')
    new_key.extend((ndim - len(new_key)) * [slice(None)])
    return tuple(new_key)

class _LocIndexer(object):
    def __init__(self, data_array):
        self.data_array = data_array
        
    def __getitem__(self, key):
        # expand the indexer so we can handle Ellipsis
        key = expanded_indexer(key, 3)
        sl = key[0]
        ifnone = lambda a, b: b if a is None else a
        if isinstance(sl, slice):
            sl = list(range(ifnone(sl.start, 0), self.data_array.nbands, ifnone(sl.step, 1)))
        
        idx = [self._get_idx(s) for s in sl]
        key = (idx, key[1], key[2])
        return self.data_array._read(key)   
    
    def _get_idx(self, value, tolerance=2):
        vals = np.abs(self.data_array.wavelengths-value)
        minidx = np.argmin(vals)
        if vals[minidx] >= tolerance:
            warning.warn("Absolute difference between requested value and found values is {}".format(vals[minidx]))
        return minidx
    
class _iLocIndexer(object):
    def __init__(self, data_array):
        self.data_array = data_array

    def __getitem__(self, key):
        # expand the indexer so we can handle Ellipsis
        key = expanded_indexer(key, 3)
        sl = key[0]
        ifnone = lambda a, b: b if a is None else a
        if isinstance(sl, slice):
            sl = list(range(ifnone(sl.start, 0),
                            ifnone(sl.stop, self.data_array.nbands),
                            ifnone(sl.step, 1)))
        
        key = (key[0], key[1], key[2])
        return self.data_array._read(key)