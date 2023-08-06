'''
Parsers can somehow - somewhere get paths, program paramaters and sequence information
for analysis builders.
For example of builder see `mapp.core.builders.BlastBuilder`

Created on Dec 1, 2013
'''
from ConfigParser import SafeConfigParser
from abc import ABCMeta, abstractmethod


class BasicParser(object):
    '''
    Abstract class for parsers. Reimplement only `populate_parser` method is 
    probably enough.
    '''

    __metaclass__ = ABCMeta

    '''CONSTANTS as keys for the settings _values dictionary.'''
    BLAST_PROGRAM = "blast"
    TREE_PROGRAM = "tree"   
    MSA_PROGRAM = "msa"
    MAPP_PROGRAM = "mapp"
    BEFOREMSA_PROGRAM = "beforemsa"
    BEFORETREE_PROGRAM = "beforetree"
    BEFOREMAPP_PROGRAM = "beforemapp"
    BLAST_OUTFILE = "blastout"
    BLASTSTAT_OUTFILE = "blaststat"
    MAPP_OUTFILE = "mappout"
    MSA_OUTFILE = "msaout"
    TREE_OUTFILE = "treeout"
    SEQUENCE_FILE = "sequence"
    
    
    def __init__(self):
        '''This constructor have to be called by descendants'''
        self._values = dict()
        self._ispopulated = False
    
    def get_val(self, name):
        '''
        Method for access to parser variables.
        
        :param name: Name of parser variable. As name use one of constant
            defined in `BasicParser` class.
        
        :returns: Value by name
        '''
        self._checkpopulate()
        return self._values[name]
    
    @abstractmethod
    def populate_parser(self):
        '''
        Override this method for specify the way parser obtain the
        values for anlysis.
        
        :returns: Dictionary with settings values. Keys to the dictionary are defined
        in `BasicParser` as constants.
        '''
        pass
    
    def _checkpopulate(self):
        if not self._ispopulated:
            self._values = self.populate_parser()
            self._ispopulated = True



class ValuesParser(BasicParser):    
    '''
    Impelemtns parser that can read correct dict variable.
    '''
    def __init__(self, settings):
        '''
        :param settings: dictionary with settings
            All of BasicParser constants have to be defined as keys.
        '''
        BasicParser.__init__(self)
        self._settings = settings
    
    def populate_parser(self):
        return self._settings
    
  
  
class SettingsParser(BasicParser):
    '''
    Impelemtns parser that can read ini file.
    '''
    
    SECTION = "commands"
    
    #format of mapping {<section name> : {<variable name in settings file> : <name in BasicParser>}}
    MAPPING = {SECTION : { "blast"       : BasicParser.BLAST_PROGRAM,
                              "tree"        : BasicParser.TREE_PROGRAM,
                              "beforetree"   : BasicParser.BEFORETREE_PROGRAM,
                              "msa"         : BasicParser.MSA_PROGRAM,
                              "beforemsa"    : BasicParser.BEFOREMSA_PROGRAM,
                              "mapp"        : BasicParser.MAPP_PROGRAM,
                              "beforemapp"   : BasicParser.BEFOREMAPP_PROGRAM,
                              "blastout"    : BasicParser.BLAST_OUTFILE,
                              "blaststat"   : BasicParser.BLASTSTAT_OUTFILE,
                              "mappout"  : BasicParser.MAPP_OUTFILE,
                              "msaout"      : BasicParser.MSA_OUTFILE,
                              "treeout"      : BasicParser.TREE_OUTFILE,
                              "sequence"    : BasicParser.SEQUENCE_FILE
                              }
               }
    
    def __init__(self, settingsfile):
        '''
        :param settingsfile: path to the settings file
        '''
        BasicParser.__init__(self)
        self._settingsfile = settingsfile
        self._config = SafeConfigParser()
        self._config.read(self._settingsfile)
        self._checkpopulate()
    

    def populate_parser(self):  
        values = dict()
        mapping = SettingsParser.MAPPING
        for section in mapping.iterkeys():
            sectiondict = mapping[section]
            for valuename in sectiondict.iterkeys():
                values[sectiondict[valuename]] = \
                    self._config.get(section, valuename)
        return values
        