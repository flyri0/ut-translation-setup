import sys


def is_nuitka():
    return getattr(sys.modules.get(__name__), "__compiled__", False)
