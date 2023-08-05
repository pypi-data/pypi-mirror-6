# Copyright (c) 2006-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope.component import getMultiAdapter
from five import grok

from Products.SilvaFind.interfaces import (
    ICriterionField, IQuery, ICriterionData, ICriterionView)


def convertValue(value):
    """Convert a value from what you get from the request to something
    working correctly with the catalog.
    """
    if not value:
        return None
    if isinstance(value, unicode):
        return value
    if not (isinstance(value, list) or isinstance(value, tuple)):
        return unicode(value, 'UTF-8')
    return [unicode(item, 'UTF-8') for item in value if item] or None


class CriterionData(grok.MultiAdapter):
    grok.adapts(ICriterionField, IQuery)
    grok.provides(ICriterionData)
    grok.implements(ICriterionData)

    def __init__(self, criterion, query):
        self.criterion = criterion
        self.query = query
        self.name = unicode(criterion.getName())

    def getValue(self):
        return self.query.getCriterionValue(self.name)

    def setValue(self, value):
        if value:
            self.query.setCriterionValue(self.name, value)
        else:
            self.query.deleteCriterionValue(self.name)

    def serializeXML(self, handler):
        value = self.getValue()
        if value is None:
            return []
        elif isinstance(value, list) or isinstance(value, tuple):
            return [item if item is not None else u'' for item in value]
        return [value]

    def setXMLValue(self, handler, value):
        if len(value) == 1:
            value = value[0]
        self.setValue(value)


class CriterionView(grok.MultiAdapter):
    grok.implements(ICriterionView)
    grok.provides(ICriterionView)
    grok.baseclass()

    def __init__(self, criterion, query, request):
        self.criterion = criterion
        self.query = query
        self.request = request
        self.data = getMultiAdapter((criterion, query), ICriterionData)
        self.name = unicode(criterion.getName())

    def renderEditWidget(self):
        return self.renderWidget(self.data.getValue())

    def renderPublicWidget(self):
        return self.renderWidget(self.getWidgetValue())

    def renderWidget(self, value):
        """Implement this method to render a widget with the given
        value. By default renderEditWidget and renderPublicWidget are
        the same, just the default used value changes.
        """
        raise NotImplementedError

    def extractWidgetValue(self):
        """Implement this method to extract a value from the request
        created by the edit/public widget.
        """
        raise NotImplementedError

    def saveWidgetValue(self):
        self.data.setValue(self.extractWidgetValue())

    def getWidgetValue(self):
        value = self.extractWidgetValue()
        if value is not None:
            return value
        return self.data.getValue()

    # IQueryPart default implementation

    def getIndexId(self):
        return self.criterion.getIndexId()

    getIndexValue = getWidgetValue

    # Proxy criterion information mainly for BBB in edit view

    def canBeShown(self):
        return self.criterion.publicField

    def getTitle(self):
        return self.criterion.getTitle()

    def getDescription(self):
        return self.criterion.getDescription()

    def getName(self):
        return self.name


class CriterionTemplateView(CriterionView):
    """Base class for criterion which wish to use a template in order
    to render themselves.
    """
    grok.baseclass()

    template = None

    def updateWidget(self, value):
        """Implement this method to prepare value that would be used
        by the template.
        """
        raise NotImplementedError

    def renderWidget(self, value):
        assert self.template is not None
        self.updateWidget(value)
        return self.template.render(self)

    # Define namespace that would be used by the Grok template

    def default_namespace(self):
        return {'criterion': self.criterion,
                'query': self.query,
                'request': self.request,
                'view': self}

    def namespace(self):
        return {}
