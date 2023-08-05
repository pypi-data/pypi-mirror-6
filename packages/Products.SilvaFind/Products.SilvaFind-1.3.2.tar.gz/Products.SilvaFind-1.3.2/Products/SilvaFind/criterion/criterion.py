# -*- coding: utf-8 -*-
# Copyright (c) 2010-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.interface import implements
from zope.component import getUtility
import persistent

from Products.SilvaFind import interfaces
from Products.SilvaFind.i18n import translate as _
from Products.SilvaMetadata.Index import createIndexId
from Products.SilvaMetadata.interfaces import IMetadataService


# XXX: BaseMetadata criterion has been changed back to
# old style classes because the unpickling is different and it breaks
# if the inherit from object

class MetadataCriterionField:
    implements(interfaces.IMetadataCriterionField)

    publicField = True

    def __init__(self, metadataSet, metadataId):
        self.setName = metadataSet
        self.elementName = metadataId

    def getSetName(self):
        return self.setName

    def getElementName(self):
        return self.elementName

    def getMetadataElement(self):
        if not hasattr(self, '_v_element'):
            service = getUtility(IMetadataService)
            metadata_set = service.getMetadataSet(self.setName)
            self._v_element = metadata_set.getElement(self.elementName)
        return self._v_element

    def getName(self):
        return "%s-%s" % (self.setName, self.elementName)

    def getTitle(self):
        return self.getMetadataElement().Title()

    def getDescription(self):
        return self.getMetadataElement().Description()

    def getIndexId(self):
        return createIndexId(self.getMetadataElement())


class DateRangeMetadataCriterionField(MetadataCriterionField):
    implements(interfaces.IDateRangeMetadataCriterionField)


class IntegerRangeMetadataCriterionField(MetadataCriterionField):
    implements(interfaces.IIntegerRangeMetadataCriterionField)


class FullTextCriterionField(object):
    implements(interfaces.IFullTextCriterionField)

    publicField = True

    def getName(self):
        return "fulltext"

    def getTitle(self):
        return _("full text")

    def getDescription(self):
        return _("Search the full text.")

    def getIndexId(self):
        return "fulltext"


class MetatypeCriterionField(object):
    implements(interfaces.IMetatypeCriterionField)

    publicField = True

    def getName(self):
        return "meta_type"

    def getTitle(self):
        return 'content type'

    def getDescription(self):
        return _('Search for the selected content types.')

    def getIndexId(self):
        return 'meta_type'


class PathCriterionField(object):
    implements(interfaces.IPathCriterionField)

    publicField = False

    def getName(self):
        return "path"

    def getTitle(self):
        return _("below path")

    def getDescription(self):
        return _("Only search below this content.")

    def getIndexId(self):
        return "path"


class AutomaticMetaDataCriterionField(object):
    """This class is a marker to put in the schemalist.
    This class will automaticly be replaced in the list
    with all possible metadata values
    """
    pass
