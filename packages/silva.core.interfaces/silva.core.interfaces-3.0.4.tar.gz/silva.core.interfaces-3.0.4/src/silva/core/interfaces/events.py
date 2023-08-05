# -*- coding: utf-8 -*-
# Copyright (c) 2009-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from zope.interface import Interface, Attribute, implements
from zope.component.interfaces import IObjectEvent, ObjectEvent
from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.lifecycleevent import ObjectModifiedEvent
from zope.lifecycleevent import ObjectCreatedEvent
from silva.core.interfaces.adapters import IRequestForApprovalStatus


# Root installation

class IInstallEvent(IObjectEvent):
    """An installation happened.
    """


class IInstallRootServicesEvent(IInstallEvent):
    """Root default services are being installed in a newly created
    Silva root.

    Silva extensions should listen to this event to add theirs
    required services to a newly created Silva root.
    """


class InstallRootServicesEvent(ObjectEvent):
    implements(IInstallRootServicesEvent)


class IInstalledExtensionEvent(IObjectEvent):
    """An extension have been installed.
    """
    root = Attribute(u"Root in which the extension have been installed")
    extension = Attribute(u"Extension that have been installed")


class InstalledExtensionEvent(ObjectEvent):
    implements(IInstalledExtensionEvent)

    def __init__(self, extension, root):
        super(InstalledExtensionEvent, self).__init__(extension.installer)
        self.extension = extension
        self.root = root


class IInstalledServiceEvent(IObjectEvent):
    """A service has been installed.

    A Silva extensions that want to configure, or register itself to a
    service after its installation should listen to this event.
    """


class InstalledServiceEvent(ObjectEvent):
    implements(IInstalledServiceEvent)


class IInstallRootEvent(IInstallEvent):
    """A new Silva root is being installed. Root services are already
    installed and should be usable.

    Extensions should listen to this event if they wish to install
    additional configuration inside the newly created Silva root.
    """


class InstallRootEvent(ObjectEvent):
    implements(IInstallRootEvent)


# Content created event

class IContentCreatedEvent(IObjectCreatedEvent):
    """A new content have been created. This event is only called with
    ISilvaObject objects. Other created object use the default Zope
    event, ObjectCreatedEvent.
    """
    no_default_version = Attribute(u"True if no default version was created")
    no_default_content = Attribute(u"True if no default content was created")


class ContentCreatedEvent(ObjectCreatedEvent):
    implements(IContentCreatedEvent)

    def __init__(self, obj, no_default_version=False, no_default_content=False):
        super(ContentCreatedEvent, self).__init__(obj)
        self.no_default_version = no_default_version
        self.no_default_content = no_default_content


# Ordered content move

class IContentOrderChangedEvent(IObjectEvent):
    """The position of a content have changed in an ordered container.
    """
    new_position = Attribute(u"New content position")
    old_position = Attribute(u"Old content position")


class ContentOrderChangedEvent(ObjectEvent):
    implements(IContentOrderChangedEvent)

    def __init__(self, obj, new_position, old_position):
        super(ContentOrderChangedEvent, self).__init__(obj)
        self.new_position = new_position
        self.old_position = old_position


# Content publication

class IPublishingEvent(IObjectModifiedEvent):
    """A publication action has been done.
    """


class IApprovalEvent(IPublishingEvent):
    """A approval operation is going on.
    """
    status = Attribute('Request for approval status')


class IContentApprovedEvent(IApprovalEvent):
    """A content has been approved.
    """


class IContentUnApprovedEvent(IApprovalEvent):
    """A content has been unapproved.
    """


class IRequestApprovalEvent(IApprovalEvent):
    """An approval request is being managed.
    """


class IRequestApprovalFailedEvent(IRequestApprovalEvent):
    """An approval request has been managed.
    """


class IContentRequestApprovalEvent(IRequestApprovalEvent):
    """A content seeks to be approved.
    """


class IContentApprovalRequestWithdrawnEvent(IRequestApprovalFailedEvent):
    """A content request for approval have been cancelled.
    """


class IContentApprovalRequestRefusedEvent(IRequestApprovalFailedEvent):
    """A content request for approval have been refused.
    """


class IContentPublishedEvent(IPublishingEvent):
    """A content has been published.
    """


class IContentClosedEvent(IPublishingEvent):
    """A content as been closed.
    """


class IContentExpiredEvent(IContentClosedEvent):
    """A content expired.
    """


class PublishingEvent(ObjectModifiedEvent):
    implements(IPublishingEvent)


class ApprovalEvent(PublishingEvent):
    implements(IApprovalEvent)

    def __init__(self, obj, status=None):
        super(ApprovalEvent, self).__init__(obj)
        if status is None:
            status = IRequestForApprovalStatus(obj)
        self.status = status


class ContentApprovedEvent(ApprovalEvent):
    implements(IContentApprovedEvent)


class ContentUnApprovedEvent(ApprovalEvent):
    implements(IContentUnApprovedEvent)


class ContentRequestApprovalEvent(ApprovalEvent):
    implements(IContentRequestApprovalEvent)


class ContentApprovalRequestWithdrawnEvent(ApprovalEvent):
    implements(IContentApprovalRequestWithdrawnEvent)


class ContentApprovalRequestRefusedEvent(ApprovalEvent):
    implements(IContentApprovalRequestRefusedEvent)


class ContentPublishedEvent(PublishingEvent):
    implements(IContentPublishedEvent)


class ContentClosedEvent(PublishingEvent):
    implements(IContentClosedEvent)


class ContentExpiredEvent(ContentClosedEvent):
    implements(IContentExpiredEvent)


# Content import/export

class IContentImportedExported(IObjectEvent):
    """A content have been imported or exported from the site.
    """


class IContentImported(IContentImportedExported):
    """A new content have been imported in the site.
    """


class IContentExported(IContentImportedExported):
    """A content have been exported from the site.
    """


class ContentImportedExported(ObjectEvent):
    implements(IContentImportedExported)


class ContentImported(ContentImportedExported):
    implements(IContentImported)


class ContentExported(ContentImportedExported):
    implements(IContentExported)


# Security

class ISecurityEvent(IObjectEvent):
    """A security setting has been changed.
    """


class ISecurityRestrictionModifiedEvent(ISecurityEvent):
    """A security restriction has been set on an object.
    """
    role = Attribute(u"Role needed to access the object")


class ISecurityRoleChangedEvent(ISecurityEvent):
    """A security role has been changed for a user.
    """
    username = Attribute(u"Username affected by the change.")
    roles =  Attribute(u"Modified role.")


class ISecurityRoleAddedEvent(ISecurityRoleChangedEvent):
    """A role as been attributed to a user.
    """


class ISecurityRoleRemovedEvent(ISecurityRoleChangedEvent):
    """A user as seen its access revoked.
    """


class SecurityRestrictionModifiedEvent(ObjectEvent):
    implements(ISecurityRestrictionModifiedEvent)

    def __init__(self, obj, role):
        super(SecurityRestrictionModifiedEvent, self).__init__(obj)
        self.role = role


class SecurityRoleChangedEvent(ObjectEvent):
    implements(ISecurityRoleChangedEvent)

    def __init__(self, obj, username, roles):
        super(SecurityRoleChangedEvent, self).__init__(obj)
        self.username = username
        self.roles = roles


class SecurityRoleAddedEvent(SecurityRoleChangedEvent):
    implements(ISecurityRoleAddedEvent)


class SecurityRoleRemovedEvent(SecurityRoleChangedEvent):
    implements(ISecurityRoleRemovedEvent)


# Upgrade events

class IUpgradeEvent(IObjectEvent):
    """Upgrade related event.
    """
    from_version = Attribute(u"Orginal version")
    to_version = Attribute(u"Final version")


class IUpgradeTransaction(Interface):
    """A new upgrade transaction has started.
    """


class IUpgradeStartedEvent(IUpgradeEvent):
    """Upgrade started.
    """


class IUpgradeFinishedEvent(IUpgradeEvent):
    """Upgrade finished.
    """
    success = Attribute(u"true if the upgrade was successful")


class UpgradeTransaction(object):
    implements(IUpgradeTransaction)


class UpgradeStartedEvent(ObjectEvent):
    implements(IUpgradeStartedEvent)

    def __init__(self, obj, from_version, to_version):
        super(UpgradeStartedEvent, self).__init__(obj)
        self.from_version = from_version
        self.to_version = to_version


class UpgradeFinishedEvent(ObjectEvent):
    implements(IUpgradeFinishedEvent)

    def __init__(self, obj, from_version, to_version, success):
        super(UpgradeFinishedEvent, self).__init__(obj)
        self.from_version = from_version
        self.to_version = to_version
        self.success = success
