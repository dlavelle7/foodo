import unittest
import mock
import foodo
from argparse import ArgumentTypeError


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_non_empty_string(self):
        # Assert the Foodo title field accepts (and strips) non empty strings
        self.assertRaises(ArgumentTypeError, foodo.non_empty_string, '')
        self.assertRaises(ArgumentTypeError, foodo.non_empty_string, ' ')
        self.assertRaises(ArgumentTypeError, foodo.non_empty_string, None)
        self.assertRaises(ArgumentTypeError, foodo.non_empty_string, 12)

        self.assertEquals('a', foodo.non_empty_string('  a'))
        self.assertEquals('b', foodo.non_empty_string('b  '))
        self.assertEquals('.', foodo.non_empty_string(' . '))
        self.assertEquals('123', foodo.non_empty_string(' 123 '))
