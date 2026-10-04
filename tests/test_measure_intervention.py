"""Independent integration and invariances of conditional measure forecasts."""
import math
import unittest

import numpy as np
from scipy.integrate import quad

from orthopolity.measure_intervention import measure_forecasts


class MeasureInterventionChecks(unittest.TestCase):
    def test_closed_forms_match_independent_density_quadrature(self):
        edges = [.4, .9, 1.7, 4., 9.]
        for degree in (.5, 1., 3.2):
            for overhead in (0., 1e-10, .8, 20.):
                with self.subTest(degree=degree, overhead=overhead):
                    budget, q0, scale = 7., 2.3, 1.4
                    result = measure_forecasts(edges, degree=degree, overhead=overhead,
                                              budget=budget, cost_scale=q0, size_scale=scale)
                    log_span = math.log(edges[-1] / edges[0])
                    cost_span = math.log(((edges[-1] / scale)**degree + overhead)
                                         / ((edges[0] / scale)**degree + overhead))
                    def variable_cost(x):
                        return (math.exp(x) / scale)**degree
                    densities = {
                        "log_size": lambda x: budget / log_span,
                        "log_cost": lambda x: budget / cost_span * degree
                        * variable_cost(x) / (variable_cost(x) + overhead),
                    }
                    for model, density in densities.items():
                        resources, counts = [], []
                        for lo, hi in zip(edges, edges[1:]):
                            bounds = math.log(lo), math.log(hi)
                            resources.append(quad(density, *bounds, epsabs=1e-11, epsrel=1e-11)[0])
                            counts.append(quad(lambda x: density(x) / (q0 * (variable_cost(x) + overhead)),
                                               *bounds, epsabs=1e-11, epsrel=1e-11)[0])
                        np.testing.assert_allclose(result[model]["resource_totals"], resources, rtol=1e-11)
                        np.testing.assert_allclose(result[model]["count_totals"], counts, rtol=1e-11)

    def test_zero_overhead_hypotheses_are_exactly_equal(self):
        result = measure_forecasts([1., 1.5, 3., 11.], degree=2.7, budget=9., cost_scale=3.)
        self.assertEqual(result["log_size"], result["log_cost"])
        result["log_size"]["count_totals"][0] = 0.
        self.assertGreater(result["log_cost"]["count_totals"][0], 0.)

    def test_coarsening_adds_unnormalized_counts_and_stocks(self):
        options = dict(degree=2.2, overhead=7., budget=13., cost_scale=.8)
        fine = measure_forecasts([1., 1.6, 2.5, 4., 8.], **options)
        coarse = measure_forecasts([1., 2.5, 8.], **options)
        for model in fine:
            for field in ("resource_totals", "count_totals", "resource_shares", "count_shares"):
                values = fine[model][field]
                np.testing.assert_allclose(coarse[model][field], [sum(values[:2]), sum(values[2:])], rtol=2e-14)

    def test_size_units_change_with_reference_scale(self):
        edges = [.5, 1., 2., 8.]
        reference = measure_forecasts(edges, degree=1.7, overhead=3., size_scale=.75)
        converted = measure_forecasts([k * 1e6 for k in edges], degree=1.7, overhead=3., size_scale=.75e6)
        for model in reference:
            for field in reference[model]:
                np.testing.assert_allclose(converted[model][field], reference[model][field], rtol=2e-14)

    def test_resource_units_preserve_counts_and_all_shares(self):
        reference = measure_forecasts([1., 3., 7.], degree=3., overhead=5., budget=9., cost_scale=.4)
        converted = measure_forecasts([1., 3., 7.], degree=3., overhead=5., budget=9000., cost_scale=400.)
        for model in reference:
            for field in ("count_totals", "count_shares", "total_count", "resource_shares"):
                np.testing.assert_allclose(converted[model][field], reference[model][field], rtol=2e-14)
            np.testing.assert_allclose(converted[model]["resource_totals"],
                                       np.array(reference[model]["resource_totals"]) * 1000., rtol=2e-14)

    def test_finite_overhead_cost_measure_predicts_fewer_total_objects(self):
        for degree in (.3, 1., 4.):
            for overhead in (.01, 1., 100.):
                with self.subTest(degree=degree, overhead=overhead):
                    result = measure_forecasts([1., 2., 4., 8.], degree=degree, overhead=overhead, budget=10.)
                    self.assertLess(result["log_cost"]["total_count"], result["log_size"]["total_count"])
                    for model in result.values():
                        self.assertAlmostEqual(model["total_resource"], 10.)
                        self.assertAlmostEqual(sum(model["count_shares"]), 1.)
                        self.assertGreater(model["total_count"], 10. / (8.**degree + overhead))
                        self.assertLess(model["total_count"], 10. / (1. + overhead))

    def test_large_overhead_has_distinct_fixed_bin_shapes(self):
        edges, degree, overhead = [1., 2., 4., 8.], 2., 1e20
        result = measure_forecasts(edges, degree=degree, overhead=overhead, budget=3.)
        size_shape = np.array([math.log(hi / lo) for lo, hi in zip(edges, edges[1:])]) / math.log(8.)
        cost_shape = np.diff(np.array(edges)**degree) / (8.**degree - 1.)
        for field in ("resource_shares", "count_shares"):
            np.testing.assert_allclose(result["log_size"][field], size_shape, rtol=2e-14)
            np.testing.assert_allclose(result["log_cost"][field], cost_shape, rtol=2e-14)
        for model in result.values():
            self.assertAlmostEqual(model["total_count"] * overhead / 3., 1.)

    def test_tiny_overhead_is_continuous_at_baseline(self):
        baseline = measure_forecasts([.2, 1., 7.], degree=2.3)
        for overhead in (1e-15, 1e-200, 5e-324):
            result = measure_forecasts([.2, 1., 7.], degree=2.3, overhead=overhead)
            for model in baseline:
                for field in baseline[model]:
                    np.testing.assert_allclose(result[model][field], baseline[model][field], rtol=1e-12)

    def test_narrow_positive_bins_are_not_lost_to_log_subtraction(self):
        result = measure_forecasts([1., 1. + 1e-12, 1. + 2e-12], degree=1., overhead=1e20)
        for model in result.values():
            self.assertTrue(all(value > 0 for value in model["resource_shares"]))
            self.assertAlmostEqual(model["total_resource"], 1.)
            self.assertAlmostEqual(model["total_count"] * 1e20, 1.)

    def test_rejects_invalid_scalars_edges_and_numerical_overflow(self):
        for field in ("degree", "budget", "cost_scale", "size_scale", "overhead"):
            invalid = [True, "1", complex(1, 0), math.nan, math.inf, -1.]
            if field != "overhead":
                invalid.append(0.)
            for value in invalid:
                options = dict(degree=1.)
                options[field] = value
                with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                    measure_forecasts([1., 2.], **options)
        for edges in ([], [1.], [1., 1.], [2., 1.], [0., 1.], [1., math.inf],
                      [True, 2.], ["1", "2"], [[1.], [2.]], None, 5.):
            with self.subTest(edges=edges), self.assertRaises(ValueError):
                measure_forecasts(edges, degree=1.)
        for options in (dict(degree=1000.), dict(degree=2., cost_scale=1e308),
                        dict(degree=1., budget=1e308, cost_scale=1e-308),
                        dict(degree=1., size_scale=5e-324)):
            with self.subTest(options=options), self.assertRaises(ValueError):
                measure_forecasts([1., 10.], **options)


if __name__ == "__main__":
    unittest.main()
