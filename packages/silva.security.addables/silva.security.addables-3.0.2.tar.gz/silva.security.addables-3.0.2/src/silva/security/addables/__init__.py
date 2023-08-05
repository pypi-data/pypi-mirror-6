# -*- coding: utf-8 -*-
# Copyright (c) 2008-2012 Infrae. All rights reserved.
# See also LICENSE.txt

from silva.core import conf as silvaconf
from silva.core.conf.installer import DefaultInstaller
from zope.interface import Interface

silvaconf.extension_name('silva.security.addables')
silvaconf.extension_title('Silva Security Addables')


class Installer(DefaultInstaller):
    service_id = 'service_addablespermissions'

    def install_custom(self, root):
        if self.service_id not in root.objectIds():
            factory = root.manage_addProduct['silva.security.addables']
            factory.manage_addAddablesPermissionsService(self.service_id)

    def uninstall_custom(self, root):
        if self.service_id in root.objectIds():
            root.manage_delObjects([self.service_id])


class IExtension(Interface):
    """Marker interface for our extension.
    """


install = Installer("silva.security.addables", IExtension)
