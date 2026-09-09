import unittest
import numpy as np
from meta import (random_effects, digit_preference, round_number_excess,
                  latent_shape, predicted_pass_fraction)


class RandomEffects(unittest.TestCase):
    def test_no_heterogeneity_gives_zero_tau_and_I2(self):
        # All estimates identical: Q = 0, so no excess variance to attribute.
        r = random_effects(np.full(20, -1.0), np.linspace(0.05, 0.3, 20))
        self.assertAlmostEqual(r['Q'], 0.0)
        self.assertEqual(r['tau_squared'], 0.0)
        self.assertEqual(r['I_squared'], 0.0)
        self.assertAlmostEqual(r['fixed_effect_mean'], -1.0)
        self.assertAlmostEqual(r['random_effects_mean'], -1.0)

    def test_hand_computed_two_study_case(self):
        # y = [0, 1], se = [1, 1] -> w = [1,1], mu = 0.5, Q = 0.25+0.25 = 0.5
        r = random_effects([0.0, 1.0], [1.0, 1.0])
        self.assertAlmostEqual(r['fixed_effect_mean'], 0.5)
        self.assertAlmostEqual(r['Q'], 0.5)
        self.assertEqual(r['df'], 1)
        self.assertEqual(r['tau_squared'], 0.0)   # Q < df, truncated at zero

    def test_large_heterogeneity_is_detected(self):
        rng = np.random.default_rng(0)
        se = np.full(200, 0.02)
        y = rng.normal(-1.0, 0.30, 200) + rng.normal(0, 0.02, 200)
        r = random_effects(y, se)
        self.assertGreater(r['I_squared'], 0.9)
        self.assertAlmostEqual(r['tau'], 0.30, delta=0.05)
        self.assertLess(r['Q_p_value'], 1e-6)

    def test_pure_sampling_noise_is_not_called_heterogeneous(self):
        rng = np.random.default_rng(3)
        se = np.full(400, 0.10)
        y = -1.0 + rng.normal(0, 0.10, 400)
        r = random_effects(y, se)
        self.assertLess(r['I_squared'], 0.25)
        self.assertLess(r['tau'], 0.05)

    def test_random_effects_interval_is_wider_than_fixed_when_heterogeneous(self):
        rng = np.random.default_rng(5)
        y = rng.normal(0, 0.5, 100)
        r = random_effects(y, np.full(100, 0.05))
        self.assertGreater(r['random_effects_se'], r['fixed_effect_se'])

    def test_degenerate_input_is_refused(self):
        with self.assertRaises(ValueError):
            random_effects([1.0], [0.1])
        with self.assertRaises(ValueError):
            random_effects([1.0, 2.0], [0.0, 0.0])


class ReportingArtefacts(unittest.TestCase):
    def test_uniform_digits_pass(self):
        v = np.array([-1 + d / 100 for d in range(10)] * 30)
        self.assertTrue(digit_preference(v)['uniform'])

    def test_rounding_to_tenths_is_detected(self):
        r = digit_preference(np.round(np.random.default_rng(1).normal(-1, .3, 500), 1))
        self.assertFalse(r['uniform'])
        self.assertLess(r['p_value'], 1e-6)

    def test_injected_spike_at_target_is_found(self):
        rng = np.random.default_rng(2)
        v = np.round(rng.normal(-1.0, 0.30, 4000), 2)
        v = np.concatenate([v, np.full(400, -1.00)])        # anchor on -1 only
        r = round_number_excess(v, target=-1.0)
        self.assertGreater(r['excess_at_target'], 3.0)
        self.assertEqual(r['rank_of_target'], 1)
        self.assertTrue(r['stands_out'])

    def test_generic_rounding_does_not_single_out_the_target(self):
        # Values rounded to tenths everywhere: every round value is inflated,
        # so the target must NOT stand out.
        rng = np.random.default_rng(4)
        v = np.concatenate([np.round(rng.normal(-1.0, .35, 3000), 2),
                            np.round(rng.normal(-1.0, .35, 1500), 1)])
        r = round_number_excess(v, target=-1.0)
        self.assertGreater(r['median_excess_elsewhere'], 1.5)
        self.assertFalse(r['stands_out'])

    def test_target_must_lie_on_the_step_grid(self):
        with self.assertRaises(ValueError):
            round_number_excess(np.round(np.linspace(-2, 0, 500), 2), target=-1.03)


if __name__ == '__main__':
    unittest.main()


class LatentShape(unittest.TestCase):
    """The observed spread is latent dispersion convolved with measurement error;
    these check that the deconvolution recovers the latent shape it was given."""

    def setUp(self):
        self.rng = np.random.default_rng(0)
        self.se = np.abs(self.rng.normal(.1, .03, 800)) + .02

    def _obs(self, latent):
        return latent + self.rng.normal(0, self.se)

    def test_quadrature_converges_to_the_closed_form_gaussian(self):
        # The Gaussian case is closed form; every other family goes through
        # quadrature. A Student t tends to a Gaussian as nu grows, so the
        # quadrature path must converge to the closed form monotonically.
        from meta import _loglik
        y = self.rng.normal(-1, .3, 200)
        se = np.full(200, .12)
        exact = _loglik(y, se, -1.0, .25, 'gaussian')
        gaps = [abs(_loglik(y, se, -1.0, .25, 'student_t', nu=nu) - exact)
                for nu in (10, 50, 400, 5000)]
        self.assertTrue(all(b < a for a, b in zip(gaps, gaps[1:])),
                        f'gaps should shrink with nu, got {gaps}')
        self.assertLess(gaps[-1], abs(exact) * 1e-3)

    def test_gaussian_latent_is_recovered(self):
        r = latent_shape(self._obs(self.rng.normal(-1, .25, 800)), self.se)
        self.assertEqual(r['best_family'], 'gaussian')
        self.assertTrue(r['maxent_consistent'])
        self.assertAlmostEqual(r['families']['gaussian']['tau'], .25, delta=.04)
        self.assertAlmostEqual(r['families']['gaussian']['mu'], -1.0, delta=.04)
        self.assertLess(abs(r['gaussian_standardised_residuals']['excess_kurtosis']), .5)

    def test_heavy_tailed_latent_is_not_called_gaussian(self):
        lat = -1 + .25 * self.rng.standard_t(3, 800) / np.sqrt(3.)
        r = latent_shape(self._obs(lat), self.se)
        self.assertNotEqual(r['best_family'], 'gaussian')
        self.assertFalse(r['maxent_consistent'])
        self.assertGreater(r['gaussian_standardised_residuals']['excess_kurtosis'], 1.0)

    def test_laplace_latent_is_recovered(self):
        lat = -1 + self.rng.laplace(0, .25 / np.sqrt(2.), 800)
        r = latent_shape(self._obs(lat), self.se)
        self.assertEqual(r['best_family'], 'laplace')


class PassFraction(unittest.TestCase):
    def test_one_sigma_tolerance_gives_the_normal_68_percent(self):
        r = predicted_pass_fraction([0.25], tau=0.25)
        self.assertAlmostEqual(r['mean_predicted_fraction'], 0.6827, places=3)

    def test_two_sigma_tolerance_gives_95_percent(self):
        r = predicted_pass_fraction([1.96 * 0.25], tau=0.25)
        self.assertAlmostEqual(r['mean_predicted_fraction'], 0.95, places=3)

    def test_tight_tolerance_predicts_widespread_individual_failure(self):
        # This is the point: a correct ensemble claim predicts most systems fail.
        r = predicted_pass_fraction([0.03], tau=0.25)
        self.assertLess(r['mean_predicted_fraction'], 0.12)

    def test_heavier_tails_put_more_mass_near_the_centre(self):
        g = predicted_pass_fraction([0.05], tau=0.25, family='gaussian')
        l = predicted_pass_fraction([0.05], tau=0.25, family='laplace')
        self.assertGreater(l['mean_predicted_fraction'], g['mean_predicted_fraction'])

    def test_bad_input_is_refused(self):
        with self.assertRaises(ValueError):
            predicted_pass_fraction([0.1], tau=0)
        with self.assertRaises(ValueError):
            predicted_pass_fraction([0.1], tau=0.2, family='student_t', nu=1.5)
