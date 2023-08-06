#!/usr/bin/env python
# coding=utf-8
"""
A base data parser module

"""
__author__  = 'Alisue (lambdalisue@hashnote.net)'


class BaseParser(object):
    """
    An abstract data parser class
    """
    def parse(self, iterable, **kwargs):
        """
        Parse iterable to an numpy array

        .. Warning:: Subclasses must override this method

        Parameters
        ----------
            iterable : iterable
                An iterable instance to parse

        Returns
        -------
        ndarray
            An instance of numpy array

        """
        raise NotImplementedError("Subclass must override this method")

    def load(self, filename, **kwargs):
        """
        Parse a file specified with the filename and return an numpy array

        Parameters
        ----------
            filename : string
                A path of a file

        Returns
        -------
        ndarray
            An instance of numpy array

        """
        with open(filename, 'r') as f:
            return self.parse(f, **kwargs)
