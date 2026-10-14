"""Pre-response discrimination gate using real wind predictors and synthetic flux."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np

from orthopolity.saltation import read_wind, split_wind, day_weights, flux, fit_flux, lognormal_factors

ROOT = Path(__file__).resolve().parents[1]
CONFIG = 'configs/saltation_qualification_2026-10-14.json'
FROZEN = [CONFIG, 'src/orthopolity/saltation.py', 'experiments/qualify_saltation.py',
          'experiments/fetch_saltation.py', 'tests/test_saltation.py',
          'docs/saltation-qualification-protocol-2026-10-14.md',
          'docs/natural-source-audit-2026-10-14.md']


def encode(value):
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n').encode()


def simulate(config):
    rows = read_wind(ROOT/config['workbook'])
    calibration, prediction = split_wind(rows, config)
    all_rows = calibration + prediction
    n = len(calibration)
    x = np.array([r['tau'] for r in all_rows])
    dates = [r['date'] for r in all_rows]
    wc = day_weights(dates[:n])
    wp = day_weights(dates[n:])
    rng = np.random.default_rng(config['seed'])
    scenarios = []
    for cv in config['noise_cv']:
        # Common random numbers across truths/thresholds at this noise level.
        factors = lognormal_factors(rng, dates, cv, config['replicates'])
        for threshold in config['thresholds_Pa']:
            for truth in config['exponents']:
                true_flux = flux(x, 1., threshold, truth)
                scores = []
                fits = []
                correct = ties = 0
                for factor in factors:
                    y = true_flux * factor
                    pair = [fit_flux(x[:n], y[:n], wc, a) for a in config['exponents']]
                    errors = [float(np.sum(wp * (flux(x[n:], p['coefficient'], p['threshold'], p['exponent']) - y[n:])**2)) for p in pair]
                    if abs(errors[0]-errors[1]) <= config['tie_relative_tolerance'] * max(errors + [1e-300]):
                        ties += 1
                    elif config['exponents'][int(np.argmin(errors))] == truth:
                        correct += 1
                    scores.append(errors)
                    fits.append([[p['coefficient'], p['threshold']] for p in pair])
                scenarios.append(dict(noise_cv=cv, threshold_Pa=threshold, generating_exponent=truth,
                    correct=correct, ties=ties, replicates=config['replicates'],
                    correct_fraction=correct/config['replicates'],
                    monte_carlo_standard_error=float(np.sqrt((correct/config['replicates'])*(1-correct/config['replicates'])/config['replicates'])),
                    test_mse=scores, calibration_parameters=fits))
    primary = [s for s in scenarios if s['noise_cv'] == config['primary_noise_cv']]
    passed = all(s['correct_fraction'] >= config['required_correct_fraction'] for s in primary)
    return dict(run_id=config['run_id'], evidence_kind='synthetic_design_qualification',
        actual_flux_values_read=False, calibration_predictors=calibration, prediction_predictors=prediction,
        observation_measure='Equal weight per calendar day, equal duration 30-minute observations within day; neither log- nor linear-orthopolic size allocation',
        scenarios=scenarios, gate=dict(passed=passed, required_correct_fraction=config['required_correct_fraction'],
        primary_noise_cv=config['primary_noise_cv'], minimum_correct_fraction=min(s['correct_fraction'] for s in primary),
        action='eligible_for_separate_real_response_protocol' if passed else 'stop_before_real_response_fitting'))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--freeze-commit', required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    from fetch_saltation import verify
    verify()
    commit = subprocess.check_output(['git','rev-parse',args.freeze_commit], cwd=ROOT, text=True).strip()
    frozen = FROZEN + [str(p.relative_to(ROOT)) for p in sorted((ROOT/'data/saltation/2026-10-14').iterdir()) if p.is_file()]
    for name in frozen:
        prior = subprocess.check_output(['git','show',f'{commit}:{name}'],cwd=ROOT)
        if prior != (ROOT/name).read_bytes():
            raise ValueError('Changed frozen input: '+name)
    if args.output.exists():
        raise FileExistsError('Use a new output directory')
    config = json.loads((ROOT/CONFIG).read_text())
    result = simulate(config)
    args.output.mkdir(parents=True)
    (args.output/'result.json').write_bytes(encode(result))
    (args.output/'summary.json').write_bytes(encode(dict(run_id=config['run_id'],
        calibration_intervals=len(result['calibration_predictors']), prediction_intervals=len(result['prediction_predictors']),
        scenarios=[{k:v for k,v in s.items() if k not in ('test_mse','calibration_parameters')} for s in result['scenarios']],
        gate=result['gate'], actual_flux_values_read=False)))
    (args.output/'execution.json').write_bytes(encode(dict(freeze_commit=commit, python=sys.version,
        sources=[dict(path=name,sha256=hashlib.sha256((ROOT/name).read_bytes()).hexdigest()) for name in frozen])))
    print(json.dumps(result['gate'], indent=2))


if __name__ == '__main__':
    main()
