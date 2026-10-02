import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

import numpy as np

from orthopolity.solar_validation import development, solar_application_gate, gate_verdict, evaluate


class SolarValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).resolve().parents[1] / "experiments/run_solar_validation.py"
        spec = importlib.util.spec_from_file_location("solar_validation_driver_test", path)
        cls.driver = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.driver)

    def fixture(self, root):
        raw = root / "data/raw"
        raw.mkdir(parents=True)
        fields = ["time", "start_time", "end_time", "flare_id", "xrsb_irrad",
                  "peak_saturated", "integrated_irrad_peak", "integrated_irrad_end"]
        rows = []
        for bin_index, peak in enumerate((5, 50)):
            for i in range(25):
                rows.append(dict(time="2022-01-01 00:02:00", start_time="2022-01-01 00:01:00",
                                 end_time="2022-01-01 00:03:00", flare_id=f"2022-{bin_index}-{i}",
                                 xrsb_irrad=peak, peak_saturated=0, integrated_irrad_peak=peak,
                                 integrated_irrad_end=peak*2))
        with (raw / "noaa_2022.csv").open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader(); writer.writerows(rows)
        metadata = {"variable_attributes": {key: {"units": "example units"}
                    for key in ("xrsb_irrad", "integrated_irrad_peak", "integrated_irrad_end", "end_time")}}
        (raw / "noaa_metadata.json").write_text(json.dumps(metadata))
        checksums = [{"file": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                     for path in raw.iterdir()]
        (root / "data/snapshot_checksums.json").write_text(json.dumps(checksums))
        config = {"run_id": "fixture", "training_years": [2022], "evaluation_years": [2025],
                  "peak_irradiance_domain_W_m2": [1, 100], "bins_per_decade": 1,
                  "minimum_training_events_per_resource_per_pooled_bin": 20,
                  "factor_margin": 1.5, "alpha": .05, "profile_bootstrap_replicates": 499,
                  "candidate_benchmark_run_id": "fixture-benchmark",
                  "validation_url": "https://example.invalid/noaa_2025.csv"}
        config_path = root / "config.json"
        config_path.write_text(json.dumps(config))
        for name in self.driver.SOURCES:
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"# fixture source {name}\n")
        gate, study = root / "benchmark-gate.json", root / "benchmark-study.json"
        gate.write_text(json.dumps({"candidate_eligible": False, "reason": "fixture"}))
        algorithm_sha = hashlib.sha256((root / "src/orthopolity/profile_calibration.py").read_bytes()).hexdigest()
        study.write_text(json.dumps({"status": "complete", "run_id": "fixture-benchmark",
                                    "config": {"factor": 1.5, "alpha": .05, "bootstrap_replicates": 499,
                                               "block_counts": [12], "log_widths": [1, 1]},
                                    "eligibility": [{"method": "centered_bootstrap", "passes": False}],
                                    "source_sha256": {"src/orthopolity/profile_calibration.py": algorithm_sha}}))
        directory = root / "data/solar-validation"
        return config, config_path, directory, gate, study

    def test_freeze_uses_development_without_accessing_missing_2025(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            _, config, directory, gate, study = self.fixture(root)
            with patch.object(self.driver, "ROOT", root):
                plan = self.driver.freeze(config, directory, gate, study)
                self.assertFalse((directory / "noaa_2025.csv").exists())
                np.testing.assert_equal(plan["pooled_edges_W_m2"], [1, 10, 100])
                self.assertFalse(plan["application_gate"]["formal_profile_eligible"])
                self.driver.verify_plan(plan)
                for source in plan["sources"]:
                    self.assertTrue((root / source["archived"]["path"]).exists())

    def test_preexisting_validation_bytes_prevent_claiming_a_new_freeze(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            _, config, directory, gate, study = self.fixture(root)
            directory.mkdir(parents=True)
            (directory / "noaa_2025.csv").write_text("already acquired")
            with patch.object(self.driver, "ROOT", root):
                with self.assertRaisesRegex(ValueError, "already exist before"):
                    self.driver.freeze(config, directory, gate, study)

    def test_changed_source_rejected_before_any_network_request(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            _, config, directory, gate, study = self.fixture(root)
            with patch.object(self.driver, "ROOT", root):
                plan = self.driver.freeze(config, directory, gate, study)
                (root / self.driver.SOURCES[0]).write_text("changed")
                with patch.object(self.driver.urllib.request, "urlopen") as network:
                    with self.assertRaisesRegex(ValueError, "Frozen input changed"):
                        self.driver.acquire(plan, directory)
                    network.assert_not_called()

    def test_initial_acquisition_failure_is_retained(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            _, config, directory, gate, study = self.fixture(root)
            with patch.object(self.driver, "ROOT", root):
                plan = self.driver.freeze(config, directory, gate, study)
                with patch.object(self.driver.urllib.request, "urlopen", side_effect=urllib.error.URLError("fixture failure")):
                    with self.assertRaises(urllib.error.URLError):
                        self.driver.acquire(plan, directory)
                records = [json.loads(line) for line in (directory / "retrieval-attempts.jsonl").read_text().splitlines()]
                self.assertEqual(records[0]["status"], "failed")
                self.assertEqual(records[0]["error_type"], "URLError")
                self.assertFalse((directory / "noaa_2025.csv").exists())

    def test_matching_acquisition_replay_does_not_download_again(self):
        class Response:
            status = 200
            headers = {"Content-Type": "text/csv", "Last-Modified": "fixture-date"}
            def __enter__(self): return self
            def __exit__(self, *args): return False
            def read(self): return b"fixture,2025\n"
            def geturl(self): return "https://example.invalid/noaa_2025.csv"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            _, config, directory, gate, study = self.fixture(root)
            with patch.object(self.driver, "ROOT", root):
                plan = self.driver.freeze(config, directory, gate, study)
                with patch.object(self.driver.urllib.request, "urlopen", return_value=Response()) as network:
                    first = self.driver.acquire(plan, directory)
                    second = self.driver.acquire(plan, directory)
                    self.assertEqual(first, second)
                    self.assertEqual(network.call_count, 1)

    def test_ineligible_application_cannot_be_promoted_by_equivalent_band(self):
        gate = solar_application_gate({"candidate_eligible": True}, {}, {"evaluation_years": [2025]})
        result = gate_verdict({"centered_bootstrap": {"decision": "equivalent"}}, gate)
        self.assertEqual(result["verdict"], "unresolved")
        self.assertEqual(result["conditional_candidate_verdict"], "equivalent")

    def test_missing_resource_gate_prevents_all_catalogue_equivalence(self):
        result = gate_verdict({"centered_bootstrap": {"decision": "equivalent"}},
                             {"formal_profile_eligible": True}, primary_missing_count=1)
        self.assertEqual(result["verdict"], "unresolved")
        self.assertIn("missing", result["reason"])

    def test_strict_json_preserves_unavailable_zero_bin_cost_as_null(self):
        converted = self.driver.json_ready({"ratio": np.array([1, np.nan]), "upper": float("inf")})
        self.assertEqual(converted, {"ratio": [1., None], "upper": None})
        json.dumps(converted, allow_nan=False)

    def test_development_support_and_forecasts_are_training_only(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config, _, _, _, _ = self.fixture(root)
            result = development(root / "data/raw", config)
            first = result["forecasts"]["integrated_irrad_peak"]
            np.testing.assert_allclose(first["log_resource_neutral"]["count_share"], [10/11, 1/11])
            self.assertFalse((root / "data/raw/noaa_2025.csv").exists())

    def test_candidate_api_integration_keeps_conditional_label_separate(self):
        statistics = {"integrated_irrad_peak": {"resource_sums": np.ones((12, 2))}}
        config = {"factor_margin": 1.5, "alpha": .05,
                  "profile_bootstrap_replicates": 20, "profile_seed": 7}
        candidates = self.driver.candidate_profiles(statistics, np.ones(2), config)
        candidate = candidates["integrated_irrad_peak"]
        self.assertEqual(candidate["centered_bootstrap"]["decision"], "equivalent")
        self.assertFalse(candidate["bounded_reference"]["available"])
        gate = solar_application_gate({}, {}, {"evaluation_years": [2025]})
        self.assertEqual(gate_verdict(candidate, gate)["verdict"], "unresolved")

    def test_candidate_zero_resource_bin_is_retained_and_unbounded(self):
        statistics = {"integrated_irrad_peak": {"resource_sums": np.tile([1., 0.], (12, 1))}}
        config = {"factor_margin": 1.5, "alpha": .05,
                  "profile_bootstrap_replicates": 20, "profile_seed": 7}
        candidate = self.driver.candidate_profiles(statistics, np.ones(2), config)["integrated_irrad_peak"]
        self.assertEqual(candidate["point"]["zero_bins"], 1)
        self.assertEqual(candidate["centered_bootstrap"]["decision"], "unresolved")
        self.assertTrue(candidate["centered_bootstrap"]["departure_upper_unbounded"])
        json.dumps(candidate, allow_nan=False)

    def test_incomplete_or_mismatched_benchmark_cannot_authorize_freeze(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            _, config_path, directory, gate, study_path = self.fixture(root)
            study = json.loads(study_path.read_text())
            study["status"] = "running"
            study_path.write_text(json.dumps(study))
            with patch.object(self.driver, "ROOT", root):
                with self.assertRaisesRegex(ValueError, "must be complete"):
                    self.driver.freeze(config_path, directory, gate, study_path)
                study["status"] = "complete"
                study["config"]["factor"] = 2
                study_path.write_text(json.dumps(study))
                with self.assertRaisesRegex(ValueError, "parameter differs"):
                    self.driver.freeze(config_path, directory, gate, study_path)
                self.assertFalse((directory / "frozen-plan.json").exists())

    def test_paired_total_log_score_is_consistent_with_cross_entropy(self):
        statistics = {"months": [f"2022-{i:02d}" for i in range(1, 13)], "years": [2022],
                      "all_counts": np.tile([10, 10], (12, 1)), "counts": np.tile([10, 10], (12, 1)),
                      "resource_sums": np.tile([50., 500.], (12, 1))}
        training = {resource: statistics for resource in ("integrated_irrad_peak", "integrated_irrad_end")}
        from orthopolity.solar_resource_transfer import forecast
        predictions = {resource: forecast([5, 50], [120, 120], np.array([1., 10., 100.]))
                       for resource in training}
        rows = []
        for month in range(1, 13):
            for index, count in ((0, 3), (1, 1)):
                for _ in range(count):
                    rows.append({"month": f"2025-{month:02d}", "bin": index,
                                 "integrated_irrad_peak": [5, 50][index], "integrated_irrad_end": [5, 50][index],
                                 "valid_integrated_irrad_peak": True, "valid_integrated_irrad_end": True})
        config = {"evaluation_years": [2025], "score_bootstrap_replicates": 20, "score_seed": 7}
        _, _, _, summary = evaluate(training, rows, predictions, np.array([1., 10., 100.]), config)
        result = summary["integrated_irrad_peak"]
        difference = result["paired_cross_entropy_differences"]["historical_count_shape"]["value"]
        self.assertAlmostEqual(result["paired_count_log_score"]["historical_minus_log_neutral_sum_log_probability"], -48*difference)


if __name__ == "__main__":
    unittest.main()
