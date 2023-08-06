'''
Created on Jan 21, 2014
'''
import unittest
from mapp.dataset.files import Dataset, AnalysisFile, Settings, Sequence,\
    Hmmerstats, Alignment, Mapp
import os
from mapp.core.parsers import BasicParser, SettingsParser
from ConfigParser import SafeConfigParser


class Test(unittest.TestCase):
   
    testfilesdir = "dataset_testfiles"
    dataset = os.path.join(testfilesdir, "dataset.csv")
    settings = os.path.join(testfilesdir, "1.conf")
    seqfile = os.path.join(testfilesdir, "1.seq")
    statfile = os.path.join(testfilesdir, "1.stats")
    msafile = os.path.join(testfilesdir, "1.afa")
    mappfile = os.path.join(testfilesdir, "1.mapp")
    
    datasetlines = """1,1,1433E_HUMAN,del,M1A,p.Leu219Ala,P62258,1433E_HUMAN,MDDRED
2,2,1433T_HUMAN,del,D6A,p.Arg127Ala,P27348,1433T_HUMAN,MCCREDA"""
    datasetlines = [line.split(",") for line in datasetlines.splitlines()]
    
    datasetheader = "Id,Row,PMD cross-reference,Effect,Variation,Variation - HGVS format,Uniprot accession number,Uniprot entry name,Sequence"
    datasetheader = datasetheader.split(",")
    
    datasetids = [line[datasetheader.index("Id")] for line in datasetlines]
    datasetseqs = [(line[datasetheader.index("Id")], line[datasetheader.index("Sequence")]) for line in datasetlines]
    
    id1 = datasetlines[0][datasetheader.index("Id")]
    id2 = datasetlines[1][datasetheader.index("Id")]
    sequence1 = datasetlines[0][datasetheader.index("Sequence")]

    def setUp(self):
        pass


    def tearDown(self):
        pass


    def test_datset(self):
        dataset = Dataset(Test.dataset)
        Test.assertSequenceEqual(self, Test.datasetheader, dataset.header)
        Test.assertSequenceEqual(self, Test.datasetlines, dataset.datalines)
    
    def test_dataset_lines_range(self):
        dataset = Dataset(Test.dataset)
        lines2 = dataset.lines_range(0, 1)
        Test.assertSequenceEqual(self, Test.datasetlines, lines2)
        lines3 = dataset.lines_range(1,1)
        Test.assertSequenceEqual(self, [Test.datasetlines[1]], lines3)
        Test.assertRaises(self, AttributeError, dataset.lines_range, 1, 0)
    
    def test_dataset_ids_range(self):
        dataset = Dataset(Test.dataset)
        ids1 = dataset.ids_range(0, 1)
        Test.assertSequenceEqual(self, Test.datasetids, ids1)
        ids2 = dataset.ids_range(1,1)
        Test.assertSequenceEqual(self, [Test.datasetids[1]], ids2)
        Test.assertRaises(self, AttributeError, dataset.ids_range, 1, 0)
    
    def test_dataset_seq_range(self):
        dataset = Dataset(Test.dataset)
        seqs1 = dataset.seq_range(0, 1)
        Test.assertSequenceEqual(self, Test.datasetseqs, seqs1)
    
    
    def test_dataset_safe_boundaries(self):
        dataset = Dataset(Test.dataset)
        start, to = dataset.safe_boundary(0, 1)
        Test.assertEqual(self, (start, to), (0, 1))
        start, to = dataset.safe_boundary(0, 0)
        Test.assertEqual(self, (start, to), (0, 0))
        start, to = dataset.safe_boundary(1, 1)
        Test.assertEqual(self, (start, to), (1, 1))
        start, to = dataset.safe_boundary(2, 2)
        Test.assertEqual(self, (start, to), (1, 1))
        start, to = dataset.safe_boundary(-1, 5)
        Test.assertEqual(self, (start, to), (0, 1))      
        Test.assertRaises(self, AttributeError, dataset.safe_boundary, 5, 1)
        
    
    def test_analysis_file(self):
        Test.assertRaises(self, AttributeError, AnalysisFile, Test.id1, "asdf")
        #test not raises
        AnalysisFile(Test.id1, Test.dataset)
    
    def test_settings(self):
        settings = Settings(Test.id1, Test.settings)
        blast = settings.get_val(BasicParser.BLAST_PROGRAM)
        Test.assertEqual(self, "cp ../default.stats 1.stats", blast)
        
        newid="id2"
        newsettings = os.path.join(Test.testfilesdir, newid + ".conf")
        newSet = Settings.create_from_default(settings.path, newid, newsettings)
        config = SafeConfigParser()
        config.read(newSet.path)
        newid2 = config.get(SettingsParser.SECTION, "id")
        Test.assertEqual(self, newid, newid2)
        
    
    def test_sequence(self):
        sequence = Sequence(Test.id1, Test.seqfile)
        Test.assertEqual(self, Test.sequence1, sequence.sequence)
    
    def test_hmmerstats(self):
        stats = Hmmerstats(Test.id1, Test.statfile)
        Test.assertEqual(self, "100", stats.hmmerseqs)
        Test.assertEqual(self, "3", stats.clusters)
    
    def test_alignment(self):
        msa = Alignment(Test.id1, Test.msafile)
        Test.assertEqual(self, "-MDDRED--", msa.sequence)
        Test.assertEqual(self, 3, msa.count)
    
    def test_mapp(self):
        header = "Position\tColumn Score\tColumn p-value\tAlignment\tGap Weight\tOver Gap Weight Threshold\tHydropathy\tPolarity\tCharge\tVolume\tFree energy alpha\tFree energy beta\tA\tC\tD\tE\tF\tG\tH\tI\tK\tL\tM\tN\tP\tQ\tR\tS\tT\tV\tW\tY\tA\tC\tD\tE\tF\tG\tH\tI\tK\tL\tM\tN\tP\tQ\tR\tS\tT\tV\tW\tY\tGood Amino Acids\tBad Amino Acids"
        header = header.split("\t")
        origline = "3\t16.72\t6.427E-4\t'DCC\t0.0\tN\t1E0\t1E0\t9.962E-1\t1.074E-1\t5.675E-1\t1E0\t18.98\t1.70\t1.82\t25.89\t20.34\t14.70\t10.62\t16.73\t16.71\t19.34\t20.20\t2.22\t37.34\t13.29\t19.22\t5.78\t2.27\t8.40\t29.50\t19.97\t3.127E-4\t9.456E-1\t9.272E-1\t5.188E-5\t2.103E-4\t1.317E-3\t7.506E-3\t6.408E-4\t6.445E-4\t2.807E-4\t2.188E-4\t8.461E-1\t6.006E-6\t2.289E-3\t2.914E-4\t1.18E-1\t8.341E-1\t2.405E-2\t2.414E-5\t2.335E-4\tCDNSTV\tAEFGHIKLMPQRWY"
        origline = origline.split("\t")
        correct = dict(zip(header[:12], origline[:12]))
        correct["Score"] = origline[12]
        correct["P-value"] = origline[32]
        
        msa = Alignment(Test.id1, Test.msafile)
        mapp = Mapp(Test.id1, Test.mappfile, msa)
        mutation = ("D", 2, "A")
        mappdict = mapp.get_values(mutation)
        Test.assertDictEqual(self, correct, mappdict)
        
        
        
        
        
        
        
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_datset']
    unittest.main()