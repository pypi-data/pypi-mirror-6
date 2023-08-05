# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Infrae. All rights reserved.
# See also LICENSE.txt


from Products.Silva.testing import SilvaLayer
import Products.SilvaFind
import transaction


class SilvaFindLayer(SilvaLayer):
    default_products = SilvaLayer.default_products + [
        'SilvaFind'
        ]

    def _install_application(self, app):
        super(SilvaFindLayer, self)._install_application(app)
        app.root.service_extensions.install('SilvaFind')
        transaction.commit()

FunctionalLayer = SilvaFindLayer(Products.SilvaFind)
