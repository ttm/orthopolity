"""File-backed prospective separation and failed-calibration admission."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


spec=importlib.util.spec_from_file_location('workload_pilot_runner',Path(__file__).resolve().parents[1]/'experiments/run_workload_pilot.py')
runner=importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class WorkloadProtocolChecks(unittest.TestCase):
    def setUp(self):
        self.config=dict(sizes=[2,4],calibration_blocks=2,
                         maximum_calibration_cpu_seconds=1.,maximum_total_worker_memory_bytes=1000)
        self.rows=[dict(split='calibration',block_id=block,size=size,completed=True,
            numerical_valid=True,status='completed',peak_rss_bytes=100*size,cpu_seconds=.1*size)
            for block in range(2) for size in [2,4]]

    def test_full_planned_calibration_required_not_one_complete_block(self):
        with self.assertRaises(ValueError):runner.audit_calibration(self.config,self.rows[:2])
        self.assertEqual(runner.audit_calibration(self.config,self.rows)['memory_costs'].shape,(2,2))

    def test_retained_failed_or_overbound_calibration_cannot_be_resumed_as_valid(self):
        self.rows[0]['completed']=False
        with self.assertRaises(ValueError):runner.audit_calibration(self.config,self.rows)
        self.rows[0].update(completed=True,cpu_seconds=1.1)
        with self.assertRaises(ValueError):runner.audit_calibration(self.config,self.rows)

    def test_freeze_refuses_unfinished_calibration_or_existing_outcomes(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory=Path(temporary);config_path=directory/'config.json'
            config_path.write_text(json.dumps(self.config))
            with self.assertRaisesRegex(ValueError,'full declared calibration'):
                runner.freeze(self.config,config_path,directory)
            (directory/'validation.jsonl').write_text('{}\n')
            with self.assertRaisesRegex(ValueError,'before prediction freeze'):
                runner.freeze(self.config,config_path,directory)

    def test_changed_inputs_invalidate_saved_forecast(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory=Path(temporary);config_path=directory/'config.json'
            config_path.write_text(json.dumps(self.config))
            calibration=directory/'calibration.jsonl';calibration.write_text('{}\n')
            plan=dict(config_sha256=runner.digest(config_path),calibration_sha256=runner.digest(calibration),source_sha256={'worker':'fixed'})
            (directory/'frozen-plan.json').write_text(json.dumps(plan))
            with patch.object(runner,'measurement_sources',return_value={'worker':'changed'}):
                with self.assertRaisesRegex(ValueError,'inputs changed'):
                    runner.freeze(self.config,config_path,directory)
            with patch.object(runner,'measurement_sources',return_value={'worker':'fixed'}):
                config_path.write_text('{}')
                with self.assertRaisesRegex(ValueError,'inputs changed'):
                    runner.freeze(self.config,config_path,directory)


if __name__=='__main__':unittest.main()
