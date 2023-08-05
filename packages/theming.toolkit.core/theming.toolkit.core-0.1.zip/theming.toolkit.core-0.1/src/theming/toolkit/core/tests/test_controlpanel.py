# -*- coding: utf-8 -*-
"""Test Control Panel for theming.toolkit.core."""

# python imports
import unittest2 as unittest

# zope imports
from Products.CMFCore.utils import getToolByName
from plone.app.testing import TEST_USER_ID, logout, setRoles
from plone.registry import Registry
from zope.component import getMultiAdapter
from zope.interface import directlyProvides

# local imports
from theming.toolkit.core.browser.interfaces import IThemingToolkitCore
from theming.toolkit.core.browser.controlpanel import ToolkitSettingsEditForm
from theming.toolkit.core.interfaces import IToolkitSettings
from theming.toolkit.core.testing import THEMING_TOOLKIT_CORE_INTEGRATION_TESTING


class TestToolkitControlPanel(unittest.TestCase):
    """Control Panel Test Case for theming.toolkit.core."""
    layer = THEMING_TOOLKIT_CORE_INTEGRATION_TESTING

    def setUp(self):
        """Additional test setup."""
        self.portal = self.layer['portal']
        directlyProvides(self.portal.REQUEST, IThemingToolkitCore)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.registry = Registry()
        self.registry.registerInterface(IToolkitSettings)

    def test_toolkit_controlpanel_view(self):
        """Test that the toolkit configuration view is available."""
        view = getMultiAdapter((self.portal, self.portal.REQUEST),
                               name='toolkit-controlpanel')
        view = view.__of__(self.portal)
        self.assertTrue(view())

    def test_toolkit_controlpanel_view_protected(self):
        """Test that the toolkit configuration view needs authentication."""
        from AccessControl import Unauthorized
        logout()
        self.assertRaises(Unauthorized, self.portal.restrictedTraverse,
                          '@@toolkit-controlpanel')

    def test_toolkit_in_controlpanel(self):
        """Check that there is an toolkit entry in the control panel."""
        self.controlpanel = getToolByName(self.portal, 'portal_controlpanel')
        self.assertTrue('propertyshelf_toolkit' in [a.getAction(self)['id']
            for a in self.controlpanel.listActions()])
