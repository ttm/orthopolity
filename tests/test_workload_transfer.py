"""Prospective comparisons preserve historical quotas and paired outcomes."""
from copy import deepcopy
import unittest

import numpy as np

from orthopolity.workload_prediction import calibration_profiles
from orthopolity.workload_transfer import (
    analyse_transfer, forecasts_for_budgets, transfer_plan, within_tolerance,
)


class TransferChecks(unittest.TestCase):
    def setUp(self):
        self.config=dict(sizes=[2,4], dtype='float64', matrix_repeats=3,
            warmup_size=1, thread_environment={}, conditions=['aligned'],
            validation_repetitions_per_budget_stratum=1, permutation_shift=1,
            cpu_tightening_factor=.65, calibration_blocks=2, seed=17,
            analysis_bootstrap_replicates=20, nominal_interval_level=.95,
            memory_resource='total process peak bytes', cpu_resource='task CPU seconds')
        self.rows=[dict(split='calibration',block_id=b,size=s,
            peak_rss_bytes=5*s,cpu_seconds=s/2,numerical_valid=True,
            completed=True,status='completed') for b in range(2) for s in [2,4]]
        profile=calibration_profiles(self.rows,[2,4])
        self.reference=dict(config=deepcopy(self.config), frozen_utc='before',
            calibrated_profile=profile, budget_strata=2, validation_blocks=2,
            design=dict(conditions=dict(aligned=dict(absolute_profile_error_tolerance=1/28))),
            conditions=dict(aligned=dict(memory_budgets_bytes=[15,25],
                cpu_budgets_seconds=[1.5,2.5],
                forecasts=forecasts_for_budgets(profile,[15,25],[1.5,2.5]))))
        self.validation=[dict(split='validation',block_id=b,condition='aligned',
            budget_stratum=b,size=s,completed=(b==1 or s==2),
            numerical_valid=True,memory_budget_bytes=[15,25][b],
            cpu_budget_seconds=[1.5,2.5][b],peak_rss_bytes=5*s,
            cpu_seconds=s/2,status='completed' if b==1 or s==2 else 'memory_limit')
            for b in range(2) for s in [2,4]]

    def test_local_cost_change_never_changes_old_forecast_quota_or_criterion(self):
        local=[dict(r,peak_rss_bytes=r['peak_rss_bytes']*2,
                    cpu_seconds=r['cpu_seconds']*2) for r in self.rows]
        plan=transfer_plan(self.reference,self.config,local)
        old=self.reference['conditions']['aligned']; new=plan['conditions']['aligned']
        self.assertEqual(new['memory_budgets_bytes'],old['memory_budgets_bytes'])
        self.assertEqual(new['cpu_budgets_seconds'],old['cpu_budgets_seconds'])
        self.assertEqual(plan['design'],self.reference['design'])
        np.testing.assert_array_equal(new['original_forecasts']['joint']['survival_at_sizes'],[1,.5])
        np.testing.assert_array_equal(new['local_forecasts']['joint']['survival_at_sizes'],[.5,0])
        new['memory_budgets_bytes'][0]=99
        self.assertEqual(old['memory_budgets_bytes'][0],15)

    def test_changed_physical_task_resource_definition_or_intervention_rejected(self):
        changes=dict(sizes=[2,8],matrix_repeats=2,permutation_shift=2,
            cpu_tightening_factor=.5,memory_resource='array storage only')
        for key,value in changes.items():
            with self.subTest(key=key),self.assertRaises(ValueError):
                transfer_plan(self.reference,dict(self.config,**{key:value}),self.rows)

    def test_missing_duplicate_failed_or_validation_calibration_rejected(self):
        candidates=[self.rows[:-1],self.rows+[self.rows[0]],
            [dict(r,block_id=3) for r in self.rows],
            [dict(r,split='validation') for r in self.rows],
            [dict(r,numerical_valid=False) for r in self.rows]]
        for rows in candidates:
            with self.assertRaises(ValueError):transfer_plan(self.reference,self.config,rows)

    def test_recalibration_can_be_worse_and_uses_the_same_actual_outcomes(self):
        local=[dict(r,peak_rss_bytes=r['peak_rss_bytes']*2,
                    cpu_seconds=r['cpu_seconds']*2) for r in self.rows]
        result=analyse_transfer(transfer_plan(self.reference,self.config,local),self.validation)
        row=result['conditions']['aligned']
        self.assertTrue(row['original_within_tolerance'])
        self.assertFalse(row['local_within_original_tolerance'])
        self.assertEqual(row['local_mean_squared_error_improvement'],-.25)
        np.testing.assert_allclose(row['paired_recalibration_gain_nominal_interval'],[-.25,-.25])
        self.assertEqual(result['sample_counts']['new_validation_tasks'],4)
        self.assertEqual(row['upper_censor_fraction'],.5)

    def test_identical_profiles_have_zero_paired_gain_in_every_resample(self):
        result=analyse_transfer(transfer_plan(self.reference,self.config,self.rows),self.validation)
        np.testing.assert_array_equal(result['conditions']['aligned']['paired_recalibration_gain_nominal_interval'],[0,0])
        with self.assertRaises(ValueError):
            analyse_transfer(transfer_plan(self.reference,self.config,self.rows),self.validation[:-1])

    def test_boundary_roundoff_is_allowed_but_scientific_margin_is_unchanged(self):
        self.assertTrue(within_tolerance(1/7-3/28,1/28))
        self.assertFalse(within_tolerance(1/28+1e-10,1/28))
        for value in [float('nan'),-1,float('inf')]:
            with self.assertRaises(ValueError):within_tolerance(value,1/28)


if __name__=='__main__':unittest.main()
