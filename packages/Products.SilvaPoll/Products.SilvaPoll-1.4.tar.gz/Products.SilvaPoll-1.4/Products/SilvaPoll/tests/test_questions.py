# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from zope.interface.verify import verifyObject
from Products.SilvaPoll.interfaces import IPollQuestion, IPollQuestionVersion
from Products.SilvaPoll.testing import FunctionalLayer


class QuestionTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('author')

    def test_question(self):
        factory = self.root.manage_addProduct['SilvaPoll']
        factory.manage_addPollQuestion('poll', 'Poll Status')

        self.assertTrue('poll' in self.root.objectIds())
        poll = self.root.poll
        self.assertTrue(verifyObject(IPollQuestion, poll))

        version = poll.get_editable()
        self.assertTrue(verifyObject(IPollQuestionVersion, version))
        version.set_question('Does it poll ?')
        version.set_answers(['Yeah baby', 'Well, not really'])

        self.assertEqual(version.get_question(), 'Does it poll ?')
        self.assertEqual(version.get_answers(), ['Yeah baby', 'Well, not really'])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(QuestionTestCase))
    return suite
