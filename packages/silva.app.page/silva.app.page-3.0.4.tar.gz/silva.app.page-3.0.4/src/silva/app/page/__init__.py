# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from Persistence import Persistent

from five import grok
from zope.interface import Interface
from zope.component import queryUtility, getUtility

from silva.core import conf as silvaconf
from silva.core.conf.installer import DefaultInstaller
from silva.core.contentlayout.interfaces import IContentLayoutService
from silva.core.contentlayout.interfaces import IDesignLookup
from silva.core.editor.interfaces import ICKEditorService
from silva.core.interfaces import IContainerPolicy

silvaconf.extension_name("silva.app.page")
silvaconf.extension_title(u"Silva Page")
silvaconf.extension_depends(
    ["Silva",
     "silva.core.contentlayout",
     "silva.app.news"])


class PagePolicy(Persistent):
    grok.implements(IContainerPolicy)

    def createDefaultDocument(self, container, title):
        factory = container.manage_addProduct['silva.app.page']
        factory.manage_addPage('index', title)
        page = container._getOb('index')
        service = getUtility(IDesignLookup)
        page.get_editable().set_design(service.default_design(page))


class PageInstaller(DefaultInstaller):
    """Installer for Page and Page Asset extension.
    """
    not_globally_addables = ['Silva News Page', 'Silva Agenda Page']

    def install_custom(self, root):
        if queryUtility(IContentLayoutService) is None:
            factory = root.manage_addProduct['silva.core.contentlayout']
            factory.manage_addContentLayoutService()
        if queryUtility(ICKEditorService) is None:
            factory = root.manage_addProduct['silva.core.editor']
            factory.manage_addCKEditorService()

        declare = queryUtility(ICKEditorService).declare_configuration
        declare('Silva Page')
        declare('Silva News Page', ['Silva Page'])
        declare('Silva Agenda Page', ['Silva News Page', 'Silva Page'])

        root.service_containerpolicy.register('Silva Page', PagePolicy, 0)


class IExtension(Interface):
    """Marker interface for our extension.
    """


install = PageInstaller("silva.app.page", IExtension)
