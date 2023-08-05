# -*- coding: utf-8 -*-
# Copyright (c) 2006-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from silva.core import conf as silvaconf
from sprout.saxext.xmlimport import BaseHandler
from zope.component import getMultiAdapter

from silva.core.xml import handlers
from Products.SilvaFind.silvaxml import NS_FIND_URI
from Products.SilvaFind.interfaces import ICriterionData

silvaconf.namespace(NS_FIND_URI)


class CriterionField(BaseHandler):
    category = 'criterion'

    def __init__(self, *args, **kwargs):
        super(CriterionField, self).__init__(*args, **kwargs)
        self.fields = {}
        self.field = None

    def startElementNS(self, name, qname, attrs):
        if name == (NS_FIND_URI, 'field'):
            name = attrs[(None, 'name')].encode('utf-8')
            self.fields[name] = []
            self.field = name
        if name == (NS_FIND_URI, 'value'):
            assert self.field is not None
            value = attrs[(None, 'value')].encode('utf-8')
            self.fields[self.field].append(value)

    def endElementNS(self, name, qname):
        if name == (NS_FIND_URI, 'name'):
            self.field = None
        if name == (NS_FIND_URI, self.category):
            self.parentHandler().setFields(self.category, self.fields)


class ResultsField(CriterionField):
    category = 'results'


class FindHandler(handlers.SilvaHandler):
    grok.name('find')

    def __init__(self, *args, **kwargs):
        super(FindHandler, self).__init__(*args, **kwargs)
        self.fields = {}

    def getOverrides(self):
        return {
            (NS_FIND_URI, 'criterion'): CriterionField,
            (NS_FIND_URI, 'results'): ResultsField,}

    def setFields(self, category, fields):
        self.fields[category] = fields

    def startElementNS(self, name, qname, attrs):
        if name == (NS_FIND_URI, 'find'):
            uid = self.generateIdentifier(attrs)
            factory = self.parent().manage_addProduct['SilvaFind']
            factory.manage_addSilvaFind(uid, '')
            self.setResultId(uid)

    def endElementNS(self, name, qname):
        if name == (NS_FIND_URI, 'find'):
            find = self.result()
            importer = self.getExtra()
            if 'results' in self.fields:
                schema = find.getResultsSchema()
                for name in self.fields['results'].keys():
                    if name not in schema:
                        importer.reportProblem(
                            u"Unknown result field {0}.".format(name),
                            find)
                    else:
                        find.shownResultsFields[name] = True
            if 'criterion' in self.fields:
                schema = find.getSearchSchema()
                for name, value in self.fields['criterion'].iteritems():
                    field = schema.getField(name, None)
                    if field is None:
                        importer.reportProblem(
                            u"Unknown search field {0}.".format(name),
                            find)
                        continue
                    if field.publicField:
                        find.shownFields[name] = True
                    if value:
                        data = getMultiAdapter((field, find), ICriterionData)
                        data.setXMLValue(self, value)
            self.storeMetadata()
            self.notifyImport()
