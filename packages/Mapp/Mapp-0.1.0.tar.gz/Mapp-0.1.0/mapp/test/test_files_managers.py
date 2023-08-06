'''
Created on Jan 29, 2014
'''
import unittest
from mapp.dataset.files_managers import FilesManager
import os, os.path as path
from mapp.dataset.files import Dataset



class Test(unittest.TestCase):

    testfilesdir = path.join(path.realpath(path.dirname(path.abspath(__file__))), "dataset_testfiles")
    newfilesdir = path.join(testfilesdir, "newfiles")   
    datasetpath = path.join(testfilesdir, "dataset.csv")
    settings = path.join(testfilesdir, "1.conf")
    
    files = ["{0}.afa", "{0}.conf", "{0}.fa", "{0}.seq", "{0}.stats", "{0}.tree", "{0}.mapp"]

    
    def setUp(self):
        self._dataset = Dataset(Test.datasetpath)
        self.manager = FilesManager(self._dataset, Test.settings, Test.newfilesdir)
        os.chdir(Test.newfilesdir)
        self._dataset = Dataset(Test.datasetpath)


    def tearDown(self):
        files = os.listdir(os.getcwd())
        for f in files:
            if path.isfile(f):
                os.remove(f)


    def test_make_mapp_files(self):
        seqid, sequence = self._dataset.seq_range(0, 0)[0]
        self.manager.make_mapp_files(seqid, sequence)
        for f in Test.files:
            Test.assertTrue(self, os.path.isfile(f.format(seqid)))
    
    def test_make_files_range(self):
        mapps = self.manager.make_files_range(0, 1)
        seqid1, sequence1 = self._dataset.seq_range(0, 0)[0]
        seqid2, sequence2 = self._dataset.seq_range(1, 1)[0]
        
        Test.assertEqual(self, mapps[0][0], seqid1)
        Test.assertEqual(self, mapps[0][1].sequence.sequence, sequence1)
        Test.assertEqual(self, mapps[1][0], seqid2)
        Test.assertEqual(self, mapps[1][1].sequence.sequence, sequence2)
      


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_make_mapp_files']
    unittest.main()