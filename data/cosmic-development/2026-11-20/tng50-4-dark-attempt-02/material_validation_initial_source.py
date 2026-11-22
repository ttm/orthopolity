"""Audit complete TNG development inventories and descriptive endpoint transfers.

Integer closure is a reader identity. These diagnostics do not validate local
transport, an independent abundance prediction, or a log-orthopolic law.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import platform
import resource
import sys

import numpy as np

try:
    from experiments.check_cosmic_development_bootstrap import (
        InvalidBootstrap, dataset, inspect_schema, load_json, require, safe_path,
        scalar, sha256, vector, prior_budget, normalize_snapshot_offsets,
    )
except ModuleNotFoundError:
    from check_cosmic_development_bootstrap import (
        InvalidBootstrap, dataset, inspect_schema, load_json, require, safe_path,
        scalar, sha256, vector, prior_budget, normalize_snapshot_offsets,
    )

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "configs/cosmic-development-2026-11-20.json"
BLOCK = 262144
# Fixed descriptive categories, not a selected plateau or scientific cutoff.
JUMP_EDGES = np.log(np.array([1., 1.25, 2., 4., 10., np.inf]))


def peak_rss_bytes():
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return int(value if sys.platform == "darwin" else value * 1024)


def complete_provenance(config_path, directory, result):
    config, receipt = load_json(config_path), load_json(directory / "acquisition.json")
    require(config.get("schema_version") == 1 and config.get("run") == "TNG50-4-Dark"
            and config.get("outputs") == [97, 98, 99]
            and config.get("development_only") is True
            and config.get("validation_target_assigned") is False,
            "unexpected_development_scope")
    result["config_sha256"] = sha256(config_path)
    result["acquisition_source_sha256"] = sha256(directory / "acquisition_source.py")
    require(sha256(directory / "config.json") == result["config_sha256"], "config_snapshot_mismatch")
    for key in ("config_sha256", "acquisition_source_sha256"):
        require(receipt.get(key) == result[key], "acquisition_provenance_mismatch")
    require(receipt.get("outcome") == "complete_downloaded"
            and receipt.get("development_only") is True, "complete_acquisition_required")
    validation_path = directory / "bootstrap_validation.json"
    validation = load_json(validation_path)
    require(sha256(validation_path) == receipt.get("bootstrap_validation_sha256")
            and validation.get("outcome") == "passed"
            and validation.get("schema_version") == 1, "bootstrap_gate_mismatch")
    for key in ("config_sha256", "acquisition_source_sha256"):
        require(validation.get(key) == result[key], "bootstrap_provenance_mismatch")
    require(sha256(directory / "bootstrap_validation_source.py")
            == validation.get("validator_source_sha256"), "bootstrap_validator_source_mismatch")
    expected = {(kind, output, chunk) for output in (97, 98, 99)
                for kind in ("particle_ids", "groupcat", "offsets")
                for chunk in ([None] if kind == "offsets" else range(4))}
    files = config.get("files")
    require(isinstance(files, list) and len(files) == 27 and all(isinstance(f, dict) for f in files)
            and {(f.get("kind"), f.get("output"), f.get("chunk")) for f in files} == expected,
            "invalid_file_inventory")
    require(len({f["id"] for f in files}) == 27
            and len({f["relative_path"] for f in files}) == 27, "duplicate_file_inventory")
    requests = receipt.get("requests")
    require(isinstance(requests, list) and len(requests) == 27 and all(isinstance(r, dict) for r in requests)
            and len({r.get("id") for r in requests}) == 27, "invalid_acquisition_requests")
    by_id = {r["id"]: r for r in requests}
    require(set(by_id) == {f["id"] for f in files}, "acquisition_inventory_mismatch")
    prior_bytes = prior_budget(config, receipt, directory, result["config_sha256"])
    bootstrap_receipt = directory / "bootstrap_acquisition.json"
    require(sha256(bootstrap_receipt) == validation.get("acquisition_receipt_sha256"),
            "bootstrap_acquisition_snapshot_mismatch")
    bootstrap_record = load_json(bootstrap_receipt)
    require(bootstrap_record.get("outcome") == "bootstrap_downloaded"
            and bootstrap_record.get("config_sha256") == result["config_sha256"]
            and bootstrap_record.get("acquisition_source_sha256") == result["acquisition_source_sha256"],
            "bootstrap_acquisition_provenance_mismatch")
    initial_requests = bootstrap_record.get("requests")
    require(isinstance(initial_requests, list) and len(initial_requests) == 3
            and all(isinstance(item, dict) and item.get("id") in by_id
                    and item == by_id[item["id"]] for item in initial_requests),
            "bootstrap_acquisition_file_mismatch")
    require({item["id"] for item in initial_requests}
            == {f["id"] for f in files if f["bootstrap"]}, "bootstrap_acquisition_inventory_mismatch")
    result["prior_body_bytes"] = prior_bytes
    result["bootstrap_acquisition_snapshot_sha256"] = sha256(bootstrap_receipt)
    total, paths = 0, {}
    for planned in files:
        item = by_id[planned["id"]]
        require(item.get("outcome") == "complete"
                and item.get("url") == planned.get("url")
                and item.get("relative_path") == planned.get("relative_path"), "incomplete_or_mismatched_file")
        path = safe_path(directory, planned["relative_path"])
        size, body = item.get("file_bytes"), item.get("body_bytes")
        require(type(size) is int and type(body) is int and 0 < size <= body <= planned["byte_cap"],
                "invalid_file_byte_count")
        require(path.is_file() and path.stat().st_size == size, "file_size_mismatch")
        digest = sha256(path)
        require(digest == item.get("sha256"), "file_hash_mismatch")
        responses = item.get("responses")
        require(isinstance(responses, list) and 1 <= len(responses) <= 2
                and all(isinstance(r, dict) and type(r.get("body_bytes")) is int and r["body_bytes"] >= 0
                        and r.get("body_complete") is True for r in responses), "invalid_response_chain")
        require(sum(r["body_bytes"] for r in responses) == body
                and responses[-1].get("http_status") == 200
                and responses[-1]["body_bytes"] == size
                and responses[-1].get("body_sha256") == digest, "response_byte_or_hash_mismatch")
        if planned["bootstrap"]:
            require(validation.get("files", {}).get(planned["id"]) == digest, "bootstrap_file_mismatch")
        total += body
        paths[(planned["kind"], planned["output"], planned["chunk"])] = path
        result["files"][planned["id"]] = digest
    require(prior_bytes + total == receipt.get("aggregate_body_bytes")
            and prior_bytes + total <= config["aggregate_byte_cap"]
            and receipt.get("remaining_body_bytes") == config["aggregate_byte_cap"] - prior_bytes - total, "aggregate_budget_mismatch")
    result["acquisition_receipt_sha256"] = sha256(directory / "acquisition.json")
    result["bootstrap_validation_sha256"] = sha256(validation_path)
    return config, paths


def mass_diagnostic(counts, masses, particle_mass, storage_dtype):
    exact = counts.astype(np.float64) * particle_mass
    rel = np.abs(masses.astype(np.float64) - exact) / exact
    unit_roundoff = np.finfo(storage_dtype).eps / 2
    final_rounding = unit_roundoff + 8 * np.finfo(np.float64).eps
    nu = counts.astype(np.float64) * unit_roundoff
    bounded = nu < 1
    gamma = np.full(len(counts), np.inf)
    gamma[bounded] = nu[bounded] / (1 - nu[bounded]) + final_rounding
    return {
        "stored_dtype": str(storage_dtype), "max_relative_difference": float(rel.max()),
        "median_relative_difference": float(np.median(rel)),
        "outside_final_rounding_only_count": int(np.count_nonzero(rel > final_rounding)),
        "outside_conditional_summation_bound_count": int(np.count_nonzero(rel > gamma)),
        "unbounded_conditional_summation_bound_count": int(np.count_nonzero(~bounded)),
        "final_rounding_only_relative_bound": float(final_rounding),
        "conditional_bound": "gamma_N=N*u/(1-N*u), u=stored dtype epsilon/2, plus final-rounding allowance; assumes at most N same-precision rounded additions",
        "catalogue_accumulation_algorithm_verified": False,
        "interpretation": "Diagnostic only. Neither envelope establishes the undocumented accumulation algorithm; material mass uses exact integer counts times snapshot particle mass.",
    }


def load_epoch(output, paths, expected, h5py):
    n = expected["num_dm"]
    e = expected["snapshots"][str(output)]
    ng = e["num_groups"]
    other = [0, 2, 3, 4, 5]
    with h5py.File(paths[("offsets", output, None)], "r") as f:
        inspect_schema(f, h5py)
        starts = dataset(f, "Group/SnapByType", (ng, 6), "iu")[:]
        require("FileOffsets/SnapByType" in f, "missing_snapshot_chunk_offsets")
        snaps, offset_layout = normalize_snapshot_offsets(f["FileOffsets/SnapByType"][:], 4)
        cats = dataset(f, "FileOffsets/Group", (4,), "iu")[:]
        subcats = dataset(f, "FileOffsets/Subhalo", (4,), "iu")[:]
    require(np.all(starts >= 0) and np.all(starts[:, other] == 0), "invalid_group_offsets")
    require(np.all(snaps >= 0) and np.all(snaps[other, :] == 0)
            and np.all(snaps[:, 0] == 0) and np.all(snaps[1, 1:] >= snaps[1, :-1])
            and np.all(snaps[1] < n), "invalid_snapshot_chunk_offsets")
    require(np.all(cats >= 0) and cats[0] == 0 and np.all(cats[1:] >= cats[:-1])
            and np.all(cats < ng), "invalid_groupcat_offsets")
    require(np.all(subcats >= 0) and subcats[0] == 0 and np.all(subcats[1:] >= subcats[:-1])
            and np.all(subcats <= e["num_subgroups"]), "invalid_subhalo_file_offsets")
    counts, masses = np.empty(ng, dtype=np.uint64), np.empty(ng, dtype=np.float64)
    mass_dtype, particle_headers, group_headers = None, [], []
    total_id_header_values = []
    for chunk in range(4):
        begin, end = int(cats[chunk]), int(cats[chunk + 1]) if chunk < 3 else ng
        with h5py.File(paths[("groupcat", output, chunk)], "r") as f:
            inspect_schema(f, h5py)
            header, observed = f["Header"].attrs, {}
            for attr, value in (("Ngroups_Total", ng), ("Nsubgroups_Total", e["num_subgroups"]),
                                ("Ngroups_ThisFile", end - begin), ("NumFiles", 4)):
                scalar(header, attr, value, observed, True)
            for attr, key in (("BoxSize", "boxsize"), ("HubbleParam", "hubble"),
                              ("Omega0", "omega_0"), ("OmegaLambda", "omega_L")):
                if attr in header:
                    scalar(header, attr, expected[key], observed)
            scalar(header, "Redshift", e["redshift"], observed)
            scalar(header, "Time", 1 / (1 + e["redshift"]), observed)
            if "Nsubgroups_ThisFile" in header:
                subend = int(subcats[chunk + 1]) if chunk < 3 else e["num_subgroups"]
                scalar(header, "Nsubgroups_ThisFile", subend - int(subcats[chunk]), observed, True)
            lengths = dataset(f, "Group/GroupLenType", (end - begin, 6), "iu")[:]
            require(np.all(lengths >= 0) and np.all(lengths[:, other] == 0)
                    and np.all(lengths[:, 1] > 0), "non_dmo_group_lengths")
            counts[begin:end] = lengths[:, 1]
            if "Nids_ThisFile" in header:
                scalar(header, "Nids_ThisFile", int(np.sum(lengths[:, 1], dtype=np.uint64)), observed, True)
            if "Nids_Total" in header:
                value = np.asarray(header["Nids_Total"])
                require(value.size == 1 and value.dtype.kind in "iu", "invalid_header_Nids_Total")
                total_id_header_values.append(int(value.reshape(-1)[0]))
                observed["Nids_Total"] = int(value.reshape(-1)[0])
            values = dataset(f, "Group/GroupMass", (end - begin,), "f")
            if mass_dtype is None:
                mass_dtype = values.dtype
            require(values.dtype == mass_dtype, "inconsistent_group_mass_dtype")
            masses[begin:end] = values[:]
            group_headers.append(observed)
    require(np.all(np.isfinite(masses)) and np.all(masses > 0), "invalid_group_masses")
    cumulative = np.cumsum(counts, dtype=np.uint64)
    require(np.all(cumulative <= n) and np.all(cumulative[1:] >= cumulative[:-1]), "group_inventory_overflow")
    require(int(starts[0, 1]) == 0 and np.array_equal(starts[1:, 1], cumulative[:-1]),
            "group_length_offset_mismatch")
    grouped = int(cumulative[-1])
    require(grouped <= n, "grouped_inventory_exceeds_total")
    require(all(value == grouped for value in total_id_header_values), "groupcat_total_id_count_mismatch")
    ids = np.empty(n, dtype=np.uint64)
    for chunk in range(4):
        begin, end = int(snaps[1, chunk]), int(snaps[1, chunk + 1]) if chunk < 3 else n
        with h5py.File(paths[("particle_ids", output, chunk)], "r") as f:
            schema = inspect_schema(f, h5py)
            require({name for name in schema if name.split("/")[0].startswith("PartType")}
                    == {"PartType1/ParticleIDs"}, "particle_selection_not_id_only")
            header, observed = f["Header"].attrs, {}
            low = vector(header, "NumPart_Total", observed, integer=True)
            high = vector(header, "NumPart_Total_HighWord", observed, integer=True)
            require([int(a) + (int(b) << 32) for a, b in zip(low, high)] == [0, n, 0, 0, 0, 0],
                    "particle_inventory_mismatch")
            local = vector(header, "NumPart_ThisFile", observed, integer=True)
            require(np.array_equal(local, [0, end - begin, 0, 0, 0, 0]), "snapshot_chunk_count_mismatch")
            mass = vector(header, "MassTable", observed)
            require(np.all(mass[other] == 0), "non_dmo_mass_table")
            scalar({"mass": mass[1]}, "mass", expected["mass_dm"], {})
            for attr, key in (("BoxSize", "boxsize"), ("HubbleParam", "hubble"),
                              ("Omega0", "omega_0"), ("OmegaLambda", "omega_L")):
                scalar(header, attr, expected[key], observed)
            scalar(header, "NumFilesPerSnapshot", 4, observed, True)
            scalar(header, "Redshift", e["redshift"], observed)
            scalar(header, "Time", 1 / (1 + e["redshift"]), observed)
            if "OmegaBaryon" in header:
                scalar(header, "OmegaBaryon", expected["omega_B"], observed)
            for name in ("UnitLength_in_cm", "UnitMass_in_g", "UnitVelocity_in_cm_per_s"):
                if name in header:
                    value = np.asarray(header[name])
                    require(value.size == 1 and value.dtype.kind in "fiu"
                            and np.isfinite(value).all() and float(value.reshape(-1)[0]) > 0, "invalid_unit_header")
                    observed[name] = float(value.reshape(-1)[0])
            values = dataset(f, "PartType1/ParticleIDs", (end - begin,), "u")
            require(values.dtype.itemsize == 8, "particle_ids_not_uint64")
            values.read_direct(ids, dest_sel=np.s_[begin:end])
            particle_headers.append(observed)
    require(ng < np.iinfo(np.uint32).max, "too_many_hosts_for_label_dtype")
    labels = np.zeros(n, dtype=np.uint32)
    for index in range(ng):
        begin = int(starts[index, 1])
        labels[begin:begin + int(counts[index])] = index + 1
    order = np.argsort(ids, kind="quicksort")
    ids = ids[order]
    labels = labels[order]
    del order
    require(not np.any(ids[1:] == ids[:-1]), "duplicate_particle_ids")
    # Counts include a leading diffuse state; its size is not a host mass.
    host_counts = np.concatenate((np.zeros(1, dtype=np.uint64), counts))
    report = {
        "output": output, "particles": n, "hosts": ng,
        "grouped_particles": grouped, "diffuse_particles": n - grouped,
        "integer_closure_residual": grouped + (n - grouped) - n,
        "particle_ids_unique": True, "stored_snapshot_offset_layout": offset_layout,
        "groupcat_total_id_headers_checked": len(total_id_header_values),
        "particle_headers": particle_headers, "group_headers": group_headers,
        "group_mass_comparison": mass_diagnostic(counts, masses, expected["mass_dm"], mass_dtype),
    }
    return ids, labels, host_counts, report


def pair_diagnostics(left, right, left_counts, right_counts, particle_mass_solar):
    require(left.shape == right.shape, "pair_inventory_shape_mismatch")
    counts = dict(diffuse_to_diffuse=0, diffuse_to_host=0, host_to_diffuse=0,
                  host_to_host=0, host_mass_increased=0, host_mass_decreased=0, host_mass_equal=0)
    hist = np.zeros(len(JUMP_EDGES) - 1, dtype=np.int64)
    absolute, signed, maximum = 0., 0., 0.
    for begin in range(0, len(left), BLOCK):
        a, b = left[begin:begin + BLOCK], right[begin:begin + BLOCK]
        ga, gb = a != 0, b != 0
        counts["diffuse_to_diffuse"] += int(np.count_nonzero(~ga & ~gb))
        counts["diffuse_to_host"] += int(np.count_nonzero(~ga & gb))
        counts["host_to_diffuse"] += int(np.count_nonzero(ga & ~gb))
        both = ga & gb
        counts["host_to_host"] += int(np.count_nonzero(both))
        old, new = left_counts[a[both]], right_counts[b[both]]
        counts["host_mass_increased"] += int(np.count_nonzero(new > old))
        counts["host_mass_decreased"] += int(np.count_nonzero(new < old))
        counts["host_mass_equal"] += int(np.count_nonzero(new == old))
        jump = np.log(new.astype(np.float64) / old.astype(np.float64))
        magnitude = np.abs(jump)
        absolute += float(magnitude.sum())
        signed += float(jump.sum())
        maximum = max(maximum, float(magnitude.max(initial=0.)))
        hist += np.histogram(magnitude, JUMP_EDGES)[0]
    n = len(left)
    require(sum(counts[k] for k in ("diffuse_to_diffuse", "diffuse_to_host", "host_to_diffuse", "host_to_host")) == n,
            "pair_partition_not_closed")
    both = counts["host_to_host"]
    return {
        "particle_counts": counts,
        "mass_solar": {key: count * particle_mass_solar for key, count in counts.items()},
        "mean_absolute_log_mass_jump_given_both_hosted": absolute / both if both else None,
        "mean_signed_log_mass_jump_given_both_hosted": signed / both if both else None,
        "maximum_absolute_log_mass_jump_given_both_hosted": maximum if both else None,
        "absolute_jump_histogram": {"absolute_host_mass_ratio_edges": [1., 1.25, 2., 4., 10., "infinity"],
                                    "particle_counts": hist.tolist(), "measure": "particle-count weighted; equal particle masses"},
        "scope": "Endpoint size changes, not tracked host identity or an instantaneous physical current. Diffuse material has no logarithmic host mass.",
    }


def cadence_diagnostics(labels, host_counts):
    n = len(labels[0])
    total, reversals, host_reservoir_host, reservoir_host_reservoir = 0, 0, 0, 0
    excess, resolved_variation, coarsened_variation = 0., 0., 0.
    for begin in range(0, n, BLOCK):
        a, b, c = [x[begin:begin + BLOCK] for x in labels]
        hosted = (a != 0) & (b != 0) & (c != 0)
        host_reservoir_host += int(np.count_nonzero((a != 0) & (b == 0) & (c != 0)))
        reservoir_host_reservoir += int(np.count_nonzero((a == 0) & (b != 0) & (c == 0)))
        ma, mb, mc = [values[x[hosted]].astype(np.float64)
                      for values, x in zip(host_counts, (a, b, c))]
        first, second = np.log(mb / ma), np.log(mc / mb)
        resolved, coarse = np.abs(first) + np.abs(second), np.abs(np.log(mc / ma))
        total += len(ma)
        reversals += int(np.count_nonzero(((mb > ma) & (mc < mb)) | ((mb < ma) & (mc > mb))))
        resolved_variation += float(resolved.sum())
        coarsened_variation += float(coarse.sum())
        excess += float(np.maximum(resolved - coarse, 0.).sum())
    return {"particles_hosted_at_all_three_outputs": total,
            "particles_with_host_mass_direction_reversal": reversals,
            "host_diffuse_host_particles": host_reservoir_host,
            "diffuse_host_diffuse_particles": reservoir_host_reservoir,
            "summed_particle_weighted_resolved_absolute_log_change": resolved_variation,
            "summed_particle_weighted_coarsened_absolute_log_change": coarsened_variation,
            "mean_resolved_minus_coarsened_absolute_log_change": excess / total if total else None,
            "scope": "Three endpoints can reveal missed reversals or diffuse excursions, but cannot establish cadence convergence or residence times."}


def cosmic_time_gyr(scale_factor, omega_m, omega_lambda, hubble):
    # Late-time flat matter+Lambda convention; radiation omitted explicitly.
    require(omega_m > 0 and omega_lambda > 0 and abs(omega_m + omega_lambda - 1) < 1e-12,
            "time_conversion_requires_flat_matter_lambda")
    h0_per_second = 100 * hubble / 3.0856775814913673e19
    seconds_per_gyr = 365.25 * 86400 * 1e9
    return 2 / (3 * h0_per_second * math.sqrt(omega_lambda)) * math.asinh(
        math.sqrt(omega_lambda / omega_m) * scale_factor ** 1.5) / seconds_per_gyr


def validate(config_path, directory):
    directory = Path(directory)
    result = dict(schema_version=1, outcome="failed", development_only=True, files={},
                  reference_measure="logarithmic host mass; log-orthopolic collisionless total-matter candidate",
                  reader_source_sha256=sha256(Path(__file__)),
                  bootstrap_helper_source_sha256=sha256(ROOT / "experiments/check_cosmic_development_bootstrap.py"),
                  started_utc=datetime.now(timezone.utc).isoformat(), epochs=[], pairs={},
                  versions={"python": platform.python_version(), "numpy": np.__version__},
                  validation_target_assigned=False, log_orthopolic_transport_validated=False)
    try:
        config, paths = complete_provenance(Path(config_path), directory, result)
        import h5py
        result["versions"].update(h5py=h5py.__version__, hdf5=h5py.version.hdf5_version)
        expected = config["expected"]
        # Upper estimate includes all retained labels, current IDs/sort copies,
        # block temporaries and a 256 MiB library/process allowance.
        estimate = 96 * expected["num_dm"] + 256 * 1024 ** 2
        require(estimate <= config["reader_max_rss_bytes"], "planned_reader_memory_exceeds_limit")
        require(peak_rss_bytes() <= config["reader_max_rss_bytes"], "reader_memory_limit_exceeded")
        result["memory"] = {"planned_upper_estimate_bytes": estimate,
                            "limit_bytes": config["reader_max_rss_bytes"], "scratch_bytes_written": 0}
        reference_ids, labels, host_counts = None, [], []
        for output in config["outputs"]:
            ids, current_labels, current_counts, report = load_epoch(output, paths, expected, h5py)
            if reference_ids is None:
                reference_ids = ids
            else:
                require(np.array_equal(reference_ids, ids), "particle_id_set_changed_between_outputs")
                del ids
            labels.append(current_labels)
            host_counts.append(current_counts)
            result["epochs"].append(report)
            require(peak_rss_bytes() <= config["reader_max_rss_bytes"], "reader_memory_limit_exceeded")
        result["identical_particle_id_sets"] = True
        mass_solar = expected["mass_dm"] * 1e10 / expected["hubble"]
        box_mpc = expected["boxsize"] / 1000 / expected["hubble"]
        result["units"] = {"particle_mass_solar": mass_solar,
                           "box_side_comoving_mpc": box_mpc, "box_volume_comoving_mpc3": box_mpc ** 3,
                           "total_inventory_mass_solar": expected["num_dm"] * mass_solar,
                           "time_convention": "Flat matter+Lambda cosmic age; radiation omitted at z<0.024; Julian year=365.25 days"}
        times = [cosmic_time_gyr(1 / (1 + expected["snapshots"][str(output)]["redshift"]),
                                expected["omega_0"], expected["omega_L"], expected["hubble"])
                 for output in config["outputs"]]
        result["cosmic_age_gyr"] = dict(zip(map(str, config["outputs"]), times))
        for i, j in ((0, 1), (1, 2), (0, 2)):
            key = f"{config['outputs'][i]}->{config['outputs'][j]}"
            pair = pair_diagnostics(labels[i], labels[j], host_counts[i], host_counts[j], mass_solar)
            pair["interval_gyr"] = times[j] - times[i]
            require(pair["interval_gyr"] > 0, "nonpositive_time_interval")
            result["pairs"][key] = pair
        result["cadence"] = cadence_diagnostics(labels, host_counts)
        result["outcome"] = "inventory_checks_passed"
        result["interpretation"] = "Exact inventory and endpoint accounting only. Catalogue mass construction, local current closure, stationarity, cadence convergence and an independent prediction remain unqualified."
    except InvalidBootstrap as exc:
        result["reason"] = str(exc)
    except (ImportError, OSError, ValueError, KeyError, TypeError, OverflowError) as exc:
        result["reason"] = "validation_exception_" + type(exc).__name__
    result["peak_resident_bytes"] = peak_rss_bytes()
    result["finished_utc"] = datetime.now(timezone.utc).isoformat()
    output = directory / "material-validation.json"
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
    return 0 if result["outcome"] == "inventory_checks_passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
