'''
Created on Jan 8, 2014
'''
import unittest
from mapp.utils.purge_sequences import purge_sequences
from mapp.utils.common import fastalist_from_string, check_fastastring


class Test(unittest.TestCase):


    def setUp(self):
        self.fastafile = """>gi_49176012
ACGTY
>gi_446728587
XY
ZZ
>gi_9879798
ACGTY
"""


    def tearDown(self):
        pass


    def test_purge_sequence(self):
        Test.assertTrue(self, check_fastastring(self.fastafile))
        l1 = fastalist_from_string(self.fastafile)
        Test.assertTrue(self, len(l1)==3)
        
        purified = purge_sequences(self.fastafile)
        Test.assertTrue(self, check_fastastring(purified))
        l2 = fastalist_from_string(purified)
        Test.assertTrue(self, len(l2)==1)
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_purge_sequence']
    unittest.main()