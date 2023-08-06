"""
recursely
"""
__version__ = "0.0.3"
__description__ = "Recursive importer for Python submodules"
__author__ = "Karol Kuczmarski"
__license__ = "Simplified BSD"


import sys

from recursely._compat import IS_PY3
from recursely.importer import RecursiveImporter
from recursely.utils import SentinelList


__all__ = ['install']


def install():
    """Install the recursive import hook in ``sys.meta_path``.

    Because the hook is a catch-all one, we ensure that it's always
    at the very end of ``sys.meta_path``, so that it's tried only if
    no other (more specific) hook has been chosen by Python.
    """
    if RecursiveImporter.is_installed():
        return

    if IS_PY3:
        for i in reversed(range(len(sys.meta_path))):
            ih_module = getattr(sys.meta_path[i], '__module__', '')
            if ih_module != '_frozen_importlib':
                break
        sys.meta_path = SentinelList(
            sys.meta_path[:i],
            sentinels=[RecursiveImporter()] + sys.meta_path[i:])
    else:
        sys.meta_path = SentinelList(sys.meta_path,
                                     sentinel=RecursiveImporter())
