# -*- coding: utf-8 -*-
# Copyright (c) 2010-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from Acquisition import aq_chain

from zope import component
from zope.interface.verify import verifyObject
from zope.publisher.browser import TestRequest
from silva.core.references.reference import get_content_id

from Products.Silva.testing import FunctionalLayer
from Products.SilvaFind.criterion import criterion
from Products.SilvaFind.interfaces import (
    ICriterionField, ICriterionData, ICriterionView)


class CriterionTestCase(unittest.TestCase):
    """Test setup for criterion testing.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('author')
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')
        factory = self.root.manage_addProduct['SilvaFind']
        factory.manage_addSilvaFind('search', 'Search your site')


class FulltextCriterionTestCase(CriterionTestCase):
    """Test fulltext criterion.
    """

    def test_criterion(self):
        field = criterion.FullTextCriterionField()

        self.failUnless(verifyObject(ICriterionField, field))
        self.assertEqual(field.getName(), "fulltext")
        self.assertEqual(field.getIndexId(), "fulltext")

    def test_data(self):
        search = self.root.search
        field = criterion.FullTextCriterionField()

        data = component.queryMultiAdapter((field, search), ICriterionData)
        self.failUnless(verifyObject(ICriterionData, data))

        data.setValue(u"I will go into the woods")
        self.assertEqual(data.getValue(), u"I will go into the woods")
        # XXX Should I test that here ?
        self.failUnless("fulltext" in search.searchValues)
        self.assertEqual(
            search.searchValues["fulltext"],
            u"I will go into the woods")

        data.setValue(None)
        self.assertEqual(data.getValue(), None)
        self.failIf("fulltext" in search.searchValues)

    def test_view(self):
        search = self.root.search
        field = criterion.FullTextCriterionField()
        request = TestRequest()
        data = component.queryMultiAdapter(
            (field, search), ICriterionData)
        view = component.queryMultiAdapter(
            (field, search, request), ICriterionView)

        self.failUnless(verifyObject(ICriterionView, view))
        self.assertEqual(view.canBeShown(), True)
        self.assertEqual(view.getWidgetValue(), None)

        self.assertEqual(view.getIndexId(), "fulltext")
        self.assertEqual(view.getIndexValue(), None)

        self.assertEqual(data.getValue(), None)
        view.saveWidgetValue()
        self.assertEqual(data.getValue(), None)

    def test_view_request_value(self):
        search = self.root.search
        field = criterion.FullTextCriterionField()
        request = TestRequest(form={"fulltext": "Dancing fever"})
        data = component.queryMultiAdapter(
            (field, search), ICriterionData)
        view = component.queryMultiAdapter(
            (field, search, request), ICriterionView)

        self.failUnless(verifyObject(ICriterionView, view))
        self.assertEqual(view.getWidgetValue(), u"Dancing fever")

        self.assertEqual(view.getIndexId(), "fulltext")
        self.assertEqual(view.getIndexValue(), u"Dancing fever")

        self.assertEqual(data.getValue(), None)
        view.saveWidgetValue()
        self.assertEqual(data.getValue(), u"Dancing fever")

    def test_view_default_value(self):
        search = self.root.search
        field = criterion.FullTextCriterionField()
        request = TestRequest(form={"fulltext": ""})
        data = component.queryMultiAdapter(
            (field, search), ICriterionData)
        data.setValue(u"Disco night")
        view = component.queryMultiAdapter(
            (field, search, request), ICriterionView)

        self.failUnless(verifyObject(ICriterionView, view))
        # This fallback on stored value
        self.assertEqual(view.getWidgetValue(), u"Disco night")

        self.assertEqual(view.getIndexId(), "fulltext")
        self.assertEqual(view.getIndexValue(), u"Disco night")

        self.assertEqual(data.getValue(), u"Disco night")
        view.saveWidgetValue()
        # We didn't have any value in the request so it got deleted
        self.assertEqual(data.getValue(), None)


class PathCriterionTestCase(CriterionTestCase):
    """Test path criterion.
    """

    def test_criterion(self):
        field = criterion.PathCriterionField()

        self.failUnless(verifyObject(ICriterionField, field))
        self.assertEqual(field.getName(), "path")
        self.assertEqual(field.getIndexId(), "path")

    def test_data(self):
        search = self.root.search
        field = criterion.PathCriterionField()

        data = component.queryMultiAdapter((field, search), ICriterionData)
        self.failUnless(verifyObject(ICriterionData, data))

        self.assertRaises(AssertionError, data.setValue, u"What ?")
        data.setValue(get_content_id(self.root.folder))
        self.assertEqual(data.getValue(), self.root.folder)
        self.assertEqual(aq_chain(data.getValue()), aq_chain(self.root.folder))

        data.setValue(None)
        self.assertEqual(data.getValue(), None)

    def test_view(self):
        search = self.root.search
        field = criterion.PathCriterionField()
        request = TestRequest()
        data = component.queryMultiAdapter(
            (field, search), ICriterionData)
        view = component.queryMultiAdapter(
            (field, search, request), ICriterionView)

        self.failUnless(verifyObject(ICriterionView, view))
        self.assertEqual(view.canBeShown(), False)

        self.assertEqual(view.getIndexId(), "path")
        self.assertEqual(view.getIndexValue(), None)

        self.assertEqual(data.getValue(), None)
        view.saveWidgetValue()
        self.assertEqual(data.getValue(), None)

    def test_view_default_value(self):
        search = self.root.search
        field = criterion.PathCriterionField()
        request = TestRequest()
        data = component.queryMultiAdapter(
            (field, search), ICriterionData)
        data.setValue(get_content_id(self.root.folder))
        view = component.queryMultiAdapter(
            (field, search, request), ICriterionView)

        self.failUnless(verifyObject(ICriterionView, view))

        self.assertEqual(view.getIndexId(), "path")
        self.assertEqual(view.getIndexValue(), '/root/folder')

        self.assertEqual(data.getValue(), self.root.folder)
        view.saveWidgetValue()
        # We didn't have any value in the request so it got deleted
        self.assertEqual(data.getValue(), None)


class MetaTypeCriterionTestCase(CriterionTestCase):
    """Test metatype criterion implementation.
    """

    def test_criterion(self):
        field = criterion.MetatypeCriterionField()

        self.failUnless(verifyObject(ICriterionField, field))
        self.assertEqual(field.getName(), "meta_type")
        self.assertEqual(field.getIndexId(), "meta_type")

    def test_data(self):
        search = self.root.search
        field = criterion.MetatypeCriterionField()

        data = component.queryMultiAdapter((field, search), ICriterionData)
        self.failUnless(verifyObject(ICriterionData, data))

        data.setValue([u"Silva Document", u"Silva Folder"])
        self.assertEqual(data.getValue(), [u"Silva Document", u"Silva Folder"])

        # empty string or empty list is like None
        data.setValue(u'')
        self.assertEqual(data.getValue(), None)
        data.setValue(u'')
        self.assertEqual(data.getValue(), None)

    def test_view(self):
        search = self.root.search
        field = criterion.MetatypeCriterionField()
        request = TestRequest()
        data = component.queryMultiAdapter(
            (field, search), ICriterionData)
        view = component.queryMultiAdapter(
            (field, search, request), ICriterionView)

        self.failUnless(verifyObject(ICriterionView, view))
        self.assertEqual(view.canBeShown(), True)
        self.assertEqual(view.getWidgetValue(), None)

        self.assertEqual(view.getIndexId(), "meta_type")
        self.assertEqual(view.getIndexValue(), None)

        self.assertEqual(data.getValue(), None)
        view.saveWidgetValue()
        self.assertEqual(data.getValue(), None)

    def test_view_request_value(self):
        search = self.root.search
        field = criterion.MetatypeCriterionField()
        request = TestRequest(
            form={"meta_type": ["Silva Link", u"", "Silva Ghost"]})
        data = component.queryMultiAdapter(
            (field, search), ICriterionData)
        view = component.queryMultiAdapter(
            (field, search, request), ICriterionView)

        self.failUnless(verifyObject(ICriterionView, view))
        self.assertEqual(view.getWidgetValue(), [u"Silva Link", u"Silva Ghost"])

        self.assertEqual(view.getIndexId(), "meta_type")
        self.assertEqual(view.getIndexValue(), [u"Silva Link", u"Silva Ghost"])

        self.assertEqual(data.getValue(), None)
        view.saveWidgetValue()
        self.assertEqual(data.getValue(), [u"Silva Link", u"Silva Ghost"])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FulltextCriterionTestCase))
    suite.addTest(unittest.makeSuite(PathCriterionTestCase))
    suite.addTest(unittest.makeSuite(MetaTypeCriterionTestCase))
    return suite
