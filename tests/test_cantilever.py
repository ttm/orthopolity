"""Synthetic physics checks; no empirical cantilever response is loaded."""
import json
import unittest

import numpy as np
from scipy.integrate import quad

from orthopolity.cantilever import (
    fit_loss, mode_moments, predict_loss, predict_temperature,
)


class CantileverMomentsTest(unittest.TestCase):
    def test_torsional_first_moment_analytic(self):
        for index in (1, 2, 5):
            moments = mode_moments("torsional", index)
            wave_number = (index - .5) * np.pi
            self.assertAlmostEqual(moments[1], .5 - 1 / (2 * wave_number**2), places=13)
            self.assertEqual(moments[0], 1.)
            self.assertTrue(np.all(np.diff(moments) < 0))

    def test_flexural_quadrature_and_independent_direct_shape(self):
        # Published mathematical roots, not fitted experimental inputs.
        for index, beta in ((1, 1.875104068711961), (5, 14.13716839104647)):
            ratio = (np.cosh(beta) + np.cos(beta)) / (np.sinh(beta) + np.sin(beta))

            def strain(z):
                return (np.cosh(beta*z) + np.cos(beta*z)
                        - ratio * (np.sinh(beta*z) + np.sin(beta*z)))

            norm = quad(lambda z: strain(z)**2, 0, 1, epsabs=1e-11)[0]
            direct = [quad(lambda z: z**r * strain(z)**2, 0, 1,
                           epsabs=1e-11)[0] / norm for r in range(4)]
            np.testing.assert_allclose(mode_moments("flexural", index), direct,
                                       rtol=1e-10, atol=1e-12)
            np.testing.assert_allclose(mode_moments("flexural", index, order=64),
                                       mode_moments("flexural", index, order=512),
                                       rtol=1e-12, atol=1e-13)

    def test_invalid_mode_specifications(self):
        for args in (("other", 1, 256), ("torsional", 0, 256),
                     ("flexural", True, 256), ("flexural", 1.5, 256),
                     ("flexural", 1, 4)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                mode_moments(*args)


class CantileverFitTest(unittest.TestCase):
    def setUp(self):
        self.mu = mode_moments("flexural", 2)
        self.delta = np.array([0., 20., 40., 60., 80., 100.])
        self.sigma = np.full(6, 1e-7)

    def test_known_local_law_recovers_heldout_fluctuations(self):
        # Integrate an independently specified, positive local law directly.
        mu = mode_moments("torsional", 1)
        local = [1e-5, 2e-8, 3e-11]
        coefficients = np.array(local) * np.array([1., mu[1], mu[2]])
        fit = fit_loss(self.delta, predict_loss(self.delta, coefficients),
                       self.sigma, mu, 300.)
        self.assertTrue(fit["admissible"])
        np.testing.assert_allclose(fit["coefficients"], coefficients, rtol=1e-11)
        for delta in (160., 300.):
            def weight(z):
                return (local[0] + local[1]*delta*z + local[2]*(delta*z)**2) * (
                    1 + np.cos(np.pi*z))

            direct = quad(lambda z: (300. + delta*z) * weight(z), 0, 1)[0] / quad(weight, 0, 1)[0]
            self.assertAlmostEqual(predict_temperature(delta, fit["coefficients"], mu, t0=300.),
                                   direct, places=10)
        json.dumps(fit, allow_nan=False)

    def test_weighted_fit_matches_independent_normal_equations(self):
        y = np.array([1., 1.03, 1.07, 1.20, 1.29, 1.48]) * 1e-5
        sigma = self.sigma * np.array([1., 2., 1., 3., 2., 1.])
        fit = fit_loss(self.delta, y, sigma, self.mu, 200.)
        design = np.column_stack((np.ones(6), self.delta/200., (self.delta/200.)**2))
        inverse_variance = np.diag(1 / sigma**2)
        beta = np.linalg.solve(design.T @ inverse_variance @ design,
                               design.T @ inverse_variance @ y)
        expected = beta / np.array([1., 200., 200.**2])
        np.testing.assert_allclose(fit["coefficients"], expected, rtol=1e-11, atol=1e-18)
        self.assertEqual(fit["train_diagnostics"]["degrees_of_freedom"], 3)

    def test_negative_local_interior_despite_positive_global_loss(self):
        # local(u)=(u-.4)^2-.01 has positive endpoints and a negative vertex.
        mu = np.array([1., .5, 1/3, .25])
        delta = np.linspace(0, 1, 8)
        coefficients = [.15, -.8*mu[1], mu[2]]
        y = predict_loss(delta, coefficients)
        self.assertTrue(np.all(y > 0))
        fit = fit_loss(delta, y, np.full(8, .001), mu, 1.)
        self.assertTrue(fit["eligible"])
        self.assertFalse(fit["admissible"])
        self.assertGreater(fit["global_minimum"], 0)
        self.assertAlmostEqual(fit["local_minimum"], -.01, places=13)
        self.assertAlmostEqual(fit["local_minimum_location"], .4, places=13)
        self.assertIn("negative_local_loss_on_prediction_domain", fit["reasons"])

    def test_hot_domain_can_defeat_a_training_valid_loss(self):
        mu = np.array([1., .5, 1/3, .25])
        delta = np.linspace(0, .5, 6)
        y = predict_loss(delta, [1., -.5, 0.])
        train_domain = fit_loss(delta, y, np.ones(6), mu, .5)
        hot_domain = fit_loss(delta, y, np.ones(6), mu, 3.)
        self.assertTrue(train_domain["admissible"])
        self.assertFalse(hot_domain["admissible"])
        self.assertIn("nonpositive_global_loss_on_prediction_domain", hot_domain["reasons"])
        self.assertAlmostEqual(hot_domain["local_minimum"], -2., places=11)

    def test_loss_units_do_not_change_admissibility_or_temperature(self):
        y = predict_loss(self.delta, [1e-5, 2e-8, 3e-11])
        original = fit_loss(self.delta, y, self.sigma, self.mu, 300.)
        scaled = fit_loss(self.delta, y * 1e-12, self.sigma * 1e-12, self.mu, 300.)
        self.assertEqual(original["admissible"], scaled["admissible"])
        np.testing.assert_allclose(predict_temperature([150., 300.], original["coefficients"], self.mu),
                                   predict_temperature([150., 300.], scaled["coefficients"], self.mu),
                                   rtol=1e-13)

    def test_invalid_rows_fail_without_silent_deletion(self):
        for field, value in (("delta", -1.), ("delta", np.nan), ("phi", 0.),
                             ("phi", np.inf), ("sigma", 0.), ("sigma", np.nan)):
            inputs = dict(delta=self.delta.copy(), phi=np.ones(6), sigma=self.sigma.copy())
            inputs[field][0] = value
            with self.subTest(field=field, value=value):
                fit = fit_loss(**inputs, moments=self.mu, domain_max=300.)
                self.assertFalse(fit["eligible"])
                self.assertIsNone(fit["coefficients"])
                self.assertTrue(fit["reasons"])
                json.dumps(fit, allow_nan=False)

    def test_sample_size_rank_and_domain_requirements(self):
        cases = [([0., 1., 2.], [1.]*3, [1.]*3, 3.),
                 ([0., 0., 1., 1.], [1.]*4, [1.]*4, 3.),
                 ([0., 1., 2., 3.], [1.]*4, [1.]*4, 2.),
                 ([0., 1., 2., 3.], [1.]*4, [1.]*4, np.inf)]
        for delta, y, sigma, domain in cases:
            with self.subTest(delta=delta, domain=domain):
                fit = fit_loss(delta, y, sigma, self.mu, domain)
                self.assertFalse(fit["eligible"])
                json.dumps(fit, allow_nan=False)

    def test_withheld_arrays_cannot_enter_calibration(self):
        # Alter both future observables; fitting is supplied only calibration rows.
        delta = np.arange(11.) * 20
        loss = predict_loss(delta, [1e-5, 2e-8, 1e-11])
        fluctuation = np.linspace(295., 500., 11)
        before = fit_loss(delta[:8], loss[:8], np.full(8, 1e-7), self.mu, delta[-1])
        loss[8:] *= 100
        fluctuation[:] = -1e20
        after = fit_loss(delta[:8], loss[:8], np.full(8, 1e-7), self.mu, delta[-1])
        self.assertEqual(before, after)


class CantileverPredictionTest(unittest.TestCase):
    def test_constant_loss_is_geometry_comparator_and_baseline_is_exact(self):
        mu = mode_moments("flexural", 1)
        delta = np.array([0., 100., 400.])
        np.testing.assert_allclose(predict_temperature(delta, [2., 0., 0.], mu, t0=300.),
                                   300. + delta * mu[1], rtol=1e-14)
        self.assertEqual(predict_temperature(0., [2., 3., 4.], mu, t0=300.), 300.)

    def test_unphysical_finite_prediction_is_preserved_not_clipped(self):
        mu = np.array([1., .5, 1/3, .25])
        # Local loss 1-2z, with a small positive global denominator.
        prediction = predict_temperature(1., [1., -.9, 0.], mu)
        self.assertLess(prediction, 295.)
        self.assertEqual(predict_loss(3., [1., -1., 0.]), -2.)

    def test_prediction_rejects_undefined_inputs(self):
        mu = mode_moments("torsional", 1)
        for delta, coefficients in ((-1., [1., 0., 0.]), (1., [1., -1., 0.]),
                                    (np.nan, [1., 0., 0.])):
            with self.subTest(delta=delta), self.assertRaises(ValueError):
                predict_temperature(delta, coefficients, mu)


if __name__ == "__main__":
    unittest.main()
