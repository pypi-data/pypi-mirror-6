# -*- coding: utf-8 -*-
# Copyright (c) 2012 Infrae. All rights reserved.
# See also LICENSE.txt

from zope.interface import Interface

from silva.core import conf as silvaconf
from silva.core.conf.installer import DefaultInstaller

silvaconf.extension_name("silva.app.sitemap")
silvaconf.extension_title("Silva Sitemaps")
silvaconf.extension_depends(['Silva'])


class SilvaSitemapInstaller(DefaultInstaller):
    """ Silva sitemap installer
    """

    service_name = 'service_sitemap'

    def install_custom(self, root):
        if self.service_name not in root.objectIds():
            factory = root.manage_addProduct['silva.app.sitemap']
            factory.manage_addSitemapService(self.service_name)


class IExtension(Interface):
    """silva.app.sitemap extension
    """


install = SilvaSitemapInstaller("silva.app.sitemap", IExtension)
