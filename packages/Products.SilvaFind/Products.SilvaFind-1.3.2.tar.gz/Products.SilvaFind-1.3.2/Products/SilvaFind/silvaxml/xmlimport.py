# Copyright (c) 2006-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import logging

from five import grok
from silva.core import conf as silvaconf
from sprout.saxext.xmlimport import BaseHandler
from zope.component import getMultiAdapter

from Products.Silva.silvaxml.xmlimport import NS_URI, SilvaBaseHandler
from Products.SilvaFind.silvaxml import NS_SILVA_FIND
from Products.SilvaFind.interfaces import ICriterionData

silvaconf.namespace(NS_URI)
logger = logging.getLogger('silva.xml')


class CriterionField(BaseHandler):
    category = 'criterion'

    def __init__(self, *args, **kwargs):
        super(CriterionField, self).__init__(*args, **kwargs)
        self.fields = {}
        self.field = None

    def startElementNS(self, name, qname, attrs):
        if name == (NS_SILVA_FIND, 'field'):
            name = attrs[(None, 'name')].encode('utf-8')
            self.fields[name] = []
            self.field = name
        if name == (NS_SILVA_FIND, 'value'):
            assert self.field is not None
            value = attrs[(None, 'value')].encode('utf-8')
            self.fields[self.field].append(value)

    def endElementNS(self, name, qname):
        if name == (NS_SILVA_FIND, 'name'):
            self.field = None
        if name == (NS_SILVA_FIND, self.category):
            self.parentHandler().setFields(self.category, self.fields)


class ResultsField(CriterionField):
    category = 'results'


class FindHandler(SilvaBaseHandler):
    grok.name('find')

    def __init__(self, *args, **kwargs):
        super(FindHandler, self).__init__(*args, **kwargs)
        self.fields = {}

    def getOverrides(self):
        return {
            (NS_SILVA_FIND, 'criterion'): CriterionField,
            (NS_SILVA_FIND, 'results'): ResultsField,
            }

    def setFields(self, category, fields):
        self.fields[category] = fields

    def startElementNS(self, name, qname, attrs):
        if name == (NS_URI, 'find'):
            uid = self.generateOrReplaceId(attrs[(None, 'id')].encode('utf-8'))
            factory = self.parent().manage_addProduct['SilvaFind']
            factory.manage_addSilvaFind(uid, '')
            self.setResultId(uid)

    def endElementNS(self, name, qname):
        if name == (NS_URI, 'find'):
            find = self.result()
            if 'results' in self.fields:
                schema = find.getResultsSchema()
                for name in self.fields['results'].keys():
                    if name not in schema:
                        logger.warn(
                            u"unknown result field %s for Silva Find" % name)
                    else:
                        find.shownResultsFields[name] = True
            if 'criterion' in self.fields:
                schema = find.getSearchSchema()
                for name, value in self.fields['criterion'].iteritems():
                    field = schema.getField(name, None)
                    if field is None:
                        logger.warn(
                            u"unknown search field %s for Silva Find" % name)
                        continue
                    if field.publicField:
                        find.shownFields[name] = True
                    if value:
                        data = getMultiAdapter((field, find), ICriterionData)
                        data.setXMLValue(self, value)
            self.storeMetadata()
            self.notifyImport()
