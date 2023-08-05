# Copyright (c) 2002-2009 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from zope import schema
from zope.interface import Interface
from grokcore.component.interfaces import IContext


class IZMIObject(IContext):
    """An object in ZMI.
    """


class IInvisibleService(Interface):
    """Marker interface for services that want to be not visible in
    the ZMI."""


class ISilvaService(IZMIObject):
    """Basic Silva service.
    """


class ISilvaLocalService(ISilvaService):
    """A Silva service which can be added in a local site.
    """


class IMessageService(ISilvaService, ISilvaLocalService):
    """Send messages to members.
    """

    def send_message(from_memberid, to_memberid, subject, message):
        """Send a message from one member to another.
        """

    def send_pending_messages():
        """Send all pending messages.

        This needs to be called at the end of a request otherwise any
        messages pending may be lost.
        """


class ISidebarService(ISilvaService):

    def render(obj, tab_name):
        """Returns the rendered PT

        Checks whether the PT is already available cached, if so
        renders the tab_name into it and returns it, if not renders
        the full pagetemplate and stores that in the cache
        """

    def invalidate(obj):
        """Invalidate the cache for a specific object
        """


class IFilesService(ISilvaLocalService):
    """Configure File storage.
    """

    storage = schema.Choice(title=u"File Storage",
                            description=u"Method used to store files",
                            required=True,
                            vocabulary="File Storage Type")

    def new_file(id):
        """Allocate a new file with the given ID.
        """

    def is_file_using_correct_storage(content):
        """Return true if the given content is a file and using the
        correct selected storage in the service.
        """
