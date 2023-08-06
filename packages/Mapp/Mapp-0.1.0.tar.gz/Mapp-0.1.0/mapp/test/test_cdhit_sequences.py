'''
Created on Jan 14, 2014
'''
import unittest
from mapp.utils.cdhit_sequences import parse_clustsorted


class Test(unittest.TestCase):


    def setUp(self):
        self.sortedfile='''
>Cluster 0
0    354aa, >D7AYF6_NOCDD/1-354... at 68%
1    345aa, >C7R506_JONDD/10-354... at 61%
2    353aa, >L8EQD8_STRRM/1-353... at 64%
3    361aa, >A4X329_SALTO/1-361... *
4    346aa, >D1BUG8_XYLCX/8-353... at 60%
5    342aa, >D2BDH4_STRRD/2-343... at 62%
6    334aa, >E6SAU5_INTC7/1-334... at 67%
7    349aa, >F4H2U3_CELFA/6-354... at 61%
8    340aa, >C7MZU6_SACVD/6-345... at 65%
9    350aa, >K6W7N6_9MICO/1-350... at 60%
10    337aa, >C7QDU1_CATAD/2-338... at 62%
11    350aa, >L8EPC4_STRRM/14-363... at 60%
>Cluster 391
0    353aa, >J0L392_RHILT/3-355... *
1    337aa, >B9JPX3_AGRRK/1-337... at 66%
>Cluster 3303
0    332aa, >C7NK71_KYTSD/2-333... *
'''


    def tearDown(self):
        pass


    def test_parse_clustsorted(self):
        names = parse_clustsorted(self.sortedfile)
        Test.assertTrue(self, len(names) == 3, 
                        "Number of names should be 3 but is {0}".format(len(names)))
        
    def test_parse_clustsorted_equals(self):
        names = parse_clustsorted(self.sortedfile)
        true_names = ["A4X329_SALTO/1-361", "J0L392_RHILT/3-355", "C7NK71_KYTSD/2-333"]
        Test.assertSequenceEqual(self, names, true_names)
        
    def test_parse_clustsorted_max(self):
        names = parse_clustsorted(self.sortedfile, 1)
        true_names = ["A4X329_SALTO/1-361"]
        Test.assertSequenceEqual(self, names, true_names)
        
    def test_parse_clustsorted_toomax(self):
        names = parse_clustsorted(self.sortedfile, 1000)
        true_names = ["A4X329_SALTO/1-361", "J0L392_RHILT/3-355", "C7NK71_KYTSD/2-333"]
        Test.assertSequenceEqual(self, names, true_names)
    
    def test_parse_clustsorted_exactly(self):
        names = parse_clustsorted(self.sortedfile, 3)
        true_names = ["A4X329_SALTO/1-361", "J0L392_RHILT/3-355", "C7NK71_KYTSD/2-333"]
        Test.assertSequenceEqual(self, names, true_names)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_']
    unittest.main()