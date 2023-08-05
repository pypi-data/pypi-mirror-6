# -*- coding: utf-8 -*-
# Copyright (c) 2006-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from zope.interface import Interface, Attribute
from silva.core import interfaces

"""
A query is a set of criterion.
A criterion is made both of an indexed field of content items
and of value(s) that will be searched for in the catalog.
"""

class ISchema(Interface):
    """A schema contains fields.
    """

    def getFields():
        """Return all the fields of the schema as a list.
        """

    def hasField(name):
        """Return True if there is field called name in the schema.
        """

    def getFieldNames():
        """Return a list of field names.
        """


class ISearchSchema(ISchema):
    """Search schema.
    """


class IResultsSchema(ISchema):
    """Result schema.
    """


class IQuery(Interface):
    """Store fields and values used by a query.
    """

    def getCriterionValue(name):
        """Returns stored value for the field named name.
        """

    def setCriterionValue(name, value):
        """Store the given value for the named name criterion.
        """

    def getSearchSchema():
        """Return the schema describing the fields of the search form
        for this query.
        """

    def getResultsSchema():
        """Return the schema describing the fields to appear in the
        result listing for this query.
        """


class IFind(interfaces.IContent, IQuery):
    """A Silva find object.
    """

    def searchResults(request={}, validate=True):
        """Return a list of ZCatalog brains that match the given
        request.
        """

    def getSearchCriterias(request):
        """Return the search crieterias as defined in the request.
        """



class IFindService(interfaces.ISilvaService, interfaces.ISilvaInvisibleService):
    """Silva find service: provides default global search/result schema.
    """

    def getSearchSchema():
        """Return the default search schema for all query.
        """

    def getResultsSchema():
        """Return the default result schema for all query.
        """


# Search criterions

class ICriterionField(Interface):
    """A criterion describes a field that can be used in a search
    query.
    """
    publicField = Attribute(
        u"Boolean to authorize display of the field on"
        u"the public search form")

    def getName():
        """Return a unique name for the criterion.
        """

    def getTitle():
        """Return a title identifying the criterion.
        """

    def getDescription():
        """Return a description.
        """

    def getIndexId():
        """Return the index id in the catalog to do a search on this
        criterion.
        """


class IMetadataCriterionField(ICriterionField):
    """Criterion to search on an indexed metadata element.
    """

    def getSetName():
        """Return the set name of the metadata element
        """

    def getElementName():
        """Return the name of the element inside its set.
        """

    def getMetadataElement():
        """Return the metadata element.
        """


class IDateRangeMetadataCriterionField(IMetadataCriterionField):
    """Criterion to search an indexed metadata date element.
    """


class IIntegerRangeMetadataCriterionField(IMetadataCriterionField):
    """Criterion to search on a indexed range of integer.
    """


class IFullTextCriterionField(ICriterionField):
    """Criterion to do full text search.
    """


class IMetatypeCriterionField(ICriterionField):
    """Criterion to restrict the search to some Silva metatype.
    """


class IPathCriterionField(ICriterionField):
    """Criterion to restrict the search on content located inside an other.
    """


class ICriterionData(Interface):
    """Manage access to stored criterion data.

    This is used by ICriterionView/IQueryPart to store and retrieve
    default data.
    """

    def getValue():
        """Return the value.
        """

    def setValue(value):
        """Change criterion value.
        """

    def serializeXML(handler):
        """Serialize current value for the given XML handler. This return a
        list of value that will be integrated in the XML.
        """

    def setXMLValue(handler, value):
        """Set value (which is a list) as current value. Handler is
        the XML handler who read those values.
        """


class IQueryPart(Interface):
    """Implemented as an adaptor on a criterion, query and request to
    provide a piece of a full catalog query.
    """

    def getIndexId():
        """Catalog Index to be queried.
        """

    def getIndexValue():
        """Return the value to passe the Catalog Index for the query.
        """


class ICriterionView(IQueryPart):
    """Render/extract value for a criterion for both data input and
    build a query (it is basically two different way to render a
    criterion).

    For data input, two widgets can be rendered:
    - edit view (default criterion value)
    - public view (value to be searched)
    """

    def canBeShown():
        """Return True or False whenever it is possible to show a
        widget for the public.
        """

    def extractWidgetValue():
        """Return the value of the widget contained in the request.
        """

    def getWidgetValue():
        """Return the value of the widget contained or the request or
        the default stored in the query if there is nothing in the
        request.
        """

    def renderPublicWidget():
        """Render a widget for the public to input search data to use
        in the query.
        """

    def renderEditWidget():
        """Render a widget for editors to input default search data to
        be used by the query.
        """


# Search results

class IResultField(Interface):
    """This describe a field which is able to appear in the
    results. That can either a special field like a breadcrumb, the
    last modification time, a link to the content, or an arbitrary
    metadata field.
    """

    def getId():
        """Gives the ID of this result field.
        """

    def getName():
        """Gives the name of this result field.
        """

    def getTitle():
        """Gives the title of this result field.
        """

    def getDescription():
        """Gives the description of this result field.
        """


class IResultView(Interface):
    """Render a ResultField for the public.
    """

    def __init__(context, result, request):
        """Build the view
        """

    def render(item):
        """renders result field for an item
        """
