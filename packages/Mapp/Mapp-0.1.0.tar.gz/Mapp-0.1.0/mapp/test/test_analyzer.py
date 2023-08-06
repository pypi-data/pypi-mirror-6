'''
Created on Nov 28, 2013
'''
import unittest
from mapp.core.analyzers import Analyzer
from mapp.core.parsers import BasicParser
from mapp.utils.common import exec_command
from mapp.utils.common import MappError


class TestAnalyzer(unittest.TestCase):

    class MockParser(BasicParser):
        def __init__(self):
            BasicParser.__init__(self)
        
        def populate_parser(self):
            d = { BasicParser.BLAST_PROGRAM         : "touch blast",
                  BasicParser.BEFOREMSA_PROGRAM     : "touch beforemsa",
                  BasicParser.MSA_PROGRAM           : "touch msa",
                  BasicParser.BEFORETREE_PROGRAM    : "touch beforetree",
                  BasicParser.TREE_PROGRAM          : "touch tree",
                  BasicParser.BEFOREMAPP_PROGRAM    : "touch beforemapp",
                  BasicParser.MAPP_PROGRAM          : "touch mapp",
                  BasicParser.MAPP_OUTFILE          : "mapp"
                }
                  
                  
                            
            return d

    def setUp(self):
        self.analyzer = Analyzer(TestAnalyzer.MockParser())


    def tearDown(self):    
        pass

    def test_analyzer_interface(self):
        analyzer = self.analyzer
        analyzer.exec_blast()
        analyzer.exec_beforemsa()
        analyzer.exec_msa()
        analyzer.exec_beforertree()
        analyzer.exec_tree()
        exec_command("rm blast beforemsa msa beforetree tree", "Clear command")
        analyzer.exec_mapp(True, True, True)
        exec_command("rm blast beforemsa msa beforetree tree beforemapp mapp", "Clear command")
    
    def test_analyzer_onlymapp(self):
        TestAnalyzer.assertRaises(self, MappError, exec_command, "rm blast", "Clear command")
        TestAnalyzer.assertRaises(self, MappError, exec_command, "rm tree", "Clear command")
        TestAnalyzer.assertRaises(self, MappError, exec_command, "rm msa", "Clear command")
        TestAnalyzer.assertRaises(self, MappError, exec_command, "rm beforetree", "Clear command")
        TestAnalyzer.assertRaises(self, MappError, exec_command, "rm beforemsa", "Clear command")
        TestAnalyzer.assertRaises(self, MappError, exec_command, "rm beforemapp", "Clear command")
        TestAnalyzer.assertRaises(self, MappError, exec_command, "rm mapp", "Clear command")
        self.analyzer.exec_mapp(False, False, False)
        TestAnalyzer.assertRaises(self, MappError, exec_command, "rm blast", "Clear command")
        TestAnalyzer.assertRaises(self, MappError, exec_command, "rm tree", "Clear command")
        TestAnalyzer.assertRaises(self, MappError, exec_command, "rm msa", "Clear command")
        TestAnalyzer.assertRaises(self, MappError, exec_command, "rm beforetree", "Clear command")
        TestAnalyzer.assertRaises(self, MappError, exec_command, "rm beforemsa", "Clear command")
        exec_command("rm beforemapp mapp", "Clear command")
            
        
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()