# -*- coding: utf-8 -*-
# Copyright (c) 2006-2010 Infrae. All rights reserved.
# See also LICENSE.txt

from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass

from Products.SilvaPoll.ServicePolls import ServicePolls
from Products.SilvaPoll.sqldb import SQLDB


class ServicePollsMySQL(ServicePolls):
    """Service that manages poll data
    """
    security = ClassSecurityInfo()
    meta_type = 'Silva Poll Service SQL'

    def _get_database(self):
        return SQLDB('service_polls_db', 'UTF-8')

    def _init_database(self):
        db = self._get_database()
        try:
            db.getSQLData(self, u'SELECT * FROM question')
        except:
            self._create_tables(db)

    def _create_tables(self, db):
        db.getSQLData(self, (
            u"""CREATE TABLE question ("""
                """id BIGINT NOT NULL AUTO_INCREMENT, """
                """question TEXT NOT NULL, """
                """PRIMARY KEY (id))"""))
        db.getSQLData(self, (
            u"""CREATE TABLE answer ("""
                """id BIGINT NOT NULL AUTO_INCREMENT, """
                """qid BIGINT NOT NULL, """
                """answer TEXT NOT NULL, """
                """votes BIGINT DEFAULT 0 NOT NULL, """
                """PRIMARY KEY(id), """
                """INDEX(qid))"""))

    def create_question(self, question, answers, votes):
        assert len(votes) == len(answers), 'votes and answers don\'t match!'
        db = self._get_database()
        db.getSQLData(self,
            u"INSERT INTO question (question) VALUES ('%(question)s')",
            {'question': question})
        idres = db.getSQLData(self, u'SELECT LAST_INSERT_ID() as id')
        id = idres[0]['id']
        for i, answer in enumerate(answers):
            query = (u"INSERT INTO answer (qid, answer, votes) VALUES "
                        "(%(qid)s, '%(answer)s', '%(votes)s')")
            db.getSQLData(self, query, {'qid': id, 'answer': answer,
                                        'votes': votes[i]})
        return id

    def get_question(self, qid):
        db = self._get_database()
        res = db.getSQLData(self,
                u'SELECT * FROM question WHERE id=%(id)s', {'id': qid})
        return res[0]['question']

    def set_question(self, qid, question):
        db = self._get_database()
        db.getSQLData(self,
                u"UPDATE question SET question='%(question)s' WHERE id=%(id)s",
                {'question': question, 'id': qid})

    def get_answers(self, qid):
        db = self._get_database()
        res = db.getSQLData(self,
                u'SELECT answer FROM answer WHERE qid=%(id)s ORDER BY id',
                    {'id': qid})
        ret = [r['answer'] for r in res]
        return ret

    def set_answers(self, qid, answers):
        db = self._get_database()
        curranswers = self.get_answers(qid)
        if curranswers and len(curranswers) == len(answers):
            # this is kinda nasty: first get the ids of the answers, then (in
            # order!) update the rows
            res = db.getSQLData(self,
                    u"SELECT id FROM answer WHERE qid=%(id)s ORDER BY id", {'id': qid})
            for i, id in enumerate([r['id'] for r in res]):
                db.getSQLData(self,
                    u"UPDATE answer SET answer='%(answer)s' where id=%(id)s",
                    {'id': id, 'answer': answers[i]})
        else:
            # drop any existing rows
            db.getSQLData(self, u'DELETE FROM answer WHERE qid=%(qid)s',
                            {'qid': qid})
            for answer in answers:
                db.getSQLData(self,
                    (u"INSERT INTO answer (qid, answer) VALUES (%(qid)s, "
                            "'%(answer)s')"), {'qid': qid, 'answer': answer})

    def get_votes(self, qid):
        db = self._get_database()
        res = db.getSQLData(self,
                u'SELECT votes FROM answer WHERE qid=%(id)s', {'id': qid})
        return [int(r['votes']) for r in res]

    def vote(self, qid, index):
        # kinda nasty too, similar problem: we first get all answer rows to
        # find out what answer has index <index>, then do the update
        db = self._get_database()
        res = db.getSQLData(self,
                u"SELECT id, votes FROM answer WHERE qid=%(id)s", {'id': qid})
        idvotes = [(r['id'], int(r['votes'])) for r in res]
        idvotesindex = idvotes[index]
        db.getSQLData(self,
                u"UPDATE answer SET votes=%(votes)s WHERE id=%(id)s",
                {'id': idvotesindex[0], 'votes': idvotesindex[1] + 1})


InitializeClass(ServicePollsMySQL)

