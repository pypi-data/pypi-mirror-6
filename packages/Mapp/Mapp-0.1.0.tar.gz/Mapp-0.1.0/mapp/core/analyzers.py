'''
Contains analyzer that can make mapp analysis with use parser
that provides settings.

Created on Nov 29, 2013
'''
from mapp.core.parsers import BasicParser as BP, BasicParser
from mapp.utils.common import exec_command
from mapp.core.exceptions import MappError


class Analyzer(object):
    '''
    Analyzer executes commands from parser and then the analysis itself.
    It uses `mapp.core.parsers` to obtain commands for analysis.
    
    It counts with that sequence and all other program output and input
    are files and the command are set in settings corectly.
    '''
    
    def __init__(self, parser):
        '''
        :param parser: parser that can get settings value for program analysis.
            For instance see `mapp.core.parsers.SettinsParser`.  
        '''
        self._parser = parser
   
    def exec_mapp(self, newblast=True, newtree=True, newmsa=True, newmapp=True):
        '''
        Most important method here. Executes mapp command otained from parser.
        If the newblast, newtree or newmsa arguments
        are set then it executes tree or/and msa or/and blast commands otained from parser too.
        
        :param newblast: If True the blast command will be executed. Default is True
        :param newtree: If True the tree and beforetree command will be executed. Default is True
        :param newmsa: If True the msa and beforemsa command will be executed. Default is True
        :param newmapp: If True the mapp and beforemapp command will be executed. Default is True
        ''' 
        if newblast:
            self.exec_blast()
                
        if newmsa:
            if self._parser.get_val(BP.BEFOREMSA_PROGRAM):
                self.exec_beforemsa()
            self.exec_msa()
        
        if newtree:
            if self._parser.get_val(BP.BEFORETREE_PROGRAM):
                self.exec_beforertree()
            self.exec_tree()
        
        if newmapp:
            if self._parser.get_val(BP.BEFOREMAPP_PROGRAM):
                self.exec_beforemapp()
            try: #Try delete old mapp file because mapp don't have --force option
                exec_command("rm -f " + self._parser.get_val(BasicParser.MAPP_OUTFILE),
                             "Delete old MAPP file") 
            except MappError as e:
                print e.header + "\n" + e.description
            exec_command(self._parser.get_val(BP.MAPP_PROGRAM), "MAPP")
        

# These methods can be overrided by offsprings

    def exec_blast(self):
        ''' Executes blast command from parser.'''
        
        exec_command(self._parser.get_val(BP.BLAST_PROGRAM), "Blast")
    
    
    def exec_msa(self):
        '''Executes msa command from parser.'''
        
        exec_command(self._parser.get_val(BP.MSA_PROGRAM), "MSA")
    
    
    def exec_beforemsa(self):
        ''' Executes beforemsa command from parser before msa program run.'''
    
        exec_command(self._parser.get_val(BP.BEFOREMSA_PROGRAM), "Before msa")
    
    
    def exec_tree(self):
        '''Executes tree command from parser.'''
        
        exec_command(self._parser.get_val(BP.TREE_PROGRAM), "Tree")
    
    
    def exec_beforertree(self):
        ''' Executes beforetree command from parser before tree program run.'''
    
        exec_command(self._parser.get_val(BP.BEFORETREE_PROGRAM), "Before tree")
    
    def exec_beforemapp(self):
        ''' Executes beforemapp command from parser before mapp program run.'''
    
        exec_command(self._parser.get_val(BP.BEFOREMAPP_PROGRAM), "Before mapp")
