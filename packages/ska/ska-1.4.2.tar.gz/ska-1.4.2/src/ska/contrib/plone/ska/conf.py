from __future__ import absolute_import

__title__ = 'ska.contrib.plone.ska.conf'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = 'Copyright (c) 2013 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = ('get_setting', 'get_settings')

from zope.component import getUtility

from plone.registry.interfaces import IRegistry

from ska.contrib.plone.ska.browser.interfaces import ISkaSettings

def get_settings():
    """
    Gets app registry settings.
    """
    registry = getUtility(IRegistry)
    return registry.forInterface(ISkaSettings)

def get_setting(setting, override=None):
    """
    Get a setting from `ska.contrib.django.ska` conf module, falling back to the default.

    If override is not None, it will be used instead of the setting.
    """
    settings = get_settings()

    return getattr(settings, setting, override)
