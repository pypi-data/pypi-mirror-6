===================
MAPP python package
===================

This package servers to simplify workflow of
`MAPP program <http://mendel.stanford.edu/sidowlab/downloads/MAPP/>`_.


Prerequisites
=============

You have to install:

* Python 2.7

* `MAPP program <http://mendel.stanford.edu/sidowlab/downloads/MAPP/>`_.

* Optionally download `fasta database <ftp://ftp.ncbi.nlm.nih.gov/blast/db/FASTA/>`_
  (or it is possible to use HMMER or BLAST program remotely).

* Install program for sequence searching. Recommended is `HMMER <http://hmmer.janelia.org/software>`_.
  Or it is possible to download  `BLAST <http://blast.ncbi.nlm.nih.gov/Blast.cgi?PAGE_TYPE=BlastDocs&DOC_TYPE=Download>`_.

* Install multiple sequence alignment program (recommended is `MAFFT <http://mafft.cbrc.jp/alignment/software/>`_).

* Install phylogenetic tree construction program (recommended is `FastTree <http://www.microbesonline.org/fasttree/#Install>`_).

* Install `Biopython <http://biopython.org/DIST/docs/install/Installation.html>`_ package (if you want to use file convert tools).


Settings File
=============

For MAPP analysis settings file is needed (in `python ConfigParser <https://docs.python.org/2/library/configparser.html>`_ syntax).

Settings file contains commands and input/output of commands.
One command should be one basic shell command (semicolon etc. are not allowed).

Settings file could be easilly created by another script and then is easy to run
multiple mapp analysis at once.

Basic and minimal required structer for ``settings.conf`` is::

   [commands]
   #id used for name of analysis
   id=
   #sequence file in fasta format
   sequence = 
   #output file from blast or hmmer program
   blastout = 
   #file where programs store stats about sequence picking
   blaststat = 
   # blast command to run
   blast = 
   # input file for multiple sequence aligning program (same as blast output)
   msain = %(blastout)s
   # msa program output file
   msaout = 
   # this command is executed before msa program is executed
   # (it could be for blast output conversion and purifying)
   beforemsa = 
   # msa program command
   msa = 
   # tree program input file (converted msaout file to newick format)
   treein = 
   # tree program output file
   treeout = 
   # this command is executed before the tree program
   beforetree = 
   # tree program command
   tree = 
   # mapp program input msa file (in fasta format - could be the same as msaout value)
   mappinmsa = 
   # mapp program input tree file (in newick format)
   mappintree =
   # mapp program output file 
   mappout = 
   # command before the mapp command (good for e.g. adjust tree to proper newick format)
   # MAPP is really sensitive to proper file format
   beforemapp = 
   # MAPP command itself
   mapp = java -jar MAPP.jar -f %(mappinmsa)s -t %(mappintree)s -o %(mappout)s
   

Basic usage in python program
=============================

Basic python code::

   from mapp.core.analyzers import Analyzer
   from mapp.core.parsers import SettingsParser
   from mapp.core.exceptions import MappError
   
   settings_file = 'settings.conf'
   
   def main():
       try:
           mapp = Analyzer(SettingsParser(settings_file))
           mapp.exec_mapp()
       except MappError as e:
           print(e.header)
           print(e.description)
      
   if __name__ == '__main__':
       main()


Helper files
============

In the ``mapp.utils`` package are files that can be use as standalone scripts or as modules. This file mostly serves for file conversions and purifying.