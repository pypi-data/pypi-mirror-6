# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

import zope.deferredimport
from grokcore.component.interfaces import IContext
from silva.core.interfaces.content import IReferable

zope.deferredimport.deprecated(
    'IFilesService moved to silva.core.services.interfaces. '
    'This import will be removed in Silva 3.1',
    IFilesService='silva.core.services.interfaces:IFilesService')


class IZMIObject(IContext, IReferable):
    """A Zope object defined in Zope but that is only accessible via
    the ZMI and not the SMI.
    """


class ISilvaService(IZMIObject):
    """Basic Silva service.
    """


class ISilvaLocalService(ISilvaService):
    """A Silva service which can be added in a local site.
    """


class ISilvaConfigurableService(ISilvaService):
    """A Silva service with configuration screen in SMI.
    """


class ISilvaInvisibleService(ISilvaService):
    """A Silva service that is not visible in the ZMI.

    It is usefull for services that doesn't have any settings and do
    not require any views for forms.
    """

# BBB
IInvisibleService = ISilvaInvisibleService


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

