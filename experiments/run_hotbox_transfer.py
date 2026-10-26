"""Locally frozen low-forcing to high-forcing temperature-profile transfer.

Forecast decodes case 6/7 c..g and case 1..5 c/g only. Evaluation releases
case 1..5 d/e/f only after a separate forecast commit. Dynamic files stay shut.
"""
import argparse
import csv
import hashlib
import io
import itertools
import json
from pathlib import Path
import subprocess
import zipfile

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
CONFIG = 'configs/hotbox_transfer_2026-10-26.json'
PROTOCOL = 'docs/hotbox-transfer-protocol-2026-10-26.md'
FROZEN = [CONFIG, PROTOCOL, 'experiments/run_hotbox_transfer.py',
          'experiments/verify_hotbox_transfer.py', 'tests/test_hotbox_transfer.py']


def dump(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n')


def freeze(commit, paths):
    full = subprocess.check_output(['git', 'rev-parse', '--verify', commit+'^{commit}'],
                                   cwd=ROOT, text=True).strip()
    subprocess.run(['git', 'merge-base', '--is-ancestor', full, 'origin/main'],
                   cwd=ROOT, check=True)
    for name in paths:
        old = subprocess.check_output(['git', 'show', f'{full}:{name}'], cwd=ROOT)
        if old != (ROOT/name).read_bytes():
            raise ValueError('Changed frozen file: '+name)
    return full


def selected_table(raw, columns, cfg):
    """Numeric conversion is restricted to explicit columns plus the clock."""
    rows = csv.reader(io.StringIO(raw.decode()), delimiter='\t')
    header = next(rows)
    if len(header) != cfg['expected_columns'] or len(set(header)) != len(header):
        raise ValueError('Unexpected or duplicate columns')
    selected = ['Time']+list(columns)
    indices = [header.index(key) for key in selected]
    data = []
    for row in rows:
        if len(row) != len(header):
            raise ValueError('Wrong row width')
        data.append([float(row[i]) for i in indices])
    a = np.asarray(data)
    if a.shape != (cfg['expected_rows'], len(selected)) or not np.all(np.isfinite(a)):
        raise ValueError('Unexpected shape or nonfinite selected readings')
    if not np.allclose(np.diff(a[:, 0]), cfg['time_step_seconds'], rtol=0, atol=1e-7):
        raise ValueError('Clock differs from frozen 60-second spacing')
    return {key: a[:, i] for i, key in enumerate(selected)}


def load_stage(cfg, stage):
    raw = (ROOT/cfg['source']).read_bytes()
    if hashlib.sha256(raw).hexdigest() != cfg['source_sha256']:
        raise ValueError('Changed original archive')
    result = {}
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        cases = range(1, 8) if stage == 'forecast' else cfg['target_cases']
        for case in cases:
            if stage == 'forecast':
                sensors = list('cdefg') if case in (6, 7) else cfg['anchors']
            else:
                sensors = cfg['interior']
            columns = [f'{p}_{s}' for p in cfg['positions'] for s in sensors]
            delta = cfg['case_differences_c'][case-1]
            name = f'dataset/steady-state/SS_case_{case}_Temp_diff_{delta}.txt'
            result[case] = selected_table(archive.read(name), columns, cfg)
    return result


def summarize(tables, cfg):
    result = []
    n = cfg['drift_window_rows']
    for case, table in tables.items():
        for key, values in table.items():
            if key == 'Time':
                continue
            position, sensor = key.split('_')
            result.append(dict(case=case, position=int(position), sensor=sensor,
                               mean_c=float(values.mean()), min_c=float(values.min()),
                               max_c=float(values.max()),
                               drift_c=float(values[-n:].mean()-values[:n].mean())))
    return result


def index(rows):
    return {(r['case'], r['position'], r['sensor']): r for r in rows}


def qualified(row, cfg):
    low, high = cfg['internal_calibration_range_c']
    e = cfg['sensor_error_c']
    return (row['min_c']-e >= low and row['max_c']+e <= high
            and abs(row['drift_c']) <= cfg['maximum_window_drift_c'])


def descending_feasible(means, error):
    """Existence of a single ordered latent temperature vector in the boxes."""
    previous = float('inf')
    for x in means:
        previous = min(previous, x+error)
        if previous < x-error:
            return False
    return True


def beta_interval(c, g, target, error):
    if c-g <= 2*error:
        return None
    corners = [(m-b)/(a-b) for a, b, m in itertools.product(
        [c-error, c+error], [g-error, g+error], [target-error, target+error])]
    low, high = max(0., min(corners)), min(1., max(corners))
    return [low, high] if low <= high else None


def observation_interval(c, g, beta, error):
    if beta is None:
        return None
    values = [b*a+(1-b)*z for b, a, z in itertools.product(
        beta, [c-error, c+error], [g-error, g+error])]
    # Include error of the independently observed target mean, with no sqrt(n).
    return [min(values)-error, max(values)+error]


def predict(summary, cfg):
    rows = index(summary)
    e = cfg['sensor_error_c']
    predictions = []
    for case, p in itertools.product(cfg['target_cases'], cfg['positions']):
        cal = [rows[(6, p, s)] for s in 'cdefg']
        c0, g0 = cal[0]['mean_c'], cal[-1]['mean_c']
        if c0-g0 <= 2*e:
            raise ValueError('Calibration anchors are not separated by the error bound')
        monotone = descending_feasible([r['mean_c'] for r in cal], e)
        c, g = [rows[(case, p, s)] for s in 'cg']
        input_ok = monotone and all(qualified(r, cfg) for r in cal+[c, g])
        for s in cfg['interior']:
            y0 = rows[(6, p, s)]['mean_c']
            beta = (y0-g0)/(c0-g0)
            interval = beta_interval(c0, g0, y0, e) if monotone else None
            geo = ((cfg['depth_m']['g']-cfg['depth_m'][s]) /
                   (cfg['depth_m']['g']-cfg['depth_m']['c']))
            geo_y = geo*c['mean_c']+(1-geo)*g['mean_c']
            predictions.append(dict(case=case, position=p, sensor=s,
                calibration_beta=beta, calibration_beta_interval=interval,
                calibration_monotone=monotone, geometry_beta=geo,
                geometry_prediction_c=geo_y,
                transfer_prediction_c=beta*c['mean_c']+(1-beta)*g['mean_c'],
                additive_prediction_c=geo_y+y0-(geo*c0+(1-geo)*g0),
                persistence_prediction_c=y0,
                transfer_observation_interval_c=observation_interval(
                    c['mean_c'], g['mean_c'], interval, e),
                geometry_observation_interval_c=[geo_y-2*e, geo_y+2*e],
                input_qualified=input_ok))
    return predictions


def forecast(cfg, commit):
    frozen = freeze(commit, FROZEN)
    tables = load_stage(cfg, 'forecast')
    summary = summarize(tables, cfg)
    return dict(design_commit=frozen, config=cfg, input_summary=summary,
                predictions=predict(summary, cfg),
                numeric_temperature_cells=sum(len(v) for t in tables.values()
                                              for k, v in t.items() if k != 'Time'),
                target_interior_temperatures_decoded=False)


def evaluate(prediction, target_summary):
    cfg = prediction['config']
    targets, inputs = index(target_summary), index(prediction['input_summary'])
    records = []
    for pred in prediction['predictions']:
        case, p, s = pred['case'], pred['position'], pred['sensor']
        obs = targets[(case, p, s)]
        profile_ok = all(qualified(targets[(case, p, j)], cfg) for j in cfg['interior'])
        interval = pred['transfer_observation_interval_c']
        residuals = {model: obs['mean_c']-pred[model+'_prediction_c']
                     for model in ('geometry', 'transfer', 'additive', 'persistence')}
        gap = abs(inputs[(case, p, 'c')]['mean_c']-inputs[(case, p, 'g')]['mean_c'])
        span = cfg['depth_m']['g']-cfg['depth_m']['c']
        extra = max(0., abs(residuals['geometry'])-2*cfg['sensor_error_c'])
        geometry_required_m = extra*span/(2*gap) if gap else None
        records.append(dict(case=case, position=p, sensor=s, observed=obs,
            residual_c=residuals, qualified=pred['input_qualified'] and profile_ok,
            transfer_outside_envelope=(obs['mean_c'] < interval[0] or
                                       obs['mean_c'] > interval[1]) if interval else None,
            geometry_outside_envelope=abs(residuals['geometry']) > 2*cfg['sensor_error_c'],
            required_equal_position_allowance_m=geometry_required_m,
            geometry_sensitivity_outside={str(delta): abs(residuals['geometry']) >
                2*cfg['sensor_error_c']+2*delta*gap/span for delta in cfg['geometry_sensitivity_m']}))
    groups = {}
    for name, subset in [('all', records)]+[(f'case_{c}', [r for r in records if r['case']==c])
                                         for c in cfg['target_cases']]:
        q = [r for r in subset if r['qualified']]
        groups[name] = dict(target_means=len(subset), qualified_target_means=len(q),
            mae_c={m: float(np.mean([abs(r['residual_c'][m]) for r in subset]))
                   for m in ('geometry', 'transfer', 'additive', 'persistence')},
            maximum_absolute_error_c={m: max(abs(r['residual_c'][m]) for r in subset)
                                      for m in ('geometry', 'transfer', 'additive', 'persistence')},
            transfer_outside_all=sum(r['transfer_outside_envelope'] is True for r in subset),
            transfer_envelopes_available=sum(r['transfer_outside_envelope'] is not None for r in subset),
            transfer_outside_qualified=sum(r['transfer_outside_envelope'] is True for r in q),
            geometry_outside_all=sum(r['geometry_outside_envelope'] for r in subset))
    all_qualified = all(r['qualified'] for r in records)
    verdict = ('not_excluded_by_marginal_bounds' if groups['all']['transfer_outside_all']==0
               else 'conditional_transfer_departure') if all_qualified else 'qualification_incomplete'
    return dict(verdict=verdict, groups=groups, records=records,
        scope='Conditional thermal-resistance profile transfer; no unique convection or general-law identification',
        no_target_refitting=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage', choices=['forecast', 'evaluate'], required=True)
    parser.add_argument('--design-commit', required=True)
    parser.add_argument('--prediction')
    parser.add_argument('--prediction-commit')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    cfg = json.loads((ROOT/CONFIG).read_text())
    if args.stage == 'forecast':
        result = forecast(cfg, args.design_commit)
    else:
        design = freeze(args.design_commit, FROZEN)
        if not args.prediction or not args.prediction_commit:
            raise ValueError('A separately committed forecast is required')
        path = Path(args.prediction).resolve()
        rel = str(path.relative_to(ROOT))
        pred_commit = freeze(args.prediction_commit, [rel])
        prediction = json.loads(path.read_text())
        if prediction['config'] != cfg or prediction['design_commit'] != design:
            raise ValueError('Forecast does not match frozen inputs')
        summary = summarize(load_stage(cfg, 'evaluate'), cfg)
        result = evaluate(prediction, summary)
        result.update(design_commit=design, prediction_commit=pred_commit,
                      prediction_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    dump(args.output, result)
    print(json.dumps({k: result[k] for k in ('verdict', 'design_commit', 'numeric_temperature_cells') if k in result}))


if __name__ == '__main__':
    main()
