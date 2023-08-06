# -*- coding: utf-8 -*-
"""Interface definitions."""

# zope imports
from zope import schema
from zope.interface import Interface

# local imports
from plone.mls.core.i18n import _


class IMLSSettings(Interface):
    """Global Propertyshelf MLS settings.

    This describes records stored in the configuration registry and obtainable
    via plone.registry.
    """

    mls_key = schema.TextLine(
        default=u'',
        required=True,
        title=_(u'MLS API Key'),
    )

    mls_site = schema.TextLine(
        default=u'',
        required=True,
        title=_(u'MLS URL'),
    )

    agency_id = schema.TextLine(
        default=u'',
        required=True,
        title=_(u'Agency ID'),
    )


class IPossibleLocalMLSSettings(Interface):
    """Marker interface for possible local MLS settings."""


class ILocalMLSSettings(Interface):
    """Marker interface for activated local MLS settings."""
