# -*- coding: utf-8 -*-
# Copyright (c) 2006-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from datetime import datetime
import os

from five import grok
from zope.intid.interfaces import IIntIds
from zope.component import getUtility, getMultiAdapter
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.traversing.browser import absoluteURL
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

from localdatetime import get_formatted_date, get_locale_info

from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass
from DateTime import DateTime

from Products.Formulator.Form import ZMIForm
from Products.Formulator.XMLToForm import XMLToForm

from Products.Silva import SilvaPermissions
from Products.Silva.Version import Version
from Products.Silva.VersionedContent import VersionedContent
from Products.SilvaExternalSources.ExternalSource import ExternalSource
from Products.SilvaExternalSources.interfaces import IExternalSource
from Products.SilvaPoll.interfaces import IPollQuestion, IPollQuestionVersion
from Products.SilvaPoll.interfaces import IServicePolls

from silva.core import conf as silvaconf
from silva.core.interfaces.events import IContentPublishedEvent
from silva.core.services.interfaces import IMetadataService
from silva.core.views import views as silvaviews
from silva.core.views.httpheaders import HTTPResponseHeaders
from silva.fanstatic import need


def convert_datetime(dt):
    if isinstance(dt, DateTime):
        return dt.asdatetime()
    return dt


class QuestionResponseHeaders(HTTPResponseHeaders):
    """Disable cache on poll questions.
    """
    grok.adapts(IBrowserRequest, IPollQuestion)

    def cachable(self):
        return False


class PollQuestion(VersionedContent, ExternalSource):
    """This Silva extension enables users to conduct polls inside Silva sites.
       A Question is posed to the public and results of the answers are
       displayed to those that respond. The poll can be an independent page
       or be embedded in a document as a Code Source.
    """
    security = ClassSecurityInfo()
    meta_type = 'Silva Poll Question'
    grok.implements(IPollQuestion, IExternalSource)

    silvaconf.icon("PollQuestion.png")
    silvaconf.version_class('PollQuestionVersion')

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'to_html')
    def to_html(self, context, request, **parameters):
        """Return HTMl for ExternalSource interface.
        """
        if parameters.get('display', 'normal') == 'link':
            url = absoluteURL(self, request)
            # Should make it more sense to put the title as link ?
            return '<p class="p"><a href="%s">%s</a></p>' % (url, url)

        # Render the default view as source content.
        # This will change again caching headers. (XXX Messy).
        return getMultiAdapter((self, request), name='content.html')()


InitializeClass(PollQuestion)


def cookie_identifier(content):
    return 'poll_cookie_%d' % getUtility(IIntIds).register(content)


class PollQuestionVersion(Version):
    """A poll question version.
    """
    # XXX Why having version if you can't edit them after a while ?
    meta_type = 'Silva Poll Question Version'
    grok.implements(IPollQuestionVersion)
    security = ClassSecurityInfo()

    qid = None
    _question_start_datetime = None
    _question_end_datetime = None
    _result_start_datetime = None
    _result_end_datetime = None

    def get_service(self):
        return getUtility(IServicePolls)

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_question')
    def set_question(self, question):
        self.get_service().set_question(self.qid, question)

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_answers')
    def set_answers(self, answers):
        self.get_service().set_answers(self.qid, answers)

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_question')
    def get_question(self):
        """returns a string"""
        return self.get_service().get_question(self.qid)

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_answers')
    def get_answers(self):
        """returns a list of strings"""
        return self.get_service().get_answers(self.qid)

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'get_votes')
    def get_votes(self):
        """returns a list of ints"""
        return self.get_service().get_votes(self.qid)

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'vote')
    def vote(self, request, answer):
        service = self.get_service()
        answers = service.get_answers(self.qid)

        id = answers.index(answer)
        service.vote(self.qid, id)
        if service.store_cookies():
            response = request.response
            response.setCookie(
                cookie_identifier(self.get_content()), '1',
                expires='Wed, 19 Feb 2020 14:28:00 GMT', path='/')

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'has_voted')
    def has_voted(self, request):
        if not self.get_service().store_cookies():
            return False
        return request.has_key(cookie_identifier(self.get_content()))

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'question_start_datetime')
    def question_start_datetime(self):
        return convert_datetime(self._question_start_datetime)

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_question_start_datetime')
    def set_question_start_datetime(self, dt):
        self._question_start_datetime = dt

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'question_end_datetime')
    def question_end_datetime(self):
        return convert_datetime(self._question_end_datetime)

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_question_end_datetime')
    def set_question_end_datetime(self, dt):
        self._question_end_datetime = dt

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'result_start_datetime')
    def result_start_datetime(self):
        return convert_datetime(self._result_start_datetime)

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_result_start_datetime')
    def set_result_start_datetime(self, dt):
        self._result_start_datetime = dt

    security.declareProtected(
        SilvaPermissions.AccessContentsInformation, 'result_end_datetime')
    def result_end_datetime(self):
        return convert_datetime(self._result_end_datetime)

    security.declareProtected(
        SilvaPermissions.ChangeSilvaContent, 'set_result_end_datetime')
    def set_result_end_datetime(self, dt):
        self._result_end_datetime = dt

InitializeClass(PollQuestionVersion)



class IPollQuestionResources(IDefaultBrowserLayer):
    silvaconf.resource('poll.css')


class PollQuestionView(silvaviews.View):
    """ default view for poll question
    """
    grok.context(IPollQuestion)

    def update(self, answer=None):
        need(IPollQuestionResources)
        # This code is too complicated and would need
        # simplification. This is all the logic that was in the
        # template before.
        now = datetime.now()
        locale_opts = {'size': 'full',
                       'locale': get_locale_info(self.request),
                       'display_time': False}
        self.question = self.content.get_question()
        self.has_voted = self.content.has_voted(self.request)
        self.show_results_not_ready = False

        if self.is_preview:
            # Preview: show poll and results
            self.show_poll_not_ready = False
            self.show_poll = True
            self.show_results = True
            self.show_outdated = False
        else:
            # Public view: show corresponding section depending of the
            # current time
            start_date = self.content.question_start_datetime()
            end_date = self.content.question_end_datetime()
            self.show_poll_not_ready = start_date is not None and start_date > now
            if self.show_poll_not_ready:
                self.poll_start_date = get_formatted_date(
                    start_date, **locale_opts)
            self.show_poll = (
                (start_date is not None and start_date < now) and
                (end_date is None or end_date > now))
            start_date = self.content.result_start_datetime()
            end_date = self.content.result_end_datetime()
            self.show_outdated = end_date is not None and end_date < now
            self.show_results = (
                (start_date is not None and start_date < now) and
                (end_date is None or end_date > now))

        if self.show_poll:
            # We want to show the poll.
            if self.has_voted:
                # The user already voted, don't show the poll, even if
                # the dates are ok.
                self.show_poll = False
            else:
                if answer is not None:
                    # User just voted, register the code, and don't
                    # show the poll.
                    answer = unicode(answer, 'utf-8')
                    self.content.vote(self.request, answer)
                    self.has_voted = True
                    self.show_poll = False
                else:
                    # The user didn't vote yet. Really show poll.
                    self.answers = []
                    for index, answer in enumerate(self.content.get_answers()):
                        self.answers.append({'title': answer,
                                             'id': 'answer-%02d' % index})

        if self.show_results:
            all_votes = self.content.get_votes()
            self.total_votes = sum(all_votes)
            self.results = []
            for answer, votes in zip(self.content.get_answers(), all_votes):
                percentage = 0
                if self.total_votes:
                    percentage = round((votes * 100.0)/ self.total_votes)
                self.results.append({'answer': answer,
                                     'votes': votes,
                                     'percentage': percentage})
        elif self.has_voted:
            # The user voted, but cannot see the results yet. Tell him
            # when he will be able to see them.

            # The result start and end date and the last fetch into
            # start_date, and end_date. Preview code doesn't fetch
            # them, but in preview the results are always shown.
            self.show_results_not_ready = True
            self.show_results_start_date = get_formatted_date(
                start_date, **locale_opts)
            self.show_results_end_date = None
            if end_date is not None:
                self.show_results_end_date = get_formatted_date(
                    end_date, **locale_opts)


@grok.subscribe(IPollQuestion, IObjectCreatedEvent)
def question_created(question, event):
    service = getUtility(IServicePolls)
    editable = question.get_editable()
    if service.automatically_hide_question():
        # Hide poll question of tocs if setting is set by default.
        binding = getUtility(IMetadataService).getMetadata(editable)
        binding.setValues('silva-extra', {'hide_from_tocs': 'hide'}, reindex=1)
    # Create question in storage.
    editable.qid = service.create_question('', [])

    # Set the code source configuration form thingy.
    cs_form = ZMIForm('form', 'Properties Form')
    cs_filename = os.path.join(
        os.path.dirname(__file__),
        'cs_configuration_form.form')
    with open(cs_filename) as cs_file:
        XMLToForm(cs_file.read(), cs_form)
    question.parameters = cs_form



@grok.subscribe(IPollQuestionVersion, IContentPublishedEvent)
def question_published(question, event):
    now = datetime.now()
    if question.question_start_datetime() is None:
        question.set_question_start_datetime(now)
    if question.result_start_datetime() is None:
        question.set_result_start_datetime(now)
