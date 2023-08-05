# -*- coding: utf-8 -*-
# Copyright (c) 2012  Infrae. All rights reserved.
# See also LICENSE.txt

from Products.Silva.testing import SilvaLayer

import transaction
import silva.app.sitemap


class SitemapLayer(SilvaLayer):
    default_packages = SilvaLayer.default_packages + [
        'silva.app.sitemap',
        ]

    def _install_application(self, app):
        super(SitemapLayer, self)._install_application(app)
        app.root.service_extensions.install('silva.app.sitemap')
        transaction.commit()


FunctionalLayer = SitemapLayer(silva.app.sitemap)
