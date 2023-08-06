"""
recursely
"""
__version__ = "0.1"
__description__ = "Recursive importer for Python submodules"
__author__ = "Karol Kuczmarski"
__license__ = "Simplified BSD"


import sys

from recursely._compat import IS_PY3
from recursely.importer import RecursiveImporter
from recursely.utils import SentinelList


__all__ = ['install']


def install(retroactive=True):
    """Install the recursive import hook in ``sys.meta_path``,
    enabling the use of ``__recursive__`` directive.

    :param retroactive: Whether the hook should be retroactively applied
                        to module's that have been imported before
                        it was installed.
    """
    if RecursiveImporter.is_installed():
        return

    importer = RecursiveImporter()

    # because the hook is a catch-all one, we ensure that it's always
    # at the very end of ``sys.meta_path``, so that it's tried only if
    # no other (more specific) hook has been chosen by Python
    if IS_PY3:
        for i in reversed(range(len(sys.meta_path))):
            ih_module = getattr(sys.meta_path[i], '__module__', '')
            is_builtin = ih_module == '_frozen_importlib'
            if not is_builtin:
                break
        sys.meta_path = SentinelList(
            sys.meta_path[:i],
            sentinels=[importer] + sys.meta_path[i:])
    else:
        sys.meta_path = SentinelList(sys.meta_path, sentinel=importer)

    # look through already imported packages and recursively import
    # their submodules, if they contain the ``__recursive__`` directive
    if retroactive:
        for module in list(sys.modules.values()):
            importer.recurse(module)
