# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok

from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass

from Products.Silva.VersionedContent import VersionedContent

from silva.core import conf as silvaconf
from silva.app.news.NewsItem import NewsItemContent, NewsItemFields
from silva.app.news.NewsItem import NewsItemContentVersion
from silva.core.contentlayout.interfaces import PageFields
from zeam.form import silva as silvaforms

from ..page import PageContentVersion
from .interfaces import INewsPage, INewsPageVersion


class NewsPageVersion(NewsItemContentVersion, PageContentVersion):
    """A news page version
    """
    security = ClassSecurityInfo()
    meta_type = 'Silva News Page Version'
    grok.implements(INewsPageVersion)


InitializeClass(NewsPageVersion)


class NewsPage(NewsItemContent, VersionedContent):
    """A page that can behave like a news item
    """
    security = ClassSecurityInfo()
    grok.implements(INewsPage)
    meta_type = 'Silva News Page'
    silvaconf.icon('news/news.png')
    silvaconf.version_class(NewsPageVersion)
    silvaconf.priority(-9)


InitializeClass(NewsPage)


class NewsPageAddForm(silvaforms.SMIAddForm):
    """Add form for an agenda page.
    """
    grok.context(INewsPage)
    grok.name(u'Silva News Page')

    fields = silvaforms.Fields(PageFields, NewsItemFields)
