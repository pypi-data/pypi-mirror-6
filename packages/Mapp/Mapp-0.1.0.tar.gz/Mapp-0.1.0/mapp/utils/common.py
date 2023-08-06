'''
Common functions or variables to all modules

Created on Dec 3, 2013
'''

import sys, os
import re
from StringIO import StringIO 
from subprocess import PIPE, Popen
from collections import Counter
import operator
#without append package path to sys.path mapp package couldn't be imported
#when this (common.py) package imports files run asi script (using main)
sys.path.append(os.path.dirname(os.path.realpath(__file__ + '/../../')))
from mapp.core.exceptions import MappError
import mapp.utils.mutation_correction as correction




class AminoAcids(object):
    ''' Contains list of standard amino acids '''
    
    list = ["A","C","D","E","F","G","H","I","K","L","M","N","P","Q","R","S","T","V","W","Y"]


class MappFile(object):
    ''' Contains offsets of positions of values in mapp files '''
    naOffset = 5
    scoreOffset = 12
    pvalueOffset = 32
    alignmentOffset = 3
    hydroOffset = 6
    polarityOffset = 7
    chargeOffset = 8
    volumeOffset = 9
    alfaEnergyOffset = 10
    betaEnergyOffset = 11


def analyse_mutations(seqid, mutations, msa, mapp, p_value=0.1):
    """
    This method evaluates mutations according to msa and mapp.
    
    :param seqid: sequence id. Sequence has to be found in msa.
    :param mutations: mutations string or [(letter, number, letter), ... ] list
    :param msa: msa string. Probably readed from msa file.
    :param mapp: mapp string. Probably readed from mapp file.
    
    :returns: list of dictionaries with keys:
        mutation - mutation "letterNUMBERletter"
        alignments - alignments column
        state - values: "correct", "incorrect letter", "not predicted"
        pvalue - p-value of target letter
        prediction - 'neu' or 'del'
    """
    if isinstance(mutations, basestring):
        mutations = parse_mutations(mutations)
    corrmuts = correction.correct_mutations(seqid, mutations, msa)
    mapplines = mapp.splitlines()
    
    results = list()    
    for i, mut in enumerate(corrmuts):
        result = dict()
        results.append(result)
        result['mutation'] = ''.join(map(str, mutations[i]))
        mutletter1 = mut[0]
        mutnumber = mut[1]
        mutletter2 = mut[2]
        
        mappline = mapplines[mutnumber]
        mappline = mappline.split("\t")
        align_column = mappline[MappFile.alignmentOffset]
        result['alignment'] = letter_count(align_column.lstrip("'"))
        result['state'] = 'correct'
        result['pvalue'] = 'N/A'
        result['prediction'] = 'N/A'
        if mutletter1.lower() not in align_column.lower(): #mutation letter1 is not in alignment column
            #it means the letter1 is not on correct position
            result['state'] = 'incorrect letter'
            continue
        if (mappline[MappFile.naOffset] != "N"): # valuepredicted by mapp
            result['state'] = 'not predicted'
            continue
        mut_pvalue = float(mappline[MappFile.pvalueOffset 
                                 + AminoAcids.list.index(mutletter2.upper())])
        result['pvalue'] = mut_pvalue
        if (mut_pvalue > p_value): #mutation is predicted neutral
            result['prediction'] = 'neutral'
        else:
            result['prediction'] = 'deleterious'
        
    return results


def letter_count(alignstr):
    '''
    Transforms align column. E.g. from ACDFAA to 3xA, 1xC, 1xD, 1xF
    :returns: Transformed alignstr
    '''
    alignstr = alignstr.upper()
    c = Counter(alignstr)
    csorted = sorted(c.iteritems(), key=operator.itemgetter(1), reverse=True)
    return ', '.join(['{0}x{1}'.format(value, key) for key, value in csorted]).replace('-', 'gap')
        


def parse_mutations(mutations):
    ''' This function returns list of tuples [(letter, position, new letter), ... ]
            Position is int.
         It searches <letterNumbersLetter> format in mutations string.'''
    mutlist = re.compile("([a-zA-Z])(\d+)([a-zA-Z])", re.IGNORECASE).findall(mutations)
    corectedlist = [(mut[0], int(mut[1]), mut[2]) for mut in mutlist]
    return corectedlist


def exec_command(command, programname):
    '''
    Executes any executable shell command.
    
    :param command: command string with arguments
    :param programname: programname is used in Error reporting.
    :raises: `MappError`
    '''
    if not command:
        return
    print("{:*^80}".format(" " + programname + " "))
    program = Popen(command.split(), stdout=PIPE, stdin=PIPE, stderr=PIPE)
    out = program.communicate()
    if program.returncode != 0:
        raise MappError(header=programname + " program ended with error!",
                        description="Exit code:" + str(program.returncode)
                            + "\n" + "stderr:\n" + out[1] + "\nstdout:\n" + out[0])
    if not out[0]:
        print("OK\n")
    else:
        print(out[0] + "\n")
    print("*"*80)


def fastalist_from_string(fastastr):
    '''
    Parse string in fastaformat and make list from it.
    
    :param fastastr: string in fasta format
    
    :returns: list of tuples [("id...", "SEQUENCE"), ...]
    '''
    seqpattern = re.compile(">(.+)\n((?:[a-z*-]+\n?)+)", re.IGNORECASE)
    fastastr += "\n"
    sequences = seqpattern.findall(fastastr)
    sequences = list(rreplace(sequences, "\n", ""))
    return sequences


def rreplace(it, old, new):
    ''' Recursively replaces `old` string to `new` string
        in list of list of lists...'''
    try:
        return it.replace(old, new)
    except AttributeError:
        return tuple([rreplace(x, old, new) for x in it])

def fastastring_from_list(fastalist):
    if len(fastalist)==0:
        raise AttributeError("fastalist len = 0!")
    output = StringIO()
    for seqid, seq in fastalist:
        output.write('>' + seqid + '\n')
        output.write(seq + '\n')
    return output.getvalue()
        

def check_fastastring(fastastr):
    ''' Check if `fastastr` is fasta formatted string.'''
    fastastr += "\n" #rather more than none "\n" at the end
    r = re.compile(r"^(>.+\n([a-zA-Z*\-]+\n)+)+\n*$", re.IGNORECASE)
    return r.match(fastastr) 
    

def check_positive(value):
    ivalue = int(value)
    if ivalue < 0:
        raise AttributeError("%s is an invalid positive int value" % value)
    return ivalue

def check_positive_nozero(value):
    ivalue = check_positive(value)
    if ivalue == 0:
        raise AttributeError("%s is zero value" % value)
    return ivalue


def transform_id(idstr):
    ''' Transforms idstr param to short form and acceptable for mapp.
    :param idstr: sequence's id obtained e.g. from blast
    :returns: short and acceptable id string
    '''
    idstr = re.sub("[\n\r]", "", idstr)
    idstr = re.sub("[^\w]", "_", idstr)
    lst = idstr.split("_")
    return lst[0] + ("_" + lst[1] if len(lst) > 1 else "")     

def transform_fasta_for_mapp(instr):
    ''' Transforming fasta file before it is used in analysis. It replaces unexpected characters. '''
    return re.sub("[^\w\n\r>_]", "_", instr).replace("\r", "\n").replace("\n\n", "\n").replace("_\n","\n")
