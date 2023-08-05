# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from AccessControl import ClassSecurityInfo
from AccessControl.requestmethod import postonly
from App.class_init import InitializeClass

from Products.Silva import roleinfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from five import grok
from silva.core import conf as silvaconf
from silva.core.services.base import SilvaService
from silva.core.interfaces import ISilvaLocalService


class IAddablesPermissionsService(ISilvaLocalService):
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
        {'label':'Edit', 'action':'manage_editForm'},
        ) + SilvaService.manage_options

    security.declareProtected('View management screens',
                              'manage_editForm')
    manage_editForm = PageTemplateFile(
        'www/addablesPermissionsServiceEdit', globals(),
        __name__='manage_editForm')


    security.declareProtected(
        'View management screens', 'manage_editAddablesPermissions')
    @postonly
    def manage_editAddablesPermissions(self, REQUEST):
        """Edit permissions.
        """
        root = self.get_root()
        for type in root.get_silva_addables_all():
            permission = 'Add ' + type + 's'
            current = root.rolesOfPermission(permission)
            current = [r['name'] for r in current if r['selected']]
            wanted = REQUEST.form[type]
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
        for type in root.get_silva_addables_all():

            permissions = root.rolesOfPermission('Add ' + type + 's')
            permissions = dict([(r['name'], '' != r['selected']) for r in permissions])
            winner = None
            for role in self.manageableRoles():
                if permissions[role]:
                    if winner is None:
                        winner = role
                elif not (winner is None): # Sanaty check
                        msg = 'Invalid permission settings. %s can add %s but %s cannot.'
                        raise ValueError, msg % (winner, type, role)

            settings[type] = winner
        return settings


InitializeClass(AddablesPermissionsService)
