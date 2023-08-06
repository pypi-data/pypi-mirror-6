'''
Created on Jan 16, 2014
'''
import unittest
from mapp.utils.hmmertofasta import convertXMLtoFASTA
from mapp.utils.common import fastalist_from_string


class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def test_convertxmltofasta(self):
        fastastr = convertXMLtoFASTA(xml, 3)
        seqs = fastalist_from_string(fastastr)
        Test.assertListEqual(self, seqs, trueseqs)
        
        
        
        
trueseqs=[("3edc_D", "MKPVTLYDVAEYAGVSYQTVSRVVNQASHVSAKTREKVEAAMAELNYIPNRVAQQLAGKQSLLIGVATSSLALHAPSQIVAAIKSRADQLGASVVVSMVERSGVEACKAAVHNLLAQRVSGLIINYPLDDQDAIAVEAACTNVPALFLDVSDQTPINSIIFSHEDGTRLGVEHLVALGHQQIALLAGPLSSVSARLRLAGWHKYLTRNQIQPIAEREGDWSAMSGFQQTMQMLNEGIVPTAMLVANDQMALGAMRAITESGLRVGADISVVGYDDTEDSSCYIPPLTTIKQDFRLLGQTSVDRLLQLSQGQAVKGNQLLPVSLVKRKTTLAPNTQTASPRALADSLMQLARQVSRLESGQ"),
          ("1lbi_D", "MKPVTLYDVAEYAGVSYQTVSRVVNQASHVSAKTREKVEAAMAELNYIPNRVAQQLAGKQSLLIGVATSSLALHAPSQIVAAIKSRADQLGASVVVSMVERSGVEACKTAVHNLLAQRVSGLIINYPLDDQDAIAVEAACTNVPALFLDVSDQTPINSIIFSHEDGTRLGVEHLVALGHQQIALLAGPLSSVSARLRLAGWHKYLTRNQIQPIAEREGDWSAMSGFQQTMQMLNEGIVPTAMLVANDQMALGAMRAITESGLRVGADISVVGYDDTEDSSCYIPPLTTIKQDFRLLGQTSVDRLLQLSQGQAVKGNQLLPVSLVKRKTTLAPNTQTASPRALADSLMQLARQVSRLESGQ"),
          ("1jyf_A", "MKPVTLYDVAEYAGVSYQTVSRVVNQASHVSAKTREKVEAAMAELNYIPNRVAQQLAGKQSLLIGVATSSLALHAPSQIVAAIKSRADQLGASVVVSMVERSGVEACKTAVHNLLAQRVSGLIINYPLDDQDAIAVEAACTNVPALFLDVSDQTPINSIIFSHEDGTRLGVEHLVALGHQQIALLAGPLSSVSARLRLAGWHKYLTRNQIQPIAEREGDWSAMSGFQQTMQMLNEGIVPTAMLVANDQMALGAMRAITESGLRVGADISVVGYDDTEDSSCYIPPLTTIKQDFRLLGQTSVDRLLQLSQGQAVKGNQLLPVSLVKRKTTLAPNTQTASPRALADSLMQL")]


xml=r"""<opt>
<data name="results" algo="phmmer" uuid="D2E7700E-7EFE-11E3-831E-3AF8988A7913">
<_internal highevalue="1.7e-229" lowevalue="0.0082"/>
<hits name="3edc_D" acc="3edc_D" arch="PF00356.16 PF13377.1" archScore="4" archindex="131326499695836" bias="7.1" dcl="12736" desc="Lactose operon repressor" evalue="1.7e-229" extlink="http://www.rcsb.org/pdb/explore.do?structureId=3edc" flags="3" kg="Bacteria" ndom="1" nincluded="1" niseqs="4" nregions="1" nreported="1" pvalue="-539.069642661259" score="764.1" sindex="6167536" species="Escherichia coli K-12" taxid="562" taxlink="http://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?mode=Info&id=">
<domains aliId="1" aliIdCount="360" aliL="360" aliM="360" aliN="360" aliSim="1" aliSimCount="360" aliaseq="MKPVTLYDVAEYAGVSYQTVSRVVNQASHVSAKTREKVEAAMAELNYIPNRVAQQLAGKQSLLIGVATSSLALHAPSQIVAAIKSRADQLGASVVVSMVERSGVEACKAAVHNLLAQRVSGLIINYPLDDQDAIAVEAACTNVPALFLDVSDQTPINSIIFSHEDGTRLGVEHLVALGHQQIALLAGPLSSVSARLRLAGWHKYLTRNQIQPIAEREGDWSAMSGFQQTMQMLNEGIVPTAMLVANDQMALGAMRAITESGLRVGADISVVGYDDTEDSSCYIPPLTTIKQDFRLLGQTSVDRLLQLSQGQAVKGNQLLPVSLVKRKTTLAPNTQTASPRALADSLMQLARQVSRLESGQ" alicsline="0" alihmmacc="" alihmmdesc="" alihmmfrom="1" alihmmname=">P03023" alihmmto="360" alimem="1291601264" alimline="mkpvtlydvaeyagvsyqtvsrvvnqashvsaktrekveaamaelnyipnrvaqqlagkqslligvatsslalhapsqivaaiksradqlgasvvvsmversgveackaavhnllaqrvsgliinyplddqdaiaveaactnvpalfldvsdqtpinsiifshedgtrlgvehlvalghqqiallagplssvsarlrlagwhkyltrnqiqpiaeregdwsamsgfqqtmqmlnegivptamlvandqmalgamraitesglrvgadisvvgyddtedsscyipplttikqdfrllgqtsvdrllqlsqgqavkgnqllpvslvkrkttlapntqtaspraladslmqlarqvsrlesgq" alimmline="0" alimodel="mkpvtlydvaeyagvsyqtvsrvvnqashvsaktrekveaamaelnyipnrvaqqlagkqslligvatsslalhapsqivaaiksradqlgasvvvsmversgveackaavhnllaqrvsgliinyplddqdaiaveaactnvpalfldvsdqtpinsiifshedgtrlgvehlvalghqqiallagplssvsarlrlagwhkyltrnqiqpiaeregdwsamsgfqqtmqmlnegivptamlvandqmalgamraitesglrvgadisvvgyddtedsscyipplttikqdfrllgqtsvdrllqlsqgqavkgnqllpvslvkrkttlapntqtaspraladslmqlarqvsrlesgq" aliniseqs="4" alippline="8**********************************************************************************************************************************************************************************************************************************************************************************************************************************************************************8" alirfline="0" alisindex="6167536" alisqacc="3edc_D" alisqdesc="Lactose operon repressor" alisqfrom="1" alisqname="3edc_D" alisqto="360" bias="7.11" bitscore="763.952880859375" cevalue="7.1e-233" iali="1" ienv="1" ievalue="1.9e-229" is_included="1" is_reported="1" jali="360" jenv="360" oasc="1.00"/>
<pdbs>1cjg_A</pdbs>
<pdbs>1cjg_B</pdbs>
<pdbs>1efa_A</pdbs>
<pdbs>1efa_B</pdbs>
<pdbs>1efa_C</pdbs>
<pdbs>1jwl_A</pdbs>
<pdbs>1jwl_B</pdbs>
<pdbs>1jwl_C</pdbs>
<pdbs>1jye_A</pdbs>
<pdbs>1jyf_A</pdbs>
<pdbs>1l1m_A</pdbs>
<pdbs>1l1m_B</pdbs>
<pdbs>1lbg_A</pdbs>
<pdbs>1lbg_B</pdbs>
<pdbs>1lbg_C</pdbs>
<pdbs>1lbg_D</pdbs>
<pdbs>1lbh_A</pdbs>
<pdbs>1lbh_B</pdbs>
<pdbs>1lbh_C</pdbs>
<pdbs>1lbh_D</pdbs>
<pdbs>1lbi_A</pdbs>
<pdbs>1lbi_B</pdbs>
<pdbs>1lbi_C</pdbs>
<pdbs>1lbi_D</pdbs>
<pdbs>1lcc_A</pdbs>
<pdbs>1lcd_A</pdbs>
<pdbs>1lqc_A</pdbs>
<pdbs>1osl_A</pdbs>
<pdbs>1osl_B</pdbs>
<pdbs>1tlf_A</pdbs>
<pdbs>1tlf_B</pdbs>
<pdbs>1tlf_C</pdbs>
<pdbs>1tlf_D</pdbs>
<pdbs>2bjc_A</pdbs>
<pdbs>2bjc_B</pdbs>
<pdbs>2kei_A</pdbs>
<pdbs>2kei_B</pdbs>
<pdbs>2kej_A</pdbs>
<pdbs>2kej_B</pdbs>
<pdbs>2kek_A</pdbs>
<pdbs>2kek_B</pdbs>
<pdbs>2p9h_A</pdbs>
<pdbs>2p9h_B</pdbs>
<pdbs>2paf_A</pdbs>
<pdbs>2paf_B</pdbs>
<pdbs>2pe5_A</pdbs>
<pdbs>2pe5_B</pdbs>
<pdbs>2pe5_C</pdbs>
<pdbs>3edc_A</pdbs>
<pdbs>3edc_B</pdbs>
<pdbs>3edc_C</pdbs>
<pdbs>3edc_D</pdbs>
<seqs an="" de="Lactose operon repressor" dn="3edc_C" sp="Escherichia coli K-12"/>
<seqs an="" de="Lactose operon repressor" dn="3edc_B" sp="Escherichia coli K-12"/>
<seqs an="" de="Lactose operon repressor" dn="3edc_A" sp="Escherichia coli K-12"/>
</hits>
<hits name="1lbi_D" acc="1lbi_D" arch="PF00356.16 PF13377.1" archScore="4" archindex="131326499695836" bias="7.0" dcl="14456" desc="LAC REPRESSOR" evalue="5.7e-229" extlink="http://www.rcsb.org/pdb/explore.do?structureId=1lbi" flags="3" kg="Bacteria" ndom="1" nincluded="1" niseqs="12" nregions="1" nreported="1" pvalue="-537.887896539854" score="762.4" sindex="6167549" species="Escherichia coli" taxid="562" taxlink="http://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?mode=Info&id=">
<domains aliId="0.997222222222222" aliIdCount="359" aliL="360" aliM="360" aliN="360" aliSim="0.997222222222222" aliSimCount="359" aliaseq="MKPVTLYDVAEYAGVSYQTVSRVVNQASHVSAKTREKVEAAMAELNYIPNRVAQQLAGKQSLLIGVATSSLALHAPSQIVAAIKSRADQLGASVVVSMVERSGVEACKTAVHNLLAQRVSGLIINYPLDDQDAIAVEAACTNVPALFLDVSDQTPINSIIFSHEDGTRLGVEHLVALGHQQIALLAGPLSSVSARLRLAGWHKYLTRNQIQPIAEREGDWSAMSGFQQTMQMLNEGIVPTAMLVANDQMALGAMRAITESGLRVGADISVVGYDDTEDSSCYIPPLTTIKQDFRLLGQTSVDRLLQLSQGQAVKGNQLLPVSLVKRKTTLAPNTQTASPRALADSLMQLARQVSRLESGQ" alicsline="0" alihmmacc="" alihmmdesc="" alihmmfrom="1" alihmmname=">P03023" alihmmto="360" alimem="46912855093120" alimline="mkpvtlydvaeyagvsyqtvsrvvnqashvsaktrekveaamaelnyipnrvaqqlagkqslligvatsslalhapsqivaaiksradqlgasvvvsmversgveack avhnllaqrvsgliinyplddqdaiaveaactnvpalfldvsdqtpinsiifshedgtrlgvehlvalghqqiallagplssvsarlrlagwhkyltrnqiqpiaeregdwsamsgfqqtmqmlnegivptamlvandqmalgamraitesglrvgadisvvgyddtedsscyipplttikqdfrllgqtsvdrllqlsqgqavkgnqllpvslvkrkttlapntqtaspraladslmqlarqvsrlesgq" alimmline="0" alimodel="mkpvtlydvaeyagvsyqtvsrvvnqashvsaktrekveaamaelnyipnrvaqqlagkqslligvatsslalhapsqivaaiksradqlgasvvvsmversgveackaavhnllaqrvsgliinyplddqdaiaveaactnvpalfldvsdqtpinsiifshedgtrlgvehlvalghqqiallagplssvsarlrlagwhkyltrnqiqpiaeregdwsamsgfqqtmqmlnegivptamlvandqmalgamraitesglrvgadisvvgyddtedsscyipplttikqdfrllgqtsvdrllqlsqgqavkgnqllpvslvkrkttlapntqtaspraladslmqlarqvsrlesgq" aliniseqs="12" alippline="8**********************************************************************************************************************************************************************************************************************************************************************************************************************************************************************8" alirfline="0" alisindex="6167549" alisqacc="1lbi_D" alisqdesc="LAC REPRESSOR" alisqfrom="1" alisqname="1lbi_D" alisqto="360" bias="6.96" bitscore="762.266906738281" cevalue="2.3e-232" iali="1" ienv="1" ievalue="6.3e-229" is_included="1" is_reported="1" jali="360" jenv="360" oasc="1.00"/>
<pdbs>1lbi_D</pdbs>
<pdbs>1lbi_C</pdbs>
<pdbs>1lbi_B</pdbs>
<pdbs>1lbi_A</pdbs>
<pdbs>1lbh_D</pdbs>
<pdbs>1lbh_C</pdbs>
<pdbs>1lbh_B</pdbs>
<pdbs>1lbh_A</pdbs>
<pdbs>1lbg_D</pdbs>
<pdbs>1lbg_C</pdbs>
<pdbs>1lbg_B</pdbs>
<pdbs>1lbg_A</pdbs>
<seqs an="" de="LAC REPRESSOR" dn="1lbi_C" sp="Escherichia coli"/>
<seqs an="" de="LAC REPRESSOR" dn="1lbi_B" sp="Escherichia coli"/>
<seqs an="" de="LAC REPRESSOR" dn="1lbi_A" sp="Escherichia coli"/>
<seqs an="" de="INTACT LACTOSE OPERON REPRESSOR WITH GRATUITO" dn="1lbh_D" sp="Escherichia coli"/>
<seqs an="" de="INTACT LACTOSE OPERON REPRESSOR WITH GRATUITO" dn="1lbh_C" sp="Escherichia coli"/>
<seqs an="" de="INTACT LACTOSE OPERON REPRESSOR WITH GRATUITO" dn="1lbh_B" sp="Escherichia coli"/>
<seqs an="" de="INTACT LACTOSE OPERON REPRESSOR WITH GRATUITO" dn="1lbh_A" sp="Escherichia coli"/>
<seqs an="" de="PROTEIN (LACTOSE OPERON REPRESSOR)" dn="1lbg_D" sp="Escherichia coli"/>
<seqs an="" de="PROTEIN (LACTOSE OPERON REPRESSOR)" dn="1lbg_C" sp="Escherichia coli"/>
<seqs an="" de="PROTEIN (LACTOSE OPERON REPRESSOR)" dn="1lbg_B" sp="Escherichia coli"/>
<seqs an="" de="PROTEIN (LACTOSE OPERON REPRESSOR)" dn="1lbg_A" sp="Escherichia coli"/>
</hits>
<hits name="1jyf_A" acc="1jyf_A" arch="PF00356.16 PF13377.1" archScore="4" archindex="131326499695836" bias="6.0" dcl="16176" desc="Lactose Operon Repressor" evalue="1.9e-222" extlink="http://www.rcsb.org/pdb/explore.do?structureId=1jyf" flags="3" kg="Bacteria" ndom="1" nincluded="1" niseqs="1" nregions="1" nreported="1" pvalue="-522.880195669746" score="741.0" sindex="6167548" species="Escherichia coli" taxid="562" taxlink="http://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?mode=Info&id=">
<domains aliId="0.997134670487106" aliIdCount="348" aliL="349" aliM="360" aliN="349" aliSim="0.997134670487106" aliSimCount="348" aliaseq="MKPVTLYDVAEYAGVSYQTVSRVVNQASHVSAKTREKVEAAMAELNYIPNRVAQQLAGKQSLLIGVATSSLALHAPSQIVAAIKSRADQLGASVVVSMVERSGVEACKTAVHNLLAQRVSGLIINYPLDDQDAIAVEAACTNVPALFLDVSDQTPINSIIFSHEDGTRLGVEHLVALGHQQIALLAGPLSSVSARLRLAGWHKYLTRNQIQPIAEREGDWSAMSGFQQTMQMLNEGIVPTAMLVANDQMALGAMRAITESGLRVGADISVVGYDDTEDSSCYIPPLTTIKQDFRLLGQTSVDRLLQLSQGQAVKGNQLLPVSLVKRKTTLAPNTQTASPRALADSLMQL" alicsline="0" alihmmacc="" alihmmdesc="" alihmmfrom="1" alihmmname=">P03023" alihmmto="349" alimem="46915001961920" alimline="mkpvtlydvaeyagvsyqtvsrvvnqashvsaktrekveaamaelnyipnrvaqqlagkqslligvatsslalhapsqivaaiksradqlgasvvvsmversgveack avhnllaqrvsgliinyplddqdaiaveaactnvpalfldvsdqtpinsiifshedgtrlgvehlvalghqqiallagplssvsarlrlagwhkyltrnqiqpiaeregdwsamsgfqqtmqmlnegivptamlvandqmalgamraitesglrvgadisvvgyddtedsscyipplttikqdfrllgqtsvdrllqlsqgqavkgnqllpvslvkrkttlapntqtaspraladslmql" alimmline="0" alimodel="mkpvtlydvaeyagvsyqtvsrvvnqashvsaktrekveaamaelnyipnrvaqqlagkqslligvatsslalhapsqivaaiksradqlgasvvvsmversgveackaavhnllaqrvsgliinyplddqdaiaveaactnvpalfldvsdqtpinsiifshedgtrlgvehlvalghqqiallagplssvsarlrlagwhkyltrnqiqpiaeregdwsamsgfqqtmqmlnegivptamlvandqmalgamraitesglrvgadisvvgyddtedsscyipplttikqdfrllgqtsvdrllqlsqgqavkgnqllpvslvkrkttlapntqtaspraladslmql" aliniseqs="1" alippline="8**********************************************************************************************************************************************************************************************************************************************************************************************************************************************************97" alirfline="0" alisindex="6167548" alisqacc="1jyf_A" alisqdesc="Lactose Operon Repressor" alisqfrom="1" alisqname="1jyf_A" alisqto="349" bias="6.01" bitscore="740.856201171875" cevalue="7.6e-226" iali="1" ienv="1" ievalue="2.1e-222" is_included="1" is_reported="1" jali="349" jenv="349" oasc="1.00"/>
<pdbs>1jyf_A</pdbs>
</hits>
<stats Z="226694" Z_setby="0" domZ="83" domZ_setby="0" elapsed="0.12" n_past_bias="1093" n_past_fwd="85" n_past_msv="1269" n_past_vit="173" nhits="83" nincluded="77" nmodels="1" nreported="83" nseqs="226694" page="1" sys="0" total="1" unpacked="83" user="0"/>
</data>
</opt>
"""

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_xmltofasta']
    unittest.main()