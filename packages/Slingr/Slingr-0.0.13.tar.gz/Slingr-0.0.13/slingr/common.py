# -*- coding: utf-8 -*-
"""
Common utility code
"""

from __future__ import absolute_import

import os
os_symlink = getattr(os, 'symlink', None)
from os import listdir, makedirs, stat, unlink, path as ospath
import posixpath
import shutil
import json
import yaml
import time
import codecs
import logging

import flask
from webassets.loaders import recursive_glob

from slingr import app

__all__ = (
    "enum",
    "SlingrError",
    "Struct",
    "itersubclasses",
    "ParserError",
    "JsonConfigReaderWriter",
    "YamlConfigReaderWriter",
    "FileRoot",
    "modification_time",
    "LocalTimeFormat",
    "format_seconds",
    "get_immediate_subdirectories",
    "splice",
    "uniquify",
    "OsStatCache",
    "relative_filenames",
    "find_files_by_extensions",
    "file_open",
    "read_file",
    "write_file",
    "shortname",
    "cp",
    "symlink",
    "OutputFileCache",
    "clone_tree",
    "make_clean_dir",
    "empty_filetree",
    "ospath",
    "listdir",
    "makedirs",
    "hashfile",
    "hash_filename",
    "timeit",
)


def enum(*sequential, **named):
    # From http://stackoverflow.com/a/1695250/6364
    enums = dict(zip(sequential, range(len(sequential))), **named)
    enums['reverse_mapping'] = {value: key for key, value in enums.iteritems()}
    return type('Enum', (), enums)


class SlingrError(Exception):
    """Base class for Build-related exceptions"""


class Struct(object):
    """Recursive class for building and representing objects."""
    # Originally adapted from http://stackoverflow.com/a/6573827/6364
    def __init__(self, dct):
        """Convert dictionary ``dct`` to a Struct."""
        for k, v in (dct or {}).items():
            setattr(self, k, self._wrap(v))

    def as_dict(self):
        """Convert Struct to Python dict."""
        return dict((k, self._unwrap(v)) for k, v in self.__dict__.items())

    def __repr__(self):
        return repr(self.as_dict())

    def __getitem__(self, val):
        """Allow s['foo'] as well as s.foo"""
        return self.__dict__[val]

    def __contains__(self, val):
        """Implement `val in s`"""
        return val in self.__dict__

    def __eq__(self, other):
        return self.as_dict() == other.as_dict()

    @classmethod
    def _wrap(cls, x):
        """Recursively convert ``x`` to ``cls``"""
        if isinstance(x, dict):
            return cls(x)
        elif isinstance(x, (list, tuple)):
            return [cls._wrap(e) for e in x]
        else:
            # Assumed to be a JSON-compatible scalar: string, number, bool
            return x

    @classmethod
    def _unwrap(cls, x):
        """Recursively convert ``x`` to something JSON/Yaml-compatible."""
        if isinstance(x, cls):
            return x.as_dict()
        elif isinstance(x, list):
            return [cls._unwrap(e) for e in x]
        else:
            # Assumed to be a JSON-compatible scalar
            return x


## {{{ http://code.activestate.com/recipes/576949/ (r3)
def itersubclasses(cls, _seen=None):
    """
    Generator over all subclasses of a given class, in depth first order.
    """
    if not isinstance(cls, type):
        raise TypeError('itersubclasses must be called with '
                        'new-style classes, not %.100r' % cls)
    if _seen is None:
        _seen = set()
    try:
        subs = cls.__subclasses__()
    except TypeError:  # fails only when cls is type
        subs = cls.__subclasses__(cls)
    for sub in subs:
        if sub not in _seen:
            _seen.add(sub)
            yield sub
            for sub in itersubclasses(sub, _seen):
                yield sub


class ParserError(SlingrError):
    """Parser errors"""


class _ConfigReaderWriter(object):
    Encoding = 'utf-8'

    @classmethod
    def _make_filename(cls, filename):
        return filename if ospath.splitext(filename)[1] \
            else filename + cls.Extension

    @classmethod
    def read_config_file(
            cls, config_filename, mode='rb',
            encoding=Encoding, *args, **kwargs):
        """Read contents of ``config_filename`` and return a parsed object,
        of type ``cls._Loader``"""
        try:
            with file_open(cls._make_filename(config_filename),
                           mode=mode, encoding=encoding) as cf:
                return cls.load(cf, encoding=encoding, *args, **kwargs)
        except cls._ParserException as ex:
            app.logger.exception("Couldn't deserialize '%s'", config_filename)
            raise ParserError(ex)

    @classmethod
    def write_config_file(
            cls, data, config_filename, mode='wb',
            encoding=Encoding, *args, **kwargs):
        """Write ``data`` to``config_filename``
        in the format ``cls._Loader``"""
        with file_open(cls._make_filename(config_filename),
                       mode=mode, encoding=encoding) as cf:
            return cls.save(data, cf, encoding=encoding, *args, **kwargs)


class JsonConfigReaderWriter(_ConfigReaderWriter):
    Extension = '.json'
    _Loader = json
    _ParserException = ValueError
    Indent = 4

    @classmethod
    def load(cls, fp, encoding, *args, **kwargs):
        return json.load(fp, *args, **kwargs)

    @classmethod
    def save(cls, data, fp, indent=Indent, *args, **kwargs):
        if indent in kwargs:
            indent = indent.pop('indent')
        json.dump(data, fp, indent=indent, *args, **kwargs)


class YamlConfigReaderWriter(_ConfigReaderWriter):
    Extension = '.yaml'
    _Loader = yaml
    _ParserException = yaml.YAMLError

    @classmethod
    def load(cls, fp, encoding, *args, **kwargs):
        return yaml.safe_load(fp, *args, **kwargs)

    @classmethod
    def save(cls, data, fp, *args, **kwargs):
        yaml.safe_dump(data, fp, *args, **kwargs)


def splice(lists):
    """Convert a list of lists into a flat list"""
    # http://stackoverflow.com/a/716761/6364
    return [inner  for outer in lists  for inner in outer]


def uniquify(lst):
    """Uniquify a sequence of strings, dicts, and tuples.
    Order is preserved."""
    # Can't use set() as dicts are unhashable
    # Note: repr({'a': 1, 'b': 2) == repr({'b': 2, 'a': 1})
    set_ = dict((repr(x), x) for x in lst)
    # So we can distinguish None and other falsy values in lst
    popped = object()
    return [x for x in lst if set_.pop(repr(x), popped) != popped]


class OsStatCache(object):
    """Context Manager to cache the results of os.stat() during builds.

    This turns out to be surprisingly expensive
    and repetitive, especially on Windows."""
    os_stat = os.stat

    def __init__(self):
        self.cache = {}

    def __enter__(self):
        global os
        os.stat = self.stat

    def __exit__(self, exc_type, exc_val, exc_tb):
        global os
        os.stat = self.os_stat

    def stat(self, path):
        # We expect to use this in a single-threaded context,
        # so no locking is necessary
        rv = self.cache.get(path)
        if not rv:
            rv = self.cache[path] = self.os_stat(path)
        return rv


LocalTimeFormat = "%Y-%m-%dT%H:%M:%S"


def format_seconds(seconds, format=LocalTimeFormat):
    return time.strftime(format, time.localtime(seconds))


def modification_time(filename):
    try:
        status = stat(_local_path(filename))
        mtime = status.st_mtime
    except OSError:
        mtime = None
    return mtime


def get_immediate_subdirectories(dir):
    # http://stackoverflow.com/a/800201/6364
    return [sub for sub in listdir(_local_path(dir))
            if ospath.isdir(_local_path(ospath.join(dir, sub)))]


def _local_path(file_path):
    """Convert posix-style paths to local filesystem paths"""
    return ospath.normpath(file_path) if ospath.sep == '\\' else file_path


def _logical_path(file_path):
    """Convert local filesystem paths to posix-style paths
    (with '/' as separator)"""
    return file_path.replace('\\', '/') if ospath.sep == '\\' else file_path


def _logical_filenames(*filenames):
    return [_logical_path(f) for f in filenames]


def relative_filenames(root, *filenames):
    lroot = _local_path(root)
    filenames = [ospath.relpath(f, lroot) for f in filenames]
    return _logical_filenames(*filenames)


def find_files_by_extensions(root, *extensions, **kwargs):
    lroot = _local_path(root)
    filenames = splice([recursive_glob(lroot, '*'+ext)
                        for ext in extensions])
    if kwargs.get('relative', False):
        return relative_filenames(root, *filenames)
    else:
        return _logical_filenames(*filenames)


def file_open(file_path, mode='r', encoding=None):
    return codecs.open(_local_path(file_path), mode, encoding=encoding)


def read_file(
        file_path, mode='rb', encoding='utf-8',
        file_required=True, cls_name='?'):
    try:
        with file_open(file_path, mode=mode, encoding=encoding) as fp:
            return fp.read()
    except IOError:
        if file_required:
            app.logger.warning("Couldn't read %s('%s')", cls_name, file_path)
            raise
        else:
            return None
    except UnicodeDecodeError:
        app.logger.warning("Couldn't decode %s('%s')", cls_name, file_path)
        raise


def write_file(file_path, data, mode='wb', encoding='utf-8'):
    with file_open(file_path, mode=mode, encoding=encoding) as fp:
        fp.write(data)


def shortname(filename):
    """Converts /dir1/dir2/filename.ext to filename"""
    return ospath.splitext(ospath.basename(filename))[0]


def _pre_copy(src, dst):
    src, dst = _local_path(src), _local_path(dst)
    dst_dir = ospath.dirname(dst)
    if not ospath.exists(dst_dir):
        makedirs(dst_dir)
    return src, dst


def cp(src, dst):
    src, dst = _pre_copy(src, dst)
    if not ospath.exists(dst):
        shutil.copy2(src, dst)


def symlink(src, dst):
    src, dst = _pre_copy(src, dst)
    if not ospath.exists(dst):
        os_symlink(src, dst)


class OutputFileCache(object):
    """Manage copying files to output directory.

    The cache prevents duplicate writes (e.g., a stylesheet
    used in a top-level view, which is present on every page).
    It also serves as in-memory symlinks so that we can
    avoid writing lots of files to disk in dev mode.
    """
    def __init__(
            self, output_path,
            force=False, local_path=_local_path, save_state=True):
        self.output_path = output_path
        self.force, self.local_path, self.save_state = (
            force, local_path, save_state)
        self.cache = {}

    def _listdir(self, local_src_dir):
        return os.listdir(local_src_dir)

    def _isdir(self, local_src):
        return ospath.isdir(local_src)

    def _join(self, local_first, *local_rest):
        return ospath.join(local_first, *local_rest)

    def _makedirs(self, local_dst_dir):
        makedirs(local_dst_dir)

    def _make_parent_dest_dir(self, local_dst):
        local_dst_dir = ospath.dirname(local_dst)
        if not ospath.exists(local_dst_dir):
            self._makedirs(local_dst_dir)

    def _remove_file_if_exists(self, local_dst):
        if ospath.isfile(local_dst):
            unlink(local_dst)

    def _copystat(self, local_src, local_dst):
        try:
            if self.force or self.save_state:
                shutil.copystat(local_src, local_dst)
        except OSError, why:
            if (shutil.WindowsError is not None
                    and isinstance(why, shutil.WindowsError)):
                pass  # Copying file access times may fail on Windows
            else:
                raise

    def _copy(self, fn, label, src, dst):
        local_src = self.local_path(src)
        local_dst = self.local_path(dst)
        assert self.cache.get(local_dst, -1) in (local_src, -1), "dupe or new"
        if self.force or local_dst not in self.cache:
            if self.force or self.save_state:
                # Do not write files to disk in dev-mode.
                # Considerably shortens rebuild time.
                self._make_parent_dest_dir(local_dst)
                self._remove_file_if_exists(local_dst)
                fn(local_src, local_dst)
            self.cache[local_dst] = local_src

    def copy(self, src, dst, fn=shutil.copy2):
        """Copy file `src` to file `dst`."""
        self._copy(fn, "copy", src, dst)

    def symlink(self, src, dst, fn=os_symlink):
        """Symlink file `src` to file `dst`."""
        self._copy(fn, "symlink", src, dst)

    def copytree(self, src_dir, dst_dir, fn=shutil.copy2):
        """Recursively copy a directory tree.

        Same semantics as shutil.copytree, but simplified"""
        local_src_dir = self.local_path(src_dir)
        local_dst_dir = self.local_path(dst_dir)
        if self.save_state:
            self._makedirs(local_dst_dir)
        for name in self._listdir(local_src_dir):
            srcname = posixpath.join(src_dir, name)
            dstname = posixpath.join(dst_dir, name)
            if self._isdir(self._join(local_src_dir, name)):
                self.copytree(srcname, dstname, fn)
            else:
                self.copy(srcname, dstname, fn)
        self._copystat(local_src_dir, local_dst_dir)

    def clone_tree(self, src, dst, use_symlink=False):
        if use_symlink and self.save_state:
            # Can only use symlinks when persisting to disk
            self._make_parent_dest_dir(self.local_path(dst))
            self.symlink(src, dst)
        else:
            self.copytree(src, dst)

    def get_filename(self, output_folder, url_filename):
        """Return path to static file.

        Use original instance of file, if possible.
        (Think of this cache as a set of in-memory symlinks.)
        Otherwise, assume file exists in `output_folder`;
        generated files are written there directly,
        bypassing this cache."""
        assert output_folder == self.output_path
        local_dst = self.local_path(
            flask.safe_join(output_folder, url_filename))
        local_src = self.cache.get(local_dst)
        return local_src or local_dst


def clone_tree(src, dst, use_symlink=False):
    src, dst = _local_path(src), _local_path(dst)
    if use_symlink:
        dst_dir = ospath.dirname(dst)
        if not ospath.exists(dst_dir):
            makedirs(dst_dir)
        os_symlink(src, dst)
    else:
        shutil.copytree(src, dst)


def make_clean_dir(root, *sub_dir):
    dir = ospath.join(root, *sub_dir)
    if ospath.isdir(dir):
        shutil.rmtree(dir)
    makedirs(dir)


def empty_filetree(root, *sub_dir):
    """remove files from `sub_dir`, but leave directories"""
    dir = ospath.join(root, *sub_dir)
    for the_file in listdir(dir):
        file_path = ospath.join(dir, the_file)
        try:
            if ospath.isfile(file_path):
                unlink(file_path)
        except IOError:
            pass


def hashfile(filename, hasher, blocksize=65536):
    # don't need to worry about codecs or newline translation,
    # so use plain open('rb')
    with open(filename, 'rb') as fp:
        buf = fp.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = fp.read(blocksize)
        return hasher


def hash_filename(hasher, char_count=16):
    return hasher.hexdigest()[:char_count]


class FileRoot(object):
    """File operations relative to a root directory"""
    def __init__(self, root):
        self.root = ospath.abspath(root)

    def __repr__(self):
        return "<%s root=%r>" % (self.__class__.__name__, self.root)

    def __eq__(self, other):
        return self.root == other.root

    def join(self, first, *rest):
        return ospath.abspath(ospath.join(self.root, first, *rest))

    def relpath(self, path):
        return ospath.relpath(path, self.root)

    def relative_filenames(self, *filenames):
        return relative_filenames(self.root, *filenames)

    def find_by_extensions(self, relpath, *extensions, **kwargs):
        return find_files_by_extensions(
            self.join(relpath), *extensions, **kwargs)


def timeit(method):
    """Decorator that logs timing information for a method."""

    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        delta = time.time() - ts

#       logging.info('%r (%r, %r) %2.2f sec' % (method.__name__, args, kw, delta))
        logging.info('%r %2.2f sec' % (method.__name__, delta))
        return result

    return timed
