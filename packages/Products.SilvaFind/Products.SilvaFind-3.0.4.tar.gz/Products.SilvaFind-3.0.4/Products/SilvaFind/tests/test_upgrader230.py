# -*- coding: utf-8 -*-
# Copyright (c) 2009-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from zope.component import getUtility
from silva.core.references.interfaces import IReferenceService

from Products.SilvaFind.testing import FunctionalLayer
from Products.SilvaFind.upgrader.upgrade_230 import find_upgrader


class SilvaFindUpgraderTestCase(unittest.TestCase):
    """Test upgrader which rewrites links and images to use
    references.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('editor')
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addPublication('pub', 'Pub')
        factory = self.root.manage_addProduct['SilvaFind']
        factory.manage_addSilvaFind('search', 'Search')
        self.silva_find = self.root.search
        self.silva_find.setCriterionValue('path', '/root/pub')

    def test_upgrade_create_reference(self):
        find_upgrader.upgrade(self.silva_find)
        ref_service = getUtility(IReferenceService)
        refs = list(ref_service.get_references_to(self.root.pub))
        self.assertTrue(self.silva_find in [r.source for r in refs])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SilvaFindUpgraderTestCase))
    return suite
