"""Append-only, hash-checked run records and privacy-limited hardware metadata.

Registration checks the complete existing registry before appending. A changed
source or artifact therefore fails an audit instead of silently replacing a
historical digest. JSONL records are locked and flushed; this is a local audit
trail, not an external timestamp service or a tamper-proof archive.
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import subprocess
import tempfile


SCHEMA_VERSION = 1
DEFAULT_REGISTRY = 'results/run-registry.jsonl'
THREAD_VARIABLES = (
    'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'OMP_NUM_THREADS',
    'VECLIB_MAXIMUM_THREADS', 'BLIS_NUM_THREADS', 'NUMEXPR_NUM_THREADS',
)
_RUN_ID = re.compile(r'[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}\Z')
_DIGEST = re.compile(r'[0-9a-f]{64}\Z')


def _canonical(value):
    try:
        return json.dumps(value, sort_keys=True, separators=(',', ':'),
                          ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError) as error:
        raise ValueError('Run records must be finite, JSON-serializable values') from error


def _relative_path(repo_root, relative_path):
    if not isinstance(relative_path, str) or not relative_path or '\\' in relative_path:
        raise ValueError('A repository-relative POSIX file path is required')
    path = PurePosixPath(relative_path)
    if path.is_absolute() or '..' in path.parts or path.as_posix() != relative_path:
        raise ValueError(f'Unsafe or noncanonical relative path: {relative_path!r}')
    root = Path(repo_root).resolve()
    resolved = (root / relative_path).resolve()
    if not resolved.is_relative_to(root):
        raise ValueError(f'File resolves outside repository: {relative_path!r}')
    return resolved


def hash_file(repo_root, relative_path):
    """SHA256 a regular file referenced by a safe repository-relative path."""
    path = _relative_path(repo_root, relative_path)
    if not path.is_file():
        raise ValueError(f'Registered file is missing or not regular: {relative_path}')
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def file_reference(repo_root, relative_path, **metadata):
    """Create a file reference; callers may attach role/provenance metadata."""
    if 'path' in metadata or 'sha256' in metadata:
        raise ValueError('File-reference metadata cannot replace path or sha256')
    return dict(path=relative_path, sha256=hash_file(repo_root, relative_path), **metadata)


def archive_reference(repo_root, relative_path):
    """Snapshot source/config bytes under data/run-sources/<sha256>/<basename>.

    The original_path is provenance, while path addresses immutable copied
    bytes. Subsequent edits to live source do not invalidate old runs. Atomic
    linking never overwrites an existing archive; conflicting bytes fail.
    """
    source = _relative_path(repo_root, relative_path)
    if not source.is_file():
        raise ValueError(f'Archive source is missing or not regular: {relative_path}')
    contents = source.read_bytes()
    digest = hashlib.sha256(contents).hexdigest()
    archived = f'data/run-sources/{digest}/{source.name}'
    target = _relative_path(repo_root, archived)
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(dir=target.parent, prefix='.archive-', delete=False) as handle:
                temporary = Path(handle.name)
                handle.write(contents)
                handle.flush()
                os.fsync(handle.fileno())
            try:
                os.link(temporary, target)
            except FileExistsError:
                pass  # Another writer linked the same content-addressed target.
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
    if hash_file(repo_root, archived) != digest:
        raise ValueError(f'Conflicting immutable source archive: {archived}')
    return dict(path=archived, sha256=digest, original_path=relative_path,
                provenance='Content-addressed byte snapshot at registration')


def _nonempty_text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{field} must be a nonempty string')


def _references(entry):
    references = []
    for field in ('data_inputs', 'configs', 'artifacts'):
        values = entry.get(field)
        if not isinstance(values, list) or (field != 'data_inputs' and not values):
            raise ValueError(f'{field} must be a list' + (' of at least one file' if field != 'data_inputs' else ''))
        references.extend(values)
    algorithms = entry.get('algorithms')
    if not isinstance(algorithms, list) or not algorithms:
        raise ValueError('algorithms must list at least one named source bundle')
    for algorithm in algorithms:
        if not isinstance(algorithm, dict):
            raise ValueError('Each algorithm must be an object')
        _nonempty_text(algorithm.get('name'), 'algorithm.name')
        if not isinstance(algorithm.get('sources'), list) or not algorithm['sources']:
            raise ValueError('Each algorithm must retain at least one source digest')
        references.extend(algorithm['sources'])
    return references


def _validate_entry(repo_root, entry, known_ids):
    if (not isinstance(entry, dict) or type(entry.get('schema_version')) is not int or
            entry.get('schema_version') != SCHEMA_VERSION):
        raise ValueError(f'Run entry schema_version must be {SCHEMA_VERSION}')
    run_id = entry.get('run_id')
    if not isinstance(run_id, str) or not _RUN_ID.fullmatch(run_id):
        raise ValueError('run_id must be a bounded alphanumeric identifier')
    if entry.get('evidence_kind') not in ('simulation', 'constructed_prediction', 'actual_measurement'):
        raise ValueError('evidence_kind must distinguish simulation, constructed_prediction, or actual_measurement')
    resources = entry.get('resources')
    if not isinstance(resources, list) or not resources:
        raise ValueError('resources must list definitions and units')
    for resource in resources:
        if not isinstance(resource, dict):
            raise ValueError('Each resource definition must be an object')
        for field in ('name', 'definition', 'units'):
            _nonempty_text(resource.get(field), f'resource.{field}')
    for field in ('generated_seeds', 'hardware_metadata', 'summary'):
        if not isinstance(entry.get(field), dict):
            raise ValueError(f'{field} must be an object (use an explicit unavailable label when needed)')
    relationships = entry.get('relationships')
    if not isinstance(relationships, list):
        raise ValueError('relationships must be a list, possibly empty')
    for relationship in relationships:
        if not isinstance(relationship, dict):
            raise ValueError('Each relationship must be an object')
        _nonempty_text(relationship.get('type'), 'relationship.type')
        parent = relationship.get('run_id')
        if not isinstance(parent, str) or parent == run_id or parent not in known_ids:
            raise ValueError(f'Related run {parent!r} must already be registered and cannot be the run itself')
    seen_paths = {}
    for reference in _references(entry):
        if not isinstance(reference, dict):
            raise ValueError('File references must contain path and sha256')
        path, digest = reference.get('path'), reference.get('sha256')
        if not isinstance(path, str):
            raise ValueError('File references require a relative string path')
        if not isinstance(digest, str) or not _DIGEST.fullmatch(digest):
            raise ValueError(f'Invalid SHA256 digest for {path!r}')
        if path in seen_paths and seen_paths[path] != digest:
            raise ValueError(f'Conflicting digests in run entry for {path!r}')
        actual = hash_file(repo_root, path)
        if actual != digest:
            raise ValueError(f'Changed registered file: {path}; expected {digest}, observed {actual}')
        seen_paths[path] = digest
    _canonical(entry)


def _read_registry(repo_root, handle):
    handle.seek(0)
    lines = handle.readlines()
    entries = {}
    for number, line in enumerate(lines, 1):
        if not line.endswith('\n') or not line.strip():
            raise ValueError(f'Registry line {number} is empty or incomplete; preserve and inspect it')
        try:
            record = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f'Registry line {number} is invalid JSON') from error
        if not isinstance(record, dict):
            raise ValueError(f'Registry line {number} must be an object')
        stored = record.pop('entry_sha256', None)
        observed = hashlib.sha256(_canonical(record).encode('utf-8')).hexdigest()
        if stored != observed:
            raise ValueError(f'Registry line {number} entry digest does not match')
        _validate_entry(repo_root, record, set(entries))
        run_id = record['run_id']
        if run_id in entries:
            raise ValueError(f'Registry contains duplicate run_id {run_id!r}')
        entries[run_id] = record
    return entries


def register_run(repo_root, entry, registry_path=DEFAULT_REGISTRY):
    """Append an immutable run, or return appended=False for an exact repeat.

    A relationship references an earlier record, giving an acyclic ordered
    lineage. Registration audits every prior entry and all its file digests.
    """
    import fcntl
    if not isinstance(entry, dict) or 'entry_sha256' in entry:
        raise ValueError('Supply a run entry without the reserved entry_sha256 field')
    # Freeze caller-owned containers and reject NaNs before any registry write.
    entry = json.loads(_canonical(entry))
    path = _relative_path(repo_root, registry_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a+', encoding='utf-8', newline='\n') as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        entries = _read_registry(repo_root, handle)
        _validate_entry(repo_root, entry, set(entries))
        digest = hashlib.sha256(_canonical(entry).encode('utf-8')).hexdigest()
        previous = entries.get(entry['run_id'])
        if previous is not None:
            if previous != entry:
                raise ValueError(f'Conflicting immutable run_id: {entry["run_id"]}')
            return dict(run_id=entry['run_id'], appended=False, entry_sha256=digest)
        handle.seek(0, os.SEEK_END)
        handle.write(_canonical(dict(entry, entry_sha256=digest)) + '\n')
        handle.flush()
        os.fsync(handle.fileno())
        return dict(run_id=entry['run_id'], appended=True, entry_sha256=digest)


def verify_registry(repo_root, registry_path=DEFAULT_REGISTRY):
    """Audit immutable records, ordered lineage, and all current file hashes."""
    import fcntl
    path = _relative_path(repo_root, registry_path)
    if not path.is_file():
        raise ValueError(f'Registry does not exist: {registry_path}')
    with path.open('r', encoding='utf-8', newline='\n') as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_SH)
        entries = _read_registry(repo_root, handle)
    return dict(valid=True, runs=len(entries), run_ids=list(entries),
                file_references=sum(len(_references(entry)) for entry in entries.values()))


def _sysctl(key):
    # Explicit keys only: never hostname, username, serial number, or broad dumps.
    try:
        result = subprocess.run(['/usr/sbin/sysctl', '-n', key], check=False,
                                text=True, capture_output=True, timeout=3)
        return result.stdout.strip() if result.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def _hardware_details(system):
    if system == 'Darwin':
        memory = _sysctl('hw.memsize')
        return dict(cpu_model=_sysctl('machdep.cpu.brand_string'),
                    total_ram_bytes=int(memory) if memory and memory.isdecimal() else None,
                    os_build=_sysctl('kern.osversion'))
    if system == 'Linux':
        model = None
        memory = None
        try:
            for line in Path('/proc/cpuinfo').read_text().splitlines():
                key, separator, value = line.partition(':')
                if separator and key.strip() in ('model name', 'Hardware'):
                    model = value.strip()
                    break
            for line in Path('/proc/meminfo').read_text().splitlines():
                if line.startswith('MemTotal:'):
                    fields = line.split()
                    if len(fields) == 3 and fields[2] == 'kB':
                        memory = int(fields[1]) * 1024
                    break
        except (OSError, ValueError):
            pass
        return dict(cpu_model=model, total_ram_bytes=memory, os_build=platform.version())
    return dict(cpu_model=None, total_ram_bytes=None, os_build=None)


def _numpy_metadata():
    try:
        import numpy as np
    except ImportError:
        return dict(available=False, version=None, blas=dict(name=None, version=None))
    config = getattr(np.__config__, 'CONFIG', {})
    blas = config.get('Build Dependencies', {}).get('blas', {}) if isinstance(config, dict) else {}
    return dict(available=True, version=np.__version__,
                blas=dict(name=blas.get('name'), version=blas.get('version')))


def _runtime_threads(blas_name):
    try:
        from threadpoolctl import threadpool_info
        reported = threadpool_info()
    except ImportError:
        return dict(inspection_available=False, blas_count_available=False,
                    libraries=[], thread_count_verified=False,
                    verified_single_thread=False,
                    scope='Optional threadpoolctl is unavailable; requested environment is not runtime verification')
    # Remove absolute library paths and all metadata outside this safe allowlist.
    fields = ('user_api', 'internal_api', 'prefix', 'version', 'num_threads', 'architecture')
    libraries = [{field: library.get(field) for field in fields} for library in reported]
    blas = [library for library in libraries if library['user_api'] == 'blas' and
            isinstance(library['num_threads'], int) and library['num_threads'] > 0]
    # Accelerate is not covered by threadpoolctl's supported BLAS providers.
    supported = bool(blas) and blas_name in ('openblas', 'mkl', 'blis', 'flexiblas')
    return dict(inspection_available=True, blas_count_available=supported,
                libraries=libraries, thread_count_verified=supported,
                verified_single_thread=supported and all(library['num_threads'] == 1 for library in blas),
                scope='Current collector process, supported loaded BLAS providers only; Accelerate runtime counts unavailable')


def collect_hardware_metadata(requested_threads=None):
    """Read current host/software facts without host, account, or serial IDs.

    Metadata describes the collector process at call time. It cannot establish
    hardware for an earlier run or verify threads in a separate worker. No
    environment variable is changed, and no dependency is installed.
    """
    if requested_threads is None:
        requested_threads = {key: os.environ[key] for key in THREAD_VARIABLES if key in os.environ}
    if not isinstance(requested_threads, dict) or any(key not in THREAD_VARIABLES for key in requested_threads):
        raise ValueError('requested_threads must map supported thread environment variables to requested values')
    requested = {key: str(value) for key, value in requested_threads.items()}
    system = platform.system()
    details = _hardware_details(system)
    numpy = _numpy_metadata()
    return dict(collected_utc=datetime.now(timezone.utc).isoformat(),
                recording_scope='Current metadata collector process; not a historical hardware reconstruction',
                os=dict(system=system, release=platform.release(), version=platform.version(),
                        build=details['os_build'],
                        product_version=platform.mac_ver()[0] if system == 'Darwin' else None),
                cpu=dict(model=details['cpu_model'], architecture=platform.machine(),
                         logical_count=os.cpu_count()),
                total_ram_bytes=details['total_ram_bytes'], python_version=platform.python_version(),
                availability=dict(cpu_model=details['cpu_model'] is not None,
                                  total_ram=details['total_ram_bytes'] is not None,
                                  os_build=details['os_build'] is not None),
                numpy=numpy, requested_thread_environment=requested,
                runtime_thread_verification=_runtime_threads(numpy['blas']['name']))
