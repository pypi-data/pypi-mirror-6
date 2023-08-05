"""
maidenhair shortcut function module

"""
__author__  = 'Alisue (lambdalisue@hashnote.net)'
__all__ = (
   'load', 
   'set_default_parser',
   'get_default_parser',
   'set_default_loader',
   'get_default_loader',
)

from maidenhair.parsers.base import BaseParser
from maidenhair.loaders.base import BaseLoader
from maidenhair.utils.plugins import registry

"""default parser instance (private)"""
_parser = None
"""default loader instance (private)"""
_loader = None


def load(pathname, using=None, unite=False, basecolumn=0,
         relative=False, baseline=None,
         parser=None, loader=None,
         with_filename=False, recursive=False, natsort=True, **kwargs):
    """
    Load data from file matched with given glob pattern.

    Return value will be a list of data unless :attr:`unite` is `True`.
    If :attr:`unite` is `True` then all data will be united into a single data.

    Parameters
    ----------
    pathname : string or list
        A glob pattern or a list of glob pattern which will be used to load
        data.
    using : integer list or slice instance, optional
        A list of index or slice instance which will be used to slice data
        columns.
    unite : boolean, optional:
        If it is `True` then dataset will be united into a single numpy
        array. See usage for more detail.
    basecolumn : integer, optional
        An index of base column. all data will be trimmed based on the order
        of this column when the number of samples are different among the
        dataset.
        It only affect when :attr:`unite` is specified as `True`.
    relative : boolean, optional
        Make the dataset relative to the first data by using
        :func:`maidenhair.filters.relative.relative` function.
    baseline : function, None, optional
        A function which will take data columns and return regulated data
        columns.
        It is useful to regulate baseline of each data in dataset.
    parser : instance, string, None, optional
        An instance or registered name of parser class.
        If it is not specified, default parser specified with
        :func:`maidenhair.functions.set_default_parser` will be used instead.
    loader : instance, string, None, optional
        An instance or registered name of loader class.
        If it is not specified, default loader specified with
        :func:`maidenhair.functions.set_default_loader` will be used instead.
    with_filename : boolean, optional
        If it is `True`, returning dataset will contain filename in the
        first column.
        It is cannot be used with :attr:`unite = True`
    recursive : boolean, optional
        Recursively find pattern in the directory
    natsort : boolean
        Naturally sort found files.

    Returns
    -------
    list
        A list of numpy array

    Examples
    --------
    Assume that there are five independent experimental data for three types
    of samples, namely there are fifteen data.
    Each data file would have two direction (X and Y) and 100 data points.
    Its filenames would be formatted as
    `<type number>.<experimental number>.txt`
    and save in `tests/fixtures` directory.

    Then the loading code will be

    >>> import maidenhair
    >>> dataset = []
    >>> dataset += maidenhair.load('tests/fixtures/1.*.txt',
    ...                             unite=True, using=(0, 1))
    >>> dataset += maidenhair.load('tests/fixtures/2.*.txt',
    ...                             unite=True, using=(0, 1))
    >>> dataset += maidenhair.load('tests/fixtures/3.*.txt',
    ...                             unite=True, using=(0, 1))
    >>> len(dataset)            # number of samples
    3
    >>> len(dataset[0])         # number of axis (X and Y)
    2
    >>> len(dataset[0][0])      # number of data points
    100
    >>> len(dataset[0][0][0])   # number of columns
    5

    Without using `unite=True`, the dataset will be

    >>> import numpy as np
    >>> import maidenhair
    >>> dataset = []
    >>> dataset += maidenhair.load('tests/fixtures/1.*.txt', using=(0, 1))
    >>> dataset += maidenhair.load('tests/fixtures/2.*.txt', using=(0, 1))
    >>> dataset += maidenhair.load('tests/fixtures/3.*.txt', using=(0, 1))
    >>> len(dataset)            # number of samples
    15
    >>> len(dataset[0])         # number of axis (X and Y)
    2
    >>> len(dataset[0][0])      # number of data points
    100
    >>> isinstance(dataset[0][0][0], np.float64)
    True

    """
    parser = parser or get_default_parser()
    loader = loader or get_default_loader()
    # make sure the pathname is a list
    if not isinstance(pathname, (list, tuple)):
        pathname = [pathname]
    dataset = []
    for _pathname in pathname:
        dataset += loader.glob(_pathname,
                using=using, parser=parser,
                unite=unite, basecolumn=basecolumn,
                with_filename=with_filename,
                recursive=recursive,
                natsort=natsort,
                **kwargs)
    if relative:
        from maidenhair.filters import relative
        dataset = relative(dataset)
    if baseline is not None:
        for i, data in enumerate(dataset):
            dataset[i] = baseline(data)
    return dataset

def get_default_parser():
    """
    Get default parser instance

    Returns
    -------
    instance
        An instance of parser class

    See also
    --------
    :func:`maidenhair.utils.plugins.Registry.register` : Register new class

    """
    if _parser is None:
        from maidenhair.parsers.plain import PlainParser
        set_default_parser(PlainParser)
    return _parser

def set_default_parser(parser):
    """
    Set defaulr parser instance

    Parameters
    ----------
    parser : instance or string
        An instance or registered name of parser class.
        The specified parser instance will be used when user did not specified
        :attr:`parser` in :func:`maidenhair.functions.load` function.

    See also
    --------
    :func:`maidenhair.utils.plugins.Registry.register` : Register new class

    """
    if isinstance(parser, basestring):
        parser = registry.find(parser)()
    if not isinstance(parser, BaseParser):
        parser = parser()
    global _parser
    _parser = parser

def get_default_loader():
    """
    Get default loader instance

    Returns
    -------
    instance
        An instance of loader class

    See also
    --------
    :func:`maidenhair.utils.plugins.Registry.register` : Register new class

    """
    if _loader is None:
        from maidenhair.loaders.plain import PlainLoader
        set_default_loader(PlainLoader)
    return _loader

def set_default_loader(loader):
    """
    Set defaulr loader instance

    Parameters
    ----------
    loader : instance or string
        An instance or registered name of loader class.
        The specified loader instance will be used when user did not specified
        :attr:`loader` in :func:`maidenhair.functions.load` function.

    See also
    --------
    :func:`maidenhair.utils.plugins.Registry.register` : Register new class

    """
    if isinstance(loader, basestring):
        loader = registry.find(loader)()
    if not isinstance(loader, BaseLoader):
        loader = loader()
    global _loader
    _loader = loader

if __name__ == '__main__':
    import doctest; doctest.testmod()
