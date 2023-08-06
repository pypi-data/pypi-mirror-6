#!/usr/bin/env python
# coding=utf-8
"""
An abstract loader class

"""
__author__  = 'Alisue (lambdalisue@hashnote.net)'
import os
import warnings
import itertools
import numpy as np
from glob import glob
from natsort import natsorted
from maidenhair.utils.rglob import glob as rglob


class BaseLoader(object):
    """
    A abstract loader class
    """
    def __init__(self, using=None, parser=None):
        """
        Construct loader class

        Parameters
        ----------
        using : list of integer or slice instance, optional
            A default list of index or slice instance.
            It will be used when :attr:`using` is not specified in
            :meth:`maidenhair.loader.base.BaseLoader.load` method.
        parser : instance or None, optional
            A default instance of parser class.
            It will be used when :attr:`parser` is not specified in
            :meth:`maidenhair.loader.base.BaseLoader.load` method.

        """
        self.using = using
        self.parser = parser

    def load(self, filename, using=None, parser=None, **kwargs):
        """
        Load data from file using a specified parser.

        Return value will be separated or sliced into a column list

        Parameters
        ----------
        filename : string
            A data file path
        using : list of integer, slice instance, or None, optional
            A list of index or slice instance used to slice data into column
            If it is not specified, :attr:`using` specified in constructor
            will be used instead.
        parser : instance or None, optional
            An instance or registered name of parser class.
            If it is not specified, :attr:`parser` specified in constructor
            will be used instead.

        Returns
        -------
        ndarray
            A list of numpy array

        """
        using = using or self.using
        parser = parser or self.parser
        if parser is None:
            raise AttributeError("A parser instance must be specified")
        # parse iterator with the specified parser
        data = parser.load(filename, **kwargs)
        # slice column by using
        return slice_columns(data, using)

    def glob(self, pathname, using=None,
             unite=False, basecolumn=0, parser=None,
             with_filename=False,
             recursive=False, natsort=True, **kwargs):
        """
        Load data from file matched with given glob pattern.

        Return value will be a list of data unless :attr:`unite` is `True`.
        If :attr:`unite` is `True`, all dataset will be united into a single
        data.

        Parameters
        ----------
        pathname : string
            A glob pattern
        using : list of integer, slice instance, or None, optional
            A list of index or slice instance used to slice data into column
            If it is not specified, :attr:`using` specified in constructor
            will be used instead.
        unite : boolean, optional:
            If it is `True` then dataset will be united into a single numpy
            array. See usage for more detail.
        basecolumn : integer, optional
            An index of base column. all data will be trimmed based on the order
            of this column when the number of samples are different among the
            dataset.
            It only affect when :attr:`unite` is specified as `True`.
        parser : instance, optional
            An instance or registered name of parser class.
            If it is not specified, :attr:`parser` specified in constructor
            will be used instead.
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
        ndarray
            A list of numpy array
        """
        # argument check
        if unite and with_filename:
            raise AttributeError(
                    "`with_filename` attribute cannot be set True when "
                    "`unite` attribute was set True.")
        # make sure that the pathname is absolute
        pathname = os.path.abspath(pathname)
        if recursive:
            filelist = rglob(pathname)
        else:
            filelist = glob(pathname)
        if natsort:
            filelist = natsorted(filelist, number_type=None)
        # create dataset
        dataset =[]
        for filename in filelist:
            data = self.load(
                filename=filename,
                using=using,
                parser=parser,
                **kwargs)
            if with_filename:
                data = [filename] + data
            dataset.append(data)
        # tell the number of files found if verbose is True
        if kwargs.get('verbose', False):
            print "%d files are found with `%s`" % (
                    len(dataset),
                    os.path.relpath(pathname))
        # warn if nothing have found unless quiet is True
        if len(dataset) == 0 and not kwargs.get('quiet', False):
            warnings.warn("Nothing found with glob pattern '%s'" % pathname)
        # unite dataset if specified
        if unite and len(dataset) > 0:
            dataset = unite_dataset(dataset, basecolumn)
        return dataset

def slice_columns(x, using=None):
    """
    Slice a numpy array to make columns

    Parameters
    ----------
    x : ndarray
        A numpy array instance
    using : list of integer or slice instance or None, optional
        A list of index or slice instance

    Returns
    -------
    ndarray
        A list of numpy array columns sliced

    """
    if using is None:
        using = range(0, len(x[0]))
    return [x[:,s] for s in using]

def unite_dataset(dataset, basecolumn=0):
    """
    Unite dataset into a single data

    Parameters
    ----------
    dataset : list of ndarray
        A data list of a column list of a numpy arrays
    basecolumn : integer, optional
        An index of base column.
        All data will be trimmed based on the order of this column when the
        number of samples are different among the dataset

    Returns
    -------
    list of numpy array
        A column list of a numpy array

    """
    ndata = [None] * len(dataset[0])
    for pdata in dataset:
        # select basecolumn
        bnx = ndata[basecolumn]
        bpx = pdata[basecolumn]
        if bnx is not None and bnx.ndim >= 2:
            bnx = bnx[:,-1]
        if bpx is not None and bpx.ndim >= 2:
            bpx = bpx[:,-1]
        # calculate min and max of this and final data
        if bnx is not None and len(bnx) != len(bpx):
            # the number of samples is different, so regulation is required
            xmin = max(np.min(bnx), np.min(bpx))
            xmax = min(np.max(bnx), np.max(bpx))
            # slice the data
            nindex = np.where((bnx>xmin) & (bnx<xmax))
            pindex = np.where((bpx>xmin) & (bpx<xmax))
        else:
            nindex = None
            pindex = None
        for i, (nx, px) in enumerate(itertools.izip(ndata, pdata)):
            if nindex:
                nx = nx[nindex]
            if pindex:
                px = px[pindex]
            ndata[i] = px if nx is None else np.c_[nx, px]
    return [ndata]
