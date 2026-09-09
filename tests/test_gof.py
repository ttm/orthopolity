import unittest
import numpy as np
from scipy.integrate import quad
from gof import (fit_powerlaw, fit_lognormal, fit_exponential, fit_weibull,
                 logpdf_of, ks_distance, powerlaw_gof, vuong,
                 flatness_equivalence, sample_powerlaw, _pl_cdf)

LO, HI = 1.0, 1000.0


def _integral(fit):
    v, _ = quad(lambda z: float(np.exp(logpdf_of(fit, np.array([z]), LO, HI))[0]),
                LO, HI, limit=400)
    return v


class BoundedFits(unittest.TestCase):
    def setUp(self):
        self.rng = np.random.default_rng(11)
        self.x = sample_powerlaw(3000, 2.4, LO, HI, self.rng)

    def test_every_truncated_density_integrates_to_one(self):
        for f in (fit_powerlaw, fit_lognormal, fit_exponential, fit_weibull):
            self.assertAlmostEqual(_integral(f(self.x, LO, HI)), 1.0, places=3)

    def test_recovers_known_exponent(self):
        self.assertAlmostEqual(fit_powerlaw(self.x, LO, HI)['params']['alpha'], 2.4, places=1)

    def test_cdf_spans_the_declared_domain(self):
        self.assertAlmostEqual(float(_pl_cdf(np.array([LO]), 2.4, LO, HI)[0]), 0.0)
        self.assertAlmostEqual(float(_pl_cdf(np.array([HI]), 2.4, LO, HI)[0]), 1.0)

    def test_alpha_one_is_not_singular(self):
        # alpha == 1 is the removable singularity in the normaliser.
        fit = dict(name='power_law', params=dict(alpha=1.0))
        self.assertAlmostEqual(_integral(fit), 1.0, places=6)

    def test_observations_outside_the_domain_are_refused(self):
        with self.assertRaises(ValueError):
            fit_powerlaw(np.array([0.5, 2.0, 5.0]), LO, HI)


class GoodnessOfFit(unittest.TestCase):
    def test_power_law_data_is_not_ruled_out(self):
        x = sample_powerlaw(1200, 2.5, LO, HI, np.random.default_rng(2))
        self.assertGreater(powerlaw_gof(x, LO, HI, n_boot=200, seed=5)['p_value'], 0.1)

    def test_lognormal_data_is_ruled_out(self):
        rng = np.random.default_rng(4)
        x = np.exp(rng.normal(2.0, 1.0, 6000))
        x = x[(x >= LO) & (x <= HI)][:1200]
        g = powerlaw_gof(x, LO, HI, n_boot=200, seed=5)
        self.assertLessEqual(g['p_value'], 0.1)
        self.assertTrue(g['ruled_out'])

    def test_vuong_identifies_a_clearly_wrong_alternative(self):
        x = sample_powerlaw(2000, 2.6, LO, HI, np.random.default_rng(6))
        r = vuong(x, fit_powerlaw(x, LO, HI), fit_exponential(x, LO, HI), LO, HI)
        self.assertGreater(r['loglike_ratio'], 0)
        self.assertEqual(r['favours'], 'power_law')

    def test_ks_distance_is_zero_for_the_exact_quantiles(self):
        u = (np.arange(2000) + 0.5) / 2000
        t = 1.4
        x = LO * np.exp(-np.log1p(u * np.expm1(-t * np.log(HI / LO))) / t)
        self.assertLess(ks_distance(x, 1 + t, LO, HI), 1e-3)


class Equivalence(unittest.TestCase):
    centers = np.geomspace(1, 100, 9)

    def test_tolerance_follows_the_declared_factor_and_span(self):
        r = flatness_equivalence(self.centers, np.ones(9), tolerance_factor=1.25)
        self.assertAlmostEqual(r['slope_tolerance'], np.log(1.25) / np.log(100), places=9)

    def test_flat_spectrum_with_tight_draws_is_equivalent(self):
        r = flatness_equivalence(self.centers, np.ones(9), tolerance_factor=1.25,
                                 slope_draws=np.random.default_rng(1).normal(0, 0.002, 400))
        self.assertTrue(r['slope_equivalent'])
        self.assertTrue(r['departure_within_tolerance'])
        self.assertEqual(r['verdict'], 'equivalent to flat')

    def test_sloped_spectrum_fails_on_slope(self):
        phi = (self.centers / self.centers[0]) ** -0.3
        r = flatness_equivalence(self.centers, phi, tolerance_factor=1.25,
                                 slope_draws=np.random.default_rng(1).normal(-0.3, 0.01, 400))
        self.assertFalse(r['slope_equivalent'])
        self.assertEqual(r['verdict'], 'not equivalent to flat')

    def test_wavy_spectrum_with_zero_slope_fails_on_departure(self):
        # The central lesson of the ocean re-expression: a spectrum can have a
        # near-zero fitted slope while varying by a large factor across bins.
        phi = np.array([3.0, 0.35, 3.0, 0.35, 3.0, 0.35, 3.0, 0.35, 3.0])
        r = flatness_equivalence(self.centers, phi, tolerance_factor=1.25,
                                 slope_draws=np.random.default_rng(1).normal(0, 0.002, 400))
        self.assertLess(abs(r['slope']), r['slope_tolerance'])   # slope test passes
        self.assertTrue(r['slope_equivalent'])
        self.assertFalse(r['departure_within_tolerance'])        # departure test fails
        self.assertEqual(r['verdict'], 'not equivalent to flat')
        self.assertEqual(r['failed_criterion'], 'departure')

    def test_no_sampling_model_yields_no_verdict(self):
        r = flatness_equivalence(self.centers, np.ones(9), tolerance_factor=1.25)
        self.assertIsNone(r['slope_ci'])
        self.assertIn('unavailable', r['verdict'])


if __name__ == '__main__':
    unittest.main()


class DiscreteGR(unittest.TestCase):
    """Magnitudes are recorded on a 0.1 grid, so the continuous KS test is
    invalid on them; these check the discrete replacement."""

    def test_recovers_a_known_b_value(self):
        from gof import discrete_gr_gof
        rng = np.random.default_rng(0)
        b, step, thr = 1.0, 0.1, 5.5
        q = 10 ** (-b * step)
        k = rng.geometric(1 - q, size=20000) - 1
        r = discrete_gr_gof(thr + k * step, thr, step, n_boot=100, seed=1)
        # SE(b) is about 0.007 at this n, so allow ~4 standard errors.
        self.assertAlmostEqual(r['b'], b, delta=0.03)

    def test_true_geometric_is_not_ruled_out(self):
        from gof import discrete_gr_gof
        rng = np.random.default_rng(2)
        q = 10 ** (-1.0 * 0.1)
        k = rng.geometric(1 - q, size=5000) - 1
        r = discrete_gr_gof(5.5 + k * 0.1, 5.5, 0.1, n_boot=200, seed=3)
        self.assertGreater(r['p_value'], 0.1)
        self.assertFalse(r['ruled_out'])

    def test_a_clearly_non_geometric_catalogue_is_ruled_out(self):
        from gof import discrete_gr_gof
        rng = np.random.default_rng(4)
        # Uniform magnitudes have no geometric tail at all.
        k = rng.integers(0, 30, size=4000)
        r = discrete_gr_gof(5.5 + k * 0.1, 5.5, 0.1, n_boot=200, seed=5)
        self.assertLessEqual(r['p_value'], 0.1)
        self.assertTrue(r['ruled_out'])

    def test_discrete_ks_is_zero_for_a_perfect_fit(self):
        from gof import discrete_ks, geometric_mle
        q = 0.7
        # Expected counts under the fitted q, scaled up so rounding is negligible.
        k = np.concatenate([[i] * int(round(200_000 * (1 - q) * q ** i)) for i in range(60)])
        self.assertLess(discrete_ks(k, geometric_mle(k)), 5e-3)

    def test_discrete_ks_does_not_apply_the_continuous_left_limit_correction(self):
        # Comparing F_emp(k-1) against F_fit(k) would compare across a jump and
        # report roughly the largest atom (here 1-q = 0.3) even on a perfect fit.
        from gof import discrete_ks, geometric_mle
        q = 0.7
        k = np.concatenate([[i] * int(round(200_000 * (1 - q) * q ** i)) for i in range(60)])
        self.assertLess(discrete_ks(k, geometric_mle(k)), 0.5 * (1 - q))

    def test_truncation_is_preferred_when_the_catalogue_is_truncated(self):
        from gof import discrete_gr_gof
        rng = np.random.default_rng(6)
        q = 10 ** (-1.0 * 0.1)
        k = rng.geometric(1 - q, size=30000) - 1
        k = k[k <= 20]
        r = discrete_gr_gof(5.5 + k * 0.1, 5.5, 0.1, n_boot=50, seed=7)
        self.assertLess(r['delta_aic_truncated'], 0)

    def test_too_few_events_is_refused(self):
        from gof import discrete_gr_gof
        with self.assertRaises(ValueError):
            discrete_gr_gof(np.array([5.6]), 5.5, 0.1)
