"""
Get special directory path

"""
__author__  = 'Alisue (lambdalisue@hashnote.net)'
__all__ = (
    'get_system_root_directory',
    'get_system_plugins_directory',
    'get_user_root_directory',
    'get_user_plugins_directory',
)

import os
import platform

"""Application name (private)"""
APP_NAME = 'maidenhair'

def get_system_root_directory():
    """
    Get system root directory (application installed root directory)

    Returns
    -------
    string
        A full path

    """
    root = os.path.dirname(__file__)
    root = os.path.dirname(root)
    root = os.path.abspath(root)
    return root

def get_system_plugins_directory():
    """
    Get system plugin directory (plugin directory for system wide use)

    Returns
    -------
    string
        A full path

    """
    root = get_system_root_directory()
    return os.path.join(root, 'plugins')

def get_user_root_directory():
    """
    Get user root directory (application user configuration root directory)

    Returns
    -------
    string
        A full path

    """
    uname = platform.system()
    if uname == 'Windows':
        root = os.path.join(os.environ['APPDATA'], APP_NAME)
        root = os.path.abspath(root)
    elif uname == 'Linux':
        if os.path.exists(os.path.expanduser('~/.config')):
            root = os.path.join(os.path.expanduser('~/.config'), APP_NAME)
        else:
            root = os.path.join(os.path.expanduser('~'), '.%s' % APP_NAME)
        root = os.path.abspath(root)
    elif uname in ('Linux', 'Darwin'):
        root = os.path.join(os.path.expanduser('~'), '.%s' % APP_NAME)
        root = os.path.abspath(root)
    else:
        root = os.path.join(os.path.expanduser('~'), APP_NAME)
        root = os.path.abspath(root)
    return root

def get_user_plugins_directory():
    """
    Get user plugin directory (plugin directory for the particular user)

    Returns
    -------
    string
        A full path

    """
    root = get_user_root_directory()
    return os.path.join(root, 'plugins')
