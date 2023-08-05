# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import localdatetime

from datetime import datetime
from five import grok
from grokcore.chameleon.components import ChameleonPageTemplate
from zope.cachedescriptors.property import Lazy
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from zope.publisher.interfaces.http import IHTTPRequest
from zope.traversing.browser import absoluteURL

from silva.app.news.datetimeutils import RRuleData
from silva.core.contentlayout.blocks import Block, BlockController
from silva.translations import translate as _
from silva.ui.rest import UIREST

from .interfaces import INewsPageVersion, IAgendaPageVersion


class NewsInfoBlock(Block):
    grok.context(INewsPageVersion)
    grok.name('news-information')
    grok.title(_(u'News information'))
    grok.order(50)


class AgendaInfoBlock(Block):
    grok.context(IAgendaPageVersion)
    grok.name('agenda-information')
    grok.title(_(u'Agenda information'))
    grok.order(50)


class NewsInfoBlockController(BlockController):
    grok.adapts(NewsInfoBlock, INewsPageVersion, IHTTPRequest)

    template = ChameleonPageTemplate(filename="templates/newsinfo.cpt")

    def __init__(self, block, version, request):
        self.version = version
        self.request = request

    @Lazy
    def url(self):
        return absoluteURL(self.version.get_content(), self.request)

    @Lazy
    def month_names(self):
        return localdatetime.get_month_names(self.request)

    def format_date(self, date, with_hours=True):
        if not isinstance(date, datetime):
            date = date.asdatetime()
        formatted = u'%s.%s.%s' % (
            date.day, self.month_names[date.month-1], date.year)
        if with_hours:
            formatted += u', %s:%s' % (
                '%02d' % date.hour, '%02d' % date.minute)
        return formatted

    @Lazy
    def publication_date(self):
        date = self.version.get_display_datetime()
        if date:
            return self.format_date(date)
        return u''

    def default_namespace(self):
        return {}

    def namespace(self):
        return {'version': self.version,
                'request': self.request,
                'view': self}

    def render(self, view=None):
        if view is None or view.final:
            return self.template.render(self)
        return _(u"This component is not available in this context.")


class AgendaInfoBlockController(NewsInfoBlockController):
    grok.adapts(AgendaInfoBlock, IAgendaPageVersion, IHTTPRequest)

    template = ChameleonPageTemplate(filename="templates/agendainfo.cpt")

    def occurrences(self):
        for occurrence in self.version.get_occurrences():
            timezone = occurrence.get_timezone()
            with_hours = not occurrence.is_all_day()

            start = occurrence.get_start_datetime(timezone)
            end = occurrence.get_end_datetime(timezone)
            end_recurrence = occurrence.get_end_recurrence_datetime()

            information = {
                'start': self.format_date(start, with_hours),
                'end': self.format_date(end, with_hours),
                'location': occurrence.get_location(),
                'recurrence_until': None}

            if end_recurrence:
                information.update({
                    'recurrence_until': self.format_date(
                        end_recurrence, with_hours),
                    'recurrence': RRuleData(
                        occurrence.get_recurrence()).get('FREQ')})

            yield information


class AddBlockREST(UIREST):
    grok.baseclass()
    grok.name('add')
    grok.require('silva.ChangeSilvaContent')

    message = _(u'Component created.')
    autoclose = 4000

    def __init__(self, context, request, configuration, restriction):
        super(AddBlockREST, self).__init__(context, request)
        self.configuration = configuration
        self.restriction = restriction

    def _create_block(self):
        raise NotImplementedError

    def GET(self):
        adding = self.__parent__
        adding.add(self._create_block())
        notify(ObjectModifiedEvent(self.context))

        return self.json_response({
                'content' : {
                    'extra': {
                        'block_id': adding.block_id,
                        'block_data': adding.block_controller.render(),
                        'block_editable': False},
                    'success': True},
                "notifications": [{
                        "category": "",
                        "message": self.message,
                        "autoclose": self.autoclose}],
                })


class AddNewsBlockREST(AddBlockREST):
    grok.adapts(NewsInfoBlock, INewsPageVersion)

    message = _(u'News information component added.')

    def _create_block(self):
        return NewsInfoBlock()


class AddAgendaBlockREST(AddBlockREST):
    grok.adapts(AgendaInfoBlock, IAgendaPageVersion)

    message = _(u'Agenda information component added.')

    def _create_block(self):
        return AgendaInfoBlock()
