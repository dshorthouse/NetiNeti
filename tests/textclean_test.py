import unittest

from src.netineti import TextClean

class TestTextClean(unittest.TestCase):
    
    def test_left_strip(self):
        tc = TextClean()
        string = "1234abcd"
        result = tc.leftStrip(string)
        self.assertEqual(result, ("abcd", 4))