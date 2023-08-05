# -*- coding: utf-8 -*-
# Copyright (c) 2006-2010 Infrae. All rights reserved.
# See also LICENSE.txt


from silva.core.interfaces import ISilvaLocalService
from silva.core.interfaces import IVersionedContent, IVersion


class IServicePolls(ISilvaLocalService):
    """Service Poll API: store poll questions.
    """

    def create_question(question, answers):
        """Create a question, with the possible answers. This should
        return a unique ID for the question.
        """

    def get_question(qid):
        """Given the unique question ID, return the question text as
        an unicode string.
        """

    def set_question(qid, question):
        """Change the question text associated to the unique question
        ID.
        """

    def get_answers(qid):
        """Given the unique question ID, return a list of possible
        answers as a list of unicode strings.
        """

    def set_answers(qid, answers):
        """Change the possible answers associated to the unique
        question ID. This can raise ValueError if some vote have
        already been casted.
        """

    def get_votes(qid):
        """Return a list identifying all votes casted for each answers
        for the given question ID, in order of definition.
        """

    def vote(qid, index):
        """For the given question ID, vote for the answer located at
        index in the list of answers.
        """

    def automatically_hide_question():
        """Return True if new Poll Question should not appear in TOCs
        and listing.
        """

    def store_cookies():
        """Return True if a Poll should set a cookie on the client
        side to prevent people to vote multiple times.
        """



class IPollQuestion(IVersionedContent):
    """A question for a poll.
    """

class IPollQuestionVersion(IVersion):
    """A version of a IPollQuestion.
    """
