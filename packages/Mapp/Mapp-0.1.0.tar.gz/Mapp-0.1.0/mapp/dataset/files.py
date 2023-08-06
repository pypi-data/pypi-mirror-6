'''
Classes that represents some file types that are used in mapp analysis.

Created on Jan 21, 2014

'''
import os
from mapp.core.parsers import SettingsParser
from mapp.utils.common import fastalist_from_string, MappFile, AminoAcids,\
    parse_mutations
from mapp.core.exceptions import MappError
from mapp.utils.mutation_correction import correct_mutations
from ConfigParser import SafeConfigParser


class Dataset(object):
    '''
    Represents dataset object
    Atributes:
        self.datalines all lines without header (list of list of values)
        self.header only header line (list of values)
    '''
    
    idname = "Id"
    seqname = "Sequence"
    mutname = "Variation"
    
    def __init__(self, path, separator=","):
        '''
        Initialize dataset object from datset file path.
        
        :param path: Path to dataset csv file
        :param separator: csv file value separator
        '''
        with open(path, "r") as dataset:
            lines = [line.rstrip("\n").split(separator) 
                     for line in dataset.readlines()]
        self.header = lines[0]
        self.datalines = lines[1:] #without header
    
    def lines_range(self, start, to):
        '''
        :params start: First element of the list. Max is last. Min is 0.
        :params to: Last returned element. Max is last. Min is 0.
        :returns: safe range of datalines. It can be even empty.
        :raises AttributeError: if start is less than to
        '''
        start, to = self.safe_boundary(start, to)
        return self.datalines[start:to+1]
    
    
    
        
    def ids_range(self, start, to):
        '''
        Range of ids from datasetfile
        
        :params start: First id from file (first in file is 0)
        :params to: Last returned id from file
        :returns: list of ids (strings)
        '''
        seqs = self.seq_range(start, to)
        return [seq[0] for seq in seqs]
    
    def seq_range(self, start, to):
        '''
        Range of fasta sequences from datasetfile. Arguments are safe and
        boundary are checked.
        
        :params start: First fasta sequence from file (first in file is 0)
        :params to: Last returned fasta sequence from file
        
        :returns list of doubles [(seqname, sequence), ....]
        '''
        idindex = self.header.index(Dataset.idname)
        seqindex = self.header.index(Dataset.seqname)
        lines = self.lines_range(start, to)
        return [(line[idindex], line[seqindex]) for line in lines]
    
    def get_mutation(self, linenum):
        ''' Returns mutation (letter, number, letter) for the line in dataset '''
        mutindex = self.header.index(Dataset.mutname)
        mutation = self.datalines[linenum][mutindex]
        return parse_mutations(mutation)[0]

    
    def safe_boundary(self, start, to):
        ''' Correct boundaries according to dataset '''
        if start > to:
            raise AttributeError("Safe Boundary: Start attr {0} is less than to attr {1}".format(start, to))
        start = start if start >= 0 else 0
        start = start if start < len(self.datalines) else len(self.datalines) - 1
        to = to if to >= 0 else 0
        to = to if to < len(self.datalines) else len(self.datalines) - 1
        return start, to
    
    
        
        



class AnalysisFile(object):
    '''
    Represents common analysis file with absolute path.
    
    '''
    def __init__(self, dataid, path):
        '''
        :params dataid: id of analysis (and also anlyzed sequence)
        :params path: path to this file
        '''
        self.id = dataid
        self.path = os.path.abspath(path)
        if not os.path.isfile(path):
            raise AttributeError("Atribute path='{0}' isn't a file!".format(path))
        

class Settings(AnalysisFile):
    '''
    Represents mapp analysis settings
    '''
    @staticmethod
    def create_from_default(default, fileid, newsettings):
        '''
        Create settings from default Settings file.
        It will be changed only id value in default settings
        
        :params default: Default Settings file path. Only id will be changed
        :params fileid: value to change id value in settings
        :params newsettings: New settings file
        
        :returns: `Settings` object
        
        :raises: MappError when default is not readable
        '''
        config = SafeConfigParser()
        if not config.read(default):
            raise MappError("Creating settings Error",
                            "{0} file cannot be readed".format(default))
        config.set(SettingsParser.SECTION, "id", fileid)
        
        with open(newsettings, "w") as fp:
            config.write(fp)
        return Settings(fileid, newsettings)
        
    
    def __init__(self, dataid, path):
        super(Settings, self).__init__(dataid, path)
        self._parser = SettingsParser(path)
    
    def get_val(self, name):
        '''
        Get settings value from settings file.
        
        :param name: Name of the settings value. For possible names see
            `mapp.core.parser.BasicParser` defined constants.
        
        :returns: str value from settings
        '''
        return self._parser.get_val(name)


class Sequence(AnalysisFile):
    '''
    Represents sequence file
    Atributes:
        self.sequence sequence string
    '''
    
    @staticmethod
    def create(fileid, sequence, filename):
        '''
        Creates sequence file in fasta format. This file
        looks like ">fileid <newline> sequence"
        
        :param fileid: id of analysis (and also anlyzed sequence)
        :param sequence: protein sequence
        :param filename: name of new sequence file
        
        :returns: Sequence object
        '''
        with open(filename, "w") as sf:
            sf.write(">{0}\n{1}\n".format(fileid, sequence))
        return Sequence(fileid, filename)
        
    
    def __init__(self, dataid, path):
        super(Sequence, self).__init__(dataid, path)
        with open(path, "r") as seqf:
            seqstr = seqf.read()
        fastaseq = fastalist_from_string(seqstr)[0]
        self.sequence = fastaseq[1]

       
        
class Hmmerstats(AnalysisFile):
    '''
    Represents stats file from hmmer sequence searching
    Attributes:
        self.hmmerseqs number of sequences searched out by hmmer
        self.clusters number of clusters by cd-hit
    '''
    section = "stats"
    hmmerseqs = "hmmerseqs"
    clusters = "clusters"
    
    headerhmmerseqs = "Hmmer sequences"
    headerclusters = "Cd-Hit clusters"
    
    def __init__(self, dataid, path):
        super(Hmmerstats, self).__init__(dataid, path)
        parser = SafeConfigParser()
        parser.read(path)
        self.hmmerseqs = parser.get(Hmmerstats.section, Hmmerstats.hmmerseqs)
        self.clusters = parser.get(Hmmerstats.section, Hmmerstats.clusters)
            
        
        
class Alignment(AnalysisFile):
    '''
    Represents alignment file
    Atributes:
        self.sequence protein sequence accordig to dataid
        self.count number of sequences
    '''
    def __init__(self, dataid, path):
        super(Alignment, self).__init__(dataid, path)
        with open(path, "r") as msaf:
            msastr = msaf.read()
        fastaseqs = fastalist_from_string(msastr)
        
        self.count = len(fastaseqs)
        try:
            self.sequence = [seq for sid, seq in fastaseqs if sid == dataid][0]
        except IndexError:
            raise MappError("Alignment object error",
                    "seqid {0} hasn't been founded in alignment {1}".format(
                                                                dataid, path))
    
    def get_contentstring(self):
        with open(self.path, "r") as msa:
            return msa.read()

        

class Mapp(AnalysisFile):
    '''
    Represents mapp result file
    '''
    def __init__(self, dataid, path, msa, separator="\t"):
        '''
        Initializes `Mapp` object
        
        :params dataid: see `AnalysisFile` constructor
        :params path: see `AnalysisFile` constructor
        :params msa: `Alignment` object
        :params separator: Separator of values in mapp csv file
        '''
        super(Mapp, self).__init__(dataid, path)
        self._separator = separator
        if msa.id != self.id:
            raise AttributeError("Mapp id {0} != msa id {1}".format(self.id, msa.id))
        self._msa = msa
    
    def get_values(self, mutation):
        '''
        Get useful values for a certain mutation
        
        :params mutation: (letter, number, letter) tuple
        
        :returns: returns dict {header name: value} from mapp file for values:
            column 0-11, "Score" for mutation, "P-value" for mutation
                                    
        '''      
        mutation = correct_mutations(self.id, [mutation],
                                     self._msa.get_contentstring())[0]
        with open(self.path, "r") as mappfile:
            mapp = [line.split(self._separator) for line in mappfile.readlines()]
        header = mapp[0]
        mappline = mapp[mutation[1]]
        result = dict(zip(header[:12], mappline[:12]))
        scoreindex = MappFile.scoreOffset + AminoAcids.list.index(mutation[2])
        pvalueindex = MappFile.pvalueOffset + AminoAcids.list.index(mutation[2])
        result["Score"] = mappline[scoreindex]
        result["P-value"] = mappline[pvalueindex]
        return result
        
        


        
    
            