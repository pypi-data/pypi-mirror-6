# Copyright (c) 2006-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from zope.component import queryMultiAdapter
from silva.core.references.reference import get_content_id

from Products.SilvaFind.interfaces import ICriterionData
from Products.Silva.silvaxml import xmlexport
from Products.Silva.tests.test_xmlexport import SilvaXMLTestCase


class XMLExportTestCase(SilvaXMLTestCase):
    """Test some silva find features.
    """

    def setUp(self):
        super(XMLExportTestCase, self).setUp()
        factory = self.root.manage_addProduct['Silva']
        factory.manage_addFolder('folder', 'Folder')
        factory = self.root.folder.manage_addProduct['SilvaFind']
        factory.manage_addSilvaFind('search', 'Search your Site')

    def test_default(self):
        """Export a default created Silva Find content.
        """
        xml, info = xmlexport.exportToString(self.root.folder.search)
        self.assertExportEqual(
            xml, 'test_export_default.silvaxml', globals())
        self.assertEqual(info.getZexpPaths(), [])
        self.assertEqual(info.getAssetPaths(), [])

    def test_shown_widgets_and_results(self):
        """Display all available fields and widgets in a default
        created Silva Find content and export it.
        """
        search = self.root.folder.search

        for field in search.getResultFields():
            search.shownResultsFields[field.getName()] = True

        for field in search.getSearchFields():
            if field.publicField:
                search.shownFields[field.getName()] = True

        xml, info = xmlexport.exportToString(search)
        self.assertExportEqual(
            xml, 'test_export_display_all.silvaxml', globals())
        self.assertEqual(info.getZexpPaths(), [])
        self.assertEqual(info.getAssetPaths(), [])

    def test_shown_widgets_with_defaults(self):
        """Display some extra widgets with some default values (test a
        simple string, a path and a list).
        """
        search = self.root.folder.search
        search.shownFields['fulltext'] = True
        search.shownFields['meta_type'] = True
        search.shownFields['silva-extra-publicationtime'] = True
        fields = search.getSearchSchema()
        data = queryMultiAdapter((fields['fulltext'], search), ICriterionData)
        data.setValue('silva')
        data = queryMultiAdapter((fields['path'], search), ICriterionData)
        data.setValue(get_content_id(self.root.folder))
        data = queryMultiAdapter((fields['meta_type'], search), ICriterionData)
        data.setValue(['Silva Document', 'Silva Folder', 'Silva File'])
        data = queryMultiAdapter(
            (fields['silva-extra-publicationtime'], search), ICriterionData)
        data.setValue(('2010-01-01', None))

        # We need to export the folder with it not do get an reference error.
        xml, info = xmlexport.exportToString(self.root.folder)
        self.assertExportEqual(
            xml, 'test_export_default_values.silvaxml', globals())
        self.assertEqual(info.getZexpPaths(), [])
        self.assertEqual(info.getAssetPaths(), [])

    def test_invalid_path(self):
        """Try to export a Silva Find content that have a path outside
        of the export tree.
        """
        search = self.root.folder.search
        fields = search.getSearchSchema()
        data = queryMultiAdapter((fields['path'], search), ICriterionData)
        data.setValue(get_content_id(self.root.folder))

        # We only export the find object, the folder selected as path
        # is not in the export so it fails with a nice exception
        self.assertRaises(
            xmlexport.ExternalReferenceError,
            xmlexport.exportToString,
            search)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(XMLExportTestCase))
    return suite
