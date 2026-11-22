"""Offline tiny HDF5 fixtures for the development-only binary schema gate."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

try:
    import h5py
except ImportError:
    h5py = None


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "cosmic_bootstrap", ROOT / "experiments/check_cosmic_development_bootstrap.py")
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


@unittest.skipIf(h5py is None, "optional h5py dependency required for HDF5 fixtures")
class BootstrapTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.out = self.root / "acquired"
        (self.out / "raw").mkdir(parents=True)
        self.config_path = self.root / "config.json"
        expected = dict(num_dm=20, mass_dm=0.1, boxsize=35000.0, hubble=0.6774,
                        omega_0=0.3089, omega_L=0.6911, omega_B=0.0486,
                        num_files_snapshot=4, num_files_groupcat=4,
                        snapshots={"97": dict(redshift=0.02, num_groups=8, num_subgroups=10)})
        self.config = dict(schema_version=1, run="TNG50-4-Dark", outputs=[97, 98, 99],
                           aggregate_byte_cap=805306368, expected=expected, files=[])
        for kind in ("offsets", "groupcat", "particle_ids"):
            ident = kind + "-97" + ("" if kind == "offsets" else "-0")
            self.config["files"].append(dict(id=ident, kind=kind, output=97,
                chunk=None if kind == "offsets" else 0, bootstrap=True,
                relative_path="raw/" + ident + ".hdf5", byte_cap=64 * 1024 ** 2,
                url="https://www.tng-project.org/api/TNG50-4-Dark/files/" + ident + ".hdf5"))
        config_bytes = (json.dumps(self.config) + "\n").encode()
        self.config_path.write_bytes(config_bytes)
        (self.out / "config.json").write_bytes(config_bytes)
        (self.out / "acquisition_source.py").write_text("# frozen mock acquisition\n")
        self.make_snapshot()
        self.make_groupcat()
        self.make_offsets()
        self.refresh_receipt()

    def path(self, kind):
        return self.out / next(item["relative_path"] for item in self.config["files"]
                               if item["kind"] == kind)

    def make_snapshot(self):
        with h5py.File(self.path("particle_ids"), "w") as handle:
            header = handle.create_group("Header").attrs
            for name, value in dict(
                NumPart_ThisFile=[0, 6, 0, 0, 0, 0], NumPart_Total=[0, 20, 0, 0, 0, 0],
                NumPart_Total_HighWord=[0] * 6, MassTable=[0.0, 0.1, 0.0, 0.0, 0.0, 0.0],
                BoxSize=35000.0, HubbleParam=0.6774, Omega0=0.3089, OmegaLambda=0.6911,
                OmegaBaryon=0.0486, NumFilesPerSnapshot=4, Redshift=0.02, Time=1 / 1.02,
                UnitLength_in_cm=3.085678e21, UnitMass_in_g=1.989e43,
                UnitVelocity_in_cm_per_s=1e5, CutoutRequest="PartType1=ParticleIDs"
            ).items():
                header[name] = value
            handle.create_dataset("PartType1/ParticleIDs", data=np.arange(6, dtype=np.uint64))

    def make_groupcat(self):
        with h5py.File(self.path("groupcat"), "w") as handle:
            header = handle.create_group("Header").attrs
            for name, value in dict(Ngroups_ThisFile=2, Nsubgroups_ThisFile=3,
                                    Ngroups_Total=8, Nsubgroups_Total=10, NumFiles=4,
                                    Redshift=0.02, Time=1 / 1.02).items():
                header[name] = value
            lengths = np.zeros((2, 6), dtype=np.int32)
            lengths[:, 1] = [7, 2]  # First FoF host straddles the six-ID snapshot chunk.
            handle.create_dataset("Group/GroupLenType", data=lengths)
            handle.create_dataset("Group/GroupMass", data=np.array([0.7, 0.2], dtype=np.float32))

    def make_offsets(self):
        with h5py.File(self.path("offsets"), "w") as handle:
            file_offsets = np.zeros((6, 4), dtype=np.int64)
            file_offsets[1] = [0, 6, 11, 16]
            group_offsets = np.zeros((8, 6), dtype=np.int64)
            group_offsets[:, 1] = [0, 7, 9, 10, 11, 12, 13, 14]
            handle.create_dataset("FileOffsets/SnapByType", data=file_offsets)
            handle.create_dataset("Group/SnapByType", data=group_offsets)
            handle.create_dataset("FileOffsets/Group", data=[0, 2, 4, 6])
            handle.create_dataset("FileOffsets/Subhalo", data=[0, 3, 6, 8])

    def refresh_receipt(self):
        requests = []
        for planned in self.config["files"]:
            path = self.out / planned["relative_path"]
            size, digest = path.stat().st_size, CHECK.sha256(path)
            requests.append(dict(id=planned["id"], outcome="complete",
                                 url=planned["url"], relative_path=planned["relative_path"],
                                 file_bytes=size, body_bytes=size, sha256=digest,
                                 responses=[dict(http_status=200, body_bytes=size,
                                                 body_complete=True, body_sha256=digest)]))
        self.receipt = dict(schema_version=1, outcome="bootstrap_downloaded", development_only=True,
                            config_sha256=CHECK.sha256(self.config_path),
                            acquisition_source_sha256=CHECK.sha256(self.out / "acquisition_source.py"),
                            aggregate_body_bytes=sum(item["body_bytes"] for item in requests),
                            requests=requests)
        self.save_receipt()

    def save_receipt(self):
        (self.out / "acquisition.json").write_text(json.dumps(self.receipt))

    def validate(self, expected="passed", reason=None):
        result = CHECK.validate(self.config_path, self.out)
        self.assertEqual(result["outcome"], expected, result)
        self.assertEqual(json.loads((self.out / "bootstrap-validation.json").read_text()), result)
        if reason:
            self.assertEqual(result["reason"], reason)
        return result

    def test_valid_straddling_chunk_passes_without_claiming_whole_closure(self):
        result = self.validate()
        self.assertEqual(set(result["files"]), {item["id"] for item in self.config["files"]})
        self.assertEqual(result["observations"]["checks"]["ids_in_bootstrap_chunk"], 6)
        self.assertFalse(result["observations"]["checks"]["whole_inventory_closure_tested"])
        self.assertFalse(result["observations"]["checks"]["log_orthopolic_transport_tested"])
        self.assertEqual(result["observations"]["offsets"]["datasets"]["FileOffsets/SnapByType"]["shape"], [6, 4])
        self.assertEqual(result["observations"]["offsets"]["snapshot_offset_layout"], "type_by_chunk")
        self.assertEqual(result["observations"]["particle_ids"]["header"]["CutoutRequest"], "PartType1=ParticleIDs")
        self.assertEqual(result["observations"]["particle_ids"]["header"]["UnitMass_in_g"], 1.989e43)

    def test_file_corruption_fails_before_opening_hdf5(self):
        path = self.path("particle_ids")
        raw = bytearray(path.read_bytes())
        raw[-1] ^= 1
        path.write_bytes(raw)
        self.validate("failed", "file_hash_mismatch")

    def test_frozen_source_change_fails(self):
        (self.out / "acquisition_source.py").write_text("# changed\n")
        self.validate("failed", "acquisition_provenance_mismatch")

    def test_config_change_fails(self):
        self.config_path.write_bytes(self.config_path.read_bytes() + b" ")
        self.validate("failed", "config_snapshot_mismatch")

    def test_partial_acquisition_fails(self):
        self.receipt["requests"][0]["outcome"] = "incomplete_response"
        self.save_receipt()
        self.validate("failed", "incomplete_or_mismatched_file")

    def make_prior(self):
        planned = self.config["files"][0]
        prior = dict(self.receipt)
        prior.update(run=self.config["run"], aggregate_byte_cap=self.config["aggregate_byte_cap"],
                     aggregate_body_bytes=57, outcome="unapproved_http_status",
                     stages=[dict(stage="bootstrap", outcome="unapproved_http_status")],
                     requests=[dict(id=planned["id"], url=planned["url"],
                                    relative_path=planned["relative_path"], body_bytes=57,
                                    file_bytes=0, retained=False, outcome="unapproved_http_status",
                                    responses=[dict(body_bytes=57, http_status=406)])])
        (self.out / "prior_acquisition.json").write_text(json.dumps(prior))
        for before, after in (("config.json", "prior_config.json"),
                              ("acquisition_source.py", "prior_acquisition_source.py")):
            (self.out / after).write_bytes((self.out / before).read_bytes())
        self.receipt.update(prior_body_bytes=57, manual_continuation=True,
                            prior_acquisition_sha256=CHECK.sha256(self.out / "prior_acquisition.json"))
        self.receipt["aggregate_body_bytes"] += 57
        self.save_receipt()

    def test_explicit_prior_failed_attempt_counts_toward_budget(self):
        self.make_prior()
        result = self.validate()
        self.assertEqual(result["prior_body_bytes"], 57)

    def test_prior_receipt_tampering_fails(self):
        self.make_prior()
        prior = self.out / "prior_acquisition.json"
        prior.write_bytes(prior.read_bytes() + b" ")
        self.validate("failed", "prior_receipt_hash_mismatch")

    def test_inherited_bytes_without_provenance_fail(self):
        self.receipt["prior_body_bytes"] = 57
        self.receipt["aggregate_body_bytes"] += 57
        self.save_receipt()
        self.validate("failed", "unverified_prior_budget")

    def test_response_counts_and_digest_are_checked(self):
        self.receipt["requests"][0]["responses"][0]["body_sha256"] = "0" * 64
        self.save_receipt()
        self.validate("failed", "response_byte_or_hash_mismatch")

    def test_extra_particle_array_fails(self):
        with h5py.File(self.path("particle_ids"), "r+") as handle:
            handle.create_dataset("PartType1/Coordinates", shape=(6, 3), dtype="f4")
        self.refresh_receipt()
        self.validate("failed", "particle_selection_not_id_only")

    def test_small_integer_ids_fail(self):
        with h5py.File(self.path("particle_ids"), "r+") as handle:
            del handle["PartType1/ParticleIDs"]
            handle.create_dataset("PartType1/ParticleIDs", data=np.arange(6, dtype=np.uint32))
        self.refresh_receipt()
        self.validate("failed", "particle_ids_not_uint64")

    def test_time_is_checked_against_scale_factor(self):
        with h5py.File(self.path("particle_ids"), "r+") as handle:
            handle["Header"].attrs["Time"] = 0.02
        self.refresh_receipt()
        self.validate("failed", "header_mismatch_Time")

    def test_wrong_unit_factor_fails(self):
        with h5py.File(self.path("particle_ids"), "r+") as handle:
            handle["Header"].attrs["UnitMass_in_g"] = 1.989e33
        self.refresh_receipt()
        self.validate("failed", "header_mismatch_UnitMass_in_g")

    def test_nonfinite_header_retains_valid_failure_json(self):
        with h5py.File(self.path("particle_ids"), "r+") as handle:
            handle["Header"].attrs["HubbleParam"] = np.nan
        self.refresh_receipt()
        result = self.validate("failed", "header_mismatch_HubbleParam")
        self.assertEqual(result["observations"]["particle_ids"]["header"]["HubbleParam"], "nan")

    def test_cosmology_mismatch_fails(self):
        with h5py.File(self.path("particle_ids"), "r+") as handle:
            handle["Header"].attrs["Omega0"] = 0.4
        self.refresh_receipt()
        self.validate("failed", "header_mismatch_Omega0")

    def test_missing_highword_is_not_assumed_zero(self):
        with h5py.File(self.path("particle_ids"), "r+") as handle:
            del handle["Header"].attrs["NumPart_Total_HighWord"]
        self.refresh_receipt()
        self.validate("failed", "missing_header_NumPart_Total_HighWord")

    def test_observed_chunk_by_type_offset_layout_passes_and_is_recorded(self):
        with h5py.File(self.path("offsets"), "r+") as handle:
            array = handle["FileOffsets/SnapByType"][:].T
            del handle["FileOffsets/SnapByType"]
            handle.create_dataset("FileOffsets/SnapByType", data=array)
        self.refresh_receipt()
        result = self.validate()
        self.assertEqual(result["observations"]["offsets"]["datasets"]["FileOffsets/SnapByType"]["shape"], [4, 6])
        self.assertEqual(result["observations"]["offsets"]["snapshot_offset_layout"], "chunk_by_type")

    def test_other_snapshot_offset_shape_fails(self):
        with h5py.File(self.path("offsets"), "r+") as handle:
            del handle["FileOffsets/SnapByType"]
            handle.create_dataset("FileOffsets/SnapByType", shape=(4, 4), dtype="i8")
        self.refresh_receipt()
        self.validate("failed", "invalid_snapshot_offset_shape")

    def test_next_group_boundary_fails(self):
        with h5py.File(self.path("offsets"), "r+") as handle:
            handle["Group/SnapByType"][2, 1] = 10
        self.refresh_receipt()
        self.validate("failed", "next_group_boundary_mismatch")

    def test_missing_hdf5_header_produces_failure_receipt(self):
        with h5py.File(self.path("groupcat"), "r+") as handle:
            del handle["Header"]
        self.refresh_receipt()
        self.validate("failed", "missing_header_group")

    def test_external_hdf5_link_is_rejected(self):
        with h5py.File(self.path("particle_ids"), "r+") as handle:
            handle["external"] = h5py.ExternalLink("elsewhere.hdf5", "/data")
        self.refresh_receipt()
        self.validate("failed", "nonlocal_hdf5_link")

    def test_existing_verdict_is_never_overwritten(self):
        self.validate()
        original = (self.out / "bootstrap-validation.json").read_bytes()
        with self.assertRaises(FileExistsError):
            CHECK.validate(self.config_path, self.out)
        self.assertEqual((self.out / "bootstrap-validation.json").read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
