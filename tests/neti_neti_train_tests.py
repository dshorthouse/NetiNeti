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
    
    def test_populateFeatures(self):
        # the original populate features only existed for its side effect.
        array = ["Carrot", "banana", "radish",]
        idx = 0
        start = -1
        stop = "sc"
        features = {}
        name = "last_char_first_word"
        self.assertEqual(self.train._populateFeatures(array, idx, start, stop,
            features, name), "t")

    def test_taxon_features(self):
        token = "pink green orange"
        context_array = ["My", "favorite", "colors", "are", "pink", "green", "orange", "and", "blue"]
        # where the token is in the context
        index = 4
        # number of words in token minus one
        span = 2
        self.assertEqual(self.train.taxon_features(token, context_array, index, span),
        {
            "last3_first": "ink",
            "last3_second": "een",
            "last3_third": "nge",
            "last2_first": "nk",
            "last2_second": "en",
            "last2_third": "ge",
            "first_char": "p",
            "last_char": "k",
            "second_char": "i",
            "sec_last_char": "n",
            # I believe there are lots of errors here.
            "lastltr_of_fw_in_sv": False,
            "lastltr_of_fw_in_svl": False,
            "lastltr_of_sw_in_sv": False,
            "lastltr_of_sw_in_svl": False,
            "lastltr_of_tw_in_sv_or_svl": True,
            "2lastltr_of_tw_in_sv_or_svl": False,
            "2lastltr_of_fw_in_sv": False,
            "2lastltr_of_fw_in_sv1": False,
            "2lastltr_of_fw_in_svlb": False,
            # There is a typo here, it should be "2lastltr_of_sw_in_sv"
            #"2lastltr_of_sw_in_sv": False
            "2lastltr_of_sw_in_sv1": True,
            # There is another typo here, it should be "2lastltr_of_sw_in_svlb"
            #"2lastltr_of_sw_in_svlb": False
            # Lesson here: Don't copy and paste code.
            "first_in_table": False,
            "second_in_table": False,
            "third_in_table": False,
            "1_context": "and",
            "-1_context": "are",
            "1up_2_dot_restok": False,
            "token": "pink green orange",
            "count(a)": 1,
            "has(a)": True,
            "count(e)": 3,
            "has(e)": True,
            "count(i)": 1,
            "has(i)": True,
            "count(o)": 1,
            "has(o)": True,
            "count(u)": 0,
            "has(u)": False,
            "imp_feature": False,
            "Str_Wgt": "F",
        })


from src.utilities import get_basic_features, left_strip, right_strip, split_get, strip_token
from src.netinetitrain import NetiNetiTrain as NNT

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
            "word_3_last_two_chars": 'to',
            "word_1_last_char_in_vowels": False,
            "word_1_last_char_in_sv": False,
            "word_1_last_char_in_sv1": False,
            "word_1_second_to_last_char_in_sv": False,
            "word_1_second_to_last_char_in_sv1": True,
            "word_1_second_to_last_char_in_svlb": False,
            "word_2_last_char_in_sv": False,
            "word_2_last_char_in_sv1": True,
            "word_2_second_to_last_char_in_sv": False,
            "word_2_second_to_last_char_in_sv1": False,
            "word_2_second_to_last_char_in_svlb": False,
            "word_3_last_char_in_vowels": True,
            "word_3_last_char_in_sv_or_sv1": True,
            "word_3_second_to_last_char_in_sv_or_sv1": False,})
