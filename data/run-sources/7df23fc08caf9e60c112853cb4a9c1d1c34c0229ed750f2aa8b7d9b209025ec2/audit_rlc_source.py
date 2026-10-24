"""Independently audit released RLC measurements against JSON and MATLAB files.

Decimal JSON parsing and an explicit complex-string grammar are independent of
the runner; scipy loads the redundant binary MATLAB numeric arrays. No circuit
parameters are estimated and no production analysis functions are imported.
"""
import argparse
from decimal import Decimal
import hashlib
import json
import math
from pathlib import Path
import re

import numpy as np
from scipy.io import loadmat


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/'data/physics-candidates/2026-10-24/rlc'
NUMBER = r'(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][+-]?\d+)?'
COMPLEX = re.compile(rf'^\s*([+-]?{NUMBER})([+-]{NUMBER})i\s*$')
NUMERIC_FIELDS = ('f', 'omega', 'z_real', 'z_imag', 'z_modulus', 'z_phase')


def parse_complex(text):
    matched = COMPLEX.fullmatch(text)
    if matched is None:
        raise AssertionError('Unexpected complex-string encoding')
    return complex(float(Decimal(matched[1])), float(Decimal(matched[2])))


def compare_tolerant(actual, expected, relative, absolute, label):
    discrepancy = abs(actual-expected)
    if not math.isfinite(discrepancy) or discrepancy > absolute+relative*abs(expected):
        raise AssertionError(f'Redundant source representations disagree: {label}')
    return discrepancy


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--result', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    released_bytes = args.result.read_bytes()
    released = json.loads(released_bytes)
    config = json.loads((ROOT/'configs/rlc_boundary_2026-10-24.json').read_text())
    count = config['expected_rows']
    relative = config['source_encoding_relative_tolerance']
    absolute = config['source_encoding_absolute_tolerance']
    receipt = json.loads((SOURCE/'acquisition.json').read_text())
    for entry in receipt['files']:
        raw = (SOURCE/entry['file']).read_bytes()
        if (len(raw) != entry['bytes'] or hashlib.sha256(raw).hexdigest() != entry['sha256']
                or hashlib.md5(raw).hexdigest() != entry['md5']):
            raise AssertionError(f'Original source checksum differs: {entry["file"]}')
    original = json.loads((SOURCE/'rlc_circuit.json').read_text(),
                          parse_float=Decimal, parse_int=Decimal)
    binary = loadmat(SOURCE/'rlc_circuit.mat', struct_as_record=True, squeeze_me=False)
    numeric = {}
    comparisons = {}
    for name in NUMERIC_FIELDS:
        if len(original[name]) != count or any(not isinstance(v, Decimal) for v in original[name]):
            raise AssertionError(f'Unexpected JSON numeric array: {name}')
        numeric[name] = [float(v) for v in original[name]]
        other = np.asarray(binary[name]).reshape(-1)
        if len(other) != count:
            raise AssertionError(f'Unexpected MATLAB numeric array: {name}')
        if any(not math.isfinite(a) or a != float(b) for a, b in zip(numeric[name], other)):
            raise AssertionError(f'MATLAB numeric values differ from JSON: {name}')
        comparisons[name] = {'count': count, 'exactly_equal': True,
                             'maximum_absolute_difference': 0.}
    observed = [complex(re, im) for re, im in zip(numeric['z_real'], numeric['z_imag'])]
    matlab_complex = np.asarray(binary['z']).reshape(-1)
    if len(matlab_complex) != count or any(a != b for a, b in zip(observed, matlab_complex)):
        raise AssertionError('MATLAB complex array differs from JSON components')
    if len(original['z']) != count:
        raise AssertionError('Complex-string count differs')
    strings = [parse_complex(value) for value in original['z']]
    maximum_string_difference = max(compare_tolerant(a, b, relative, absolute, f'z[{i}]')
                                    for i, (a, b) in enumerate(zip(strings, observed)))
    maximum_omega_difference = max(compare_tolerant(
        omega, 2*math.pi*f, relative, absolute, f'omega[{i}]')
        for i, (omega, f) in enumerate(zip(numeric['omega'], numeric['f'])))
    maximum_modulus_difference = max(compare_tolerant(
        magnitude, math.hypot(z.real, z.imag), relative, absolute, f'modulus[{i}]')
        for i, (magnitude, z) in enumerate(zip(numeric['z_modulus'], observed)))
    phases = [math.atan2(z.imag, z.real) for z in observed]
    phase_matches = []
    for unit, factor in [('radians', 1.), ('degrees', 180/math.pi)]:
        differences = [abs(value-factor*phase) for value, phase in zip(numeric['z_phase'], phases)]
        if all(error <= absolute+relative*abs(factor*phase)
               for error, phase in zip(differences, phases)):
            phase_matches.append((unit, max(differences)))
    if len(phase_matches) != 1:
        raise AssertionError('Phase units are ambiguous or inconsistent')
    phase_unit, maximum_phase_difference = phase_matches[0]
    rows = released['observations']
    if len(rows) != count or sorted(row['row'] for row in rows) != list(range(count)):
        raise AssertionError('Released row inventory differs')
    for row in rows:
        for key, source_key in [('frequency_hz', 'f'), ('real_ohm', 'z_real'), ('imag_ohm', 'z_imag')]:
            if row[key] != numeric[source_key][row['row']]:
                raise AssertionError(f'Released observation differs: row {row["row"]}, {key}')
    if released['encoding']['phase_units'] != phase_unit:
        raise AssertionError('Released phase-unit report differs')
    compare_tolerant(released['encoding']['maximum_complex_string_difference_ohm'],
                     maximum_string_difference, 1e-12, 1e-12, 'released encoding discrepancy')
    result = {
        'passed': True,
        'scope': 'independent source decoding after response release; no parameter fitting',
        'design_commit': released['design_commit'],
        'forecast_commit': released['forecast_commit'],
        'result_sha256': hashlib.sha256(released_bytes).hexdigest(),
        'source_files_verified': len(receipt['files']),
        'checksums': ['SHA-256', 'MD5'],
        'json_parser': 'Decimal numbers and explicit complex-string regular expression',
        'matlab_parser': 'scipy.io.loadmat; opaque object retained but ordinary numeric arrays decoded',
        'numeric_json_matlab_comparisons': comparisons,
        'numeric_json_matlab_values_exact': count*len(NUMERIC_FIELDS),
        'matlab_complex_values_exact': count,
        'released_observation_values_exact': count*3,
        'complex_strings_checked': count,
        'maximum_complex_string_difference_ohm': maximum_string_difference,
        'maximum_omega_identity_difference_rad_s': maximum_omega_difference,
        'maximum_modulus_identity_difference_ohm': maximum_modulus_difference,
        'phase_units': phase_unit,
        'maximum_phase_identity_difference': maximum_phase_difference,
        'source_encoding_relative_tolerance': relative,
        'source_encoding_absolute_tolerance': absolute,
        'phase_or_impedance_sign_changed': False,
        'production_analysis_imported': False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False)+'\n')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
