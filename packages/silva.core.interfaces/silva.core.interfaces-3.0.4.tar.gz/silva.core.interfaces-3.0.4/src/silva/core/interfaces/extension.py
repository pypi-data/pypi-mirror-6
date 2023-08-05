# -*- coding: utf-8 -*-
# Copyright (c) 2002-2013 Infrae. All rights reserved.
# See also LICENSE.txt

from zope.interface import Interface, Attribute
from silva.core.interfaces.registry import IRegistry


class IExtension(Interface):
    """An extension to Silva.
    """

    name = Attribute("Name")
    version = Attribute("Version")
    title = Attribute(u"Title")
    description = Attribute("Description")
    product = Attribute("Product name")
    installer = Attribute("Installer module")
    depends = Attribute("Dependancy to other modules")
    module = Attribute("Python package implementing")
    module_name = Attribute("Name of the python package")
    module_directory = Attribute(
        "Physical directory where the module is located")

    def get_content():
        """Return ALL content class availables for this extension.
        """


class ISystemExtension(IExtension):
    """A system extension can't be un-installed and is used by the
    system.
    """


class IExtensionInstaller(Interface):
    """A Silva extension installer.
    """

    def install(root, extension):
        """Install the extension in root.
        """

    def uninstall(root, extension):
        """Uninstall the extension in root.
        """

    def refresh(root, extension):
        """Refresh the extension in root.
        """

    def is_installed(root, extension):
        """Return true if the extension is installed in root.
        """


class IExtensionRegistry(IRegistry):
    """Silva extension registry.
    """

    # MANIPULATORS

    def register(
        name, title,
        install_module=None, module_path=None, depends_on=(u'Silva',)):
        """Register a new extension.
        """

    def add_addable(meta_type, priority, content_type):
        """Declare a new addable. Meta type is main content class,
        content_type is the one holding the data. (which is different
        of the first one in case of versioned content).
        """

    def install(name, root):
        """Install this extension to the given Silva root.
        """

    def uninstall(name, root):
        """Uninstall this extension from the given Silva root.
        """

    # ACCESSORS

    def is_installed(name, root):
        """Tells you if the given product is installed in this root.
        """

    def get_names():
        """Return available extensions names.
        """

    def get_extension(name):
        """Return the given extension.
        """

    def get_name_for_class(cls):
        """Return the extension name to which belongs this class.
        """

    def get_addables():
        """Return all addables content information.
        """

    def get_addable(content_type):
        """Return a specific addable content information.
        """
