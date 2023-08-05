# Copyright (c) 2006-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from zope.interface.verify import verifyObject
from zope.component import getUtility

from Products.Silva.testing import FunctionalLayer, get_event_names
from Products.SilvaFind import interfaces


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
        self.failUnless('search' in self.root.objectIds())
        search = self.root.search
        self.failUnless(verifyObject(interfaces.IFind, search))

    def test_events(self):
        """Check that events are launch when a find object is
        added/modified.
        """
        get_event_names()

        factory = self.root.manage_addProduct['SilvaFind']
        factory.manage_addSilvaFind('new_search', 'New Search')

        self.assertEqual(
            get_event_names(),
            ['ObjectWillBeAddedEvent', 'ObjectAddedEvent',
             'IntIdAddedEvent', 'ContainerModifiedEvent',
             'ObjectCreatedEvent'])

    def test_service(self):
        """Test Silva Find service.
        """
        service = getUtility(interfaces.IFindService)
        self.failUnless(verifyObject(interfaces.IFindService, service))

        search_schema = service.getSearchSchema()
        self.failUnless(verifyObject(interfaces.ISearchSchema, search_schema))

        results_schema = service.getResultsSchema()
        self.failUnless(verifyObject(interfaces.IResultsSchema, results_schema))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SilvaFindTestCase))
    return suite
