"""Retrospective transfer of measured plant-mass profiles across whole locales.

calibrate: synthetic finite-census diagnostics, with no plant outcome decoding
forecast: fit BFEC plots only; retain templates before formal RMBL evaluation
evaluate: verify/replay templates, then decode and score RMBL plots
audit: replay all computations offline without changing retained artifacts

Prior raw outcome exposure is disclosed. These stages cannot restore blinding.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import scipy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from orthopolity.plant_observation import DEFAULT_SPECIFICATION, calibrate_observation
from orthopolity.plant_profiles import fit_forecasts, profile, score_profile

CONFIG = ROOT / 'configs/plant_biomass_profile_2026-10-03.json'
AMENDMENT = ROOT / 'configs/plant_biomass_profile_2026-10-03_amendment-1.json'
SOURCES = ROOT / 'data/plant-sources/2026-10-03'
DATA = ROOT / 'data/plant-biomass-profile/2026-10-03'
RESULTS = ROOT / 'results/plant-biomass-profile'
SOURCE_PATHS = ['experiments/run_plant_biomass_profile.py', 'experiments/fetch_plant_sources.py',
                'src/orthopolity/plant_profiles.py', 'src/orthopolity/plant_observation.py']


def now():
    return datetime.now(timezone.utc).isoformat()


def read_json(path):
    return json.loads(Path(path).read_text())


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)+'\n').encode()


def save_json(path, value):
    path = Path(path)
    body = encoded(value)
    if path.exists():
        if path.read_bytes() != body:
            raise RuntimeError(f'Refusing to replace changed retained artifact: {path}')
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(body)


def ref(path):
    path = Path(path)
    return dict(path=path.relative_to(ROOT).as_posix(), sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def verify_reference(reference):
    if ref(ROOT / reference['path']) != reference:
        raise RuntimeError(f'Frozen input/source changed: {reference["path"]}')


def source_references(require_committed=False):
    if require_committed:
        for path in [CONFIG, AMENDMENT]:
            config_name = path.relative_to(ROOT).as_posix()
            committed_config = subprocess.check_output(['git', 'show', 'HEAD:'+config_name], cwd=ROOT)
            if committed_config != path.read_bytes():
                raise RuntimeError('Commit the exact protocol/amendment before execution')
        if read_json(AMENDMENT)['base_config_reference'] != ref(CONFIG):
            raise RuntimeError('Amendment belongs to a different base protocol')
    references = []
    for name in SOURCE_PATHS:
        path = ROOT / name
        if require_committed:
            committed = subprocess.check_output(['git', 'show', 'HEAD:'+name], cwd=ROOT)
            if committed != path.read_bytes():
                raise RuntimeError(f'Commit the analysis source before execution: {name}')
        references.append(ref(path))
    return references


def input_references(config):
    check = subprocess.run([sys.executable, str(ROOT / 'experiments/fetch_plant_sources.py')],
                           cwd=ROOT, capture_output=True, text=True)
    if check.returncode:
        raise RuntimeError(f'Plant source verification failed: {check.stderr}')
    receipt = read_json(SOURCES / 'acquisition.json')
    references = {item['plot']: ref(ROOT / item['path']) for item in receipt['files']}
    references['acquisition'] = ref(SOURCES / 'acquisition.json')
    references['exposure'] = ref(ROOT / config['source']['exposure_record'])
    metadata = ROOT / 'data/neutrality-audit/2026-10-03'
    for name in ['acquisition.json', 'plant-commit.json', 'plant-resolved-tree.json', 'plant-repository.json']:
        references['metadata:'+name] = ref(metadata / name)
    return references


def decode_mass_csv(body, field, plot):
    """Universal newline decoding handles CR-only source files safely.

    Return finite positive masses and a complete CSV-record membership ledger.
    Source tokens and invalid values remain in that ledger, never silently fixed.
    """
    stream = io.TextIOWrapper(io.BytesIO(body), encoding='utf-8-sig', newline='')
    reader = csv.DictReader(stream)
    if not reader.fieldnames or reader.fieldnames.count(field) != 1:
        raise ValueError(f'Missing or duplicated mass field: {plot}/{field}')
    masses, membership = [], []
    for record, row in enumerate(reader, 2):
        if None in row:
            raise ValueError(f'Unexpected extra CSV fields at {plot} record {record}')
        token = row.get(field)
        stripped = token.strip() if token is not None else ''
        value, reason = None, 'included_positive'
        if stripped.lower() in {'', 'na', 'nan', 'null', 'none'}:
            reason = 'missing'
        else:
            try:
                number = float(stripped)
            except ValueError:
                reason = 'unparseable'
            else:
                if not math.isfinite(number):
                    reason = 'nonfinite'
                elif number <= 0:
                    reason = 'nonpositive'
                    value = number
                else:
                    value = number
                    masses.append(number)
        membership.append(dict(unit=f'{plot}:{record}', plot=plot, csv_record=record,
                               source_mass_field=field, source_mass_token=token,
                               mass_g=value, status=reason))
    return np.asarray(masses, dtype=float), membership


def read_plots(config, role, release_evaluation=False):
    if role not in {'development', 'evaluation'}:
        raise ValueError('Unknown plot role')
    if role == 'evaluation' and not release_evaluation:
        raise RuntimeError('Evaluation masses are unavailable to the forecast stage')
    arrays, membership = {}, []
    for item in config['source']['files']:
        if item['role'] != role:
            continue
        body = (SOURCES / (item['plot']+'.csv')).read_bytes()
        values, rows = decode_mass_csv(body, item['mass_field'], item['plot'])
        arrays[item['plot']] = values
        membership.extend(rows)
    if len(arrays) != 5:
        raise ValueError('Exactly five complete plots are required in each locale')
    return arrays, membership


def classify_membership(membership, domain):
    result = []
    for row in membership:
        row = dict(row)
        if row['status'] == 'included_positive':
            value = row['mass_g']
            row['status'] = ('below_domain' if value < domain['lower'] else
                             'above_domain' if value > domain['upper'] else 'in_domain')
        result.append(row)
    return result


def calibration_computation(config):
    specification = {key: config['calibration'][key] for key in DEFAULT_SPECIFICATION}
    return calibrate_observation(specification)


def calibrate():
    config = read_json(CONFIG)
    if (DATA / 'calibration.json').exists():
        stored = read_json(DATA / 'calibration.json')
        for item in stored['source_references']+stored['amendment_references']+[stored['config_reference']]:
            verify_reference(item)
        if stored['calibration'] != calibration_computation(config):
            raise RuntimeError('Calibration replay differs')
        return
    sources = source_references(require_committed=True)
    save_json(DATA / 'calibration.json', dict(run_id=config['run_id'], evidence_kind='simulation',
              recorded_utc=now(), config_reference=ref(CONFIG), source_references=sources,
              amendment_references=[ref(AMENDMENT)],
              calibration=calibration_computation(config)))


def forecast_computation(config):
    arrays, membership = read_plots(config, 'development')
    forecasts = fit_forecasts(arrays, lower=config['domain']['lower'],
                              bin_log10_width=config['domain']['log10_bin_width'])
    return forecasts, classify_membership(membership, forecasts['domain'])


def verify_forecasts():
    frozen = read_json(DATA / 'frozen-forecasts.json')
    for item in (frozen['source_references']+list(frozen['input_references'].values())+
                 frozen['amendment_references']+
                 [frozen['config_reference'], frozen['calibration_reference'], frozen['development_membership_reference']]):
        verify_reference(item)
    return frozen


def replay_forecasts(frozen, config):
    forecasts, membership = forecast_computation(config)
    if forecasts != frozen['forecasts'] or membership != read_json(DATA / 'development-membership.json'):
        raise RuntimeError('Development forecast/membership replay differs')
    return forecasts


def forecast():
    config = read_json(CONFIG)
    if (DATA / 'frozen-forecasts.json').exists():
        replay_forecasts(verify_forecasts(), config)
        return
    sources = source_references(require_committed=True)
    inputs = input_references(config)
    calibration = read_json(DATA / 'calibration.json')
    for item in calibration['source_references']+calibration['amendment_references']+[calibration['config_reference']]:
        verify_reference(item)
    forecasts, membership = forecast_computation(config)
    save_json(DATA / 'development-membership.json', membership)
    save_json(DATA / 'frozen-forecasts.json', dict(
        run_id=config['run_id'], frozen_utc=now(), config_reference=ref(CONFIG),
        amendment_references=[ref(AMENDMENT)],
        source_references=sources, input_references=inputs,
        calibration_reference=ref(DATA / 'calibration.json'),
        development_membership_reference=ref(DATA / 'development-membership.json'),
        protocol_commit=subprocess.check_output(['git', 'log', '-1', '--format=%H', '--', str(CONFIG)], cwd=ROOT, text=True).strip(),
        implementation_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        environment=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__),
        scope=config['recorded_scope'], forecasts=forecasts))


def evaluation_computation(forecasts, arrays):
    observed = {plot: profile(values, forecasts['domain']) for plot, values in sorted(arrays.items())}
    raw_scores = {plot: score_profile(forecasts, row) for plot, row in observed.items()}
    scores = {}
    for plot, models in raw_scores.items():
        scores[plot] = {}
        for model, row in models.items():
            loss = row['count_logloss']
            if math.isnan(loss) or loss == -math.inf:
                raise ValueError('Invalid count log loss')
            scores[plot][model] = dict(row, count_logloss=loss if math.isfinite(loss) else None,
                                      count_logloss_infinite=not math.isfinite(loss))
    metrics = ['stock_tv', 'count_tv', 'count_logloss']
    mean_scores = {}
    for model in forecasts['models']:
        values = {metric: float(np.mean([row[model][metric] for row in raw_scores.values()])) for metric in metrics}
        mean_scores[model] = dict(values, count_logloss=values['count_logloss'] if math.isfinite(values['count_logloss']) else None,
                                 count_logloss_infinite=not math.isfinite(values['count_logloss']))
    differences = {}
    for model in forecasts['models']:
        if model == 'log_neutral':
            continue
        deltas = {plot: row[model]['stock_tv']-row['log_neutral']['stock_tv'] for plot, row in scores.items()}
        differences[model] = dict(mean_stock_tv_difference=float(np.mean(list(deltas.values()))),
                                  per_plot_difference=deltas,
                                  comparator_better_plots=sum(value < 0 for value in deltas.values()),
                                  log_neutral_better_plots=sum(value > 0 for value in deltas.values()))
    pooled = profile(np.concatenate(list(arrays.values())), forecasts['domain'])
    return dict(observed_profiles=observed, per_plot_scores=scores, equal_plot_mean_scores=mean_scores,
                ranking_by_stock_tv=sorted(mean_scores, key=lambda model: (mean_scores[model]['stock_tv'], model)),
                differences_from_log_neutral=differences, pooled_profile=pooled,
                mean_observed_stock_shares=np.mean([row['stock_shares'] for row in observed.values()], axis=0).tolist(),
                ecological_neutrality_decision='unresolved: ecological dependence, inclusion and regional replication not calibrated')


def evaluate():
    if (RESULTS / 'study.json').exists():
        return audit(restore_manifest=True)
    frozen = verify_forecasts()
    config = read_json(CONFIG)
    forecasts = replay_forecasts(frozen, config)
    started = now()
    if started <= frozen['frozen_utc']:
        raise RuntimeError('Evaluation must follow the retained forecast freeze')
    arrays, membership = read_plots(config, 'evaluation', release_evaluation=True)
    membership = classify_membership(membership, forecasts['domain'])
    save_json(DATA / 'evaluation-membership.json', membership)
    evaluation = evaluation_computation(forecasts, arrays)
    save_json(RESULTS / 'study.json', dict(
        run_id=config['run_id'], status='complete', evidence_kind='actual_measurement',
        evaluation_started_utc=started, frozen_forecasts=ref(DATA / 'frozen-forecasts.json'),
        config_reference=frozen['config_reference'], evaluation_membership_reference=ref(DATA / 'evaluation-membership.json'),
        evaluation=evaluation, interpretation='Directly weighed coexisting aboveground ramets give realized stock profiles. '
        'Development-only templates transfer across locales; expected ecological neutrality remains unresolved. '
        'Raw plant outcomes were exposed before the protocol: this is retrospective, not blinded.',
        statistical_scope=config['statistical_scope']))
    save_json(RESULTS / 'output-manifest.json', dict(run_id=config['run_id'], artifacts=[ref(RESULTS / 'study.json')],
                                                  membership=ref(DATA / 'evaluation-membership.json')))


def audit(restore_manifest=False):
    config, frozen = read_json(CONFIG), verify_forecasts()
    forecasts = replay_forecasts(frozen, config)
    calibration = read_json(DATA / 'calibration.json')
    if calibration['calibration'] != calibration_computation(config):
        raise RuntimeError('Synthetic calibration replay differs')
    arrays, membership = read_plots(config, 'evaluation', release_evaluation=True)
    if classify_membership(membership, forecasts['domain']) != read_json(DATA / 'evaluation-membership.json'):
        raise RuntimeError('Evaluation membership replay differs')
    result = read_json(RESULTS / 'study.json')
    if result['run_id'] != config['run_id'] or result.get('status') != 'complete':
        raise RuntimeError('Evaluation report belongs to another run or is incomplete')
    if evaluation_computation(forecasts, arrays) != result['evaluation']:
        raise RuntimeError('Evaluation replay differs')
    for item in [result['frozen_forecasts'], result['config_reference'], result['evaluation_membership_reference']]:
        verify_reference(item)
    manifest_path = RESULTS / 'output-manifest.json'
    if restore_manifest and not manifest_path.exists():
        save_json(manifest_path, dict(run_id=config['run_id'], artifacts=[ref(RESULTS / 'study.json')],
                                     membership=ref(DATA / 'evaluation-membership.json')))
    manifest = read_json(manifest_path)
    for item in manifest['artifacts']+[manifest['membership']]:
        verify_reference(item)
    return dict(run_id=config['run_id'], status='verified_offline')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--stage', choices=['calibrate', 'forecast', 'evaluate', 'audit'], required=True)
    stage = parser.parse_args().stage
    result = dict(calibrate=calibrate, forecast=forecast, evaluate=evaluate, audit=audit)[stage]()
    print(json.dumps(result or dict(stage=stage, status='complete', run_id=read_json(CONFIG)['run_id'])))
