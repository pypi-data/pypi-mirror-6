from __future__ import unicode_literals
from __future__ import absolute_import

import os
import codecs
import hashlib
import unittest

from blogtopoid import blogtopoid


class TestTag(unittest.TestCase):
    def setUp(self):
        self.tag1 = blogtopoid.Tag('tag')
        self.tag2 = blogtopoid.Tag('tag2')

    def test_tag(self):
        colour = hashlib.md5('tag'.encode('utf-8')).hexdigest()[:6]
        self.assertEqual(self.tag1.colour, colour)

        self.assertEqual(self.tag2.colour, 'f32af7')


class TestHashstore(unittest.TestCase):
    def setUp(self):
        self.hashstore = blogtopoid.Hashstore('testfile.json')

    def tearDown(self):
        try:
            os.remove('testfile.json')
        except OSError:  # it's ok if the file is not existant
            pass

    def test_init(self):
        # new hashstore should be empty
        self.assertEqual(self.hashstore.store, {})

        # set something, delete obj, instanciate new hashstore
        self.hashstore.set('testkey', 'blah')
        del self.hashstore
        raised = False
        try:
            self.hashstore
        except AttributeError:
            raised = True
        self.assertTrue(raised)
        self.hashstore = blogtopoid.Hashstore('testfile.json')
        # new hashstore needs to have old key loaded
        self.assertIn('testkey', self.hashstore.store)

    def test_get(self):
        self.assertIsNone(self.hashstore.get('not existant'))

    def test_set(self):
        self.assertFalse(os.path.isfile('testfile.json'))
        self.hashstore.set('testkey', 'hashvalue')
        self.assertTrue(os.path.isfile('testfile.json'))
        self.assertEqual(self.hashstore.get('testkey'), 'hashvalue')

    def test_hashfile(self):
        with codecs.open('hashme.txt', 'w', 'utf-8') as afile:
            afile.write('abc123def456')

        self.assertEqual(
            'e861b2eab679927cfa36fe256e9deb1969b0468ad0744d61064f9d188333aec6',
            self.hashstore.hashfile('hashme.txt')
        )
        os.remove('hashme.txt')


class TestStaticMethods(unittest.TestCase):
    def test_write_file(self):
        blogtopoid.write_file('testfilename.txt', '1234')

        with codecs.open('testfilename.txt', 'r', 'utf8') as afile:
            contents = afile.read()
            self.assertEqual('1234', contents)

        os.remove('testfilename.txt')
