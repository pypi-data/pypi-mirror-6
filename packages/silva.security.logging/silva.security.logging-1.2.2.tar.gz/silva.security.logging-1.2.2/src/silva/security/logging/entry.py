# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from AccessControl import getSecurityManager

from five import grok
from zope.intid.interfaces import IIntIds
from zope.keyreference.interfaces import NotYet
from zope.component import queryUtility

from silva.security.logging.interfaces import (
    ILoggingEvent, ISecurityLoggingService)


def convert_string(value):
    if value is None:
        return None
    if isinstance(value, unicode):
        try:
            return value.encode('utf-8')
        except UnicodeEncodeError:
            return 'n/a'
    if not isinstance(value, str):
        return 'n/a'
    return value

def get_username():
    """Return the username of the current user.
    """
    return getSecurityManager().getUser().getUserName()

def get_path(content):
    """Return the path in Zope for the content.
    """
    return '/'.join(content.getPhysicalPath())

def get_id(content):
    """Return an unique identifier for the content, in order to be
    able to find it again even if it moves.
    """
    service = queryUtility(IIntIds)
    if service is not None:
        try:
            return service.register(content)
        except NotYet:
            return 0
    return 0


class LoggingEvent(object):
    """Represent an event.
    """
    grok.implements(ILoggingEvent)

    def __init__(self, action, content, detail=None):
        self.action = convert_string(action)
        self.username = convert_string(get_username())
        self.content_path = convert_string(get_path(content))
        self.content_id = get_id(content)
        self.detail = convert_string(detail)
        self._service = None

    def get_service(self):
        if self._service is None:
            self._service = queryUtility(ISecurityLoggingService)
        return self._service

    def log(self):
        service = self.get_service()
        if service is not None:
            logger = service.get_logger()
            if logger is not None:
                logger.log(self)

    def enable(self):
        service = self.get_service()
        if service is not None:
            service.enable_logging = True

    def disable(self):
        service = self.get_service()
        if service is not None:
            service.enable_logging = False
