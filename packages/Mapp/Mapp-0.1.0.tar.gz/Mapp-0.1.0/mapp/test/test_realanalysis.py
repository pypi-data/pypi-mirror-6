'''
Created on Dec 6, 2013
'''
import unittest
from mapp.core.analyzers import Analyzer
from mapp.core.parsers import SettingsParser
from mapp.utils.common import exec_command

SECTION = "commands"
SETTINGS = "../../settings.ini"

class Test(unittest.TestCase):


    def setUp(self):
        self._parser = SettingsParser(SETTINGS)
        self._analyzer = Analyzer(self._parser)
        self._blastout = self._parser._config.get(SECTION, "blastout")
        self._msain = self._parser._config.get(SECTION, "msain")
        self._msaout = self._parser._config.get(SECTION, "msaout")
        self._treein = self._parser._config.get(SECTION, "treein")
        self._treeout = self._parser._config.get(SECTION, "treeout")
        self._mappinmsa = self._parser._config.get(SECTION, "mappinmsa")
        self._mappintree = self._parser._config.get(SECTION, "mappintree")
        self._mappout = self._parser._config.get(SECTION, "mappout")

    def tearDown(self):
        pass


    def test_blast(self):
        self._analyzer.exec_blast() 
        with open(self._blastout) :
            pass
    
    def test_beforemsa(self):
        self._analyzer.exec_beforemsa()
        with open(self._msain) :
            pass
    
    def test_msa(self):
        self._analyzer.exec_msa()
        with open(self._msaout) :
            pass
        
    def test_beforetree(self):
        self._analyzer.exec_beforertree()
        with open(self._treein) :
            pass


    def test_tree(self):
        self._analyzer.exec_tree()
        with open(self._treeout) :
            pass
        
    def test_beforemapp(self):
        self._analyzer.exec_beforemapp()
        with open(self._mappinmsa) :
            pass
        with open(self._mappintree) :
            pass
    
    def test_mapponly(self):
        self._analyzer.exec_mapp(False, False, False)
        with open(self._mappout) :
            pass
    
    def test_mapp_with_all_programs(self):
        self._analyzer.exec_mapp(True, True, True)
        with open(self._mappout) :
            pass
    
    def clearcommand(self):
        exec_command("rm " + " ".join([self._msain,
                                        self._msaout,
                                        self._treein,
                                        self._treeout,
                                        self._mappinmsa,
                                        self._mappintree,
                                        self._mappout])
                     , "Clear command")
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_blast']
    unittest.main()