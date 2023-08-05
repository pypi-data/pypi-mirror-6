from __future__ import unicode_literals
from __future__ import absolute_import

import hashlib
import unittest

from blogtopoid import blogtopoid


class TestTag(unittest.TestCase):
    def setUp(self):
        self.tag1 = blogtopoid.Tag('tag')
        self.tag2 = blogtopoid.Tag('tag2')

    def test_tag(self):
        colour = hashlib.md5('tag'.encode('utf-8')).hexdigest()[:6]
        self.assertEqual(self.tag1.colour(), colour)

        self.assertEqual(self.tag2.colour(), 'f32af7')
