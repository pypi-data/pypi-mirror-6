# -*- coding: utf-8 -*-
# Copyright (c) 2008-2012 Infrae. All rights reserved.
# See also LICENSE.txt

from AccessControl import ClassSecurityInfo
from AccessControl.requestmethod import postonly
from App.class_init import InitializeClass

from Products.Silva import roleinfo
from zope.component import getUtility

from five import grok
from silva.core import conf as silvaconf
from silva.core.interfaces import ISilvaConfigurableService
from silva.core.interfaces import ISilvaLocalService, IAddableContents
from silva.core.messages.interfaces import IMessageService
from silva.core.services.base import SilvaService
from silva.translations import translate as _
from silva.core.views import views as silvaviews
from silva.ui import rest


class IAddablesPermissionsService(
    ISilvaLocalService,
    ISilvaConfigurableService):
    pass


class AddablesPermissionsService(SilvaService):
    """Service to configure which content type is addable.
    """
    grok.implements(IAddablesPermissionsService)

    default_service_identifier = 'service_addablespermissions'
    meta_type = 'Silva Addables Permissions Service'
    title = 'Silva Addables Permissions Service'

    silvaconf.icon('AddablesPermissions.gif')

    security = ClassSecurityInfo()

    manage_options = (
        {'label':'Edit', 'action':'manage_permissions'},
        ) + SilvaService.manage_options

    security.declareProtected(
        'View management screens', 'manage_editAddablesPermissions')
    @postonly
    def manage_editAddablesPermissions(self, REQUEST):
        """Edit permissions.
        """
        root = self.get_root()
        for metatype in IAddableContents(root).get_all_addables():
            permission = 'Add ' + metatype + 's'
            current = root.rolesOfPermission(permission)
            current = [r['name'] for r in current if r['selected']]
            wanted = REQUEST.form.get(metatype)
            if wanted is None:
                # metatype not in request, just ignore it.
                continue
            authorized = False
            for role in self.manageableRoles():
                if role == wanted:
                    authorized = True
                if (not authorized) and role in current:
                    current.remove(role)
                if authorized and not (role in current):
                    current.append(role)
            root.manage_permission(permission, current, 0)

    security.declareProtected(
        'View management screens', 'manageableRoles')
    def manageableRoles(self):
        """Return roles for which we manage permissions.
        """
        return roleinfo.AUTHOR_ROLES

    security.declareProtected(
        'View management screens', 'currentAddablesPermissions')
    def currentAddablesPermissions(self):
        """Return current permission settings.
        """
        root = self.get_root()
        settings = {}
        for metatype in IAddableContents(root).get_all_addables():
            permissions = root.rolesOfPermission('Add ' + metatype + 's')
            permissions = dict([(r['name'], '' != r['selected']) for r in permissions])
            winner = None
            for role in self.manageableRoles():
                if permissions[role]:
                    if winner is None:
                        winner = role
                elif not (winner is None): # Sanaty check
                    msg = 'Invalid permission settings. %s can add %s but %s cannot.'
                    raise ValueError, msg % (winner, metatype, role)

            settings[metatype] = winner
        return settings


InitializeClass(AddablesPermissionsService)


class ManagePermissions(silvaviews.ZMIView):
    grok.context(AddablesPermissionsService)
    grok.name('manage_permissions')
    grok.require('zope2.ViewManagementScreens')

    def update(self):
        super(ManagePermissions, self).update()
        self.status = None
        if 'update' in self.request:
            self.context.manage_editAddablesPermissions(self.request)
            self.status = _("Permissions updated.")


class ConfigurePermissions(rest.FormWithTemplateREST):
    grok.adapts(rest.Screen, AddablesPermissionsService)
    grok.name('admin')
    grok.require('zope2.ViewManagementScreens')

    def get_menu_title(self):
        return _('Addables permissions configuration')

    def update(self):
        super(ConfigurePermissions, self).update()
        if 'update' in self.request:
            self.context.manage_editAddablesPermissions(self.request)
            service = getUtility(IMessageService)
            service.send(_(u"Permissions updated."),
                         self.request,
                         namespace='feedback')
