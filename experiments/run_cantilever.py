"""Freeze thermal-noise forecasts from damping before evaluating fluctuations."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

import numpy as np
from scipy.io import loadmat

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from orthopolity.cantilever import mode_moments, fit_loss, predict_loss, predict_temperature
from fetch_cantilever import verify, encode

BASE = ROOT / 'data/cantilever/2026-10-13'
CONFIG = 'configs/cantilever_2026-10-13.json'
FROZEN = [CONFIG, 'docs/cantilever-protocol-2026-10-13.md',
          'src/orthopolity/cantilever.py', 'tests/test_cantilever.py',
          'experiments/run_cantilever.py', 'experiments/fetch_cantilever.py',
          'tests/test_cantilever_runner.py',
          'data/cantilever/2026-10-13/predictor-audit.json']


def nullable(x):
    return float(x) if math.isfinite(float(x)) else None


def algebraic_temperature(delta, coefficients, moments, t0):
    try:
        return nullable(predict_temperature(delta, coefficients, moments, t0=t0))
    except ValueError:
        return None  # Undefined predictions remain visible as failed cases.


def predictor_audit(archive):
    result = {}
    for sample, ntrain in [('C30', 8), ('C30C', 5)]:
        data = archive[sample]
        temp = np.asarray(data['AVG_TAVG'])
        if not np.all(np.isfinite(temp)) or np.any(temp < 300):
            raise ValueError('Unqualified temperature predictors')
        order = np.argsort(temp, kind='stable')
        if temp[order[ntrain - 1]] == temp[order[ntrain]]:
            raise ValueError('Temperature tie across split; protocol amendment required')
        result[sample] = dict(n_conditions=len(temp),
            train_rows=(order[:ntrain] + 1).tolist(), target_rows=(order[ntrain:] + 1).tolist(),
            tavg_K=temp.tolist(), tavg_error_K=data['AVG_TAVG_ERR'].tolist(),
            archived_tmax_K=data['AVG_TMAX'].tolist(),
            implied_base_K=(2*temp-data['AVG_TMAX']).tolist())
    return result


def forecast(archive, config):
    audit = predictor_audit(archive)
    analyses = []
    for setting in config['analyses']:
        cases = []
        t0 = setting['t0_K']
        for sample, modes in config['modes'].items():
            data = archive[sample]
            temp = np.asarray(data['AVG_TAVG'])
            delta = 2*(temp-t0)
            for kind, indices in modes.items():
                prefix = 'D' if kind == 'flexural' else 'T'
                for index in indices:
                    mu = mode_moments(kind, index, order=config['quadrature_order'])
                    train = (list(range(1, len(temp)+1)) if setting['all_phi']
                             else audit[sample]['train_rows'])
                    targets = audit[sample]['target_rows']
                    masked = ([1] if setting['publisher_mask'] and sample == 'C30C'
                              and kind == 'flexural' and index == 4 else [])
                    train = [r for r in train if r not in masked]
                    # Select calibration entries before any numerical reduction.
                    phi = np.asarray(data[f'AVG_{prefix}_PHI']).reshape(len(temp), -1)[np.array(train)-1, index-1]
                    sigma = np.asarray(data[f'AVG_{prefix}_PHI_ERR']).reshape(len(temp), -1)[np.array(train)-1, index-1]
                    finite = np.isfinite(phi) & np.isfinite(sigma)
                    used = [r for r, good in zip(train, finite) if good]
                    missing = [r for r, good in zip(train, finite) if not good]
                    fit = fit_loss(delta[np.array(used, dtype=int)-1], phi[finite], sigma[finite],
                                   mu, domain_max=float(max(delta)))
                    rows = []
                    for row in targets:
                        j = row-1
                        coefs = fit.get('coefficients')
                        rows.append(dict(row=row, tavg_K=float(temp[j]),
                            tavg_error_K=nullable(data['AVG_TAVG_ERR'][j]),
                            delta_K=float(delta[j]), tmax_model_K=float(t0+delta[j]),
                            phi_prediction=nullable(predict_loss(delta[j], coefs)) if coefs is not None else None,
                            temperature_prediction_K=algebraic_temperature(delta[j], coefs, mu, t0) if coefs is not None else None,
                            comparators_K=dict(spatial_average=float(temp[j]), cold_clamp=float(t0),
                                               uniform_local_loss=float(t0+delta[j]*mu[1]))))
                    if fit['admissible'] and any(
                            r['temperature_prediction_K'] is None or
                            not t0-1e-7 <= r['temperature_prediction_K'] <= r['tmax_model_K']+1e-7
                            for r in rows):
                        fit['admissible'] = False
                        fit['status'] = 'inadmissible'
                        fit['reasons'].append('target_temperature_outside_physical_envelope')
                    cases.append(dict(sample=sample, kind=kind, mode=index, moments=mu.tolist(),
                        train_rows=used, missing_train_rows=missing, masked_train_rows=masked,
                        fit=fit, rows=rows))
        analyses.append(dict(**setting, cases=cases))
    return dict(schema_version=1, run_id='cantilever-transfer-2026-10-13',
                predictor_audit=audit, analyses=analyses)


def balanced(cases, field):
    per_sample = {}
    for case in cases:
        values = [r[field] for r in case['rows'] if r.get(field) is not None]
        if values:
            per_sample.setdefault(case['sample'], []).append(float(np.mean(values)))
    sample_means = {k:float(np.mean(v)) for k,v in per_sample.items()}
    return dict(by_preparation=sample_means,
                equal_preparation_mean=float(np.mean(list(sample_means.values()))) if sample_means else None)


def evaluate(predictions, archive):
    # Deep copy makes prediction bytes immutable; no fitting takes place here.
    result = json.loads(json.dumps(predictions))
    for analysis in result['analyses']:
        for case in analysis['cases']:
            data = archive[case['sample']]
            prefix = 'D' if case['kind']=='flexural' else 'T'
            idx = case['mode']-1
            for row in case['rows']:
                j = row['row']-1
                obs = nullable(np.asarray(data[f'AVG_{prefix}_TFLUC']).reshape(len(data['AVG_TAVG']), -1)[j, idx])
                phi = nullable(np.asarray(data[f'AVG_{prefix}_PHI']).reshape(len(data['AVG_TAVG']), -1)[j, idx])
                row.update(observed_temperature_K=obs,
                    observed_temperature_error_K=nullable(np.asarray(data[f'AVG_{prefix}_TFLUC_ERR']).reshape(len(data['AVG_TAVG']), -1)[j, idx]),
                    observed_phi=phi, observed_phi_error=nullable(np.asarray(data[f'AVG_{prefix}_PHI_ERR']).reshape(len(data['AVG_TAVG']), -1)[j, idx]))
                qualified = case['fit']['admissible'] and row['temperature_prediction_K'] is not None and obs is not None
                row['qualified_temperature_target'] = qualified
                row['absolute_error_K'] = abs(row['temperature_prediction_K']-obs) if qualified else None
                pred_phi = row['phi_prediction']
                row['phi_absolute_error'] = abs(pred_phi-phi) if pred_phi is not None and phi is not None else None
                row['phi_absolute_relative_error'] = row['phi_absolute_error']/phi if row['phi_absolute_error'] is not None and phi>0 else None
                for name, value in row['comparators_K'].items():
                    row[f'{name}_absolute_error_K'] = abs(value-obs) if qualified else None
                    row[f'{name}_all_targets_error_K'] = abs(value-obs) if obs is not None else None
                    row[f'difference_vs_{name}_K'] = row['absolute_error_K']-abs(value-obs) if qualified else None
            case['temperature_mae_K'] = balanced([case], 'absolute_error_K')['equal_preparation_mean']
            case['phi_mean_absolute_relative_error'] = balanced([case], 'phi_absolute_relative_error')['equal_preparation_mean']
        cases = analysis['cases']
        fields = ['absolute_error_K','phi_absolute_relative_error']
        for name in ['spatial_average','cold_clamp','uniform_local_loss']:
            fields += [f'{name}_absolute_error_K', f'{name}_all_targets_error_K', f'difference_vs_{name}_K']
        analysis['summary'] = dict(attempted_modes=len(cases),
            admissible_modes=sum(c['fit']['admissible'] for c in cases),
            attempted_targets=sum(len(c['rows']) for c in cases),
            qualified_temperature_targets=sum(r['qualified_temperature_target'] for c in cases for r in c['rows']),
            scores={field:balanced(cases,field) for field in fields},
            interpretation='Scores on admissible modes are conditional; invalid local-loss fits remain model failures. No inferential p-values or population replication claim.')
    return result


def check_freeze(commit):
    freeze = subprocess.check_output(['git','rev-parse',commit],cwd=ROOT,text=True).strip()
    refs=[]
    for path in FROZEN:
        body=(ROOT/path).read_bytes()
        if body != subprocess.check_output(['git','show',f'{freeze}:{path}'],cwd=ROOT):
            raise ValueError(f'Unfrozen source: {path}')
        refs.append(dict(path=path,sha256=hashlib.sha256(body).hexdigest()))
    return freeze,refs


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage',choices=['audit','predict','evaluate'],required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--freeze-commit')
    parser.add_argument('--prediction-commit')
    parser.add_argument('--predictions',type=Path)
    args=parser.parse_args()
    verify()
    archive=loadmat(BASE/'data.mat',simplify_cells=True)
    config=json.loads((ROOT/CONFIG).read_text())
    audit=predictor_audit(archive)
    if args.stage=='audit':
        if args.output.exists(): raise ValueError('Refusing to replace audit')
        args.output.write_bytes(encode(audit))
        return
    if not args.freeze_commit: raise ValueError('Explicit design freeze required')
    freeze,sources=check_freeze(args.freeze_commit)
    if audit!=json.loads((BASE/'predictor-audit.json').read_text()):
        raise ValueError('Predictor audit changed')
    for item in config['inputs']:
        if hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()!=item['sha256']:
            raise ValueError('Changed frozen input')
    if args.output.exists(): raise ValueError('Use a new output directory')
    execution=dict(freeze_commit=freeze,sources=sources,inputs=config['inputs'],python=sys.version,
        chronology='Published findings and predictor arrays exposed before freeze; numerical damping fitted after freeze; fluctuation outcomes scored after prediction commit.',
        uncertainty='Reported errors retained; no joint covariance, significance test or full prediction interval.')
    if args.stage=='predict':
        value=forecast(archive,config)
        name='predictions.json'
    else:
        if not args.prediction_commit or not args.predictions: raise ValueError('Committed forecasts required')
        path=args.predictions.resolve().relative_to(ROOT).as_posix()
        body=args.predictions.read_bytes()
        commit=subprocess.check_output(['git','rev-parse',args.prediction_commit],cwd=ROOT,text=True).strip()
        if body!=subprocess.check_output(['git','show',f'{commit}:{path}'],cwd=ROOT):
            raise ValueError('Predictions differ from committed forecast')
        sealed=json.loads(body)
        if sealed!=forecast(archive,config): raise ValueError('Forecast replay differs from seal')
        execution.update(prediction_commit=commit,predictions=dict(path=path,sha256=hashlib.sha256(body).hexdigest()))
        value=evaluate(sealed,archive)
        name='result.json'
    args.output.mkdir(parents=True)
    (args.output/name).write_bytes(encode(value))
    (args.output/'execution.json').write_bytes(encode(execution))
    print(json.dumps({a['name']:a.get('summary',{'admissible_modes':sum(c['fit']['admissible'] for c in a['cases'])}) for a in value['analyses']},indent=2))


if __name__=='__main__': main()
