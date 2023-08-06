'''
Created on Dec 1, 2013

'''
import unittest
from mapp.core.parsers import SettingsParser, BasicParser

class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def test_settingsparser(self):
        parser = SettingsParser("../settings.ini")
        self._assert_value_exists(parser, BasicParser.BLAST_PROGRAM)
        self._assert_value_exists(parser, BasicParser.TREE_PROGRAM)
        self._assert_value_exists(parser, BasicParser.BEFORETREE_PROGRAM)
        self._assert_value_exists(parser, BasicParser.MSA_PROGRAM)
        self._assert_value_exists(parser, BasicParser.BEFOREMSA_PROGRAM)
        self._assert_value_exists(parser, BasicParser.MAPP_PROGRAM)
        self._assert_value_exists(parser, BasicParser.BEFOREMAPP_PROGRAM)
        
        Test.assertRaises(self, KeyError, self._assert_value_exists, parser, "blahblah")
        
        
    def _assert_value_exists(self, parser, name):
        value = parser.get_val(name)
        Test.assert_(self, isinstance(value,basestring),  "Variable name " + name + " is is there no string!")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_settingsparser_interface']
    unittest.main()