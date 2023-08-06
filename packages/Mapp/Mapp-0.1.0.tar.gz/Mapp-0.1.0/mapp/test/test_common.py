'''
Created on Jan 8, 2014

'''
import unittest
from mapp.utils.common import fastalist_from_string, check_fastastring,\
    fastastring_from_list


class Test(unittest.TestCase):


    def test_fastalist_from_string(self):
        fastafile = """>gi_49176012
ABC
DEF
>gi_446728587
XY
ZZ"""

        l1 = fastalist_from_string(fastafile)
        Test.assertItemsEqual(self, ("gi_49176012", "ABCDEF"), l1[0])
        Test.assertItemsEqual(self, ("gi_446728587", "XYZZ"), l1[1])
        Test.assert_(self, len(l1)==2)
        
        fastafile += "\n"
        l1 = fastalist_from_string(fastafile)
        Test.assertItemsEqual(self, ("gi_49176012", "ABCDEF"), l1[0])
        Test.assertItemsEqual(self, ("gi_446728587", "XYZZ"), l1[1])
        Test.assert_(self, len(l1)==2)
    
    def test_check_fastastring(self):
        fastastr = """>gi_49176012
ABC
DEF
>gi_446728587
XY
ZZ"""
        Test.assert_(self, check_fastastring(fastastr))
        fastastr = """>gi_49176012
ABC
DEF
>gi_446728587
XY
ZZ
"""
        Test.assert_(self, check_fastastring(fastastr))
        fastastr = """>gi_49176012
ABC
DEF
>gi_446728587
XY
ZZ

"""
        Test.assert_(self, check_fastastring(fastastr))
        fastastr = """gi_49176012
ABC
DEF
>gi_446728587
XY
ZZ
"""
        Test.assertTrue(self, not check_fastastring(fastastr))
        fastastr = """>gi_49176012
ABC
DEF

>gi_446728587
XY
ZZ
"""
        Test.assertTrue(self, not check_fastastring(fastastr))
        fastastr = """>gi_49176012
ABC
DEF
>gi_446728587
XY
ZZ


"""
        Test.assertTrue(self, check_fastastring(fastastr))
        
    
    def test_fastastring_from_list(self): 
        fastalist = [("gi_789456", "ABCABCBAC"), ("gi_97654321", "BBBBBB")]
        fastastr = fastastring_from_list(fastalist)
        Test.assertEqual(self, fastastr, ">gi_789456\nABCABCBAC\n>gi_97654321\nBBBBBB\n")
        

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_fastalist_from_string']
    unittest.main()