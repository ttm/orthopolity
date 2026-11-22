"""Small known inventories exercise joins and corruption stops without network."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("cosmic_material", ROOT / "experiments/check_cosmic_material_inventory.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
try:
    import h5py
except ImportError:
    h5py = None


def expected():
    return dict(num_dm=12, mass_dm=.125, boxsize=35000., hubble=.6774,
                omega_0=.3089, omega_L=.6911, omega_B=.0486,
                num_files_snapshot=4, num_files_groupcat=4,
                snapshots={str(s): dict(redshift=z, num_groups=4, num_subgroups=4)
                           for s, z in ((97, .024), (98, .0095), (99, 0.))})


def write_epoch(directory, output, e, id_order=None, counts=None):
    paths = {}
    counts = np.array([2, 2, 2, 2] if counts is None else counts, dtype=np.uint64)
    starts = np.concatenate(([0], np.cumsum(counts)[:-1])).astype(np.uint64)
    snapoffsets = np.zeros((6, 4), dtype=np.uint64)
    snapoffsets[1] = [0, 3, 6, 9]
    go = np.zeros((4, 6), dtype=np.uint64)
    go[:, 1] = starts
    path = directory / f"offsets-{output}.hdf5"
    with h5py.File(path, "w") as f:
        f["Group/SnapByType"] = go
        f["FileOffsets/SnapByType"] = snapoffsets
        f["FileOffsets/Group"] = np.arange(4, dtype=np.uint64)
        f["FileOffsets/Subhalo"] = np.arange(4, dtype=np.uint64)
    paths[("offsets", output, None)] = path
    order = np.arange(1, 13, dtype=np.uint64) if id_order is None else np.array(id_order, dtype=np.uint64)
    z = e["snapshots"][str(output)]["redshift"]
    for chunk in range(4):
        path = directory / f"groupcat-{output}-{chunk}.hdf5"
        with h5py.File(path, "w") as f:
            attrs = f.create_group("Header").attrs
            for k, v in dict(Ngroups_Total=4, Nsubgroups_Total=4, Ngroups_ThisFile=1,
                             Nsubgroups_ThisFile=1, NumFiles=4).items():
                attrs[k] = np.int32(v)
            attrs["Nids_ThisFile"] = np.int64(counts[chunk])
            attrs["Nids_Total"] = np.int64(counts.sum())
            attrs["Redshift"], attrs["Time"] = z, 1 / (1 + z)
            lengths = np.zeros((1, 6), dtype=np.uint32)
            lengths[0, 1] = counts[chunk]
            f["Group/GroupLenType"] = lengths
            f["Group/GroupMass"] = np.array([counts[chunk] * e["mass_dm"]], dtype=np.float32)
        paths[("groupcat", output, chunk)] = path
        path = directory / f"particle_ids-{output}-{chunk}.hdf5"
        with h5py.File(path, "w") as f:
            attrs = f.create_group("Header").attrs
            attrs["NumPart_ThisFile"] = np.array([0, 3, 0, 0, 0, 0], dtype=np.uint32)
            attrs["NumPart_Total"] = np.array([0, 12, 0, 0, 0, 0], dtype=np.uint32)
            attrs["NumPart_Total_HighWord"] = np.zeros(6, dtype=np.uint32)
            attrs["MassTable"] = np.array([0, e["mass_dm"], 0, 0, 0, 0])
            attrs["NumFilesPerSnapshot"] = np.int32(4)
            attrs["Redshift"], attrs["Time"] = z, 1 / (1 + z)
            for a, k in (("BoxSize", "boxsize"), ("HubbleParam", "hubble"),
                         ("Omega0", "omega_0"), ("OmegaLambda", "omega_L")):
                attrs[a] = e[k]
            f["PartType1/ParticleIDs"] = order[3 * chunk:3 * (chunk + 1)]
        paths[("particle_ids", output, chunk)] = path
    return paths


class TransferDiagnosticsTests(unittest.TestCase):
    def test_pair_partitions_and_size_jumps_have_known_answer(self):
        left = np.array([0, 0, 1, 1, 2, 2], dtype=np.uint32)
        right = np.array([0, 1, 0, 1, 2, 1], dtype=np.uint32)
        report = MODULE.pair_diagnostics(left, right, np.array([0, 2, 8]), np.array([0, 4, 8]), 10.)
        self.assertEqual(report["particle_counts"], dict(diffuse_to_diffuse=1, diffuse_to_host=1,
                         host_to_diffuse=1, host_to_host=3, host_mass_increased=1,
                         host_mass_decreased=1, host_mass_equal=1))
        self.assertAlmostEqual(report["mean_absolute_log_mass_jump_given_both_hosted"], 2 * np.log(2) / 3)
        self.assertAlmostEqual(report["mean_signed_log_mass_jump_given_both_hosted"], 0.)
        self.assertEqual(sum(report["absolute_jump_histogram"]["particle_counts"]), 3)
        self.assertEqual(report["mass_solar"]["diffuse_to_host"], 10.)

    def test_three_epochs_expose_reversal_and_diffuse_excursion(self):
        labels = [np.array(x, dtype=np.uint32) for x in ([1, 1, 0], [1, 0, 1], [1, 1, 0])]
        sizes = [np.array(x) for x in ([0, 2], [0, 8], [0, 4])]
        result = MODULE.cadence_diagnostics(labels, sizes)
        self.assertEqual(result["particles_hosted_at_all_three_outputs"], 1)
        self.assertEqual(result["particles_with_host_mass_direction_reversal"], 1)
        self.assertEqual(result["host_diffuse_host_particles"], 1)
        self.assertEqual(result["diffuse_host_diffuse_particles"], 1)
        self.assertAlmostEqual(result["mean_resolved_minus_coarsened_absolute_log_change"], 2 * np.log(2))

    def test_mass_envelope_does_not_claim_verified_accumulation(self):
        result = MODULE.mass_diagnostic(np.array([2, 4]), np.array([.25, .5], dtype=np.float32), .125, np.dtype("float32"))
        self.assertEqual(result["max_relative_difference"], 0.)
        self.assertFalse(result["catalogue_accumulation_algorithm_verified"])
        altered = MODULE.mass_diagnostic(np.array([2]), np.array([1.], dtype=np.float32), .125, np.dtype("float32"))
        self.assertEqual(altered["outside_conditional_summation_bound_count"], 1)

    def test_time_conversion_orders_outputs_and_rejects_nonflat(self):
        ages = [MODULE.cosmic_time_gyr(a, .3089, .6911, .6774) for a in [.97, .99, 1.]]
        self.assertLess(ages[0], ages[1])
        self.assertLess(ages[1], ages[2])
        self.assertGreater(ages[2], 13.)
        self.assertLess(ages[2], 14.)
        with self.assertRaisesRegex(MODULE.InvalidBootstrap, "flat_matter_lambda"):
            MODULE.cosmic_time_gyr(1., .3, .6, .7)


@unittest.skipIf(h5py is None, "optional cosmic HDF5 dependency is not installed")
class MaterialInventoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp.name)
        self.expected = expected()
        self.paths = write_epoch(self.directory, 97, self.expected)

    def tearDown(self):
        self.temp.cleanup()

    def test_groups_cross_snapshot_chunk_boundaries_and_diffuse_is_explicit(self):
        ids, labels, counts, report = MODULE.load_epoch(97, self.paths, self.expected, h5py)
        self.assertEqual(ids.tolist(), list(range(1, 13)))
        self.assertEqual(labels.tolist(), [1, 1, 2, 2, 3, 3, 4, 4, 0, 0, 0, 0])
        self.assertEqual(counts.tolist(), [0, 2, 2, 2, 2])
        self.assertEqual(report["grouped_particles"], 8)
        self.assertEqual(report["diffuse_particles"], 4)
        self.assertEqual(report["integer_closure_residual"], 0)

    def test_sort_reorders_memberships_with_their_ids(self):
        ids = [9, 1, 12, 4, 6, 7, 3, 2, 5, 8, 10, 11]
        paths = write_epoch(self.directory, 98, self.expected, ids)
        sorted_ids, labels, _, _ = MODULE.load_epoch(98, paths, self.expected, h5py)
        source_labels = [1, 1, 2, 2, 3, 3, 4, 4, 0, 0, 0, 0]
        expected_labels = [label for _, label in sorted(zip(ids, source_labels))]
        self.assertEqual(sorted_ids.tolist(), list(range(1, 13)))
        self.assertEqual(labels.tolist(), expected_labels)

    def test_observed_transposed_snapshot_offsets_preserve_membership(self):
        with h5py.File(self.paths[("offsets", 97, None)], "r+") as f:
            values = f["FileOffsets/SnapByType"][:].T
            del f["FileOffsets/SnapByType"]
            f["FileOffsets/SnapByType"] = values
        _, labels, _, result = MODULE.load_epoch(97, self.paths, self.expected, h5py)
        self.assertEqual(result["stored_snapshot_offset_layout"], "chunk_by_type")
        self.assertEqual(labels.tolist(), [1, 1, 2, 2, 3, 3, 4, 4, 0, 0, 0, 0])

    def test_independent_catalogue_total_counter_disagreement_is_rejected(self):
        with h5py.File(self.paths[("groupcat", 97, 1)], "r+") as f:
            f["Header"].attrs["Nids_Total"] = np.int64(9)
        with self.assertRaisesRegex(MODULE.InvalidBootstrap, "groupcat_total_id_count_mismatch"):
            MODULE.load_epoch(97, self.paths, self.expected, h5py)

    def test_file_id_counters_can_partition_material_differently_from_group_rows(self):
        for chunk, count in enumerate([1, 3, 0, 4]):
            with h5py.File(self.paths[("groupcat", 97, chunk)], "r+") as f:
                f["Header"].attrs["Nids_ThisFile"] = np.int64(count)
        _, labels, _, result = MODULE.load_epoch(97, self.paths, self.expected, h5py)
        self.assertEqual(labels.tolist(), [1, 1, 2, 2, 3, 3, 4, 4, 0, 0, 0, 0])
        counters = result["groupcat_id_counter_comparison"]
        self.assertEqual(counters["per_file_Nids_ThisFile"], [1, 3, 0, 4])
        self.assertEqual(counters["per_file_group_length_sum"], [2, 2, 2, 2])
        self.assertEqual(counters["per_file_counter_minus_group_length_sum"], [-1, 1, -2, 2])
        self.assertEqual(counters["summed_Nids_ThisFile"], 8)
        self.assertTrue(counters["global_agreement_checked"])

    def test_file_id_counter_sum_disagreement_is_rejected(self):
        with h5py.File(self.paths[("groupcat", 97, 1)], "r+") as f:
            f["Header"].attrs["Nids_ThisFile"] = np.int64(3)
        with self.assertRaisesRegex(MODULE.InvalidBootstrap, "groupcat_summed_file_id_count_mismatch"):
            MODULE.load_epoch(97, self.paths, self.expected, h5py)

    def test_negative_or_noninteger_file_id_counter_is_rejected(self):
        path = self.paths[("groupcat", 97, 1)]
        for invalid in (np.int64(-1), np.float64(2.)):
            with self.subTest(value=invalid):
                with h5py.File(path, "r+") as f:
                    del f["Header"].attrs["Nids_ThisFile"]
                    f["Header"].attrs["Nids_ThisFile"] = invalid
                with self.assertRaisesRegex(MODULE.InvalidBootstrap, "invalid_header_Nids_ThisFile"):
                    MODULE.load_epoch(97, self.paths, self.expected, h5py)

    def test_incomplete_file_id_counters_cannot_claim_global_agreement(self):
        with h5py.File(self.paths[("groupcat", 97, 1)], "r+") as f:
            del f["Header"].attrs["Nids_ThisFile"]
        with self.assertRaisesRegex(MODULE.InvalidBootstrap, "incomplete_groupcat_file_id_counters"):
            MODULE.load_epoch(97, self.paths, self.expected, h5py)

    def test_duplicate_ids_across_chunks_are_rejected(self):
        with h5py.File(self.paths[("particle_ids", 97, 3)], "r+") as f:
            f["PartType1/ParticleIDs"][0] = 1
        with self.assertRaisesRegex(MODULE.InvalidBootstrap, "duplicate_particle_ids"):
            MODULE.load_epoch(97, self.paths, self.expected, h5py)

    def test_overlapping_membership_offsets_are_rejected(self):
        with h5py.File(self.paths[("offsets", 97, None)], "r+") as f:
            f["Group/SnapByType"][2, 1] = 3
        with self.assertRaisesRegex(MODULE.InvalidBootstrap, "group_length_offset_mismatch"):
            MODULE.load_epoch(97, self.paths, self.expected, h5py)

    def test_non_dmo_lengths_are_rejected(self):
        with h5py.File(self.paths[("groupcat", 97, 2)], "r+") as f:
            f["Group/GroupLenType"][0, 0] = 1
        with self.assertRaisesRegex(MODULE.InvalidBootstrap, "non_dmo_group_lengths"):
            MODULE.load_epoch(97, self.paths, self.expected, h5py)

    def test_changed_particle_mass_header_is_rejected(self):
        with h5py.File(self.paths[("particle_ids", 97, 1)], "r+") as f:
            f["Header"].attrs["MassTable"] = np.array([0, .25, 0, 0, 0, 0])
        with self.assertRaisesRegex(MODULE.InvalidBootstrap, "header_mismatch_mass"):
            MODULE.load_epoch(97, self.paths, self.expected, h5py)

    def test_external_hdf5_link_is_rejected(self):
        with h5py.File(self.paths[("groupcat", 97, 0)], "r+") as f:
            f["Unexpected"] = h5py.ExternalLink("unread-source.hdf5", "/secret")
        with self.assertRaisesRegex(MODULE.InvalidBootstrap, "nonlocal_hdf5_link"):
            MODULE.load_epoch(97, self.paths, self.expected, h5py)

    def test_changed_complete_id_set_fails_validation_and_preserves_partial_results(self):
        allpaths = dict(self.paths)
        allpaths.update(write_epoch(self.directory, 98, self.expected, list(range(2, 14))))
        allpaths.update(write_epoch(self.directory, 99, self.expected))
        config = dict(expected=self.expected, outputs=[97, 98, 99], reader_max_rss_bytes=3 * 1024**3)
        with patch.object(MODULE, "complete_provenance", return_value=(config, allpaths)):
            result = MODULE.validate(self.directory / "config.json", self.directory)
        self.assertEqual(result["outcome"], "failed")
        self.assertEqual(result["reason"], "particle_id_set_changed_between_outputs")
        self.assertEqual(len(result["epochs"]), 1)
        self.assertTrue((self.directory / "material-validation.json").is_file())

    def test_full_known_inventory_driver_retains_unqualified_physical_scope(self):
        allpaths = dict(self.paths)
        allpaths.update(write_epoch(self.directory, 98, self.expected, list(reversed(range(1, 13)))))
        allpaths.update(write_epoch(self.directory, 99, self.expected))
        config = dict(expected=self.expected, outputs=[97, 98, 99], reader_max_rss_bytes=3 * 1024**3)
        with patch.object(MODULE, "complete_provenance", return_value=(config, allpaths)):
            result = MODULE.validate(self.directory / "config.json", self.directory)
        self.assertEqual(result["outcome"], "inventory_checks_passed")
        self.assertTrue(result["identical_particle_id_sets"])
        self.assertFalse(result["log_orthopolic_transport_validated"])
        self.assertFalse(result["validation_target_assigned"])
        self.assertEqual(set(result["pairs"]), {"97->98", "98->99", "97->99"})
        self.assertEqual(result["cadence"]["host_diffuse_host_particles"], 4)


@unittest.skipIf(h5py is None, "optional cosmic HDF5 dependency is not installed")
class CompleteProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp.name)
        raw = self.directory / "raw"
        raw.mkdir()
        self.config = json.loads((ROOT / "configs/cosmic-development-2026-11-20.json").read_text())
        self.config["expected"] = expected()
        self.paths = {}
        for output in [97, 98, 99]:
            self.paths.update(write_epoch(raw, output, self.config["expected"]))
        self.config_path = self.directory / "manifest.json"
        self.config_path.write_text(json.dumps(self.config))
        (self.directory / "config.json").write_bytes(self.config_path.read_bytes())
        (self.directory / "acquisition_source.py").write_text("# synthetic frozen acquisition source\n")
        self.record = dict(schema_version=1, run="TNG50-4-Dark", development_only=True,
                           config_sha256=MODULE.sha256(self.config_path),
                           acquisition_source_sha256=MODULE.sha256(self.directory / "acquisition_source.py"),
                           aggregate_byte_cap=self.config["aggregate_byte_cap"], requests=[],
                           outcome="complete_downloaded")
        for entry in self.config["files"]:
            path = self.paths[(entry["kind"], entry["output"], entry["chunk"])]
            size, digest = path.stat().st_size, MODULE.sha256(path)
            self.record["requests"].append(dict(id=entry["id"], url=entry["url"],
                relative_path=entry["relative_path"], outcome="complete", file_bytes=size,
                body_bytes=size, sha256=digest, retained=True,
                responses=[dict(http_status=200, body_bytes=size, body_complete=True, body_sha256=digest)]))
        self.record["aggregate_body_bytes"] = sum(r["body_bytes"] for r in self.record["requests"])
        self.record["remaining_body_bytes"] = self.config["aggregate_byte_cap"] - self.record["aggregate_body_bytes"]
        bootstrap_ids = {f["id"] for f in self.config["files"] if f["bootstrap"]}
        bootstrap = copy.deepcopy(self.record)
        bootstrap["requests"] = [r for r in bootstrap["requests"] if r["id"] in bootstrap_ids]
        bootstrap["outcome"] = "bootstrap_downloaded"
        bootstrap["aggregate_body_bytes"] = sum(r["body_bytes"] for r in bootstrap["requests"])
        bootstrap["remaining_body_bytes"] = self.config["aggregate_byte_cap"] - bootstrap["aggregate_body_bytes"]
        (self.directory / "bootstrap_acquisition.json").write_text(json.dumps(bootstrap))
        (self.directory / "bootstrap_validation_source.py").write_text("# frozen synthetic validator\n")
        validation = dict(schema_version=1, outcome="passed", config_sha256=self.record["config_sha256"],
                          validator_source_sha256=MODULE.sha256(self.directory / "bootstrap_validation_source.py"),
                          acquisition_source_sha256=self.record["acquisition_source_sha256"],
                          acquisition_receipt_sha256=MODULE.sha256(self.directory / "bootstrap_acquisition.json"),
                          files={r["id"]: r["sha256"] for r in bootstrap["requests"]})
        (self.directory / "bootstrap_validation.json").write_text(json.dumps(validation))
        self.record["bootstrap_validation_sha256"] = MODULE.sha256(self.directory / "bootstrap_validation.json")
        self.save()

    def save(self):
        (self.directory / "acquisition.json").write_text(json.dumps(self.record))

    def tearDown(self):
        self.temp.cleanup()

    def test_complete_chain_verifies_all_files_and_bootstrap_snapshot(self):
        result = {"files": {}}
        config, paths = MODULE.complete_provenance(self.config_path, self.directory, result)
        self.assertEqual(len(paths), 27)
        self.assertEqual(len(result["files"]), 27)
        self.assertEqual(result["prior_body_bytes"], 0)

    def test_tampered_raw_file_is_rejected(self):
        path = next(iter(self.paths.values()))
        with path.open("ab") as f:
            f.write(b"tampered")
        with self.assertRaisesRegex(MODULE.InvalidBootstrap, "file_size_mismatch"):
            MODULE.complete_provenance(self.config_path, self.directory, {"files": {}})

    def test_bootstrap_snapshot_is_required_and_hash_checked(self):
        (self.directory / "bootstrap_acquisition.json").write_text("{}")
        with self.assertRaisesRegex(MODULE.InvalidBootstrap, "bootstrap_acquisition_snapshot_mismatch"):
            MODULE.complete_provenance(self.config_path, self.directory, {"files": {}})

    def test_prior_budget_cannot_be_forged_without_verified_chain(self):
        self.record["prior_body_bytes"] = 57
        self.record["aggregate_body_bytes"] += 57
        self.record["remaining_body_bytes"] -= 57
        self.save()
        with self.assertRaisesRegex(MODULE.InvalidBootstrap, "unverified_prior_budget"):
            MODULE.complete_provenance(self.config_path, self.directory, {"files": {}})

    def test_verified_prior_error_bytes_are_carried_once(self):
        entry = next(f for f in self.config["files"] if f["kind"] == "offsets" and f["output"] == 97)
        (self.directory / "prior_config.json").write_bytes(self.config_path.read_bytes())
        (self.directory / "prior_acquisition_source.py").write_text("# prior source\n")
        prior = dict(run=self.config["run"], aggregate_byte_cap=self.config["aggregate_byte_cap"],
                     aggregate_body_bytes=57, config_sha256=self.record["config_sha256"],
                     acquisition_source_sha256=MODULE.sha256(self.directory / "prior_acquisition_source.py"),
                     stages=[dict(stage="bootstrap")], outcome="unapproved_http_status",
                     requests=[dict(id=entry["id"], url=entry["url"], relative_path=entry["relative_path"],
                                    file_bytes=0, retained=False, outcome="unapproved_http_status", body_bytes=57,
                                    responses=[dict(body_bytes=57)])])
        (self.directory / "prior_acquisition.json").write_text(json.dumps(prior))
        self.record["manual_continuation"] = True
        self.record["prior_body_bytes"] = 57
        self.record["prior_acquisition_sha256"] = MODULE.sha256(self.directory / "prior_acquisition.json")
        self.record["aggregate_body_bytes"] += 57
        self.record["remaining_body_bytes"] -= 57
        self.save()
        result = {"files": {}}
        MODULE.complete_provenance(self.config_path, self.directory, result)
        self.assertEqual(result["prior_body_bytes"], 57)


if __name__ == "__main__":
    unittest.main()
