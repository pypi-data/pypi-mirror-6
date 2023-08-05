# -*- coding: utf-8 -*-
# Copyright (c) 2006-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from Acquisition import aq_chain

from zope.interface.verify import verifyObject
from zope.component import getMultiAdapter

from Products.SilvaFind.testing import FunctionalLayer
from Products.SilvaFind.interfaces import IFind, ICriterionData
from Products.Silva.tests.test_xml_import import SilvaXMLTestCase
from Products.Silva.testing import Transaction

from silva.core.interfaces import IFolder


class XMLImportTestCase(SilvaXMLTestCase):
    """Test import of Silva Find.
    """
    layer = FunctionalLayer

    def test_default(self):
        """Import a default Silva Find object, With no special data in it.
        """
        with Transaction():
            importer = self.assertImportFile(
                'test_import_default.silvaxml',
                ['/root/search'])

        self.assertEqual(importer.getProblems(), [])

        search = self.root.search
        binding = self.metadata.getMetadata(search)

        self.assertTrue(verifyObject(IFind, search))
        self.assertEqual(
            search.get_title(),
            u'Find something in your Site')
        self.assertEqual(
            binding.get('silva-extra', 'content_description'),
            u'This content will find you, even if you hide, it will find you.')
        self.assertEqual(
            binding.get('silva-content', 'maintitle'),
            u'Find something in your Site')

        # Actually those are the fields by default ...
        self.assertItemsEqual(
            search.shownFields,
            ['fulltext'])
        self.assertItemsEqual(
            search.shownResultsFields,
            ['breadcrumbs', 'date', 'icon', 'link', 'ranking',
             'resultcount', 'textsnippet', 'thumbnail'])

    def test_all_fields_shown(self):
        """Try to import a Silva Find object that all search and
        result fields display, but no default search values.
        """
        with Transaction():
            importer = self.assertImportFile(
                'test_import_shown_all.silvaxml',
                ['/root/search'])

        search = self.root.search
        binding = self.metadata.getMetadata(search)
        self.assertTrue(verifyObject(IFind, search))
        self.assertEqual(
            search.get_title(),
            u'Find something in your Site')
        self.assertEqual(
            binding.get('silva-extra', 'content_description'),
            u'Best breed Belgium finder')
        self.assertEqual(
            binding.get('silva-extra', 'lastauthor'),
            u'editor')
        self.assertItemsEqual(
            search.shownFields,
            [f.getName() for f in search.getSearchFields() if f.publicField])
        self.assertItemsEqual(
            search.shownResultsFields,
            [field.getName() for field in search.getResultFields()])
        self.assertEqual(
            importer.getProblems(),
            [(u'Unknown result field publicationtime.', search),
             (u'Unknown result field expirationtime.', search)])

        schema = search.getSearchSchema()
        data = getMultiAdapter((schema['meta_type'], search), ICriterionData)
        self.assertEqual(
            data.getValue(),
            None)

        data = getMultiAdapter((schema['path'], search), ICriterionData)
        self.assertEqual(
            data.getValue(),
            None)

    def test_field_shown_and_default_values(self):
        """Import a Silva Find content that some search fields shown
        field default values.
        """
        with Transaction():
            importer = self.assertImportFile(
                'test_import_default_values.silvaxml',
                ['/root/folder',
                 '/root/folder/search'])

        self.assertEqual(importer.getProblems(), [])

        folder = self.root.folder
        self.assertTrue(verifyObject(IFolder, folder))
        search = folder.search
        self.assertTrue(verifyObject(IFind, search))
        self.assertItemsEqual(
            search.shownFields,
            ['fulltext', 'meta_type'])
        self.assertItemsEqual(
            search.shownResultsFields,
            ['breadcrumbs', 'date', 'icon', 'link', 'ranking',
             'resultcount', 'textsnippet', 'thumbnail'])

        schema = search.getSearchSchema()
        data = getMultiAdapter((schema['fulltext'], search), ICriterionData)
        self.assertEqual(
            data.getValue(),
            u"silva rox")

        data = getMultiAdapter((schema['meta_type'], search), ICriterionData)
        self.assertEqual(
            data.getValue(),
            ['Silva Document', 'Silva Folder', 'Silva File'])

        data = getMultiAdapter((schema['path'], search), ICriterionData)
        self.assertEqual(
            data.getValue(),
            self.root.folder)
        self.assertEqual(
            aq_chain(data.getValue()),
            aq_chain(self.root.folder))


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(XMLImportTestCase))
    return suite
