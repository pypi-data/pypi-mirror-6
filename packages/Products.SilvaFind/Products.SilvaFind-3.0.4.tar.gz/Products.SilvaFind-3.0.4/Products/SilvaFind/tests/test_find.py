# -*- coding: utf-8 -*-
# Copyright (c) 2006-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from zope.interface.verify import verifyObject
from zope.component import getUtility

from Products.SilvaFind.testing import FunctionalLayer
from Products.SilvaFind import interfaces
from Products.Silva.testing import assertTriggersEvents


class SilvaFindTestCase(unittest.TestCase):
    """Test some silva find features.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('author')
        factory = self.root.manage_addProduct['SilvaFind']
        factory.manage_addSilvaFind('search', 'Search your Site')

    def test_find(self):
        self.assertTrue('search' in self.root.objectIds())
        search = self.root.search
        self.assertTrue(verifyObject(interfaces.IFind, search))

    def test_events(self):
        """Check that events are launch when a find object is
        added/modified.
        """

        with assertTriggersEvents(
            'ObjectAddedEvent', 'ContentCreatedEvent'):
            factory = self.root.manage_addProduct['SilvaFind']
            factory.manage_addSilvaFind('new_search', 'New Search')

    def test_service(self):
        """Test Silva Find service.
        """
        service = getUtility(interfaces.IFindService)
        self.assertTrue(verifyObject(interfaces.IFindService, service))

        search_schema = service.getSearchSchema()
        self.assertTrue(verifyObject(interfaces.ISearchSchema, search_schema))

        results_schema = service.getResultsSchema()
        self.assertTrue(verifyObject(interfaces.IResultsSchema, results_schema))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SilvaFindTestCase))
    return suite
