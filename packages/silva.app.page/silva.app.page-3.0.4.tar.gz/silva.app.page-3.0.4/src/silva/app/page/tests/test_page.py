# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt


import unittest
from zope.component import queryUtility
from zope.interface.verify import verifyObject

from silva.app.page.interfaces import IPage, IPageVersion
from silva.app.page.testing import FunctionalLayer
from silva.core.contentlayout.interfaces import IContentLayoutService
from silva.core.interfaces import IPublicationWorkflow


class PageTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

    def search(self, path):
        return map(lambda b: (b.getPath(), b.publication_status),
                   self.root.service_catalog(path=path))

    def test_page(self):
        factory = self.root.manage_addProduct['silva.app.page']
        factory.manage_addPage('page', 'Page')

        page = self.root._getOb('page', None)
        self.assertNotEqual(page, None)
        self.assertTrue(verifyObject(IPage, page))
        self.assertTrue(verifyObject(IPageVersion, page.get_editable()))
        self.assertEqual(page.get_viewable(), None)

    def test_page_catalog(self):
        factory = self.root.manage_addProduct['silva.app.page']
        factory.manage_addPage('page', 'Page')

        page = self.root._getOb('page')
        self.assertItemsEqual(
            self.search('/root/page'),
            [('/root/page', 'unapproved'),
             ('/root/page/0', 'unapproved')])

        IPublicationWorkflow(page).publish()
        self.assertItemsEqual(
            self.search('/root/page'),
            [('/root/page', 'public'),
             ('/root/page/0', 'public')])

    def test_installation(self):
        # Service must be installed by default by the extension
        service = queryUtility(IContentLayoutService)
        self.assertNotEqual(service, None)
        self.assertTrue(verifyObject(IContentLayoutService, service))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PageTestCase))
    return suite
