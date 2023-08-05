# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from Products.SilvaFind.i18n import translate as _

from Products.SilvaFind.results import MetatypeResultField
from Products.SilvaFind.results import LinkResultField
from Products.SilvaFind.results import DateResultField
from Products.SilvaFind.results import BreadcrumbsResultField
from Products.SilvaFind.results import FullTextResultField
from Products.SilvaFind.results import ThumbnailResultField
from Products.SilvaFind.results import ResultCountField
from Products.SilvaFind.results import RankingResultField
from Products.SilvaFind.results import AutomaticMetaDataResultField
from Products.SilvaFind.results import TotalResultCountField

from Products.SilvaFind.criterion import FullTextCriterionField
from Products.SilvaFind.criterion import MetatypeCriterionField
from Products.SilvaFind.criterion import PathCriterionField
from Products.SilvaFind.criterion import AutomaticMetaDataCriterionField


globalSearchFields= [
    MetatypeCriterionField(),
    FullTextCriterionField(),
    AutomaticMetaDataCriterionField(),
    PathCriterionField(),
    ]

globalResultsFields = [
    RankingResultField('',      _(u'Ranking'),
                                _(u'Full text result ranking')),
    TotalResultCountField('',   _(u'TotalResultCount'),
                                _(u'Show total number of results')),
    ResultCountField('',        _(u'ResultCount'),
                                _(u'Search result count')),
    MetatypeResultField('',     _(u'Icon'),
                                _(u'Display the icon of the content type.')),
    LinkResultField('',         _(u'Link')),
    DateResultField('',         _(u'Date')),
    FullTextResultField('',     _(u'Text snippet'),),
    ThumbnailResultField('',    _(u'Thumbnail')),
    AutomaticMetaDataResultField(),
    BreadcrumbsResultField('',  _(u'Breadcrumbs')),
    ]
