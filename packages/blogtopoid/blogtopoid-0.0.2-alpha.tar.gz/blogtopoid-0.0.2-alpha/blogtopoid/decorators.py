""" decorator functions.
"""
from __future__ import unicode_literals
from __future__ import absolute_import


def singleton(cls):
    """ @singleton decorator, copied from pep-0318.
    """
    instances = {}

    def getinstance(*args, **kwargs):
        """ return existing instance of new
        """
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return getinstance
