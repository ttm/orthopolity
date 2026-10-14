"""Freeze pure-gas calibration forecasts before evaluating mixture uptake."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from orthopolity.adsorption import read_aif, fugacity, langmuir, competitive, iast, fit_pure
from fetch_adsorption import verify, encode

BASE = ROOT/'data/adsorption/2026-10-13'
CONFIG = 'configs/adsorption_2026-10-13.json'
FROZEN = [CONFIG, 'docs/adsorption-protocol-2026-10-13.md',
          'docs/adsorption-source-audit-2026-10-13.md',
          'src/orthopolity/adsorption.py', 'experiments/fetch_adsorption.py',
          'experiments/run_adsorption.py', 'tests/test_adsorption.py',
          'tests/test_adsorption_runner.py',
          'data/adsorption/2026-10-13/predictor-audit.json']
GASES = ['CO2', 'CH4']


def pure_path(temp, gas):
    return BASE/f'RM8850_{gas}_{temp}K_CW.aif'


def mixed_path(temp):
    return BASE/f'RM8850_CO2_CH4_{temp}K_CW.aif'


def table_rows(label):
    root = ET.parse(BASE/'paper.xml').getroot()
    table = next(t for t in root.findall('.//table-wrap') if t.findtext('label') == label)
    return [[ ''.join(c.itertext()).strip() for c in row]
            for row in table.findall('./table/tbody/tr') if ''.join(row[0].itertext()).strip()]


def predictor_audit():
    # Only pressure, composition and reported uncertainty are converted here.
    paper = table_rows('Table 7')
    result = dict(mixture={}, pure={}, responses_inspected=False)
    for temp in [298, 313, 333, 353]:
        a = read_aif(mixed_path(temp), ['_adsorp_pressure', '_adsorp_molefraction1',
            '_adsorp_molefraction2', '_adsorp_amount1_uncertainty', '_adsorp_amount2_uncertainty'])
        p = [r for r in paper if round(float(r[0])) == temp]
        if len(a) != len(p) or not np.array_equal(a[:, :2], [[float(r[1]),float(r[2])] for r in p]):
            raise ValueError('Paper/archive predictor mismatch')
        if not np.array_equal(a[:, 3:], [[float(r[7]),float(r[8])] for r in p]):
            raise ValueError('Archive uncertainty no longer matches MC columns')
        if np.any(a[:, 0] <= 0) or np.any(a[:, 1:3] <= 0) or not np.allclose(a[:, 1:3].sum(axis=1), 1, atol=1e-12, rtol=0):
            raise ValueError('Unqualified mixture predictors')
        result['mixture'][str(temp)] = dict(rows=len(a),pressure_MPa=a[:,0].tolist(),
            y_CO2=a[:,1].tolist(),paper_temperature_K=[float(r[0]) for r in p],
            uncertainty='Archive matches Table 7 Monte Carlo columns; footnote k=2')
    for temp in [298,333,353,393]:
        for gas in GASES:
            a = read_aif(pure_path(temp,gas),['_adsorp_pressure','_adsorp_amount_uncertainty'])
            result['pure'][f'{gas}_{temp}'] = dict(rows=len(a),pressure_MPa=a[:,0].tolist())
    return result


def forecast(config):
    analyses = []
    for name in ['peng_robinson','ideal']:
        ideal = name == 'ideal'
        cases = []
        for temp in config['temperatures_K']:
            fs, qs, us, pure = [], [], [], []
            for i, gas in enumerate(GASES):
                a = read_aif(pure_path(temp,gas),['_adsorp_pressure','_adsorp_amount','_adsorp_amount_uncertainty'])
                source_rows = [r for r in table_rows('Table 5' if i == 0 else 'Table 6')
                               if round(float(r[0])) == temp]
                if not np.array_equal(a, [[float(r[1]),float(r[3]),float(r[5])] for r in source_rows]):
                    raise ValueError('Pure archive/paper mismatch')
                f = np.array([fugacity(temp,p,np.eye(2)[i],config['critical_constants'],ideal)[i] for p in a[:,0]])
                fs.append(f); qs.append(a[:,1]); us.append(a[:,2])
                pure.append(dict(fugacity_MPa=f.tolist(),amount_mmol_g=a[:,1].tolist(),
                    expanded_U_mmol_g=a[:,2].tolist()))
            shared = fit_pure(fs,qs,us,shared=True)
            separate = fit_pure(fs,qs,us,shared=False)
            rows = []
            # Deliberately never parse mixture response/error columns in forecast.
            predictors = read_aif(mixed_path(temp),['_adsorp_pressure','_adsorp_molefraction1'])
            for j,(p,y) in enumerate(predictors):
                f = fugacity(temp,p,[y,1-y],config['critical_constants'],ideal)
                common = competitive(f,shared['capacities'][0],shared['affinities'])
                independent = langmuir(f,np.array(shared['capacities']),np.array(shared['affinities']))
                benchmark, f0 = iast(f,separate['capacities'],separate['affinities'])
                rows.append(dict(row=j+1,p_MPa=float(p),y_CO2=float(y),fugacity_MPa=f.tolist(),
                    predictions=dict(shared=common.tolist(),ablation=independent.tolist(),iast=benchmark.tolist()),
                    iast_f0_MPa=f0.tolist(),
                    iast_extrapolated=(f0 > np.array(separate['max_fugacity_MPa'])).tolist()))
            cases.append(dict(temperature_K=temp,shared_fit=shared,separate_fit=separate,pure_data=pure,rows=rows))
        analyses.append(dict(name=name,cases=cases))
    return dict(run_id='adsorption-transfer-2026-10-13',reference_measure='Counting measure over species and vacancies',
        models='Shared-capacity Langmuir; no-competition ablation; separate-pure-capacity IAST',analyses=analyses)


def score_case(rows, model):
    predicted = np.array([r['predictions'][model] for r in rows])
    observed = np.array([r['observed_mmol_g'] for r in rows])
    u = np.array([r['expanded_U_mmol_g'] for r in rows])
    error = predicted-observed
    return dict(component_mae_mmol_g=np.mean(abs(error),axis=0).tolist(),
        component_bias_mmol_g=np.mean(error,axis=0).tolist(),
        total_mae_mmol_g=float(np.mean(abs(error.sum(axis=1)))),
        adsorbed_CO2_fraction_mae=float(np.mean(abs(predicted[:,0]/predicted.sum(axis=1)-observed[:,0]/observed.sum(axis=1)))),
        within_reported_U=int(np.sum(abs(error)<=u)),component_targets=int(error.size))


def evaluate(sealed):
    result = copy.deepcopy(sealed)
    paper = table_rows('Table 7')
    for analysis in result['analyses']:
        for case in analysis['cases']:
            temp = case['temperature_K']
            a = read_aif(mixed_path(temp),['_adsorp_amount1','_adsorp_amount2',
                '_adsorp_amount1_uncertainty','_adsorp_amount2_uncertainty'])
            p = [r for r in paper if round(float(r[0])) == temp]
            if not np.array_equal(a[:,:2],[[float(r[3]),float(r[4])] for r in p]):
                raise ValueError('Archive/paper response mismatch; do not silently resolve')
            if len(a)!=len(case['rows']) or np.any(a[:,:2] < 0) or np.any(a[:,2:] <= 0):
                raise ValueError('Unqualified target measurements')
            for row,values in zip(case['rows'],a):
                row.update(observed_mmol_g=values[:2].tolist(),expanded_U_mmol_g=values[2:].tolist())
                row['residuals_mmol_g'] = {m:(np.asarray(v)-values[:2]).tolist()
                                         for m,v in row['predictions'].items()}
            case['scores'] = {model:score_case(case['rows'],model) for model in ['shared','ablation','iast']}
            n = len(case['rows'])//3
            case['sweeps'] = [{model:score_case(case['rows'][i*n:(i+1)*n],model)
                              for model in ['shared','ablation','iast']} for i in range(3)]
            case['shared_transfer_adequate'] = bool(case['shared_fit']['locally_identified'] and
                case['shared_fit']['pure_fit_adequate'] and all(e/q <= .10 for e,q in
                zip(case['scores']['shared']['component_mae_mmol_g'],case['shared_fit']['pure_max_mmol_g'])))
        summaries = {}
        for model in ['shared','ablation','iast']:
            scores = [c['scores'][model] for c in analysis['cases']]
            summaries[model] = dict(balanced_mae_mmol_g=float(np.mean([s['component_mae_mmol_g'] for s in scores])),
                balanced_total_mae_mmol_g=float(np.mean([s['total_mae_mmol_g'] for s in scores])),
                balanced_composition_mae=float(np.mean([s['adsorbed_CO2_fraction_mae'] for s in scores])),
                within_reported_U=sum(s['within_reported_U'] for s in scores),
                component_targets=sum(s['component_targets'] for s in scores))
        gain = 1-summaries['shared']['balanced_mae_mmol_g']/summaries['ablation']['balanced_mae_mmol_g']
        analysis['summary'] = dict(scores=summaries,shared_improvement_over_ablation=gain,
            adequate_temperatures=sum(c['shared_transfer_adequate'] for c in analysis['cases']),
            declared_joint_transfer_pass=bool(all(c['shared_transfer_adequate'] for c in analysis['cases']) and gain>=.20),
            interpretation='Descriptive within-material transfer; pragmatic accuracy rule, not a statistical test or universal-law confirmation')
    return result


def check_freeze(commit):
    freeze = subprocess.check_output(['git','rev-parse',commit],cwd=ROOT,text=True).strip()
    refs = []
    for path in FROZEN:
        body = (ROOT/path).read_bytes()
        if body != subprocess.check_output(['git','show',f'{freeze}:{path}'],cwd=ROOT):
            raise ValueError('Unfrozen source: '+path)
        refs.append(dict(path=path,sha256=hashlib.sha256(body).hexdigest()))
    return freeze,refs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage',choices=['audit','predict','evaluate'],required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--freeze-commit')
    parser.add_argument('--prediction-commit')
    parser.add_argument('--predictions',type=Path)
    args = parser.parse_args()
    verify()
    audit = predictor_audit()
    if args.output.exists():
        raise ValueError('Use an unused output path')
    if args.stage == 'audit':
        args.output.write_bytes(encode(audit)); return
    if not args.freeze_commit:
        raise ValueError('Design must be committed before fitting')
    freeze,sources = check_freeze(args.freeze_commit)
    if audit != json.loads((BASE/'predictor-audit.json').read_text()):
        raise ValueError('Changed predictor audit')
    config = json.loads((ROOT/CONFIG).read_text())
    for item in config['inputs']:
        if hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()!=item['sha256']:
            raise ValueError('Changed input '+item['path'])
    execution = dict(freeze_commit=freeze,sources=sources,inputs=config['inputs'],python=sys.version,
        chronology='Published qualitative results exposed; numerical pure fits after design commit; mixture responses after forecast commit.',
        uncertainty='U/2 used as fitting weights only; unknown joint covariance, no population inference or calibrated prediction intervals.')
    predicted = forecast(config)
    if args.stage == 'predict':
        value,name = predicted,'predictions.json'
    else:
        if not args.prediction_commit or not args.predictions:
            raise ValueError('Committed forecasts required')
        commit = subprocess.check_output(['git','rev-parse',args.prediction_commit],cwd=ROOT,text=True).strip()
        path = args.predictions.resolve().relative_to(ROOT).as_posix()
        body = args.predictions.read_bytes()
        if body != subprocess.check_output(['git','show',f'{commit}:{path}'],cwd=ROOT):
            raise ValueError('Forecast differs from seal')
        sealed = json.loads(body)
        if sealed != predicted:
            raise ValueError('Forecast replay differs')
        execution.update(prediction_commit=commit,predictions=dict(path=path,sha256=hashlib.sha256(body).hexdigest()))
        value,name = evaluate(sealed),'result.json'
    args.output.mkdir(parents=True)
    (args.output/name).write_bytes(encode(value))
    (args.output/'execution.json').write_bytes(encode(execution))
    print(json.dumps({a['name']:a.get('summary',{'temperatures':len(a['cases'])}) for a in value['analyses']},indent=2))


if __name__ == '__main__':
    main()
