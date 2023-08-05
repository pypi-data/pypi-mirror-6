# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$


from zope import interface


class IContentImporter(interface.Interface):
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

    def importFromZip(input_archive, replace=False):
        """Import Silva content from a full media opened zip
        file. Optionaly replace content.
        """


IZipfileImporter = IZipFileImporter


class IContentExporter(interface.Interface):
    """Adapter for export context content in a file.
    """

    name = interface.Attribute("Name of the registered exporter")
    extension = interface.Attribute("Filename extension for this exporter")

    def export(settings):
        """Export context with given settings.
        """


class IDefaultContentExporter(IContentExporter):
    """This mark the default content exporter.
    """


class IAssetData(interface.Interface):
    def getData():
        """ Get actual data stored for this asset as calling index_html()
        for assets can have all kinds of unwanted side effects.
        """


class IVersionManagement(interface.Interface):
    def getVersionById(id):
        """get a version by id"""

    def getPublishedVersion():
        """return the current published version, None if it doesn't exist"""

    def getUnapprovedVersion():
        """return the current unapproved (editable) version, None if
        it doesn't exist"""

    def getApprovedVersion():
        """return the current approved version, None if it doesn't exist"""

    def revertPreviousToEditable(id):
        """revert a previous version to be editable version

        The current editable will become the last closed (last closed
        will move to closed list). If the published version will not
        be changed.

        Raises AttributeError when version id is not available.

        Raises VersioningError when 'editable' version is approved or
        in pending for approval.
        """

    def getVersionIds():
        """return a list of all version ids
        """

    def getVersions(sort_attribute='id'):
        """return a list of version objects

        If sort_attribute resolves to False, no sorting is done, by
        default it sorts on id converted to int (so [0,1,2,3,...]
        instead of [0,1,10,2,3,...] if values < 20).
        """

    def deleteVersion(id):
        """Delete a version

        Can raise AttributeError when the version doesn't exist,
        VersioningError if the version is approved(XXX?) or published.
        """

    def deleteOldVersions(number_to_keep):
        """Delete all but <number_to_keep> last closed versions.

        Can be called only by managers, and should be used with great care,
        since it can potentially remove interesting versions
        """


class IIndexable(interface.Interface):

    def getTitle():
        """Returns the title of the indexable.
        """

    def getPath():
        """Returns the path of the indexable.
        """

    def getIndexes():
        """Returns the indexes for a certain object, or an empty list.
        """


class ILanguageProvider(interface.Interface):

    def getAvailableLanguages():
        """Return the available languages.
        """

    def setPreferredLanguage(language):
        """Sets the preferred language.
        """

    def getPreferredLanguage():
        """Gets the preferred language.
        """

class IPath(interface.Interface):

    def pathToUrl(path):
        """Convert a physical path to a URL.
        """

    def urlToPath(url):
        """Convert a HTTP URL to a physical path.
        """


class IFeedEntryProvider(interface.Interface):
    """Adapter to a object which provides a list feed entry that can
    used to build a RSS/Atom feed.
    """

    def entries():
        """Generate IFeedEntry objects.
        """


class IFeedEntry(interface.Interface):
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


class IVirtualHosting(interface.Interface):
    """Access to virtual hosting information.
    """

    def getVirtualRootPhysicalPath():
        """ Get the physical path of the object being the virtual host
        root.

        If there is no virtual hosting, return None
        """

    def getVirtualHostKey():
        """ Get a key for the virtual host root.

        If there is no virtual hosting, return None.
        """

    def getVirtualRoot():
        """ Get the virtual host root object.
        """

    def getSilvaOrVirtualRoot():
        """ Get either the virtual host root object, or the silva root.
        """

    def containsVirtualRoot():
        """ Return true if object contains the current virtual host root.
        """


class ISiteManager(interface.Interface):
    """Site Manager adapter.
    """

    def makeSite():
        """Make the context become a local site.
        """

    def deleteSite():
        """Release the context of being a local site.
        """

    def isSite():
        """Return true if the context is a local site.
        """


class IHaunted(interface.Interface):
    """Interface for haunted adapter
    """

    def getHaunting():
        """Return iterator of objects (ghosts) haunting the adapted object.
        """
