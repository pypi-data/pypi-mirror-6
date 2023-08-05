# -*- coding: utf-8 -*-
"""
    slingr.testsuite.test_build
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Test Build and friends
"""

from __future__ import with_statement

import json
import yaml
import unittest
import slingr

from slingr.testsuite import SlingrTestCase


class BuildTest(SlingrTestCase):
    def test_load(self):
        b = slingr.Build.make(self.cobroot)
        self.assertEqual(['home'], b.cobstate.page_names)
        self.assertEqual(1, len(b.cobstate.global_node.views))
        self.assertTrue('view.nav', b.cobstate.global_node.views['nav'].name)

    def test_parse_page_declarations(self):
        config = slingr.Struct({
            'pages': [
                'home',
                {'page': 'about', 'route': '/about'},
                'contact',
                {'page': 'users', 'route': '/users/<user_id:int>'},
            ]})
        page_names, routes = slingr.Build.parse_page_declarations(
            config.pages)
        self.assertEqual(
            ['home', 'about', 'contact', 'users'], page_names)
        self.assertEqual(
            {'/users/<user_id:int>': 'users', '/about': 'about'}, routes)

    def test_compile_globals(self):
        b = slingr.Build.make(self.cobroot)
        b.compile_global_node({})
        for t in b.cobstate.global_node.html_templates():
            t

    def test_compile(self):
        b = slingr.Build.make(self.cobroot)
        pages = b.compile({})
        self.assertEqual(
            ["chromeWeb", "legacyWeb", "modernWeb"],
            sorted(pages["home"]))
        self.assertTrue("homeSnippet" in pages['home']['chromeWeb'].compiled.html.tree['page']['home'])
        self.assertTrue("homeSnippet" in pages['home']['modernWeb'].compiled.html.tree['page']['home'])

    def test_emit(self):
        b = slingr.Build.make(self.cobroot)
        b.set_options()
        pages = b.compile({})
        b.emit({"concatenate": False})
        css_includes = pages['home']['chromeWeb'].compiled.get_css_includes(
            '<% &CDN_ROOT %>', 'output', 'a/b', use_querystring=False)
        self.assertEqual(
            [{'url': '<% &CDN_ROOT %>/output/css/helpers.css', 'media': 'media="screen"'},
             {'url': '<% &CDN_ROOT %>/output/css/main.css', 'media': 'media="screen"'},
             {'url': '<% &CDN_ROOT %>/output/css/printer.css', 'media': 'media="print"'},
             {'url': '<% &CDN_ROOT %>/output/views/nav/css/nav.css', 'media': 'media="screen"'},
             {'url': '<% &CDN_ROOT %>/output/pages/home/chromeWeb/views/content/css/test/test.css', 'media': 'media="screen"'},
             {'url': '<% &CDN_ROOT %>/output/pages/home/chromeWeb/css/home.css', 'media': 'media="screen"'}],
            css_includes)

    def test_serialize(self):
        b = slingr.Build.make(self.cobroot)
        pages = b.compile({})
        assert pages

        dct1 = b.cobstate.serialize()
        json_str = json.dumps(dct1, indent=2)
        dct2 = json.loads(json_str)
        self.assertEqual(dct1, dct2)

        assert yaml.dump(dct1)
        dct2 = yaml.safe_load(json_str)
        self.assertEqual(dct1, dct2)

        state2 = slingr.CobState.deserialize(self, dct1)
        self.assertEqual(b.cobstate, state2)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(BuildTest))
    return suite
