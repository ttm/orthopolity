import unittest
import numpy as np
from orthopolity import resource_spectrum, bounded_power_mle, mean_resource_exponent, residual_audio

class ScientificChecks(unittest.TestCase):
    def test_total_resource_including_final_edge_and_empty_bin(self):
        s=resource_spectrum([1,2,1000],[1,100,7],[1,10,100,1000])
        self.assertEqual(s['count'].tolist(),[2,0,1])
        self.assertAlmostEqual(s['resource_sum'].sum(),108)
        self.assertEqual(s['phi'][1],0)
        self.assertAlmostEqual(np.dot(s['occupancy'],s['log_width']),108)
    def test_mean_not_median_for_resource_accounting(self):
        s=resource_spectrum([1,2,3],[1,1,100],[1,10])
        self.assertEqual(s['resource_sum'][0],102)
        self.assertEqual(s['mean_resource'][0],34)
    def test_change_of_units_preserves_normalized_spectrum(self):
        a=resource_spectrum([1,2,20],[1,3,8],[1,10,100])
        b=resource_spectrum([100,200,2000],[1000,3000,8000],[100,1000,10000])
        np.testing.assert_allclose(a['phi'],b['phi'])
    def test_weighted_accounting_and_exclusions(self):
        s=resource_spectrum([1,20,200],[2,3,999],[1,10,100],weights=[3,4,1])
        self.assertEqual(s['excluded'],1)
        self.assertEqual(s['resource_sum'].sum(),18)
    def test_missing_data_cannot_disappear(self):
        with self.assertRaises(ValueError):resource_spectrum([1,2],[1,np.nan],[1,10])
    def test_known_bounded_distribution(self):
        # Deterministic quantiles of alpha=2 on [1,100], avoiding random flukes.
        u=(np.arange(10000)+.5)/10000
        x=1/(1-u*(1-.01))
        self.assertAlmostEqual(bounded_power_mle(x,1,100),2,places=3)
    def test_conditional_mean_scaling(self):
        x=np.geomspace(1,100,100)
        d,A=mean_resource_exponent(x,3*x**1.7)
        self.assertAlmostEqual(d,1.7,places=4)
        self.assertAlmostEqual(A,3,places=3)
    def test_sound_is_bounded_and_empty_bins_silent(self):
        s=residual_audio([1,0,2],seconds_per_bin=.1)
        self.assertEqual(len(s),6615)
        self.assertLessEqual(abs(s).max(),.150001)
        self.assertTrue(np.all(s[2205:4410]==0))

if __name__=='__main__':unittest.main()
