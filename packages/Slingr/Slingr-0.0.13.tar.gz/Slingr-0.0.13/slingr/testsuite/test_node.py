# -*- coding: utf-8 -*-
"""
    slingr.testsuite.test_asset
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Test Node and friends
"""

from __future__ import with_statement

import unittest
import slingr

from slingr.testsuite import SlingrTestCase


class NodeMapTest(SlingrTestCase):
    def test_serialize(self):
        footer = slingr.View.load(self.coburl, "views/footer")
        nav    = slingr.View.load(self.coburl, "views/nav")
        content = slingr.PageView.load(
            self.coburl.join(self.HomePath), "views/content")
        nodes = [footer, nav, content]
        nodemap = slingr.NodeMap.make(nodes)
        self.assertEqual(3, len(nodemap))
        self.validate_serialize(nodemap, slingr.NodeMap)


class NodeTest(SlingrTestCase):
    def test_load(self):
        node = slingr.Node.load(self.coburl, self.HomePath)
        self.assertEqual("_node.home", node.name)
        self.assertTrue(
            any(r[1].endswith('home.css')
                for r in node.css.resolve_contents(self.cobroot.env)))
        self.assertTrue(
            any(r[1].endswith('home.js')
                for r in node.js.resolve_contents(self.cobroot.env)))

    def test_eq(self):
        node = slingr.Node.load(self.coburl, self.HomePath)
        slingr.Node.clear_cache()
        node2 = slingr.Node.load(self.coburl, self.HomePath)
        self.assertEqual(node, node2)
        self.assertNotEqual(id(node), id(node2))

    def test_serialize(self):
        self.validate_serialize(
            slingr.Node.load(self.coburl, self.HomePath),
            slingr.Node)


class ViewTest(SlingrTestCase):
    def test_load(self):
        footer = slingr.View.load(self.coburl, "views/footer")
        self.assertEqual('view.footer', footer.name)

    def test_load_nodes(self):
        self.assertEqual(
            ['footer', 'nav'],
            sorted(slingr.View.find_node_dirs(self.coburl)))
        views = slingr.View.load_nodes(self.coburl, search=False)
        self.assertEqual(0, len(views))
        views = slingr.View.load_nodes(self.coburl, search=True)
        self.assertEqual(2, len(views))
        self.assertEqual('view.footer', views['footer'].name)
        self.assertEqual('view.nav',    views['nav'].name)

    def test_load_nodes_uniquify(self):
        views = slingr.View.load_nodes(
            self.coburl,
            names_and_prefixes=[
                ('footer', 'view'),
                ('nav', 'view'),
                ('nav', 'view'),
                ('footer', 'view'),
                ])
        self.assertEqual(2, len(views))
        self.assertEqual('view.footer', views['footer'].name)
        self.assertEqual('view.nav',    views['nav'].name)

    def test_serialize(self):
        self.validate_serialize(
            slingr.View.load(self.coburl, "views/footer"),
            slingr.View)


class PageTest(SlingrTestCase):
    def setUp(self):
        super(PageTest, self).setUp()
        slingr.Node.clear_cache()

    def page_path(self, page_name):
        return slingr.Page.node_path(page_name)

    def test_load(self):
        home = slingr.Page.load(self.coburl, self.page_path("home"))
        self.assertEqual(2, len(home.views))
        content_view = home.views['content']
        self.assertEqual('page.home._view.content', content_view.name)
        self.assertTrue(isinstance(content_view, slingr.PageView))

    def test_load_nodes(self):
        self.assertEqual(['home'], slingr.Page.find_node_dirs(self.coburl))
        pages = slingr.Page.load_nodes(self.coburl, search=False)
        self.assertEqual(0, len(pages))
        pages = slingr.Page.load_nodes(self.coburl, search=True)
        self.assertEqual(1, len(pages))
        self.assertEqual('page.home', pages['home'].name)
        self.assertEqual(
            ['pages/home/views/content/js/nav.js',
             'pages/home/views/content/js/content.js',
             'pages/home/views/footer/js/footer1.js',
             'pages/home/views/footer/js/footer2.js',
             'pages/home/views/footer/js/footer3.js',
             'pages/home/js/home.js'
            ],
            [pv.url.path for pv in pages['home'].js.pathvals],
            "augment_sheaves")

    def test_profile_view_names(self):
        def vn(profile, page_name="home"):
            return slingr.Page.profile_view_names(
                self.coburl, self.page_path(page_name), profile)
        self.assertFalse(vn('NonExistent'))
        self.assertFalse(vn('legacyWeb'))
        self.assertEqual(['nav'], vn('chromeWeb'))

    def test_config_view_names(self):
        def cn(page_name, config=None):
            config = config or slingr.Page.load_node_config(
                self.coburl, self.page_path(page_name))
            return slingr.Page.config_view_names(config)
        self.assertEqual(['content', 'footer'], cn('home'))

    def test_serialize(self):
        self.validate_serialize(
            slingr.Page.load(self.coburl, self.page_path("home")),
            slingr.Page)

    def test_asset_coburls(self):
        home = slingr.Page.load(self.coburl, self.page_path("home"))
        expected = [
            'pages/home',
            'pages/home/views/content/js/nav.js',
            'pages/home/views/content/js/content.js',
            'pages/home/views/footer/js/footer1.js',
            'pages/home/views/footer/js/footer2.js',
            'pages/home/views/footer/js/footer3.js',
            'pages/home/js/home.js',
            'pages/home/html/homeSnippet.html',
            'pages/home/html/home.html',
            'pages/home/css/home.css',
            'pages/home/views/content',
            'pages/home/views/content/js/nav.js',
            'pages/home/views/content/js/content.js',
            'pages/home/views/footer',
            'pages/home/views/footer/js/footer1.js',
            'pages/home/views/footer/js/footer2.js',
            'pages/home/views/footer/js/footer3.js',
        ]
        actual = [pv.url.path for pv in home.pathvals]
        self.assertEqual(expected, actual)


class GlobalNodeTest(SlingrTestCase):
    def setUp(self):
        super(GlobalNodeTest, self).setUp()
        slingr.Node.clear_cache()

    def test_load(self):
        gn = slingr.GlobalNode.load_with_config(self.coburl)
        self.assertEqual('', gn.coburl.path)
        self.assertEqual('cob.yaml', gn.config.coburl.path)

    def test_js_load_order(self):
        gn = slingr.GlobalNode.load_with_config(self.coburl)
        self.assertEqual(
            ['js/third-party/require-min.js',
             '//ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js',
             'js/requireConfig.js',
             'views/nav/js/nav.js',
             'js/helpers.js',
             'js/main.js'],
            [pv.url.path for pv in gn.js.pathvals],
            "augment_sheaves")

    def test_serialize(self):
        self.validate_serialize(
            slingr.GlobalNode.load_with_config(self.coburl),
            slingr.GlobalNode)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(NodeMapTest))
    suite.addTest(unittest.makeSuite(NodeTest))
    suite.addTest(unittest.makeSuite(ViewTest))
    suite.addTest(unittest.makeSuite(PageTest))
    suite.addTest(unittest.makeSuite(GlobalNodeTest))
    return suite
