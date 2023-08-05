# -*- coding: utf-8 -*-
"""
    slingr.testsuite.test_common
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Test common.py
"""

from __future__ import with_statement

import mock
import posixpath
import unittest
import slingr
import slingr.common
from slingr import ospath
from slingr.common import _local_path, _logical_path, OutputFileCache
from slingr.coburl import pathjoin
from slingr.testsuite import SlingrTestCase


class StructTest(SlingrTestCase):
    def test_empty(self):
        s = slingr.Struct({})
        self.assertEqual("{}", str(s))
        self.assertEqual({}, s.as_dict())

    def test_none(self):
        s = slingr.Struct(None)
        self.assertEqual("{}", str(s))
        self.assertEqual({}, s.as_dict())

    def test_complex(self):
        data = {'a': 7,
                'b': {'c': 5,
                      'd': {'e': 9, 'f': 2},
                      'g': 'gee',
                      'h': [1, 'two', 3],
                      'i': [[{'j': 14, 'k': 15}, {'j': 16, 'k': 17}]],
                      'l': [[1, 2, 3], [4, 5, 6]]}}
        s = slingr.Struct(data)
        self.assertEqual(9, s['b'].d['e'])
        self.assertEqual(7, s.a)
        self.assertEqual(5, s.b.c)
        self.assertTrue('c' in s.b)
        self.assertFalse('q' in s.b)
        self.assertEqual(9, s.b.d.e)
        self.assertEqual(2, s.b.d.f)
        self.assertEqual("gee", s.b.g)
        self.assertEqual([1, "two", 3], s.b.h)
        self.assertEqual(16, s.b.i[0][1].j)
        self.assertEqual(3, s.b.l[0][2])
        self.assertEqual(5, s.b.l[1][1])
        self.assertEqual(data, s.as_dict())
        s2 = slingr.Struct(data)
        self.assertEqual(s, s2)

    def test_reserved_word(self):
        data = {"a": 7, "from": "somewhere", "c": "++"}
        s = slingr.Struct(data)
        self.assertEqual(7, s.a)
        self.assertEqual("somewhere", getattr(s, 'from'))
        self.assertEqual("++", s.c)
        self.assertEqual(data, s.as_dict())
        for k in data.keys():
            self.assertTrue(k in s)


class ConfigReaderWriterTest(SlingrTestCase):
    def _checkext(self, expected, value, cls):
        self.assertEqual(
            expected, cls._make_filename(value))

    def _json_checkext(self, expected, value):
        self._checkext(expected, value, slingr.JsonConfigReaderWriter)

    def _yaml_checkext(self, expected, value):
        self._checkext(expected, value, slingr.YamlConfigReaderWriter)

    def test_extension_json(self):
        self._json_checkext('x.y',     'x.y')
        self._json_checkext('x.json',  'x')
        self._json_checkext('x.json',  'x.json')
        self._json_checkext('/foo/x.json',  '/foo/x')

    def test_extension_yaml(self):
        self._yaml_checkext('x.y',     'x.y')
        self._yaml_checkext('x.yaml',  'x')
        self._json_checkext('x.yaml',  'x.yaml')
        self._yaml_checkext('/foo/x.yaml',  '/foo/x')

    def test_json_save_indent(self):
        Indent = slingr.JsonConfigReaderWriter.Indent
        Default = object()

        def _test_json_save_indent(param, expected):
            data, fp = {"a": 7}, 42
            with mock.patch('slingr.json.dump') as js:
                if param is not Default:
                    slingr.JsonConfigReaderWriter.save(
                        data, fp, indent=param)
                else:
                    slingr.JsonConfigReaderWriter.save(data, fp)
                js.assert_called_once_with(data, fp, indent=expected)

        _test_json_save_indent(Default, Indent)
        _test_json_save_indent(Indent, Indent)
        _test_json_save_indent(None, None)
        _test_json_save_indent(7, 7)


class MiscTest(SlingrTestCase):
    def test_splice(self):
        l = [['a.j', 'b.j'], ['c.y', 'd.y', 'e.y'], ['f.z'], ['g.q']]
        e = ['a.j', 'b.j', 'c.y', 'd.y', 'e.y', 'f.z', 'g.q']
        self.assertEqual(e, slingr.splice(l))
        self.assertEqual(e, slingr.splice([e]))

    def test_shortname(self):
        self.assertEqual("foo", slingr.shortname("foo"))
        self.assertEqual("foo", slingr.shortname("foo.bar"))
        self.assertEqual("foo", slingr.shortname("quux/foo.bar"))
        self.assertEqual("foo", slingr.shortname("/quux/foo.bar"))
        self.assertEqual("foo", slingr.shortname("/fred/jim/sheila/foo.bar"))

    def test_uniquify(self):
        l = [
            'spam',
            {'a':1, 'b':2, 'c':3},
            'spam',
            {'c':3, 'b':2, 'a':1},
            'ham',
            None,
            False,
            'eggs',
            ]
        u = slingr.uniquify(l)
        self.assertEqual(6, len(u))
        # Check order
        self.assertEqual([
                'spam',
                {'a':1, 'c': 3, 'b':2},  # Dict key-order irrelevant
                'ham',
                None,
                False,
                'eggs',
                ], u)

    def test_find_files_by_extensions(self):
        self.maxDiff = None
        expected = sorted([
            posixpath.join('base',     'en.yaml'),
            posixpath.join('base',     'fr.yaml'),
            posixpath.join('testDir1', 'en.yaml'),
            posixpath.join('testDir1', 'fr.yaml'),
            posixpath.join('testDir2', 'en.yaml'),
            posixpath.join('testDir2', 'fr.yaml')
            ])
        lang_root = posixpath.join(self.TestDataDir, 'lang')
        abs_filenames = sorted(slingr.find_files_by_extensions(
            lang_root, '.yaml', relative=False))
        self.assertEqual(
            [_logical_path(posixpath.join(lang_root, f)) for f in expected],
            abs_filenames)
        rel_filenames = sorted(slingr.find_files_by_extensions(
            lang_root, '.yaml', relative=True))
        self.assertEqual(expected, rel_filenames)

    def test_modification_time(self):
        f = ospath.join(self.TestDataDir, "cob.yaml")
        self.assertLess(0, slingr.modification_time(f))
        self.assertIsNone(slingr.modification_time(f + "x"))


_drive_prefix = "[drv]:"


def _test_local_path(file_path):
    return _drive_prefix + file_path.replace('/', '|')


def _test_logical_path(file_path):
    assert file_path.startswith(_drive_prefix)
    return file_path[len(_drive_prefix):].replace('|', '/')


def _test_join(local_first, *local_rest):
    return ospath.join(local_first, *local_rest).replace(ospath.sep, '|')


class OutputFileCacheTest(SlingrTestCase):
    def test_rewrite_path(self):
        if ospath.sep == '\\':
            self.assertEqual('/foo/bar',  _logical_path(r'\foo\bar'))
            self.assertEqual(r'\foo\bar', _local_path('/foo/bar'))
        else:
            self.assertEqual('/foo/bar',  _logical_path('/foo/bar'))
            self.assertEqual('/foo/bar', _local_path('/foo/bar'))

    def test_local_logical(self):
        file_path = "/alpha/beta/gamma/delta"
        f1 = _test_local_path(file_path)
        f2 = _test_logical_path(f1)
        self.assertEqual(file_path, f2)

    def _make_file_cache(self, force=False):
        file_cache = OutputFileCache(
            slingr.Build.Output, force=force, local_path=_test_local_path)
        file_cache._join = _test_join
        file_cache._makedirs = mock.Mock()
        file_cache._make_parent_dest_dir = mock.Mock()
        file_cache._remove_file_if_exists = mock.Mock()
        file_cache._copystat = mock.Mock()
        return file_cache

    def test_copy(self):
        file_cache = self._make_file_cache()
        self.assertTrue(file_cache.save_state)
        path, copy = 'foo/bar', mock.Mock()
        src, dst = pathjoin('/input', path), pathjoin('/output', path)
        local_src, local_dst = _test_local_path(src), _test_local_path(dst)

        file_cache.copy(src, dst, fn=copy)
        file_cache._make_parent_dest_dir.assert_called_once_with(local_dst)
        copy.assert_called_once()
        self.assertEqual(local_src, file_cache.cache[local_dst])

        # Should be a no-op the second time
        file_cache.copy(src, dst, fn=copy)
        self.assertEqual(1, copy.call_count)  # still 1
        self.assertEqual(1, file_cache._make_parent_dest_dir.call_count)
        self.assertEqual(local_src, file_cache.cache[local_dst])

        # Force another copy
        file_cache.force = True
        file_cache.copy(src, dst, fn=copy)
        self.assertEqual(2, file_cache._make_parent_dest_dir.call_count)
        self.assertEqual(2, copy.call_count)
        self.assertEqual(local_src, file_cache.cache[local_dst])

    def test_copy_no_save_state(self):
        file_cache = self._make_file_cache()
        file_cache.save_state = False
        path, copy = 'foo/bar', mock.Mock()
        src, dst = pathjoin('/input', path), pathjoin('/output', path)
        local_src, local_dst = _test_local_path(src), _test_local_path(dst)

        file_cache.copy(src, dst, fn=copy)
        self.assertEqual(0, file_cache._make_parent_dest_dir.call_count)
        self.assertEqual(0, copy.call_count)
        self.assertEqual(local_src, file_cache.cache[local_dst])

    def test_copytree(self):
        file_cache = self._make_file_cache()
        path, copy = 'tree/root', mock.Mock()
        src_dir, dst_dir = pathjoin('/input', path), pathjoin('/output', path)

        _dst_join = lambda *f: posixpath.join(dst_dir, *f)
        _local_join = lambda d, *f: _test_join(_test_local_path(d), *f)
        _lsrc_join = lambda *f: _local_join(src_dir, *f)
        _ldst_join = lambda *f: _local_join(dst_dir, *f)

        filenames = (
            ('left',),
            ('middle', 'mean',),
            ('middle', 'average', 'blah',),
            ('middle', 'average', 'humdrum',),
            ('right',),
        )
        tree = {
            # Map directory paths to directory contents
            ():
                ('left', 'middle', 'right'),  # root's children; middle=dir
            ('middle',):
                ('mean', 'average'),          # middle's chlldren; average=dir
            ('middle', 'average'):
                ('blah', 'humdrum'),          # middle/average's chlldren
        }
        dir_contents = dict((_lsrc_join(*dirs), names)
                            for dirs, names in tree.items())
        file_cache._isdir = lambda path: path in dir_contents
        file_cache._listdir = lambda path: dir_contents[path]

        # "Copy" src_dir to dst_dir
        file_cache.copytree(src_dir, dst_dir, copy)

        expected = [mock.call(_lsrc_join(*f), _ldst_join(*f))
                    for f in filenames]
        self.assertEqual(expected, copy.mock_calls)
        self.assertEqual(len(filenames), len(file_cache.cache))
        self.assertTrue(all(file_cache.cache[_ldst_join(*f)] == _lsrc_join(*f)
                            for f in filenames))


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(StructTest))
    suite.addTest(unittest.makeSuite(ConfigReaderWriterTest))
    suite.addTest(unittest.makeSuite(MiscTest))
    suite.addTest(unittest.makeSuite(OutputFileCacheTest))
    return suite
