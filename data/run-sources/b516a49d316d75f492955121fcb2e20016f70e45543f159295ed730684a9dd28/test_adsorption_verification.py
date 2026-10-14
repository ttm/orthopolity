"""Synthetic checks of the independently implemented adsorption verifier."""
import importlib.util
from pathlib import Path
import unittest

import numpy as np
from orthopolity import adsorption


SPEC = importlib.util.spec_from_file_location(
    "independent_adsorption", Path(__file__).parents[1] / "experiments/verify_adsorption.py")
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)
TC = [304.1282, 190.564]
PC = [73.773, 45.99]
OMEGA = [0.22394, 0.01142]


class IndependentAdsorptionTest(unittest.TestCase):
    def test_fugacity_has_ideal_limit_and_euler_identity(self):
        y = np.array([0.4, 0.6])
        np.testing.assert_allclose(VERIFY.pr_fugacity_coefficients(0, 320, y, TC, PC, OMEGA), 1)
        np.testing.assert_allclose(VERIFY.pr_fugacity_coefficients(1e-5, 320, y, TC, PC, OMEGA),
                                   1, rtol=1e-7)
        for pressure in [0.1, 10, 50, 100]:
            phi = VERIFY.pr_fugacity_coefficients(pressure, 320, y, TC, PC, OMEGA)
            gibbs = VERIFY.residual_gibbs_rt(pressure, 320, y, TC, PC, OMEGA)
            self.assertAlmostEqual(np.dot(y, np.log(phi)), gibbs, delta=2e-10)

    def test_fugacity_identical_species_and_component_exchange(self):
        same = VERIFY.pr_fugacity_coefficients(50, 320, [0.3, 0.7],
                                               [TC[0]] * 2, [PC[0]] * 2, [OMEGA[0]] * 2)
        pure_gibbs = VERIFY.residual_gibbs_rt(50, 320, [1], TC[:1], PC[:1], OMEGA[:1])
        np.testing.assert_allclose(same, np.exp(pure_gibbs), rtol=2e-9)
        original = VERIFY.pr_fugacity_coefficients(30, 310, [0.2, 0.8], TC, PC, OMEGA, .09)
        reverse = VERIFY.pr_fugacity_coefficients(
            30, 310, [.8, .2], TC[::-1], PC[::-1], OMEGA[::-1], .09)
        np.testing.assert_allclose(original, reverse[::-1], atol=2e-10, rtol=0)

    def test_fugacity_derivative_refinement_including_zero_species(self):
        for composition in [[0, 1], [1, 0], [1e-5, .99999], [.5, .5]]:
            with self.subTest(composition=composition):
                coarse = VERIFY.pr_fugacity_coefficients(50, 320, composition, TC, PC, OMEGA)
                fine = VERIFY.pr_fugacity_coefficients(
                    50, 320, composition, TC, PC, OMEGA, step=1e-4)
                np.testing.assert_allclose(coarse, fine, rtol=2e-8)

    def test_iast_common_capacity_matches_competitive_langmuir(self):
        f, affinity, capacity = np.array([3., 7.]), np.array([.8, .15]), 4.
        result = VERIFY.iast_binary(f, [capacity] * 2, affinity)
        expected = capacity * affinity * f / (1 + np.dot(affinity, f))
        np.testing.assert_allclose(result["loadings"], expected, rtol=2e-12)

    def test_iast_unequal_capacity_satisfies_spreading_and_volume_relations(self):
        f, q, b = np.array([10., 1.]), np.array([8., 3.]), np.array([.1, 1.])
        result = VERIFY.iast_binary(f, q, b)
        x, fictive = result["adsorbed_fraction"], result["fictive_fugacities"]
        spreading = q * np.log1p(b * fictive)
        np.testing.assert_allclose(spreading[0], spreading[1], rtol=1e-12)
        np.testing.assert_allclose(x * fictive, f, rtol=1e-12)
        pure = q * b * fictive / (1 + b * fictive)
        self.assertAlmostEqual(sum(result["loadings"]), 1 / np.sum(x / pure))
        reverse = VERIFY.iast_binary(f[::-1], q[::-1], b[::-1])
        np.testing.assert_allclose(result["loadings"], reverse["loadings"][::-1], rtol=1e-12)

    def test_iast_zero_and_pure_limits(self):
        q, b = np.array([4., 7.]), np.array([.3, .5])
        for f in [[0, 0], [0, 5], [5, 0]]:
            with self.subTest(f=f):
                result = VERIFY.iast_binary(f, q, b)
                np.testing.assert_allclose(result["loadings"], q * b * f / (1 + b * f))

    def test_variable_projection_recovers_synthetic_pure_fits(self):
        for common in [True, False]:
            with self.subTest(common=common):
                f = [np.geomspace(.01, 100, 35), np.geomspace(.02, 80, 30)]
                capacities = np.array([4., 4. if common else 7.])
                affinities = np.array([.4, .1])
                observed = [q * b * x / (1 + b * x)
                            for q, b, x in zip(capacities, affinities, f)]
                result = VERIFY.independent_langmuir_fit(f, observed, common_capacity=common)
                np.testing.assert_allclose(result["capacities"], capacities, rtol=1e-6)
                np.testing.assert_allclose(result["affinities"], affinities, rtol=1e-6)
                self.assertLess(result["objective"], 1e-10)

    def test_invalid_inputs_are_rejected(self):
        with self.assertRaises(ValueError):
            VERIFY.pr_fugacity_coefficients(-1, 320, [.5, .5], TC, PC, OMEGA)
        with self.assertRaises(ValueError):
            VERIFY.iast_binary([1, 1], [-1, 1], [1, 1])
        with self.assertRaises(ValueError):
            VERIFY.independent_langmuir_fit([[0, 0]], [[1, 2]])

    def test_independent_fugacity_matches_analytic_implementation_on_synthetic_states(self):
        constants = np.column_stack((TC, np.array(PC) * 1e5, OMEGA))
        for temperature in [298., 333., 353.]:
            for pressure in [.001, .1, 1., 2.5]:
                for composition in [[1., 0.], [0., 1.], [.1, .9], [.5, .5], [.9, .1]]:
                    with self.subTest(T=temperature, P=pressure, y=composition):
                        phi = VERIFY.pr_fugacity_coefficients(
                            pressure * 10, temperature, composition, TC, PC, OMEGA)
                        expected = pressure * np.array(composition) * phi
                        np.testing.assert_allclose(
                            adsorption.fugacity(temperature, pressure, composition, constants),
                            expected, rtol=2e-9, atol=2e-11)

    def test_independent_iast_matches_spreading_pressure_solver_on_synthetic_cases(self):
        for f in [[.01, .02], [10, 1], [1, 10], [5, 5]]:
            for q in [[4, 4], [8, 3], [3, 8]]:
                with self.subTest(f=f, q=q):
                    independent = VERIFY.iast_binary(f, q, [.1, 1.])
                    loadings, fictive = adsorption.iast(f, q, [.1, 1.])
                    np.testing.assert_allclose(independent['loadings'], loadings, rtol=1e-9)
                    np.testing.assert_allclose(independent['fictive_fugacities'], fictive, rtol=1e-9)

    def test_independent_weighted_fit_matches_nonlinear_fit_on_synthetic_noise(self):
        f = [np.geomspace(.01, 20, 21), np.geomspace(.02, 15, 24)]
        q = [4 * .7 * f[0] / (1 + .7 * f[0]), 4 * .13 * f[1] / (1 + .13 * f[1])]
        observed = [a + .005 * np.sin(np.arange(len(a))) for a in q]
        expanded_u = [np.linspace(.02, .08, len(a)) for a in q]
        for shared in [True, False]:
            with self.subTest(shared=shared):
                independent = VERIFY.independent_langmuir_fit(
                    f, observed, [u / 2 for u in expanded_u], common_capacity=shared,
                    capacity_bounds=(1e-3, 1e3), affinity_bounds=(1e-6, 1e6))
                direct = adsorption.fit_pure(f, observed, expanded_u, shared=shared)
                np.testing.assert_allclose(independent['capacities'], direct['capacities'], rtol=2e-6)
                np.testing.assert_allclose(independent['affinities'], direct['affinities'], rtol=2e-6)
                self.assertAlmostEqual(independent['objective'], direct['weighted_sse'], delta=1e-8)

    def test_analytic_diagnostics_match_synthetic_fit(self):
        f = [np.geomspace(.01,10,20)]*2
        q = [adsorption.langmuir(x,4,b) for x,b in zip(f,[2,.5])]
        u = [np.full(20,.02)]*2
        direct = adsorption.fit_pure(f,q,u)
        checked = VERIFY.fit_diagnostics(f,q,[x/2 for x in u],direct)
        self.assertTrue(checked['locally_identified'])
        self.assertTrue(checked['pure_fit_adequate'])
        np.testing.assert_allclose(checked['jacobian_condition'],direct['jacobian_condition'],rtol=1e-6)
        np.testing.assert_allclose(checked['parameter_correlation'],direct['parameter_correlation'],rtol=1e-5,atol=1e-8)
