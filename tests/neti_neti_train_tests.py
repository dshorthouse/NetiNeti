# -*- coding: utf-8 -*-
import unittest
import cPickle

from src.netineti import NetiNetiTrain

# this is testing the old one
class TestNetiNetiTrain(unittest.TestCase):
    def setUp(self):
        self.train = cPickle.load(open('src/netinetitrain.pkl'))

    # O_o _splitGet adds an extra '' to the end of the array.
    def test_split_get(self):
        self.assertEqual(self.train._splitGet('../tests/testdata.txt'), 
                ['bacon', 'milk', 'cheeseburger', 'fish', 'clam', 'quahog']) 

from src.netinetitrain import get_basic_features, split_get, left_strip, right_strip, strip_token, NetiNetiTrain as NNT

class TestNNT(unittest.TestCase):
    def setUp(self):
        self.train = cPickle.load(open('src/netinetitrain.pkl'))

    def test_split_get(self):
        self.assertEqual(split_get('tests/testdata.txt'),
                ['bacon', 'milk', 'cheeseburger', 'fish', 'clam', 'quahog']) 

    def test_left_strip(self):
        self.assertEqual(left_strip('  crab cakes'), ('crab cakes', 2))
        self.assertEqual(left_strip(''), ('', 0))
        self.assertEqual(left_strip('banana pudding'), ('banana pudding', 0))

    def test_right_strip(self):
        self.assertEqual(right_strip('chocolate  '), ('chocolate', -2))
        self.assertEqual(right_strip(''), ('', 0))
        self.assertEqual(right_strip('bank'), ('bank', 0))

    def test_strip_token(self):
        self.assertEqual(strip_token('1#413boo3;23@)('), 'boo')

    def test_get_taxon_features(self):
        self.assertEqual(get_basic_features("bacon lettuce tomato"), {
            "word_1_first_char": 'b',
            "word_1_second_char": 'a',
            "word_1_last_char": 'n',
            "word_1_second_to_last_char": 'o',
            "word_1_last_three_chars": 'con',
            "word_1_last_two_chars": 'on',
            "word_2_first_char": 'l',
            "word_2_second_char": 'e',
            "word_2_last_char": 'e',
            "word_2_second_to_last_char": 'c',
            "word_2_last_three_chars": 'uce',
            "word_2_last_two_chars": 'ce',
            "word_3_first_char": 't',
            "word_3_second_char": 'o',
            "word_3_last_char": 'o',
            "word_3_second_to_last_char": 't',
            "word_3_last_three_chars": 'ato',
            "word_3_last_two_chars": 'to',})
