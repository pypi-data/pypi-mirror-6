# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$


from zope import interface
from zope.annotation import IAttributeAnnotatable
from grokcore.component.interfaces import IContext


class ICustomizable(interface.Interface):
    """Customizable content
    """


class IDirectlyRendered(interface.Interface):
    """Content directly rendered without the help of a layout.
    """


class ISecurity(interface.Interface):
    """Content object with author and creator information.
    """

    def sec_get_last_author_info():
        """Return the member object corresponding to the last author
        who modified this content object.
        """

    def sec_get_creator_info():
        """Return the member object corresponding to the creator of
        this content object.
        """


class ITitledObject(interface.Interface):
    """Content objects with a title.
    """

    def get_title():
        """The title of the content object.
        """

    def get_title_or_id():
        """The title or id of the content object.
        """

    def set_title(title):
        """Change the title of the content object.
        """


class ISilvaObject(IContext, IAttributeAnnotatable, ISecurity, ITitledObject, ICustomizable):
    """All Silva content object.
    """

    def get_creation_datetime():
        """Return of creation datetime of the object. Return None if
        not supported.
        """

    def get_modification_datetime():
        """Return the last modification datetime of the object. Return None if not
        supported.
        """

    def get_editable():
        """Get the editable version (may be object itself if no versioning).
        Returns None if there is no such version.
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

    def preview():
        """Render this object using the public view defined in the
        view registry.

        This should use methods on the object itself and the version object
        obtained by ``get_previewable()`` to render the object to HTML.
        """

    def view():
        """Render this object using the public view defined in the
        view registry.

        This should use methods on the object itself and the version object
        obtained by get_viewable() to render the object to HTML.
        """

    def is_deletable():
        """Returns True if object is deletable right now.
        """


class IPublishable(ISilvaObject):
    """Silva Objects that can be published to the public, and appear
    in table of contents.
    """

    # ACCESSORS
    def is_published():
        """Return true if this object is visible to the public.
        """

    def is_approved():
        """Return true if this object is versioned or contains
        versioned content that is approved.
        """


###############################################################
### Container
###############################################################

class IContainer(IPublishable):
    """Silva containers.
    """

    used_space = interface.Attribute(u"Used space by assets.")

    # MANIPULATORS
    def move_object_up(id):
        """Move object with ``id`` up in the list of ordered publishables.
        Return true in case of success.
        """

    def move_object_down(id):
        """Move object with ``id`` down in the list of ordered publishables.
        Return true in case of success.
        """

    def move_to(move_ids, index):
        """Move ``ids`` just before index.
        Return true in case success.
        """

    def action_rename(orig_id, new_id):
        """Rename subobject with orig_id into new_id.
        Cannot rename approved or published content.
        """

    def action_delete(ids):
        """Delete ids in this container.
        Cannot delete approved or published content.
        """

    def action_cut(ids, REQUEST):
        """Cut ``ids`` in this folder, putting them on clipboard in
        ``REQUEST``.  Cannot cut approved or published content.
        """

    def action_copy(ids, REQUEST):
        """Copy ``ids`` in this folder, putting them on clipboard in
        ``REQUEST``.
        """

    def action_paste(REQUEST):
        """Paste clipboard to this folder.  After paste, approved or
        published content is automatically unapproved and/or closed.
        """

    def update_quota(delta):
        """Update used space with ``delta``, and verify quota for this folder.
        """

    # ACCESSORS
    def get_silva_addables():
        """Get a list of meta_type dictionnaries (from
        ``filtered_meta_types()``) that are addable to this container.
        """

    def get_silva_addables_all():
        """Get a list of meta_types of all addables that exist in
        Silva.
        """

    def get_silva_addables_allowed():
        """Gives a list of all meta_types that are explicitly allowed here.
        """

    def get_container():
        """Get the nearest container in the acquisition hierarchy.
        (this one)
        """

    def is_transparent():
        """Show this subtree in ``get_tree()``.
        """

    def is_delete_allowed(id):
        """Return true if subobject with name 'id' can be deleted.
        This is only allowed if the subobject is not published or
        approved.
        """

    def get_default():
        """Get the default content object of the folder. If
        no default is available, return None.
        """

    def get_ordered_publishables():
        """Get list of active publishables of this folder, in
        order.
        """

    def get_assets():
        """Get a list of assets objects in this folder.  (not in any
        fixed order).
        """

    def get_non_publishables():
        """Get a list of non-publishable objects in this folder,
        sorted in alphabetical order. This includes assets,
        configuration objects and anything else that is not a
        publishable.
        """

    def get_tree():
        """Get flattened tree of all active publishables.
        This is a list of indent, object tuples.
        """

    def get_container_tree():
        """Get flattened tree of all sub-containers.
        This is a list of indent, object tuples.
        """

    def get_public_tree():
        """Get tree of all publishables that are public.
        and not hidden from tocs
        """

    def get_public_tree_all():
        """Get tree of all publishables that are public,
        and not hidden from tocs
        including the publishables in subpublications.
        """

    def get_status_tree():
        """Get tree of all active content objects. For containers,
        show the default object if available.
        """


class IFolder(IContainer):
    """Silva Folder
    """

    def set_silva_addables_allowed_in_container(addables):
        """Set the list of addables explicitly allowed in this
        container.  If 'addables' is set to None the list is acquired
        from the container higher in the hierarchy. If this is the
        root, return the complete list.
        """

    def get_silva_addables_allowed_in_container():
        """Get a list of all addables explicitly allowed in this
        container (and its subcontainers).
        """

    def is_silva_addables_acquired():
        """Return true if the list of addables is acquired from above
        (set_silva_addables_allowed_in_container set to None), false
        if not.
        """


class IPublication(IContainer):
    """Silva Publication
    """


class IRoot(IPublication):
    """Silva Root
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
        """Used by acquisition to get the nearest containing content object.
        """

    def is_cacheable():
        """Return true if the public view of this object can be safely
        cached.  This means the public view should not contain any
        dynamically generated content.
        """

    def is_default():
        """True if this content object is the default content object of
        the folder.
        """


class IAutoTOC(IContent):
    """Auto TOC content
    """


class IIndexer(IContent):
    """Indexer content
    """

    def getIndexNames():
        """Returns a list of all index entry names in the index,
        sorted alphabetically.
        """

    def getIndexEntry(indexTitle):
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
    def create_version(version_id,
                       publication_datetime,
                       expiration_datetime):
        """Add unapproved version.
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

    def is_version_approved():
        """Check whether there exists an approved version.
        """

    def is_version_published():
        """Check whether there exists a published version.
        """

    def is_version_approval_requested():
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

    def get_next_version_status():
        """Get the status of the next version.
        Result can be 'not_approved', 'approved', or 'no_next_version'.
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

    def get_public_version_status():
        """Get the status of the published version.  Result can be
        ``published``, ``closed``, or ``no_public_version``.
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

    def get_approval_requester():
        """Return the id of the user requesting approval
        of the currently unapproved version.
        XXX fishy: If the request for approval is withdrawn/rejected,
        this returns the user id of the one having
        withdrawn/rejected the request.
        (Maybe write another method for this?)
        """

    def get_approval_request_message():
        """Get the current message associated with
        request for approval; i.e. argument passed the
        on the last call to "set_approval_request_message".
        May return None if there is no such message or
        the message has been purged by an approval.
        """

    def get_approval_request_datetime():
        """Get the date when the currently unapproved version
        did get a request for approval as a DateTime object,
        or None if there is no such version or request.
        """


class IVersionedContent(IVersioning, IContent):
    """Content that can have versions
    """

    # MANIPULATORS
    def create_copy():
        """Create a new copy of the public version. Automatically
        assign a new id for this copy and register this as the
        next version. If there is already a next version, this
        operation will fail.
        """


class ICatalogedVersionedContent(IVersionedContent):
    """Cataloged versioned content
    """


class IVersion(ITitledObject, IAttributeAnnotatable):
    """Version of a versioned content

    A version effectively store the data of the content.
    """

    def version_status():
        """Returns the current status of this version (unapproved, approved,
        public, last closed or closed).
        """

    def publication_datetime():
        """Returns the version's publication datetime.
        """

    def expiration_datetime():
        """Returns the version's expiration datetime.
        """


class ICatalogedVersion(IVersion):
    """Cataloged version content
    """


class ILinkVersion(ICatalogedVersion):
    """Version of a Silva Link content
    """


class ILink(ICatalogedVersionedContent):
    """Silva Link content

    Silva Link can be used to create links to either other contents in
    Silva or to external URLs.
    """

###############################################################
### Asset
###############################################################


class INonPublishable(ISilvaObject):
    """A content which is not publicly viewable

    A non publisable content never appears in the navigation or in
    table of contents.
    """


class IAsset(INonPublishable):
    """Asset content

    An asset is a resource which is not a content object by itself,
    but contain data. Files and Images are assets for example.
    """

    # MANIPULATORS

    def update_quota():
        """Update used space, and verify quota for this asset.
        """

    def reset_quota():
        """Reset the status of the quota.
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


class IFile(IAsset, IDirectlyRendered):
    """Silva File content to encapsulate "downloadable" data
    """
    # MANIPULATORS

    def set_file_data(file):
        """Re-upload data for this file object. It will change the
        ``content_type``, however id, title, etc. will not change.
        """

    def set_text_file_data(datastr):
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
        """Set file content encoding.
        """

    # ACCESSORS

    def tag(**kw):
        """Generate a tag to download file content.
        """

    def content_type():
        """Return the file content type as it is send to a visitor
        while downloading the file.
        """

    def content_encoding():
        """Return the file content encoding as it is send to a visitor
        while downloading the file.
        """

    def get_text_content():
        """Return the text content of the file or TypesError is it's
        not a text file.
        """

    def get_content():
        """Return the content of the file in any cases.
        """

    def get_content_fd():
        """Return a file descriptor to access the file data.
        """

    def get_download_url():
        """Obtain the public URL the public could use to download this
        file. Typically it's the URL used in ``tag``.
        """


class IZODBFile(IFile):
    """A file in ZODB.
    """

class IFileSystemFile(IFile):
    """A file on the file system.
    """

class IBlobFile(IFile):
    """A file as a blob.
    """

class IImage(IAsset, IDirectlyRendered):
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

    def tag(hires=0, thumbnail=0, **extra_attributes):
        """Generate a image tag to render either the original version
        (if ``hires`` set to True), or the thumbnail (if ``thumbnail``
        set to True) or the web version (by default).

        If some ``extra_attributes`` are given, they will be added to
        the image tag as HTML attributes.
        """

    def get_crop_box(crop=None):
        """Return a tuple describing the current crop box used to
        create the web image. The describe the coordinate of the top
        left and the bottom right corner.
        """

    def get_orientation():
        """Returns the image orientation: ``square``, ``landscape`` or
        ``portrait``.
        """

    def get_dimensions(img=None):
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

    def get_image(hires=1, webformat=0):
        """Return image raw data. If ``hires`` is set to True, the
        original image data is returned. If ``webformat`` is set to
        True, the web version image raw data is returned.
        """


###############################################################
### Ghost
###############################################################


class IGhostAware(interface.Interface):
    """This mark any ghost content.
    """


class IGhostManagable(IGhostAware):
    """Interface for ghosts (and ghost folders).
    """

    def get_haunted():
        """Return the haunted object.
        """

    def set_haunted(content):
        """Set content to be haunted.
        """

    def get_link_status():
        """Report a marker indicating the status of the ghost: broken,
        link not set, to a folder ...
        """


class IGhostVersion(IGhostManagable, ICatalogedVersion):
    """Version of a ghost object.
    """


class IGhost(IGhostAware, ICatalogedVersionedContent):
    """Marker interface for "normal" ghosts, i.e. Silva.Ghost.Ghost.
    """

class IGhostFolder(IGhostManagable, IContainer):
    """Marker interface for Ghost Folders.
    """
