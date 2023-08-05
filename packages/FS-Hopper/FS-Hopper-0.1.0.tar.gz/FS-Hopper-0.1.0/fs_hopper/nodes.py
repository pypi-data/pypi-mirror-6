"""fs_hopper.nodes - Nodes

FS-Hopper knows two different types of nodes - directories and files.
Both are initialized by passing an absolute path-name to either a
directory or a file.

It is prohibited to create nodes located above set_root which
defaults to '/'.
"""
__author__ = "Brian Wiborg <baccenfutter@c-base.org>"
__date__ = '2013-12-08'
__license__ = 'public domain'

import os
import glob
import fnmatch

set_root = '/'


class BaseNode(object):
    """fs_hopper.nodes.BaseNode - Base-class"""

    def __new__(cls, name):
        """Enforce jail to set_root

        :raises IOError:    if path-name is located above set_root
        """
        if len(name) < len(set_root):
            raise IOError('%s is outside of base-root: %s' % (name, set_root))
        else:
            return object.__new__(cls, name)

    def __init__(self, name):
        """
        :param name:    absolute path-name
        """
        if len(name) >= 2 and name.endswith('/'):
            name = name[:-1]
        self.name = name

    def __repr__(self):
        """Print straight-forward string representation"""
        return self.name

    def exists(self):
        """Check if node exists

        :returns bool:  True if node exists
        """
        return os.path.exists(self.name)

    def get_parent(self):
        """Obtain parent-directory

        :returns obj:   instance of fs_hopper.nodes.DirectoryNode
        :returns self:  if parent is located above set_root
        """
        parent_dir = os.path.abspath(os.path.join(self.name, '..'))
        if len(parent_dir) < len(set_root):
            return self
        else:
            return DirectoryNode(parent_dir)

    def is_dir(self):
        """Check if node is a directory

        :returns bool:  True if node is a directory
        """
        return os.path.isdir(self.name)

    def is_file(self):
        """Check if node is a file

        :returns bool:  True if node is a file
        """
        return os.path.isfile(self.name)


class FileNode(BaseNode):
    """Representation of a file in the filesystem"""

    def get_content(self, binary=False):
        """Obtain contents from file

        :param binary:  set to True to open in binary-mode
        :returns str:   contents of file
        """
        output = ''
        if binary:
            open_as = 'rb'
        else:
            open_as = 'r'
        fd = open(self.name, open_as)
        lines = fd.readlines()
        fd.close()
        for line in lines:
            output += line
        return output

    def set_content(self, content, binary=False, force_sync=False):
        """Write contents to file

        :param content:     new content as string
        :param binary:      set to True to write in binary-mode
        :param force_sync:  set to True to force fsync
        """
        if binary:
            open_as = 'wb'
        else:
            open_as = 'w'
        fd = open(self.name, open_as)
        fd.write(content)
        if force_sync:
            fd.flush()
        fd.close()

    def create(self):
        fd = open(self.name, 'a')
        fd.close()


class DirectoryNode(BaseNode):
    """Representation of a directory in the filesystem"""

    def get_childs(self, pattern='*'):
        """Obtain all child nodes

        :param pattern: globular expression (defaults to '*')
        :returns list:  instances of FileNode and DirectoryNode
        """
        output = []
        for basename in glob.glob(os.path.join(self.name, pattern)):
            f = os.path.join(self.name, basename)
            if os.path.isdir(f):
                output.append(DirectoryNode(f))
            else:
                output.append(FileNode(f))
        return output

    def get_subs(self, pattern='*'):
        """Obtain all child nodes recursively

        :param pattern: globular expression (defaults to '*')
        :returns list:  instances of FileNode and DirectoryNode
        """
        output = []
        for root, dirs, files in os.walk(self.name):
            for d in fnmatch.filter(dirs, pattern):
                output.append(DirectoryNode(os.path.join(root, d)))
            for f in fnmatch.filter(files, pattern):
                output.append(FileNode(os.path.join(root, f)))
        return output

    def mkdir(self):
        """Create this directory in the filesystem"""
        os.mkdir(self.name)

    def add_dir(self, name):
        """Add a sub-directory

        :param name:    absolute path-name or relative to self.name
        :returns obj:   instance of DirectoryNode
        """
        if not name.startswith(self.name):
            name = os.path.join(self.name, name)
        child = DirectoryNode(name)
        child.mkdir()
        return child

    def add_file(self, name):
        """Add a file in this directory

        :param name:    absolute path-name or relative to self.name
        """
        if not name.startswith(self.name):
            name = os.path.join(self.name, name)
        child = FileNode(name)
        child.create()
        return child
