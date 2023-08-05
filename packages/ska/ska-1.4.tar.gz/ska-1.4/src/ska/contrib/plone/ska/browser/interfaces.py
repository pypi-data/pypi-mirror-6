__title__ = 'ska.contrib.plone.ska.browser.interfaces'
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__copyright__ = 'Copyright (c) 2013 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = ('ISkaSettings',)

from zope.i18nmessageid import MessageFactory
from zope.interface import Interface
from zope.schema import TextLine

from ska.contrib.plone.ska.defaults import I18N_DOMAIN

_ = MessageFactory(I18N_DOMAIN)

class ISkaSettings(Interface):
    """
    Global Ska settings.
    """
    secret_key = TextLine(
        title = _("Secret Key"),
        description = _("help_ska_secret_key", default="Enter your site Secret Key here."),
        required = False,
        default = u'',
        )
