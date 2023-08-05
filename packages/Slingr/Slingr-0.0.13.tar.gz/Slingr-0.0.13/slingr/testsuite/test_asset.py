# -*- coding: utf-8 -*-
"""
    slingr.testsuite.test_asset
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Test the asset classes
"""

from __future__ import with_statement

import unittest
import slingr
import mock

from slingr.testsuite import SlingrTestCase

class PathValTest(SlingrTestCase):
    def setUp(self):
        super(PathValTest, self).setUp()
        self.node_coburl = self.coburl.join("page/down")

    def test_serialize(self):
        pv = slingr.PathVal.make(self.node_coburl)
        self.validate_serialize(pv, slingr.PathVal)
        self.assertTrue(pv.is_simple)

    def test_serialize_css(self):
        pv = slingr.CssPathVal.make(self.node_coburl)
        self.validate_serialize(pv, slingr.CssPathVal)
        self.assertTrue(pv.is_simple)

    def test_serialize_css_media(self):
        pv = slingr.CssPathVal.make(self.node_coburl, media="screen, tty")
        self.validate_serialize(pv, slingr.CssPathVal)
        self.assertFalse(pv.is_simple)

    def test_css_equal(self):
        media = "screen, tty"
        pv1 = slingr.CssPathVal.make(self.node_coburl, media=media)
        pv2 = slingr.CssPathVal.make(self.node_coburl, media=media)
        self.assertEqual(pv1, pv2)
        self.assertFalse(pv1.is_simple)
        self.assertFalse(pv2.is_simple)

    def test_css_not_equal(self):
        media = "screen, tty"
        pv1 = slingr.CssPathVal.make(self.node_coburl, media=media)
        pv2 = slingr.CssPathVal.make(self.node_coburl, media=media+", aural")
        self.assertNotEqual(pv1, pv2)
        self.assertFalse(pv1.is_simple)
        self.assertFalse(pv2.is_simple)

    def test_css_not_equal_no_media(self):
        media = "screen, tty"
        pv1 = slingr.CssPathVal.make(self.node_coburl, media=media)
        pv2 = slingr.CssPathVal.make(self.node_coburl)
        self.assertNotEqual(pv1, pv2)
        self.assertFalse(pv1.is_simple)
        self.assertTrue(pv2.is_simple)

    def test_css_not_equal_different_urls(self):
        media = "screen, tty"
        pv1 = slingr.CssPathVal.make(self.node_coburl, media=media)
        pv2 = slingr.CssPathVal.make(self.coburl, media=media)
        self.assertNotEqual(pv1, pv2)
        self.assertFalse(pv1.is_simple)
        self.assertFalse(pv2.is_simple)


class AssetNameTest(SlingrTestCase):
    def test_serialize(self):
        an = slingr.AssetName(
            slingr.PathVal.make(self.coburl), "foo/bar/baz", 12345)
        self.validate_serialize(an, slingr.AssetName)

class TemplateTreeTest(SlingrTestCase):
    def test_add_leaf(self):
        tt = slingr.TemplateTree()
        self.assertEqual(0, len(tt.tree))
        tt.add_leaf(('foo', 'bar'), 'quux', "hello")
        self.assertEqual("hello", tt.tree['foo']['bar']['quux'])
        tt.add_leaf(('foo', 'bar'), 'somefink', "goodbye")
        self.assertEqual("goodbye", tt.tree['foo']['bar']['somefink'])

    def test_html_template(self):
        ht = slingr.HtmlTemplate.make_template_tree()
        self.assertTrue('page' in ht.tree)
        self.assertTrue('view' in ht.tree)
        self.assertTrue('html' in ht.tree)

    def test_html_template_serialize(self):
        coburl = self.coburl.join("down", "below")
        ht = slingr.HtmlTemplate(['foo', 'bar'], coburl, "some data")
        self.validate_serialize(ht, slingr.HtmlTemplate)


class HtmlSheafTest(SlingrTestCase):
    def load_sheaf(self, path=None, name=None):
        path = self.HomePath if path is None else path
        ac = slingr.NodeConfig.load(self.coburl, path, "config")
        return slingr.HtmlSheaf.load_sheaf(
            name or "foo.bar", self.coburl.join(self.HomePath), "", ac)

    def test_load(self):
        hs = self.load_sheaf()
        self.assertEqual("pages/home/html/homeSnippet.html",
                         hs.templates[0].coburl.path)
        self.assertEqual(['foo', 'bar'], hs.templates[0].branch_path)
        self.assertTrue("{{homeSnippetContent}}" in hs.templates[0].data)

    def test_serialize(self):
        self.validate_serialize(self.load_sheaf(), slingr.HtmlSheaf)


class AssetBundleTest(SlingrTestCase):
    Paths = [
        "//cdn.com/x/y",       # schemeless HTTP(S) remote
        "foo",                 # relative local
        "bar/1",               # relative local
        "bar/2",               # relative local
        "http://cdn.com/a/b",  # HTTP remote
        "/quux/3",             # local absolute
    ]
    Reldir = "rel/a/tive"
    Target_filename = 'target'
    Preamble_filename = 'preamble'
    maxDiff = 5000

    def setUp(self):
        super(AssetBundleTest, self).setUp()
        self.node_coburl = self.coburl.join("page/down")

    def test_Xpend(self):
        pathvals = [slingr.PathVal.make(self.coburl),
                   slingr.PathVal.make(self.coburl.join("foo"))]
        ab = slingr.AssetBundle(pathvals)
        self.assertEqual(pathvals, ab.pathvals)

        bar = [slingr.PathVal.make(self.coburl.join("bar"))]
        ab.prepend(bar)
        self.assertEqual(bar + pathvals, ab.pathvals)

        quux = [slingr.PathVal.make(self.coburl.join("quux"))]
        ab.append(quux)
        self.assertEqual(bar + pathvals + quux, ab.pathvals)

    def _compute_op_assets(
            self, expected,
            node_coburl=None, coburls=None, paths=Paths,
            reldir=Reldir, target_filename=Target_filename,
            concatenate=None,
            preamble=None, preamble_filename=Preamble_filename):
        if node_coburl is None:
            node_coburl = self.node_coburl
        if coburls is None:
            coburls = [slingr.PathVal.make(node_coburl.join(p))
                       for p in paths]
        ab = slingr.AssetBundle(coburls)
        expected = [
            (op, slingr.PathVal.make(self.coburl.join(s)) if s else None, t)
            for op, s, t in expected]
        with mock.patch("slingr.asset.modification_time",
                        new=mock.Mock(return_value=7)):
            with mock.patch("slingr.asset.hashfile"):
                with mock.patch("slingr.asset.hash_filename",
                                new=mock.Mock(return_value="HASH")):
                    op_assets = ab.compute_op_assets(
                        node_coburl, reldir, target_filename, concatenate,
                        preamble, preamble_filename)
                    actual = [
                        (op, an.source, an.target) for op,an in op_assets]
                    self.assertEqual(expected, actual)
                    return op_assets

    def test_compute_op_assets_no_concat_no_preamble(self):
        Ops = slingr.AssetBundle.Ops
        self._compute_op_assets(
            [(Ops.Name, "//cdn.com/x/y",   "//cdn.com/x/y"),
             (Ops.Copy, 'page/down/foo',   'rel/a/tive/foo'),
             (Ops.Copy, 'page/down/bar/1', 'rel/a/tive/bar/1'),
             (Ops.Copy, 'page/down/bar/2', 'rel/a/tive/bar/2'),
             (Ops.Name, "http://cdn.com/a/b",   "http://cdn.com/a/b"),
             (Ops.Copy, 'quux/3',          'quux/3')],
            concatenate=False)

    def test_compute_op_assets_no_concat_preamble(self):
        Ops = slingr.AssetBundle.Ops
        self._compute_op_assets(
            [(Ops.Preamble, None,   'rel/a/tive/HASH_preamble'),
             (Ops.Name, "//cdn.com/x/y",   "//cdn.com/x/y"),
             (Ops.Copy, 'page/down/foo',   'rel/a/tive/foo'),
             (Ops.Copy, 'page/down/bar/1', 'rel/a/tive/bar/1'),
             (Ops.Copy, 'page/down/bar/2', 'rel/a/tive/bar/2'),
             (Ops.Name, "http://cdn.com/a/b",   "http://cdn.com/a/b"),
             (Ops.Copy, 'quux/3',          'quux/3')],
            concatenate=False, preamble="x")

    def test_compute_op_assets_concat_no_preamble(self):
        Ops = slingr.AssetBundle.Ops
        self._compute_op_assets(
            [(Ops.Name,    "//cdn.com/x/y",   "//cdn.com/x/y"),
             (Ops.Combine, 'page/down/foo',   None),
             (Ops.Combine, 'page/down/bar/1', None),
             (Ops.Combine, 'page/down/bar/2', None),
             (Ops.Name,    "http://cdn.com/a/b",   "http://cdn.com/a/b"),
             (Ops.Combine, 'quux/3',          None),
             (Ops.CombineTarget, None,   'rel/a/tive/HASH_target')],
            concatenate=True, preamble=None)

    def test_compute_op_assets_concat_preamble(self):
        Ops = slingr.AssetBundle.Ops
        self._compute_op_assets(
            [(Ops.Preamble, None,   'rel/a/tive/HASH_preamble'),
             (Ops.Name,    "//cdn.com/x/y",   "//cdn.com/x/y"),
             (Ops.Combine, 'page/down/foo',   None),
             (Ops.Combine, 'page/down/bar/1', None),
             (Ops.Combine, 'page/down/bar/2', None),
             (Ops.Name,    "http://cdn.com/a/b",   "http://cdn.com/a/b"),
             (Ops.Combine, 'quux/3',          None),
             (Ops.CombineTarget, None,   'rel/a/tive/HASH_target')],
            concatenate=True, preamble="x")

    def test_compute_op_assets_no_coburls_no_preamble(self):
        for concatenate in (False, True):
            self._compute_op_assets(
                [],
                coburls=[],
                concatenate=concatenate, preamble=None)

    def test_compute_op_assets_no_coburls_preamble(self):
        Ops = slingr.AssetBundle.Ops
        for concatenate in (False, True):
            self._compute_op_assets(
                [(Ops.Preamble, None,   'rel/a/tive/HASH_preamble')],
                coburls=[],
                concatenate=concatenate, preamble="x")


class JavaScriptBundleTest(SlingrTestCase):
    def load_sheaf(self):
        ac = slingr.NodeConfig.load(self.coburl, self.HomePath, "config")
        return slingr.JavaScriptBundle.load_sheaf(
            "foo.bar", self.coburl.join(self.HomePath), "", ac)

    def test_load(self):
        js = self.load_sheaf()
        self.assertEqual(["pages/home/js/home.js"],
                         [pv.url.path for pv in js.pathvals])

    def test_load_missing(self):
        bad_js = "ASDfjkalsjf.js"
        js = slingr.JavaScriptBundle(
            [slingr.PathVal.make(self.coburl.make(bad_js))])
        with mock.patch("slingr.asset.write_file"):
            with mock.patch('slingr.app.logger.warning') as log_warn:
                js.compute_op_assets(
                    self.coburl, "", "x.js", concatenate=True)
                self.assertGreaterEqual(
                    log_warn.call_args[0][0].find(
                        "Can't read '{}'".format(bad_js)), 0)

    def test_serialize(self):
        self.validate_serialize(self.load_sheaf(), slingr.JavaScriptBundle)


class LangSheafTest(SlingrTestCase):
    def load_sheaf(self, path=None, name=None):
        path = self.HomePath if path is None else path
        ac = slingr.NodeConfig.load(self.coburl, path, "config")
        return slingr.LangSheaf.load_sheaf(
            name or "foo.bar", self.coburl.join(self.HomePath), "", ac)

    def test_load(self):
        ls = self.load_sheaf()
        self.assertEqual(
            # FIXME
            ['pages/home/pages/home/lang/base/en.yaml',
             'pages/home/pages/home/lang/base/fr.yaml',
             'pages/home/pages/home/lang/home/en.yaml',
             'pages/home/pages/home/lang/home/fr.yaml'],
            sorted(pv.url.path for pv in ls.pathvals))

    def test_serialize(self):
        self.validate_serialize(self.load_sheaf(), slingr.LangSheaf)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AssetNameTest))
    suite.addTest(unittest.makeSuite(TemplateTreeTest))
    suite.addTest(unittest.makeSuite(HtmlSheafTest))
    suite.addTest(unittest.makeSuite(AssetBundleTest))
    suite.addTest(unittest.makeSuite(JavaScriptBundleTest))
    suite.addTest(unittest.makeSuite(LangSheafTest))
    return suite
