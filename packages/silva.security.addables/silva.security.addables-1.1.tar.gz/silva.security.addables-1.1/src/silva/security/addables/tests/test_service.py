# Copyright (c) 2008 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import unittest

from Acquisition import aq_base
from Products.Silva.testing import SilvaLayer
from zope.publisher.browser import TestRequest
import silva.security.addables

class SilvaSecurityAddablesLayer(SilvaLayer):
    default_packages = SilvaLayer.default_packages + [
        'silva.security.addables',
        ]

FunctionalLayer = SilvaSecurityAddablesLayer(
    silva.security.addables, zcml_file='configure.zcml')


class AddablesPermissionsTestCase(unittest.TestCase):
    """Tests for silva.security.addables.
    """
    layer = FunctionalLayer

    def setUp(self):
        """After set up, install the extension.
        """
        self.root = self.layer.get_application()
        factory = self.root.manage_addProduct['silva.security.addables']
        factory.manage_addAddablesPermissionsService()

    def test_service(self):
        """Install should provide a new service.
        """
        self.assertTrue(
            hasattr(aq_base(self.root),
                    'service_addablespermissions'))

    def test_retrieve(self):
        """There is utilities which retrieve current settings.
        """
        service = self.root.service_addablespermissions

        expected_roles = ('Author', 'Editor', 'ChiefEditor', 'Manager')
        self.assertEqual(service.manageableRoles(), expected_roles)

        expected_perms = {'Silva AutoTOC': 'Author',
                          'Silva Link': 'Author',
                          'Silva Folder': 'Author',
                          'Silva Image': 'Author',
                          'Silva Publication': 'Editor',
                          'Silva Document': 'Author',
                          'Silva File': 'Author',
                          'Silva Find': 'Editor',
                          'Silva Ghost Folder': 'Editor',
                          'Silva CSV Source': 'Author',
                          'Silva Indexer': 'Editor',
                          'Silva Ghost': 'Author'}

        self.assertEqual(service.currentAddablesPermissions(), expected_perms)

    def test_modification(self):
        """Modification should work.
        """
        service = self.root.service_addablespermissions

        new_perms = {'Silva AutoTOC': 'Manager',
                     'Silva Link': 'Author',
                     'Silva Folder': 'Author',
                     'Silva Image': 'Author',
                     'Silva Publication': 'Editor',
                     'Silva Document': 'Author',
                     'Silva Find': 'ChiefEditor',
                     'Silva File': 'Author',
                     'Silva CSV Source': 'Author',
                     'Silva Ghost Folder': 'Editor',
                     'Silva Indexer': 'ChiefEditor',
                     'Silva Ghost': 'Author'}

        request = TestRequest(form=new_perms, REQUEST_METHOD='POST')
        service.manage_editAddablesPermissions(request)

        self.assertEqual(service.currentAddablesPermissions(), new_perms)

    def test_corrupt_permissions(self):
        """When permission settings doesn't match Silva logic,
        should get an value error.
        """
        service = self.root.service_addablespermissions

        # Set bad permissions
        self.root.manage_permission(
            'Add Silva Documents', ('Author', 'Manager'), 0)

        self.assertRaises(ValueError, service.currentAddablesPermissions)


def test_suite():
    # Run tests
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(AddablesPermissionsTestCase))
    return suite
