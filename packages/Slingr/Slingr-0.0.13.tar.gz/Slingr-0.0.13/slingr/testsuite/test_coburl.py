# -*- coding: utf-8 -*-
"""
    slingr.testsuite.test_coburl
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Test CobUrls
"""

from __future__ import with_statement

import unittest
import slingr
from slingr import ospath

from slingr.testsuite import SlingrTestCase

class CobUrlTest(SlingrTestCase):
    def setUp(self):
        super(CobUrlTest, self).setUp()
        self.cobroot = slingr.CobRoot(self.TestDataDir)
        self.root = slingr.CobUrl(self.cobroot, slingr.CobUrl.RootPath)
        self.alpha_beta = slingr.CobUrl(self.cobroot, "alpha/beta")

    def test_make_path_schemeless(self):
        path = "//remote/foo/bar" # scheme-less HTTP or HTTPS
        self.assertTrue(slingr.CobUrl.is_remote_path(path))
        self.assertEqual(
            path, slingr.CobUrl.make_path(self.alpha_beta, path))

    def test_make_path_http(self):
        path = "http://remote/foo/bar"
        self.assertTrue(slingr.CobUrl.is_remote_path(path))
        self.assertEqual(
            path, slingr.CobUrl.make_path(self.alpha_beta, path))

    def test_make_path_https(self):
        path = "https://remote/foo/bar"
        self.assertTrue(slingr.CobUrl.is_remote_path(path))
        self.assertEqual(
            path, slingr.CobUrl.make_path(self.alpha_beta, path))

    def test_make_path_cob(self):
        path = "cob://cobname/foo/bar"
        self.assertTrue(slingr.CobUrl.is_remote_path(path))
        with self.assertRaises(slingr.CobUrlError):
            slingr.CobUrl.make_path(self.alpha_beta, path)

    def test_make_path_root_slash(self):
        path = "/"
        self.assertFalse(slingr.CobUrl.is_remote_path(path))
        self.assertTrue(slingr.CobUrl.is_absolute_path(path))
        self.assertEqual(
            slingr.CobUrl.RootPath,
            slingr.CobUrl.make_path(self.root, path))

    def test_make_path_root_empty(self):
        path = slingr.CobUrl.RootPath
        self.assertFalse(slingr.CobUrl.is_remote_path(path))
        self.assertFalse(slingr.CobUrl.is_absolute_path(path))
        self.assertEqual(
            slingr.CobUrl.RootPath,
            slingr.CobUrl.make_path(self.root, path))

    def test_make_path_absolute(self):
        path = "/foo/bar"
        self.assertFalse(slingr.CobUrl.is_remote_path(path))
        self.assertTrue(slingr.CobUrl.is_absolute_path(path))
        self.assertEqual(
            "foo/bar",
            slingr.CobUrl.make_path(self.alpha_beta, path))

    def test_make_path_relative(self):
        path = "foo/bar"
        self.assertFalse(slingr.CobUrl.is_remote_path(path))
        self.assertFalse(slingr.CobUrl.is_absolute_path(path))
        self.assertEqual(
            "alpha/beta/foo/bar",
            slingr.CobUrl.make_path(self.alpha_beta, path))

    def test_make_path_relative_up(self):
        path = "../foo/bar"
        self.assertFalse(slingr.CobUrl.is_remote_path(path))
        self.assertFalse(slingr.CobUrl.is_absolute_path(path))
        self.assertEqual(
            "alpha/foo/bar",
            slingr.CobUrl.make_path(self.alpha_beta, path))

    def test_abspath(self):
        self.assertEqual(
            ospath.join(self.TestDataDir, "alpha", "beta"),
            self.alpha_beta.abspath)

    def test_make_relative(self):
        self.assertEqual(
            ospath.join(self.TestDataDir, "alpha", "beta", "foo", "bar"),
            self.alpha_beta.make("foo/bar").abspath)

    def test_make_absolute(self):
        self.assertEqual(
            ospath.join(self.TestDataDir, "foo", "bar"),
            self.alpha_beta.make("/foo/bar").abspath)

    def test_serialize(self):
        dct = self.alpha_beta.serialize()
        self.assertEqual("alpha/beta", dct['path'])
        coburl = slingr.CobUrl.deserialize(self, dct)
        self.assertEqual(self.alpha_beta, coburl)

    def test_serialize_http(self):
        for p in (
            "//remote/foo/bar",
            "http://remote/foo/bar",
            "https://remote/foo/bar"
        ):
            coburl = self.root.make(p)
            dct = coburl.serialize()
            self.assertEqual(p, dct['path'])
            coburl2 = slingr.CobUrl.deserialize(self, dct)
            self.assertEqual(coburl, coburl2)

    def test_deserialize_empty(self):
        self.assertIsNone(slingr.CobUrl.deserialize(self, None))

    def test_init_dot(self):
        with self.assertRaises(AssertionError):
            slingr.CobUrl(self.cobroot, ".")

    def test_init_slash(self):
        with self.assertRaises(AssertionError):
            slingr.CobUrl(self.cobroot, "/")
        with self.assertRaises(AssertionError):
            slingr.CobUrl(self.cobroot, "/x")

    def test_init(self):
        path = "blah"
        coburl = slingr.CobUrl(self.cobroot, path)
        self.assertEqual(path, coburl.path)
        self.assertTrue(coburl.is_local)

    def test_init_schemeless(self):
        path = "//cdn.com/blah"
        coburl = slingr.CobUrl(self.cobroot, path)
        self.assertEqual(path, coburl.path)
        self.assertFalse(coburl.is_local)

    def test_init_http(self):
        path = "http://cdn.com/blah"
        coburl = slingr.CobUrl(self.cobroot, path)
        self.assertEqual(path, coburl.path)
        self.assertFalse(coburl.is_local)

    def test_init_https(self):
        path = "https://cdn.com/blah"
        coburl = slingr.CobUrl(self.cobroot, path)
        self.assertEqual(path, coburl.path)
        self.assertFalse(coburl.is_local)

    def test_relpath_same(self):
        self.assertEqual(".", self.alpha_beta.relpath(self.alpha_beta))

    def test_child_path_remote(self):
        c1 = slingr.CobUrl(self.cobroot, "https://remote/foo/bar")
        c2 = slingr.CobUrl(self.cobroot, "http://other/bar/foo")
        self.assertFalse(c1.is_child_path(c2))
        self.assertFalse(c2.is_child_path(c1))

    def test_relpath_remote(self):
        c1 = slingr.CobUrl(self.cobroot, "https://remote/foo/bar")
        c2 = slingr.CobUrl(self.cobroot, "http://other/bar/foo")
        self.assertEqual(c2.path, c1.relpath(c2))
        self.assertEqual(c1.path, c2.relpath(c1))

    def test_relpath_child_root(self):
        self.assertTrue(self.root.is_child_path(self.alpha_beta))
        self.assertEqual("alpha/beta", self.root.relpath(self.alpha_beta))

    def test_relpath_child_nonroot(self):
        alpha = self.root.join("alpha")
        self.assertTrue(alpha.is_child_path(self.alpha_beta))
        self.assertEqual("beta", alpha.relpath(self.alpha_beta))

    def test_relpath_nonchild(self):
        alpha = self.root.join("alpha")
        alphabet = self.root.join("alphabet")
        self.assertFalse(alpha.is_child_path(alphabet))
        self.assertEqual("../alphabet", alpha.relpath(alphabet))

    def test_relpath_peer(self):
        gamma = slingr.CobUrl(self.cobroot, "alpha/gamma")
        self.assertFalse(self.alpha_beta.is_child_path(gamma))
        self.assertEqual("../gamma", self.alpha_beta.relpath(gamma))

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CobUrlTest))
    return suite
