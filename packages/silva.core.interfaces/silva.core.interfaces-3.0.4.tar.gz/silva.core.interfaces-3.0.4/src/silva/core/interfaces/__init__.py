# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from zope.interface import Interface


class RequiredParameterNotSetError(Exception):
    pass


class IContainerPolicy(Interface):
    """Policy for container's default documents"""

    def createDefaultDocument(container, title):
        """create default document in given container"""


class IMimeTypeClassifier(Interface):
    """Detect content_type and extension for files.
    """

    def guess_filename(asset, basename):
        """Given an ``IFile`` and a basename, set and return a correct
        filename that would be usage for the file.
        """

    def guess_extension(content_type):
        """Return the most plausible extension to use with a file of
        the given type.
        """

    def guess_type(id=None, filename=None, buffer=None, default=None):
        """Given a file id, or a filename, or a buffer containing some
        data, return the most plausible content_type associated to a
        file. If nothing is found and default is provided, return
        default, otherwise 'application/octet-stream'.
        """

    def guess_buffer_type(buffer):
        """Given a buffer containing some data, return the most
        plausible content_type associated, or None.
        """

    def guess_file_type(filename):
        """Given a filename pointing to a valid file on the disk,
        return the most plausible content_type associated or None.
        """


class IUpgrader(Interface):
    """Upgraders takes an object and modify its attributes in order to
    make it conform to a newer version of Silva.
    """

    def validate(content):
        """Return true if the upgrader apply to the given object.
        """

    def upgrade(content):
        """Upgrades object, and return the upgraded object.

        During upgrade the object identity of the upgraded object may
        change.
        """

class IPostUpgrader(Interface):
    """Post upgraders execute themselves after regular upgraders.
    """


from silva.core.interfaces.content import *
from silva.core.interfaces.extension import *
from silva.core.interfaces.registry import *
from silva.core.interfaces.service import *
from silva.core.interfaces.adapters import *
from silva.core.interfaces.events import *
from silva.core.interfaces.auth import *
from silva.core.interfaces.errors import *
from silva.core.interfaces.silvaxml import *


CLASS_CHANGES = {
    'silva.core.interfaces.service IFilesService':
        'silva.core.services.interfaces IFilesService',
}

