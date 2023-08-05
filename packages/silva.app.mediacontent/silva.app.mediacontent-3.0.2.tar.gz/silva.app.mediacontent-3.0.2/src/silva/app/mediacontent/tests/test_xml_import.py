# -*- coding: utf-8 -*-
# Copyright (c) 2013  Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from Products.Silva.tests.test_xml_import import SilvaXMLTestCase
from zope.interface.verify import verifyObject

from ..interfaces import IMediaContent, IMediaContentVersion
from ..testing import FunctionalLayer


class MediaContentXMLImportTestCase(SilvaXMLTestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

    def test_import_slideshow_block(self):
        importer = self.assertImportFile(
            "test_import_slideshow_block.silvaxml",
            ['/root/base', '/root/base/bear'])
        self.assertEqual(importer.getProblems(), [])

        bear = self.root.base._getOb('bear')
        self.assertTrue(verifyObject(IMediaContent, bear))
        version = bear.get_editable()
        self.assertTrue(verifyObject(IMediaContentVersion, version))
        self.assertEqual(version.get_external_url(), 'http://silvacms.org')
        self.assertEqual(version.get_link(), self.root.base)
        self.assertEqual(version.get_asset(), None)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MediaContentXMLImportTestCase))
    return suite


