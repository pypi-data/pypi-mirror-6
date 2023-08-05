# Copyright (c) 2002-2011 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from bisect import insort_right
import os.path
import pkg_resources
import types

from zope.configuration.name import resolve
from zope.interface import implements
from zope.testing import cleanup

import Products

from silva.core.conf.registry import Registry
from silva.core import interfaces


class Addable(object):

    def __init__(self, meta_type, priority=0.0):
        self.meta_type = meta_type
        self.priority = priority

    def __cmp__(self, other):
        sort = cmp(self.priority, other.priority)
        if sort == 0:
            sort = cmp(self.meta_type['name'], other.meta_type['name'])
        return sort


class BaseExtension(object):
    """Base for extensions.
    """

    def __init__(self, name, install, path,
                 description=None, depends=(u'Silva',)):
        self._name = name
        self._description = description
        self._install = install
        self._module_name = path

        if depends and not (isinstance(depends, types.ListType) or
                            isinstance(depends, types.TupleType)):
            depends = (depends,)

        self._depends = depends

    @property
    def name(self):
        return self._name

    @property
    def product(self):
        return self._product

    @property
    def module_name(self):
        return self._module_name

    @property
    def module_directory(self):
        return os.path.dirname(self.module.__file__)

    @property
    def module(self):
        return resolve(self.module_name)

    @property
    def version(self):
        return self._version

    @property
    def description(self):
        return self._description

    @property
    def installer(self):
        return self._install

    @property
    def depends(self):
        return self._depends

    def get_content(self):
        # XXX Maybe rename that to get_content_types.
        result = []
        my_name = self.name
        for content in Products.meta_types:
            if content['product'] == my_name:
                result.append(content)
        return result


class ProductExtension(BaseExtension):
    """Extension based on a Zope product.
    """
    implements(interfaces.IExtension)

    def __init__(self, name, install, path,
                 description=None, depends=(u'Silva',)):
        super(ProductExtension, self).__init__(name, install, path,
                                               description, depends)
        assert path.startswith('Products.')
        self._product = path.split('.')[1]
        self._version = open(os.path.join(
                self.module_directory, 'version.txt')).read()

    @property
    def module_name(self):
        return 'Products.%s' % self._product


class EggExtension(BaseExtension):
    """Extension package as an egg.
    """
    implements(interfaces.IExtension)

    def __init__(self, egg, name, install, path,
                 description=None, depends=(u'Silva',)):
        super(EggExtension, self).__init__(
            name, install, path, description, depends)
        # We assume that the name of this egg is the name of the
        # python extension.
        if path.startswith('Products.'):
            self._product = path.split('.', 1)[1]
        else:
            self._product = path
        self._module_name = path
        self._version = egg.version

    @property
    def module_name(self):
        return self._module_name


class ExtensionRegistry(Registry):

    implements(interfaces.IExtensionRegistry)

    def __init__(self):
        self.clear_registry()

    # MANIPULATORS

    def clear_registry(self):
        """Clear the registry. *Don't call this in regular order of operation*.
        """
        self._extensions_order = []
        self._extensions = {}
        self._extensions_by_module = {}
        self._silva_addables = []

    def register(self, name, description, context, modules,
                 install_module=None, module_path=None,
                 depends_on=(u'Silva',)):
        # Figure out which is the extension path.
        path = None
        assert not ((install_module is None) and (module_path is None))
        if module_path:
            path = resolve(module_path).__file__
        elif isinstance(install_module, types.ModuleType):
            # Installer is a module install.py which HAVE TO BE in the
            # extension package.
            module_path = '.'.join(install_module.__name__.split('.')[:-1])
            path = install_module.__file__
        else:
            # Installer is a class in the __init__.py of the extension.
            module_path = install_module.__module__
            path = resolve(module_path).__file__

        # Search throught eggs to see if extension is an egg.
        ext = None
        for egg in pkg_resources.working_set:
            if (path.startswith(egg.location) and
                path[len(egg.location)] == os.path.sep):
                ext = EggExtension(
                    egg, name, install_module, module_path,
                    description, depends_on)
                break

        # Otherwise, that's a product.
        if ext is None:
            ext = ProductExtension(
                name, install_module, module_path,
                description, depends_on)

        self._extensions[ext.name] = ext
        self._extensions_by_module[ext.module_name] = ext

        # Try to order based on dependencies
        self._orderExtensions()

        for module in modules:
            self.registerClass(context, module)

    def addAddable(self, meta_type, priority):
        """Allow adding an addable to silva without using the
        registerClass shortcut method.
        """
        meta_types = Products.meta_types
        for mt_dict in meta_types:
            if mt_dict['name'] == meta_type:
                mt_dict['doc'] = mt_dict['instance'].__doc__
                insort_right(self._silva_addables, Addable(mt_dict, priority))

    def _orderExtensions(self):
        """Reorder extensions based on depends_on constraints.
        """
        # make mapping from name depended on to names that depend on it
        depends_on_mapping = {}
        for value in self._extensions.values():
            if not value.depends:
                depends_on_mapping.setdefault(None, []).append(value.name)
                continue
            for do in value.depends:
                depends_on_mapping.setdefault(do, []).append(value.name)

        # if depends_on is None, this should be first in the list
        added = depends_on_mapping.get(None, [])

        # now add them to the list and get dependencies in turn
        result = []
        while added:
            new_added = []
            for name in added:
                if name in result:
                    result.remove(name)
                result.append(name)
                new_added.extend(depends_on_mapping.get(name, []))
            added = new_added
        self._extensions_order = result

    def install(self, name, root):
        self._extensions[name].installer.install(root)

    def uninstall(self, name, root):
        self._extensions[name].installer.uninstall(root)

    def refresh(self, name, root):
        if hasattr(self._extensions[name].installer, 'refresh'):
            # installer has a refresh, so use it note: the default
            # refresh (in silva.core.conf.installer.DefaultInstaller)
            # is to just uninstall/install.  Extensions may choose to
            # override this to do a custom uninstall/install which may,
            # e.g. not remove a special service_<extension> object
            # which contains site-specific customizations
            self._extensions[name].installer.refresh(root)
        else:
            self._extensions[name].installer.uninstall(root)
            self._extensions[name].installer.install(root)

    # ACCESSORS

    def get_names(self):
        return self._extensions_order

    def get_extension(self, name):
        return self._extensions.get(name, None)

    def have(self, name):
        return name in self._extensions_order

    def is_installed(self, name, root):
        extension = self.get_extension(name)
        if extension:
            return extension.installer.is_installed(root)
        return False

    def get_name_for_class(self, class_):
        path = class_.__module__
        for module in self._extensions_by_module.keys():
            if (path.startswith(module) and
                (len(path) == len(module) or
                 path[len(module)] == '.')):
                return self._extensions_by_module[module].name
        return None

    def get_addables(self):
        return [addable.meta_type for addable in self._silva_addables]

    def get_addable(self, content_type):
        for addable in self._silva_addables:
            if content_type == addable.meta_type['name']:
                return addable.meta_type
        return {}


extensionRegistry = ExtensionRegistry()

# Cleanup registry on test tearDown
cleanup.addCleanUp(extensionRegistry.clear_registry)
