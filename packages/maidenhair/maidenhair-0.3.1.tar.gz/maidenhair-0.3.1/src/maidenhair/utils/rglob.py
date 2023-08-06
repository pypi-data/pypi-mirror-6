"""
Recursive glob module

This glob is a recursive version of `glob` module.

"""
__author__ = 'Alisue <lambdalisue@hashnote.net>'
__all__ = ['iglob', 'glob']
import os
import fnmatch


def iglob(pathname):
    """
    Return an iterator which yields the same values as glob() without actually
    storing them all simultaneously.

    Parameters
    ----------
    pathname : string
        A glob pattern string which will be used for finding files

    Returns
    -------
    iterator
        An iterator instance which will yield full path name

    """
    dirname = os.path.dirname(pathname)
    basename_pattern = os.path.basename(pathname)
    for root, dirs, files in os.walk(dirname):
        for basename in files:
            if fnmatch.fnmatch(basename, basename_pattern):
                yield os.path.join(root, basename)

def glob(pathname):
    """
    Return a possibly-empty list of path names that match pathname.
    It is recursive version of `glob.glob()`

    Parameters
    ----------
    pathname : string
        A glob pattern string which will be used for finding files

    Returns
    -------
    list
        A list of full path names

    """
    return list(iglob(pathname))
