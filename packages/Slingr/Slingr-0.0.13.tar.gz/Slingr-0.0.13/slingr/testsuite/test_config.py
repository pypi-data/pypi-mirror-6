# -*- coding: utf-8 -*-
"""
    slingr.testsuite.test_config
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Test _Config and friends
"""

from __future__ import with_statement

import unittest
import slingr
import mock

from slingr.testsuite import SlingrTestCase

class GlobalConfigTest(SlingrTestCase):
    def setUp(self):
        super(GlobalConfigTest, self).setUp()
        self.data = {
            "dir" : {
                "views" : "views",
                "pages" : "pages",
                "js" : "js",
                "css" : "css",
                "html" : "html",
                "index" : "indexes",
                "static" : "static",
                "staticRequire" : "requireJs",
                "staticRoot" : "root"
                },
            "nameSpace" : {
                "js" : "appName",
                "template" : "html",
                "view" : "view",
                "page" : "page"
                },
            "defaultLang" : "en",
            "baseTemplate" : "base"
            }

    def test_load_data(self):
        gc = slingr.GlobalConfig( self.data )
        self.assertTrue(gc)
        self.assertIsNone(gc.coburl)
        self.assertEqual("en", gc.data.defaultLang)
        self.assertEqual("appName", gc.data.nameSpace.js)

    def test_roundtrip(self):
        gc = slingr.GlobalConfig( self.data )
        data2 = gc.data.as_dict()
        self.assertEqual(self.data, data2)
        gc2 = slingr.GlobalConfig( data2 )
        self.assertEqual(self.data, gc2.data.as_dict())

    def test_serialize(self):
        dct = self.validate_serialize(slingr.GlobalConfig(self.data), slingr.GlobalConfig)
        self.assertTrue("data" in dct)
        self.assertFalse("coburl" in dct)

    def test_load(self):
        gc = slingr.GlobalConfig.load(self.coburl, '', "globals")
        self.assertTrue(gc)
        self.assertTrue(isinstance(gc, slingr.GlobalConfig), "instance of derived class")
        self.assertTrue("globals" in gc.coburl.path)

    @mock.patch('slingr.app.logger.warning')
    def test_load_non_existent_fatal(self, log_warn):
        with self.assertRaises(IOError):
            gc = slingr.GlobalConfig.load(self.coburl, "adsflkjkl", "kujopiu")
        self.assertTrue(log_warn.call_args[0][0].startswith("Couldn't read"))

    @mock.patch('slingr.app.logger.warning')
    def test_load_non_existent_recoverable(self, log_warn):
        gc = slingr.GlobalConfig.load(self.coburl, "adsflkjkl", "kujopiu", file_required=False)
        self.assertIsNone(gc)
        self.assertFalse(log_warn.called)

    def _test_load_invalid_data(self, reader_cls):
        with mock.patch('slingr.app.logger.exception') as log_ex:
            with self.assertRaises(slingr.ParserError) as ex:
                gc = slingr.GlobalConfig.load(self.coburl, "invalid", "malformed", reader_cls)
            self.assertTrue(log_ex.call_args[0][0].startswith("Couldn't deserialize"))

    def test_load_invalid_json_data(self):
        self._test_load_invalid_data(slingr.JsonConfigReaderWriter)

    def test_load_invalid_yaml_data(self):
        self._test_load_invalid_data(slingr.YamlConfigReaderWriter)


class ProfilesConfigTest(SlingrTestCase):
    def setUp(self):
        super(ProfilesConfigTest, self).setUp()
        self.data = {
            "profiles" : [
                "modernWeb",
                "legacyWeb",
                "chromeWeb"
                ]
            }

    def test_load_data(self):
        pc = slingr.ProfilesConfig( self.data )
        self.assertTrue(pc)
        self.assertTrue("legacyWeb" in pc.data.profiles)


class NodeConfigTest(SlingrTestCase):
    def setUp(self):
        super(NodeConfigTest, self).setUp()
        self.data = {
            "pages" : [
		"home"
                ]
            }

    def test_load_data(self):
        pc = slingr.NodeConfig( self.data )
        self.assertTrue(pc)
        self.assertTrue("home" in pc.data.pages)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(GlobalConfigTest))
    suite.addTest(unittest.makeSuite(ProfilesConfigTest))
    suite.addTest(unittest.makeSuite(NodeConfigTest))
    return suite
