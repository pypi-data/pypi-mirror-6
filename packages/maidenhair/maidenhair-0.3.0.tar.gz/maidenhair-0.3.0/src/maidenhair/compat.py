# coding=utf-8
"""
"""
__author__ = 'Alisue <lambdalisue@hashnote.net>'

# prefer new OrderedDict
try:
    # from Python 2.7
    from collections import OrderedDict
except ImportError:
    # pip install ordereddict
    from ordereddict import OrderedDict
