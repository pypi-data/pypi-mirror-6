# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import logging

from zope.component import getUtility

from Products.SilvaFind.interfaces import IPathCriterionField
from silva.core.references.interfaces import IReferenceService
from silva.core.upgrade.upgrade import BaseUpgrader, content_path

VERSION_B1='2.3b1'


logger = logging.getLogger('silva.core.upgrade')


class SilvaFindUpgrader(BaseUpgrader):

    def validate(self, obj):
        return True

    def upgrade(self, obj):
        service = getUtility(IReferenceService)
        fields = obj.service_find.getSearchSchema().getFields()
        fields = filter(lambda x: IPathCriterionField.providedBy(x), fields)
        root = obj.get_root()
        root_path = root.getPhysicalPath()
        for field in fields:
            field_name = field.getName()
            if obj.searchValues.has_key(field_name):
                value = obj.searchValues[field_name]
                if value:
                    path = value.split('/')
                    if tuple(path[:len(root_path)]) == root_path:
                        traverse_path = path[len(root_path):]
                        target = root.unrestrictedTraverse(traverse_path, None)
                        if target:
                            ref = service.new_reference(
                                obj, name=unicode(field_name))
                            ref.set_target(target)
                            logger.info('reference created for field %s of '
                                        'silva find at %s' %
                                        (field_name, content_path(obj)))
                        else:
                            logger.warn('silva find target at %s '
                                        'not found' % value)
                    else:
                        logger.warn('silva find target at %s '
                                    'outside of silva root' % value)
                del obj.searchValues[field_name]
        return obj

find_upgrader = SilvaFindUpgrader(VERSION_B1, "Silva Find")
