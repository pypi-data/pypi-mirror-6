# coding=utf-8
"""
"""
__author__ = 'Alisue <lambdalisue@hashnote.net>'
import os
from maidenhair.loaders.base import unite_dataset as _unite_dataset
from maidenhair.compat import OrderedDict


def default_classify_function(data):
    """
    A default classify_function which recieve `data` and return filename without
    characters just after the last underscore

    >>> # [<filename>] is mimicking `data`
    >>> default_classify_function(['./foo/foo_bar_hoge.piyo'])
    './foo/foo_bar.piyo'
    >>> default_classify_function(['./foo/foo_bar.piyo'])
    './foo/foo.piyo'
    >>> default_classify_function(['./foo/foo.piyo'])
    './foo/foo.piyo'
    >>> default_classify_function(['./foo/foo'])
    './foo/foo'
    """
    # data[0] indicate the filename of the data
    rootname, basename = os.path.split(data[0])
    filename, ext = os.path.splitext(basename)
    if '_' in filename:
        filename = filename.rsplit('_', 1)[0]
    filename = os.path.join(rootname, filename + ext)
    return filename


def classify_dataset(dataset, fn):
    """
    Classify dataset via fn

    Parameters
    ----------
    dataset : list
        A list of data
    fn : function
        A function which recieve :attr:`data` and return classification string.
        It if is None, a function which return the first item of the
        :attr:`data` will be used (See ``with_filename`` parameter of
        :func:`maidenhair.load` function).

    Returns
    -------
    dict
        A classified dataset
    """
    if fn is None:
        fn = default_classify_function
    # classify dataset via classify_fn
    classified_dataset = OrderedDict()
    for data in dataset:
        classify_name = fn(data)
        if classify_name not in classified_dataset:
            classified_dataset[classify_name] = []
        classified_dataset[classify_name].append(data)
    return classified_dataset
