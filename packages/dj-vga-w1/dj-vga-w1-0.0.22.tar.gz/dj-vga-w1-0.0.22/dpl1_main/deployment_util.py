"""This file contains developments useful for deployment
"""
import os
import sys


def correct_sys_path(relative_dir=os.pardir):
    """Adds to sys.path the directory given directory (relative to the current)

    :param relative_dir: the relative folder address
    """
    try:
        sys.path.remove(os.getcwd())
    except ValueError:
        pass
    sys.path.append(os.path.abspath(os.path.join(os.getcwd(), relative_dir)))
    sys.path = list(set(sys.path))