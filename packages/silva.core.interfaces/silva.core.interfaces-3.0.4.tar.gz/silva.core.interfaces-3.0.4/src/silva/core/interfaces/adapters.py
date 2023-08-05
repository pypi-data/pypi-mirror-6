# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt


from zope.interface import Interface, Attribute


class IContentImporter(Interface):
    """Generic content importer.
    """


class IArchiveFileImporter(IContentImporter):

    def importArchive(archivefile, assettitle=None, recreatedirs=1, replace=0):
        """Import archive file

        Use 'assettitle' for the title to set on all assets created

        According to the recreatedirs setting, create a substructure of
        Silva Containers (probably Silva Folders) reflecting the structure
        of the archive file. This substructure will be created relative to
        the adapted context.

        If replace is true, replace items with identical ids.

        Return a tuple with the list of succeeded items and failed items
        providing feedback on what archive contents have succesfully been
        imported into Silva Assets and what contents have not.
        """


class IZipFileImporter(IContentImporter):

    def isFullmediaArchive(input_archive):
        """Tests if the zip archive is a fullmedia archive
        """

    def importFromZip(input_archive, request, replace=False):
        """Import Silva content from a full media opened zip
        file. Optionaly replace content.
        """


# BBB
IZipfileImporter = IZipFileImporter


class IContentExporter(Interface):
    """Adapter for export context content in a file.
    """

    name = Attribute(
        u"Name of the registered exporter.")
    extension = Attribute(
        u"Filename extension of the created export files.")
    options = Attribute(
        u"Interface describing the list of expected options.")

    def export(request, **options):
        """Export context with given settings.
        """


class IDefaultContentExporter(IContentExporter):
    """This mark the default content exporter.
    """


class IAssetPayload(Interface):

    def get_payload():
        """ Get actual data stored for this asset, or None.
        """


class IIndexEntries(Interface):

    def get_title():
        """Returns the title of the indexable.
        """

    def get_entries():
        """Returns the indexes for a certain object, or an empty list.
        """


class ILanguageProvider(Interface):

    def getAvailableLanguages():
        """Return the available languages.
        """

    def setPreferredLanguage(language):
        """Sets the preferred language.
        """

    def getPreferredLanguage():
        """Gets the preferred language.
        """


class IFeedEntryProvider(Interface):
    """Adapter to a object which provides a list feed entry that can
    used to build a RSS/Atom feed.
    """

    def entries():
        """Generate IFeedEntry objects.
        """


class IFeedEntry(Interface):
    """Adapter to object to provide information to include in a
    RSS/Atom feed.
    """

    def id():
        """Give the id of the object.
        """
        pass

    def title():
        """Give the title.
        """

    def html_description():
        """Give an HTML description.
        """

    def description():
        """Give an non-HTML description.
        """

    def url():
        """Give the URL of the object.
        """

    def authors():
        """Give a list of authors.
        """

    def date_updated():
        """Date at which the content have been updated.
        """

    def date_published():
        """Publication date.
        """

    def subject():
        """Content subject.
        """

    def keywords():
        """Give a list of keywords matching the content
        """


class ISiteManager(Interface):
    """Adapt a publication to manage its local site status.
    """

    def make_site():
        """Make the publication become a local site.

        It raises ``ValueError`` in case of error.
        """

    def delete_site():
        """Remove the local site from the publication. No local
        services must be registered on the site for this to be
        successful.

        It raises ``ValueError`` in case of error.
        """

    def is_site():
        """Return True if the publication is a local site, False if
        not.
        """


class IHaunted(Interface):
    """Interface for haunted adapter
    """

    def getHaunting():
        """Return iterator of objects (ghosts) haunting the adapted object.
        """


class IRequestForApprovalStatus(Interface):
    """Status about the request for approval.
    """
    pending = Attribute(
        u'True if a request is pending')
    messages = Attribute(
        u'List of messages associated with the request')

    def comment(status, message=None):
        """Update the request status, with an optional message.
        """

    def validate():
        """The request is validated. It is finshed.
        """

    def reset():
        """Reset the request. All history is lost forever.
        """


class IVersionManager(Interface):

    def make_editable():
        """revert a previous version to be editable version

        The current editable will become the last closed (last closed
        will move to closed list). If the published version will not
        be changed.

        Raises AttributeError when version id is not available.

        Raises VersioningError when 'editable' version is approved or
        in pending for approval.
        """

    def get_modification_datetime():
        """Return last modification time for the given version.
        """

    def get_publication_datetime():
        """Return publication time for the given version.
        """

    def get_expiration_datetime():
        """Return expiration time for the given version.
        """

    def get_last_author():
        """Return the last author of the given version.
        """

    def get_status():
        """Return the version status.
        """

    def delete():
        """Delete a version,

        Can raise AttributeError when the version doesn't exist,
        ``VersioningError`` if the version is approved or published.
        """


class IPublicationWorkflow(Interface):
    """ Publication workflow of silva objects.

    All the following methods may raise a ``VersioningError``.
    """

    def new_version():
        """Create a new version if one is published or closed.
        """

    def request_approval(message):
        """Issue a request for approval.
        """

    def withdraw_request(message):
        """Withdraw a previous request for approval.
        """

    def reject_request(message):
        """Reject a request for approval.
        """

    def revoke_approval():
        """Revoke the currently approved version.
        """

    def publish():
        """Approve unapproved or last closed version.
        """

    def approve(time=None):
        """ Approve unapproved version. Set the publication date to
        the given ``time``, or to now if it is None.
        """

    def close():
        """ Close published version.
        """

    def get_versions(sort_attribute='id'):
        """Return a list of versions.

        If ``sort_attribute`` is False, no sorting is done. By default
        it sorts on ``id`` converted to int (so you receive
        [0,1,2,3,...] instead of [0,1,10,2,3,...]).
        """


class IAddableContents(Interface):
    """Return addables that can be added in the adapted container.
    """

    def get_authorized_addables(require=None):
        """Get a list of content that the current user is allowed to
        add in the adapted container (they can be added to the site,
        are not restricted in that container, and the current user
        have the permission to add them).

        If require is not None, it is an interface that the all the
        returned addable must implement.
        """

    def get_container_addables(require=None):
        """Get a list of content that can be added in the adapter
        container (they can be added to the site, and are not
        restricted in that container).

        If require is not None, it is an interface that the all the
        returned addable must implement.
        """

    def get_all_addables(require=None):
        """Get a list of all content that could be added in the
        adapted container (they can be added to the site).

        If require is not None, it is an interface that the all the
        returned addable must implement.
        """


class IContainerManager(Interface):
    """Operation on container contents. Each method returns a coroutine
    object, that can be used as a context manager.
    """

    def renamer():
        """Rename content into this container.

        The coroutine takes as argument a tuple, containing a Silva
        content, a new identifier, and a new title. It will rename
        accordingly the content inside the current container. If you
        do not wish the change the identifier or the title, you can
        pass ``None`` instead for those values. It will return the
        renamed content, or a ``ContentError`` in case of failure.
        """

    def copier():
        """Copy content into this container.

        The coroutine takes as argument a Silva content, that is copied
        in the current container, and return the copy, or a
        ``ContentError`` is case of failure.
        """

    def mover():
        """Move content into this container.

        The coroutine takes as argument a Silva content, that is moved
        inside the current container, and return the moved content, or
        a ``ContentError`` in case of failure.
        """

    def ghoster():
        """Ghost content into this container.

        The coroutine takes as argument a Silva content, and will
        either create a ghost of it inside the current container (if
        it is publishable content), or will copy it inside the current
        container (if it is an asset). The ghost or copy will be
        return, or a ``ContentError`` in case of failure.
        """

    def deleter():
        """Delete content that are in this container.

        The coroutine takes as argument a Silva content, and will
        delete this content from the current container. It will return
        the deleted content, or a ``ContentError`` in case of failure.
        """


class IOrderManager(Interface):
    """Manage order of a container content.
    """
    order = Attribute(u"List storing the order of the contents.")
    order_only = Attribute(u"Interface restricting ordered content")

    def add(content):
        """Add a new content to the order list, if possible.
        """

    def remove(content):
        """Remove a content from the order list, if needed.
        """

    def move(content, index):
        """Move content just before index.
        Return true in case of success, False in case of failure.
        """

    def get_position(content):
        """Return the position of a content, or -1 if the content is
        unknown or has no position.
        """

    def __len__():
        """Return the number of content in the order list.
        """

    def repair(contents):
        """Ensure the order manages only the given contents. This can
        be used if the order goes out of sync with the real
        one. Return True in case of modification, False if nothing was
        changed.

        IF YOU GIVE THE WRONG CONTENTS TO THE MANAGER, ORDER WILL BE
        LOST.
        """

class ITreeContents(Interface):

    def get_tree(depth=-1):
        """Get flattened tree of all active publishables. The 'depth'
        argument limits the number of levels, defaults to unlimited.
        This is a list of indent, object tuples.
        """

    def get_container_tree(depth=-1):
        """Get flattened tree of all sub-containers. The 'depth'
        argument limits the number of levels, defaults to unlimited.
        This is a list of indent, object tuples.
        """

    def get_public_tree(depth=-1):
        """Get flattened tree with public content not hidden from
        tocs, excluding subpublications. The 'depth' argument limits
        the number of levels, defaults to unlimited. This is a list
        of indent, object tuples.
        """

    def get_public_tree_all(depth=-1):
        """Get flattened tree with all public content, excluding
        subpublications.  The 'depth' argument limits the number of
        levels, defaults to unlimited.  This is a list of indent,
        object tuples.
        """

    def get_status_tree(depth=-1):
        """Get tree of all active content objects. For containers,
        show the default object if available.  This is a list of
        indent, object tuples.
        """


class IGhostManager(Interface):

    def modify(target, identifier=None):
        """Return a ghost manipulator object to create, modify and
        update it following a standard API.
        """

    def validate(target, adding=True):
        """Validate target is valid for the given ghost object.
        """



class IIcon(Interface):
    """An icon for a content type.
    """
    icon = Attribute('Icon')
    template = Attribute('Template of a tag to render the icon')

    def get_url(view, content):
        """Return the URL of the icon for the given content.
        """


class IIconResolver(Interface):
    """Adapt a Zope request to return a content icon.
    """
    sprite = Attribute('Sprite being used to lookup icons')

    root_url = Attribute('URL of the site')

    def get_tag(content=None, identifier=None):
        """Return a tag that generate an icon associated to the
        content or identifier.
        """

    def get_identifier(identifier, default):
        """Return the icon associated to the given meta_type
        identifier. If the icon is not found, an icon matching default
        can be lookup for (not required). If it is not found, ``None``
        is returned.
        """

    def get_content(content):
        """Return the icon associated to the given Zope content.
        """

    def get_identifier_url(identifier, default):
        """Return the full icon URL associated to the given
        meta_type_identifier. If the icon is not found, the URL of an
        icon matching default can be looked up for (not required). If
        it is not found, ``None`` is returned.
        """

    def get_content_url(content):
        """Return the full icon URL associated to the given Zope
        content.
        """



