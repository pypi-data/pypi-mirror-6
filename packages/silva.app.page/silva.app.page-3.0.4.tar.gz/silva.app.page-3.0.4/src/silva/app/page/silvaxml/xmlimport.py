# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from silva.core import conf as silvaconf
from silva.core.xml import NS_SILVA_URI, handlers
from silva.app.news.silvaxml import helpers
from silva.app.page.silvaxml import NS_PAGE_URI
from silva.core.contentlayout.silvaxml import NS_LAYOUT_URI
from silva.core.contentlayout.silvaxml.xmlimport import DesignHandler,\
    BlockHandler
from silva.app.page.news.blocks import NewsInfoBlock, AgendaInfoBlock


silvaconf.namespace(NS_PAGE_URI)


class PageHandler(handlers.SilvaHandler):
    silvaconf.name('page')

    def getOverrides(self):
        return {(NS_SILVA_URI, 'content'): PageVersionHandler}

    def _createContent(self, identifier):
        factory = self.parent().manage_addProduct['silva.app.page']
        factory.manage_addPage(identifier, '', no_default_version=True)

    def startElementNS(self, name, qname, attrs):
        if name == (NS_PAGE_URI, 'page'):
            self.createContent(attrs)

    def endElementNS(self, name, qname):
        if name == (NS_PAGE_URI, 'page'):
            self.notifyImport()


class PageVersionHandler(handlers.SilvaVersionHandler):

    def getOverrides(self):
        return {(NS_LAYOUT_URI, 'design'): DesignHandler}

    def _createVersion(self, identifier):
        factory = self.parent().manage_addProduct['silva.app.page']
        factory.manage_addPageVersion(identifier, '')

    def startElementNS(self, name, qname, attrs):
        if (NS_SILVA_URI, 'content') == name:
            self.createVersion(attrs)

    def endElementNS(self, name, qname):
        if (NS_SILVA_URI, 'content') == name:
            self.updateVersionCount()
            self.storeMetadata()
            self.storeWorkflow()


class NewsPageHandler(handlers.SilvaHandler):
    silvaconf.name('news_page')

    def getOverrides(self):
        return {(NS_SILVA_URI, 'content'): NewsPageVersionHandler}

    def _createContent(self, identifier):
        factory = self.parent().manage_addProduct['silva.app.page']
        factory.manage_addNewsPage(identifier, '', no_default_version=True)

    def startElementNS(self, name, qname, attrs):
        if name == (NS_PAGE_URI, 'news_page'):
            self.createContent(attrs)

    def endElementNS(self, name, qname):
        if name == (NS_PAGE_URI, 'news_page'):
            self.notifyImport()


class NewsPageVersionHandler(handlers.SilvaVersionHandler):

    def getOverrides(self):
        return {(NS_LAYOUT_URI, 'design'): DesignHandler}

    def _createVersion(self, identifier):
        factory = self.parent().manage_addProduct['silva.app.page']
        factory.manage_addNewsPageVersion(identifier, '')

    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVA_URI, 'content'):
            version = self.createVersion(attrs)

            helpers.set_as_list(version, 'target_audiences', attrs)
            helpers.set_as_list(version, 'subjects', attrs)
            helpers.set_as_naive_datetime(version, 'display_datetime', attrs)

    def endElementNS(self, name, qname):
        if name == (NS_SILVA_URI, 'content'):
            self.updateVersionCount()
            self.storeMetadata()
            self.storeWorkflow()


class AgendaPageHandler(handlers.SilvaHandler):
    silvaconf.name('agenda_page')

    def getOverrides(self):
        return {(NS_SILVA_URI, 'content'): AgendaPageVersionHandler}

    def _createContent(self, identifier):
        factory = self.parent().manage_addProduct['silva.app.page']
        factory.manage_addAgendaPage(identifier, '', no_default_version=True)

    def startElementNS(self, name, qname, attrs):
        if name == (NS_PAGE_URI, 'agenda_page'):
            self.createContent(attrs)

    def endElementNS(self, name, qname):
        if name == (NS_PAGE_URI, 'agenda_page'):
            self.notifyImport()


class AgendaPageVersionHandler(handlers.SilvaVersionHandler):

    def getOverrides(self):
        return {(NS_LAYOUT_URI, 'design'): DesignHandler}

    def _createVersion(self, identifier):
        factory = self.parent().manage_addProduct['silva.app.page']
        factory.manage_addAgendaPageVersion(identifier, '')

    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVA_URI, 'content'):
            version = self.createVersion(attrs)

            helpers.set_as_list(version, 'target_audiences', attrs)
            helpers.set_as_list(version, 'subjects', attrs)
            helpers.set_as_naive_datetime(version, 'display_datetime', attrs)
            self.occurrences = []

    def endElementNS(self, name, qname):
        if name == (NS_SILVA_URI, 'content'):
            self.result().set_occurrences(self.occurrences)
            self.updateVersionCount()
            self.storeMetadata()
            self.storeWorkflow()


class NewsInfoBlockHandler(BlockHandler):
    silvaconf.name('newsinfoblock')

    def startElementNS(self, name, qname, attrs):
        if name == (NS_PAGE_URI, 'newsinfoblock'):
            block = NewsInfoBlock()
            self._block = block

    def endElementNS(self, name, qname):
        if name == (NS_PAGE_URI, 'newsinfoblock'):
            self.add_block(self._block)
            self._block = None


class AgendaInfoBlockHandler(BlockHandler):
    silvaconf.name('agendainfoblock')

    def startElementNS(self, name, qname, attrs):
        if name == (NS_PAGE_URI, 'agendainfoblock'):
            block = AgendaInfoBlock()
            self._block = block

    def endElementNS(self, name, qname):
        if name == (NS_PAGE_URI, 'agendainfoblock'):
            self.add_block(self._block)
            self._block = None

