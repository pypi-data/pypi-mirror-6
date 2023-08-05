# -*- coding: utf-8 -*-
# Copyright (c) 2010-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import re

from five import grok
from Products.SilvaFind.interfaces import IResultField


NAME = re.compile(r'[^a-z]')

class ResultField(object):
    grok.implements(IResultField)

    # BBB
    id=''
    title=''
    description=''

    def __init__(self, id='', title='', description=''):
        self.id = id
        self.title = title
        self.description = description

    def getName(self):
        return NAME.sub('', self.title.lower())

    def getId(self):
        return self.id

    def getTitle(self):
        return self.title

    def getDescription(self):
        return self.description


class MetatypeResultField(ResultField):
    pass


class AutomaticMetaDataResultField(object):
    """This class is a marker to put in the schemalist.
    This class will automaticly be replaced in the list
    with all possible metadata values
    """
    pass


class RankingResultField(ResultField):
    pass


class TotalResultCountField(ResultField):
    pass


class ResultCountField(ResultField):
    pass


class LinkResultField(ResultField):
    pass


class DateResultField(ResultField):
    pass


class ThumbnailResultField(ResultField):
    pass


class FullTextResultField(ResultField):
    pass


class BreadcrumbsResultField(ResultField):
    pass


class MetadataResultField(ResultField):

    def __init__(self, id='', title='', description=''):
        super(MetadataResultField, self).__init__(id, title, description)
        self.element = id

    def setMetadataElement(self, el):
        self.element = el

    def getMetadataElement(self):
        return self.element
