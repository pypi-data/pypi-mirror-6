# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from Acquisition import aq_chain
from zope.interface.verify import verifyObject

from Products.Silva.tests.test_xml_import import SilvaXMLTestCase
from silva.app.page.news.interfaces import IAgendaPage, IAgendaPageVersion
from silva.app.page.news.interfaces import INewsPage, INewsPageVersion
from silva.app.page.news.blocks import NewsInfoBlock, AgendaInfoBlock
from silva.app.page.interfaces import IPage, IPageVersion
from silva.core.contentlayout.interfaces import IBlockManager
from silva.core.contentlayout.interfaces import IPageModel, IPageModelVersion

from ..testing import FunctionalLayer


class PageXMLImportTestCase(SilvaXMLTestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

    def test_import_page(self):
        """Import a simple page.
        """
        importer = self.assertImportFile(
            "test_import_page.silvaxml",
            ['/root/base',
             '/root/base/page'])
        self.assertEqual(importer.getProblems(), [])
        page = self.root.base._getOb('page')
        self.assertTrue(verifyObject(IPage, page))
        page_version = page.get_editable()
        self.assertTrue(verifyObject(IPageVersion, page_version))
        design = page_version.get_design()
        self.assertTrue(design)

    def test_import_with_page_model(self):
        """Import a page with a page model at the same time.
        """
        importer = self.assertImportFile(
            "test_import_page_with_page_model.silvaxml",
            ['/root/base/page',
             '/root/base/model',
             '/root/base'])
        self.assertEqual(importer.getProblems(), [])

        page = self.root.base._getOb('page')
        self.assertTrue(verifyObject(IPage, page))
        page_version = page.get_editable()
        self.assertTrue(verifyObject(IPageVersion, page_version))
        model = self.root.base._getOb('model')
        self.assertTrue(verifyObject(IPageModel, model))

        page_model = page_version.get_design()
        model_version = model.get_viewable()
        self.assertTrue(verifyObject(IPageModelVersion, page_model))
        self.assertTrue(verifyObject(IPageModelVersion, model_version))
        self.assertEqual(model_version, page_model)
        self.assertEqual(aq_chain(model_version), aq_chain(page_model))

    def test_import_with_page_model_ignore_top_level(self):
        """Import a page with a page model while ignoring the top
        level container. In that case, the page should still use the
        imported page model.
        """
        importer = self.assertImportFile(
            "test_import_page_with_page_model.silvaxml",
            ['/root/page',
             '/root/model'], ignore_top_level=True)
        self.assertEqual(importer.getProblems(), [])

        page = self.root._getOb('page')
        self.assertTrue(verifyObject(IPage, page))
        page_version = page.get_editable()
        self.assertTrue(verifyObject(IPageVersion, page_version))
        model = self.root._getOb('model')
        self.assertTrue(verifyObject(IPageModel, model))

        page_model = page_version.get_design()
        model_version = model.get_viewable()
        self.assertTrue(verifyObject(IPageModelVersion, page_model))
        self.assertTrue(verifyObject(IPageModelVersion, model_version))
        self.assertEqual(model_version, page_model)
        self.assertEqual(aq_chain(model_version), aq_chain(page_model))

    def test_import_page_existing_rename_with_external_page_model(self):
        """Import a page when an item with the same identifier
        already exists. In addition to this, the page uses a page
        model that is not included inside the import.
        """
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addMockupVersionedContent('page', 'Existing page')
        factory = self.root.manage_addProduct['silva.core.contentlayout']
        factory.manage_addPageModel('model', 'Existing model')

        importer = self.assertImportFile(
            "test_import_page_with_external_page_model.silvaxml",
            ['/root/import_of_page'], ignore_top_level=True)
        self.assertEqual(importer.getProblems(), [])

    def test_import_news_page(self):
        """Import a news page.
        """
        importer = self.assertImportFile(
            "test_import_news_page.silvaxml",
            ['/root/news/index',
             '/root/news/newspage',
             '/root/news/filter',
             '/root/news'])
        self.assertEqual(importer.getProblems(), [])

        base = self.root._getOb('news')
        news_page = base._getOb('newspage')
        self.assertTrue(verifyObject(INewsPage, news_page))
        version = news_page.get_editable()
        self.assertTrue(verifyObject(INewsPageVersion, version))
        self.assertIsNot(version.get_design(), None)

        manager = IBlockManager(version)
        slot = manager.get_slot('one')
        _, block = slot[0]
        self.assertIsInstance(block, NewsInfoBlock)

    def test_import_agenda_page(self):
        """Import an agenda page.
        """
        importer = self.assertImportFile(
            "test_import_agenda_page.silvaxml",
            ['/root/news/index',
             '/root/news/agendapage',
             '/root/news/filter',
             '/root/news'])
        self.assertEqual(importer.getProblems(), [])

        base = self.root._getOb('news')
        agenda_page = base._getOb('agendapage')
        self.assertTrue(verifyObject(IAgendaPage, agenda_page))
        version = agenda_page.get_editable()
        self.assertTrue(verifyObject(IAgendaPageVersion, version))
        design = version.get_design()
        self.assertIsNot(design, None)

        manager = IBlockManager(version)
        slot = manager.get_slot('one')
        _, block = slot[0]
        self.assertIsInstance(block, AgendaInfoBlock)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PageXMLImportTestCase))
    return suite
