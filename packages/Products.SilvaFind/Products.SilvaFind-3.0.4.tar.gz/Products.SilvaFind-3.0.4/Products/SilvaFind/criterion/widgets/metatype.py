# -*- coding: utf-8 -*-
# Copyright (c) 2006-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from five import grok
from grokcore.chameleon.components import ChameleonPageTemplate
from silva.core.interfaces import IAddableContents
from zope.interface import Interface

from .default import CriterionTemplateView, convertValue
from ...interfaces import IMetatypeCriterionField, IQuery


class MetatypeCriterionView(CriterionTemplateView):
    grok.adapts(IMetatypeCriterionField, IQuery, Interface)

    template = ChameleonPageTemplate(filename='templates/metatypecriterion.cpt')

    def updateWidget(self, value):
        self.selected = value or []
        self.types = self.getAvailableMetaTypes()

    def extractWidgetValue(self):
        return convertValue(self.request.form.get(self.name, None))

    def getAvailableMetaTypes(self):
        container = self.query.get_container()
        meta_types = []
        for content in IAddableContents(container).get_all_addables():
            meta_types.append(
                {"title": content.replace('Silva ', ''),
                 "value": content})
        return meta_types
