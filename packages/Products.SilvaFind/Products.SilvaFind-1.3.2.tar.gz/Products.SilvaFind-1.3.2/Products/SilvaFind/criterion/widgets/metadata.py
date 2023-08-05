# Copyright (c) 2006-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

# Zope
from DateTime import DateTime
from five import grok
from megrok.chameleon.components import ChameleonPageTemplate
from zope.interface import Interface

# Silva
from Products.SilvaFind.criterion.widgets.default import CriterionTemplateView
from Products.SilvaFind.criterion.widgets.default import CriterionView
from Products.SilvaFind.criterion.widgets.default import convertValue
from Products.SilvaFind.interfaces import IDateRangeMetadataCriterionField
from Products.SilvaFind.interfaces import IIntegerRangeMetadataCriterionField
from Products.SilvaFind.interfaces import IMetadataCriterionField, IQuery


class MetadataCriterionView(CriterionView):
    grok.adapts(IMetadataCriterionField, IQuery, Interface)

    def renderPublicWidget(self):
        # we don't want to show widgets for stored values.
        # BBB convertValue is here for previously stored (wrong) values
        value = convertValue(self.data.getValue())
        if value:
            return self.renderValue(value)
        return self.renderWidget(self.extractWidgetValue())

    def renderValue(self, value):
        if isinstance(value, list):
            value = u", ".join(value)
        return u"<strong>%s</strong>" % value

    def renderWidget(self, value):
        # XXX does None values work ?
        element = self.criterion.getMetadataElement()
        return element.field.render(value)

    def extractWidgetValue(self):
        set_name = self.criterion.getSetName()
        set_values = self.request.get(set_name, None)
        if set_values is None:
            return None
        element_name = self.criterion.getElementName()
        value = set_values.get(element_name, None)
        return convertValue(value)


class RangeMetadataCriterionTemplateView(CriterionTemplateView):
    grok.baseclass()

    def updateWidget(self, value):
        self.begining = None
        self.end = None
        if value:
            self.begining, self.end = value

    def renderPublicWidget(self):
        # we don't want to show data input widgets for stored values
        value = self.data.getValue()
        if value:
            return self.renderValue(value)
        return self.renderWidget(self.extractWidgetValue())

    def renderValue(self, value):
        return "<strong>%s - %s</strong>" % value

    def extractWidgetValue(self):

        def extractValue(key):
            try:
                value = self.request.get(key, None)
                if self.convertValue(value) is None:
                    raise ValueError(value)
                return value
            except:
                pass
            return None

        value_begin = extractValue(self.name + '-begin')
        value_end = extractValue(self.name + '-end')
        if value_begin is None and value_end is None:
            return None
        # XXX It will be better to store directly converted objects
        return (value_begin, value_end)

    def getIndexValue(self):
         return self.constructQuery(self.getWidgetValue())

    def constructQuery(self, value):
        if value is None:
            return None
        begin, end = map(self.convertValue, value)

        if begin is None:
            if end is None:
                return None
            else:
                return {'query': end, 'range': 'max'}
        else:
            if end is None:
                return {'query': begin, 'range': 'min'}
            else:
                return {'query': [begin, end], 'range': 'min:max'}

    def convertValue(self, value):
        raise NotImplementedError


class IntegerRangeMetadataCriterionView(RangeMetadataCriterionTemplateView):
    grok.adapts(IIntegerRangeMetadataCriterionField, IQuery, Interface)

    template = ChameleonPageTemplate(
        filename="templates/integerrangecriterion.cpt")

    def convertValue(self, value):
        """Convert a value to an integer or return None.
        """
        try:
            return int(value)
        except:
            return None


class DateRangeMetadataCriterionView(RangeMetadataCriterionTemplateView):
    grok.adapts(IDateRangeMetadataCriterionField, IQuery, Interface)

    template = ChameleonPageTemplate(
        filename="templates/daterangecriterion.cpt")

    def convertValue(self, value):
        """Convert a date or return None if it is invalid.
        """
        try:
            return DateTime(value)
        except:
            return None

