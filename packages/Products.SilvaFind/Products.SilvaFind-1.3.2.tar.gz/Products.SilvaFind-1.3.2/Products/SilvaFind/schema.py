# Copyright (c) 2006-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.interface import implements
from Products.SilvaFind import interfaces

# XXX: The Schema and BaseMetadata criterion have been changed back to
# old style classes because the unpickling is different and it breaks
# if the inherit from object

# XXX: This is based on a list implementation so it is slow on large
# schemas. Don't do large schemas.


_marker = object()

class Schema:
    implements(interfaces.ISchema)

    def __init__(self, fields):
        self.fields = fields

    def getField(self, name, default=_marker):
        for field in self.fields:
            if field.getName() == name:
                return field
        if default is _marker:
            raise KeyError(name)
        return default

    def hasField(self, name):
        return name in self.getFieldNames()

    __getitem__ = getField
    __contains__ = hasField

    def getFields(self):
        return self.fields

    def getFieldNames(self):
        return [field.getName() for field in self.getFields()]


class SearchSchema(Schema):
    implements(interfaces.ISearchSchema)


class ResultsSchema(Schema):
    implements(interfaces.IResultsSchema)



# BBB
from Products.SilvaFind.criterion import MetadataCriterionField
from Products.SilvaFind.criterion import DateRangeMetadataCriterionField
from Products.SilvaFind.criterion import IntegerRangeMetadataCriterionField
from Products.SilvaFind.criterion import FullTextCriterionField
from Products.SilvaFind.criterion import MetatypeCriterionField
from Products.SilvaFind.criterion import PathCriterionField
from Products.SilvaFind.criterion import AutomaticMetaDataCriterionField


from Products.SilvaFind.results import ResultField
from Products.SilvaFind.results import MetatypeResultField
from Products.SilvaFind.results import RankingResultField
from Products.SilvaFind.results import TotalResultCountField
from Products.SilvaFind.results import ResultCountField
from Products.SilvaFind.results import LinkResultField
from Products.SilvaFind.results import DateResultField
from Products.SilvaFind.results import ThumbnailResultField
from Products.SilvaFind.results import FullTextResultField
from Products.SilvaFind.results import BreadcrumbsResultField
from Products.SilvaFind.results import MetadataResultField
from Products.SilvaFind.results import AutomaticMetaDataResultField

IconResultField = MetatypeResultField
