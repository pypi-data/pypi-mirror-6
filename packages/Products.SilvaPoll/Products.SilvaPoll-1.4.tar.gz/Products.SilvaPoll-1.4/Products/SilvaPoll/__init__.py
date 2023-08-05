# -*- coding: utf-8 -*-
# Copyright (c) 2006-2010 Infrae. All rights reserved.
# See also LICENSE.txt

from silva.core import conf as silvaconf
from silva.core.conf.installer import DefaultInstaller
from zope.interface import Interface

silvaconf.extension_name("SilvaPoll")
silvaconf.extension_title("Silva Poll")
silvaconf.extension_depends(["SilvaExternalSources"])


class IExtension(Interface):
    """Silva Forum extension.
    """


class SilvaPollInstaller(DefaultInstaller):

    def install_custom(self, root):
        if 'service_polls' not in root.objectIds():
            factory = root.manage_addProduct['SilvaPoll']
            factory.manage_addServicePolls()
        root.service_view_registry.register(
            'edit', 'Silva Poll Question',
            ['edit', 'VersionedContent', 'PollQuestion'])


install = SilvaPollInstaller('SilvaPoll', IExtension)
