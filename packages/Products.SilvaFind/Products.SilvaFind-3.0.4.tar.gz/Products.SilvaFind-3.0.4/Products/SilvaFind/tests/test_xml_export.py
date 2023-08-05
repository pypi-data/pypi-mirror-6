# -*- coding: utf-8 -*-
# Copyright (c) 2006-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from zope.component import queryMultiAdapter
from silva.core.references.reference import get_content_id

from Products.Silva.testing import Transaction
from Products.SilvaFind.testing import FunctionalLayer
from Products.SilvaFind.interfaces import ICriterionData
from Products.Silva.tests.test_xml_export import SilvaXMLTestCase


class XMLExportTestCase(SilvaXMLTestCase):
    """Test some silva find features.
    """
    layer = FunctionalLayer

    def setUp(self):
        with Transaction():
            super(XMLExportTestCase, self).setUp()
            factory = self.root.manage_addProduct['Silva']
            factory.manage_addFolder('folder', 'Folder')
            factory = self.root.folder.manage_addProduct['SilvaFind']
            factory.manage_addSilvaFind('search', 'Search your Site')

    def test_default(self):
        """Export a default created Silva Find content.
        """
        exporter = self.assertExportEqual(
            self.root.folder.search,
            'test_export_default.silvaxml')
        self.assertEqual(exporter.getZexpPaths(), [])
        self.assertEqual(exporter.getAssetPaths(), [])

    def test_shown_widgets_and_results(self):
        """Display all available fields and widgets in a default
        created Silva Find content and export it.
        """
        with Transaction():
            search = self.root.folder.search

            for field in search.getResultFields():
                search.shownResultsFields[field.getName()] = True

            for field in search.getSearchFields():
                if field.publicField:
                    search.shownFields[field.getName()] = True

        exporter = self.assertExportEqual(
            search,
            'test_export_display_all.silvaxml')
        self.assertEqual(exporter.getZexpPaths(), [])
        self.assertEqual(exporter.getAssetPaths(), [])

    def test_shown_widgets_with_defaults(self):
        """Display some extra widgets with some default values (test a
        simple string, a path and a list).
        """
        with Transaction():
            search = self.root.folder.search
            search.shownFields['fulltext'] = True
            search.shownFields['meta_type'] = True
            fields = search.getSearchSchema()
            data = queryMultiAdapter((fields['fulltext'], search), ICriterionData)
            data.setValue('silva')
            data = queryMultiAdapter((fields['path'], search), ICriterionData)
            data.setValue(get_content_id(self.root.folder))
            data = queryMultiAdapter((fields['meta_type'], search), ICriterionData)
            data.setValue(['Silva Document', 'Silva Folder', 'Silva File'])

        # We need to export the folder with it not do get an reference error.
        exporter = self.assertExportEqual(
            self.root.folder,
            'test_export_default_values.silvaxml')
        self.assertEqual(exporter.getZexpPaths(), [])
        self.assertEqual(exporter.getAssetPaths(), [])

    def test_invalid_path(self):
        """Try to export a Silva Find content that have a path outside
        of the export tree.
        """
        with Transaction():
            search = self.root.folder.search
            fields = search.getSearchSchema()
            data = queryMultiAdapter((fields['path'], search), ICriterionData)
            data.setValue(get_content_id(self.root.folder))

        # We only export the find object, the folder selected as path
        # is not in the export so it fails with a nice exception
        self.assertExportFail(search)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(XMLExportTestCase))
    return suite
