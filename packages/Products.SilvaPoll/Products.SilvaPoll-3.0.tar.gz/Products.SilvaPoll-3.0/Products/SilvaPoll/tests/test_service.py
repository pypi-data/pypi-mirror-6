# -*- coding: utf-8 -*-
# Copyright (c) 2013  Infrae. All rights reserved.
# See also LICENSE.txt

import unittest
from zope.interface.verify import verifyObject
from zope.component import queryUtility

from Products.SilvaPoll.interfaces import IServicePolls
from Products.SilvaPoll.testing import FunctionalLayer


class ServiceTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('manager')

    def test_zodb_service(self):
        service = queryUtility(IServicePolls)
        self.assertTrue(verifyObject(IServicePolls, service))
        self.assertEqual(service.meta_type, 'Silva Poll Service')
        self.assertIn('service_polls', self.root.objectIds())

    def test_sql_service(self):
        factory = self.root.manage_addProduct['ZSQLiteDA']
        factory.manage_addZSQLiteConnection(
            'service_polls_db', 'SQLite', ':memory:')
        self.assertIn('service_polls', self.root.objectIds())
        self.root.manage_delObjects(['service_polls'])
        factory = self.root.manage_addProduct['SilvaPoll']
        factory.manage_addServicePollsMySQL('service_polls', sqlite=True)
        service = queryUtility(IServicePolls)
        self.assertTrue(verifyObject(IServicePolls, service))
        self.assertEqual(service.meta_type, 'Silva Poll Service SQL')
        self.assertIn('service_polls', self.root.objectIds())


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ServiceTestCase))
    return suite

