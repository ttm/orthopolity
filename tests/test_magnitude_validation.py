import importlib.util
from pathlib import Path
import unittest

import numpy as np

from orthopolity.magnitude_validation import (
    first_accepted_tick, gate_cell, observed_bins, population_limit,
    registered_summary, simulate_source_ticks, source_grid_estimate, wilson_interval,
)

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('registered_volumetric', ROOT/'experiments/run_volumetric_b.py')
old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)
MODEL = dict(intercept=-0.03, slope=1.035, source_sigma=0)


class MagnitudeValidation(unittest.TestCase):
    def test_point_and_completeness_match_original_runner(self):
        m = np.repeat([1, 1.1, 1.2, 1.3, 1.5], [120, 100, 90, 80, 70])
        actual = registered_summary(m, np.random.default_rng(3), n_boot=1000)
        mc = old.completeness(m)
        b, _ = old.b_value(m[m >= mc-1e-9], mc, np.random.default_rng(4), n_boot=10)
        self.assertEqual(actual['mc'], mc)
        self.assertAlmostEqual(actual['b'], b)

    def test_multinomial_bootstrap_matches_independent_analytic_delta_se(self):
        m = np.repeat([1, 1.1, 1.2, 1.3, 1.5], [1200, 1000, 900, 800, 700])
        fit = registered_summary(m, np.random.default_rng(12), n_boot=2000)
        selected = m[m >= fit['mc']-1e-9]
        expected = np.log10(np.e)/(selected.mean()-fit['mc']+0.05)**2*np.std(selected)/np.sqrt(len(selected))
        self.assertLess(abs(fit['se']/expected-1), 0.06)

    def test_geometric_lattice_diagnostic_recovers_known_population(self):
        for beta in (1, 1.035, 1.718):
            model = dict(MODEL, slope=beta)
            limit = population_limit(1.3, 1.17, model)
            self.assertAlmostEqual(limit['integrated_mass'], 1, places=11)
            self.assertGreater(limit['lowest_accepted_source_edge'], limit['true_source_lower'])
            self.assertAlmostEqual(limit['grid_b_limit'], 1.3, places=9)

    def test_rounded_boundary_inversion_and_ties(self):
        for beta in (1, 1.035, 1.718):
            model = dict(MODEL, slope=beta)
            for mc in (0, 1.2, 2.1, 3.5):
                first = first_accepted_tick(mc, model)
                self.assertGreaterEqual(observed_bins(first, model), mc-1e-9)
                self.assertLess(observed_bins(first-1, model), mc-1e-9)
        self.assertIsNone(source_grid_estimate([20]*200, observed_bins(20, MODEL), MODEL))

    def test_insufficient_and_invalid_data_do_not_fit(self):
        result = registered_summary([1]*300+[2]*199, np.random.default_rng(1))
        self.assertFalse(result['eligible'])
        self.assertNotIn('b', result)
        for values in ([], [np.nan], [np.inf]):
            with self.assertRaises(ValueError):
                registered_summary(values, np.random.default_rng(1))
        with self.assertRaises(ValueError):
            simulate_source_ticks(1,1,5,dict(MODEL,slope=0),np.random.default_rng(1))

    def test_gaussian_cdf_zero_scatter_limit(self):
        a = population_limit(1.3, 1.173, MODEL)
        b = population_limit(1.3, 1.173, dict(MODEL, source_sigma=1e-5))
        self.assertAlmostEqual(a['b_limit'], b['b_limit'], places=7)
        self.assertAlmostEqual(b['integrated_mass'], 1, places=11)

    def test_gate_and_coverage_boundaries(self):
        gate = dict(minimum_eligibility_rate=.95, max_absolute_mean_bias=.05, minimum_coverage=.9)
        self.assertTrue(gate_cell(380,400,.05,.9,gate))
        self.assertFalse(gate_cell(380,400,.05001,.9,gate))
        self.assertFalse(gate_cell(379,400,0,1,gate))
        self.assertFalse(gate_cell(0,400,None,None,gate))
        self.assertEqual(wilson_interval(0,0),[None,None])
        lo, hi = wilson_interval(380,400)
        self.assertLess(lo,.95)
        self.assertGreater(hi,.95)


if __name__ == '__main__':
    unittest.main()
