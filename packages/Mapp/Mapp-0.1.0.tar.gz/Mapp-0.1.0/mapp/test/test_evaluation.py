'''
Created on Jan 3, 2014
'''
import unittest
from mapp.utils.common import MappFile
from mapp.utils.common import AminoAcids as aa
from mapp.performance.evaluation import evaluate_mapp


class Test(unittest.TestCase):

    def setUp(self):
        mapp = ["Position\tColumn Score\tColumn p-value\tAlignment\tGap Weight\tOver Gap Weight Threshold\tHydropathy\tPolarity\tCharge\tVolume\tFree energy alpha\tFree energy beta\tA\tC\tD\tE\tF\tG\tH\tI\tK\tL\tM\tN\tP\tQ\tR\tS\tT\tV\tW\tY\tA\tC\tD\tE\tF\tG\tH\tI\tK\tL\tM\tN\tP\tQ\tR\tS\tT\tV\tW\tY\tGood Amino Acids\tBad Amino Acids",
                "1\t10.08\t1.262E-3\t'MMMMVMMMMVMMMMMMMMMMMMMMVVMVVMVVVMMVMVMMVMVMVVMMMVMMMV\t0.0\tN\t5.113E-1\t2.07E-2\t1E0\t9.952E-1\t9.004E-1\t9.865E-1\t7.56\t8.47\t39.89\t34.94\t4.51\t11.96\t15.09\t4.48\t31.73\t4.22\t2.83\t16.90\t15.20\t13.34\t38.53\t9.73\t8.80\t7.03\t8.74\t10.41\t6.226E-3\t3.348E-3\t3.831E-7\t8.458E-7\t8.35E-2\t4.737E-4\t1.226E-4\t8.523E-2\t1.502E-6\t1.11E-1\t4.57E-1\t6.305E-5\t1.176E-4\t2.518E-4\t4.716E-7\t1.54E-3\t2.698E-3\t9.2E-3\t2.814E-3\t1.047E-3\tFILM\tACDEGHKNPQRSTVWY",
                "2\t23.22\t9.644E-6\t'KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK\t0.0\tN\t6.268E-3\t3.588E-3\t2\t3.082E-2\t2.039E-1\t1.252E-1\t26.45\t29.33\t21.52\t23.70\t21.07\t26.98\t15.82\t25.96\t0.14\t18.99\t17.24\t14.55\t39.91\t14.08\t7.31\t23.00\t27.99\t33.06\t23.44\t26.46\t4.448E-6\t2.403E-6\t1.514E-5\t8.544E-6\t1.717E-5\t3.953E-6\t9.285E-5\t4.97E-6\t1E0\t3.173E-5\t5.611E-5\t1.519E-4\t3.819E-7\t1.841E-4\t7.494E-3\t1.021E-5\t3.173E-6\t1.176E-6\t9.121E-6\t4.436E-6\tK\tACDEFGHILMNPQRSTVWY",
                "3\t20.24\t2.179E-5\t'PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP\t0.0\tN\t2.263E-1\t6.835E-1\t1E0\t2.659E-2\t1.717E-3\t2.369E-3\t20.00\t20.21\t41.24\t38.89\t22.47\t20.27\t19.31\t28.75\t31.81\t26.92\t17.48\t17.41\t0.14\t17.67\t41.48\t17.50\t17.77\t27.21\t25.36\t19.95\t2.339E-5\t2.199E-5\t3.14E-7\t4.459E-7\t1.173E-5\t2.159E-5\t2.878E-5\t2.708E-6\t1.482E-6\t4.008E-6\t5.174E-5\t5.296E-5\t1E0\t4.848E-5\t3.034E-7\t5.136E-5\t4.696E-5\t3.755E-6\t5.712E-6\t2.371E-5\tP\tACDEFGHIKLMNQRSTVWY",
                "4\t20.95\t1.773E-5\t'VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV\t0.0\tN\t3.402E-3\t1.577E-2\t1E0\t1E0\t9.97E-1\t3.294E-3\t27.75\t9.32\t33.13\t32.45\t21.09\t23.22\t17.83\t11.96\t30.41\t20.81\t24.43\t15.88\t38.09\t17.56\t33.95\t17.62\t15.28\t0.11\t33.75\t19.81\t3.342E-6\t1.965E-3\t1.162E-6\t1.314E-6\t1.704E-5\t9.653E-6\t4.602E-5\t4.74E-4\t1.936E-6\t1.845E-5\t7.133E-6\t9.099E-5\t5.051E-7\t5.039E-5\t1.005E-6\t4.931E-5\t1.14E-4\t1E0\t1.04E-6\t2.475E-5\tV\tACDEFGHIKLMNPQRSTWY",
                "5\t20.95\t1.773E-5\t'VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV\t0.0\tN\t3.402E-3\t1.577E-2\t1E0\t1E0\t9.97E-1\t3.294E-3\t27.75\t9.32\t33.13\t32.45\t21.09\t23.22\t17.83\t11.96\t30.41\t20.81\t24.43\t15.88\t38.09\t17.56\t33.95\t17.62\t15.28\t0.11\t33.75\t19.81\t3.342E-6\t1.965E-3\t1.162E-6\t1.314E-6\t1.704E-5\t9.653E-6\t4.602E-5\t4.74E-4\t1.936E-6\t1.845E-5\t7.133E-6\t9.099E-5\t5.051E-7\t5.039E-5\t1.005E-6\t4.931E-5\t1.14E-4\t1E0\t1.04E-6\t2.475E-5\tV\tACDEFGHIKLMNPQRSTWY",
                "6\t20.95\t1.773E-5\t'VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV\t0.0\tN\t3.402E-3\t1.577E-2\t1E0\t1E0\t9.97E-1\t3.294E-3\t27.75\t9.32\t33.13\t32.45\t21.09\t23.22\t17.83\t11.96\t30.41\t20.81\t24.43\t15.88\t38.09\t17.56\t33.95\t17.62\t15.28\t0.11\t33.75\t19.81\t3.342E-6\t1.965E-3\t1.162E-6\t1.314E-6\t1.704E-5\t9.653E-6\t4.602E-5\t4.74E-4\t1.936E-6\t1.845E-5\t7.133E-6\t9.099E-5\t5.051E-7\t5.039E-5\t1.005E-6\t4.931E-5\t1.14E-4\t1E0\t1.04E-6\t2.475E-5\tV\tACDEFGHIKLMNPQRSTWY",
                "7\t20.95\t1.773E-5\t'VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV\t0.0\tN\t3.402E-3\t1.577E-2\t1E0\t1E0\t9.97E-1\t3.294E-3\t27.75\t9.32\t33.13\t32.45\t21.09\t23.22\t17.83\t11.96\t30.41\t20.81\t24.43\t15.88\t38.09\t17.56\t33.95\t17.62\t15.28\t0.11\t33.75\t19.81\t3.342E-6\t1.965E-3\t1.162E-6\t1.314E-6\t1.704E-5\t9.653E-6\t4.602E-5\t4.74E-4\t1.936E-6\t1.845E-5\t7.133E-6\t9.099E-5\t5.051E-7\t5.039E-5\t1.005E-6\t4.931E-5\t1.14E-4\t1E0\t1.04E-6\t2.475E-5\tV\tACDEFGHIKLMNPQRSTWY",
                "8\t20.95\t1.773E-5\t'VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV\t0.0\tN\t3.402E-3\t1.577E-2\t1E0\t1E0\t9.97E-1\t3.294E-3\t27.75\t9.32\t33.13\t32.45\t21.09\t23.22\t17.83\t11.96\t30.41\t20.81\t24.43\t15.88\t38.09\t17.56\t33.95\t17.62\t15.28\t0.11\t33.75\t19.81\t3.342E-6\t1.965E-3\t1.162E-6\t1.314E-6\t1.704E-5\t9.653E-6\t4.602E-5\t4.74E-4\t1.936E-6\t1.845E-5\t7.133E-6\t9.099E-5\t5.051E-7\t5.039E-5\t1.005E-6\t4.931E-5\t1.14E-4\t1E0\t1.04E-6\t2.475E-5\tV\tACDEFGHIKLMNPQRSTWY",
                "9\t20.95\t1.773E-5\t'VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV\t0.0\tN\t3.402E-3\t1.577E-2\t1E0\t1E0\t9.97E-1\t3.294E-3\t27.75\t9.32\t33.13\t32.45\t21.09\t23.22\t17.83\t11.96\t30.41\t20.81\t24.43\t15.88\t38.09\t17.56\t33.95\t17.62\t15.28\t0.11\t33.75\t19.81\t3.342E-6\t1.965E-3\t1.162E-6\t1.314E-6\t1.704E-5\t9.653E-6\t4.602E-5\t4.74E-4\t1.936E-6\t1.845E-5\t7.133E-6\t9.099E-5\t5.051E-7\t5.039E-5\t1.005E-6\t4.931E-5\t1.14E-4\t1E0\t1.04E-6\t2.475E-5\tV\tACDEFGHIKLMNPQRSTWY",
                "10\t20.95\t1.773E-5\t'VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV\t0.0\tN\t3.402E-3\t1.577E-2\t1E0\t1E0\t9.97E-1\t3.294E-3\t27.75\t9.32\t33.13\t32.45\t21.09\t23.22\t17.83\t11.96\t30.41\t20.81\t24.43\t15.88\t38.09\t17.56\t33.95\t17.62\t15.28\t0.11\t33.75\t19.81\t3.342E-6\t1.965E-3\t1.162E-6\t1.314E-6\t1.704E-5\t9.653E-6\t4.602E-5\t4.74E-4\t1.936E-6\t1.845E-5\t7.133E-6\t9.099E-5\t5.051E-7\t5.039E-5\t1.005E-6\t4.931E-5\t1.14E-4\t1E0\t1.04E-6\t2.475E-5\tV\tACDEFGHIKLMNPQRSTWY"
                ]
        mapplist = [line.split("\t") for line in mapp]
        self.mutations = list()
        
        mapplist[1][MappFile.pvalueOffset + aa.list.index("A")] = 0.01 #deleterious
        self.mutations.append((("M", 1, "A"), "del")) #tp
        
        mapplist[2][MappFile.pvalueOffset + aa.list.index("C")] = 0.02 #deleterious
        self.mutations.append((("K", 2, "C"), "neu")) #fp       
        mapplist[3][MappFile.pvalueOffset + aa.list.index("C")] = 0.02 #deleterious
        self.mutations.append((("K", 3, "C"), "neu")) #fp
        
        mapplist[4][MappFile.pvalueOffset + aa.list.index("D")] = 0.5 #neutral
        self.mutations.append((("P", 4, "D"), "neu")) #tn        
        mapplist[5][MappFile.pvalueOffset + aa.list.index("D")] = 0.5 #neutral
        self.mutations.append((("P", 5, "D"), "neu")) #tn
        mapplist[6][MappFile.pvalueOffset + aa.list.index("D")] = 0.5 #neutral
        self.mutations.append((("P", 6, "D"), "neu")) #tn
        
        mapplist[7][MappFile.pvalueOffset + aa.list.index("E")] = 0.9 #neutral
        self.mutations.append((("V", 7, "E"), "del")) #fn
        mapplist[8][MappFile.pvalueOffset + aa.list.index("E")] = 0.9 #neutral
        self.mutations.append((("V", 8, "E"), "del")) #fn
        mapplist[9][MappFile.pvalueOffset + aa.list.index("E")] = 0.9 #neutral
        self.mutations.append((("V", 9, "E"), "del")) #fn
        mapplist[10][MappFile.pvalueOffset + aa.list.index("E")] = 0.9 #neutral
        self.mutations.append((("V", 10, "E"), "del")) #fn
        
        
        #values are: tp = 1, fp = 2, tn = 3, fn = 4
        
        self.mapp = ['\t'.join(map(str, mappline)) for mappline in mapplist]

    def tearDown(self):
        pass


    def test_evaluation(self):
        result = evaluate_mapp(self.mapp, self.mutations)
        Test.assertEqual(self, 1, result["tp"], "Wrong evaluation value")
        Test.assertEqual(self, 2, result["fp"], "Wrong evaluation value")
        Test.assertEqual(self, 3, result["tn"], "Wrong evaluation value")
        Test.assertEqual(self, 4, result["fn"], "Wrong evaluation value")
        Test.assertAlmostEqual(self, 4.0/10, result["accuracy"])
        Test.assertAlmostEqual(self, -0.21821789, result["mcc"])
        Test.assertAlmostEqual(self, 1.0, result["coverage"])
        Test.assertAlmostEqual(self, 1.0/5, result["sensitivity"])
        Test.assertAlmostEqual(self, 3.0/5, result["specificity"])
        Test.assertAlmostEqual(self, 1.0/3, result["ppv"])
        Test.assertAlmostEqual(self, 3.0/7, result["npv"])


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_evaluation']
    unittest.main()