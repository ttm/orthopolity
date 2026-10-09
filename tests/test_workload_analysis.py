"""Actual completed-size auditing, including irregular success patterns."""
import unittest

from orthopolity.workload_analysis import observed_opportunities, profile_errors


class WorkloadAnalysisChecks(unittest.TestCase):
    def setUp(self):
        self.plan = dict(config=dict(sizes=[2,4,8]), validation_blocks=2, budget_strata=2,
                         conditions=dict(aligned=dict(memory_budgets_bytes=[100,200],
                                                      cpu_budgets_seconds=[1.,2.])))
        self.rows=[]
        for block,pattern in enumerate([[False,True,False],[False,False,False]]):
            for size,completed in zip([2,4,8],pattern):
                self.rows.append(dict(split='validation',block_id=block,condition='aligned',
                    budget_stratum=block,size=size,completed=completed,numerical_valid=completed,
                    memory_budget_bytes=[100,200][block],cpu_budget_seconds=[1.,2.][block],
                    peak_rss_bytes=90,cpu_seconds=.5))

    def test_largest_uses_actual_completion_and_retains_zero(self):
        outcome=observed_opportunities(self.plan,self.rows)
        self.assertEqual([row['largest_completed_size'] for row in outcome],[4,0])
        self.assertTrue(outcome[0]['nonmonotone_success_pattern'])
        self.assertTrue(outcome[1]['zero_completion'])
        self.assertFalse(outcome[0]['upper_censored'])
        self.rows[2].update(completed=True,numerical_valid=True)
        self.assertTrue(observed_opportunities(self.plan,self.rows)[0]['upper_censored'])

    def test_missing_duplicate_or_changed_quota_cannot_enter_audit(self):
        for rows in [self.rows[:-1],self.rows+[self.rows[0]]]:
            with self.assertRaises(ValueError):observed_opportunities(self.plan,rows)
        self.rows[0]['memory_budget_bytes']=101
        with self.assertRaises(ValueError):observed_opportunities(self.plan,self.rows)

    def test_invalid_or_overquota_completion_is_rejected(self):
        self.rows[1]['numerical_valid']=False
        with self.assertRaises(ValueError):observed_opportunities(self.plan,self.rows)
        self.rows[1].update(numerical_valid=True,cpu_seconds=1.1)
        with self.assertRaises(ValueError):observed_opportunities(self.plan,self.rows)

    def test_unconditioned_profile_error_keeps_zero_and_endpoint_mass(self):
        actual=dict(probability=[.5,0.,.5,0.],survival_at_sizes=[.5,.5,0.])
        predicted=dict(probability=[0.,.5,0.,.5],survival_at_sizes=[1.,.5,.5])
        error=profile_errors(actual,predicted)
        self.assertEqual(error['probability_total_variation'],1.)
        self.assertEqual(error['maximum_absolute_survival_error'],.5)
        self.assertAlmostEqual(error['mean_squared_survival_error'],1/6)


if __name__=='__main__':unittest.main()
