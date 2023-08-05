# Copyright (c) 2006-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from megrok.chameleon.components import ChameleonPageTemplate
from zope.interface import Interface

from Products.Silva.ExtensionRegistry import extensionRegistry
from Products.SilvaFind.criterion.widgets.default import CriterionTemplateView
from Products.SilvaFind.criterion.widgets.default import convertValue
from Products.SilvaFind.interfaces import IMetatypeCriterionField, IQuery


class MetatypeCriterionView(CriterionTemplateView):
    grok.adapts(IMetatypeCriterionField, IQuery, Interface)

    template = ChameleonPageTemplate(filename='templates/metatypecriterion.cpt')

    def updateWidget(self, value):
        self.selected = value or []
        self.types = self.getAvailableMetaTypes()

    def extractWidgetValue(self):
        return convertValue(self.request.form.get(self.name, None))

    def getAvailableMetaTypes(self):
        meta_types = []
        for content in extensionRegistry.get_addables():
            meta_types.append(
                {"title": content['name'].replace('Silva ', ''),
                 "value": content['name']})
        return meta_types
