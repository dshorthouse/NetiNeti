# -*- coding: utf-8 -*-
import unittest

from src.netineti import TextClean

class TestTextClean(unittest.TestCase):
    def setUp(self):
        self.tc = TextClean()
    
    def test_left_strip_nothing(self):
        self.assertEqual(self.tc.leftStrip(""), ("", 0))

    def test_right_strip_nothing_weird(self):
        self.assertEqual(self.tc.rightStrip("nothing"), ("nothing", 0))

    def test_left_strip_spaces(self):
        self.assertEqual(self.tc.leftStrip("one two three"), ("one two three", 0))

    def test_left_strip_numbers(self):
        self.assertEqual(self.tc.leftStrip("1234abcd"), ("abcd", 4))

    def test_left_strip_whitespace(self):
        self.assertEqual(self.tc.leftStrip("  whitespace"), ("whitespace", 2))

# unittest.skip(reason) is available in python 3.1
#    @unittest.skip("Not sure what the expected behavior is.")
#    def test_left_strip_unicode(self):
#        self.assertEqual(self.tc.leftStrip("¢™£unicode"), ("unicode", 3))

    def test_left_strip_other_chars(self):
        self.assertEqual(self.tc.leftStrip("@#$%^&*some characters"), ("some characters", 7))

    def test_right_strip_nothing(self):
        self.assertEqual(self.tc.rightStrip(""), ("", 0))

    def test_right_strip_nothing_weird(self):
        self.assertEqual(self.tc.rightStrip("woop"), ("woop", 0))

    def test_right_strip_spaces(self):
        self.assertEqual(self.tc.rightStrip("harpsichord and banjo"), ("harpsichord and banjo", 0))
    
    def test_right_strip_numbers(self):
        self.assertEqual(self.tc.rightStrip("abcd12345"),("abcd", -5))

    def test_right_strip_whitespace(self):
        self.assertEqual(self.tc.rightStrip("whitespace     "), ("whitespace", -5))

#    @unittest.skip("Not sure what the expected behavior is.")
#    def test_right_strip_unicode(self):
#        self.assertEqual(self.tc.rightStrip("unicode¢™£"), ("unicode", -3))

    def test_right_strip_other_chars(self):
        self.assertEqual(self.tc.rightStrip("bacon%$(!)(#"), ("bacon", -7))
        
    def test_striptok_one_word(self):
        self.assertEqual(self.tc.striptok("  banana  "), "banana")
