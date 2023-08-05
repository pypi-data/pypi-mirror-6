# -*- coding: utf-8 -*-
"""Test Setup of theming.toolkit.core."""

# python imports
import unittest2 as unittest

# zope imports
from Products.CMFCore.utils import getToolByName
from plone.browserlayer import utils as layerutils

# local imports
from theming.toolkit.core.browser.interfaces import IThemingToolkitCore
from theming.toolkit.core.testing import (
    THEMING_TOOLKIT_CORE_INTEGRATION_TESTING,
)


class TestSetup(unittest.TestCase):
    """Setup Test Case for theming.toolkit.core."""
    layer = THEMING_TOOLKIT_CORE_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.qi_tool = getToolByName(self.portal, 'portal_quickinstaller')

    def test_product_is_installed(self):
        """Test that the product is installed."""
        self.assertTrue(
            self.qi_tool.isProductInstalled('theming.toolkit.core'),
        )

    def test_browserlayer(self):
        """Test that the browserlayer is registered."""
        self.assertIn(IThemingToolkitCore, layerutils.registered_layers())

