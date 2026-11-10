"""Compare a BioMe replay without rewriting the frozen diagnostic.

Only computed floating results use the independent verifier's existing
tolerances. Design metadata, counts, types and provenance remain exact.
This is a retrospective numerical replay check, not an empirical criterion.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / 'results/biome-stock-audit-2026-10-23'
REL_TOL = 1e-11
ABS_TOL = 1e-10


def load_json(path):
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f'Duplicate JSON field: {key}')
            result[key] = value
        return result

    def invalid_constant(value):
        raise ValueError(f'Nonfinite JSON value: {value}')

    return json.loads(path.read_bytes(), object_pairs_hook=unique_pairs,
                      parse_constant=invalid_constant)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compare(expected, actual, stats, path):
    if type(actual) is not type(expected):
        raise ValueError(f'Different type at {path}')
    if isinstance(expected, dict):
        if expected.keys() != actual.keys():
            raise ValueError(f'Different fields at {path}')
        for key in expected:
            compare(expected[key], actual[key], stats, f'{path}.{key}')
    elif isinstance(expected, list):
        if len(expected) != len(actual):
            raise ValueError(f'Different list length at {path}')
        for index, (left, right) in enumerate(zip(expected, actual)):
            compare(left, right, stats, f'{path}[{index}]')
    elif isinstance(expected, float):
        if not math.isfinite(expected) or not math.isfinite(actual):
            raise ValueError(f'Nonfinite value at {path}')
        computed = (path.startswith('diagnostic.dyes.')
                    and not path.endswith('.pore_um'))
        computed = computed or path == 'verification.maximum_absolute_difference'
        if computed:
            if not math.isclose(expected, actual, rel_tol=REL_TOL, abs_tol=ABS_TOL):
                raise ValueError(f'Numerical replay differs at {path}')
            difference = abs(expected - actual)
            stats['floating_comparisons'] += 1
            stats['different_floats'] += expected != actual
            stats['maximum_absolute_difference'] = max(
                stats['maximum_absolute_difference'], difference)
        elif expected != actual:
            raise ValueError(f'Design metadata differs at {path}')
    elif expected != actual:
        raise ValueError(f'Values differ at {path}')


def check_replay(reference_dir, replay_dir):
    documents = {}
    hashes = {}
    for label, directory in (('reference', reference_dir), ('replay', replay_dir)):
        diagnostic_path = directory / 'diagnostic.json'
        verification_path = directory / 'verification.json'
        diagnostic = load_json(diagnostic_path)
        verification = load_json(verification_path)
        diagnostic_hash = digest(diagnostic_path)
        if verification['diagnostic_sha256'] != diagnostic_hash:
            raise ValueError(f'{label} verifier is bound to a different diagnostic')
        if verification['passed'] is not True:
            raise ValueError(f'{label} independent verification did not pass')
        if (verification['relative_tolerance'] != REL_TOL
                or verification['absolute_tolerance'] != ABS_TOL):
            raise ValueError(f'{label} independent verification tolerance changed')
        error = verification['maximum_absolute_difference']
        if type(error) is not float or not math.isfinite(error) or error < 0:
            raise ValueError(f'{label} independent verification error is invalid')
        documents[label] = (diagnostic, verification)
        hashes[label] = {'diagnostic_sha256': diagnostic_hash,
                         'verification_sha256': digest(verification_path)}

    stats = {'floating_comparisons': 0, 'different_floats': 0,
             'maximum_absolute_difference': 0.}
    compare(documents['reference'][0], documents['replay'][0], stats, 'diagnostic')
    diagnostic_stats = dict(stats)
    # Each hash was checked against its own diagnostic, not ignored or copied
    # from the reference. Every other verifier field is compared below.
    reports = [{key: value for key, value in report.items() if key != 'diagnostic_sha256'}
               for _, report in documents.values()]
    compare(reports[0], reports[1], stats, 'verification')
    return {
        'passed': True,
        'scope': 'numerical replay of the frozen BioMe diagnostic; not a new empirical test',
        'relative_tolerance': REL_TOL, 'absolute_tolerance': ABS_TOL,
        'tolerance_source': 'unchanged independent BioMe verifier',
        'diagnostic_byte_equal': hashes['reference']['diagnostic_sha256'] == hashes['replay']['diagnostic_sha256'],
        'verification_byte_equal': hashes['reference']['verification_sha256'] == hashes['replay']['verification_sha256'],
        'hashes': hashes,
        'diagnostic_comparison': diagnostic_stats,
        'including_verification': stats,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--replay-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    protected = [directory / filename for directory in (REFERENCE, args.replay_dir)
                 for filename in ('diagnostic.json', 'verification.json')]
    if args.output.resolve() in [path.resolve() for path in protected]:
        parser.error('Replay report must not overwrite an input artifact')
    report = check_replay(REFERENCE, args.replay_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
