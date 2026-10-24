"""Frozen component forecast and collocated RC boundary comparison.

The inventory and forecast stages never numerically decode response fields.
See docs/rlc-boundary-protocol-2026-10-24.md for exposure and scope.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import subprocess

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
CONFIG = 'configs/rlc_boundary_2026-10-24.json'
PROTOCOL = 'docs/rlc-boundary-protocol-2026-10-24.md'
FROZEN = [CONFIG, PROTOCOL, 'experiments/run_rlc_boundary.py',
          'experiments/verify_rlc_boundary.py', 'tests/test_rlc_boundary.py',
          'data/physics-candidates/2026-10-24/rlc/acquisition.json']


def dump(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n')


def verify_sources(cfg):
    directory = ROOT / cfg['source']
    receipt = json.loads((directory / 'acquisition.json').read_text())
    for entry in receipt['files']:
        path = directory / entry['file']
        if path.parent != directory:
            raise ValueError('Invalid source path')
        raw = path.read_bytes()
        if len(raw) != entry['bytes'] or hashlib.sha256(raw).hexdigest() != entry['sha256']:
            raise ValueError('Changed original: '+str(path))
    return directory


def lexical_source(cfg):
    directory = verify_sources(cfg)
    # Numeric tokens remain strings, including frequencies until explicitly selected.
    return json.loads((directory / 'rlc_circuit.json').read_text(),
                      parse_float=str, parse_int=str)


def schema(value):
    # Never emit string content: the source also stores complex responses as strings.
    if isinstance(value, dict):
        return {key: schema(item) for key, item in value.items()}
    if isinstance(value, list):
        return dict(length=len(value), item_types=sorted({type(x).__name__ for x in value}))
    return type(value).__name__


def freeze(commit, paths):
    full = subprocess.check_output(['git', 'rev-parse', '--verify', commit+'^{commit}'], cwd=ROOT, text=True).strip()
    subprocess.run(['git', 'merge-base', '--is-ancestor', full, 'origin/main'], cwd=ROOT, check=True)
    for name in paths:
        old = subprocess.check_output(['git', 'show', f'{full}:{name}'], cwd=ROOT)
        if old != (ROOT / name).read_bytes():
            raise ValueError('Changed frozen file: '+name)
    return full


def frequencies(doc, cfg):
    values = np.array([float(x) for x in doc['f']])
    if (values.shape != (cfg['expected_rows'],) or not np.all(np.isfinite(values))
            or np.any(values <= 0) or len(np.unique(values)) != len(values)):
        raise ValueError('Invalid frequency design')
    if not np.allclose([values.min(), values.max()], cfg['frequency_range_hz'],
                       rtol=cfg['frequency_relative_tolerance'], atol=0):
        raise ValueError('Frequency span differs from source description')
    return values


def impedance(frequency, resistance, inductance, capacitance):
    omega = 2*np.pi*np.asarray(frequency)
    return (resistance+1j*omega*inductance)/(1-omega**2*inductance*capacitance+1j*omega*capacitance*resistance)


def crossing(resistance, inductance, capacitance):
    square = 1/(inductance*capacitance)-(resistance/inductance)**2
    if square <= 0:
        raise ValueError('No positive sign crossover')
    return float(np.sqrt(square)/(2*np.pi))


def intervals(cfg):
    ls = [cfg['inductance_henry']*(1+sign*cfg['inductance_fractional_tolerance']) for sign in (-1, 1)]
    cs = [cfg['capacitance_farad']*(1+sign*cfg['capacitance_fractional_tolerance']) for sign in (-1, 1)]
    r = cfg['resistance_ohm']
    if ls[0] <= 2*r*r*cs[1]:
        raise ValueError('Corner-extrema monotonicity not established')
    primary = [crossing(r, l, c) for l, c in itertools.product(ls, cs)]
    alternate = [crossing(cfg['alternative_resistance_ohm'], l, c) for l, c in itertools.product(ls, cs)]
    return [min(primary), max(primary)], [min(primary+alternate), max(primary+alternate)]


def signs(frequency, interval):
    return np.where(frequency < interval[0], 1, np.where(frequency > interval[1], -1, 0))


def forecast(cfg, design_commit):
    design_commit = freeze(design_commit, FROZEN)
    f = frequencies(lexical_source(cfg), cfg)
    z = impedance(f, cfg['resistance_ohm'], cfg['inductance_henry'], cfg['capacitance_farad'])
    primary, union = intervals(cfg)
    a, b = signs(f, primary), signs(f, union)
    return dict(design_commit=design_commit, config=cfg,
        crossing_hz_nominal=crossing(cfg['resistance_ohm'], cfg['inductance_henry'], cfg['capacitance_farad']),
        crossing_hz_interval=primary, crossing_hz_unit_union=union,
        rows=[dict(row=i, frequency_hz=float(x), real_ohm=float(y.real), imag_ohm=float(y.imag),
                   sign_table_s3=int(a[i]), sign_unit_union=int(b[i])) for i, (x, y) in enumerate(zip(f, z))])


def quadrature(f):
    # Caller sorts first. Trapezoid integration normalized by total log span.
    if len(f) < 2 or np.any(np.diff(f) <= 0):
        raise ValueError('Quadrature requires sorted distinct frequencies')
    steps = np.diff(np.log(f))
    weights = np.zeros(len(f))
    weights[:-1] += steps/2
    weights[1:] += steps/2
    return weights/weights.sum()


def crossing_report(f, observed, interval):
    s = np.sign(observed.imag)
    brackets = [dict(low_hz=float(f[i]), high_hz=float(f[i+1]),
                     from_sign=int(s[i]), to_sign=int(s[i+1]))
                for i in range(len(f)-1) if s[i]*s[i+1] < 0]
    zeros = f[s == 0].tolist()
    compatible = (not zeros and len(brackets) == 1 and brackets[0]['from_sign'] == 1
                  and brackets[0]['to_sign'] == -1 and brackets[0]['low_hz'] <= interval[1]
                  and brackets[0]['high_hz'] >= interval[0])
    return dict(brackets=brackets, exact_zero_hz=zeros,
                single_crossing_bracket_intersects_interval=bool(compatible))


def score(rows, obs, cfg):
    ordered = sorted(rows, key=lambda x: x['frequency_hz'])
    ids = np.array([x['row'] for x in ordered])
    f = np.array([x['frequency_hz'] for x in ordered])
    z = obs[ids]
    prediction = np.array([complex(x['real_ohm'], x['imag_ohm']) for x in ordered])
    w = quadrature(f)
    denominator = float(np.sum(w*np.abs(z)**2))
    if denominator <= 0:
        raise ValueError('Zero observed impedance norm')
    rms = lambda a: float(np.sqrt(np.sum(w*np.abs(a)**2)/denominator))
    alternative = impedance(f, cfg['alternative_resistance_ohm'], cfg['inductance_henry'], cfg['capacitance_farad'])
    nominal_error = rms(prediction-z)
    rc_bound = rms(np.maximum(z.imag, 0))
    reports = {}
    for key, interval in zip(('table_s3', 'unit_union'), intervals(cfg)):
        predicted = np.array([x['sign_'+key] for x in ordered])
        eligible = predicted != 0
        wrong = eligible & (predicted != np.sign(z.imag))
        reports[key] = dict(classified=int(eligible.sum()), unclassified=int((~eligible).sum()),
                            agreements=int((eligible & ~wrong).sum()), disagreement_rows=ids[wrong].tolist(),
                            all_classified_signs_agree=bool(not wrong.any()),
                            **crossing_report(f, z, interval))
    positive = z.imag > 0
    return dict(count=len(ids), row_indices=ids.tolist(),
        rlc_relative_rms=nominal_error, rc_relative_rms_lower_bound=rc_bound,
        alternative_resistance_relative_rms=rms(alternative-z),
        rlc_error_below_rc_lower_bound=bool(nominal_error < rc_bound),
        positive_imaginary_count=int(positive.sum()), positive_imaginary_fraction=float(positive.mean()),
        positive_imaginary_range_ohm=([float(z.imag[positive].min()), float(z.imag[positive].max())] if positive.any() else None),
        signs=reports)


def decode(doc, f, cfg):
    fields = ['omega', 'z_real', 'z_imag', 'z_modulus', 'z_phase']
    arrays = {key: np.array([float(x) for x in doc[key]]) for key in fields}
    if any(x.shape != f.shape or not np.all(np.isfinite(x)) for x in arrays.values()):
        raise ValueError('Invalid response fields')
    z = arrays['z_real']+1j*arrays['z_imag']
    string_z = np.array([complex(x.replace('i', 'j')) for x in doc['z']])
    kwargs = dict(rtol=cfg['source_encoding_relative_tolerance'], atol=cfg['source_encoding_absolute_tolerance'])
    for left, right in [(arrays['omega'], 2*np.pi*f), (string_z, z), (arrays['z_modulus'], np.abs(z))]:
        if left.shape != right.shape or not np.allclose(left, right, **kwargs):
            raise ValueError('Inconsistent source encoding')
    units = [name for name, target in [('radians', np.angle(z)), ('degrees', np.angle(z, deg=True))]
             if np.allclose(arrays['z_phase'], target, **kwargs)]
    if len(units) != 1:
        raise ValueError('Ambiguous or inconsistent source phase convention')
    return z, dict(phase_units=units[0], numeric_rows=len(z),
                   maximum_complex_string_difference_ohm=float(np.max(np.abs(string_z-z))))


def evaluate(cfg, prediction_path, prediction_commit):
    relative = Path(prediction_path).resolve().relative_to(ROOT).as_posix()
    seal = freeze(prediction_commit, [relative])
    raw = Path(prediction_path).read_bytes()
    prediction = json.loads(raw)
    freeze(prediction['design_commit'], FROZEN)
    if cfg != prediction['config']:
        raise ValueError('Changed config')
    doc = lexical_source(cfg)
    f = frequencies(doc, cfg)
    if [x['frequency_hz'] for x in prediction['rows']] != f.tolist():
        raise ValueError('Frequency inputs changed')
    z, encoding = decode(doc, f, cfg)
    primary_rows = [row for row in prediction['rows'] if row['row'] not in cfg['previously_exposed_zero_based_rows']]
    return dict(forecast_commit=seal, forecast_sha256=hashlib.sha256(raw).hexdigest(),
        design_commit=prediction['design_commit'], encoding=encoding,
        observations=[dict(row=i, frequency_hz=float(x), real_ohm=float(y.real), imag_ohm=float(y.imag))
                      for i, (x, y) in enumerate(zip(f, z))],
        primary=score(primary_rows, z, cfg), all_rows=score(prediction['rows'], z, cfg),
        interpretation='One actual driven circuit; conditional independent-component forecast and descriptive passive-RC boundary test, not a noise-qualified statistical rejection or unique law confirmation')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=['inventory', 'forecast', 'evaluate'], required=True)
    parser.add_argument('--design-commit')
    parser.add_argument('--prediction', type=Path)
    parser.add_argument('--prediction-commit')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    cfg = json.loads((ROOT / CONFIG).read_text())
    if args.stage == 'inventory':
        result = dict(schema=schema(lexical_source(cfg)), numerical_responses_decoded=False)
    elif args.stage == 'forecast':
        if not args.design_commit:
            parser.error('forecast requires --design-commit')
        result = forecast(cfg, args.design_commit)
    else:
        if not args.prediction or not args.prediction_commit:
            parser.error('evaluate requires --prediction and --prediction-commit')
        result = evaluate(cfg, args.prediction, args.prediction_commit)
    dump(args.output, result)
    print(json.dumps(dict(stage=args.stage, output=str(args.output))))


if __name__ == '__main__':
    main()
