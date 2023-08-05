__title__ = 'ska.contrib.plone.ska.browser.forms'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = 'Copyright (c) 2013 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = ('SkaSettingsEditForm',)

from zope.i18nmessageid import MessageFactory

from plone.app.registry.browser import controlpanel

from ska.contrib.plone.ska.defaults import I18N_DOMAIN
from ska.contrib.plone.ska.browser.interfaces import ISkaSettings

_ = MessageFactory(I18N_DOMAIN)

class SkaSettingsEditForm(controlpanel.RegistryEditForm):
    """
    Control panel form.
    """
    schema = ISkaSettings
    label = _("Ska settings")
    description = _(u"""Ska app settings""")

    def updateFields(self):
        super(SkaSettingsEditForm, self).updateFields()

    def updateWidgets(self):
        super(SkaSettingsEditForm, self).updateWidgets()
