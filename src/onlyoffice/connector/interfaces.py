# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope import schema
from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from zope.i18nmessageid import MessageFactory

_ = MessageFactory('onlyoffice.connector')

class IOnlyofficeConnectorLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""