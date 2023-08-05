# -*- coding: utf-8 -*-
"""
Cob URLs: references to resources within current or remote Cobs.
"""

from __future__ import absolute_import

import posixpath

import webassets

from slingr.common import SlingrError, FileRoot


# Always use '/' to join CobUrl paths, even on Windows
pathjoin = posixpath.join


class CobUrlError(SlingrError):
    """Base class for CobUrl-related exceptions"""


class CobUrl(object):
    """Symbolic naming scheme for files and directories.

    - Absolute within another Cob:  Starts with 'cob://cobname/' (TODO)
    - Starts with "http://" or "https://"
      or "//" (scheme-neutral, but implicitly http[s]).
    - Absolute within current Cob:  Starts with "/"
    - Relative to another CobUrl in the current Cob:
      Does not start with "/"; may include "..".

    Note: "/" is always the path separator, even on Windows.
    Just like URLs.
    """

    RootPath = ""

    @classmethod
    def make_path(cls, parent_coburl, new_path):
        if cls.is_remote_cob_path(new_path):
            raise CobUrlError("Can't handle remote Cobs yet")  # TODO
        elif cls.is_http_path(new_path):
            return new_path
        else:
            assert not parent_coburl.path.startswith("/")
            # if new_path starts with "/", it replaces parent_coburl;
            # otherwise, it is appended
            relpath = pathjoin("/" + parent_coburl.path, new_path)
            assert relpath.startswith("/")
            if relpath == "/":
                return cls.RootPath
            else:
                # Strip leading "/", eliminate ".."
                return posixpath.normpath(relpath[1:])

    @classmethod
    def is_absolute_path(cls, path):
        return path.startswith("/") or cls.is_remote_path(path)

    @classmethod
    def is_remote_path(cls, path):
        return cls.is_http_path(path) or cls.is_remote_cob_path(path)

    @classmethod
    def is_http_path(cls, path):
        # "//" => remote http: or https: (protocol-neutral)
        return (path.startswith("//") or
                path.startswith("http://") or
                path.startswith("https://"))

    @classmethod
    def is_remote_cob_path(cls, path):
        return path.startswith("cob://")

    def make(self, new_path):
        """Make a new CobUrl from existing one + ``new_path``.

        Most CobUrls should be constructed with ``make``."""
        return self.__class__(self.cobroot, self.make_path(self, new_path))

    def __init__(self, cobroot, path):
        assert not path.startswith("/") or path[:2] == "//"
        assert not path.startswith(".")
        self.cobroot, self.path = cobroot, path

    def __repr__(self):
        return "<%s %r>" % (self.__class__.__name__, self.path)

    def __eq__(self, other):
        return self.key == other.key

    def serialize(self):
        return dict(path=self.path)

    @classmethod
    def deserialize(cls, context, dct):
        return cls(context.cobroot, dct['path']) if dct else None

    @property
    def abspath(self):
        return self.cobroot.join(self.path)

    @property
    def key(self):
        """A representation that can be used as a key or a value in a dict."""
        return self.cobroot.key + (self.path,)

    def join(self, first, *rest):
        """Construct a new CobUrl from ``first`` and ``*rest``"""
        assert isinstance(first, basestring), type(first)
        assert all(isinstance(r, basestring) for r in rest)
        return self.make(pathjoin(first, *rest))

    @property
    def is_local(self):
        """Belongs to local Cob"""
        return not self.is_remote_path(self.path)

    def find_by_extensions(self, path, *extensions, **kwargs):
        relpath   = self.make_path(self, path)
        filenames = self.cobroot.find_by_extensions(
            relpath, *extensions, **kwargs)
        return [self.make(pathjoin(relpath, f)) for f in filenames]

    def watch_file(self):
        self.cobroot.watch_file(self.abspath)

    @classmethod
    def watch_files(cls, *coburls):
        for coburl in coburls:
            coburl.cobroot.watch_file(coburl.abspath)

    @property
    def watched_files(self):
        return self.cobroot.watched_files

    def is_child_path(self, child):
        if self.is_remote_path(self.path) or child.is_remote_path(child.path):
            return False
        elif self.path == self.RootPath:
            return True
        else:
            return child.path.startswith(self.path + "/")

    def relpath(self, other):
        """Relative path of ``other`` to ``self``."""
        if self.is_remote_path(self.path) or other.is_remote_path(other.path):
            return other.path
        else:
            return posixpath.relpath(other.path, self.path)


class CobRoot(FileRoot):
    """The logical root of a web application.

    CobRoot manages the relationship between CobUrls
    and the underlying file system.
    """
    def __init__(self, root):
        super(CobRoot, self).__init__(root)
        self.env = webassets.Environment(root)
        self.watched_files = []

    @property
    def key(self):
        """A representation that can be used as a key or a value in a dict."""
        return (self.root,)

    def watch_file(self, filepath):
        self.watched_files.append(self.join(filepath))

    def watch_files(self, *filepaths):
        for f in filepaths:
            self.watch_file(f)
