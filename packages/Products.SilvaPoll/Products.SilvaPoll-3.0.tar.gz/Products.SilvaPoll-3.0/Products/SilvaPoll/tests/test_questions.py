# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from zope.interface.verify import verifyObject
from silva.core.interfaces import IPublicationWorkflow
from Products.Silva.ftesting import public_settings
from Products.SilvaPoll.interfaces import IPollQuestion, IPollQuestionVersion
from Products.SilvaPoll.testing import FunctionalLayer


def poll_settings(browser):
    public_settings(browser)
    browser.inspect.add('title', css='.poll h1')
    browser.inspect.add('vote_question', css='.poll h2')
    browser.inspect.add('results_question', css='.poll h3')
    browser.inspect.add('forms', css='form.poll-form', type='form')


class QuestionTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')

    def test_question(self):
        """Test content type.
        """
        factory = self.root.manage_addProduct['SilvaPoll']
        factory.manage_addPollQuestion('poll', 'Poll Status')

        self.assertTrue('poll' in self.root.objectIds())
        poll = self.root.poll
        self.assertTrue(verifyObject(IPollQuestion, poll))

        version = poll.get_editable()
        self.assertTrue(verifyObject(IPollQuestionVersion, version))
        version.set_title('New Poll')
        version.set_question('Does it poll ?')
        version.set_answers(['Yeah baby', 'Well, not really'])

        self.assertEqual(version.get_title(), 'New Poll')
        self.assertEqual(version.get_question(), 'Does it poll ?')
        self.assertEqual(version.get_answers(),
                         ['Yeah baby', 'Well, not really'])

    def test_view(self):
        """Test public view.
        """
        factory = self.root.manage_addProduct['SilvaPoll']
        factory.manage_addPollQuestion('poll', 'Poll Status')
        version = self.root.poll.get_editable()
        version.set_title('New Poll')
        version.set_question('Does it poll ?')
        version.set_answers(['Yeah baby', 'Well, not really'])
        IPublicationWorkflow(self.root.poll).publish()

        with self.layer.get_browser(poll_settings) as browser:
            self.assertEqual(browser.open('/root/poll'), 200)
            self.assertEqual(browser.inspect.title, ['New Poll'])
            self.assertEqual(browser.inspect.vote_question, ['Does it poll ?'])
            self.assertEqual(len(browser.inspect.forms), 1)
            form = browser.inspect.forms[0]
            self.assertIn('answer', form.controls)
            self.assertIn('submit', form.controls)
            self.assertEqual(
                form.controls['answer'].options,
                ['Yeah baby', 'Well, not really'])
            form.controls['answer'].value = 'Yeah baby'
            self.assertEqual(
                form.controls['submit'].click(),
                200)
            self.assertEqual(browser.inspect.title, ['New Poll'])
            self.assertEqual(browser.inspect.results_question,
                             ['Does it poll ?'])
            self.assertEqual(len(browser.inspect.forms), 0)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(QuestionTestCase))
    return suite
