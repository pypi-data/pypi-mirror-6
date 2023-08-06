# -*- coding: utf-8 -*-
"""Test Layer for theming.toolkit.core."""

# zope imports
from plone.app.testing import (
    IntegrationTesting,
    PloneSandboxLayer,
    PLONE_FIXTURE,
    applyProfile,
)
from zope.configuration import xmlconfig


class ThemingToolkitCore(PloneSandboxLayer):
    """Custom Test Layer for theming.toolkit.core."""
    defaultBases = (PLONE_FIXTURE, )

    def setUpZope(self, app, configurationContext):
        # Load ZCML for this package
        import theming.toolkit.core
        xmlconfig.file('configure.zcml',
                       theming.toolkit.core,
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'theming.toolkit.core:default')


THEMING_TOOLKIT_CORE_FIXTURE = ThemingToolkitCore()
THEMING_TOOLKIT_CORE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(THEMING_TOOLKIT_CORE_FIXTURE, ),
    name="ThemingToolkitCore:Integration")
