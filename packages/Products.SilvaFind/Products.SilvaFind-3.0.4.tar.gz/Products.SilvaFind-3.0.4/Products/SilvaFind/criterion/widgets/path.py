# -*- coding: utf-8 -*-
# Copyright (c) 2006-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from grokcore.chameleon.components import ChameleonPageTemplate
from zope.component import getUtility
from zope.interface import Interface

from Products.SilvaFind.criterion.widgets.default import CriterionData
from Products.SilvaFind.criterion.widgets.default import CriterionTemplateView
from Products.SilvaFind.interfaces import IPathCriterionField, IQuery

from silva.core.interfaces import IContainer
from silva.core.references.interfaces import IReferenceService
from silva.core.references.reference import get_content_id
from silva.core.references.widgets import ReferenceInfoResolver


class PathCriterionData(CriterionData):
    grok.adapts(IPathCriterionField, IQuery)

    def __init__(self, criterion, query):
        super(PathCriterionData, self).__init__(criterion, query)
        self.service = getUtility(IReferenceService)

    def getValue(self):
        reference = self.service.get_reference(self.query, name=self.name)
        if reference is not None:
            target = reference.target
            if IContainer.providedBy(target):
                return target
        return None

    def setValue(self, value):
        if value is None:
            self.service.delete_reference(self.query, name=self.name)
            return

        assert isinstance(value, int)
        reference = self.service.get_reference(
            self.query, name=self.name, add=True)
        if reference.target_id != value:
            reference.set_target_id(value)

    def serializeXML(self, handler):
        value = handler.get_reference(self.name)
        if value is None:
            return []
        return [value]

    def setXMLValue(self, handler, value):
        find = handler.result()
        importer = handler.getExtra()
        importer.resolveImportedPath(
            find,
            lambda content: self.setValue(get_content_id(content)),
            value[0])


class PathCriterionView(CriterionTemplateView):
    grok.adapts(IPathCriterionField, IQuery, Interface)

    template = ChameleonPageTemplate(filename="templates/pathcriterion.cpt")
    interface = 'silva.core.interfaces.content.IContainer'

    def renderPublicWidget(self):
        raise ValueError(u"Cannot render path widgets for the public")

    def updateWidget(self, value):
        resolver = ReferenceInfoResolver(self.request, self.query, self)
        resolver.update(interface=self.interface)
        resolver.add(value=value)

    def extractWidgetValue(self):
        value = self.request.form.get(self.name, None)
        try:
            return int(value)
        except (ValueError, TypeError):
            return 0

    def getIndexValue(self):
        content = self.data.getValue()
        if content is None:
            return None
        return "/".join(content.getPhysicalPath())
