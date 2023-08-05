# -*- coding: utf-8 -*-
# Copyright (c) 2011-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from silva.translations import translate as _
from zope.interface import Interface, Attribute, implements
from zope.schema.interfaces import InvalidValue

# Ghost validation

class InvalidTarget(InvalidValue):
    __doc__ = _("Invalid ghost target.")


class EmptyInvalidTarget(InvalidTarget):
    __doc__ = _(u"Missing required ghost target.")


class CircularInvalidTarget(InvalidTarget):
    __doc__ = _(u"Ghost target creates a circular reference.")


class GhostInvalidTarget(InvalidTarget):
    __doc__ = _(u"Ghost target is a ghost.")


class ContainerInvalidTarget(InvalidTarget):
    __doc__ = _(u"Ghost target should be a container.")


class AssetInvalidTarget(InvalidTarget):
    __doc__ = _(u"Ghost target should be an asset.")


class ContentInvalidTarget(InvalidTarget):
    __doc__ = _(u"Ghost target should be a content.")


# Silva errors

class IError(Interface):
    """A generic Silva error.
    """
    reason = Attribute(
        u'Translatable text message explaining the error.')


class IContentError(IError):
    """An error related to a specific content in Silva.
    """
    content = Attribute(
        u'Related content to the error.')


class IContentErrorBundle(IContentError):
    """An error related to a specific content in Silva that is
    actually due a bundle of other errors.
    """
    errors = Attribute(
        u'List of errors')


class IUpgradeError(IContentError):
    """An error related to the upgrade of a content during the upgrade
    process in Silva.
    """

class ISecurityError(IContentError):
    """An error related to a security issue with a specific content in
    Silva.
    """

class IUnauthorizedRoleAssignement(ISecurityError):
    """An unauthorized role assignement.
    """
    role = Attribute(
        u"Role affected.")
    identifier = Attribute(
        u"Identifier to which the role modification is denied.")


class IContainerError(IContentError):
    """An error related to a specific content with a specific
    container in Silva.
    """


class IVersioningError(IContentError):
    """An error related to the versioning of a specific content in Silva.
    """
    version = Attribute(
        u'Related content version that triggered the error, if applicable.')


class IExportError(IContentError):
    """An error related to the export of a content in Silva.
    """


class IExternalReferenceError(IExportError):
    """An error related to the export of a content in Silva, that have
    a reference to an another content not included inside of the
    export tree.
    """
    exported = Attribute(
        u'Exported content.')
    target = Attribute(
        u'Target of the reference.')


class Error(Exception):
    implements(IError)

    def __init__(self, reason):
        super(Error, self).__init__(reason)
        self.reason = reason


class ContentError(Error):
    implements(IContentError)

    def __init__(self, reason, content):
        super(ContentError, self).__init__(reason)
        self.content = content


class ContentErrorBundle(ContentError):
    implements(IContentErrorBundle)

    def __init__(self, reason, content, errors):
        super(ContentErrorBundle, self).__init__(reason, content)
        self.errors = errors


class UpgradeError(ContentError):
    implements(IUpgradeError)


class SecurityError(ContentError):
    implements(ISecurityError)


class UnauthorizedRoleAssignement(SecurityError):
    implements(IUnauthorizedRoleAssignement)

    def __init__(self, reason, content, role, identifier):
        super(UnauthorizedRoleAssignement, self).__init__(reason, content)
        self.role = role
        self.identifier = identifier


class ContainerError(ContentError):
    implements(IContainerError)


class VersioningError(ContentError):
    implements(IVersioningError)

    def __init__(self, reason, content, version=None):
        super(VersioningError, self).__init__(reason, content)
        self.version = version


class ExportError(ContentError):
    implements(IExportError)


class ExternalReferenceError(ExportError):
    implements(IExternalReferenceError)

    def __init__(self, reason, content, target, exported):
        super(ExternalReferenceError, self).__init__(reason, content)
        self.target = target
        self.exported = exported

