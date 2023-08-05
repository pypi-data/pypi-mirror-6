# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

# Zope
from AccessControl import ClassSecurityInfo
from App.class_init import InitializeClass

from zope.component import getUtility
from five import grok

# Silva Find
from Products.SilvaMetadata.interfaces import IMetadataService
from Products.SilvaFind.interfaces import IFindService
from Products.SilvaFind.globalschema import (
    globalSearchFields, globalResultsFields)
from Products.SilvaFind.results import AutomaticMetaDataResultField
from Products.SilvaFind.results import MetadataResultField
from Products.SilvaFind.criterion import AutomaticMetaDataCriterionField
from Products.SilvaFind.criterion import DateRangeMetadataCriterionField
from Products.SilvaFind.criterion import IntegerRangeMetadataCriterionField
from Products.SilvaFind.criterion import MetadataCriterionField
from Products.SilvaFind.schema import ResultsSchema
from Products.SilvaFind.schema import SearchSchema

from silva.core.services.base import SilvaService
from silva.core import conf as silvaconf


class FindService(SilvaService):
    """Find Service
    """
    security = ClassSecurityInfo()
    meta_type = "Silva Find Service"
    grok.implements(IFindService)
    grok.name('service_find')
    silvaconf.icon('findservice.png')

    def __init__(self, id, title=None):
        super(FindService, self).__init__(id, title)
        self.search_schema = None
        self.result_schema = None

    def getSearchSchema(self):
        if not self.search_schema is None:
            return self.search_schema
        amd = [obj for obj in globalSearchFields if isinstance(
                obj, AutomaticMetaDataCriterionField)]
        if amd:
            metadata_fields = self._createMetadataCriterionFields()
            amd = amd[0]
            index = globalSearchFields.index(amd)
            fields = (globalSearchFields[:index]
                        + metadata_fields +
                        globalSearchFields[index:])
            fields.remove(amd)
        else:
            fields = globalSearchFields
        return SearchSchema(fields)

    def getResultsSchema(self):
        if not self.result_schema is None:
            return self.result_schema
        amd = [obj for obj in globalResultsFields if isinstance(
                obj, AutomaticMetaDataResultField)]
        if amd:
            metadata_fields = self._createMetadataResultFields()
            amd = amd[0]
            index = globalResultsFields.index(amd)
            fields = (globalResultsFields[:index]
                        + metadata_fields +
                        globalResultsFields[index:])
            fields.remove(amd)
        else:
            fields = globalResultsFields
        return ResultsSchema(fields)

    def _createMetadataResultFields(self):
        fields = []
        service = getUtility(IMetadataService)
        for set in service.getCollection().getMetadataSets():
            for el in set.getElements():
                if el.id == 'hide_from_tocs':
                    continue
                id = '%s:%s' % (set.id, el.id)
                field = MetadataResultField(id, el.Title(), el.Description())
                fields.append(field)
        return fields

    def _createMetadataCriterionFields(self):
        fields = []
        service = getUtility(IMetadataService)
        for set in service.getCollection().getMetadataSets():
            for el in set.getElements():
                if not el.index_p:
                    continue
                if el.field_type == 'DateTimeField':
                    field = DateRangeMetadataCriterionField(set.id, el.id)
                elif el.field_type == 'IntegerField':
                    field = IntegerRangeMetadataCriterionField(set.id, el.id)
                else:
                    field = MetadataCriterionField(set.id, el.id)
                fields.append(field)
        return fields

InitializeClass(FindService)
