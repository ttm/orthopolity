"""Sampling targets, likelihood identities, and independent null calibration."""
import itertools
import unittest

import numpy as np
from scipy.stats import binom

from orthopolity.interventions import (
    decision_outcomes, expected_log_likelihood_ratio, intervention_allocations,
    log_likelihood_ratio, monte_carlo_rank_pvalue, multinomial_deviance,
    multinomial_samples, observation_probabilities, resource_probability_from_sample,
)


class InterventionChecks(unittest.TestCase):
    def test_count_and_resource_targets_and_propensity_correction(self):
        intensity=np.array([[4.,1.]]);q=np.array([1.,4.])
        np.testing.assert_allclose(observation_probabilities(intensity,q),[[.8,.2]])
        np.testing.assert_allclose(observation_probabilities(intensity,q,sampling='primary_resource'),[[.5,.5]])
        np.testing.assert_allclose(resource_probability_from_sample([[400,100]],q),[[.5,.5]])
        np.testing.assert_allclose(resource_probability_from_sample([[250,250]],q,sampling='primary_resource'),[[.5,.5]])
        # Applying q twice would instead give [.2,.8], a different observable.
        np.testing.assert_allclose(resource_probability_from_sample([[250,250]],q),[[.2,.8]])

    def test_finite_deviance_retains_unobserved_classes(self):
        p=np.array([[.5,.5],[.25,.75]])
        self.assertAlmostEqual(multinomial_deviance([[50,50],[25,75]],p),0)
        value=multinomial_deviance([[10,0],[0,10]],p)
        self.assertAlmostEqual(value,20*(np.log(2)+np.log(4/3)))

    def test_likelihood_mean_and_variance_against_exact_enumeration(self):
        pf=np.array([[.7,.3],[.4,.6]]);kl=np.array([[.5,.5],[.2,.8]])
        truth=np.array([[.6,.4],[.3,.7]]);n=2
        values=[];weights=[]
        for before,after in itertools.product(range(n+1),repeat=2):
            c=np.array([[before,n-before],[after,n-after]])
            values.append(log_likelihood_ratio(c,pf,kl))
            weights.append(binom.pmf(before,n,truth[0,0])*binom.pmf(after,n,truth[1,0]))
        values=np.asarray(values);weights=np.asarray(weights)
        mean=np.dot(weights,values);variance=np.dot(weights,(values-mean)**2)
        expected=expected_log_likelihood_ratio(truth,pf,kl,n)
        self.assertAlmostEqual(expected['mean'],mean,places=12)
        self.assertAlmostEqual(expected['variance'],variance,places=12)
        positive=expected_log_likelihood_ratio(pf,pf,kl,n)['mean']
        negative=expected_log_likelihood_ratio(kl,pf,kl,n)['mean']
        self.assertGreater(positive,0);self.assertLess(negative,0)

    def test_monte_carlo_rank_handles_plus_one_and_ties(self):
        np.testing.assert_allclose(monte_carlo_rank_pvalue([4,3,2],[0,1,2,3]),[.2,.4,.6])
        np.testing.assert_allclose(monte_carlo_rank_pvalue([1],[1,1,1]),[1])

    def test_independent_calibration_controls_null_and_detects_wrong_model(self):
        p=np.array([[.1,.2,.3,.4],[.4,.3,.2,.1]])
        bad=np.array([[.7,.1,.1,.1],[.1,.1,.1,.7]])
        rng=np.random.default_rng(11593)
        calibration=multinomial_deviance(multinomial_samples(p,150,3000,rng),p)
        heldout=multinomial_deviance(multinomial_samples(p,150,5000,rng),p)
        alternative=multinomial_deviance(multinomial_samples(bad,150,1000,rng),p)
        false_positive=np.mean(monte_carlo_rank_pvalue(heldout,calibration)<=.05)
        power=np.mean(monte_carlo_rank_pvalue(alternative,calibration)<=.05)
        self.assertTrue(.025<false_positive<.075)
        self.assertGreater(power,.99)

    def test_same_binding_budgets_under_all_three_objectives(self):
        k=np.geomspace(1.05,61,48);q=np.vstack([k*k,k*k*k]);w=np.ones(48)
        extra=w*np.exp(.8*np.cos(2*np.pi*np.log(k)/np.log(64)))
        result=intervention_allocations(q,w,1,[12,8],extra_weights=extra)
        for model in result.values():
            np.testing.assert_allclose(model['resource_totals'],[[1,12],[1,8]],atol=1e-8)
        self.assertGreater(np.max(abs(result['extra']['counts']-result['pf']['counts'])),1e-3)

    def test_decision_does_not_force_a_winner(self):
        result=decision_outcomes([.5,.01,.8,.01],[.01,.5,.8,.01],.025)
        self.assertEqual(result.tolist(),['pf','kl','ambiguous','both_rejected'])

    def test_invalid_budget_scope_and_sampling_are_rejected(self):
        k=np.geomspace(1.05,61,48);q=np.vstack([k*k,k*k*k])
        for call in (
            lambda: intervention_allocations(q,np.ones(48),1,[12,2]),
            lambda: observation_probabilities([[1,2]],[1,1],sampling='unknown'),
            lambda: multinomial_deviance([[1.5,2.5]],[[.5,.5]]),
            lambda: log_likelihood_ratio([[1.5,2.5]],[[.5,.5]],[[.3,.7]]),
            lambda: decision_outcomes([1.1],[.5],.025),
            lambda: monte_carlo_rank_pvalue([2],[]),
        ):
            with self.assertRaises(ValueError):call()


if __name__=='__main__':unittest.main()
