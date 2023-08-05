# Copyright (c) 2006-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import operator

from zope.interface import Interface
from zope import component
from five import grok

from Products.SilvaFind import interfaces
from Products.SilvaFind.silvaxml import NS_SILVA_FIND
from Products.SilvaFind.interfaces import ICriterionData
from Products.Silva.silvaxml.xmlexport import SilvaBaseProducer, theXMLExporter

theXMLExporter.registerNamespace('silva-find', NS_SILVA_FIND)


class FindProducer(SilvaBaseProducer):
    """XML export a Silva Find object.
    """
    grok.adapts(interfaces.IFind, Interface)

    def sax(self):

        def searchValues(field):
            view = component.getMultiAdapter(
                (field, self.context), ICriterionData)
            for value in view.serializeXML(self):
                self.startElementNS(NS_SILVA_FIND, 'value', {'value': value})
                self.endElementNS(NS_SILVA_FIND, 'value')

        def serializeOptions(prefix, fields, states, handler=None):
            self.startElementNS(NS_SILVA_FIND, prefix)
            for field in fields:
                name = field.getName()
                if not operator.xor(
                    getattr(field, 'publicField', True),
                    states.get(name, False)):
                    self.startElementNS(
                        NS_SILVA_FIND, 'field', {'name': name})
                    if handler is not None:
                        handler(field)
                    self.endElementNS(
                        NS_SILVA_FIND, 'field')
            self.endElementNS(NS_SILVA_FIND, prefix)

        self.startElement('find', {'id': self.context.id})
        self.metadata()
        serializeOptions(
            'criterion',
            self.context.getSearchFields(),
            self.context.shownFields,
            searchValues)
        serializeOptions(
            'results',
            self.context.getResultFields(),
            self.context.shownResultsFields)
        self.endElement('find')
