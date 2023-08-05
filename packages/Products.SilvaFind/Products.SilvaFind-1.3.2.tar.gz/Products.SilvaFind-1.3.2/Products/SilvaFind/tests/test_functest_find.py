# -*- coding: utf-8 -*-
# Copyright (c) 2008-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from zope.component import getUtility
from Products.SilvaMetadata.interfaces import IMetadataService
from Products.Silva.converters import PDF_TO_TEXT_AVAILABLE
from Products.Silva.tests.helpers import open_test_file
from Products.Silva.testing import FunctionalLayer, smi_settings


test_fixture = {
    'the_great_figure': {
        'id': 'the_great_figure.pdf',
        'title': 'The Great Figure',
        'file': 'the_great_figure.pdf',
        'keywords': None,
    },
    'the_raven': {
        'id': 'the_raven.txt',
        'title': 'The Raven',
        'file': 'raven.txt',
        'keywords': None,
    },
    'the_second_coming': {
        'id': 'the_second_coming.txt',
        'title': 'The Second Coming',
        'file': 'the_second_coming.txt',
        'keywords': 'hyper yeats',
    },
}


class AuthorContentTestCase(unittest.TestCase):
    """Test the Silva find creation.
    """
    layer = FunctionalLayer
    username = 'author'

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('manager')

    def test_create_and_edit(self):
        """An author can't create a SilvaFind by default.
        """
        browser = self.layer.get_browser(smi_settings)
        browser.login(self.username, self.username)

        self.assertEqual(browser.open('/root/edit'), 200)

        form = browser.get_form('md.container')
        self.assertFalse(
            'Silva Find' in
            form.controls['md.container.field.content'].options)

        self.assertEqual(browser.open('/root/edit/+/Silva Find'), 401)


class EditorContentTestCase(AuthorContentTestCase):
    username = 'editor'

    def test_create_and_edit(self):
        """Create and configure a silva find object.
        """
        browser = self.layer.get_browser(smi_settings)
        browser.login(self.username, self.username)
        self.assertEqual(browser.open('/root/edit'), 200)

        browser.macros.create(
            'Silva Find', id='search', title='Search')
        self.assertEqual(
            browser.inspect.folder_listing, ['index', 'search'])

        # The user should by the last author on the content and container.
        self.assertEqual(
            self.root.sec_get_last_author_info().userid(),
            self.username)
        self.assertEqual(
            self.root.search.sec_get_last_author_info().userid(),
            self.username)

        # Visit the edit page
        self.assertEqual(
            browser.inspect.folder_listing['search'].click(),
            200)
        self.assertEqual(browser.url, '/root/search/edit/tab_edit')

        # Change settings
        form = browser.get_form('silva_find_edit')
        form.get_control('show_meta_type:bool').checked = True
        form.get_control('show_silva-content-maintitle:bool').checked = True
        form.get_control('show_silva-extra-keywords:bool').checked = True
        form.get_control('silva-extra.keywords:record').value = u'keyword value'
        form.get_control('silvafind_save').click()

        self.assertEqual(browser.inspect.feedback, ['Changes saved.'])
        form = browser.get_form('silva_find_edit')
        self.assertEquals(
            form.get_control('show_meta_type:bool').checked, True)
        self.assertEquals(
            form.get_control('show_silva-content-maintitle:bool').checked, True)
        self.assertEquals(
            form.get_control('show_silva-extra-keywords:bool').checked, True)
        self.assertEquals(
            form.get_control('silva-extra.keywords:record').value,
            u'keyword value')

        # Delete
        self.assertEqual(browser.inspect.breadcrumbs, ['root', 'Search'])
        browser.inspect.breadcrumbs['root'].click()
        browser.macros.delete('search')


class ChiefEditorContentTestCase(EditorContentTestCase):
    """Test creating content as ChiefEditor.
    """
    username = 'chiefeditor'


class ManagerContentTestCase(ChiefEditorContentTestCase):
    """Test creating content as Manager.
    """
    username = 'manager'


def search_settings(browser):
    browser.inspect.add(
        'search_feedback',
        '//div[@class="searchresults"]/p')
    browser.inspect.add(
        'search_results',
        '//div[@class="searchresults"]//a[@class="searchresult-link"]',
        type='link')


class SearchTestCase(unittest.TestCase):
    """Check if machine has pdftotext. If pdftotext is present run all
    tests, if not leave out pdftotext tests. Test search results of
    SilvaFind.
    """
    layer = FunctionalLayer

    def setUp(self):
        self.root = self.layer.get_application()
        self.layer.login('manager')

        factory = self.root.manage_addProduct['SilvaFind']
        factory.manage_addSilvaFind('search', 'Search Test')

    def create_file(self, document):
        """Helper to create a Silva File with the given data.
        """
        factory = self.root.manage_addProduct['Silva']
        with open_test_file(document['file'], globals()) as file:
            factory.manage_addFile(document['id'], document['title'], file)
            if document['keywords'] is not None:
                content = getattr(self.root, document['id'])
                metadata = getUtility(IMetadataService).getMetadata(content)
                metadata.setValues(
                    'silva-extra',
                    {'keywords': document['keywords']},
                    reindex=1)

    def test_empty_search(self):
        """Test to search just by clicking on the search button.
        """
        browser = self.layer.get_browser(search_settings)
        self.assertEqual(browser.open('/root/search'), 200)

        self.assertEqual(browser.inspect.search_feedback, [])
        self.assertEqual(browser.inspect.search_results, [])
        form = browser.get_form('search_form')
        self.assertEqual(form.inspect.actions, ['Search'])
        self.assertEqual(form.inspect.actions['Search'].click(), 200)
        self.assertEqual(
            browser.inspect.search_feedback,
            ['You need to fill at least one field in the search form.'])
        self.assertEqual(browser.inspect.search_results, [])

    def test_no_result(self):
        """Try to make a search which match no results at all.
        """
        browser = self.layer.get_browser(search_settings)
        self.assertEqual(browser.open('/root/search'), 200)

        self.assertEqual(browser.inspect.search_feedback, [])
        self.assertEqual(browser.inspect.search_results, [])
        form = browser.get_form('search_form')
        form.get_control('fulltext').value = 'grrmuppfff tchak raz ma!'
        self.assertEqual(form.inspect.actions, ['Search'])
        self.assertEqual(form.inspect.actions['Search'].click(), 200)
        self.assertEqual(
            browser.inspect.search_feedback,
            ['No items matched your search.'])
        self.assertEqual(browser.inspect.search_results, [])

    def test_search_pdf(self):
        """Test search inside a PDF file.
        """
        if not PDF_TO_TEXT_AVAILABLE:
            return

        fixture = test_fixture['the_great_figure']
        browser = self.layer.get_browser(search_settings)
        self.assertEqual(browser.open('/root/search'), 200)

        self.create_file(fixture)
        self.assertEqual(browser.inspect.search_feedback, [])
        self.assertEqual(browser.inspect.search_results, [])
        form = browser.get_form('search_form')
        form.get_control('fulltext').value = 'Gold'
        self.assertEqual(form.inspect.actions, ['Search'])
        self.assertEqual(form.inspect.actions['Search'].click(), 200)
        self.assertEqual(browser.inspect.search_feedback, [])
        self.assertEqual(browser.inspect.search_results, ['The Great Figure'])
        self.assertEqual(
            browser.inspect.search_results['The Great Figure'].url,
            'http://localhost/root/the_great_figure.pdf')

    def test_search_fulltext(self):
        """Test search with a regular file.
        """
        fixture = test_fixture['the_raven']
        browser = self.layer.get_browser(search_settings)
        self.assertEqual(browser.open('/root/search'), 200)

        self.create_file(fixture)
        self.assertEqual(browser.inspect.search_feedback, [])
        self.assertEqual(browser.inspect.search_results, [])
        form = browser.get_form('search_form')
        form.get_control('fulltext').value = 'bleak'
        self.assertEqual(form.inspect.actions, ['Search'])
        self.assertEqual(form.inspect.actions['Search'].click(), 200)
        self.assertEqual(browser.inspect.search_feedback, [])
        self.assertEqual(browser.inspect.search_results, ['The Raven'])
        self.assertEqual(
            browser.inspect.search_results['The Raven'].url,
            'http://localhost/root/the_raven.txt')

    def test_search_keywords(self):
        """Test search using metadata keywords
        """
        browser = self.layer.get_browser(smi_settings)
        browser.login('editor')
        self.assertEqual(browser.open('/root/search/edit'), 200)

        form = browser.get_form('silva_find_edit')
        form.get_control('show_meta_type:bool').checked = True
        form.get_control('show_silva-content-maintitle:bool').checked = True
        form.get_control('show_silva-extra-keywords:bool').checked = True
        form.get_control('silva-extra.keywords:record').value = 'yeats'
        form.get_control('silvafind_save').click()
        self.assertEqual(browser.inspect.feedback, ['Changes saved.'])

        fixture = test_fixture['the_second_coming']
        browser = self.layer.get_browser(search_settings)

        self.create_file(fixture)
        self.assertEqual(browser.open('/root/search'), 200)
        self.assertEqual(browser.inspect.search_feedback, [])
        self.assertEqual(browser.inspect.search_results, [])
        form = browser.get_form('search_form')
        form.get_control('fulltext').value = 'blood-dimmed tide'
        self.assertEqual(form.inspect.actions, ['Search'])
        self.assertEqual(form.inspect.actions['Search'].click(), 200)
        self.assertEqual(browser.inspect.search_feedback, [])
        self.assertEqual(browser.inspect.search_results, ['The Second Coming'])
        self.assertEqual(
            browser.inspect.search_results['The Second Coming'].url,
            'http://localhost/root/the_second_coming.txt')

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AuthorContentTestCase))
    suite.addTest(unittest.makeSuite(EditorContentTestCase))
    suite.addTest(unittest.makeSuite(ChiefEditorContentTestCase))
    suite.addTest(unittest.makeSuite(ManagerContentTestCase))
    suite.addTest(unittest.makeSuite(SearchTestCase))
    return suite
