# -*- coding: utf-8 -*-
# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from Products.Silva.testing import SilvaLayer
import Products.SilvaPoll
import transaction

class PollLayer(SilvaLayer):
    default_products = ['SilvaPoll'] + SilvaLayer.default_products

    def _install_application(self, app):
        super(PollLayer, self)._install_application(app)
        app.root.service_extensions.install('SilvaPoll')
        transaction.commit()


FunctionalLayer = PollLayer(Products.SilvaPoll, zcml_file='configure.zcml')
