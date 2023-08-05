from __future__ import unicode_literals
from __future__ import absolute_import

import unittest

from . import test_blogtopoid
from blogtopoid.test import test_decorators


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTests(test_decorators)
    test_suite.addTests(test_blogtopoid)
    return test_suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
