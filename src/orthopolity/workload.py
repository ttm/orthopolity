"""Measured dense-matrix work with cooperative resource checkpoints.

The parent must set BLAS thread environment variables before NumPy is imported
and run each task in a fresh child. Peak RSS is the TOTAL child-process peak,
including imports and warmup. CPU accounting starts after imports and fixed
warmup, before RNG/task construction, and includes numerical verification.
Checks occur between phases; these are not operating-system hard limits.
"""
from __future__ import annotations

import math
import sys
import time


MAX_MATRIX_SIZE = 2048
MAX_REPEATS = 32
MAX_WARMUP_SIZE = 256
VERIFICATION_TOLERANCE = 1e-10


def normalize_peak_rss(raw_peak, platform=None):
    """Convert ru_maxrss to bytes: Darwin reports bytes, Linux reports KiB."""
    platform = sys.platform if platform is None else platform
    if not math.isfinite(raw_peak) or raw_peak < 0:
        raise ValueError('A finite nonnegative resident-memory peak is required')
    if platform == 'darwin':
        return int(raw_peak)
    if platform.startswith('linux'):
        return int(raw_peak * 1024)
    raise NotImplementedError(f'Peak-RSS units are not specified for platform {platform!r}')


def _read_process_usage():
    import resource
    usage = resource.getrusage(resource.RUSAGE_SELF)
    return dict(cpu_user_seconds=float(usage.ru_utime),
                cpu_system_seconds=float(usage.ru_stime),
                cpu_total_seconds=float(usage.ru_utime + usage.ru_stime),
                peak_rss_bytes=normalize_peak_rss(usage.ru_maxrss))


def _threadpool_metadata():
    try:
        from threadpoolctl import threadpool_info
    except ImportError:
        return dict(available=False, libraries=[])
    return dict(available=True, libraries=threadpool_info())


def verify_matrix_product(left, right, product, probe, *, tolerance=VERIFICATION_TOLERANCE):
    """Independently compare product@v with left@(right@v), using float64.

    A deterministic independently randomized, scaled probe checks the actual
    product. This is a numerical consistency check, not an exhaustive element
    comparison or a proof against every conceivable adversarial error.
    """
    import numpy as np
    left, right, product, probe = (np.asarray(v, dtype=np.float64) for v in (left, right, product, probe))
    if (left.ndim != 2 or right.ndim != 2 or product.ndim != 2 or probe.ndim != 1 or
        left.shape[1] != right.shape[0] or product.shape != (left.shape[0], right.shape[1]) or
        probe.shape != (right.shape[1],) or not math.isfinite(tolerance) or tolerance <= 0):
        raise ValueError('Aligned matrices, probe, and positive finite tolerance required')
    reference = left @ (right @ probe)
    observed = product @ probe
    finite = bool(np.all(np.isfinite(product)) and np.all(np.isfinite(reference)) and np.all(np.isfinite(observed)))
    if not finite:
        return dict(passed=False, relative_residual=None, absolute_residual=None,
                    reference_norm=None, tolerance=tolerance, checksum=None,
                    failure='Nonfinite matrix product or verification vector')
    reference_norm = float(np.linalg.norm(reference))
    absolute = float(np.linalg.norm(observed-reference))
    relative = absolute/max(reference_norm, float(np.finfo(np.float64).tiny))
    checksum = float(np.sum(product, dtype=np.float64))
    passed = bool(math.isfinite(relative) and math.isfinite(checksum) and relative <= tolerance)
    return dict(passed=passed,
                relative_residual=relative if math.isfinite(relative) else None,
                absolute_residual=absolute if math.isfinite(absolute) else None,
                reference_norm=reference_norm, tolerance=tolerance,
                checksum=checksum if math.isfinite(checksum) else None,
                failure=None if passed else 'Independent matrix-vector residual exceeds tolerance')


def _bounded_integer(value, name, upper):
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= upper:
        raise ValueError(f'{name} must be an integer in [1,{upper}]')


def _validate_budget(value, name):
    if value is not None and (isinstance(value, bool) or not math.isfinite(value) or value < 0):
        raise ValueError(f'{name} must be a finite nonnegative allowance or None')


def run_workload(size, *, repeats=3, memory_budget_bytes=None,
                 cpu_budget_seconds=None, warmup_size=64):
    """Run a deterministic actual workload and return JSON-safe measurements.

    Reuse two size-by-size float64 inputs and one committed output buffer.
    Every repeat performs A@B and independent matrix-vector verification. The
    same size always uses the same inputs/probe; calibration and evaluation
    do not change task contents. Limits are checked after warmup, allocations,
    each matrix multiply, and each verification. A phase may overshoot its CPU
    allowance before the next cooperative check observes and reports that cost.
    """
    _bounded_integer(size, 'size', MAX_MATRIX_SIZE)
    _bounded_integer(repeats, 'repeats', MAX_REPEATS)
    _bounded_integer(warmup_size, 'warmup_size', MAX_WARMUP_SIZE)
    _validate_budget(memory_budget_bytes, 'memory_budget_bytes')
    _validate_budget(cpu_budget_seconds, 'cpu_budget_seconds')
    worker_start = time.perf_counter()
    import numpy as np
    # NumPy exposes these subpackages lazily. Import them before the CPU origin
    # so task construction/verification do not accidentally include import work.
    from numpy.random import SeedSequence, default_rng
    from numpy.linalg import norm

    warm = np.ones((warmup_size, warmup_size), dtype=np.float64)
    warm_output = np.empty_like(warm)
    np.matmul(warm, warm, out=warm_output)
    del warm, warm_output
    threadpools = _threadpool_metadata()
    baseline = _read_process_usage()
    workload_start = time.perf_counter()
    checkpoints = []
    verification = None
    multiplications = verified = 0

    def checkpoint(phase):
        usage = _read_process_usage()
        cpu = max(0.0, usage['cpu_total_seconds']-baseline['cpu_total_seconds'])
        violations = []
        if memory_budget_bytes is not None and usage['peak_rss_bytes'] > memory_budget_bytes:
            violations.append('memory')
        if cpu_budget_seconds is not None and cpu > cpu_budget_seconds:
            violations.append('cpu')
        snapshot = dict(phase=phase, cpu_seconds=cpu,
            cpu_user_seconds=max(0.0, usage['cpu_user_seconds']-baseline['cpu_user_seconds']),
            cpu_system_seconds=max(0.0, usage['cpu_system_seconds']-baseline['cpu_system_seconds']),
            wall_seconds=float(time.perf_counter()-workload_start),
            peak_rss_bytes=usage['peak_rss_bytes'], violated_budgets=violations)
        checkpoints.append(snapshot)
        return violations

    def finish(status, failure=None):
        last = checkpoints[-1]
        numerical_valid = (False if verification is not None and not verification['passed'] else
                           True if multiplications > 0 and verified == multiplications else None)
        return dict(status=status, completed=status == 'completed', failure=failure,
            numerical_valid=numerical_valid,
            quota_status='within_limits' if status == 'completed' else status,
            size=size, repeats=repeats, warmup_size=warmup_size, dtype='float64',
            deterministic_seed=[1729, size], multiplications_completed=multiplications,
            verified_multiplications=verified,
            memory_budget_bytes=memory_budget_bytes, cpu_budget_seconds=cpu_budget_seconds,
            baseline_rss_bytes=baseline['peak_rss_bytes'], baseline_peak_rss_bytes=baseline['peak_rss_bytes'],
            peak_rss_bytes=last['peak_rss_bytes'],
            cpu_seconds=last['cpu_seconds'], cpu_user_seconds=last['cpu_user_seconds'],
            cpu_system_seconds=last['cpu_system_seconds'], wall_seconds=last['wall_seconds'],
            worker_wall_seconds=float(time.perf_counter()-worker_start),
            checksum=verification['checksum'] if verification is not None else None,
            verification=verification, checkpoints=checkpoints, threadpools=threadpools,
            measurement=dict(peak_rss='total process ru_maxrss normalized to bytes; includes imports/warmup',
                cpu='process user+system seconds after imports/warmup; includes inputs and verification',
                wall='workload wall seconds after imports/warmup',
                enforcement='cooperative checkpoints; no operating-system hard limit',
                platform=sys.platform))

    def quota_failure(violations):
        status = 'memory_quota' if 'memory' in violations else 'cpu_quota'
        return finish(status, 'Observed resource allowance exceeded at '+checkpoints[-1]['phase'])

    violations = checkpoint('start')
    if violations:
        return quota_failure(violations)
    rng = default_rng(SeedSequence([1729, size]))
    left = rng.standard_normal((size, size), dtype=np.float64)
    right = rng.standard_normal((size, size), dtype=np.float64)
    scale = 1/math.sqrt(size)
    left *= scale
    right *= scale
    product = np.empty((size, size), dtype=np.float64)
    product.fill(0.0)  # Commit resident pages before the allocation checkpoint.
    probe = default_rng(SeedSequence([1730, size])).standard_normal(size)
    probe /= norm(probe)
    violations = checkpoint('allocations')
    if violations:
        return quota_failure(violations)
    for repeat in range(1, repeats+1):
        np.matmul(left, right, out=product)
        multiplications += 1
        violations = checkpoint(f'matmul_{repeat}')
        if violations:
            return quota_failure(violations)
        verification = verify_matrix_product(left, right, product, probe)
        if verification['passed']:
            verified += 1
        violations = checkpoint(f'verification_{repeat}')
        if not verification['passed']:
            return finish('numerical_failure', verification['failure'])
        if violations:
            return quota_failure(violations)
    return finish('completed')
