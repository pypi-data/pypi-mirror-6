# -*- coding: utf-8 -*-
# Copyright (c) 2006-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass

from Products.SilvaPoll.interfaces import IServicePolls
from Products.SilvaPoll.zodbdb import DB

from five import grok
from silva.core.services.base import SilvaService
from silva.core import conf as silvaconf
from zeam.form import silva as silvaforms
from zope import interface, schema
from zope.lifecycleevent.interfaces import IObjectCreatedEvent


class ServicePolls(SilvaService):
    """Service that manages poll data
    """
    grok.implements(IServicePolls)

    meta_type = 'Silva Poll Service'
    default_service_identifier = 'service_polls'
    silvaconf.icon('ServicePolls.png')

    manage_options = (
        {'label':'Settings', 'action':'manage_settings'},
        ) + SilvaService.manage_options

    security = ClassSecurityInfo()

    _store_cookies = True
    _automatically_hide_question = True

    def _init_database(self):
        self.db = DB()

    def create_question(self, question, answers):
        return self.db.create(question, answers)

    def get_question(self, qid):
        return self.db.get(qid).question

    def set_question(self, qid, question):
        return self.db.set_question(qid, question)

    def get_answers(self, qid):
        return self.db.get(qid).answers

    def set_answers(self, qid, answers):
        return self.db.set_answers(qid, answers)

    def get_votes(self, qid):
        return self.db.get(qid).votes

    def vote(self, qid, index):
        self.db.vote(qid, index)

    def automatically_hide_question(self):
        return self._automatically_hide_question

    def store_cookies(self):
        return self._store_cookies

InitializeClass(ServicePolls)


class IServicePollsConfiguration(interface.Interface):

    _store_cookies = schema.Bool(
        title=u"Prevent visitor to vote multiple times by setting a cookie",
        default=True)
    _automatically_hide_question = schema.Bool(
        title=u"Hide by default questions from navigation and TOCs.",
        default=True)


class ServicePollsConfiguration(silvaforms.ZMIForm):
    """Configure service polls settings.
    """
    grok.context(IServicePolls)
    grok.name('manage_settings')

    label = u"Configure globals poll settings"
    fields = silvaforms.Fields(IServicePollsConfiguration)
    actions = silvaforms.Actions(silvaforms.EditAction())
    ignoreContext = False


@grok.subscribe(IServicePolls, IObjectCreatedEvent)
def service_added(service, event):
    service._init_database()
