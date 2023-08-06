# -*- coding: utf-8 -*-
"""MLS Settings Control Panel."""

# zope imports
from plone.app.registry.browser import controlpanel

# local imports
from plone.mls.core.i18n import _
from plone.mls.core.interfaces import IMLSSettings


class MLSSettingsEditForm(controlpanel.RegistryEditForm):
    """Global/default MLS Settings Form."""

    schema = IMLSSettings
    label = _(u'Propertyshelf MLS Settings')
    description = _(
        u'This MLS configuration will be used as the default for this '
        u'Plone site. You can add more MLS configurations by activating '
        u'the local MLS settings on any content item within the site.'
    )

    def updateFields(self):
        super(MLSSettingsEditForm, self).updateFields()

    def updateWidgets(self):
        super(MLSSettingsEditForm, self).updateWidgets()


class MLSSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    """MLS Settings Control Panel."""

    form = MLSSettingsEditForm
