# -*- coding: utf-8 -*-
"""Interface definitions."""

# zope imports

from Products.CMFPlone import PloneMessageFactory as PMF

from zope import schema
from zope.interface import Interface

# local imports
from theming.toolkit.core.i18n import _


class IToolkitSettings(Interface):
    """Global theming.toolkit settings.
    This describes records stored in the configuration registry and obtainable
    via plone.registry.
    """

    show_headerplugin = schema.Bool(
        default=True,
        required=False,
        title=_(
            u"label_show_header_plugin",
            default=u"Show Social Header Viewlet",
        ),
    )

    headerplugin_code =schema.Text(
        description=PMF(
            u'help_plugin_code',
            default=u'Please enter the Social Header Plugin Code.',
        ),
        required=False,
        title=PMF(u'label_plugin_code', default=u'Social Plugins Code'),
    )

    show_title_contact = schema.Bool(
        default=False,
        required=False,
        title=_(
            u"label_show_header_plugin",
            default=u"Show Site title & contact viewlet",
        ),
    )

    contact_code =schema.TextLine(
        default=u"",
        required=False,
        title=_(
            u"label_toolkit_contact_code",
            default=u"Contact Info for Website header",
        )      
    )

    show_featuredNavigation = schema.Bool(
        default=True,
        required=False,
        title=_(
            u"label_show_featuredNavigation",
            default=u"Show the featured Navigation",
        ),
    )

    featuredNavigation_taglist =schema.Text(
        default=u"featured navigation, Featured Navigation",
        description=PMF(
            u'help_plugin_code',
            default=u'Please enter a comma seperated list of category tags to identify Pages& Folders for featured navigation',
        ),
        required=False,
        title=PMF(u'label_featuredNavigation_taglist', default=u'Tag list featured Navigation'),
    )
