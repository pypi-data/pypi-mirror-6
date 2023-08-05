__title__ = 'ska.contrib.plone.ska.browser.controlpanel'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = 'Copyright (c) 2013 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = ('SkaSettingsControlPanel',)

from plone.app.registry.browser import controlpanel

from ska.contrib.plone.ska.browser.forms import SkaSettingsEditForm

class SkaSettingsControlPanel(controlpanel.ControlPanelFormWrapper):
    """
    Control panel.
    """
    form = SkaSettingsEditForm
