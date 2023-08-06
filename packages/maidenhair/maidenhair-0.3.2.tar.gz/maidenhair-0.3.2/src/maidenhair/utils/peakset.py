# coding=utf-8
"""
"""
__author__ = 'Alisue <lambdalisue@hashnote.net>'
import numpy as np
import maidenhair.statistics


def find_peakset(dataset, basecolumn=-1, method='', where=None):
    """
    Find peakset from the dataset

    Parameters
    -----------
    dataset : list
        A list of data
    basecolumn : int
        An index of column for finding peaks
    method : str
        A method name of numpy for finding peaks
    where : function
        A function which recieve ``data`` and return numpy indexing list

    Returns
    -------
    list
        A list of peaks of each axis (list)
    """
    peakset = []
    where_i = None
    for data in dataset:
        base = data[basecolumn]
        base = maidenhair.statistics.average(base)
        # limit data points
        if where:
            where_i = np.where(where(data))
            base = base[where_i]
        # find peak index
        index = getattr(np, method, np.argmax)(base)
        # create peakset
        for a, axis in enumerate(data):
            if len(peakset) <= a:
                peakset.append([])
            if where_i:
                axis = axis[where_i]
            peakset[a].append(axis[index])
    peakset = np.array(peakset)
    return peakset
