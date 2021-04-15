#
# (c) Copyright Ascensio System SIA 2021
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from onlyoffice.connector.testing import ONLYOFFICE_CONNECTOR_INTEGRATION_TESTING  # noqa: E501
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import unittest


try:
    from Products.CMFPlone.utils import get_installer
except ImportError:
    get_installer = None


class TestSetup(unittest.TestCase):
    """Test that onlyoffice.connector is properly installed."""

    layer = ONLYOFFICE_CONNECTOR_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        if get_installer:
            self.installer = get_installer(self.portal, self.layer['request'])
        else:
            self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if onlyoffice.connector is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'onlyoffice.connector'))

    def test_browserlayer(self):
        """Test that IOnlyofficeConnectorLayer is registered."""
        from onlyoffice.connector.interfaces import (
            IOnlyofficeConnectorLayer)
        from plone.browserlayer import utils
        self.assertIn(
            IOnlyofficeConnectorLayer,
            utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = ONLYOFFICE_CONNECTOR_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        if get_installer:
            self.installer = get_installer(self.portal, self.layer['request'])
        else:
            self.installer = api.portal.get_tool('portal_quickinstaller')
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer.uninstallProducts(['onlyoffice.connector'])
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if onlyoffice.connector is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'onlyoffice.connector'))

    def test_browserlayer_removed(self):
        """Test that IOnlyofficeConnectorLayer is removed."""
        from onlyoffice.connector.interfaces import \
            IOnlyofficeConnectorLayer
        from plone.browserlayer import utils
        self.assertNotIn(
            IOnlyofficeConnectorLayer,
            utils.registered_layers())
