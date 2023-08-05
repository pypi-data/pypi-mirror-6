# Copyright (c) 2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from five import grok
from zope.container.interfaces import (
    IObjectMovedEvent, IObjectAddedEvent, IObjectRemovedEvent,
    IContainerModifiedEvent)
from zope.lifecycleevent.interfaces import (
    IObjectCreatedEvent, IObjectCopiedEvent, IObjectModifiedEvent)

from OFS.interfaces import IObjectWillBeRemovedEvent

from silva.security.logging.entry import LoggingEvent, get_path
from silva.core.interfaces import events
from silva.core.interfaces import ISilvaObject, IVersion


@grok.subscribe(ISilvaObject, IObjectCreatedEvent)
def log_create(content, event):
    if IObjectCopiedEvent.providedBy(event):
        detail = 'from %s' % get_path(event.original)
        LoggingEvent('copy', content, detail).log()
    else:
        LoggingEvent('create', content).log()

@grok.subscribe(IVersion, IObjectWillBeRemovedEvent)
@grok.subscribe(ISilvaObject, IObjectWillBeRemovedEvent)
def log_delete(content, event):
    if content is event.object:
        LoggingEvent('delete', content).log()

@grok.subscribe(IVersion, IObjectAddedEvent)
@grok.subscribe(ISilvaObject, IObjectAddedEvent)
def log_add(content, event):
    if content is event.object:
        LoggingEvent('add', content).log()

@grok.subscribe(IVersion, IObjectModifiedEvent)
@grok.subscribe(ISilvaObject, IObjectModifiedEvent)
def log_modify(content, event):
    if not events.IPublishingEvent.providedBy(event):
        if IContainerModifiedEvent.providedBy(event):
            LoggingEvent('modify the container', content).log()
        else:
            LoggingEvent('modify', content).log()

@grok.subscribe(ISilvaObject, IObjectMovedEvent)
def log_move(content, event):
    if content is event.object:
        if not (IObjectAddedEvent.providedBy(event) or
                IObjectRemovedEvent.providedBy(event)):
            detail = 'from %s/%s to %s/%s' % (
                get_path(event.oldParent), event.oldName,
                get_path(event.newParent), event.newName)
            LoggingEvent('move', content, detail).log()

if hasattr(events, 'IContentOrderChangedEvent'):
    # Only available in Silva 3.0
    @grok.subscribe(ISilvaObject, events.IContentOrderChangedEvent)
    def log_order_changed(content, event):
        detail = 'from %s to %s' % (event.old_position, event.new_position)
        LoggingEvent('order changed', content, detail).log()


# Security changes

@grok.subscribe(ISilvaObject, events.ISecurityRestrictionModifiedEvent)
def log_security_restriction_set(content, event):
    if event.role:
        detail = 'with role %s' % event.role
        LoggingEvent('set a access restriction to', content, detail).log()
    else:
        LoggingEvent('remove the access restriction to', content).log()

@grok.subscribe(ISilvaObject, events.ISecurityRoleAddedEvent)
def log_security_add_role(content, event):
    detail = 'for %r roles %s' % (event.username, ', '.join(event.roles))
    LoggingEvent('changed roles on', content, detail).log()

@grok.subscribe(ISilvaObject, events.ISecurityRoleRemovedEvent)
def log_security_remove_role(content, event):
    detail = 'for %r' % event.username
    if event.roles:
        detail += ' roles %s' % ', '.join(event.roles)
    LoggingEvent('removed roles on', content, detail).log()


# Publication events

@grok.subscribe(IVersion, events.IContentRequestApprovalEvent)
def log_publication_request_approval(content, event):
    LoggingEvent('request approval', content).log()

if hasattr(events, 'IContentApprovalRequestWithdrawnEvent'):
    # Silva 3.0
    @grok.subscribe(IVersion, events.IContentApprovalRequestWithdrawnEvent)
    def log_publication_approval_request_withdrawn(content, event):
        LoggingEvent('cancel request approval', content).log()
else:
    # Silva 2.3+
    @grok.subscribe(IVersion, events.IContentApprovalRequestCanceledEvent)
    def log_publication_approval_request_cancel(content, event):
        LoggingEvent('cancel request approval', content).log()

@grok.subscribe(IVersion, events.IContentApprovalRequestRefusedEvent)
def log_publication_approval_request_refused(content, event):
    LoggingEvent('reject request approval', content).log()

@grok.subscribe(IVersion, events.IContentApprovedEvent)
def log_publication_approved(content, event):
    LoggingEvent('approve', content).log()

@grok.subscribe(IVersion, events.IContentUnApprovedEvent)
def log_publication_unapproved(content, event):
    LoggingEvent('revoke', content).log()

@grok.subscribe(IVersion, events.IContentPublishedEvent)
def log_publication_published(content, event):
    LoggingEvent('publish', content).log()

@grok.subscribe(IVersion, events.IContentClosedEvent)
def log_publication_closed(content, event):
    LoggingEvent('close', content).log()


# Upgrade

@grok.subscribe(ISilvaObject, events.IUpgradeStartedEvent)
def log_upgrade_start(content, event):
    # Disable logging during upgrade
    detail = "from %s to %s" % (event.from_version, event.to_version)
    event = LoggingEvent('upgrade start', content, detail)
    event.log()
    event.disable()

@grok.subscribe(ISilvaObject, events.IUpgradeFinishedEvent)
def log_upgrade_finished(content, event):
    detail = "from %s to %s (%s)" % (
        event.from_version, event.to_version,
        event.success and 'success' or 'failure')
    event = LoggingEvent('upgrade finished', content, detail)
    event.enable()
    event.log()
