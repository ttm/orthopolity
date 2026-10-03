"""Mathematical checks on synthetic masses; no study outcomes are loaded."""
import json
import math
import unittest
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
from scipy.integrate import quad
from scipy.stats import weibull_min

from orthopolity.plant_profiles import (
    _weibull_model, draw_bounded_power, fit_forecasts, profile, score_profile,
    weibull_logpdf,
)


class QuantileRng:
    def random(self, n):
        return (np.arange(n)+.5)/n


class PlantProfileChecks(unittest.TestCase):
    def test_neutral_integrals_use_the_declared_reference_measure(self):
        result = fit_forecasts({'a': np.array([.01, .03, .1, .3, 1.])})
        edges = np.asarray(result['domain']['edges'])
        log_expected = np.diff(np.log(edges))/math.log(edges[-1]/edges[0])
        linear_expected = np.diff(edges)/(edges[-1]-edges[0])
        np.testing.assert_allclose(result['models']['log_neutral']['stock_shares'], log_expected, atol=1e-14)
        np.testing.assert_allclose(result['models']['linear_neutral']['stock_shares'], linear_expected, atol=1e-14)
        inverse_width = 1./edges[:-1]-1./edges[1:]
        np.testing.assert_allclose(result['models']['log_neutral']['count_shares'], inverse_width/inverse_width.sum())
        np.testing.assert_allclose(result['models']['linear_neutral']['count_shares'], log_expected)
        json.dumps(result, allow_nan=False)

    def test_upper_support_is_development_only_and_inclusive(self):
        result = fit_forecasts({'b': [1.], 'a': [.01, .1, .2]})
        domain = result['domain']
        self.assertEqual(domain['upper'], 1.)
        self.assertEqual(result['development_units'], ['a', 'b'])
        observed = profile([.005, .01, domain['edges'][1], 1., 2.], domain)
        self.assertEqual(observed['counts'], [1, 1, 0, 1])
        self.assertEqual((observed['raw_count'], observed['below_count'], observed['in_domain_count'], observed['above_count']),
                         (5, 1, 3, 1))
        self.assertAlmostEqual(observed['count_coverage'], .6)
        self.assertAlmostEqual(observed['raw_mass'], .005+.01+domain['edges'][1]+1.+2.)
        self.assertAlmostEqual(observed['mass_coverage'], observed['in_domain_mass']/observed['raw_mass'])
        self.assertEqual(domain['upper'], 1.)  # Held-out tails cannot extend the frozen support.
        self.assertEqual(fit_forecasts({'a': [1.00001]})['domain']['upper'], 10.)
        with self.assertRaises(ValueError):
            fit_forecasts({'a': [.01]})  # The dev-max rule would yield U=L.

    def test_empty_bins_and_empirical_equal_plot_weighting(self):
        result = fit_forecasts({'small': [.01], 'large': [1.]*19})
        empirical = result['models']['empirical']
        np.testing.assert_allclose(empirical['stock_shares'], [.5, 0., 0., .5])
        expected_counts = .5*((np.array([1, 0, 0, 0])+.5)/3.+(np.array([0, 0, 0, 19])+.5)/21.)
        np.testing.assert_allclose(empirical['count_shares'], expected_counts)
        self.assertTrue(all(value > 0 for value in empirical['count_shares']))
        row = profile([.04, .1], result['domain'])
        scores = score_profile(result, row)
        self.assertTrue(math.isfinite(scores['empirical']['count_logloss']))
        self.assertEqual(scores['empirical']['stock_tv'], 1.)
        self.assertIsNone(profile([], result['domain'])['count_shares'])
        with self.assertRaises(ValueError):
            score_profile(result, profile([5.], result['domain']))

    def test_bounded_power_quantiles_and_known_pareto_fit(self):
        lower, upper = .01, 100.
        for alpha in (1., 1.+1e-12, 2., -2., 4.):
            values = draw_bounded_power(QuantileRng(), 300, lower, upper, alpha)
            self.assertTrue(np.all((values >= lower) & (values <= upper)))
            if abs(alpha-1) < 1e-10:
                actual_cdf = np.log(values/lower)/math.log(upper/lower)
            else:
                power = 1-alpha
                actual_cdf = (values**power-lower**power)/(upper**power-lower**power)
            np.testing.assert_allclose(actual_cdf, QuantileRng().random(300), atol=2e-12)
        masses = draw_bounded_power(QuantileRng(), 2500, lower, upper, 2.3)
        # The development maximum may be well below U: explicitly include U
        # at negligible weight in a sufficiently large synthetic sample.
        masses = np.r_[masses, upper]
        result = fit_forecasts({'a': masses})
        self.assertEqual(result['domain']['upper'], upper)
        self.assertAlmostEqual(result['parameters']['bounded_pareto']['alpha'], 2.3, delta=.012)

    def test_pareto_likelihood_weights_plots_equally(self):
        result = fit_forecasts({'many': [.02]*30, 'one': [1.]})
        expected = .5*(math.log(.02)+math.log(1.))
        self.assertAlmostEqual(result['parameters']['bounded_pareto']['mean_log_mass'], expected)
        self.assertGreater(result['parameters']['bounded_pareto']['alpha'], -2.)
        self.assertLess(result['parameters']['bounded_pareto']['alpha'], 4.)

    def test_weibull_density_and_stock_moments_match_independent_quadrature(self):
        lower, upper = .01, 10.
        edges = [.01, .1, 1., 10.]
        for shape, scale in ((.3, .2), (1., 1.), (3., .5), (.1, 1000.)):
            distribution = weibull_min(shape, scale=scale)
            normalizer = distribution.cdf(upper)-distribution.cdf(lower)
            mass_total = quad(lambda x: x*distribution.pdf(x), lower, upper, epsabs=1e-11)[0]
            expected_counts = np.diff(distribution.cdf(edges))/normalizer
            expected_stocks = [quad(lambda x: x*distribution.pdf(x), a, b, epsabs=1e-11)[0]/mass_total
                               for a, b in zip(edges[:-1], edges[1:])]
            model = _weibull_model(edges, shape, scale)
            np.testing.assert_allclose(model['count_shares'], expected_counts, rtol=1e-10, atol=1e-12)
            np.testing.assert_allclose(model['stock_shares'], expected_stocks, rtol=2e-8, atol=1e-10)
            density_integral = quad(lambda y: math.exp(weibull_logpdf([math.exp(y)], lower, upper, shape, scale)[0]+y),
                                    math.log(lower), math.log(upper), epsabs=1e-10)[0]
            self.assertAlmostEqual(density_integral, 1., places=9)

    def test_weibull_extreme_truncation_keeps_probabilities_and_logloss(self):
        edges = [.01, .1, 1., 10.]
        concentrated = _weibull_model(edges, 5., .0001)
        self.assertAlmostEqual(concentrated['count_shares'][0], 1.)
        self.assertAlmostEqual(concentrated['stock_shares'][0], 1.)
        self.assertTrue(all(math.isfinite(value) for value in concentrated['count_log_shares']))
        diffuse = _weibull_model(edges, 5., 1000.)
        expected_counts = np.diff(np.asarray(edges)**5)
        expected_stocks = np.diff(np.asarray(edges)**6)
        np.testing.assert_allclose(diffuse['count_shares'], expected_counts/expected_counts.sum(), rtol=1e-10)
        np.testing.assert_allclose(diffuse['stock_shares'], expected_stocks/expected_stocks.sum(), rtol=1e-10)
        forecasts = {'models': {'concentrated': concentrated}}
        observed = profile([5.], {'lower': .01, 'upper': 10., 'edges': edges})
        self.assertTrue(math.isfinite(score_profile(forecasts, observed)['concentrated']['count_logloss']))

    def test_validation_and_reproducibility(self):
        for values in ([0.], [-1.], [math.nan], [math.inf], [[1., 2.]]):
            with self.assertRaises(ValueError):
                fit_forecasts({'a': values})
        for data in ({}, {'a': []}, {'a': [.001]}):
            with self.assertRaises(ValueError):
                fit_forecasts(data)
        development = {'a': [.02, .04, .08, .2], 'b': [.03, .07, .3, 1.]}
        first = fit_forecasts(development)
        held_out = [1000.]
        profile(held_out, first['domain'])
        held_out[0] = 1000000.
        self.assertEqual(first, fit_forecasts(development))
        shape = first['parameters']['bounded_weibull']['shape']
        scale = first['parameters']['bounded_weibull']['scale']
        self.assertTrue(.1 <= shape <= 5.)
        self.assertTrue(.0001 <= scale <= 100.)

    def test_optimizer_failure_aborts_instead_of_using_initial_guesses(self):
        development = {'a': [.02, .04, .08, .2], 'b': [.03, .07, .3, 1.]}

        def failed_restart(objective, start, **kwargs):
            # A finite apparent loss cannot override the convergence status.
            return SimpleNamespace(success=False, fun=-1000., x=start, status=2,
                                   message='synthetic convergence failure', nit=1)

        with patch('orthopolity.plant_profiles.minimize', side_effect=failed_restart) as mocked:
            with self.assertRaisesRegex(ValueError, 'No bounded Weibull'):
                fit_forecasts(development)
            self.assertEqual(mocked.call_count, 12)
        failed_scalar = SimpleNamespace(success=False, fun=0., x=2., status=1, message='synthetic failure')
        with patch('orthopolity.plant_profiles.minimize_scalar', return_value=failed_scalar):
            with self.assertRaisesRegex(ValueError, 'Pareto optimization failed'):
                fit_forecasts(development)
        fitted = fit_forecasts(development)
        parameters = fitted['parameters']['bounded_weibull']
        self.assertGreater(parameters['successful_restarts'], 0)
        self.assertEqual(parameters['successful_restarts'], sum(row['usable'] for row in parameters['restart_statuses']))
        self.assertEqual(len(parameters['restart_statuses']), 12)
        self.assertTrue(fitted['parameters']['bounded_pareto']['optimizer_success'])


if __name__ == '__main__':
    unittest.main()
