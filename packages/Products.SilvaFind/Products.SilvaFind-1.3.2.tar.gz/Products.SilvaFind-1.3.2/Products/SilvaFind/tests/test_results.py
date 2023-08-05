# -*- coding: utf-8 -*-
# Copyright (c) 2010-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from zope.component import queryMultiAdapter
from zope.interface.verify import verifyObject
from zeam.utils.batch.batch import batch

from Products.SilvaFind import schema
from Products.SilvaFind.interfaces import IResultField, IResultView
from Products.Silva.testing import FunctionalLayer


class ResultTestCase(unittest.TestCase):
    """Test some silva find features.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('author')
        # XXX should be a test request, but it sucks too much
        self.request = self.root.REQUEST
        factory = self.root.manage_addProduct['SilvaFind']
        factory.manage_addSilvaFind('search', 'Search your Site')

        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')
        factory = self.root.folder.manage_addProduct['SilvaDocument']
        factory.manage_addDocument('info', 'Information')

        self.documents = batch(
            self.root.service_catalog(
                meta_type=['Silva Document'], path='/root/folder'))
        self.empty = batch([])

    def test_date(self):
        result = schema.DateResultField('date', 'Publication Date')
        self.failUnless(verifyObject(IResultField, result))
        self.assertEqual(result.getName(), 'publicationdate')
        self.assertEqual(result.getId(), 'date')
        self.assertEqual(result.getTitle(), 'Publication Date')
        self.assertEqual(result.getDescription(), '')

        view = queryMultiAdapter(
            (result, self.root.search, self.request), IResultView)
        self.failUnless(verifyObject(IResultView, view))
        view.update(self.documents)
        # XXX difficult to test, contain a date
        self.assertNotEqual(view.render(self.documents[0]), '')

    def test_metatype(self):
        result = schema.MetatypeResultField('icon', 'Icon')
        self.failUnless(verifyObject(IResultField, result))
        self.assertEqual(result.getName(), 'icon')
        self.assertEqual(result.getId(), 'icon')
        self.assertEqual(result.getTitle(), 'Icon')
        self.assertEqual(result.getDescription(), '')

        view = queryMultiAdapter(
            (result, self.root.search, self.request), IResultView)
        self.failUnless(verifyObject(IResultView, view))

        view.update(self.documents)
        self.assertEqual(
            view.render(self.documents[0]),
            u'<img class="searchresult-icon" '
            u'src="http://localhost/root/misc_/SilvaDocument/silvadoc.gif" '
            u'alt="Silva Document" />')

    def test_link(self):
        result = schema.LinkResultField('link', 'Link to result')
        self.failUnless(verifyObject(IResultField, result))
        self.assertEqual(result.getName(), 'linktoresult')
        self.assertEqual(result.getId(), 'link')
        self.assertEqual(result.getTitle(), 'Link to result')
        self.assertEqual(result.getDescription(), '')

        view = queryMultiAdapter(
            (result, self.root.search, self.request), IResultView)
        self.failUnless(verifyObject(IResultView, view))

        view.update(self.documents)
        self.assertEqual(
            view.render(self.documents[0]),
            u'<a href="http://localhost/root/folder/info" '
            u'class="searchresult-link">info</a>')

    def test_thumbnail(self):
        result = schema.ThumbnailResultField(
            'thumb', 'Image Thumbnail', 'Small version of the image')
        self.failUnless(verifyObject(IResultField, result))
        self.assertEqual(result.getName(), 'imagethumbnail')
        self.assertEqual(result.getId(), 'thumb')
        self.assertEqual(result.getTitle(), 'Image Thumbnail')
        self.assertEqual(result.getDescription(), 'Small version of the image')

        view = queryMultiAdapter(
            (result, self.root.search, self.request), IResultView)
        self.failUnless(verifyObject(IResultView, view))

        view.update(self.documents)
        self.assertEqual(
            view.render(self.documents[0]), None)

    def test_breadcrumbs(self):
        result = schema.BreadcrumbsResultField('breadcrumbs', 'Breadcrumbs')
        self.failUnless(verifyObject(IResultField, result))

        view = queryMultiAdapter(
            (result, self.root.search, self.request), IResultView)
        self.failUnless(verifyObject(IResultView, view))

        view.update(self.documents)
        self.assertEqual(
            view.render(self.documents[0]),
            u'<span class="searchresult-breadcrumb">'
            u'<a href="http://localhost/root">root</a>'
            u'<span> &#183; </span>'
            u'<a href="http://localhost/root/folder">Folder</a></span>')

    def test_metadata(self):
        result = schema.MetadataResultField(
            'silva-extra:creator', 'Creator', 'Content creator')
        self.failUnless(verifyObject(IResultField, result))
        self.assertEqual(result.getName(), 'creator')
        self.assertEqual(result.getId(), 'silva-extra:creator')
        self.assertEqual(result.getTitle(), 'Creator')
        self.assertEqual(result.getDescription(), 'Content creator')

        view = queryMultiAdapter(
            (result, self.root.search, self.request), IResultView)
        self.failUnless(verifyObject(IResultView, view))

        view.update(self.documents)
        self.assertEqual(
            view.render(self.documents[0]),
            u'<span class="searchresult-field metadata-silva-extra-creator">'
            u'<span class="searchresult-field-title">Creator</span>'
            u'<span class="searchresult-field-value">author</span></span>')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ResultTestCase))
    return suite
