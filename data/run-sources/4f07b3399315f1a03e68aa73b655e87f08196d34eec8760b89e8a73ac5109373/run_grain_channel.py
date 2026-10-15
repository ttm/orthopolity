"""Seal narrow-calibrated forecasts, then evaluate wider-channel sediment flux."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np

from audit_grain_channel import ROOT, BASE, encode, verify_sources, audit
from orthopolity.grain_channel import table, stress, fit_transport, transport, weights, MODELS

DESIGN_FILES = ['src/orthopolity/grain_channel.py', 'experiments/run_grain_channel.py',
    'experiments/audit_grain_channel.py', 'experiments/verify_grain_channel.py',
    'configs/grain_channel_2026-10-15.json',
    'docs/grain-channel-protocol-2026-10-15.md', 'tests/test_grain_channel.py',
    'data/grain-channel/2026-10-15/acquisition.json',
    'data/grain-channel/2026-10-15/predictor-audit.json']


def frozen_commit(ref, files):
    full = subprocess.check_output(['git','rev-parse',ref], cwd=ROOT, text=True).strip()
    for name in files:
        if subprocess.check_output(['git','show',f'{full}:{name}'], cwd=ROOT) != (ROOT/name).read_bytes():
            raise ValueError('Changed frozen input: '+name)
    return full


def read_responses(rows, cohort):
    """Convert ONLY the selected cohort's measured mass_flux column."""
    if any(r['cohort'] != cohort for r in rows):
        raise ValueError('Wrong response cohort')
    cache, values = {}, []
    for r in rows:
        name = r['raw_file']
        if name not in cache:
            cache[name] = table(BASE/'02_data/source_data'/name)
        source = cache[name][r['raw_row']-2]
        identity = source['names' if cohort == 'narrow' else 'name']
        if identity != r['id']:
            raise ValueError('Response identity mismatch')
        mass = float(source['mass_flux'])
        if not np.isfinite(mass) or mass < 0:
            raise ValueError('Missing/invalid response; no cohort substitution')
        values.append(dict(id=r['id'], mass_flux=mass,
                           dimensionless_flux=mass/r['mass_per_dimensionless_flux']))
    return values


def predict(design):
    verify_sources()
    data = audit()
    if encode(data) != (BASE/'predictor-audit.json').read_bytes():
        raise ValueError('Changed predictor audit')
    rows = data['rows']
    if not all(r['qualified_hydraulics'] for r in rows):
        raise ValueError('Hydraulically unqualified cohort')
    old = [r for r in rows if r['cohort'] == 'narrow']
    new = [r for r in rows if r['cohort'] == 'wide']
    responses = read_responses(old, 'narrow')
    response_map = {r['id']: r['dimensionless_flux'] for r in responses}
    results = {}
    for name, cal in [('sphere', [r for r in old if r['grain'] == 'sphere']), ('pooled', old)]:
        y = np.array([response_map[r['id']] for r in cal])
        ww = weights(cal)
        fits = {}
        for model in MODELS:
            x = [stress(r, model) for r in cal]
            fit = fit_transport(x, y, ww)
            xp = [stress(r, model) for r in new]
            forecasts = transport(xp, fit['amplitude'], fit['threshold'])
            fit.update(calibration_ids=[r['id'] for r in cal], calibration_stress=x,
                       calibration_flux=y.tolist(), weights=ww.tolist(),
                       calibration_rmse=float(np.sqrt(fit['mse'])),
                       forecasts=[dict(id=r['id'], grain=r['grain'], stress=xx,
                            dimensionless_flux=float(v), mass_flux=float(v*r['mass_per_dimensionless_flux']),
                            extrapolates=bool(xx<min(x) or xx>max(x))) for r,xx,v in zip(new,xp,forecasts)])
            fits[model] = fit
        results[name] = fits
    # Material-label rival: separate narrow fits with Guo and no measured shape.
    label = {}
    for grain in ('sphere', 'gravel'):
        cal = [r for r in old if r['grain'] == grain]
        y = [response_map[r['id']] for r in cal]
        x = [stress(r, 'guo_unity') for r in cal]
        fit = fit_transport(x, y, weights(cal))
        fit.update(calibration_ids=[r['id'] for r in cal], calibration_stress=x,
                   calibration_flux=y, weights=weights(cal).tolist())
        label[grain] = fit
    label_forecasts = []
    for r in new:
        fit = label[r['grain']]
        xx = stress(r, 'guo_unity')
        v = float(transport(xx, fit['amplitude'], fit['threshold']))
        label_forecasts.append(dict(id=r['id'], grain=r['grain'], stress=xx,
            dimensionless_flux=v, mass_flux=v*r['mass_per_dimensionless_flux'],
            extrapolates=bool(xx<min(fit['calibration_stress']) or xx>max(fit['calibration_stress']))))
    primary_ids = results['sphere']['guo_shape']['calibration_ids']
    return dict(study='grain-channel-2026-10-15', design_commit=design,
        config=json.loads((ROOT/'configs/grain_channel_2026-10-15.json').read_text()),
        predictor_audit=data, calibration_responses=responses, fits=results,
        material_label=dict(fits=label, forecasts=label_forecasts),
        normalization=max(response_map[k] for k in primary_ids),
        wide_numerical_responses_converted_by_prediction=False)


def score(forecasts, observations, normalization):
    by_id = {r['id']: r for r in observations}
    entries = []
    for f in forecasts:
        o = by_id[f['id']]
        err = f['dimensionless_flux']-o['dimensionless_flux']
        entries.append(dict(**f, observed_flux=o['dimensionless_flux'], observed_mass_flux=o['mass_flux'],
                            error=err, mass_error=f['mass_flux']-o['mass_flux']))
    groups = {}
    for grain in ('sphere', 'gravel'):
        group = [r for r in entries if r['grain'] == grain]
        mae = float(np.mean([abs(r['error']) for r in group]))
        groups[grain] = dict(n=len(group), mae=mae, normalized_mae=mae/normalization,
            bias=float(np.mean([r['error'] for r in group])),
            mass_mae=float(np.mean([abs(r['mass_error']) for r in group])))
    return dict(rows=entries, groups=groups,
                balanced_mae=float(np.mean([x['mae'] for x in groups.values()])))


def evaluate(predictions, prediction_commit):
    verify_sources()
    new = [r for r in predictions['predictor_audit']['rows'] if r['cohort'] == 'wide']
    observations = read_responses(new, 'wide')
    norm = predictions['normalization']
    scores = {family: {m: score(fit['forecasts'], observations, norm) for m,fit in fits.items()}
              for family,fits in predictions['fits'].items()}
    scores['material_label'] = score(predictions['material_label']['forecasts'], observations, norm)
    primary = scores['sphere']
    full = primary['guo_shape']
    gains = {m: 1-full['balanced_mae']/primary[m]['balanced_mae']
             if primary[m]['balanced_mae'] else None for m in MODELS if m != 'guo_shape'}
    cfg = predictions['config']
    fit = predictions['fits']['sphere']['guo_shape']
    calibration_adequate = fit['active_calibration_count'] >= 3 and fit['calibration_rmse']/norm <= cfg['maximum_normalized_mae']
    accuracy = calibration_adequate and all(x['normalized_mae'] <= cfg['maximum_normalized_mae'] for x in full['groups'].values())
    return dict(study=predictions['study'], design_commit=predictions['design_commit'],
        prediction_commit=prediction_commit, normalization=norm, observations=observations,
        scores=scores, primary_relative_gains=gains, decision=dict(
            calibration_adequate=calibration_adequate,
            pragmatic_accuracy=accuracy,
            shape_advantage=accuracy and gains['guo_unity'] is not None and gains['guo_unity']>=cfg['minimum_relative_gain'],
            geometry_advantage=accuracy and gains['radius_shape'] is not None and gains['radius_shape']>=cfg['minimum_relative_gain']),
        uncertainty='Descriptive finite-cohort errors; no population confidence interval or independent-replicate claim.',
        reference_measure=cfg['reference_measure'])


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--stage', choices=['predict','evaluate'], required=True)
    p.add_argument('--freeze-commit', required=True)
    p.add_argument('--prediction-commit')
    p.add_argument('--predictions', type=Path)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    design = frozen_commit(args.freeze_commit, DESIGN_FILES)
    if args.output.exists():
        raise ValueError('Use a fresh output directory')
    if args.stage == 'predict':
        result, name = predict(design), 'predictions.json'
    else:
        if args.predictions is None or args.prediction_commit is None:
            raise ValueError('Sealed predictions required')
        path = args.predictions.resolve().relative_to(ROOT)
        pred_commit = frozen_commit(args.prediction_commit, [str(path)])
        predictions = json.loads(args.predictions.read_text())
        if predictions['design_commit'] != design:
            raise ValueError('Prediction/design mismatch')
        result, name = evaluate(predictions, pred_commit), 'result.json'
        result['prediction_sha256'] = hashlib.sha256(args.predictions.read_bytes()).hexdigest()
    args.output.mkdir(parents=True)
    (args.output/name).write_bytes(encode(result))
    print(json.dumps(dict(output=str(args.output/name), stage=args.stage,
                          design_commit=design, decision=result.get('decision'))))
