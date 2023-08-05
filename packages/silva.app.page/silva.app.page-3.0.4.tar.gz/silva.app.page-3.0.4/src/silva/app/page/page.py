# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from zope.component import getMultiAdapter
from zope.i18n import translate
from zope.publisher.browser import TestRequest

from AccessControl import ClassSecurityInfo
from AccessControl.security import checkPermission
from App.class_init import InitializeClass

from Products.Silva.VersionedContent import VersionedContent
from Products.Silva.Version import Version

from silva.core import conf as silvaconf
from silva.core.contentlayout.interfaces import PageFields
from silva.core.contentlayout.interfaces import IBoundBlockManager
from silva.core.contentlayout.designs.design import DesignAccessors

from silva.core.interfaces.adapters import IIndexEntries
from silva.core.smi.content import IEditScreen
from silva.core.smi.settings import Settings
from silva.core.views import views as silvaviews
from silva.translations import translate as _
from silva.ui.interfaces import IJSView
from silva.ui.rest.base import Screen, PageREST
from zeam.form import silva as silvaforms

from .interfaces import IPage, IPageVersion, IPageContent
from .interfaces import IPageContentVersion


class PageContentVersion(Version, DesignAccessors):
    grok.baseclass()
    grok.implements(IPageContentVersion)

    def fulltext(self):
        fulltext = [self.get_title()]
        manager = getMultiAdapter(
            (self, TestRequest()), IBoundBlockManager)

        def collect(block_id, controller):
            fulltext.extend(controller.fulltext())

        manager.visit(collect)
        return fulltext


class PageVersion(PageContentVersion):
    """A version of a Silva Page (i.e. a web page)
    """
    security = ClassSecurityInfo()
    meta_type = 'Silva Page Version'
    grok.implements(IPageVersion)


InitializeClass(PageVersion)


class Page(VersionedContent):
    """ A Silva Page represents a web page, supporting advanced
        inline editing and content layout.
    """
    security = ClassSecurityInfo()
    grok.implements(IPage)
    meta_type = 'Silva Page'
    silvaconf.icon('page.png')
    silvaconf.version_class(PageVersion)
    silvaconf.priority(-10)


InitializeClass(Page)


class PageAddForm(silvaforms.SMIAddForm):
    """Add form for a page asset"""

    grok.context(IPage)
    grok.name(u'Silva Page')

    fields = PageFields


class PageEdit(PageREST):
    grok.adapts(Screen, IPageContent)
    grok.name('content')
    grok.implements(IEditScreen)
    grok.require('silva.ReadSilvaContent')

    def payload(self):
        if checkPermission('silva.ChangeSilvaContent', self.context):
            version = self.context.get_editable()
            if version is not None:
                view = getMultiAdapter(
                    (version, self.request), IJSView, name='content-layout')
                return view(self, identifier=version.getId())

        view = getMultiAdapter(
            (self.context, self.request), IJSView, name='content-preview')
        return view(self)


class PageDesignForm(silvaforms.SMISubEditForm):
    grok.context(IPageContent)
    grok.view(Settings)
    grok.order(10)

    label = _(u"Page template")
    fields = PageFields.omit('id', 'title')


class PageView(silvaviews.View):
    grok.context(IPageContent)

    def render(self):
        if self.content is not None:
            design = self.content.get_design()
            if design is not None:
                render = design(self.content, self.request, [self.content])
                if render is not None:
                    return render()
        msg = _('Sorry, this ${meta_type} is not viewable.',
                mapping={'meta_type': self.context.meta_type})
        return '<p>%s</p>' % translate(msg, context=self.request)


#Indexes
class PageIndexEntries(grok.Adapter):
    grok.implements(IIndexEntries)
    grok.context(IPageContent)

    def get_title(self):
        return self.context.get_title()

    def get_entries(self):
        version = self.context.get_viewable()
        if version is None:
            return []

        indexes = []
        manager = getMultiAdapter(
            (version, TestRequest()), IBoundBlockManager)

        def collect(block_id, controller):
            indexes.extend(controller.indexes())

        manager.visit(collect)

        return indexes
