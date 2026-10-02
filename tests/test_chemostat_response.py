"""Resource-response tests use analytic examples, never validation observations."""
import unittest

import numpy as np

from orthopolity.chemostat_response import (
    baseline_anchored_forecast, common_comparison_support, fractional_trajectory,
    interpolate_trajectory, mean_unit_trajectory, pooled_profile_envelope,
    profile_tv_envelope, recovery_endpoint, resource_profile, simplex_projection,
    stock_forecast, trajectory_scores, whole_unit_partition,
)


class ChemostatResponseChecks(unittest.TestCase):
    def test_density_translation_and_scale_invariant_composition(self):
        result = resource_profile([2., 3., 5.], [3., 2., 1.])
        np.testing.assert_allclose(result['stocks'], [6., 6., 5.])
        np.testing.assert_allclose(result['shares'], np.array([6., 6., 5.])/17.)
        self.assertEqual(result['total'], 17.)
        np.testing.assert_allclose(resource_profile([4., 6., 10.], [3., 2., 1.])['shares'], result['shares'])

    def test_zero_groups_zero_totals_and_missing_groups_remain_distinct(self):
        result = resource_profile([[0., 2.], [0., 0.], [np.nan, 2.]], [1., 3.])
        np.testing.assert_allclose(result['shares'][0], [0., 1.])
        self.assertEqual(result['total'][1], 0.)
        self.assertTrue(np.all(np.isnan(result['shares'][1:])))
        np.testing.assert_array_equal(result['valid'], [True, False, False])
        self.assertTrue(np.isnan(result['total'][2]))

    def test_invalid_costs_negative_data_and_infinity_are_rejected(self):
        for volumes, density in [([1., -1.], [1., 2.]), ([1., np.inf], [1., 2.]),
                                 ([1., 2.], [0., 1.]), ([1., 2.], [np.nan, 1.]),
                                 ([1., 2.], [1.])]:
            with self.subTest(volumes=volumes, density=density), self.assertRaises(ValueError):
                resource_profile(volumes, density)

    def test_unknown_pooled_mixture_has_exact_monotone_coordinate_bounds(self):
        result = pooled_profile_envelope([2., 3., 4.], [1., 2., 999.], 2, [1., 3.])
        endpoints = np.array([[2., 6., 4.], [2., 6., 12.]])
        endpoints /= endpoints.sum(axis=1)[:, None]
        np.testing.assert_allclose(result['endpoint_shares'], endpoints)
        np.testing.assert_allclose(result['lower'], [0.1, 0.3, 1./3.])
        np.testing.assert_allclose(result['upper'], [1./6., .5, .6])
        for rho in np.linspace(1., 3., 27):
            shares = resource_profile([2., 3., 4.], [1., 2., rho])['shares']
            self.assertTrue(np.all(shares >= result['lower']-1e-14))
            self.assertTrue(np.all(shares <= result['upper']+1e-14))
        self.assertAlmostEqual(result['total_lower'], 12.)
        self.assertAlmostEqual(result['total_upper'], 20.)

    def test_tv_sensitivity_minimum_can_be_inside_pooled_interval(self):
        forecast = resource_profile([1., 1.], [1., 2.])['shares']
        result = profile_tv_envelope(forecast, [1., 1.], [1., 99.], 1, [1., 4.])
        self.assertAlmostEqual(result['lower'], 0.)
        self.assertGreater(min(result['endpoint_scores']), 0.)
        self.assertAlmostEqual(result['upper'], 1./6.)
        self.assertTrue(0 < result['minimum_segment_position'] < 1)

    def test_simplex_projection_preserves_feasible_zeros_and_reports_correction(self):
        np.testing.assert_array_equal(simplex_projection([0., .3, .7]), [0., .3, .7])
        forecast = baseline_anchored_forecast([0., .3, .7], [-.1, .1, 0.])
        np.testing.assert_allclose(forecast['unprojected'], [-.1, .4, .7])
        np.testing.assert_allclose(forecast['shares'], [0., .35, .65])
        self.assertGreater(forecast['projection_distance'], 0.)
        emergence = baseline_anchored_forecast([0., 1.], [.2, -.2])
        np.testing.assert_allclose(emergence['shares'], [.2, .8])
        with self.assertRaises(ValueError):
            baseline_anchored_forecast([.3, .7], [.1, .1])

    def test_initial_state_forecast_is_not_aliased_or_fitted_from_outcome(self):
        initial = np.array([.4, .6])
        change = np.array([.1, -.1])
        forecast = baseline_anchored_forecast(initial, change)
        forecast['shares'][0] = 99.
        np.testing.assert_array_equal(initial, [.4, .6])
        np.testing.assert_array_equal(change, [.1, -.1])

    def test_total_factor_and_shares_jointly_conserve_predicted_stock(self):
        forecast = stock_forecast([2., 3.], [3., 2.], [.1, -.1], 1.5)
        self.assertEqual(forecast['baseline_total'], 12.)
        self.assertEqual(forecast['total'], 18.)
        np.testing.assert_allclose(forecast['stocks'], [10.8, 7.2])
        self.assertAlmostEqual(np.sum(forecast['stocks']), forecast['total'])
        for total in [0., -1., np.nan, np.inf]:
            with self.assertRaises(ValueError):
                stock_forecast([2., 3.], [3., 2.], [.1, -.1], total)

    def test_fractional_trajectory_uses_total_initial_stock_not_group_divisors(self):
        result = fractional_trajectory([0., 1., 2.], [[0., 2.], [1., 1.], [0., 4.]],
                                       [1., 2.], [0., 2.])
        np.testing.assert_allclose(result['share_change'], [[0., 0.], [1./3., -1./3.], [0., 0.]])
        np.testing.assert_allclose(result['total_factor'], [1., .75, 2.])

    def test_interpolation_does_not_extrapolate_or_bridge_missing_data(self):
        result = interpolate_trajectory([0., 1., 2., 3.], [[0., 0.], [1., np.nan], [2., 2.], [3., 3.]],
                                        [-1., 0., .5, 1.5, 2.5, 4.])
        self.assertTrue(np.all(np.isnan(result[[0, 5]])))
        np.testing.assert_array_equal(result[1], [0., 0.])
        self.assertTrue(np.isnan(result[2, 1]))
        self.assertTrue(np.isnan(result[3, 1]))
        np.testing.assert_allclose(result[4], [2.5, 2.5])

    def test_training_mean_weights_units_equally_not_their_sample_counts(self):
        units = [dict(unit_id='dense', times=[0., .5, 1.], values=[[1., -1.], [1., -1.], [1., -1.]]),
                 dict(unit_id='sparse', times=[0., 1.], values=[[3., -3.], [3., -3.]])]
        result = mean_unit_trajectory(units, [0., .5, 1., 2.])
        np.testing.assert_allclose(result['mean'][:3], [[2., -2.]]*3)
        np.testing.assert_array_equal(result['contributors'], [2, 2, 2, 0])
        self.assertTrue(np.all(np.isnan(result['mean'][3])))
        with self.assertRaises(ValueError):
            mean_unit_trajectory(units+[units[0]], [0., 1.])

    def test_category_partition_uses_whole_units_and_reports_unknown_categories(self):
        metadata = [dict(unit_id='v2', category='poly'), dict(unit_id='v1', category='mono'),
                    dict(unit_id='other', category='unknown')]
        self.assertEqual(whole_unit_partition(metadata, 'mono', 'poly'),
                         dict(development=['v1'], validation=['v2'], unsupported=['other']))
        with self.assertRaises(ValueError):
            whole_unit_partition(metadata+[metadata[0]], 'mono', 'poly')
        with self.assertRaises(ValueError):
            whole_unit_partition(metadata, 'mono', 'mono')

    def test_time_weighted_tv_uses_actual_intervals_not_unweighted_rows(self):
        observed = [[1., 0.], [.5, .5], [0., 1.]]
        predicted = [[1., 0.]]*3
        result = trajectory_scores([0., 1., 3.], predicted, observed)
        np.testing.assert_allclose(result['total_variation'], [0., .5, 1.])
        self.assertAlmostEqual(result['time_weighted_total_variation'], 7./12.)
        self.assertEqual(result['covered_duration'], 3.)
        np.testing.assert_allclose(result['signed_share_error'][-1], [1., -1.])

    def test_missing_row_breaks_score_exposure_instead_of_bridging_it(self):
        observed = [[1., 0.], [np.nan, np.nan], [0., 1.], [0., 1.]]
        result = trajectory_scores([0., 1., 2., 4.], [[1., 0.]]*4, observed)
        self.assertEqual(result['scored_observations'], 3)
        self.assertEqual(result['invalid_observations'], 1)
        self.assertEqual(result['covered_duration'], 2.)
        self.assertEqual(result['time_weighted_total_variation'], 1.)
        point = trajectory_scores([1.], [[1., 0.]], [[0., 1.]])
        self.assertIsNone(point['time_weighted_total_variation'])

    def test_comparators_use_one_common_observation_support(self):
        observed = [[1., 0.], [.5, .5], [0., 1.]]
        models = {'persistence': [[1., 0.]]*3,
                  'trained': [[1., 0.], [np.nan, np.nan], [.2, .8]]}
        result = common_comparison_support(observed, models)
        np.testing.assert_array_equal(result['valid'], [True, False, True])
        self.assertEqual(result['common_observations'], 2)
        self.assertEqual(result['excluded_observations'], 1)
        np.testing.assert_array_equal(result['individual_valid']['persistence'], [True]*3)

    def test_recovery_requires_observed_departure_and_consecutive_confirmation(self):
        result = recovery_endpoint([0., 1., 2., 3.],
                                   [[.5, .5], [.8, .2], [.55, .45], [.53, .47]],
                                   [.5, .5], .1, consecutive=2)
        self.assertEqual(result['status'], 'observed_baseline_recovery')
        self.assertEqual(result['within_margin_from'], 2.)
        self.assertEqual(result['confirmation_time'], 3.)

    def test_missing_recovery_observation_breaks_run_and_retains_right_censoring(self):
        result = recovery_endpoint([0., 1., 2., 3.],
                                   [[.8, .2], [.55, .45], [np.nan, np.nan], [.53, .47]],
                                   [.5, .5], .1, consecutive=2)
        self.assertEqual(result['status'], 'recovery_right_censored')
        self.assertIsNone(result['confirmation_time'])
        self.assertEqual(result['last_valid_time'], 3.)
        unchanged = recovery_endpoint([0., 1.], [[.5, .5]]*2, [.5, .5], .1)
        self.assertEqual(unchanged['status'], 'no_observed_departure')

    def test_time_order_invalid_compositions_and_duplicate_times_are_rejected(self):
        with self.assertRaises(ValueError):
            interpolate_trajectory([0., 0.], [1., 2.], [0.])
        with self.assertRaises(ValueError):
            trajectory_scores([0.], [[.6, .6]], [[.5, .5]])
        with self.assertRaises(ValueError):
            common_comparison_support([[.5, .5]], {'bad': [[-.1, np.nan]]})


if __name__ == '__main__':
    unittest.main()
