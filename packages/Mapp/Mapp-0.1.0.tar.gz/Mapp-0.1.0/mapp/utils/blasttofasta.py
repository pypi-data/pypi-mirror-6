'''
Converting XML blast output to fasta format. Can be used as script.

Usage: blasttofasta.py [-h] [-i INPUT] [-o OUTPUT] [-m MAX SEQ]

Created on Dec 3, 2013

'''
import sys, os
#without append package path to sys.path mapp package couldn't be imported
sys.path.append(os.path.dirname(os.path.realpath(__file__ + '/../../')))

from xml.etree import ElementTree
from cStringIO import StringIO      #most efficient string builder - see http://www.skymind.com/~ocrow/python_string/
import re
from mapp.utils.common import check_positive_nozero, transform_id

"""
MAIN FUNCTION
"""
def main():
    import argparse
    
    #parsing comand line argumetns
    parser = argparse.ArgumentParser(description='Convert BLAST xml file to FASTA file.')
    parser.add_argument('-i', '--input', help='Path to the input BLAST xml file. Default is stdin.', dest='input')
    parser.add_argument('-o', '--output', help='Path to the output FASTA file. Default is stdout.', dest='output')
    parser.add_argument('-m', '--max', help='Maximum sequences to be converted.', dest='maxseqs', type=check_positive_nozero)
    args = parser.parse_args()
    #set input
    infile = sys.stdin
    if args.input != None:
        infilePath = args.input
        try:
            infile = open(infilePath, 'r')
        except IOError:
            exit("Input file {0} cann't be opened!\n".format(infilePath))
            #read xml file to string
    try:
        instr = infile.read()
        infile.close()
    except IOError:
        sys.stderr.write("ERROR while reading from {0}\n".format(infile.name))
        exit(1)
        #set output
    openedOutFile = sys.stdout
    if args.output != None:
        outfilePath = args.output
        try:
            openedOutFile = open(outfilePath, 'w')
        except IOError:
            exit("Output file {0} cann't be opened!\n".format(outfilePath))
    #convert xml to fasta and write to the output file
    maxseqs = args.maxseqs if args.maxseqs else sys.maxint
    try:
        fastaSeqs = convertXMLtoFASTA(instr, maxseqs=maxseqs)
    except ElementTree.ParseError:
        sys.stderr.write("ERROR in xml instr. Parser cann't parse it!\n")
        openedOutFile.close()
        exit(1)
    openedOutFile.write(fastaSeqs)
    openedOutFile.close()
    exit(0)
    
    
    

def convertXMLtoFASTA(inputStr, maxseqs=sys.maxint):
    """
    Converts XML file in blast format to fasta format. Moreover it is needed to
    remove sequences that contains (besides standard 20 amino acid letters) nonstandard
    amino acid letter (like J etc.) and/or removes duplicate sequences.
    
    :param inputStr: XML string - output from blast with parameter -fmt=5
    :param maxseqs: Maximum sequences to be saved.
    
    :returns: None if error occured. Else it retuns (multiline) string contains
        sequences in FASTA format.
        
    :raises: ElementTree.ParseError when errors occure in xml instr.
    """
       
    output = StringIO()
    seqcount = 0
    root = ElementTree.fromstring(inputStr)
    for hit in root.getiterator('Hit'):
        hit_seq = hit.find('Hit_hsps/Hsp/Hsp_hseq')
        #erase spaces and - from sequence
        hit_seq.text = re.compile("[ -]").sub("", hit_seq.text)
        seqcount += 1
        if seqcount > maxseqs:
            break
        hit_id = hit.find('Hit_id')
        idstr = transform_id(hit_id.text)
        output.write('>' + idstr + '\n')
        output.write(hit_seq.text + '\n')
    return output.getvalue()




if __name__ == "__main__":
    main()

