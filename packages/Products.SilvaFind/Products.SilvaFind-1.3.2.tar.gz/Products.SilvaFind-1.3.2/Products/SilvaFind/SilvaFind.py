# Copyright (c) 2006-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import operator

# Zope
from AccessControl import ClassSecurityInfo, getSecurityManager
from App.class_init import InitializeClass
from OFS.SimpleItem import SimpleItem
from Products.ZCTextIndex.ParseTree import ParseError
from ZODB.PersistentMapping import PersistentMapping

# Zope 3
from five import grok
from zope.component import getMultiAdapter
from zope.lifecycleevent import ObjectModifiedEvent
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.event import notify
from zope import component

# Silva
from Products.Silva.Content import Content
from Products.SilvaFind.i18n import translate as _
from Products.Silva import SilvaPermissions

from silva.core import conf as silvaconf
from silva.core.smi import smi as silvasmi
from silva.core.smi.interfaces import IEditTabIndex
from silva.core.views import views as silvaviews
from silva.core.views.httpheaders import HTTPResponseHeaders
from zeam.form import silva as silvaforms
from zeam.utils.batch import batch
from zeam.utils.batch.interfaces import IBatching

# SilvaFind
from Products.SilvaFind.query import Query
from Products.SilvaFind.interfaces import IFind
from Products.SilvaFind.interfaces import ICriterionView
from Products.SilvaFind.interfaces import IResultView
from Products.SilvaFind.interfaces import IQueryPart


class FindResponseHeaders(HTTPResponseHeaders):
    """This reliably set HTTP headers on file serving, for GET and
    HEAD requests.
    """
    grok.adapts(IBrowserRequest, IFind)

    def cache_headers(self):
        self.disable_cache()


class SilvaFind(Query, Content, SimpleItem):
    __doc__ = _("""Silva Find is a powerful search feature that allows easy
        creation of search forms and result pages. Users can add a Find
        anywhere and define which fields to make searchable by site visitors
        and/or which fields to limit to a preset value. Users also can
        determine which fields should be displayed in the search results. All
        metadata sets/fields are supported.""")

    security = ClassSecurityInfo()

    meta_type = "Silva Find"
    grok.implements(IFind)
    silvaconf.icon('SilvaFind.png')

    def __init__(self, id):
        Content.__init__(self, id)
        Query.__init__(self)
        self.shownFields = PersistentMapping()
        self.shownResultsFields = PersistentMapping()
        # by default we only show fulltext search
        # and a couple of resultfields
        self.shownFields['fulltext'] = True
        self.shownResultsFields['link'] = True
        self.shownResultsFields['ranking'] = True
        self.shownResultsFields['resultcount'] = True
        self.shownResultsFields['icon'] = True
        self.shownResultsFields['date'] = True
        self.shownResultsFields['textsnippet'] = True
        self.shownResultsFields['thumbnail'] = True
        self.shownResultsFields['breadcrumbs'] = True

    # ACCESSORS
    security.declareProtected(SilvaPermissions.View, 'getPublicResultFields')
    def getPublicResultFields(self):
        return filter(lambda field: self.isResultShown(field.getName()),
                      self.getResultFields())

    security.declareProtected(SilvaPermissions.View, 'getPublicSearchFields')
    def getPublicSearchFields(self):
        return filter(lambda field: self.isCriterionShown(field.getName()),
                      self.getSearchFields())

    security.declareProtected(SilvaPermissions.View, 'isCriterionShown')
    def isCriterionShown(self, fieldName):
        return self.shownFields.get(fieldName, False)

    security.declareProtected(SilvaPermissions.View, 'isResultShown')
    def isResultShown(self, fieldName):
        return self.shownResultsFields.get(fieldName, False)

    security.declareProtected(SilvaPermissions.View, 'havePublicSearchFields')
    def havePublicSearchFields(self):
        # BBB map(bool) is here for previously non-boolean stored values
        return reduce(operator.or_, map(bool, self.shownFields.values()))

    security.declareProtected(SilvaPermissions.View,
                             'searchResultsWithDescription')
    def searchResultsWithDescription(self, request={}):
        if not request.has_key('search_submit'):
            return ([], '')
        searchArguments = self.getCatalogSearchArguments(request)
        queryEmpty = True
        for key, value in searchArguments.items():
            if key in ['path', 'meta_type']:
                # these fields do not count as a real search query
                # they are always there to filter unwanted results
                continue
            if type(value) is unicode and value.strip():
                queryEmpty = False
                break
            elif type(value) is list:
                queryEmpty = False
                break
        searchArguments['version_status'] = ['public']
        query = searchArguments.get('fulltext', '').strip()
        if query and query[0] in ['?', '*']:
            return ([], _(
                    u'Search query can not start with wildcard character.'))
        if queryEmpty:
            return ([], _(
                    u'You need to fill at least one field in the search form.'))
        catalog = self.get_root().service_catalog
        try:
            results = catalog.searchResults(searchArguments)
        except ParseError:
            return ([], _(
                    u'Search query contains only common or reserved words.'))

        if not results:
            return ([], _(u'No items matched your search.'))

        return (results, '')

    def getCatalogSearchArguments(self, request):
        searchArguments = {}
        for field in self.getSearchFields():
            name = field.getName()
            if (self.shownFields.get(name, False) or name == 'path'):
                queryPart = getMultiAdapter((field, self, request), IQueryPart)
                value = queryPart.getIndexValue()
                if value is None:
                    value = ''
                searchArguments[queryPart.getIndexId()] = value
        return searchArguments


InitializeClass(SilvaFind)


class SilvaFindAddForm(silvaforms.SMIAddForm):
    """Add form for Silva Find.
    """
    grok.name(u'Silva Find')
    grok.context(IFind)


class SilvaFindEditView(silvasmi.SMIPage):
    """Edit a Silva Find
    """
    grok.context(IFind)
    grok.name('tab_edit')
    grok.require('silva.ChangeSilvaContent')
    grok.implements(IEditTabIndex)

    tab = 'edit'

    def save(self):
        """Store fields values
        """
        # Validate values
        def validate(prefix, schema):
            atLeastOneShown = False
            for field in schema:
                shown = self.request.get(prefix + field.getName(), False)
                atLeastOneShown = atLeastOneShown or shown
            return atLeastOneShown

        if not validate('show_', self.context.getSearchFields()):
            self.send_message(
                _(u'You need to activate at least one search criterion.'),
                type=u'error')
            return
        if not validate('show_result_', self.context.getResultFields()):
            self.send_message(
                _(u'You need to display at least one field in the results.'),
                type=u'error')
            return

        for widget in self.widgets:
            widget.saveWidgetValue()

        for field in self.context.getSearchFields():
            fieldName = field.getName()
            self.context.shownFields[fieldName] = bool(
                self.request.form.get('show_' + fieldName, False))

        for field in self.context.getResultFields():
            fieldName = field.getName()
            self.context.shownResultsFields[fieldName] = bool(
                self.request.form.get('show_result_' + fieldName, False))

        notify(ObjectModifiedEvent(self.context))
        return self.send_message(_(u'Changes saved.'), type=u'feedback')


    def update(self):
        self.widgets = []
        for field in self.context.getSearchFields():
            widget = getMultiAdapter((
                    field, self.context, self.request), ICriterionView)
            self.widgets.append(widget)

        self.title = self.context.get_title_or_id()

        if 'silvafind_save' in self.request.form:
            self.save()


class SilvaFindView(silvaviews.View):
    """View a Silva Find.
    """
    grok.context(IFind)

    def update(self):
        # Do search
        checkPermission = getSecurityManager().checkPermission
        results, self.message = \
            self.context.searchResultsWithDescription(self.request)
        # Filter results on View permission
        # XXX This could be done more in a more lazy fashion
        results = filter(
            lambda b: checkPermission('View', b.getObject()),
            results)
        self.results = batch(results, count=20, request=self.request)
        self.result_widgets = []
        self.batch = u''
        if self.results:
            for result in self.context.getPublicResultFields():
                widget = getMultiAdapter((
                        result, self.context, self.request), IResultView)
                widget.update(self.results)
                self.result_widgets.append(widget)

            self.batch = component.getMultiAdapter(
                (self.context, self.results, self.request), IBatching)()

        # Search Widgets
        self.widgets = []
        for field in self.context.getPublicSearchFields():
            widget = getMultiAdapter((
                    field, self.context, self.request), ICriterionView)
            self.widgets.append(widget)
