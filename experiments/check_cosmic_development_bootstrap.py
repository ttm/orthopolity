"""Check three frozen development HDF5 files before completing acquisition.

This checks schema, provenance and the available chunk boundaries. It neither
closes the whole particle inventory nor tests log-orthopolic transport.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import platform

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "configs/cosmic-development-2026-11-20.json"
# TNG's base cgs unit factors; the h and scale-factor conventions remain
# separate (mass in 1e10 solar masses / h, positions in comoving kpc / h).
UNIT_CONVENTIONS = {"UnitLength_in_cm": 3.085678e21,
                    "UnitMass_in_g": 1.989e43,
                    "UnitVelocity_in_cm_per_s": 1e5}


class InvalidBootstrap(Exception):
    """A local, fixed explanation for a failed prerequisite."""


def require(condition, reason):
    if not condition:
        raise InvalidBootstrap(reason)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path):
    value = json.loads(path.read_bytes())
    require(isinstance(value, dict), "invalid_json_object")
    return value


def safe_path(directory, relative):
    require(isinstance(relative, str) and relative.startswith("raw/")
            and "\\" not in relative
            and all(part not in ("", ".", "..") for part in relative.split("/")),
            "invalid_raw_path")
    path = directory / relative
    require(path.resolve() == directory.resolve() / relative, "raw_path_symlink")
    return path


def prior_budget(config, receipt, directory, config_hash):
    """Verify the copied failed attempt before inheriting its consumed bytes."""
    amount = receipt.get("prior_body_bytes", 0)
    require(type(amount) is int and amount >= 0, "invalid_prior_budget")
    if receipt.get("manual_continuation") is not True:
        require(amount == 0 and "prior_acquisition_sha256" not in receipt,
                "unverified_prior_budget")
        return 0
    prior_path = directory / "prior_acquisition.json"
    require(sha256(prior_path) == receipt.get("prior_acquisition_sha256"),
            "prior_receipt_hash_mismatch")
    prior = load_json(prior_path)
    require(sha256(directory / "prior_config.json") == config_hash
            and prior.get("config_sha256") == config_hash
            and sha256(directory / "prior_acquisition_source.py")
            == prior.get("acquisition_source_sha256"), "prior_provenance_mismatch")
    require(prior.get("run") == config["run"]
            and prior.get("aggregate_byte_cap") == config["aggregate_byte_cap"]
            and prior.get("aggregate_body_bytes") == amount
            and prior.get("prior_body_bytes", 0) == 0
            and not prior.get("manual_continuation", False), "invalid_prior_scope")
    stages = prior.get("stages")
    require(isinstance(stages, list) and len(stages) == 1
            and isinstance(stages[0], dict) and stages[0].get("stage") == "bootstrap"
            and prior.get("outcome") not in (None, "initialized", "bootstrap_downloaded", "complete_downloaded"),
            "prior_attempt_not_failed_bootstrap")
    requests = prior.get("requests")
    require(isinstance(requests, list) and requests, "invalid_prior_requests")
    planned = {entry["id"]: entry for entry in config["files"] if entry.get("bootstrap") is True}
    counted, seen = 0, set()
    for item in requests:
        require(isinstance(item, dict) and item.get("id") in planned
                and item["id"] not in seen, "invalid_prior_request")
        entry = planned[item["id"]]
        require(item.get("file_bytes") == 0 and item.get("retained") is False
                and item.get("outcome") != "complete"
                and item.get("url") == entry["url"]
                and item.get("relative_path") == entry["relative_path"], "prior_contains_binary_or_mismatch")
        body = item.get("body_bytes")
        require(type(body) is int and 0 <= body <= entry["byte_cap"], "invalid_prior_request_bytes")
        responses = item.get("responses")
        require(isinstance(responses, list)
                and all(isinstance(r, dict) and type(r.get("body_bytes")) is int
                        and r["body_bytes"] >= 0 for r in responses)
                and sum(r["body_bytes"] for r in responses) == body,
                "invalid_prior_response_bytes")
        counted += body
        seen.add(item["id"])
    require(counted == amount <= config["aggregate_byte_cap"], "invalid_prior_budget")
    return amount


def provenance(config_path, directory, result):
    config = load_json(config_path)
    receipt = load_json(directory / "acquisition.json")
    result["config_sha256"] = sha256(config_path)
    result["acquisition_source_sha256"] = sha256(directory / "acquisition_source.py")
    require(sha256(directory / "config.json") == result["config_sha256"],
            "config_snapshot_mismatch")
    for key in ("config_sha256", "acquisition_source_sha256"):
        require(receipt.get(key) == result[key], "acquisition_provenance_mismatch")
    require(config.get("schema_version") == 1 and config.get("run") == "TNG50-4-Dark"
            and config.get("outputs") == [97, 98, 99], "unexpected_development_scope")
    require(receipt.get("outcome") == "bootstrap_downloaded"
            and receipt.get("development_only") is True, "bootstrap_not_downloaded")
    entries = config.get("files")
    require(isinstance(entries, list) and all(isinstance(entry, dict) for entry in entries),
            "invalid_file_inventory")
    planned = [entry for entry in entries if entry.get("bootstrap") is True]
    require(len(planned) == 3 and {entry.get("kind") for entry in planned}
            == {"offsets", "groupcat", "particle_ids"}, "invalid_bootstrap_inventory")
    require(all(entry.get("output") == 97 and entry.get("chunk")
                == (None if entry["kind"] == "offsets" else 0) for entry in planned),
            "invalid_bootstrap_identity")
    require(len({entry["id"] for entry in planned}) == 3, "duplicate_bootstrap_id")
    requests = receipt.get("requests")
    require(isinstance(requests, list) and len(requests) == 3
            and all(isinstance(item, dict) for item in requests), "invalid_acquisition_requests")
    by_id = {item.get("id"): item for item in requests}
    require(set(by_id) == {entry["id"] for entry in planned}, "acquisition_inventory_mismatch")
    total = 0
    paths = {}
    for entry in planned:
        item = by_id[entry["id"]]
        require(item.get("outcome") == "complete"
                and item.get("relative_path") == entry.get("relative_path")
                and item.get("url") == entry.get("url"), "incomplete_or_mismatched_file")
        path = safe_path(directory, entry["relative_path"])
        size, body = item.get("file_bytes"), item.get("body_bytes")
        require(type(size) is int and type(body) is int
                and 0 < size <= body <= entry["byte_cap"], "invalid_file_byte_count")
        require(path.is_file() and path.stat().st_size == size, "file_size_mismatch")
        actual = sha256(path)
        require(actual == item.get("sha256"), "file_hash_mismatch")
        responses = item.get("responses")
        require(isinstance(responses, list) and 1 <= len(responses) <= 2,
                "invalid_response_chain")
        require(all(isinstance(r, dict) and type(r.get("body_bytes")) is int and r["body_bytes"] >= 0
                    and r.get("body_complete") is True for r in responses),
                "incomplete_response_chain")
        require(sum(r["body_bytes"] for r in responses) == body
                and responses[-1].get("http_status") == 200
                and responses[-1]["body_bytes"] == size
                and responses[-1].get("body_sha256") == actual,
                "response_byte_or_hash_mismatch")
        total += body
        result["files"][entry["id"]] = actual
        paths[entry["kind"]] = path
    inherited = prior_budget(config, receipt, directory, result["config_sha256"])
    result["prior_body_bytes"] = inherited
    require(total + inherited == receipt.get("aggregate_body_bytes")
            and total + inherited <= config["aggregate_byte_cap"], "aggregate_budget_mismatch")
    result["acquisition_receipt_sha256"] = sha256(directory / "acquisition.json")
    return config, paths


def json_value(value):
    value = np.asarray(value)
    plain = value.item() if value.ndim == 0 else value.tolist()

    def clean(item):
        if isinstance(item, list):
            return [clean(child) for child in item]
        if isinstance(item, float) and not math.isfinite(item):
            return str(item)
        return item
    return clean(plain)


def scalar(attrs, name, expected, observed, integer=False):
    require(name in attrs, "missing_header_" + name)
    array = np.asarray(attrs[name])
    require(array.size == 1 and array.dtype.kind in "iuf", "invalid_header_" + name)
    value = array.reshape(-1)[0]
    observed[name] = json_value(array)
    if integer:
        require(array.dtype.kind in "iu" and int(value) == expected,
                "header_mismatch_" + name)
    else:
        # Fixed allowance for serialization/attribute rounding, using its stored
        # precision; this is not a tolerance fitted to a physical discrepancy.
        eps = np.finfo(array.dtype).eps if array.dtype.kind == "f" else np.finfo(float).eps
        tolerance = 8 * max(eps, np.finfo(float).eps) * max(1.0, abs(float(expected)))
        require(math.isfinite(float(value)) and abs(float(value) - expected) <= tolerance,
                "header_mismatch_" + name)
    return value


def vector(attrs, name, observed, integer=False):
    require(name in attrs, "missing_header_" + name)
    array = np.asarray(attrs[name])
    require(array.shape == (6,) and array.dtype.kind in ("iu" if integer else "f"),
            "invalid_header_" + name)
    require(np.all(np.isfinite(array)) and np.all(array >= 0), "invalid_header_" + name)
    observed[name] = json_value(array)
    return array


def dataset(handle, name, shape, kind):
    require(name in handle, "missing_dataset_" + name)
    value = handle[name]
    require(hasattr(value, "dtype") and value.shape == shape and value.dtype.kind in kind,
            "invalid_dataset_" + name)
    require(not value.is_virtual and value.external is None, "external_dataset_" + name)
    return value


def inspect_schema(handle, h5py):
    schema = {}

    def visit(group, prefix="", ancestors=()):
        address = h5py.h5o.get_info(group.id).addr
        require(address not in ancestors, "cyclic_hdf5_group")
        for name in group:
            path = prefix + name
            require(isinstance(group.get(name, getlink=True), h5py.HardLink),
                    "nonlocal_hdf5_link")
            item = group[name]
            if isinstance(item, h5py.Dataset):
                require(not item.is_virtual and item.external is None, "external_hdf5_dataset")
                schema[path] = {"shape": list(item.shape), "dtype": str(item.dtype)}
            elif isinstance(item, h5py.Group):
                visit(item, path + "/", ancestors + (address,))
    visit(handle)
    return schema


def normalize_snapshot_offsets(values, num_chunks):
    """Return type-by-chunk offsets and the unambiguous stored orientation.

    The TNG table describes [6, chunks], whereas the acquired output-97 file
    stores [chunks, 6]. Accept these two layouts explicitly; never infer an
    orientation from the numerical values or silently reshape another array.
    """
    values = np.asarray(values)
    require(values.dtype.kind in "iu", "invalid_snapshot_offset_dtype")
    require(num_chunks != 6, "ambiguous_snapshot_offset_orientation")
    if values.shape == (6, num_chunks):
        return values, "type_by_chunk"
    if values.shape == (num_chunks, 6):
        return values.T, "chunk_by_type"
    raise InvalidBootstrap("invalid_snapshot_offset_shape")


def binary_checks(paths, expected, observations, h5py):
    output = expected["snapshots"]["97"]
    with h5py.File(paths["particle_ids"], "r") as snap, \
            h5py.File(paths["groupcat"], "r") as cats, \
            h5py.File(paths["offsets"], "r") as offsets:
        for kind, handle in (("particle_ids", snap), ("groupcat", cats), ("offsets", offsets)):
            observations[kind] = {"datasets": inspect_schema(handle, h5py), "header": {}}
        particle_fields = {name for name in observations["particle_ids"]["datasets"]
                           if name.split("/")[0].startswith("PartType")}
        require(particle_fields == {"PartType1/ParticleIDs"}, "particle_selection_not_id_only")
        require("Header" in snap and "Header" in cats, "missing_header_group")
        header = snap["Header"].attrs
        observed = observations["particle_ids"]["header"]
        counts = vector(header, "NumPart_ThisFile", observed, integer=True)
        low = vector(header, "NumPart_Total", observed, integer=True)
        high = vector(header, "NumPart_Total_HighWord", observed, integer=True)
        totals = [int(a) + (int(b) << 32) for a, b in zip(low, high)]
        require(totals == [0, expected["num_dm"], 0, 0, 0, 0], "particle_inventory_mismatch")
        require(0 < int(counts[1]) <= expected["num_dm"]
                and np.all(counts[[0, 2, 3, 4, 5]] == 0), "non_dmo_chunk_inventory")
        ids = dataset(snap, "PartType1/ParticleIDs", (int(counts[1]),), "u")
        require(ids.dtype.itemsize == 8, "particle_ids_not_uint64")
        mass = vector(header, "MassTable", observed)
        require(np.all(mass[[0, 2, 3, 4, 5]] == 0), "non_dmo_mass_table")
        scalar({"mass_dm": mass[1]}, "mass_dm", expected["mass_dm"], {}, False)
        for attr, key in (("BoxSize", "boxsize"), ("HubbleParam", "hubble"),
                          ("Omega0", "omega_0"), ("OmegaLambda", "omega_L")):
            scalar(header, attr, expected[key], observed)
        scalar(header, "NumFilesPerSnapshot", expected["num_files_snapshot"], observed, True)
        scalar(header, "Redshift", output["redshift"], observed)
        scalar(header, "Time", 1 / (1 + output["redshift"]), observed)
        if "OmegaBaryon" in header:
            scalar(header, "OmegaBaryon", expected["omega_B"], observed)
        for attr, expected_unit in UNIT_CONVENTIONS.items():
            scalar(header, attr, expected_unit, observed)
        require("CutoutRequest" in header, "missing_header_CutoutRequest")
        selection = np.asarray(header["CutoutRequest"])
        require(selection.ndim == 0, "invalid_header_CutoutRequest")
        selection = selection.item()
        if isinstance(selection, bytes):
            selection = selection.decode("utf-8")
        require(selection == "PartType1=ParticleIDs", "header_mismatch_CutoutRequest")
        observed["CutoutRequest"] = selection

        cheader, cobserved = cats["Header"].attrs, observations["groupcat"]["header"]
        for attr, value in (("Ngroups_Total", output["num_groups"]),
                            ("Nsubgroups_Total", output["num_subgroups"]),
                            ("NumFiles", expected["num_files_groupcat"])):
            scalar(cheader, attr, value, cobserved, True)
        scalar(cheader, "Redshift", output["redshift"], cobserved)
        scalar(cheader, "Time", 1 / (1 + output["redshift"]), cobserved)
        for attr, key in (("BoxSize", "boxsize"), ("HubbleParam", "hubble"),
                          ("Omega0", "omega_0"), ("OmegaLambda", "omega_L")):
            if attr in cheader:
                scalar(cheader, attr, expected[key], cobserved)
        require("Ngroups_ThisFile" in cheader, "missing_header_Ngroups_ThisFile")
        group_count = np.asarray(cheader["Ngroups_ThisFile"])
        require(group_count.size == 1 and group_count.dtype.kind in "iu",
                "invalid_header_Ngroups_ThisFile")
        ng = int(group_count.reshape(-1)[0])
        require(0 < ng <= output["num_groups"], "invalid_chunk_group_count")
        cobserved["Ngroups_ThisFile"] = ng
        lengths = dataset(cats, "Group/GroupLenType", (ng, 6), "iu")[:]
        require(np.all(lengths >= 0) and np.all(lengths[:, [0, 2, 3, 4, 5]] == 0)
                and np.all(lengths[:, 1] > 0)
                and sum(map(int, lengths[:, 1])) <= expected["num_dm"], "non_dmo_group_lengths")
        masses = dataset(cats, "Group/GroupMass", (ng,), "f")[:]
        require(np.all(np.isfinite(masses)) and np.all(masses > 0), "invalid_group_masses")

        require("FileOffsets/SnapByType" in offsets, "missing_dataset_FileOffsets/SnapByType")
        offset_dataset = offsets["FileOffsets/SnapByType"]
        require(hasattr(offset_dataset, "dtype"), "invalid_dataset_FileOffsets/SnapByType")
        fo, layout = normalize_snapshot_offsets(offset_dataset[:], expected["num_files_snapshot"])
        observations["offsets"]["snapshot_offset_layout"] = layout
        observations["offsets"]["normalized_snapshot_offset_layout"] = "type_by_chunk"
        go = dataset(offsets, "Group/SnapByType", (output["num_groups"], 6), "iu")[:]
        fg = dataset(offsets, "FileOffsets/Group", (expected["num_files_groupcat"],), "iu")[:]
        fs = dataset(offsets, "FileOffsets/Subhalo", (expected["num_files_groupcat"],), "iu")[:]
        require(np.all(fo >= 0) and np.all(fo[:, 0] == 0)
                and np.all(fo[[0, 2, 3, 4, 5], :] == 0)
                and np.all(fo[1, 1:] >= fo[1, :-1]) and np.all(fo[1] < expected["num_dm"]),
                "invalid_snapshot_chunk_offsets")
        require(int(fo[1, 1]) == int(counts[1]), "snapshot_chunk_boundary_mismatch")
        require(np.all(fg >= 0) and int(fg[0]) == 0 and np.all(fg[1:] >= fg[:-1])
                and np.all(fg < output["num_groups"])
                and int(fg[1]) == ng, "groupcat_chunk_boundary_mismatch")
        require(np.all(fs >= 0) and int(fs[0]) == 0 and np.all(fs[1:] >= fs[:-1])
                and np.all(fs <= output["num_subgroups"]), "invalid_subhalo_chunk_offsets")
        scalar(cheader, "Nsubgroups_ThisFile", int(fs[1]), cobserved, True)
        require(np.all(go >= 0) and np.all(go[:, [0, 2, 3, 4, 5]] == 0)
                and int(go[0, 1]) == 0 and np.all(go[1:, 1] >= go[:-1, 1])
                and np.all(go[:, 1] < expected["num_dm"]), "invalid_group_offsets")
        # Available group lengths can straddle the particle-chunk boundary;
        # compare global offsets, never force the chunk to close by itself.
        prefix = np.cumsum(lengths[:, 1], dtype=np.uint64)
        require(np.all(prefix <= expected["num_dm"])
                and np.array_equal(go[1:ng, 1], prefix[:-1]), "group_length_offset_mismatch")
        if ng < output["num_groups"]:
            require(int(go[ng, 1]) == int(prefix[-1]), "next_group_boundary_mismatch")
        observations["checks"] = {
            "ids_in_bootstrap_chunk": int(counts[1]), "groups_in_bootstrap_chunk": ng,
            "particle_ids_values_read": False, "whole_inventory_closure_tested": False,
            "group_mass_rounding_comparison_tested": False,
            "log_orthopolic_transport_tested": False,
            "units": {"mass": "1e10 solar masses / h", "box": "comoving kpc / h",
                      "Time": "scale factor"},
        }


def validate(config_path, directory):
    directory = Path(directory)
    result = dict(schema_version=1, outcome="failed", development_only=True, files={},
                  reference_measure="logarithmic host mass; log-orthopolic collisionless total-matter candidate",
                  validator_source_sha256=sha256(Path(__file__)),
                  started_utc=datetime.now(timezone.utc).isoformat(), observations={},
                  versions={"python": platform.python_version(), "numpy": np.__version__})
    try:
        config, paths = provenance(Path(config_path), directory, result)
        import h5py
        result["versions"].update(h5py=h5py.__version__, hdf5=h5py.version.hdf5_version)
        binary_checks(paths, config["expected"], result["observations"], h5py)
        result["outcome"] = "passed"
    except InvalidBootstrap as exc:
        result["reason"] = str(exc)
    except (ImportError, OSError, ValueError, KeyError, TypeError, OverflowError) as exc:
        result["reason"] = "validation_exception_" + type(exc).__name__
    result["finished_utc"] = datetime.now(timezone.utc).isoformat()
    output = directory / "bootstrap-validation.json"
    # Validation is a recorded gate: never silently replace an earlier verdict.
    with output.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        result = validate(args.config, args.output_dir)
    except OSError as exc:
        print(json.dumps({"outcome": "failed", "reason": type(exc).__name__}))
        return 1
    print(json.dumps({"outcome": result["outcome"], "reason": result.get("reason")}))
    return 0 if result["outcome"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
