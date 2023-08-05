# -*- coding: utf-8 -*-
# Copyright (c) 2006-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from silva.core.conf.installer import DefaultInstaller
from silva.core import conf as silvaconf
from zope.interface import Interface
from zope.component import getUtility, queryUtility

from Products.SilvaFind.interfaces import IFindService
from silva.core.services.interfaces import ICatalogService


silvaconf.extension_name('SilvaFind')
silvaconf.extension_title('Silva Find')
silvaconf.extension_default()


class IExtension(Interface):
    """Silva Find extension.
    """


class SilvaFindInstaller(DefaultInstaller):

    def install_custom(self, root):
        if queryUtility(IFindService) is None:
            factory = root.manage_addProduct['SilvaFind']
            factory.manage_addFindService()

        catalog = getUtility(ICatalogService)
        indexes = set(catalog.indexes())
        for field in getUtility(IFindService).getSearchSchema().getFields():
            field_index = field.getIndexId()
            if field_index not in indexes:
                raise ValueError(
                    u'Name "%s" not indexed by the catalog' % field_index)

install = SilvaFindInstaller('SilvaFind', IExtension)


