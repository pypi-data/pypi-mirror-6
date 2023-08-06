"""
Base class for import hooks.
"""
from contextlib import contextmanager
import imp
import inspect
import sys

from recursely._compat import IS_PY3


__all__ = ['ImportHook']


class ImportHook(object):
    """Base class for import hooks, including both ``sys.meta_path``
    and ``sys.path_hooks`` ones.

    By default, the hook simulates the standard Python behavior
    when importing a module, and exposes several events which can be
    overridden in subclasses to perform custom logic at different steps.

    Alternativaly, it's possible to completely either the process
    of finding a module to import, or loading the module, or both.
    """
    @classmethod
    def is_installed(cls):
        """Checks whether any instance of this import hook is installed."""
        return any(isinstance(ih, cls) for ih in sys.meta_path)

    @contextmanager
    def import_lock(self):
        """Context manager for establishing a lock on the import facility.
        Uses ``imp.acquire_lock`` and ``imp.release_lock``.
        """
        imp.acquire_lock()
        try:
            yield
        finally:
            imp.release_lock()

    # Overrideable import events

    def on_module_found(self, fullname, path):
        """Event triggered when module has been succesfully found
        and will be loaded using this importer.
        """

    def on_module_already_imported(self, fullname, module):
        """Event triggered when module has been already imported,
        i.e. is present in ``sys.modules``.

        :param module: Existing module object
        :return: ``True`` if importing should proceed regardless.
                 The module will be reloaded in this case.
        """

    def on_module_imported(self, fullname, module):
        """Event triggered when module has been successfully imported.

        :param module: Module object that was imported
        :return: A final (possibly modified) module object
                 or ``None`` if it's not to be changed
        """

    def on_find_module(self, fullname, path):
        """Low-level event that allows to override (almost) whole procedure
        for finding a module of given name within an import path.

        :raise ImportError: If module cannot be found by this importer
        :return: ``True`` if module finding has been overridden
        """

    def on_load_module(self, fullname, path):
        """Low-level event that allows to override (almost) whole procedure
        for loading a module of given name using given import path.

        :return: Module object or ``None``
                 if standard import procedure should be used
        """

    # Main importing logic

    def find_module(self, fullname, path=None):
        """Module finding method.

        By default, we locate the module using a standard method
        that involves ``find_module`` function from ``imp`` package.
        This can be overridden in subclasses by implementing ``on_find_module``
        that returns truthy value.
        """
        try:
            finding_overridden = bool(self.on_find_module(fullname, path))
            if not finding_overridden:
                # although documentation on ``imp`` module says otherwise,
                # without adding ``sys.path`` the hook doesn't really work
                # because it doesn't capture the submodules of the module
                # where it was itself imported to
                find_path = (path or []) + sys.path

                name = fullname
                while '.' in name:
                    head, tail = name.split('.', 1)
                    _, filepath, _ = imp.find_module(head, find_path)

                    find_path = [filepath]
                    name = tail

                imp.find_module(name, path)
                self.on_module_found(fullname, path)
        except ImportError:
            return None  # couldn't find the module, let Python try
                         # the next importer from ``sys.meta_path/path_hooks``

        self._path = path
        return self

    def load_module(self, fullname):
        """Module loading method.

        By default, we use standard importing method that involves
        the ``load_module`` function from ``imp`` package.
        This can be overriden in subclasses by implementing ``on_load_module``
        that returns a module object.
        """
        with self.import_lock():
            module = self.on_load_module(fullname, self._path)
            return module or self._import(fullname)

    def _import(self, fullname):
        """Imports module of given name using the standard Python procedure.

        :return: Module object
        :raise ImportError: When finding or loading the module fails
        """
        existing = self._get_module(fullname)
        if existing is not None:
            reimport = bool(self.on_module_already_imported(fullname, existing))
            if not reimport:
                return existing

        # for dotted names, apply importing procedure recursively
        if '.' in fullname:
            package, module = fullname.rsplit('.', 1)
            pkg_obj = self._import(package)
            path = pkg_obj.__path__
        else:
            module = fullname
            path = self._path

        file_obj, pathname, desc = imp.find_module(module, path)
        try:
            mod_obj = imp.load_module(fullname, file_obj, pathname, desc)
            sys.modules[fullname] = mod_obj

            # do post-processing defined in subclasses, if any
            processed_mod_obj = self.on_module_imported(fullname, mod_obj)
            if processed_mod_obj is not None:
                mod_obj = sys.modules[fullname] = processed_mod_obj
            return mod_obj
        finally:
            if file_obj:
                file_obj.close()

    def _get_module(self, fullname):
        """Retrieve existing module from ``sys.modules``.
        :return: Module object or ``None`` if it's not imported
        """
        try:
            return sys.modules[fullname]
        except KeyError:
            return None

    # Optional PEP302 methods

    def is_package(self, fullname):
        module = self._get_module(fullname) or self._import(fullname)
        return hasattr(module, '__path__')

    def get_code(self, fullname):
        return compile(self.get_source(fullname))

    def get_source(self, fullname):
        module = self._get_module(fullname) or self._import(fullname)
        return inspect.getsource(module)

if IS_PY3:
    from importlib import abc
    for ab in (abc.Finder, abc.Loader, abc.InspectLoader):
        ab.register(ImportHook)
