# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt


from zope import interface
from zope.container.interfaces import INameChooser
from zope.annotation import IAttributeAnnotatable
from grokcore.component.interfaces import IContext


class IHTTPHeadersSettings(interface.Interface):
    """Settings for IHTTPResponseHeaders on Silva objects
    """
    # XXX Add an override for the developer to always disable caching without
    # letting the user choose.
    http_disable_cache = interface.Attribute('Prevent caching altogether')
    http_max_age = interface.Attribute('Max caching ime')
    http_last_modified = interface.Attribute('Add Last-Modified headers')


class ICustomizable(interface.Interface):
    """Layout-customizable content
    """


class ISilvaXMLExportable(interface.Interface):
    """Exportable content in Silva XML
    """


class IXMLZEXPExportable(ISilvaXMLExportable):
    """Content that is exportable via the fallback ZEXP exportable
    handler.
    """


class IDirectlyRendered(interface.Interface):
    """Content directly rendered without the help of a layout
    """


class IQuotaObject(interface.Interface):
    """Content that can be accounted inside a site quota
    """

    def get_quota_usage():
        """Return the space used by this content.
        """

    def update_quota():
        """Update used space, and verify quota for this content.
        """

    def reset_quota():
        """Reset the status of the quota.
        """

class IQuotaContainer(interface.Interface):
    """Container that aggregate the usage of the contained quota items
    """
    used_space = interface.Attribute(u"Used space by quota items.")

    def update_used_space(delta, verify):
        """Update used space with ``delta``, and verify quota for this
        folder. This is a private method (meaning it can't be called
        from the ZODB).
        """


class IReferable(interface.Interface):
    """Content can be referred by an another
    """


class ISecurity(interface.Interface):
    """Content with author and creator information
    """

    def get_creator_info():
        """Return the member object corresponding to the creator of
        this content object.
        """

    def get_last_author_info():
        """Return the member object corresponding to the last author
        who modified this content object.
        """

    def set_last_author_info(user):
        """Set the last author information to the given user.
        """


class ITitledObject(interface.Interface):
    """Content with a title
    """

    def get_title():
        """The title of the content object.
        """

    def get_title_or_id():
        """The title, or the identifier if there is no title of the
        content object.
        """

    def get_short_title():
        """Return the short title of the content object. If there is
        no short title, when the title is returned. If there is no
        title, when the identifier is returned.
        """

    def set_title(title):
        """Change the title of the content object if possible.
        """


class IEditableTitledObject(ITitledObject):

    def get_editable():
        """Get the editable version (may be object itself). Returns
        ``None`` if there is no such version.
        """

    def get_title_editable():
        """Get the title of the editable version if possible.
        """

    def get_short_title_editable():
        """Get the short title of the editable version if possible.
        """

    def get_title_or_id_editable():
        """Get the title of the editable version if possible, or id if
        not available.
        """


class ISilvaObject(IContext,
                   IReferable,
                   IAttributeAnnotatable,
                   ISecurity,
                   IEditableTitledObject,
                   ISilvaXMLExportable):
    """Silva Content
    """

    def get_silva_object():
        """Used by acquisition to get the nearest containing
        SilvaObject.
        """

    def get_creation_datetime():
        """Return of creation datetime of the object. Return None if
        not supported.
        """

    def get_modification_datetime():
        """Return the last modification datetime of the object. Return
        None if not supported.
        """

    def is_deletable():
        """Returns True if object is deletable right now.
        """


class IImageIncluable(ISilvaObject):
    """Content represent an image that can be included in text
    """


class IViewableObject(ICustomizable):
    """Silva Content viewable by the public
    """

    def get_previewable():
        """Get the previewable version (may be the object itself if no
        versioning).
        Returns None if there is no such version.
        """

    def get_viewable():
        """Get the publically viewable version (may be the object itself if
        no versioning).
        Returns None if there is no such version.
        """


class IPublishable(ISilvaObject, IViewableObject):
    """Content that can be published to the public

    They can appear in table of contents.
    """

    def is_default():
        """True if this content object is the default content object
        of the folder.
        """

    def is_published():
        """Return true if this object is visible to the public.
        """

    def is_approved():
        """Return true if this object is versioned or contains
        versioned content that is approved.
        """


class INonPublishable(ISilvaObject):
    """A content which is not publicly directly viewable

    A non publisable content never appears in the navigation or in
    table of contents.
    """


###############################################################
### Container
###############################################################

class IContainer(IPublishable, IQuotaContainer):
    """Container

    Contains content.
    """

    # ACCESSORS
    def get_container():
        """Get the nearest container in the acquisition hierarchy.
        (this one)
        """

    def is_transparent():
        """Show this subtree in ``get_tree()``.
        """

    def get_default():
        """Get the default content object of the folder. If
        no default is available, return None.
        """


class IOrderableContainer(IContainer):
    """Ordered Container

    Content in that container can be ordered.
    """


class IFolder(IOrderableContainer):
    """Folder
    """

    # Get content
    def get_ordered_publishables(interface=IPublishable):
        """Get list of active publishables of this folder, in
        order.

        You can restrict futher the list by providing an interface.
        """

    def get_non_publishables(interface=INonPublishable):
        """Get a list of non-publishable objects in this folder,
        sorted in alphabetical order. This includes assets,
        configuration objects and anything else that is not a
        publishable.

        You can restrict futher the list by providing an interface.
        """

    # Set addables
    def set_silva_addables_allowed_in_container(addables):
        """Set the list of addables explicitly allowed in this
        container.  If 'addables' is set to None the list is acquired
        from the container higher in the hierarchy. If this is the
        root, return the complete list.
        """

    def get_silva_addables_allowed_in_container():
        """Get a list of all addables explicitly allowed in this
        container.
        """

    def is_silva_addables_acquired():
        """Return true if the list of addables is acquired from above
        (set_silva_addables_allowed_in_container set to None), false
        if not.
        """


class IPublication(IContainer):
    """Publication
    """

    def get_publication():
        """Return the nearest publication by acquisition.
        """


class IRoot(IPublication):
    """Root
    """

    def get_root():
        """Get root of site.
        """

    def add_silva_addable_forbidden(meta_type):
        """Forbid use of meta_type in SMI. The meta_type won't show
        up anymore, including in the publication metadata tab where
        individual items can be disabled for particular publications.
        """

    def clear_silva_addables_forbidden():
        """Clear any forbidden addables. All addables show up in the
        SMI again.
        """

    def is_silva_addable_forbidden(meta_type):
        """Returns true if meta_type should not show up in the SMI.
        """


###############################################################
### Content
###############################################################


class IContent(IPublishable):
    """Silva non-container content

    Those objects that can be published directly and would appear
    in the table of contents. Can be ordered.
    """
    # ACCESSORS
    def get_content():
        """Used by acquisition to get the nearest containing content
        object.
        """


class IAutoTOC(IContent):
    """Automatic table of content
    """


class IIndexer(IContent):
    """Indexer
    """

    def get_index_names():
        """Returns a list of all index entry names in the index,
        sorted alphabetically.
        """

    def get_index_entry(entry):
        """Returns a list of (title, path) tuples for an entry name in the
        index, sorted alphabetically on title
        """

    def update():
        """Update the index.
        """


###############################################################
### Versioned content
###############################################################

class IVersioning(interface.Interface):
    """Can be mixed in with an object to support simple versioning.
    This interface only keeps a reference id to the version and the
    various datetimes. The versioned objects themselves are not
    managed by this interface (see VersionedContent instead).
    """

    # MANIPULATORS
    def create_copy(version_id=None):
        """Copy a version as currently editable one.
        """

    def approve_version():
        """Approve the current unapproved version.
        """

    def unapprove_version():
        """Unapproved an approved but not yet published version.
        """

    def close_version():
        """Close the public version.
        """

    def request_version_approval(message):
        """Request approval for the current unapproved version
        Implementation should raise VersioningError, if there
        is no such version.
        Returns None otherwise
        """

    def withdraw_version_approval(message):
        """Withdraw a previous request for approval
        Implementation should raise VersioningError, if the
        currently unapproved version has no request for approval yet,
        or if there is no unapproved version.
        """

    def reject_version_approval(message):
        """Reject a request for approval made by some Author
        Implementation should raise VersioningError, if the
        currently unapproved version has no request for approval yet,
        or if there is no unapproved version.
        One need to have the ApproveSilvaContent permission to call
        this method
        """

    def set_unapproved_version_publication_datetime(dt):
        """Set the publicationd datetime for the unapproved version,
        or None if this is not yet known.
        """

    def set_unapproved_version_expiration_datetime(dt):
        """Set the expiration datetime of the unapproved version,
        or None if it never expires.
        """

    def set_approved_version_publication_datetime(dt):
        """Change the publication datetime for the approved version.
        """

    def set_approved_version_expiration_datetime(dt):
        """Change the expiration datetime for the approved version, or
        None if there is no expiration.
        """

    # ACCESSORS

    def is_approved():
        """Check whether there exists an approved version.
        """

    def is_published():
        """Check whether there exists a published version.
        """

    def is_approval_requested():
        """Check if there exists an unapproved version
        which has a request for approval.
        """

    def get_unapproved_version():
        """Get the id of the unapproved version.
        """

    def get_unapproved_version_publication_datetime():
        """Get the publication datetime for the unapproved version,
        or None if no publication datetime yet.
        """

    def get_unapproved_version_expiration_datetime():
        """Get the expiration datetime for the unapproved version,
        or None if no publication datetime yet.
        """

    def get_approved_version():
        """Get the id of the approved version.
        """

    def get_approved_version_publication_datetime():
        """Get the publication of the approved version.
        """

    def get_approved_version_expiration_datetime():
        """Get the expiration datetime for the approved version,
        or None if no expiration datetime yet.
        """

    def get_next_version():
        """Get the id of the next version. This is the approved version
        if available, or the unapproved version otherwise, or None if
        there is no next version at all.
        """

    def get_next_version_publication_datetime():
        """Get the publication datetime of the next version, or None
        if no such datetime is known.
        """

    def get_next_version_expiration_datetime():
        """Get the expiration datetime of the next version, or None
        if there is no expiration datetime.
        """

    def get_public_version():
        """Get the id of the public version.
        """

    def get_first_publication_date():
        """Get the earliest publication date of any version of this Content.
        Needed for rss/atom feeds.
        """

    def get_public_version_publication_datetime():
        """Get the publication datetime of the public version.
        """

    def get_public_version_expiration_datetime():
        """Get the expiration datetime of the public version, or
        None if this version never expires.
        """

    def get_previous_versions():
        """Get a list of the ids of the most recent versions (that
        are not public anymore. Index 0 is oldest, up is more recent
        versions).
        """

    def get_last_closed_version():
        """Get the id of the version that was last closed, or None if
        no such version.
        """


class IVersionedObject(IVersioning, ISilvaObject, IViewableObject):
    """Object that can have versions
    """


class IVersionedNonPublishable(IVersionedObject, INonPublishable):
    """Non publishable object that can have versions
    """


class IVersionedContent(IVersionedObject, IContent):
    """Content that can have versions
    """

    # MANIPULATORS
    def create_copy():
        """Create a new copy of the public version. Automatically
        assign a new id for this copy and register this as the
        next version. If there is already a next version, this
        operation will fail.
        """


class IVersion(IReferable, ISecurity, ITitledObject, IAttributeAnnotatable):
    """Version of a versioned content

    A version effectively store the data of the content.
    """


class ILinkVersion(IVersion):
    """Version of a Silva Link content
    """


class ILink(IVersionedContent):
    """Silva Link content

    Silva Link can be used to create links to either other contents in
    Silva or to external URLs.
    """

###############################################################
### Asset
###############################################################


class IAsset(INonPublishable, IViewableObject, IQuotaObject):
    """Asset content

    An asset is a resource which is not a content object by itself,
    but contain data. Files and Images are assets for example.
    """

    # ACCESSORS

    def get_filename():
        """Return filename of the asset as it is downloaded by the
        user.
        """

    def get_file_size():
        """Get data size as it will be downloaded.
        """

    def get_file_system_path():
        """Return file system path of the asset.
        """

    def get_mime_type():
        """Get data mime-type.
        """


class IDownloableAsset(IAsset):

    def get_html_tag(preview=False, request=None, **extra_attributes):
        """Return an HTML tag that points to the asset.
        """

    def get_download_url(preview=False, request=None):
        """Return an URL to download the asset.
        """


class IFile(IDownloableAsset, IDirectlyRendered):
    """Silva File content to encapsulate "downloadable" data
    """
    # MANIPULATORS

    def set_file(stream, content_type=None, content_encoding=None):
        """Re-upload data for this file object. It will change the
        ``content_type`` and ``content_encoding``, however id, title,
        etc. will not change. If ``content_type`` is None, it will be
        detected with ``content_encoding``, if possible.
        """

    def set_text(text):
        """Set content of the file from the given string.
        """

    def set_filename(filename):
        """Set the filename as it is downloaded by the user.
        """

    def set_content_type(content_type):
        """Set file content type. It will be sent to users downloading
        that file. This is used as well to compute the
        mime-type/extension of the file.
        """

    def set_content_encoding(content_encoding):
        """Set the file content encoding: gzip, bzip2 or none.
        """

    # ACCESSORS

    def get_content_type():
        """Return the file content type as it is send to a visitor
        while downloading the file.
        """

    def get_content_encoding():
        """Return the file content encoding.
        """

    def get_text():
        """Return the text content of the file or TypesError is it's
        not a text file.
        """

    def is_text():
        """Return True if the file content is text based.
        """

    def get_file():
        """Return the content of the file in any cases.
        """

    def get_file_fd():
        """Return a file descriptor to access the file data.
        """


class IZODBFile(IFile):
    """A file stored in ZODB
    """


class IFileSystemFile(IFile):
    """A file stored on the file system
    """


class IBlobFile(IFile):
    """A file stored with the help of a blob
    """


class IImage(IDownloableAsset, IImageIncluable, IDirectlyRendered):
    """Silva Image

    A Silva Image can be used in a Silva Document. An image stored
    three images for each uploaded image:

    - The original image often called hires image,

    - The web image (which can be a resized and cropped from the
      original image),

    - A thumbnail created from the original image.
    """

    thumbnail_size = interface.Attribute(
        u"Maximum width or height of the thumbnail image in pixels.")

    def set_image(file):
        """Set the image from the given ``file``. It must have a
        ``read`` method to retrieve the raw data of the image. This
        will computed  web version and a thumbnail of the new image.
        """

    def set_web_presentation_properties(web_format, web_scale, web_crop):
        """Sets format, scaling and cropping information to create the
        web image.

        - ``web_format`` (str): either ``JPEG``, ``GIF`` or ``PNG``,

        - ``web_scale`` (str): WidthXHeight or nn.n%.

        - ``web_crop`` (str): X1xY1-X2xY2, crop-box or empty for no
          cropping.

        Raises ``ValueError`` if ``web_scale`` cannot be parsed.  If
        changing the settings succeed, it will update the web version
        of the image.
        """

    def get_html_tag(preview=False, request=None, hires=False, thumbnail=False,**extra_attributes):
        """Generate a image tag to render either the original version
        (if ``hires`` set to True), or the thumbnail (if ``thumbnail``
        set to True) or the web version (by default).

        If some ``extra_attributes`` are given, they will be added to
        the image tag as HTML attributes.
        """


    def get_download_url(preview=False, request=None, hires=False, thumbnail=False):
        """Return an URL to download the corresponding image. If ``hires``
        is True, the URL to the original version will be returned and
        if ``thumbnail`` is True the URL to the thumbnail will be returned
        instead.
        """

    def get_crop_box(crop=None):
        """Return a tuple describing the current crop box used to
        create the web image. The describe the coordinate of the top
        left and the bottom right corner.
        """

    def get_canonical_web_scale(scale=None):
        """returns (width, height) of web image
        """

    def get_orientation():
        """Returns the image orientation: ``square``, ``landscape`` or
        ``portrait``.
        """

    def get_dimensions(thumbnail=False, hires=False):
        """Returns the width and height of the original image as a
        tuple.

        - Raises ``ValueError`` if there is no way of determining the
          dimensions,

        - Return (0, 0) if there is no image,
        """

    def get_format():
        """Return the orignal image format: ``PNG``, ``JPEG``, ``BMP`` ...
        """

    def get_web_format():
        """Return the web version image format: ``PNG`` or ``JPEG`` or
        ``GIF``.
        """

    def get_web_scale():
        """Return the scaling information used for the web version of
        the image.
        """

    def get_image(hires=True, webformat=False):
        """Return image raw data. If ``hires`` is set to True, the
        original image data is returned. If ``webformat`` is set to
        True, the web version image raw data is returned.
        """


###############################################################
### Ghost
###############################################################


class IGhostAware(interface.Interface):
    """This mark any ghost content
    """

    def get_haunted():
        """Return the final target object.
        """


class IGhostManagable(IGhostAware):
    """Interface for ghosts (and ghost folders).
    """

    def set_haunted(content):
        """Set content to be haunted.
        """

    def get_link_status():
        """Report a marker indicating the status of the ghost: broken,
        link not set, to a folder ...
        """


class IGhostVersion(IGhostManagable, IVersion):
    """Version of a ghost
    """


class IGhost(IGhostAware, IVersionedContent):
    """Ghost content
    """


class IGhostFolder(IGhostManagable, IContainer):
    """Ghost Folder
    """


class IGhostAsset(IGhostManagable, IAsset, IDirectlyRendered):
    """Ghost Asset
    """


class ISilvaNameChooser(INameChooser):
    """Choose and check name for Silva content
    """

    def checkName(identifier, content, file=None, interface=None):
        """Verify the identifier is valid. Raise ContentError if it is
        not.
        """

    def chooseName(identifier, content, file=None, interface=None):
        """Choose an identifier form name and content (both can be none).
        """
