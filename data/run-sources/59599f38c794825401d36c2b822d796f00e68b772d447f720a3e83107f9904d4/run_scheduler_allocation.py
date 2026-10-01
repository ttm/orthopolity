"""Inspect hardware, simulate declared models, and run only eligible scheduling trials."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import random
import select
import statistics
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[1]


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def source_hashes():
    return {str(path.relative_to(ROOT)): digest(path) for path in
            (Path(__file__), ROOT / "src/orthopolity/scheduler_allocation.py")}


def worker_command(config, mode, size):
    command = [sys.executable, str(Path(__file__).resolve()), "--worker-mode", mode,
               "--worker-size", str(size)]
    if mode == "calibration":
        command += ["--worker-jobs", str(config["calibration_jobs_per_block"])]
    return command


def child_environment(config):
    environment = os.environ.copy()
    environment.update(config["thread_environment"])
    environment["PYTHONPATH"] = str(ROOT / "src")
    return environment


def execute_trial(config, counts):
    """Popen avoids multiprocessing's extra resource-tracker process."""
    children, rows, ready = [], [], []
    try:
        for size, count in zip(config["sizes"], counts):
            for _ in range(count):
                children.append(subprocess.Popen(worker_command(config, "trial", size),
                    env=child_environment(config), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE, text=True))
        for child in children:
            if not select.select([child.stdout], [], [], config["worker_timeout_seconds"])[0]:
                raise RuntimeError("worker readiness deadline exceeded")
            message = json.loads(child.stdout.readline())
            if message.get("status") != "ready":
                raise RuntimeError("worker failed to reach synchronized ready state")
            ready.append(message)
        # Each spawned child must inherit the same declared priority/policy and
        # a CPU bound supporting scarcity. No changing system settings here.
        from orthopolity.scheduler_allocation import hardware_gate
        if any(not hardware_gate(config, item["hardware"])["eligible"] for item in ready):
            raise RuntimeError("a child did not inherit eligible CPU constraints")
        if len({(item["hardware"].get("inherited_nice"), item["hardware"].get("inherited_scheduler_policy")) for item in ready}) != 1:
            raise RuntimeError("worker priorities or scheduler policies differ")
        start = time.monotonic() + config["synchronization_lead_seconds"]
        stop = start + config["trial_seconds"]
        control = json.dumps(dict(start_at=start, stop_at=stop)) + "\n"
        for child in children:
            child.stdin.write(control)
            child.stdin.flush()
            child.stdin.close()
            child.stdin = None
        for child, metadata in zip(children, ready):
            stdout, stderr = child.communicate(timeout=config["worker_timeout_seconds"])
            if child.returncode != 0:
                raise RuntimeError(f"worker failed: {stderr}")
            row = json.loads(stdout)
            row["worker_pid"] = metadata["pid"]
            row["inherited_hardware"] = metadata["hardware"]
            rows.append(row)
        return rows
    finally:
        for child in children:
            if child.poll() is None:
                child.terminate()
                child.wait(timeout=3)


def actual_study(config, config_path, directory, output, gate):
    from orthopolity.scheduler_allocation import summarize_trial
    if not gate["eligible"]:
        raise ValueError("actual scheduling measurements are prohibited by the hardware gate")
    # Study directories are append-free. Reruns need a new directory so no
    # earlier outcomes or model freeze can be silently replaced.
    if any((directory / name).exists() for name in ("calibration.json", "frozen-plan.json", "trials.json", "study.json")):
        raise ValueError("actual run records already exist; use a new study directory")
    started = utc_now()
    specification = dict(config=config, config_sha256=digest(config_path), source_sha256=source_hashes(),
                         started_utc=started, gate=gate)
    write_json(directory / "study-specification.json", specification)
    calibration = []
    for block in range(config["calibration_blocks"]):
        sizes = list(config["sizes"])
        random.Random(config["seed"] + block).shuffle(sizes)
        for order, size in enumerate(sizes):
            result = subprocess.run(worker_command(config, "calibration", size),
                env=child_environment(config), text=True, capture_output=True,
                timeout=config["worker_timeout_seconds"], check=True)
            calibration.append(dict(json.loads(result.stdout), block_id=block,
                                    order_in_block=order, measured_utc=utc_now()))
    write_json(directory / "calibration.json", calibration)
    q_cpu = [statistics.mean(value for row in calibration if row["size"] == size
                for value in row["job_cpu_seconds"]) for size in config["sizes"]]
    from orthopolity.scheduler_allocation import allocation_predictions
    plan = dict(specification, frozen_utc=utc_now(), calibration_sha256=digest(directory / "calibration.json"),
        q_cpu_seconds_per_job=q_cpu,
        predictions={name: allocation_predictions(counts, q_cpu, config["log_bin_edges"])
                     for name, counts in config["conditions"].items()},
        uncertainty="All short-trial shares and calibration costs will be reported; no guaranteed confidence interval or post-hoc significance threshold")
    write_json(directory / "frozen-plan.json", plan)
    frozen_hash = digest(directory / "frozen-plan.json")
    trials = []
    for replicate in range(config["trial_replicates_per_condition"]):
        names = list(config["conditions"])
        random.Random(config["seed"] + 1000 + replicate).shuffle(names)
        for name in names:
            if plan["source_sha256"] != source_hashes():
                raise RuntimeError("measurement source changed after freeze")
            rows = execute_trial(config, config["conditions"][name])
            summary = summarize_trial(rows, config["sizes"], q_cpu, config["log_bin_edges"], config["conditions"][name])
            timings_valid = all(row["start_lag_seconds"] <= config["maximum_start_lag_seconds"]
                and row["stop_lag_seconds"] <= config["maximum_stop_lag_seconds"] for row in rows)
            trials.append(dict(condition=name, replicate=replicate, measured_utc=utc_now(),
                frozen_plan_sha256=frozen_hash, timing_assumptions_satisfied=timings_valid,
                workers=rows, summary=summary))
            write_json(directory / "trials.json", trials)
            print(f"Measured {name} trial {replicate + 1}; timing_valid={timings_valid}", flush=True)
    result = dict(kind="actual_os_scheduler_cpu_allocation", gate=gate, config=config,
        frozen_plan_sha256=frozen_hash, calibration_sha256=plan["calibration_sha256"],
        trials_sha256=digest(directory / "trials.json"), source_sha256=source_hashes(),
        frozen_utc=plan["frozen_utc"], completed_utc=utc_now(), q_cpu_seconds_per_job=q_cpu,
        calibration=calibration, trials=trials,
        scope="Direct CPU allocation under inherited OS policy and experimentally declared runnable opportunities; no selection principle for Nature or fitted exponent",
        accounting="Primary CPU includes completed work, censored partial jobs and loop overhead; calibrated job-count reconstruction is secondary")
    write_json(directory / "study.json", result)
    write_json(output / "study.json", result)
    return result


def worker_main(args):
    from orthopolity.scheduler_allocation import calibrate_jobs, dense_job, host_capacity, run_cpu_worker
    if args.worker_mode == "calibration":
        result = calibrate_jobs(args.worker_size, args.worker_jobs)
    else:
        dense_job(8)
        print(json.dumps(dict(status="ready", pid=os.getpid(), hardware=host_capacity())), flush=True)
        control = json.loads(sys.stdin.readline())
        result = run_cpu_worker(args.worker_size, control["start_at"], control["stop_at"])
    print(json.dumps(result, allow_nan=False), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/scheduler_allocation_2026-10-01.json")
    parser.add_argument("--directory", type=Path, default=ROOT / "data/scheduler-allocation/2026-10-01")
    parser.add_argument("--output", type=Path, default=ROOT / "results/scheduler-allocation")
    parser.add_argument("--stage", choices=("gate", "design", "actual", "all"), default="all")
    parser.add_argument("--worker-mode", choices=("calibration", "trial"), help=argparse.SUPPRESS)
    parser.add_argument("--worker-size", type=int, help=argparse.SUPPRESS)
    parser.add_argument("--worker-jobs", type=int, default=3, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker_mode:
        worker_main(args)
        return
    from orthopolity.scheduler_allocation import conditional_design, hardware_gate
    config = json.loads(args.config.read_text())
    args.directory.mkdir(parents=True, exist_ok=True)
    args.output.mkdir(parents=True, exist_ok=True)
    gate_path=args.directory / "hardware-gate.json"
    if gate_path.exists():
        gate_record=json.loads(gate_path.read_text())
        if gate_record["config_sha256"] != digest(args.config) or gate_record["source_sha256"] != source_hashes():
            raise ValueError("Retained gate has different inputs; use new data and output directories")
    else:
        gate_record = dict(hardware_gate(config), inspected_utc=utc_now(), config_sha256=digest(args.config),
                           source_sha256=source_hashes(), actual_allocation_measurements_executed=False)
        write_json(gate_path, gate_record)
    output_gate=args.output / "hardware-gate.json"
    if output_gate.exists():
        if json.loads(output_gate.read_text()) != gate_record:
            raise ValueError("Output directory belongs to a different gate inspection")
    else:
        write_json(output_gate, gate_record)
    print(json.dumps(gate_record, indent=2), flush=True)
    if args.stage in ("design", "all"):
        design_path=args.output / "conditional-design.json"
        if design_path.exists():
            design=json.loads(design_path.read_text())
            if (design["config_sha256"] != digest(args.config) or
                    design["source_sha256"] != source_hashes() or design["gate"] != gate_record):
                raise ValueError("Retained design has different inputs; use a new output directory")
        else:
            design = dict(conditional_design(config), gate=gate_record,
                          config_sha256=digest(args.config), source_sha256=source_hashes())
            write_json(design_path, design)
    if args.stage in ("actual", "all"):
        # Never use an earlier inspection to authorize measurements on a changed host.
        gate=hardware_gate(config)
        if not gate["eligible"]:
            print("No actual allocation trial executed: unsupported hardware under the fixed process bound.", flush=True)
            return
        actual_study(config, args.config, args.directory, args.output, gate)


if __name__ == "__main__":
    main()
