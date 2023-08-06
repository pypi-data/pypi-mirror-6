'''
This classes can operate with and manage `mapp.dataset.files` classes.
Creates apropriate files from dataset file.
Created on Jan 28, 2014

'''
from mapp.dataset.files import Settings, Sequence, Hmmerstats, Alignment,\
    AnalysisFile, Mapp
from mapp.core.analyzers import Analyzer
from mapp.core.parsers import SettingsParser, BasicParser
import os


class FilesManager(object):
    '''
    File manager operates with `mapp.dataset.files` classes and store
    them.
    When some error during mapp analysis occures MappError is raised.
    '''
    
    SETPATTERN = "{0}.conf"
    SEQPATTERN = "{0}.seq"

    def __init__(self, dataset, defaultsettings, settingsdir=None):
        '''
        Initializes Files manager.
        
        :param dataset: `Dataset` object to analyze
        :param defaultsettings: default settings file path
        :param settingsdir: directory for saving settings files (if none
            settings files will be saved to the same directory
            as default settings).
        '''
        self._dataset = dataset
        self._defset = defaultsettings
        if settingsdir:
            self._settingsdir = settingsdir
        else:
            self._settingsdir = os.path.dirname(os.path.realpath(defaultsettings))
        self._analyzer = Analyzer
    

    
    
    def make_files_range(self, start, to):
        ''' Makes files for given line interval in dataset
        
        :params start: first line in dataset
        :params to: last used line in dataset
        
        :returns: list of (id, `FilesContainer` object) doubles
        '''
        seqs = self._dataset.seq_range(start, to)
        containers = list()
        for seqid, sequence in seqs:
            containers.append((seqid, self.make_mapp_files(seqid, sequence)))
        return containers
    
    
    def make_mapp_files(self, fileid, sequence):
        ''' Runs mapp analysis and creates files for given id
        
        :param fileid: Id from dataset. Serves to identify relevant files.
        :param sequence: Protein sequence string
        
        :returns: object FilesContainer
        '''
        setpath = os.path.join(self._settingsdir,
                               FilesManager.SETPATTERN.format(fileid))
        newsettings = Settings.create_from_default(self._defset, fileid, setpath)
        seqpath = newsettings.get_val(BasicParser.SEQUENCE_FILE)
        sequence = Sequence.create(fileid, sequence, seqpath)
        mapp = self._analyzer(SettingsParser(newsettings.path))
        mapp.exec_mapp()
        msa = Alignment(fileid, newsettings.get_val(BasicParser.MSA_OUTFILE))
        return FilesContainer(newsettings,
                        sequence,
                        AnalysisFile(fileid, newsettings.get_val(BasicParser.BLASTSTAT_OUTFILE)),
                        Hmmerstats(fileid, newsettings.get_val(BasicParser.BLASTSTAT_OUTFILE)),
                        msa,
                        AnalysisFile(fileid, newsettings.get_val(BasicParser.TREE_OUTFILE)),
                        Mapp(fileid, newsettings.get_val(BasicParser.MAPP_OUTFILE), msa))
        
        
        
class FilesContainer(object):
    def __init__(self, settings, sequence, blast, stats, msa, tree, mapp):
        self.settings = settings
        self.sequence = sequence
        self.blast = blast
        self.stats = stats
        self.msa = msa
        self.tree = tree
        self.mapp = mapp
        
    def __eq__(self, other): 
        return self.settings == other.settings and \
                self.sequence == other.sequence and \
                self.blast == other.blast and \
                self.stats == other.stats and \
                self.msa == other.msa and \
                self.tree == other.tree and \
                self.mapp == other.mapp 
            
            