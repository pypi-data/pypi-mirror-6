# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from persistent.dict import PersistentDict
from zeam.form import silva as silvaforms
from zeam.form.base.datamanager import DictDataManager
from zope.component import getUtility

from silva.core import conf as silvaconf
from silva.core.views import views as silvaviews
from silva.core.services.base import SilvaService
from silva.security.logging.interfaces import (
    ISecurityLoggingService, ILoggingStorage, ISecurityLoggingConfiguration)


class SecurityLoggingService(SilvaService):
    """Service to logging security events.
    """
    meta_type = "Silva Security Logging Service"
    default_service_identifier = 'service_securitylogging'
    grok.implements(ISecurityLoggingService)
    silvaconf.icon('service.png')

    enable_logging = True       # Default, BBB
    manage_options = (
        {'label': 'Access log', 'action': 'manage_main'},
        {'label': 'Configuration', 'action': 'manage_config'},
        ) + SilvaService.manage_options

    def __init__(self, identifier):
        super(SecurityLoggingService, self).__init__(identifier)
        self.storage_name = "Python Logger"
        self.storage_conf = PersistentDict()

    def get_storage(self):
        return getUtility(ILoggingStorage, name=self.storage_name)

    def get_logger(self):
        if self.enable_logging:
            return self.get_storage().configure(self)
        return None


class ViewLog(silvaviews.ZMIView):
    """View logs.
    """
    grok.name('manage_main')

    def update(self):
        self.is_viewable = False


class Configuration(silvaforms.ZMIComposedForm):
    """Configure service.
    """
    grok.name('manage_config')

    label = u"Change configuration"
    description = u"Modify storage and storage options"



class SelectStorage(silvaforms.SubForm):
    silvaforms.view(Configuration)

    label = u"Select storage to use"
    fields = silvaforms.Fields(ISecurityLoggingConfiguration)
    actions = silvaforms.Actions(silvaforms.EditAction(u"Change"))
    ignoreContent = False


class StorageConfiguration(silvaforms.SubForm):
    silvaforms.view(Configuration)

    label = u"Configure storage"
    actions = silvaforms.Actions(silvaforms.EditAction(u"Change"))
    ignoreContent = False

    @property
    def fields(self):
        return self.context.get_storage().storage_conf

    def update(self):
        self.setContentData(DictDataManager(self.context.storage_conf))


