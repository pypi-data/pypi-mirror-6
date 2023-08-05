# -*- coding: utf-8 -*-
# Copyright (c) 2006-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from ZODB.PersistentMapping import PersistentMapping
from zope.component import getUtility

from Products.SilvaFind.interfaces import IFindService


class Query(object):

    def __init__(self):
        self.searchValues = PersistentMapping()

    def getSearchSchema(self):
        return getUtility(IFindService).getSearchSchema()

    def getResultsSchema(self):
        return getUtility(IFindService).getResultsSchema()

    def getSearchFields(self):
        return self.getSearchSchema().getFields()

    def getResultFields(self):
        return self.getResultsSchema().getFields()

    def getCriterionValue(self, name):
        searchSchema = self.getSearchSchema()
        if searchSchema.hasField(name):
            return self.searchValues.get(name, None)
        else:
            raise ValueError(
                u'No field named %s defined in search schema' %
                name)

    def deleteCriterionValue(self, name):
        searchSchema = self.getSearchSchema()
        if searchSchema.hasField(name):
            if name in self.searchValues:
                del self.searchValues[name]

    def setCriterionValue(self, name, value):
        searchSchema = self.getSearchSchema()
        if searchSchema.hasField(name):
            self.searchValues[name] = value
        else:
            raise ValueError(
                u'No field named %s defined in search schema' %
                name)
