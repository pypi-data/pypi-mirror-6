#!/usr/bin/env python
"""
Baseline regulation filter module

"""
__author__  = 'Alisue (lambdalisue@hashnote.net)'
from maidenhair.statistics import average


def baseline(dataset, column=1, fn=None, fail_silently=True):
    """
    Substract baseline from the dataset

    Parameters
    ----------
    dataset : list of numpy array list
        A list of numpy array list
    column : integer
        An index of column which will be proceeded
    fn : function
        A function which require data and return baseline.
        If it is `None`, the first value of data will be used
        for subtracting
    fail_silently : boolean
        If `True`, do not raise exception if no data exists

    Returns
    -------
    ndarray
        A list of numpy array list

    Examples
    --------
    >>> import numpy as np
    >>> from maidenhair.filters.baseline import baseline
    >>> dataset = []
    >>> dataset.append([np.array([0, 1, 2]), np.array([3, 4, 5])])
    >>> dataset.append([np.array([0, 1, 2]), np.array([3, 5, 7])])
    >>> dataset.append([np.array([0, 1, 2]), np.array([100, 103, 106])])
    >>> expected = [
    ...     [np.array([0, 1, 2]), np.array([0, 1, 2])],
    ...     [np.array([0, 1, 2]), np.array([0, 2, 4])],
    ...     [np.array([0, 1, 2]), np.array([0, 3, 6])],
    ... ]
    >>> proceed = baseline(dataset)
    >>> np.array_equal(proceed, expected)
    True

    """
    try:
        if fn is None:
            fn = lambda columns, column: columns[column][0]
        for i, data in enumerate(dataset):
            _baseline = fn(data, column=column)
            dataset[i][column] -= _baseline
        return dataset
    except IndexError, e:
        if fail_silently:
            # fail silently
            return dataset
        raise e

if __name__ == '__main__':
    import doctest; doctest.testmod()
