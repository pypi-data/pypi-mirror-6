# -*- coding: utf-8 -*-
# Copyright (c) 2006-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import operator

from zope.interface import Interface
from zope import component
from five import grok

from Products.SilvaFind import interfaces
from Products.SilvaFind.silvaxml import NS_FIND_URI
from Products.SilvaFind.interfaces import ICriterionData

from silva.core.xml import producers


class FindProducer(producers.SilvaProducer):
    """XML export a Silva Find object.
    """
    grok.adapts(interfaces.IFind, Interface)

    def sax(self):

        def searchValues(field):
            view = component.getMultiAdapter(
                (field, self.context), ICriterionData)
            for value in view.serializeXML(self):
                self.startElementNS(
                    NS_FIND_URI, 'value', {'value': value})
                self.endElementNS(
                    NS_FIND_URI, 'value')

        def serializeOptions(prefix, fields, states, handler=None):
            self.startElementNS(NS_FIND_URI, prefix)
            for field in fields:
                name = field.getName()
                if not operator.xor(
                    bool(getattr(field, 'publicField', True)),
                    bool(states.get(name, False))):
                    self.startElementNS(
                        NS_FIND_URI, 'field', {'name': name})
                    if handler is not None:
                        handler(field)
                    self.endElementNS(
                        NS_FIND_URI, 'field')
            self.endElementNS(NS_FIND_URI, prefix)

        self.startElementNS(
            NS_FIND_URI, 'find', {'id': self.context.id})
        self.sax_metadata()
        serializeOptions(
            'criterion',
            self.context.getSearchFields(),
            self.context.shownFields,
            searchValues)
        serializeOptions(
            'results',
            self.context.getResultFields(),
            self.context.shownResultsFields)
        self.endElementNS(
            NS_FIND_URI, 'find')
