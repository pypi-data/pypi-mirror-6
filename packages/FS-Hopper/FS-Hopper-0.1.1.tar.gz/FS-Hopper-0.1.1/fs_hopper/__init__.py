"""FS-Hopper

A thin and simplistic abstraction layer for accessing a filesystem
directory tree in an object-oriented fashion.
"""
__author__ = "Brian Wiborg <baccenfutter@c-base.org>"
__date__ = '2013-12-08'
__license__ = 'public domain'

from nodes import DirectoryNode as Directory
from nodes import FileNode as File

def get_root():
    import nodes
    return nodes.set_root

def set_root(base_root):
    import nodes
    nodes.set_root = base_root
