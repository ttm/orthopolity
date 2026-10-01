"""A gated CPU-allocation protocol; conditional models are not observations.

The workload uses Python arithmetic in one thread, avoiding unverified BLAS
thread counts. The OS chooses execution time; the controller chooses only
runnable worker counts and a common wall-clock observation window.
"""
from __future__ import annotations

import math
import os
from pathlib import Path, PurePosixPath
import platform
import random
import statistics
import sys
import time


def parse_cpu_max(text):
    """Parse cgroup-v2 cpu.max, returning a CPU-time rate or no limit."""
    fields = text.split()
    if len(fields) != 2:
        raise ValueError("cpu.max must contain quota and period")
    period = int(fields[1])
    if period <= 0:
        raise ValueError("CPU period must be positive")
    if fields[0] == "max":
        return None, period
    quota = int(fields[0])
    if quota <= 0:
        raise ValueError("CPU quota must be positive")
    return quota / period, period


def _unescape_mount(value):
    for escaped, plain in (("\\040", " "), ("\\011", "\t"), ("\\012", "\n"), ("\\134", "\\")):
        value = value.replace(escaped, plain)
    return value


def cgroup_cpu_limits(membership_text, mountinfo_text, read_text):
    """Read current cgroup and visible ancestors; never modify controllers.

    Unresolvable namespace paths are recorded, not replaced with a guessed
    quota. Both unified cpu.max and legacy cpu.cfs_* limits are understood.
    """
    memberships = []
    for line in membership_text.splitlines():
        fields = line.split(":", 2)
        if len(fields) == 3:
            hierarchy, controllers, directory = fields
            if hierarchy == "0" and not controllers:
                memberships.append(("cgroup2", directory))
            elif "cpu" in controllers.split(","):
                memberships.append(("cgroup", directory))
    mounts = []
    for line in mountinfo_text.splitlines():
        fields = line.split()
        if "-" not in fields:
            continue
        separator = fields.index("-")
        if len(fields) < separator + 4:
            continue
        filesystem = fields[separator + 1]
        if filesystem == "cgroup2" or (filesystem == "cgroup" and "cpu" in fields[separator + 3].split(",")):
            mounts.append((filesystem, _unescape_mount(fields[3]), _unescape_mount(fields[4])))
    limits, warnings = [], []
    for filesystem, membership in memberships:
        matched = False
        for fs, root, mountpoint in mounts:
            if fs != filesystem:
                continue
            try:
                relative = PurePosixPath(membership).relative_to(PurePosixPath(root))
            except ValueError:
                continue
            if ".." in relative.parts:
                continue
            current = Path(mountpoint).joinpath(*relative.parts)
            mount = Path(mountpoint)
            matched = True
            while True:
                try:
                    if filesystem == "cgroup2":
                        path = current / "cpu.max"
                        capacity, period = parse_cpu_max(read_text(path))
                        try:
                            burst = int(read_text(current / "cpu.max.burst").strip())
                        except FileNotFoundError:
                            burst = 0
                        if burst < 0:
                            raise ValueError("negative CPU burst allowance")
                    else:
                        path = current / "cpu.cfs_quota_us"
                        quota = int(read_text(path).strip())
                        period = int(read_text(current / "cpu.cfs_period_us").strip())
                        if period <= 0 or quota == 0 or quota < -1:
                            raise ValueError("invalid legacy CPU limit")
                        capacity = None if quota == -1 else quota / period
                        burst = 0
                    if capacity is not None:
                        limits.append(dict(path=str(path), capacity_cpus=capacity,
                                           period_microseconds=period, burst_microseconds=burst))
                except FileNotFoundError:
                    # A hierarchy root often has no CPU controller interface.
                    pass
                except (OSError, ValueError) as error:
                    warnings.append(f"Could not interpret {current}: {error}")
                if current == mount:
                    break
                current = current.parent
        if not matched:
            warnings.append(f"Cannot resolve {filesystem} membership {membership} against visible mounts")
    return dict(limits=limits, warnings=warnings)


def host_capacity():
    """Conservative visible capacity bound, including inherited CPU limits."""
    logical = os.cpu_count()
    affinity = sorted(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else None
    constraints = []
    if logical is not None and logical > 0:
        constraints.append(dict(kind="logical_cpu_count", capacity_cpus=float(logical)))
    if affinity:
        constraints.append(dict(kind="inherited_affinity", capacity_cpus=float(len(affinity))))
    cgroup = dict(limits=[], warnings=[])
    if sys.platform.startswith("linux"):
        try:
            cgroup = cgroup_cpu_limits(Path("/proc/self/cgroup").read_text(),
                Path("/proc/self/mountinfo").read_text(), lambda path: Path(path).read_text())
        except OSError as error:
            cgroup["warnings"].append(f"Cgroup metadata unavailable: {error}")
        constraints.extend(dict(kind="cgroup_cpu_quota", **entry) for entry in cgroup["limits"])
    return dict(system=platform.system(), architecture=platform.machine(),
        logical_cpu_count=logical, inherited_affinity=affinity,
        capacity_bound_cpus=min((entry["capacity_cpus"] for entry in constraints), default=None),
        capacity_constraints=constraints, cgroup_warnings=cgroup["warnings"],
        inherited_nice=os.getpriority(os.PRIO_PROCESS, 0) if hasattr(os, "getpriority") else None,
        inherited_scheduler_policy=os.sched_getscheduler(0) if hasattr(os, "sched_getscheduler") else None,
        load_average=list(os.getloadavg()) if hasattr(os, "getloadavg") else None)


def validate_design(config):
    sizes = config["sizes"]
    edges = config["log_bin_edges"]
    if (not sizes or any(isinstance(s, bool) or not isinstance(s, int) or not 2 <= s <= 128 for s in sizes)
            or sizes != sorted(set(sizes))):
        raise ValueError("sizes must be a positive increasing bounded integer grid")
    if (len(edges) != len(sizes) + 1 or any(not math.isfinite(v) or v <= 0 for v in edges)
            or any(a >= b for a, b in zip(edges[:-1], edges[1:]))
            or any(not edges[i] < size < edges[i + 1] for i, size in enumerate(sizes))):
        raise ValueError("each declared size needs its own fixed positive log bin")
    if config["maximum_total_processes"] != 4:
        raise ValueError("the protocol is bounded to controller plus at most three workers")
    if not 2 <= config["trial_seconds"] <= 5:
        raise ValueError("trial duration must be between two and five seconds")
    for name, counts in config["conditions"].items():
        if (len(counts) != len(sizes) or any(isinstance(n, bool) or not isinstance(n, int) or n < 0 for n in counts)
                or not 1 <= sum(counts) <= 3):
            raise ValueError(f"invalid runnable-worker counts for {name}")


def hardware_gate(config, capacity=None):
    """Require independently visible scarcity for every condition.

    CPU quotas are sustained rates, not instantaneous core counts. Quota-only
    eligibility additionally requires short periods and no positive burst.
    Unknown/unreadable limits never fabricate a smaller effective CPU count.
    """
    validate_design(config)
    capacity = host_capacity() if capacity is None else capacity
    workers = min(sum(counts) for counts in config["conditions"].values())
    constraints = capacity["capacity_constraints"]
    qualifying = []
    for entry in constraints:
        bound = entry["capacity_cpus"]
        if not math.isfinite(bound) or bound <= 0 or bound >= workers or bound > 2:
            continue
        if entry["kind"] == "cgroup_cpu_quota":
            if entry.get("burst_microseconds", 0) > 0:
                continue
            if entry["period_microseconds"] / 1e6 > config["trial_seconds"] / 10:
                continue
        qualifying.append(entry)
    policy = capacity.get("inherited_scheduler_policy")
    normal_policy = policy is None or policy == 0
    eligible = bool(qualifying) and normal_policy
    return dict(eligible=eligible, status="eligible_for_measurement" if eligible else "unsupported_hardware",
        reason=("Every condition has more continuously runnable single-thread workers than an independently visible CPU bound"
                if eligible else "CPU scarcity under the four-total-process bound is not established, or the inherited scheduling policy is unsupported"),
        maximum_total_processes=4, maximum_workers=3, minimum_workers_per_condition=workers,
        qualifying_constraints=qualifying, hardware=capacity,
        changes_to_priority_affinity_or_cgroups=False)


def allocation_predictions(worker_counts, q_cpu, log_edges):
    """Declare competing class CPU shares before observing scheduler outputs."""
    if (len(worker_counts) != len(q_cpu) or len(log_edges) != len(q_cpu) + 1
            or any(n < 0 or int(n) != n for n in worker_counts) or sum(worker_counts) <= 0
            or any(not math.isfinite(q) or q <= 0 for q in q_cpu)):
        raise ValueError("paired nonnegative counts and positive independent CPU costs are required")
    widths = [math.log(b / a) for a, b in zip(log_edges[:-1], log_edges[1:])]
    if any(not math.isfinite(w) or w <= 0 for w in widths):
        raise ValueError("log bin widths must be positive")
    process = [n / sum(worker_counts) for n in worker_counts]
    job_total = sum(n * q for n, q in zip(worker_counts, q_cpu))
    jobs = [n * q / job_total for n, q in zip(worker_counts, q_cpu)]
    active = sum(n > 0 for n in worker_counts)
    equal_class = [1 / active if n else 0 for n in worker_counts]
    return dict(fair_runnable_process_cpu_share=process,
        equal_job_service_cpu_share=jobs, equal_active_class_cpu_share=equal_class,
        cpu_share_per_log_class=[share / width for share, width in zip(process, widths)],
        log_widths=widths,
        per_thread_and_per_process_identifiable=False)


def duty_constrained_rates(worker_duties, capacity_cpus):
    """Conditional equal-weight water filling with independently known duty caps.

    This supplies a competing demand-limited model, not a claim that sleeping
    jobs behave like continuously runnable ones or that the OS guarantees it.
    """
    if (not worker_duties or not math.isfinite(capacity_cpus) or capacity_cpus <= 0
            or any(not math.isfinite(d) or not 0 <= d <= 1 for d in worker_duties)):
        raise ValueError("duties must be in [0,1] and CPU capacity positive")
    if sum(worker_duties) <= capacity_cpus:
        return list(worker_duties)
    low, high = 0., 1.
    for _ in range(70):
        middle = (low + high) / 2
        if sum(min(d, middle) for d in worker_duties) < capacity_cpus:
            low = middle
        else:
            high = middle
    return [min(d, (low + high) / 2) for d in worker_duties]


def conditional_design(config):
    """Generated resource-quanta allocation under declared rival hypotheses."""
    validate_design(config)
    q = config["simulation_cpu_costs_seconds"]
    quanta = config["simulation_quanta"]
    trials = config["simulation_replicates"]
    if quanta <= 0 or trials <= 0:
        raise ValueError("simulation counts must be positive")
    rng = random.Random(config["seed"])
    results = {}
    for name, counts in config["conditions"].items():
        predicted = allocation_predictions(counts, q, config["log_bin_edges"])
        models = {}
        for model in ("fair_runnable_process_cpu_share", "equal_job_service_cpu_share", "equal_active_class_cpu_share"):
            shares = predicted[model]
            errors = []
            for _ in range(trials):
                selected = rng.choices(range(len(counts)), weights=shares, k=quanta)
                observed = [selected.count(i) / quanta for i in range(len(counts))]
                errors.append(max(abs(a - b) for a, b in zip(observed, shares)))
            errors.sort()
            models[model] = dict(expected_cpu_shares=shares,
                generated_max_share_error_95th_percentile=errors[math.ceil(.95 * trials) - 1])
        results[name] = dict(worker_counts=counts, hypotheses=predicted, generated_models=models)
    return dict(kind="conditional_generated_design_not_scheduler_measurements",
        simulation_cpu_costs_seconds=q, replicates=trials, resource_quanta_per_replicate=quanta,
        conditions=results,
        scientific_status="These simulations encode the declared allocation models and cannot validate OS fairness or Nature's allocation selection",
        uncertainty_status="Generated quanta variability is not an empirical scheduler interval or a frozen acceptance tolerance")


def dense_job(size, deadline=None):
    """Pure-Python, single-thread dense product with an independent probe check.

    A common deadline may censor a job after a row. No completed-job resource
    is invented for such work; its measured CPU is separately retained.
    """
    if isinstance(size, bool) or not isinstance(size, int) or not 2 <= size <= 128:
        raise ValueError("workload size outside the bounded protocol")
    left = [[((i + 2 * j) % 17 - 8) / 17 for j in range(size)] for i in range(size)]
    right = [[((3 * i - j) % 19 - 9) / 19 for j in range(size)] for i in range(size)]
    output = []
    for row in left:
        if deadline is not None and time.monotonic() >= deadline:
            return dict(completed=False, numerical_valid=None)
        output.append([sum(row[k] * right[k][j] for k in range(size)) for j in range(size)])
    probe = [(j % 11 - 5) / 11 for j in range(size)]
    inner = [sum(row[j] * probe[j] for j in range(size)) for row in right]
    reference = [sum(row[j] * inner[j] for j in range(size)) for row in left]
    observed = [sum(row[j] * probe[j] for j in range(size)) for row in output]
    residual = math.sqrt(sum((a - b) ** 2 for a, b in zip(reference, observed)))
    scale = max(math.sqrt(sum(v * v for v in reference)), 1e-300)
    valid = residual / scale <= 1e-10 and all(math.isfinite(v) for v in observed)
    if not valid:
        raise RuntimeError("numerical workload verification failed")
    finished = deadline is None or time.monotonic() <= deadline
    return dict(completed=finished, numerical_valid=True, relative_residual=residual / scale,
                checksum=sum(sum(row) for row in output))


def _cpu_usage():
    import resource
    usage = resource.getrusage(resource.RUSAGE_SELF)
    return usage.ru_utime, usage.ru_stime


def calibrate_jobs(size, jobs):
    """Independent fresh-child job costs; no allocation outcome is consulted."""
    if not isinstance(jobs, int) or jobs < 1:
        raise ValueError("at least one calibration job is required")
    dense_job(8)
    costs = []
    for _ in range(jobs):
        before = sum(_cpu_usage())
        dense_job(size)
        costs.append(sum(_cpu_usage()) - before)
    if any(cost <= 0 for cost in costs):
        raise RuntimeError("CPU-clock resolution does not support this workload")
    return dict(size=size, completed_jobs=jobs, job_cpu_seconds=costs,
                mean_cpu_seconds_per_job=statistics.mean(costs), numerical_valid=True)


def run_cpu_worker(size, start_at, stop_at):
    """Measure a continuously runnable worker between shared monotonic times."""
    if not (math.isfinite(start_at) and math.isfinite(stop_at) and 0 < stop_at - start_at <= 5):
        raise ValueError("worker needs a finite short observation interval")
    while time.monotonic() < start_at:
        time.sleep(min(.001, max(0., start_at - time.monotonic())))
    actual_start = time.monotonic()
    baseline_user, baseline_system = _cpu_usage()
    completed, partial = 0, 0
    complete_cpu, partial_cpu = 0., 0.
    while time.monotonic() < stop_at:
        before = sum(_cpu_usage())
        job = dense_job(size, deadline=stop_at)
        cost = sum(_cpu_usage()) - before
        if job["completed"]:
            completed += 1
            complete_cpu += cost
        else:
            partial += 1
            partial_cpu += cost
            break
    user, system = _cpu_usage()
    actual_stop = time.monotonic()
    cpu = (user - baseline_user) + (system - baseline_system)
    overhead = cpu - complete_cpu - partial_cpu
    if overhead < -1e-9:
        raise RuntimeError("CPU accounting intervals do not partition the observation")
    return dict(size=size, completed_jobs=completed, censored_partial_jobs=partial,
        cpu_user_seconds=user - baseline_user, cpu_system_seconds=system - baseline_system,
        cpu_seconds=cpu, complete_job_cpu_seconds=complete_cpu,
        partial_job_cpu_seconds=partial_cpu, loop_overhead_cpu_seconds=max(0., overhead),
        start_at_monotonic=start_at, stop_at_monotonic=stop_at,
        actual_start_monotonic=actual_start, actual_stop_monotonic=actual_stop,
        start_lag_seconds=actual_start - start_at, stop_lag_seconds=actual_stop - stop_at,
        continuously_runnable=True, python_workload_threads=1)


def summarize_trial(worker_rows, sizes, q_cpu, log_edges, worker_counts):
    """Primary measured CPU allocation and secondary calibrated reconstruction."""
    if len(worker_rows) != sum(worker_counts):
        raise ValueError("trial worker count does not match the declared opportunity measure")
    cpu, jobs, completed_cpu, partial_cpu, overhead = ([0.] * len(sizes) for _ in range(5))
    seen = [0] * len(sizes)
    for row in worker_rows:
        index = sizes.index(row["size"])
        seen[index] += 1
        fields=("cpu_seconds", "complete_job_cpu_seconds", "partial_job_cpu_seconds", "loop_overhead_cpu_seconds")
        if any(row[key] < 0 or not math.isfinite(row[key]) for key in fields):
            raise ValueError("all actual CPU charges must be finite and nonnegative")
        if isinstance(row["completed_jobs"], bool) or not isinstance(row["completed_jobs"], int) or row["completed_jobs"] < 0:
            raise ValueError("completed jobs must be a nonnegative integer")
        if not math.isclose(row["cpu_seconds"], row["complete_job_cpu_seconds"] + row["partial_job_cpu_seconds"] + row["loop_overhead_cpu_seconds"], abs_tol=1e-8):
            raise ValueError("worker CPU accounting is incomplete")
        cpu[index] += row["cpu_seconds"]
        jobs[index] += row["completed_jobs"]
        completed_cpu[index] += row["complete_job_cpu_seconds"]
        partial_cpu[index] += row["partial_job_cpu_seconds"]
        overhead[index] += row["loop_overhead_cpu_seconds"]
    if seen != worker_counts or sum(cpu) <= 0:
        raise ValueError("measured worker classes do not match the frozen trial")
    predicted = allocation_predictions(worker_counts, q_cpu, log_edges)
    shares = [value / sum(cpu) for value in cpu]
    reconstructed = [count * cost for count, cost in zip(jobs, q_cpu)]
    return dict(cpu_seconds_by_class=cpu, measured_cpu_share_by_class=shares,
        completed_jobs_by_class=jobs, complete_job_cpu_seconds_by_class=completed_cpu,
        partial_job_cpu_seconds_by_class=partial_cpu, loop_overhead_cpu_seconds_by_class=overhead,
        measured_cpu_per_log_class=[v / w for v, w in zip(cpu, predicted["log_widths"])],
        calibrated_completed_job_cpu_by_class=reconstructed,
        reconstruction_minus_measured_complete_job_cpu=[a - b for a, b in zip(reconstructed, completed_cpu)],
        hypotheses=predicted,
        maximum_absolute_share_errors={name: max(abs(a - b) for a, b in zip(shares, predicted[name]))
            for name in ("fair_runnable_process_cpu_share", "equal_job_service_cpu_share", "equal_active_class_cpu_share")})
