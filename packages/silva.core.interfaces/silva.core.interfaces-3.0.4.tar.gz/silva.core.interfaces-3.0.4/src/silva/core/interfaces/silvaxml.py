# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from zope.interface import Interface


class ISettings(Interface):
    """ settings for import/export context information
    """


class IExportSettings(ISettings):
    """ export settings
    """


class IImportSettings(ISettings):
    """ import settings
    """


class ISilvaXMLProducer(Interface):
    """ export producer
    """


class ISilvaXMLHandler(Interface):
    """ import handler
    """
