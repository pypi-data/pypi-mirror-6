#!/usr/bin/env python
# coding=utf-8
"""
A plain parser class

"""
__author__  = 'Alisue (lambdalisue@hashnote.net)'

import numpy as np
from maidenhair.parsers.base import BaseParser

class PlainParser(BaseParser):
    """
    A plain text parser class based on `numpy.loadtxt` method
    """
    def parse(self, iterable, **kwargs):
        """
        Parse whitespace separated iterable to a numpy array.
        It is based on `numpy.loadtxt` method.

        Parameters
        ----------
            iterable : iterable
                An iterable instance to parse

        Returns
        -------
        ndarray
            An instance of numpy array

        """
        return np.loadtxt(iterable, **kwargs)
