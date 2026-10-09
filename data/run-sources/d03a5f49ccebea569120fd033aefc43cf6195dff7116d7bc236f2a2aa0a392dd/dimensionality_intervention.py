"""Independently calibrated cost dimensions and measured GIL allocation.

CPU allocation is an observation. Equal runnable-thread CPU shares are a
conditional hypothesis, never a worker quota or completion rule.
"""
from __future__ import annotations

import math
import os
import platform
import random
import statistics
import sys
import threading
import time


def runtime_metadata():
    gil = (sys._is_gil_enabled() if hasattr(sys, "_is_gil_enabled") else
           platform.python_implementation() == "CPython" and sys.version_info < (3, 13))
    clock = time.get_clock_info("thread_time")
    return dict(python=sys.version, implementation=platform.python_implementation(),
        system=platform.system(), architecture=platform.machine(), logical_cpu_count=os.cpu_count(),
        gil_enabled=bool(gil), switch_interval_seconds=sys.getswitchinterval(),
        thread_cpu_clock=dict(implementation=clock.implementation, resolution=clock.resolution,
                              monotonic=clock.monotonic, adjustable=clock.adjustable),
        priority_affinity_and_switch_interval_changed=False)


def validate_config(config):
    sizes, edges = config["sizes"], config["log_bin_edges"]
    if (sizes != sorted(set(sizes)) or len(sizes) < 3
            or any(isinstance(s, bool) or not isinstance(s, int) or not 2 <= s <= 96 for s in sizes)):
        raise ValueError("fixed increasing integer sizes within [2,96] are required")
    if (len(edges) != len(sizes) + 1 or any(not math.isfinite(v) or v <= 0 for v in edges)
            or any(a >= b for a, b in zip(edges, edges[1:]))
            or any(not edges[i] < k < edges[i+1] for i, k in enumerate(sizes))):
        raise ValueError("fixed positive bins must contain the declared representatives")
    if not 2 <= config["trial_seconds"] <= 5:
        raise ValueError("each common observation window must be between two and five seconds")
    if set(config["kernels"]) != {"quadratic", "cubic"}:
        raise ValueError("both independently calibrated kernels must be retained")
    if not 1 <= config["quadratic_repeats"] <= 32:
        raise ValueError("quadratic repetitions must be bounded")
    for counts in config["conditions"].values():
        if (len(counts) != len(sizes) or any(isinstance(n, bool) or not isinstance(n, int) or n < 0 for n in counts)
                or not 2 <= sum(counts) <= 5):
            raise ValueError("each condition must declare two to five runnable threads")
    if config["calibration_blocks"] < 2 or config["calibration_jobs_per_block"] < 1:
        raise ValueError("independent replicated calibration is required")


def execute_job(kernel, size, *, quadratic_repeats=16, deadline=None):
    """Pure Python kernels with bounded deadline checkpoints and verification."""
    if kernel not in ("quadratic", "cubic") or not isinstance(size, int) or not 2 <= size <= 96:
        raise ValueError("unsupported bounded kernel or size")
    if deadline is not None and time.monotonic() >= deadline:
        return dict(completed=False, numerical_valid=None)
    left = [[((i + 2*j) % 17 - 8)/17 for j in range(size)] for i in range(size)]
    if kernel == "quadratic":
        expected = sum(sum(((i + 2*j) % 17 - 8)**2/289 + ((i + 2*j) % 17 - 8)/34
                           for j in range(size)) for i in range(size))
        checksum = 0.
        for _ in range(quadratic_repeats):
            checksum = 0.
            for row in left:
                if deadline is not None and time.monotonic() >= deadline:
                    return dict(completed=False, numerical_valid=None)
                checksum += sum(v*v + .5*v for v in row)
        valid = abs(checksum-expected) <= 1e-10*max(abs(expected), 1.)
    else:
        right = [[((3*i - j) % 19 - 9)/19 for j in range(size)] for i in range(size)]
        product = []
        for row in left:
            if deadline is not None and time.monotonic() >= deadline:
                return dict(completed=False, numerical_valid=None)
            product.append([sum(row[k]*right[k][j] for k in range(size)) for j in range(size)])
        probe = [(j % 11 - 5)/11 for j in range(size)]
        inner = [sum(row[j]*probe[j] for j in range(size)) for row in right]
        reference = [sum(row[j]*inner[j] for j in range(size)) for row in left]
        observed = [sum(row[j]*probe[j] for j in range(size)) for row in product]
        residual = math.sqrt(sum((a-b)**2 for a,b in zip(reference, observed)))
        norm = max(math.sqrt(sum(v*v for v in reference)), 1e-300)
        valid = residual/norm <= 1e-10 and all(math.isfinite(v) for v in observed)
        checksum = sum(sum(row) for row in product)
    if not valid or not math.isfinite(checksum):
        raise RuntimeError("actual numerical computation failed independent consistency verification")
    return dict(completed=deadline is None or time.monotonic() <= deadline,
                numerical_valid=True, checksum=checksum)


def regression_degree(sizes, costs):
    """Finite-domain cost slope, including a curvature diagnostic."""
    if len(sizes) != len(costs) or len(sizes) < 2 or any(q <= 0 or not math.isfinite(q) for q in costs):
        raise ValueError("paired positive sizes/costs are required")
    x, y = [math.log(k) for k in sizes], [math.log(q) for q in costs]
    xm, ym = statistics.mean(x), statistics.mean(y)
    denominator = sum((v-xm)**2 for v in x)
    if denominator <= 0:
        raise ValueError("cost dimension requires distinct coordinates")
    degree = sum((a-xm)*(b-ym) for a,b in zip(x,y))/denominator
    intercept = ym-degree*xm
    residual = math.sqrt(statistics.mean((b-intercept-degree*a)**2 for a,b in zip(x,y)))
    return dict(degree=degree, log_intercept=intercept, log_rms_curvature=residual)


def calibrate(config):
    """Cost data only: finish every job before any allocation trial starts."""
    validate_config(config)
    rows = []
    for block in range(config["calibration_blocks"]):
        tasks = [(kernel,k) for kernel in config["kernels"] for k in config["sizes"]]
        random.Random(config["seed"]+block).shuffle(tasks)
        for order,(kernel,size) in enumerate(tasks):
            costs = []
            for _ in range(config["calibration_jobs_per_block"]):
                # A far-future deadline executes the same row checks as trials.
                before = time.thread_time()
                outcome = execute_job(kernel,size,quadratic_repeats=config["quadratic_repeats"],
                                      deadline=time.monotonic()+5)
                cost = time.thread_time()-before
                if not outcome["completed"] or not outcome["numerical_valid"] or cost <= 0:
                    raise RuntimeError("calibration did not complete a positive-cost verified job")
                costs.append(cost)
            rows.append(dict(split="calibration",block_id=block,order_in_block=order,
                kernel=kernel,size=size,job_cpu_seconds=costs,numerical_valid=True,
                status="completed",measured_utc=__import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()))
    return rows


def calibration_summary(rows, config):
    """Mean cost and block-bootstrap slope from independent calibration rows."""
    validate_config(config)
    grouped = {}
    for row in rows:
        if row.get("split") != "calibration" or row.get("status") != "completed" or row.get("numerical_valid") is not True:
            raise ValueError("only completed numerical calibration rows may predict allocation")
        key = row["block_id"],row["kernel"],row["size"]
        if key in grouped:
            raise ValueError("duplicate calibration block/kernel/size")
        costs = row["job_cpu_seconds"]
        if len(costs) != config["calibration_jobs_per_block"] or any(not math.isfinite(q) or q <= 0 for q in costs):
            raise ValueError("calibration costs must be complete, finite and positive")
        grouped[key] = statistics.mean(costs)
    expected = {(b,k,s) for b in range(config["calibration_blocks"]) for k in config["kernels"] for s in config["sizes"]}
    if set(grouped) != expected:
        raise ValueError("every declared calibration block/kernel/size is required")
    summary = {}
    rng = random.Random(config["seed"]+10000)
    for kernel in config["kernels"]:
        block_costs = [[grouped[b,kernel,s] for s in config["sizes"]] for b in range(config["calibration_blocks"])]
        q = [statistics.mean(row[j] for row in block_costs) for j in range(len(config["sizes"]))]
        fit = regression_degree(config["sizes"],q)
        draws = []
        for _ in range(config["calibration_bootstrap_replicates"]):
            indices = [rng.randrange(len(block_costs)) for _ in block_costs]
            qb = [statistics.mean(block_costs[i][j] for i in indices) for j in range(len(q))]
            draws.append(regression_degree(config["sizes"],qb)["degree"])
        draws.sort()
        lower = draws[math.floor(.025*(len(draws)-1))]
        upper = draws[math.ceil(.975*(len(draws)-1))]
        summary[kernel] = dict(q_cpu_seconds=q,raw_block_costs=block_costs,
            independently_measured_cost_fit=fit,
            degree_nominal_block_bootstrap_interval=[lower,upper],
            degree_for_area_coordinate=fit["degree"]/2,
            leading_algorithm_operation_degree=2 if kernel=="quadratic" else 3,
            uncertainty="Nominal percentile resampling of 12 randomized calibration blocks; hardware drift and correlated blocks are not covered")
    return summary


def _normalize(values):
    total = sum(values)
    if total <= 0:
        raise ValueError("normalization requires positive unconditioned exposure")
    return [v/total for v in values]


def profile_predictions(sizes, edges, q_cpu, worker_counts, *, cost_degree=None):
    """Whole-cost forecasts and rivals; no abundance data enter this function."""
    if (len(q_cpu)!=len(sizes) or len(worker_counts)!=len(sizes) or len(edges)!=len(sizes)+1
            or any(not math.isfinite(q) or q<=0 for q in q_cpu)
            or any(not isinstance(n,int) or n<0 for n in worker_counts)):
        raise ValueError("paired positive independent costs and worker counts required")
    widths = [math.log(b/a) for a,b in zip(edges,edges[1:])]
    if any(not math.isfinite(w) or w<=0 for w in widths):
        raise ValueError("declared logarithmic widths must be positive")
    fair_cpu = _normalize(worker_counts)
    active = [int(n>0) for n in worker_counts]
    output = dict(
        fair_thread_cpu=dict(cpu_share=fair_cpu,count_share=_normalize([n/q for n,q in zip(worker_counts,q_cpu)])),
        equal_job_service=dict(cpu_share=_normalize([n*q for n,q in zip(worker_counts,q_cpu)]),count_share=_normalize(worker_counts)),
        equal_active_class_cpu=dict(cpu_share=_normalize(active),count_share=_normalize([n/q for n,q in zip(active,q_cpu)])),
        unit_cost_fair_cpu=dict(cpu_share=fair_cpu,count_share=_normalize([n/k for n,k in zip(worker_counts,sizes)])))
    if cost_degree is not None:
        output["power_cost_fair_cpu"] = dict(cpu_share=fair_cpu,
            count_share=_normalize([n*k**(-cost_degree) for n,k in zip(worker_counts,sizes)]))
    for row in output.values():
        row["cpu_share_per_log_width"] = [p/w for p,w in zip(row["cpu_share"],widths)]
    return output


def run_trial(kernel, config, worker_counts, *, order_seed=None):
    """Actual CPU allocation among runnable Python threads, without quotas."""
    metadata = runtime_metadata()
    if not metadata["gil_enabled"] or metadata["implementation"] != "CPython":
        raise RuntimeError("the declared single-execution-bottleneck runtime is unavailable")
    workers = [size for size,n in zip(config["sizes"],worker_counts) for _ in range(n)]
    order_seed=config["seed"] if order_seed is None else order_seed
    random.Random(order_seed).shuffle(workers)
    barrier = threading.Barrier(len(workers)+1)
    rows = [None]*len(workers)
    errors = []
    # Workers warm up and then wait. A shared future epoch gives the main
    # thread time to block in joins rather than competing for interpreter work.
    start = time.monotonic()+config["synchronization_lead_seconds"]
    stop = start+config["trial_seconds"]
    def worker(index,size):
        try:
            execute_job(kernel,4,quadratic_repeats=config["quadratic_repeats"])
            barrier.wait(timeout=5)
            while time.monotonic()<start:
                time.sleep(min(.001,max(0.,start-time.monotonic())))
            actual_start = time.monotonic()
            baseline = time.thread_time()
            completed=partial=0
            complete_cpu=partial_cpu=0.
            while time.monotonic()<stop:
                before=time.thread_time()
                result=execute_job(kernel,size,quadratic_repeats=config["quadratic_repeats"],deadline=stop)
                cost=time.thread_time()-before
                if result["completed"]:
                    completed+=1;complete_cpu+=cost
                else:
                    partial+=1;partial_cpu+=cost
                    break
            cpu=time.thread_time()-baseline
            actual_stop=time.monotonic()
            overhead=cpu-complete_cpu-partial_cpu
            if overhead < -1e-8:
                raise RuntimeError("thread CPU accounting is inconsistent")
            rows[index]=dict(size=size,thread_native_id=threading.get_native_id(),completed_jobs=completed,
                censored_partial_jobs=partial,cpu_seconds=cpu,complete_job_cpu_seconds=complete_cpu,
                partial_job_cpu_seconds=partial_cpu,loop_overhead_cpu_seconds=max(overhead,0.),
                actual_start_monotonic=actual_start,actual_stop_monotonic=actual_stop,
                start_lag_seconds=actual_start-start,stop_lag_seconds=actual_stop-stop)
        except BaseException as error:
            errors.append(repr(error))
            barrier.abort()
    threads=[threading.Thread(target=worker,args=(i,size)) for i,size in enumerate(workers)]
    for thread in threads:thread.start()
    envelope_start=time.monotonic();process_start=time.process_time()
    barrier.wait(timeout=5)
    for thread in threads:
        thread.join(timeout=config["trial_seconds"]+5)
    process_cpu=time.process_time()-process_start
    envelope_stop=time.monotonic()
    if errors or any(thread.is_alive() for thread in threads) or any(row is None for row in rows):
        raise RuntimeError("allocation trial failed: "+repr(errors))
    worker_cpu=sum(row["cpu_seconds"] for row in rows)
    unassigned=process_cpu-worker_cpu
    if unassigned < -1e-6:
        raise RuntimeError("measured thread CPU exceeds its enclosing process CPU interval")
    return dict(workers=rows,worker_order_seed=order_seed,worker_creation_size_order=workers,
        start_at_monotonic=start,stop_at_monotonic=stop,
        process_control_envelope_cpu_seconds=process_cpu,worker_cpu_seconds=worker_cpu,
        unassigned_process_cpu_seconds=max(unassigned,0.),
        process_control_envelope_wall_seconds=envelope_stop-envelope_start,
        interpretation="The enclosing process interval includes common pre-start waits, controller bookkeeping and final joins; primary worker charges cover their common trial window",
        timing_assumptions_satisfied=all(r["start_lag_seconds"]<=config["maximum_start_lag_seconds"]
            and r["stop_lag_seconds"]<=config["maximum_stop_lag_seconds"] for r in rows))


def summarize_trials(trials, config, q_cpu, predictions, worker_counts):
    """Pool raw CPU and completed work once; retain missing classes as zeros."""
    sizes,edges=config["sizes"],config["log_bin_edges"]
    cpu=[0.]*len(sizes);complete_cpu=[0.]*len(sizes);partial_cpu=[0.]*len(sizes);overhead=[0.]*len(sizes);jobs=[0]*len(sizes)
    for trial in trials:
        seen=[0]*len(sizes)
        for row in trial["workers"]:
            j=sizes.index(row["size"]);seen[j]+=1
            if not math.isclose(row["cpu_seconds"],row["complete_job_cpu_seconds"]+row["partial_job_cpu_seconds"]+row["loop_overhead_cpu_seconds"],abs_tol=1e-7):
                raise ValueError("partial jobs and overhead must remain in primary CPU accounting")
            cpu[j]+=row["cpu_seconds"];complete_cpu[j]+=row["complete_job_cpu_seconds"]
            partial_cpu[j]+=row["partial_job_cpu_seconds"];overhead[j]+=row["loop_overhead_cpu_seconds"]
            jobs[j]+=row["completed_jobs"]
        if seen!=worker_counts:
            raise ValueError("actual runnable opportunities differ from the frozen design")
    shares,counts=_normalize(cpu),_normalize(jobs)
    reconstruction=[n*q for n,q in zip(jobs,q_cpu)]
    widths=[math.log(b/a) for a,b in zip(edges,edges[1:])]
    errors={name:dict(maximum_absolute_cpu_share_error=max(abs(a-b) for a,b in zip(shares,pred["cpu_share"])),
                     count_total_variation=.5*sum(abs(a-b) for a,b in zip(counts,pred["count_share"])))
            for name,pred in predictions.items()}
    active=[i for i,n in enumerate(worker_counts) if n>0 and jobs[i]>0 and complete_cpu[i]>0]
    dimension={}
    if len(active)>=2:
        active_sizes=[sizes[i] for i in active]
        count_fit=regression_degree(active_sizes,[jobs[i]/widths[i] for i in active])
        linear_fit=regression_degree(active_sizes,[jobs[i]/(edges[i+1]-edges[i]) for i in active])
        tilt_fit=regression_degree(active_sizes,[cpu[i]/widths[i] for i in active])
        actual_cost_fit=regression_degree(active_sizes,[complete_cpu[i]/jobs[i] for i in active])
        dimension=dict(apparent_log_class_count_degree=-count_fit["degree"],
            binned_linear_density_degree=-linear_fit["degree"],
            observed_full_cpu_allocation_tilt=tilt_fit["degree"],
            realized_completed_job_cost_degree=actual_cost_fit["degree"],
            interpretation="Descriptive finite-class slopes; these are not fitted continuous power-law tails. Absent classes remain zeros in full profiles and are not in slope diagnostics.")
    return dict(cpu_seconds_by_class=cpu,measured_cpu_share=shares,completed_jobs_by_class=jobs,count_share=counts,
        complete_job_cpu_seconds_by_class=complete_cpu,partial_job_cpu_seconds_by_class=partial_cpu,
        loop_overhead_cpu_seconds_by_class=overhead,calibrated_completed_job_cpu_seconds_by_class=reconstruction,
        reconstruction_relative_error_by_active_class=[(r-c)/c if c>0 else None for r,c in zip(reconstruction,complete_cpu)],
        cpu_resource_per_log_class=[c/w for c,w in zip(cpu,widths)],dimension_diagnostics=dimension,
        forecasts=predictions,errors=errors,
        pooled_cpu_within_frozen_tolerance=errors["fair_thread_cpu"]["maximum_absolute_cpu_share_error"]<=config["maximum_absolute_cpu_share_error_tolerance"],
        pooled_counts_within_frozen_tolerance=errors["fair_thread_cpu"]["count_total_variation"]<=config["count_total_variation_tolerance"])
