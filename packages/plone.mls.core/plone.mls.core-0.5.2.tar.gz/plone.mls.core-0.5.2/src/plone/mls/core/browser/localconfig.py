# -*- coding: utf-8 -*-
"""Local MLS configurations."""

# zope imports
from plone.directives import form
from z3c.form import field, button
from zope.annotation.interfaces import IAnnotations
from zope.interface import alsoProvides, noLongerProvides
from zope.traversing.browser.absoluteurl import absoluteURL

# local imports
from plone.mls.core.i18n import _
from plone.mls.core.interfaces import (
    ILocalMLSSettings,
    IMLSSettings,
    IPossibleLocalMLSSettings,
)


CONFIGURATION_KEY = 'plone.mls.core.localmlssettings'


class LocalMLSSettings(form.Form):
    """Local MLS Settings Form."""

    fields = field.Fields(IMLSSettings)
    label = _(u'Local Propertyshelf MLS Settings')
    description = _(
        u'This MLS configuration will be used for this content item and all '
        u'possible child elements.'
    )

    def getContent(self):
        """Get the annotations with the local MLS config."""
        annotations = IAnnotations(self.context)
        return annotations.get(
            CONFIGURATION_KEY,
            annotations.setdefault(CONFIGURATION_KEY, {}),
        )

    @button.buttonAndHandler(_(u'Save'))
    def handle_save(self, action):
        """Save the new configuration to the context annotations."""
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        annotations = IAnnotations(self.context)
        annotations[CONFIGURATION_KEY] = data
        self.request.response.redirect(absoluteURL(self.context, self.request))

    @button.buttonAndHandler(_(u'Cancel'))
    def handle_cancel(self, action):
        """Discard changes."""
        self.request.response.redirect(absoluteURL(self.context, self.request))


class LocalMLSSettingsStatus(object):
    """Return activation/deactivation status of the local MLS settings."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def can_activate(self):
        """Can the local MLS configuration be activated for this context?"""
        return IPossibleLocalMLSSettings.providedBy(self.context) and \
            not ILocalMLSSettings.providedBy(self.context)

    @property
    def active(self):
        """Is the local MLS configuration active for this context?"""
        return ILocalMLSSettings.providedBy(self.context)


class LocalMLSSettingsToggle(object):
    """Toggle local MLS settings for the current context."""

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        """Perform the toggle."""
        msg_type = 'info'

        if ILocalMLSSettings.providedBy(self.context):
            # Deactivate local MLS settings.
            noLongerProvides(self.context, ILocalMLSSettings)
            self.context.reindexObject(idxs=['object_provides', ])
            msg = _(u'Local MLS settings deactivated.')
        elif IPossibleLocalMLSSettings.providedBy(self.context):
            alsoProvides(self.context, ILocalMLSSettings)
            self.context.reindexObject(idxs=['object_provides', ])
            msg = _(u'Local MLS settings activated.')
        else:
            msg = _(
                u'The local MLS settings don\'t work with this '
                u'content type. Add \'IPossibleLocalMLSSettings\' to the '
                u'provided interfaces to enable this feature.'
            )
            msg_type = 'error'

        self.context.plone_utils.addPortalMessage(msg, msg_type)
        self.request.response.redirect(self.context.absolute_url())
