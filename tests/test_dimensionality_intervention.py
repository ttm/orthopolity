"""Independent-cost forecasts, coordinate conventions and CPU accounting."""
import copy
import json
from pathlib import Path
import unittest

from orthopolity.dimensionality_intervention import (
    calibration_summary,execute_job,profile_predictions,regression_degree,
    runtime_metadata,summarize_trials,validate_config,
)


ROOT=Path(__file__).resolve().parents[1]


class DimensionalityInterventionChecks(unittest.TestCase):
    def setUp(self):
        self.config=json.loads((ROOT/"configs/dimensionality_intervention_2026-10-02.json").read_text())

    def test_independent_nonunit_cost_changes_full_count_profile(self):
        sizes=[2,4,8];edges=[1,3,6,12]
        cubic=profile_predictions(sizes,edges,[1,8,64],[1,1,1],cost_degree=3)
        quadratic=profile_predictions(sizes,edges,[1,4,16],[1,1,1],cost_degree=2)
        self.assertEqual(cubic["fair_thread_cpu"]["cpu_share"],[1/3]*3)
        self.assertGreater(cubic["fair_thread_cpu"]["count_share"][0],quadratic["fair_thread_cpu"]["count_share"][0])
        self.assertEqual(cubic["equal_job_service"]["count_share"],[1/3]*3)
        self.assertAlmostEqual(regression_degree(sizes,[1,8,64])["degree"],3)
        self.assertAlmostEqual(regression_degree([k*k for k in sizes],[1,8,64])["degree"],1.5)

    def test_restriction_separates_opportunity_and_class_neutrality(self):
        result=profile_predictions([2,4,8],[1,3,6,12],[1,8,64],[2,1,0])
        self.assertEqual(result["fair_thread_cpu"]["cpu_share"],[2/3,1/3,0])
        self.assertEqual(result["equal_active_class_cpu"]["cpu_share"],[.5,.5,0])
        for model in result.values():
            self.assertEqual(model["cpu_share"][-1],0)
            self.assertEqual(model["count_share"][-1],0)
            self.assertAlmostEqual(sum(model["count_share"]),1)

    def test_calibration_is_complete_and_rejects_output_split(self):
        config=copy.deepcopy(self.config)
        config["calibration_blocks"]=2;config["calibration_jobs_per_block"]=1
        config["calibration_bootstrap_replicates"]=30
        rows=[dict(split="calibration",status="completed",numerical_valid=True,block_id=b,kernel=k,size=s,
            job_cpu_seconds=[s**(2 if k=="quadratic" else 3)*1e-6])
            for b in range(2) for k in config["kernels"] for s in config["sizes"]]
        result=calibration_summary(rows,config)
        self.assertAlmostEqual(result["quadratic"]["independently_measured_cost_fit"]["degree"],2)
        self.assertAlmostEqual(result["cubic"]["independently_measured_cost_fit"]["degree"],3)
        for invalid in (rows[:-1],rows+[rows[0]],[dict(rows[0],split="validation")]+rows[1:]):
            with self.assertRaises(ValueError):calibration_summary(invalid,config)

    def test_complete_partial_and_overhead_cpu_are_distinct(self):
        config=copy.deepcopy(self.config);config["sizes"]=[2,4,8];config["log_bin_edges"]=[1,3,6,12]
        counts=[2,1,0];q=[1,2,4]
        forecasts=profile_predictions(config["sizes"],config["log_bin_edges"],q,counts)
        rows=[dict(size=2,completed_jobs=1,cpu_seconds=2,complete_job_cpu_seconds=1,partial_job_cpu_seconds=.5,loop_overhead_cpu_seconds=.5),
              dict(size=2,completed_jobs=1,cpu_seconds=2,complete_job_cpu_seconds=1,partial_job_cpu_seconds=.5,loop_overhead_cpu_seconds=.5),
              dict(size=4,completed_jobs=1,cpu_seconds=2,complete_job_cpu_seconds=2,partial_job_cpu_seconds=0,loop_overhead_cpu_seconds=0)]
        result=summarize_trials([dict(workers=rows)],config,q,forecasts,counts)
        self.assertEqual(result["measured_cpu_share"],[2/3,1/3,0])
        self.assertEqual(result["calibrated_completed_job_cpu_seconds_by_class"],[2,2,0])
        self.assertEqual(result["partial_job_cpu_seconds_by_class"],[1,0,0])
        self.assertEqual(result["cpu_seconds_by_class"],[4,2,0])
        corrupted=copy.deepcopy(rows);corrupted[0]["cpu_seconds"]=1
        with self.assertRaises(ValueError):summarize_trials([dict(workers=corrupted)],config,q,forecasts,counts)

    def test_density_slopes_use_actual_bin_widths(self):
        config=copy.deepcopy(self.config);config["sizes"]=[2,4,8];config["log_bin_edges"]=[1,3,7,15]
        counts=[1,1,1];q=[1,1,1]
        forecasts=profile_predictions(config["sizes"],config["log_bin_edges"],q,counts)
        rows=[dict(size=k,completed_jobs=8,cpu_seconds=8,complete_job_cpu_seconds=8,partial_job_cpu_seconds=0,loop_overhead_cpu_seconds=0) for k in config["sizes"]]
        result=summarize_trials([dict(workers=rows)],config,q,forecasts,counts)
        # Linear bins grow by two, while their logarithmic widths are unequal.
        self.assertAlmostEqual(result["dimension_diagnostics"]["binned_linear_density_degree"],1)
        self.assertNotAlmostEqual(result["dimension_diagnostics"]["apparent_log_class_count_degree"],0)

    def test_actual_kernels_verify_and_deadlines_censor(self):
        for kernel in ("quadratic","cubic"):
            outcome=execute_job(kernel,4,quadratic_repeats=2)
            self.assertTrue(outcome["completed"])
            self.assertTrue(outcome["numerical_valid"])
            self.assertFalse(execute_job(kernel,4,deadline=0)["completed"])
        with self.assertRaises(ValueError):execute_job("unknown",4)

    def test_declared_exposure_and_runtime_clock(self):
        validate_config(self.config)
        invalid=copy.deepcopy(self.config);invalid["conditions"]["equal_threads"]=[2]*5
        with self.assertRaises(ValueError):validate_config(invalid)
        metadata=runtime_metadata()
        self.assertGreater(metadata["thread_cpu_clock"]["resolution"],0)
        self.assertFalse(metadata["priority_affinity_and_switch_interval_changed"])


if __name__=="__main__":unittest.main()
