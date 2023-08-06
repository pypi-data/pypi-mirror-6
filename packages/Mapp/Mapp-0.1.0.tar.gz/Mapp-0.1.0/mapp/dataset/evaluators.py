'''
Classes that can evaluate some dataset and create results files.
Created on Jan 28, 2014

'''
from mapp.dataset.files import Dataset, Hmmerstats
from mapp.dataset.files_managers import FilesManager
from os import path
from mapp.core.exceptions import MappError
import logging

class Evaluator(object):
    '''
    Evaluator can evaluate `mapp.dataset.files.Dataset`
    '''


    def __init__(self, dataset, defsettings, workdir):
        '''
        Initializes Evaluator
        Attribute self.resultdir can be changed to change output directory
                  self.filepattern can be changed to change result file format.
                      name of the file is result of self.filepattern.format(id)
                      expression
        
        :param datset: path to dataset
        :param defsettings: path to default settings. Common for all anlysis.
        :param workdir: path to working directory where files will be created
        '''
        self._dataset = Dataset(dataset)
        self._settings = defsettings
        self._workdir = workdir
        self.resultdir = workdir
        self.filepattern = "{0}.result"
        self.separator = "\t"
        
    
    def make_results_range(self, start, to):
        '''
        Makes result files for given line range in dataset file
        
        :param start: first analyzed line in dataset
        :param to: last analyzed line in dataset
        
        :returns: list of created result csv files. Values in these files are
            separated with self.separator
        '''
        filesman = FilesManager(self._dataset, self._settings, self._workdir)
        containers = filesman.make_files_range(start, to)
        files = list()
        for i, cont in enumerate(containers, start):
            fileid, cont = cont
            try:
                header, data = self.make_result_lines(cont, i)
            except MappError as e: #Some error in dataset.
                logging.warning("%s\n%s", e.header, e.description)
                continue
            result = path.join(self.resultdir, self.filepattern.format(fileid))
            files.append(result)
            with open(result, "w") as resf:
                resf.write(self.separator.join(header) + "\n" + \
                           self.separator.join(data) + "\n")
        return files
    
    
    def make_results_stepwise(self, start, to):
        '''
        Makes result files for given range one by one
            (not at once like `make_results_range` does.
            
        :param start: first analyzed line in dataset
        :param to: last analyzed line in dataset
        
        :returns: list of created result csv files. Values in these files are
            separated with self.separator
        '''
        start, to = self._dataset.safe_boundary(start, to)
        files = list()
        for i in xrange(start, to+1):
            try:
                files += self.make_results_range(i, i)
            except MappError as e:
                logging.warning("Making result for dataline %s ends with MappError\n%s\n%s" % \
                                (i, e.header, e.description))
        return files
        
            
            
    def make_result_lines(self, container, linenum):
        header = self._dataset.header
        dataline = self._dataset.datalines[linenum]
        header.append(Hmmerstats.headerhmmerseqs)
        dataline.append(str(container.stats.hmmerseqs))
        header.append(Hmmerstats.headerclusters)
        dataline.append(str(container.stats.clusters))
        mutation = self._dataset.get_mutation(linenum)
        mappdict = container.mapp.get_values(mutation)
        mappheader, mappline = zip(*mappdict.items())
        header += mappheader
        dataline += mappline
        return (header, dataline)

    
    
    
    
    
    
        