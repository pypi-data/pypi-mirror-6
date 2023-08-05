# Copyright (c) 2006-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from zope.interface import Interface

from Products.SilvaFind.criterion.widgets.default import CriterionView
from Products.SilvaFind.interfaces import IQuery, IFullTextCriterionField


HTML_CHARACTERS = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
    }

escape = lambda string: ''.join(HTML_CHARACTERS.get(c) or c for c in string)

HTML = u"""<input class="store" type="text"
                  name="%s" id="%s" value="%s" size="20" />"""


class FullTextCriterionView(CriterionView):
    grok.adapts(IFullTextCriterionField, IQuery, Interface)

    def renderWidget(self, value):
        if value is None:
            value = ""

        return HTML % (self.name, self.name, escape(value))

    def extractWidgetValue(self):
        value = self.request.form.get(self.name, None)
        if not value:
            return None
        return unicode(value, 'UTF-8')
