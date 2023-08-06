'''
Created on Jan 30, 2014
'''
import unittest, os.path as path
from mapp.dataset.evaluators import Evaluator
import os
from mapp.dataset.files import Dataset


class Test(unittest.TestCase):

    testfilesdir = path.join(path.realpath(path.dirname(path.abspath(__file__))), "dataset_testfiles")
    newfilesdir = path.join(testfilesdir, "newfiles")   
    datasetpath = path.join(testfilesdir, "dataset.csv")
    settings = path.join(testfilesdir, "1.conf")

    files = ["{0}.afa", "{0}.conf", "{0}.fa", "{0}.seq",
             "{0}.stats", "{0}.tree", "{0}.mapp", "{0}.result"]
    
    def setUp(self):
        os.chdir(Test.newfilesdir)
        self._dataset = Dataset(Test.datasetpath)

    def tearDown(self):
        os.chdir(Test.newfilesdir)
        files = os.listdir(os.getcwd())
        for f in files:
            if path.isfile(f):
                os.remove(f)


    def test_make_results_range(self):
        seqid = self._dataset.seq_range(0, 0)[0][0]
        evaluator = Evaluator(Test.datasetpath,
                              Test.settings,
                              Test.newfilesdir)
        evaluator.make_results_range(0, 0)
        for f in Test.files:
            Test.assertTrue(self, os.path.isfile(f.format(seqid)))
    
    def test_make_results_stepwise(self):
        seqid = self._dataset.seq_range(0, 0)[0][0]
        evaluator = Evaluator(Test.datasetpath,
                              Test.settings,
                              Test.newfilesdir)
        evaluator.make_results_stepwise(0, 1)
        for f in Test.files:
            Test.assertTrue(self, os.path.isfile(f.format(seqid)))
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_init']
    unittest.main()