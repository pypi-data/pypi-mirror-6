# -*- coding: utf-8 -*-
# Copyright (c) 2006-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from zope import schema, interface
from zope.i18nmessageid import MessageFactory

from Products.SilvaPoll.interfaces import IPollQuestion

from silva.core.conf.interfaces import ITitledContent
from silva.core.smi.content.publish import Publish
from silva.core.smi.content.publish import IPublicationFields
from silva.core.views import views as silvaviews
from zeam.form import silva as silvaforms
from zeam.form import autofields

_ = MessageFactory('silvapoll')


class IPollQuestionFields(ITitledContent):
    question = schema.Text(
        title=_(u"Question"),
        required=True)
    answers = schema.List(
        title=_(u"Answers"),
        description=_(u"Possible answers that a visitor can select."),
        value_type=schema.TextLine(required=True),
        required=True,
        min_length=1,
        max_length=20)


class PollQuestionAddForm(silvaforms.SMIAddForm):
    """Poll Question Add Form
    """
    grok.context(IPollQuestion)
    grok.name(u"Silva Poll Question")

    fields = silvaforms.Fields(IPollQuestionFields)


class PollQuestionEditForm(silvaforms.SMIEditForm):
    """Poll Question Add Form
    """
    grok.context(IPollQuestion)

    fields = silvaforms.Fields(IPollQuestionFields).omit('id')



# Add display datetime on publish smi tab

class IQuestionPublicationFields(interface.Interface):
    question_start_datetime = schema.Datetime(
        title=_(u"Publication time of question"),
        description=_(u"Time at which the question should be "
                      u"shown to the public."))
    question_end_datetime = schema.Datetime(
        title=_(u"Expiration time of question"),
        description=_(u"Time at which the question should be "
                      u"hidden from the public."),
        required=False)
    result_start_datetime = schema.Datetime(
        title=_(u"Publication time of results"),
        description=_(u"Time at which the poll results should be "
                      u"shown to the public."))
    result_end_datetime = schema.Datetime(
        title=_(u"Expiration time of results"),
        description=_(u"Time at which the poll results should be "
                      u"hidden from the public."),
        required=False)

    @interface.invariant
    def check_question_end_datetime(data):
        if data.question_end_datetime:
            if data.question_end_datetime < data.question_start_datetime:
                raise interface.Invalid(
                    _(u"Question expiration cannot be "
                      u"before question publication."))

    @interface.invariant
    def check_result_end_datetime(data):
        if data.result_end_datetime:
            if data.result_end_datetime < data.result_start_datetime:
                raise interface.Invalid(
                    _(u"Result display expiration cannot be "
                      u"before result display publication."))


class QuestionPublication(grok.Adapter):
    grok.context(IPollQuestion)
    grok.provides(IQuestionPublicationFields)

    def __init__(self, context):
        self.context = context
        self.version = context.get_editable()

    @apply
    def question_start_datetime():

        def getter(self):
            return self.version.question_start_datetime()

        def setter(self, value):
            self.version.set_question_start_datetime(value)

        return property(getter, setter)


    @apply
    def question_end_datetime():

        def getter(self):
            return self.version.question_end_datetime()

        def setter(self, value):
            self.version.set_question_end_datetime(value)

        return property(getter, setter)

    @apply
    def result_start_datetime():

        def getter(self):
            return self.version.result_start_datetime()

        def setter(self, value):
            self.version.set_result_start_datetime(value)

        return property(getter, setter)
    @apply
    def result_end_datetime():

        def getter(self):
            return self.version.result_end_datetime()

        def setter(self, value):
            self.version.set_result_end_datetime(value)

        return property(getter, setter)


class QuestionPublicationFields(autofields.AutoFields):
    autofields.context(IPollQuestion)
    autofields.group(IPublicationFields)
    autofields.order(20)

    fields = silvaforms.Fields(IQuestionPublicationFields)


class QuestionInfo(silvaviews.Viewlet):
    grok.context(IPollQuestion)
    grok.view(Publish)
    grok.viewletmanager(silvaforms.SMIFormPortlets)
    grok.order(40)

    def available(self):
        return self.version is not None

    def update(self):
        self.version = self.context.get_viewable()
        if self.version is not None:
            dates = self.request.locale.dates
            format = dates.getFormatter('dateTime', 'short').format
            convert = lambda d: d is not None and format(d) or None
            self.question_start_datetime = convert(
                self.version.question_start_datetime())
            self.question_end_datetime = convert(
                self.version.question_end_datetime())
            self.result_start_datetime = convert(
                self.version.result_start_datetime())
            self.result_end_datetime = convert(
                self.version.result_end_datetime())
