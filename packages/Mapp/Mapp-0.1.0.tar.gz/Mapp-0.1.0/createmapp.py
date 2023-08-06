'''
Module can be run from command line and with good settings file can
provide mapp analysis. See main section at the end of file.

Created on Dec 4, 2013
'''

from argparse import ArgumentParser
from mapp.core.analyzers import Analyzer
from mapp.core.parsers import SettingsParser
from mapp.core.exceptions import MappError


def prepare_arguments():
    parser = ArgumentParser(description='Runs MAPP analysis. Settings file is required.')
    parser.add_argument('-s', '--settings', required=True,
                        help='Path to the settings file', dest='settings')
    parser.add_argument('-b', '--blast', help='Exclude blast searching?',
                            dest='blast', action='store_false', default=True)
    parser.add_argument('-a', '--msa', help='Exclude aligning?',
                            dest='msa', action='store_false', default=True)
    parser.add_argument('-t', '--tree', help='Exclude tree constructing?',
                            dest='tree', action='store_false', default=True)
    parser.add_argument('-m', '--mapp', help='Exclude mapp analysing?',
                            dest='mapp', action='store_false', default=True)
    args = parser.parse_args()
    return args
    


#------------------------------------------------------------------------------
#---------------------------------    MAIN    ---------------------------------
#------------------------------------------------------------------------------
def main():
    args = prepare_arguments()
    try:
        mapp = Analyzer(SettingsParser(args.settings))
        
        mapp.exec_mapp(newblast=args.blast,
                       newmsa=args.msa,
                       newtree=args.tree,
                       newmapp=args.mapp)
    except MappError as e:
        print(e.header)
        print(e.description)



if __name__ == '__main__':
    main()

