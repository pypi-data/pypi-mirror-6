# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest
from datetime import datetime

from Products.Silva.testing import TestRequest, Transaction
from Products.Silva.tests.test_xml_export import SilvaXMLTestCase

from silva.core.contentlayout.interfaces import IBlockController, IBlockManager
from silva.core.contentlayout.blocks.slot import BlockSlot
from silva.core.contentlayout.blocks.text import TextBlock
from silva.core.contentlayout.designs.registry import registry
from silva.core.interfaces import IPublicationWorkflow
from silva.app.news.interfaces import IServiceNews
from zeam.component import getWrapper
from zope.component import getUtility

from ..news.blocks import NewsInfoBlock, AgendaInfoBlock
from ..testing import FunctionalLayer


class PageXMLExportTestCase(SilvaXMLTestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        with Transaction():
            self.layer.login('editor')
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addFolder('base', 'Export base')
            factory = self.root.base.manage_addProduct['silva.app.page']
            factory.manage_addPage('page', 'Page')
            design = registry.lookup_design_by_name('adesign')
            version = self.root.base.page.get_editable()
            version.set_design(design)

    def test_export_page(self):
        """Export a simple page.
        """
        exporter = self.assertExportEqual(
            self.root.base,
            'test_export_page.silvaxml')
        self.assertEqual(exporter.getZexpPaths(), [])
        self.assertEqual(exporter.getAssetPaths(), [])
        self.assertEqual(exporter.getProblems(), [])

    def test_export_page_with_page_model(self):
        """Export a page with a page model at the same time.
        """
        with Transaction():
            factory = self.root.base.manage_addProduct['silva.core.contentlayout']
            factory.manage_addPageModel('model', 'A Page Model')

            model = self.root.base.model
            model_version = model.get_editable()
            model_version.set_design(registry.lookup_design_by_name('adesign'))
            IPublicationWorkflow(model).publish()

            text_block = TextBlock(identifier='text block 1')
            controller = getWrapper(
                (text_block, model_version, TestRequest()),
                IBlockController)
            controller.text = "<div>text</div>"

            manager = IBlockManager(model_version)
            manager.add('two', text_block)
            manager.add('two', BlockSlot(identifier='slot-for-two'))
            manager.add('one', BlockSlot(
                    identifier='slot-for-one',
                    tag='div',
                    css_class='the-only-one'))

            page_version = self.root.base.page.get_editable()
            page_version.set_design(model_version)

        self.assertEquals(model_version, page_version.get_design())

        exporter = self.assertExportEqual(
            self.root.base,
            'test_export_page_with_page_model.silvaxml')
        self.assertEqual(exporter.getZexpPaths(), [])
        self.assertEqual(exporter.getAssetPaths(), [])
        self.assertEqual(exporter.getProblems(), [])

    def test_export_page_with_external_page_model(self):
        """Export a page that uses a page model that is not inside the
        export folder.
        """
        with Transaction():
            factory = self.root.manage_addProduct['silva.core.contentlayout']
            factory.manage_addPageModel('model', 'A Page Model')
            IPublicationWorkflow(self.root.model).publish()

            model_version = self.root.model.get_viewable()
            page_version = self.root.base.page.get_editable()
            page_version.set_design(model_version)

        self.assertEquals(model_version, page_version.get_design())

        exporter = self.assertExportEqual(
            self.root.base,
            'test_export_page_with_external_page_model.silvaxml')
        self.assertEqual(exporter.getZexpPaths(), [])
        self.assertEqual(exporter.getAssetPaths(), [])
        self.assertEqual(exporter.getProblems(), [])


class NewsPageXMLExportTestCase(SilvaXMLTestCase):
    layer = FunctionalLayer

    def setUp(self):
        # adding base folder
        self.root = self.layer.get_application()
        with Transaction():
            self.layer.login('editor')
            factory = self.root.manage_addProduct['silva.app.news']
            factory.manage_addNewsPublication('news', 'News')
            self.root.news.filter.set_show_agenda_items(True)
            service = getUtility(IServiceNews)
            service.add_subject('all', 'All')
            service.add_subject('other', 'Others')
            service.add_target_audience('generic', 'Generic')

    def test_export_news_info_page(self):
        # adding news page
        with Transaction():
            factory = self.root.news.manage_addProduct['silva.app.page']
            factory.manage_addNewsPage('newspage', 'A News Page')

        version = self.root.news.newspage.get_editable()
        design = registry.lookup_design_by_name('adesign')
        self.assertIsNotNone(design)
        self.assertIsNotNone(version)

        with Transaction():
            version.set_design(design)
            version.set_subjects(['all'])
            version.set_target_audiences(['generic'])
            version.set_display_datetime(datetime(2010, 9, 30, 10, 0, 0))

        # adding blocks
        IBlockManager(version).add('one', NewsInfoBlock())

        exporter = self.assertExportEqual(
            self.root.news,
            'test_export_news_page.silvaxml')
        self.assertEqual(exporter.getZexpPaths(), [])
        self.assertEqual(exporter.getAssetPaths(), [])
        self.assertEqual(exporter.getProblems(), [])

    def test_export_agenda_info_page(self):
        # adding agenda page
        with Transaction():
            factory = self.root.news.manage_addProduct['silva.app.page']
            factory.manage_addAgendaPage('agendapage', 'An Agenda Page')
            version = self.root.news.agendapage.get_editable()
            design = registry.lookup_design_by_name('adesign')

        self.assertIsNotNone(version)
        self.assertIsNotNone(design)

        with Transaction():
            version.set_design(design)
            # adding block
            IBlockManager(version).add('one', AgendaInfoBlock())

        exporter = self.assertExportEqual(
            self.root.news,
            'test_export_agenda_page.silvaxml')
        self.assertEqual(exporter.getZexpPaths(), [])
        self.assertEqual(exporter.getAssetPaths(), [])
        self.assertEqual(exporter.getProblems(), [])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PageXMLExportTestCase))
    suite.addTest(unittest.makeSuite(NewsPageXMLExportTestCase))
    return suite
