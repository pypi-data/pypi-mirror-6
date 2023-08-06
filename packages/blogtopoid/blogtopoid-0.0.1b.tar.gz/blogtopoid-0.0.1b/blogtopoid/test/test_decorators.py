import random
import unittest

from blogtopoid.decorators import singleton


@singleton
class Singleton(object):
    """ dummy singleton class for testing. """
    value = None


class TestSingleton(unittest.TestCase):
    def setUp(self):
        self.singleton = Singleton()
        self.singleton.value = "1234"

    def test_singleton(self):
        new_singleton = Singleton()
        self.assertEqual(self.singleton, new_singleton)
        self.assertEqual(new_singleton.value, '1234')

        value = random.random()
        self.singleton.value = value
        self.assertEqual(new_singleton.value, value)


if __name__ == '__main__':
    unittest.main()
