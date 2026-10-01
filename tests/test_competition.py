import unittest

import numpy as np
from scipy.integrate import quad

from orthopolity.competition import (
    competing_capacities, forward_resource_profile, local_dimensions,
    minimum_density, minimum_survival,
)


class CompetitionChecks(unittest.TestCase):
    def test_opposed_resources_have_finite_support_and_fixed_marginals(self):
        x = competing_capacities(120000, -1, np.random.default_rng(92))
        np.testing.assert_allclose(np.mean(x>=2,axis=0), .5, atol=.006)
        np.testing.assert_allclose(1/x[:,0]+1/x[:,1], 1, atol=3e-15)
        sizes = x.min(axis=1)
        self.assertTrue(np.all(sizes<=2))
        self.assertAlmostEqual(np.mean(sizes>=1.5), 1/3, delta=.005)
        self.assertEqual(minimum_survival(2.1,-1),0)

    def test_density_integrates_to_one_for_all_correlations(self):
        for rho in (-1,-.5,0,.5,1):
            upper = 2 if rho==-1 else np.inf
            total = quad(lambda k: minimum_density(k,rho),1,upper,epsabs=1e-9,limit=200)[0]
            self.assertAlmostEqual(total,1,delta=3e-8)

    def test_density_matches_independent_survival_derivative(self):
        for rho in (-.5,0,.5):
            for k in (1.3,2,5):
                delta=k*1e-5
                difference=(minimum_survival(k-delta,rho)-minimum_survival(k+delta,rho))/(2*delta)
                self.assertAlmostEqual(difference,minimum_density(k,rho),delta=1e-8)

    def test_opposed_profile_is_neutral_despite_varying_feasibility(self):
        edges=np.geomspace(1,2,11)
        prediction=forward_resource_profile(edges,-1)
        np.testing.assert_allclose(prediction['phi'],1,atol=3e-15)
        self.assertAlmostEqual(prediction['totals'].sum(),2*np.log(2))
        result=local_dimensions(np.array([1.2,1.8]),-1)
        np.testing.assert_allclose(result['density_exponent'],2)
        np.testing.assert_allclose(result['feasibility'],[2.5,10])

    def test_gaussian_density_dimension_and_finite_bridge(self):
        for rho in (-.5,0,.5):
            k=10.0;step=1e-4
            left=local_dimensions(k*np.exp(-step),rho)['feasibility']
            right=local_dimensions(k*np.exp(step),rho)['feasibility']
            current=local_dimensions(k,rho)
            correction=(np.log(right)-np.log(left))/(2*step)
            self.assertAlmostEqual(current['density_exponent'],1+current['feasibility']-correction,delta=2e-8)
        self.assertGreater(local_dimensions(10000,-.5)['feasibility'],3.7)

    def test_positive_and_negative_coupling_change_joint_extremes(self):
        threshold=3.0
        negative=minimum_survival(threshold,-.5)
        independent=minimum_survival(threshold,0)
        positive=minimum_survival(threshold,.5)
        self.assertLess(negative,independent)
        self.assertLess(independent,positive)
        capacities=competing_capacities(120000,-.5,np.random.default_rng(100))
        self.assertAlmostEqual(np.mean(np.all(capacities>=threshold,axis=1)),negative,delta=.003)

    def test_invalid_parameters_and_support_are_rejected(self):
        with self.assertRaises(ValueError):competing_capacities(10,-1.1,np.random.default_rng(0))
        with self.assertRaises(ValueError):local_dimensions(2,-1)
        with self.assertRaises(ValueError):forward_resource_profile([1,3],-1)


if __name__=='__main__':unittest.main()
