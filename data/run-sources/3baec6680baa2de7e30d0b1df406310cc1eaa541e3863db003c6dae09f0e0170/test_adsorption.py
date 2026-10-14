"""Synthetic recovery and thermodynamic limiting cases, before real fitting."""
import tempfile
from pathlib import Path
import unittest

import numpy as np

from orthopolity.adsorption import read_aif, fugacity, langmuir, competitive, iast, fit_pure

CONSTANTS = [[304.1282,7377300,.22394],[190.564,4599200,.01142]]


class AdsorptionTests(unittest.TestCase):
    def test_target_text_is_not_converted_when_only_predictors_requested(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'x.aif'
            p.write_text('loop_\n_p\n_target\n0.1 WITHHELD\n')
            self.assertEqual(read_aif(p,['_p']).tolist(),[[.1]])
            with self.assertRaises(ValueError):
                read_aif(p,['_target'])

    def test_pr_ideal_low_pressure_and_pure_limits(self):
        f = fugacity(333,1e-6,[.3,.7],CONSTANTS)
        np.testing.assert_allclose(f,[.3e-6,.7e-6],rtol=1e-6)
        self.assertEqual(fugacity(298,1,[1,0],CONSTANTS)[1],0)
        np.testing.assert_allclose(fugacity(298,2,[.3,.7],CONSTANTS,True),[.6,1.4])

    def test_pr_symmetry_and_invalid_composition(self):
        a = fugacity(333,2,[.3,.7],CONSTANTS)
        b = fugacity(333,2,[.7,.3],CONSTANTS[::-1])
        np.testing.assert_allclose(a,b[::-1],rtol=1e-13)
        with self.assertRaises(ValueError):
            fugacity(333,2,[.3,.8],CONSTANTS)

    def test_competition_conserves_sites_and_has_pure_limit(self):
        np.testing.assert_allclose(competitive([1,0],4,[2,.5]),[langmuir(1,4,2),0])
        q = competitive([2,3],4,[2,.5])
        self.assertLess(q.sum(),4)
        self.assertLess(q[0],competitive([2,0],4,[2,.5])[0])

    def test_iast_equals_shared_capacity_and_is_symmetric(self):
        for f in [[.001,.01],[1,2],[10,.1]]:
            a,_ = iast(f,[4,4],[2,.5])
            np.testing.assert_allclose(a,competitive(f,4,[2,.5]),rtol=1e-10)
        a,f0 = iast([1,2],[3,5],[2,.5])
        b,_ = iast([2,1],[5,3],[.5,2])
        np.testing.assert_allclose(a,b[::-1],rtol=1e-10)
        self.assertAlmostEqual(np.sum(np.array([1,2])/f0),1)

    def test_iast_zero_and_single_component(self):
        np.testing.assert_array_equal(iast([0,0],[3,4],[2,1])[0],[0,0])
        np.testing.assert_allclose(iast([1,0],[3,4],[2,1])[0],[2,0])

    def test_common_capacity_recovers_synthetic_world(self):
        fs = [np.geomspace(.01,10,18)]*2
        qs = [langmuir(f,4,b) for f,b in zip(fs,[2,.5])]
        fit = fit_pure(fs,qs,[np.full(18,.02)]*2)
        np.testing.assert_allclose(fit['capacities'],[4,4],rtol=1e-7)
        np.testing.assert_allclose(fit['affinities'],[2,.5],rtol=1e-7)
        self.assertTrue(fit['locally_identified'])
        self.assertTrue(fit['pure_fit_adequate'])

    def test_different_capacities_fail_common_fit_but_separate_recovers(self):
        fs = [np.geomspace(.01,100,24)]*2
        qs = [langmuir(f,q,b) for f,q,b in zip(fs,[2,6],[2,.5])]
        us = [np.full(24,.02)]*2
        common, separate = fit_pure(fs,qs,us),fit_pure(fs,qs,us,False)
        self.assertFalse(common['pure_fit_adequate'])
        np.testing.assert_allclose(separate['capacities'],[2,6],rtol=1e-7)
        np.testing.assert_allclose(separate['affinities'],[2,.5],rtol=1e-7)

    def test_unsaturated_curves_flag_weak_capacity_identification(self):
        fs = [np.geomspace(1e-7,1e-5,12)]*2
        qs = [langmuir(f,4,b) for f,b in zip(fs,[2,.5])]
        fit = fit_pure(fs,qs,[np.full(12,.001)]*2)
        self.assertFalse(fit['locally_identified'])


if __name__ == '__main__':
    unittest.main()
