# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt


from silva.app.news.interfaces import INewsItemContent, INewsItemContentVersion
from silva.app.news.interfaces import IAgendaItemContent
from silva.app.news.interfaces import IAgendaItemContentVersion
from silva.app.page.interfaces import IPageContent, IPageContentVersion


class INewsPageVersion(INewsItemContentVersion, IPageContentVersion):
    """A news page version
    """


class INewsPage(INewsItemContent, IPageContent):
    """A news page.
    """


class IAgendaPageVersion(IAgendaItemContentVersion, IPageContentVersion):
    """A agenda page version
    """


class IAgendaPage(IAgendaItemContent, IPageContent):
    """An agenda page
    """
