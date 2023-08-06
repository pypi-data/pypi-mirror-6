#!/usr/bin/env python
"""
A plugin registry module

"""
__author__  = 'Alisue (lambdalisue@hashnote.net)'
__all__ = (
    'Registry',
    'registry',
)
import os
import sys
from bunch import Bunch
from maidenhair.utils import environment


class Registry(object):
    """
    A registry class which store plugin objects
    """

    """entry_point for plugins"""
    ENTRY_POINT = 'maidenhair.plugins'

    def __init__(self):
        self.raw = Bunch()

    def find(self, name, namespace=None):
        """
        Find plugin object

        Parameters
        ----------
        name : string
            A name of the object entry or full namespace
        namespace : string, optional
            A period separated namespace. E.g. `foo.bar.hogehoge`

        Returns
        -------
        instance
            An instance found

        Raises
        ------
        KeyError
            If the named instance have not registered

        Examples
        --------
        >>> registry = Registry()
        >>> registry.register('hello', 'goodbye')
        >>> registry.register('foo', 'bar', 'hoge.hoge.hoge')
        >>> registry.register('foobar', 'foobar', 'hoge.hoge')
        >>> registry.find('hello') == 'goodbye'
        True
        >>> registry.find('foo', 'hoge.hoge.hoge') == 'bar'
        True
        >>> registry.find('hoge.hoge.foobar') == 'foobar'
        True

        """
        if "." in name:
            namespace, name = name.rsplit(".", 1)
        caret = self.raw
        if namespace:
            for term in namespace.split('.'):
                if term not in caret:
                    caret[term] = Bunch()
                caret = caret[term]
        return caret[name]

    def register(self, name, obj, namespace=None):
        """
        Register :attr:`obj` as :attr:`name` in :attr:`namespace`

        Parameters
        ----------
        name : string
            A name of the object entry
        obj : instance
            A python object which will be registered
        namespace : string, optional
            A period separated namespace. E.g. `foo.bar.hogehoge`

        Examples
        --------
        >>> registry = Registry()
        >>> registry.register('hello', 'goodbye')
        >>> registry.raw.hello == 'goodbye'
        True
        >>> registry.register('foo', 'bar', 'hoge.hoge.hoge')
        >>> isinstance(registry.raw.hoge, Bunch)
        True
        >>> isinstance(registry.raw.hoge.hoge, Bunch)
        True
        >>> isinstance(registry.raw.hoge.hoge.hoge, Bunch)
        True
        >>> registry.raw.hoge.hoge.hoge.foo == 'bar'
        True
        >>> registry.register('hoge.hoge.foobar', 'foobar')
        >>> registry.raw.hoge.hoge.hoge.foo == 'bar'
        True
        >>> registry.raw.hoge.hoge.foobar == 'foobar'
        True

        """
        if "." in name:
            namespace, name = name.rsplit(".", 1)
        caret = self.raw
        if namespace:
            for term in namespace.split('.'):
                if term not in caret:
                    caret[term] = Bunch()
                caret = caret[term]
        caret[name] = obj

    def load_plugins(self, plugin_dirs=None, quiet=True):
        """
        Load plugins in `sys.path` and :attr:`plugin_dirs`

        Parameters
        ----------
        plugin_dirs : list or tuple of string, optional
            A list or tuple of plugin directory path
        quiet : bool, optional
            If True, print all error message

        """
        from pkg_resources import working_set
        from pkg_resources import iter_entry_points
        from pkg_resources import Environment

        if plugin_dirs is None:
            plugin_dirs = []
            plugin_dirs.append(environment.get_system_plugins_directory())
            plugin_dirs.append(environment.get_user_plugins_directory())

        distributions, errors = working_set.find_plugins(
                Environment(plugin_dirs)
            )
        map(working_set.add, distributions)

        if not quiet:
            # display error info
            for distribution, error in errors:
                print distrubution, error

        for entry_point in iter_entry_points(self.ENTRY_POINT):
            # load entry point
            plugin = entry_point.load()
            # if plugin is callable and `manually` is True, initialize manually
            if callable(plugin) and getattr(plugin, 'manually', False):
                # manually initialize plugin
                plugin(self)
            else:
                # automatically initialize plugin
                self.register(entry_point.name, plugin)

"""A plugin registry"""
registry = Registry()
registry.load_plugins(quiet=False)


if __name__ == '__main__':
    import doctest; doctest.testmod()
