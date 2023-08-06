'''
Created on Jan 8, 2014
'''
import unittest
from mapp.utils.mutation_correction import correct_mutations


class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def test_correct_mutations(self):
        msa = ">id_123\n--A-B-C--\n"
        muts = [("A", 1, "G"), ("B", 2, "G"), ("C", 3, "G")]
        newmuts = correct_mutations("id_123", muts, msa)
        Test.assertSequenceEqual(self, [("A", 3, "G"), ("B", 5, "G"), ("C", 7, "G")],
                                 newmuts)
        muts = [("B", 1, "G"), ("B", 2, "G"), ("C", 3, "G")]
        newmuts = correct_mutations("id_123", muts, msa)
        Test.assertSequenceEqual(self, [("B", 5, "G"), ("C", 7, "G")],
                                 newmuts)
        
        
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_']
    unittest.main()