# -*- coding: utf-8 -*-
"""
    slingr.testsuite.test_coburl
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Test CobUrls
"""

from __future__ import with_statement

from mock import Mock, patch
import unittest
import sys

from slingr.watch import FileWatcher, CobUrlWatcher
from slingr.coburl import CobUrl, CobRoot


from slingr.testsuite import SlingrTestCase

class FileWatcherTest(SlingrTestCase):
    def setUp(self):
        super(FileWatcherTest, self).setUp()
        self.fw = FileWatcher(None, ["/b/2", "/c/3", "/a/1", ])
        self.fw.mtimes = dict(
            (f, i+11) for i,f in enumerate(self.fw.filenames))

    def test_poll_noop(self):
        fw = FileWatcher(None, [])
        mod_time_mock = Mock(return_value=7)
        with patch('slingr.watch.modification_time', mod_time_mock):
            self.assertEqual([], fw.poll_mtimes())
            self.assertEqual(0, mod_time_mock.call_count)

    def test_poll_no_changes(self):
        with patch('slingr.watch.modification_time', Mock(return_value=7)):
            self.assertEqual([], self.fw.poll_mtimes())

    def test_poll_changes(self):
        def mod_time(fn):
            return {"/a/1": 25, "/c/3": 42}.get(fn, 1)

        with patch('slingr.watch.modification_time', mod_time):
            self.assertEqual(["/a/1", "/c/3"], self.fw.poll_mtimes())


class CobUrlWatcherTest(SlingrTestCase):
    def setUp(self):
        super(CobUrlWatcherTest, self).setUp()
        self.cobroot = CobRoot("/foo/bar")
        self.a1 = CobUrl(self.cobroot, "a/1")
        self.b2 = CobUrl(self.cobroot, "b/2")
        self.c3 = CobUrl(self.cobroot, "c/3")

    def test_notify(self):
        def _notify(coburls): pass
        watcher = CobUrlWatcher(_notify, [self.a1, self.b2, self.c3])
        rv = watcher.notify([self.a1.abspath, self.c3.abspath])
        self.assertEqual([self.a1, self.c3], rv)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FileWatcherTest))
    suite.addTest(unittest.makeSuite(CobUrlWatcherTest))
    return suite
