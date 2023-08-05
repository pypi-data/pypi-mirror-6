# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok

from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass

from Products.Silva.VersionedContent import VersionedContent

from silva.core import conf as silvaconf
from silva.app.news.AgendaItem import AgendaItemContent
from silva.app.news.AgendaItem import AgendaItemContentVersion
from silva.app.news.AgendaItem import AgendaItemFields
from silva.core.contentlayout.interfaces import PageFields
from zeam.form import silva as silvaforms

from ..page import PageContentVersion
from .interfaces import IAgendaPage, IAgendaPageVersion


class AgendaPageVersion(AgendaItemContentVersion, PageContentVersion):
    """An agenda page version
    """
    security = ClassSecurityInfo()
    meta_type = 'Silva Agenda Page Version'
    grok.implements(IAgendaPageVersion)


InitializeClass(AgendaPageVersion)


class AgendaPage(AgendaItemContent, VersionedContent):
    """A page that can behave as an agenda item
    """
    security = ClassSecurityInfo()
    grok.implements(IAgendaPage)
    meta_type = 'Silva Agenda Page'
    silvaconf.icon('news/agenda.png')
    silvaconf.version_class(AgendaPageVersion)
    silvaconf.priority(-8)


InitializeClass(AgendaPage)


class AgendaPageAddForm(silvaforms.SMIAddForm):
    """Add form for an agenda page.
    """
    grok.context(IAgendaPage)
    grok.name(u'Silva Agenda Page')

    fields = silvaforms.Fields(PageFields, AgendaItemFields)
