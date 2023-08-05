# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from zope.component import queryUtility
from zope.interface.verify import verifyObject
from silva.security.logging.testing import FunctionalLayer
from silva.security.logging.interfaces import ISecurityLoggingService
from silva.security.logging.interfaces import ILogger, ILoggingStorage


class ServiceTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('manager')

    def test_add(self):
        """We add a service and check we can retrieve it.
        """
        self.assertFalse(hasattr(self.root, 'service_securitylogging'))
        service = queryUtility(ISecurityLoggingService)
        self.assertEqual(None, service)

        factory = self.root.manage_addProduct['silva.security.logging']
        factory.manage_addSecurityLoggingService()
        self.assertTrue(hasattr(self.root, 'service_securitylogging'))

        service = queryUtility(ISecurityLoggingService)
        self.assertEqual(self.root.service_securitylogging, service)
        self.assertTrue(verifyObject(ISecurityLoggingService, service))

        self.root.manage_delObjects(['service_securitylogging'])
        service = queryUtility(ISecurityLoggingService)
        self.assertEqual(None, service)


class LoggerTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('manager')

        factory = self.root.manage_addProduct['silva.security.logging']
        factory.manage_addSecurityLoggingService()

    def test_memory_logger(self):
        service = queryUtility(ISecurityLoggingService)
        service.storage_name = 'Memory Logger (for testing)'

        storage = service.get_storage()
        self.assertTrue(verifyObject(ILoggingStorage, storage))

        logger = service.get_logger()
        self.assertTrue(verifyObject(ILogger, logger))

    def test_python_logger(self):
        service = queryUtility(ISecurityLoggingService)
        service.storage_name = 'Python Logger'

        storage = service.get_storage()
        self.assertTrue(verifyObject(ILoggingStorage, storage))

        logger = service.get_logger()
        self.assertTrue(verifyObject(ILogger, logger))

    def test_sql_logger(self):
        service = queryUtility(ISecurityLoggingService)
        service.storage_name = 'Zope SQL'

        storage = service.get_storage()
        self.assertTrue(verifyObject(ILoggingStorage, storage))

        # Storage is not configured, the logger is None
        logger = service.get_logger()
        self.assertEqual(logger, None)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ServiceTestCase))
    suite.addTest(unittest.makeSuite(LoggerTestCase))
    return suite
