# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from zope.interface import Interface

from Products.Silva.silvaxml.xmlimport import NS_SILVA_URI

from silva.core.xml import producers
from silva.app.page.silvaxml import NS_PAGE_URI
from silva.core.contentlayout.silvaxml.xmlexport import BasePageProducer
from silva.app.page.page import Page, PageVersion
from silva.app.page.news.news import NewsPage
from silva.app.page.news.news import NewsPageVersion
from silva.app.news.silvaxml.xmlexport import NewsItemVersionProducer
from silva.app.news.silvaxml.xmlexport import AgendaItemVersionProducer
from silva.app.page.news.agenda import AgendaPage, AgendaPageVersion
from silva.app.page.news.blocks import AgendaInfoBlock, NewsInfoBlock


class PageProducer(producers.SilvaVersionedContentProducer):
    """Export a Silva Page object to XML."""
    grok.adapts(Page, Interface)

    def sax(self):
        self.startElementNS(NS_PAGE_URI, 'page', {'id': self.context.id})
        self.sax_workflow()
        self.sax_versions()
        self.endElementNS(NS_PAGE_URI, 'page')


class PageVersionProducer(BasePageProducer):
    """Export a version of a Silva Page object to XML."""
    grok.adapts(PageVersion, Interface)

    def sax(self):
        self.startElementNS(NS_SILVA_URI, 'content',
                            {'version_id': self.context.id})
        self.sax_metadata()
        self.sax_design()
        self.endElementNS(NS_SILVA_URI, 'content')


class NewsPageProducer(producers.SilvaVersionedContentProducer):
    """Export a News item Page object to XML."""
    grok.adapts(NewsPage, Interface)

    def sax(self):
        self.startElementNS(NS_PAGE_URI, 'news_page', {'id': self.context.id})
        self.sax_workflow()
        self.sax_versions()
        self.endElementNS(NS_PAGE_URI, 'news_page')


class NewsPageVersionProducer(NewsItemVersionProducer, BasePageProducer):
    """ Export news item page version to XML
    """
    grok.adapts(NewsPageVersion, Interface)

    def sax_content(self):
        self.sax_design()


class AgendaPageProducer(producers.SilvaVersionedContentProducer):
    """ Export Agenda Page to XML
    """
    grok.adapts(AgendaPage, Interface)

    def sax(self):
        self.startElementNS(NS_PAGE_URI, 'agenda_page', {'id': self.context.id})
        self.sax_workflow()
        self.sax_versions()
        self.endElementNS(NS_PAGE_URI, 'agenda_page')


class AgendaPageVersionProducer(AgendaItemVersionProducer, BasePageProducer):
    """ Export Agenda Page Version to XML
    """
    grok.adapts(AgendaPageVersion, Interface)

    def sax_content(self):
        self.sax_design()


class NewsInfoBlockProducer(producers.SilvaProducer):
    """ Export AgendaInfoBlock to XML
    """
    grok.adapts(NewsInfoBlock, Interface)

    def sax(self, parent=None):
        self.startElementNS(NS_PAGE_URI, 'newsinfoblock')
        self.endElementNS(NS_PAGE_URI, 'newsinfoblock')


class AgendaInfoBlockProducer(producers.SilvaProducer):
    """ Export AgendaInfoBlock to XML
    """
    grok.adapts(AgendaInfoBlock, Interface)

    def sax(self, parent=None):
        self.startElementNS(NS_PAGE_URI, 'agendainfoblock')
        self.endElementNS(NS_PAGE_URI, 'agendainfoblock')

