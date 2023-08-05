
import operator
from Persistence import Persistent
from Products.SilvaPoll.i18n import translate as _


class Question:
    # XXX This is class is almost useless.

    def __init__(self, question, answers, votes):
        self.question = question
        self.answers = answers
        self.votes = votes


class DB(Persistent):

    def __init__(self):
        self.db = []

    def create(self, question, answers):
        self.db.append((question, answers, [0] * len(answers)))
        self._p_changed = True
        # note that removing elements from the db breaks things big-time
        return len(self.db) - 1

    def get(self, id):
        return Question(*self.db[id])

    def set_question(self, id, question):
        current = self.get(id)
        self.db[id] = (question, current.answers, current.votes)
        self._p_changed = True

    def set_answers(self, id, answers):
        current = self.get(id)
        if reduce(operator.or_, current.votes + [0]):
            raise ValueError(
                _(u"Cannot change answers as votes have already been casted"))
        self.db[id] = (current.question, answers, [0] * len(answers))
        self._p_changed = True

    def vote(self, id, index):
        self.db[id][2][index] += 1
        self._p_changed = True
