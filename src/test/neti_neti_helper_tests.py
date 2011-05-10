import unittest
from neti_neti_helper import *

class TestHelperFunctions(unittest.TestCase):

    def test_create_index(self):
        test_tokens = ["hello", "bacon", "chocolate", "banana"]
        index = create_index(test_tokens)
        self.assertEqual(index, {0:0, 1:6, 2:12, 3:22})
