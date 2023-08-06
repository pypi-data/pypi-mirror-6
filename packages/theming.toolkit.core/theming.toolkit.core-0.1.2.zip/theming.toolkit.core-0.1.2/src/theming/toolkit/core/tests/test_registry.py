# -*- coding: utf-8 -*-
"""Test Registry for theming.toolkit.core."""

# python imports
import unittest2 as unittest

# zope imports
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

# local imports
from theming.toolkit.core.interfaces import IToolkitSettings
from theming.toolkit.core.testing import THEMING_TOOLKIT_CORE_INTEGRATION_TESTING


class TestToolkitRegistry(unittest.TestCase):
    """Registry Test Case for theming.toolkit.core."""
    layer = THEMING_TOOLKIT_CORE_INTEGRATION_TESTING

    def test_registry_registered(self):
        """Test that the settings are registered correctly."""
        registry = getUtility(IRegistry)
        self.assertTrue(registry.forInterface(IToolkitSettings))


    def test_toolkit_registry_featuredNavigation(self):
        """Test for the 'show_featuredNavigation' key and the default value."""
        #took the color out, update test
        registry = getUtility(IRegistry)
        key = 'theming.toolkit.core.interfaces.IToolkitSettings.show_featuredNavigation'
        self.assertTrue(key in registry.records.keys())
        self.assertTrue(registry.records.get(key))
        key_taglist = 'theming.toolkit.core.interfaces.IToolkitSettings.featuredNavigation_taglist'
        self.assertTrue(key_taglist in registry.records.keys())
        self.assertEquals(registry.records.get(key_taglist).value, u"featured navigation, Featured Navigation")

    def test_toolkit_registry_show_viewlets(self):
        """Test the setters for activating the implemented viewlets"""
        registry = getUtility(IRegistry)
        key = 'theming.toolkit.core.interfaces.IToolkitSettings.show_headerplugin'
        self.assertTrue(key in registry.records.keys())
        self.assertTrue(registry.records.get(key).value)

        key = 'theming.toolkit.core.interfaces.IToolkitSettings.show_title_contact'
        self.assertTrue(key in registry.records.keys())
        self.assertFalse(registry.records.get(key).value)
