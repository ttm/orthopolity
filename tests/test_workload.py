"""Small real matrix tasks and unit/phase-accounting checks."""
import json
import unittest
from unittest.mock import patch

import numpy as np

from orthopolity.workload import normalize_peak_rss, run_workload, verify_matrix_product


def usage(cpu, peak):
    return dict(cpu_user_seconds=cpu, cpu_system_seconds=0.0,
                cpu_total_seconds=cpu, peak_rss_bytes=peak)


class WorkloadChecks(unittest.TestCase):
    def test_explicit_platform_memory_units(self):
        self.assertEqual(normalize_peak_rss(12345,'darwin'),12345)
        self.assertEqual(normalize_peak_rss(12345,'linux'),12345*1024)
        with self.assertRaises(NotImplementedError):normalize_peak_rss(100,'win32')
        with self.assertRaises(ValueError):normalize_peak_rss(-1,'darwin')

    def test_independent_integrity_check_detects_corruption(self):
        a=np.array([[1.,2.],[3.,4.]]);b=np.array([[5.,6.],[7.,8.]])
        # Product entries are independently known from four scalar sums.
        correct=np.array([[19.,22.],[43.,50.]])
        probe=np.array([.6,.8])
        self.assertTrue(verify_matrix_product(a,b,correct,probe)['passed'])
        wrong=correct.copy();wrong[0,0]+=1
        self.assertFalse(verify_matrix_product(a,b,wrong,probe)['passed'])
        wrong[0,0]=np.inf
        result=verify_matrix_product(a,b,wrong,probe)
        self.assertFalse(result['passed']);self.assertIsNone(result['checksum'])
        json.dumps(result,allow_nan=False)

    def test_tiny_real_completion_measures_and_verifies_actual_work(self):
        result=run_workload(16,repeats=2,warmup_size=8)
        self.assertTrue(result['completed']);self.assertEqual(result['status'],'completed')
        self.assertEqual(result['multiplications_completed'],2)
        self.assertEqual(result['verified_multiplications'],2)
        self.assertGreater(result['cpu_seconds'],0)
        self.assertGreater(result['wall_seconds'],0)
        self.assertGreaterEqual(result['peak_rss_bytes'],result['baseline_peak_rss_bytes'])
        self.assertTrue(result['verification']['passed'])
        self.assertLess(result['verification']['relative_residual'],1e-10)
        json.dumps(result,allow_nan=False)
        repeat=run_workload(16,repeats=1,warmup_size=8)
        self.assertAlmostEqual(result['checksum'],repeat['checksum'],places=12)

    def test_start_rejection_uses_total_observed_process_peak(self):
        result=run_workload(8,repeats=1,warmup_size=4,memory_budget_bytes=0)
        self.assertFalse(result['completed']);self.assertEqual(result['status'],'memory_quota')
        self.assertGreater(result['peak_rss_bytes'],0)
        self.assertEqual(result['multiplications_completed'],0)
        self.assertEqual(result['checkpoints'][-1]['phase'],'start')

    def test_allocation_rejection_retains_observed_cost_not_size_estimate(self):
        with patch('orthopolity.workload._read_process_usage',side_effect=[usage(12,1000),usage(12.001,1000),usage(12.05,2000)]):
            result=run_workload(8,repeats=1,warmup_size=4,memory_budget_bytes=1500)
        self.assertEqual(result['status'],'memory_quota')
        self.assertEqual(result['peak_rss_bytes'],2000)
        self.assertAlmostEqual(result['cpu_seconds'],.05)
        self.assertEqual(result['checkpoints'][-1]['phase'],'allocations')
        self.assertEqual(result['multiplications_completed'],0)

    def test_cpu_rejection_occurs_after_actual_multiply_and_preserves_overshoot(self):
        observed=[usage(12,1000),usage(12.001,1000),usage(12.02,1100),usage(13.5,1100)]
        with patch('orthopolity.workload._read_process_usage',side_effect=observed):
            result=run_workload(8,repeats=3,warmup_size=4,cpu_budget_seconds=1)
        self.assertEqual(result['status'],'cpu_quota')
        self.assertAlmostEqual(result['cpu_seconds'],1.5)
        self.assertEqual(result['multiplications_completed'],1)
        self.assertEqual(result['verified_multiplications'],0)
        self.assertEqual(result['checkpoints'][-1]['phase'],'matmul_1')

    def test_final_verification_cost_is_subject_to_cpu_check(self):
        observed=[usage(12,1000),usage(12.001,1000),usage(12.02,1100),usage(12.5,1100),usage(13.2,1100)]
        with patch('orthopolity.workload._read_process_usage',side_effect=observed):
            result=run_workload(8,repeats=1,warmup_size=4,cpu_budget_seconds=1)
        self.assertEqual(result['status'],'cpu_quota')
        self.assertAlmostEqual(result['cpu_seconds'],1.2)
        self.assertEqual(result['verified_multiplications'],1)
        self.assertTrue(result['verification']['passed'])
        self.assertEqual(result['checkpoints'][-1]['phase'],'verification_1')

    def test_invalid_bounds_are_rejected_before_work(self):
        for kwargs in ({'size':0},{'size':2049},{'size':8,'repeats':0},
                       {'size':8,'repeats':33},{'size':8,'warmup_size':257},
                       {'size':8,'cpu_budget_seconds':-1},{'size':8,'memory_budget_bytes':np.inf}):
            with self.assertRaises(ValueError):run_workload(**kwargs)


if __name__=='__main__':unittest.main()
