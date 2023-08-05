# -*- coding: utf-8 -*-
# Copyright (c) 2006-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from zope.interface.verify import verifyObject

from Products.SilvaFind.schema import Schema
from Products.SilvaFind.schema import MetadataCriterionField
from Products.SilvaFind.interfaces import ISchema


class SchemaTestCase(unittest.TestCase):

    def setUp(self):
        self.field1 = MetadataCriterionField('meta-set', 'field-id1')
        self.field2 = MetadataCriterionField('meta-set', 'field-id2')
        self.schema = Schema([self.field1, self.field2])

    def test_schema(self):
        """Test Schema object.
        """
        self.assertTrue(verifyObject(ISchema, self.schema))

        self.assertEqual(
            self.schema.getFields(),
            [self.field1, self.field2])

        self.assertEqual(
            self.schema.getFieldNames(),
            ['meta-set-field-id1', 'meta-set-field-id2'])

        self.assertFalse(self.schema.hasField('meta-set-field-id3'))
        self.assertFalse('meta-set-field-id3' in self.schema)
        self.assertTrue(self.schema.hasField('meta-set-field-id1'))
        self.assertTrue('meta-set-field-id1' in self.schema)

        self.assertEqual(
            self.schema.getField('meta-set-field-id1'),
            self.field1)

        self.assertEqual(
            self.schema['meta-set-field-id1'],
            self.field1)

        self.assertRaises(KeyError, self.schema.getField, 'carambar')


class MetadataCriterionFieldTestCase(unittest.TestCase):

    def setUp(self):
        self.field = MetadataCriterionField('meta-set', 'field-id')

    def test_metadata(self):
        self.assertFalse(self.field is None)
        self.assertEquals('meta-set', self.field.getSetName())
        self.assertEquals('field-id', self.field.getElementName())


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SchemaTestCase))
    suite.addTest(unittest.makeSuite(MetadataCriterionFieldTestCase))
    return suite
