"""
Statistics shortcut functions

"""
__author__ = 'Alisue (lambdalisue@hashnote.net)'
import numpy as np

def average(x):
    """
    Return a numpy array of column average.
    It does not affect if the array is one dimension

    Parameters
    ----------
    x : ndarray
        A numpy array instance

    Returns
    -------
    ndarray
        A 1 x n numpy array instance of column average

    Examples
    --------
    >>> a = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    >>> np.array_equal(average(a), [2, 5, 8])
    True
    >>> a = np.array([1, 2, 3])
    >>> np.array_equal(average(a), [1, 2, 3])
    True

    """
    if x.ndim > 1 and len(x[0]) > 1:
        return np.average(x, axis=1)
    return x

def mean(x):
    """
    Return a numpy array of column mean.
    It does not affect if the array is one dimension

    Parameters
    ----------
    x : ndarray
        A numpy array instance

    Returns
    -------
    ndarray
        A 1 x n numpy array instance of column mean

    Examples
    --------
    >>> a = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    >>> np.array_equal(mean(a), [2, 5, 8])
    True
    >>> a = np.array([1, 2, 3])
    >>> np.array_equal(mean(a), [1, 2, 3])
    True

    """
    if x.ndim > 1 and len(x[0]) > 1:
        return np.mean(x, axis=1)
    return x

def median(x):
    """
    Return a numpy array of column median.
    It does not affect if the array is one dimension

    Parameters
    ----------
    x : ndarray
        A numpy array instance

    Returns
    -------
    ndarray
        A 1 x n numpy array instance of column median

    Examples
    --------
    >>> a = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    >>> np.array_equal(median(a), [2, 5, 8])
    True
    >>> a = np.array([1, 2, 3])
    >>> np.array_equal(median(a), [1, 2, 3])
    True

    """
    if x.ndim > 1 and len(x[0]) > 1:
        return np.median(x, axis=1)
    return x

def variance(x):
    """
    Return a numpy array of column variance

    Parameters
    ----------
    x : ndarray
        A numpy array instance

    Returns
    -------
    ndarray
        A 1 x n numpy array instance of column variance

    Examples
    --------
    >>> a = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    >>> np.testing.assert_array_almost_equal(
    ...     variance(a),
    ...     [0.666666, 0.666666, 0.666666])
    >>> a = np.array([1, 2, 3])
    >>> np.testing.assert_array_almost_equal(
    ...     variance(a),
    ...     0.666666)

    """
    if x.ndim > 1 and len(x[0]) > 1:
        return np.var(x, axis=1)
    return np.var(x)

def standard_deviation(x):
    """
    Return a numpy array of column standard deviation

    Parameters
    ----------
    x : ndarray
        A numpy array instance

    Returns
    -------
    ndarray
        A 1 x n numpy array instance of column standard deviation

    Examples
    --------
    >>> a = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    >>> np.testing.assert_array_almost_equal(
    ...     standard_deviation(a),
    ...     [0.816496, 0.816496, 0.816496])
    >>> a = np.array([1, 2, 3])
    >>> np.testing.assert_array_almost_equal(
    ...     standard_deviation(a),
    ...     0.816496)

    """
    if x.ndim > 1 and len(x[0]) > 1:
        return np.std(x, axis=1)
    return np.std(x)

def confidential_interval(x, alpha=0.98):
    """
    Return a numpy array of column confidential interval

    Parameters
    ----------
    x : ndarray
        A numpy array instance
    alpha : float
        Alpha value of confidential interval

    Returns
    -------
    ndarray
        A 1 x n numpy array which indicate the each difference from sample
        average point to confidential interval point
    """
    from scipy.stats import t
    if x.ndim == 1:
        df = len(x) - 1
        # calculate positive critical value of student's T distribution
        cv = t.interval(alpha, df)
        # calculate sample standard distribution
        std = np.std(x)
    else:
        # calculate degree of freedom
        df = len(x[0]) - 1
        # calculate positive critical value of student's T distribution
        cv = t.interval(alpha, df)[1]
        # calculate sample standard distribution
        std = np.std(x, axis=1)
    # calculate positive difference from
    # sample average to confidential interval
    return std * cv / np.sqrt(df)

def simple_moving_matrix(x, n=10):
    """
    Create simple moving matrix.

    Parameters
    ----------
    x : ndarray
        A numpy array
    n : integer
        The number of sample points used to make average

    Returns
    -------
    ndarray
        A n x n numpy array which will be useful for calculating confidentail
        interval of simple moving average

    """
    if x.ndim > 1 and len(x[0]) > 1:
        x = np.average(x, axis=1)
    h = n / 2
    o = 0 if h * 2 == n else 1
    xx = []
    for i in range(h, len(x) - h):
        xx.append(x[i-h:i+h+o])
    return np.array(xx)

def simple_moving_average(x, n=10):
    """
    Calculate simple moving average

    Parameters
    ----------
    x : ndarray
        A numpy array
    n : integer
        The number of sample points used to make average

    Returns
    -------
    ndarray
        A 1 x n numpy array instance
    """
    if x.ndim > 1 and len(x[0]) > 1:
        x = np.average(x, axis=1)
    a = np.ones(n) / float(n)
    return np.convolve(x, a, 'valid')

if __name__ == '__main__':
    import doctest; doctest.testmod()
