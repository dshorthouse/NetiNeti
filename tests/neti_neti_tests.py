import unittest
import cPickle

from src.netineti import NetiNetiTrain, NameFinder

# this is testing the old one
class TestNameFinder(unittest.TestCase):
    def setUp(self):
        self.nf = NameFinder(cPickle.load(open('src/netinetitrain.pkl')))

    def test_createIndex(self):
        token = ["squid", "whale", "hilarious"]
        self.assertEqual(self.nf._createIndex(token), {0:0, 1:6, 2:12})

    def test_endingCheck(self):
        self.assertTrue(check_end("homobacideomycota"))
        self.assertFalse(check_end("cheescake"))
     
from src.utilities import create_index, check_end

class TestUtilities(unittest.TestCase):

    def test_create_index(self):
        token = ["squid", "whale", "hilarious"]
        self.assertEqual(create_index(token), {0: 0, 1: 6, 2: 12})

    def test_check_end(self):
        self.assertTrue(check_end("homobacideomycota"))
        self.assertFalse(check_end("cheescake"))
