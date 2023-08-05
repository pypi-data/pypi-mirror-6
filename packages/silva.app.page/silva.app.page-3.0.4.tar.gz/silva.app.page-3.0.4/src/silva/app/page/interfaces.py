# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from silva.core.interfaces import IVersion,  IVersionedContent
from silva.core.contentlayout.interfaces import IPage as IBasicPage
from silva.core.contentlayout.interfaces import IPageAware


class IPageContent(IVersionedContent, IPageAware):
    """ Basic page feature

    This content supports advanced inline editing and content
    layout. Use this class to extend a page.
    """


class IPage(IPageContent):
    """A page
    """


class IPageContentVersion(IVersion, IBasicPage):
   """Basic page version feature
   """


class IPageVersion(IPageContentVersion):
    """A page version
    """

