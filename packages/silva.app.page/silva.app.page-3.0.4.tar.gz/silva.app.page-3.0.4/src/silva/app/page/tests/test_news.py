# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt


import unittest
from zope.interface.verify import verifyObject

from silva.core.interfaces import IAddableContents
from silva.core.interfaces import IPublicationWorkflow
from silva.app.page.news.interfaces import INewsPage, INewsPageVersion
from silva.app.page.news.interfaces import IAgendaPage, IAgendaPageVersion
from silva.app.page.testing import FunctionalLayer


class NewsPageTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')
        factory = self.root.manage_addProduct['silva.app.news']
        factory.manage_addNewsPublication('news', 'News')
        # Show agenda items in the filter.
        self.root.news.filter.set_show_agenda_items(True)

    def search(self, path):
        return map(lambda b: (b.getPath(), b.publication_status),
                   self.root.service_catalog(path=path))

    def test_news_addables(self):
        """News page and Agenda page should be addable in a news
        publication by default.
        """
        root_addables = IAddableContents(self.root).get_container_addables()
        self.assertFalse('Silva News Page' in root_addables)
        self.assertFalse('Silva Agenda Page' in root_addables)
        # XXX Addable API need to be fixed for this.
        #root_addables = IAddableContents(self.root).get_all_addables()
        #self.assertFalse('Silva News Page' in root_addables)
        #self.assertFalse('Silva Agenda Page' in root_addables)

        news_addables = IAddableContents(self.root.news).get_container_addables()
        self.assertTrue('Silva News Page' in news_addables)
        self.assertTrue('Silva Agenda Page' in news_addables)
        news_addables = IAddableContents(self.root.news).get_all_addables()
        self.assertTrue('Silva News Page' in news_addables)
        self.assertTrue('Silva Agenda Page' in news_addables)


    def test_news_page(self):
        factory = self.root.news.manage_addProduct['silva.app.page']
        factory.manage_addNewsPage('item', 'Page item')

        page = self.root.news._getOb('item')
        self.assertTrue(verifyObject(INewsPage, page))
        self.assertTrue(verifyObject(INewsPageVersion, page.get_editable()))
        self.assertEqual(page.get_viewable(), None)

        IPublicationWorkflow(page).publish()
        self.assertTrue(verifyObject(INewsPageVersion, page.get_viewable()))
        self.assertEqual(page.get_editable(), None)

        # When the page is published, the news will appear in the filter.
        self.assertItemsEqual(
            map(lambda b: b.getObject(),
                self.root.news.filter.get_all_items()),
            [page.get_viewable()])

    def test_news_page_catalog(self):
        factory = self.root.news.manage_addProduct['silva.app.page']
        factory.manage_addNewsPage('item', 'Page item')

        page = self.root.news._getOb('item')
        self.assertItemsEqual(
            self.search('/root/news/item'),
            [('/root/news/item/0', 'unapproved'),
             ('/root/news/item', 'unapproved')])

        IPublicationWorkflow(page).publish()
        self.assertItemsEqual(
            self.search('/root/news/item'),
            [('/root/news/item/0', 'public'),
             ('/root/news/item', 'public')])

    def test_agenda_page(self):
        factory = self.root.news.manage_addProduct['silva.app.page']
        factory.manage_addAgendaPage('event', 'Page event')

        page = self.root.news._getOb('event')
        self.assertTrue(verifyObject(IAgendaPage, page))
        self.assertTrue(verifyObject(IAgendaPageVersion, page.get_editable()))
        self.assertEqual(page.get_viewable(), None)

        IPublicationWorkflow(page).publish()
        self.assertEqual(page.get_editable(), None)
        self.assertTrue(verifyObject(IAgendaPageVersion, page.get_viewable()))

        # When the page is published, the event will appear in the filter.
        self.assertItemsEqual(
            map(lambda b: b.getObject(),
                self.root.news.filter.get_all_items()),
            [page.get_viewable()])

    def test_agenda_page_catalog(self):
        factory = self.root.news.manage_addProduct['silva.app.page']
        factory.manage_addAgendaPage('event', 'Page event')

        page = self.root.news._getOb('event')
        self.assertItemsEqual(
            self.search('/root/news/event'),
            [('/root/news/event/0', 'unapproved'),
             ('/root/news/event', 'unapproved')])

        IPublicationWorkflow(page).publish()
        self.assertItemsEqual(
            self.search('/root/news/event'),
            [('/root/news/event/0', 'public'),
             ('/root/news/event', 'public')])

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(NewsPageTestCase))
    return suite
