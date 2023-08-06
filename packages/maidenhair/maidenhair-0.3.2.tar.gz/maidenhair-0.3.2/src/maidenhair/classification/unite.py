# coding=utf-8
"""
"""
__author__ = 'Alisue <lambdalisue@hashnote.net>'
import os
from maidenhair.loaders.base import unite_dataset as _unite_dataset
from maidenhair.compat import OrderedDict


def default_unite_function(data):
    """
    A default unite_function which recieve `data` and return filename without
    middle extensions

    >>> # [<filename>] is mimicking `data`
    >>> default_unite_function(['./foo/foo.bar.hoge.piyo'])
    './foo/foo.piyo'
    >>> default_unite_function(['./foo/foo.piyo'])
    './foo/foo.piyo'
    >>> default_unite_function(['./foo/foo'])
    './foo/foo'
    """
    # data[0] indicate the filename of the data
    rootname, basename = os.path.split(data[0])
    filename, ext = os.path.splitext(basename)
    if '.' in filename:
        filename = filename.rsplit('.')[0]
    filename = os.path.join(rootname, filename + ext)
    return filename


def unite_dataset(dataset, basecolumn, fn=None):
    """
    Unite dataset via fn

    Parameters
    ----------
    dataset : list
        A list of data
    basecolumn : int
        A number of column which will be respected in uniting dataset
    fn : function
        A function which recieve :attr:`data` and return classification string.
        It if is None, a function which return the first item of the
        :attr:`data` will be used (See ``with_filename`` parameter of
        :func:`maidenhair.load` function).

    Returns
    -------
    list
        A united dataset
    """
    # create default unite_fn
    if fn is None:
        fn = default_unite_function
    # classify dataset via unite_fn
    united_dataset = OrderedDict()
    for data in dataset:
        unite_name = fn(data)
        if unite_name not in united_dataset:
            united_dataset[unite_name] = []
        united_dataset[unite_name].append(data[1:])
    # unite dataset via maidenhair.loaders.base.unite_dataset
    for name, dataset in united_dataset.items():
        united_dataset[name] = _unite_dataset(dataset, basecolumn)[0]
    # create new dataset (respect the order of the dataset)
    dataset = []
    for name, _dataset in united_dataset.items():
        dataset.append([name] + _dataset)
    return dataset
