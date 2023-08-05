# Copyright (c) 2006-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from Acquisition import aq_chain

from zope.interface.verify import verifyObject
from zope.component import getMultiAdapter

from Products.SilvaFind.interfaces import IFind, ICriterionData
from Products.Silva.tests.test_xmlimport import SilvaXMLTestCase

from silva.core.interfaces.events import IContentImported
from silva.core.interfaces import IFolder


class XMLImportTestCase(SilvaXMLTestCase):
    """Test import of Silva Find.
    """

    def test_default(self):
        """Import a default Silva Find object, With no special data in it.
        """
        self.import_file('test_import_default.silvaxml', globals())

        self.assertEventsAre(
            ['ContentImported for /root/search',],
            IContentImported)

        search = self.root.search
        binding = self.metadata.getMetadata(search)

        self.failUnless(verifyObject(IFind, search))
        self.assertEqual(
            search.get_title(),
            u'Find something in your Site')
        self.assertEqual(
            binding.get('silva-extra', 'content_description'),
            u'This content will find you, even if you hide, it will find you.')
        self.assertEqual(
            binding.get('silva-content', 'maintitle'),
            u'Find something in your Site')
        self.assertEqual(binding.get('silva-extra', 'creator'), u'author')
        self.assertEqual(binding.get('silva-extra', 'lastauthor'), u'paul')

        # Actually those are the fields by default ...
        self.assertListEqual(
            search.shownFields,
            ['fulltext'])
        self.assertListEqual(
            search.shownResultsFields,
            ['breadcrumbs', 'date', 'icon', 'link', 'ranking',
             'resultcount', 'textsnippet', 'thumbnail'])

    def test_all_fields_shown(self):
        """Try to import a Silva Find object that all search and
        result fields display, but no default search values.
        """
        self.import_file('test_import_shown_all.silvaxml', globals())

        self.assertEventsAre(
            ['ContentImported for /root/search',],
            IContentImported)

        search = self.root.search
        binding = self.metadata.getMetadata(search)
        self.failUnless(verifyObject(IFind, search))
        self.assertEqual(
            search.get_title(),
            u'Find something in your Site')
        self.assertEqual(
            binding.get('silva-extra', 'content_description'),
            u'Best breed Belgium finder')
        self.assertEqual(
            binding.get('silva-extra', 'lastauthor'),
            u'wim the roxor')

        self.assertListEqual(
            search.shownFields,
            [f.getName() for f in search.getSearchFields() if f.publicField])
        self.assertListEqual(
            search.shownResultsFields,
            [field.getName() for field in search.getResultFields()])

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
        self.import_file('test_import_default_values.silvaxml', globals())

        self.assertEventsAre(
            ['ContentImported for /root/folder',
             'ContentImported for /root/folder/search'],
            IContentImported)

        folder = self.root.folder
        self.failUnless(verifyObject(IFolder, folder))
        search = folder.search
        self.failUnless(verifyObject(IFind, search))
        self.assertListEqual(
            search.shownFields,
            ['fulltext', 'meta_type'])
        self.assertListEqual(
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
