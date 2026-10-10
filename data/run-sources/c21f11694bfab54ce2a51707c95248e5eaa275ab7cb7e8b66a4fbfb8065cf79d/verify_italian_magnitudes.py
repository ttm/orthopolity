"""Replay retained summaries and compare synthetic samples with the original runner."""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import statistics

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def verify(directory):
    execution = json.loads((directory/'execution.json').read_text())
    for path, sha in execution['source_sha256'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == sha, path
    for path, sha in execution['artifact_sha256'].items():
        assert hashlib.sha256((directory/path).read_bytes()).hexdigest() == sha, path
    cfg = json.loads((directory/'config.json').read_text())
    assert hashlib.sha256((directory/'config.json').read_bytes()).hexdigest() == execution['config_sha256']
    assert hashlib.sha256((ROOT/cfg['source']['path']).read_bytes()).hexdigest() == execution['methods_pdf_sha256']
    summary = json.loads((directory/'summary.json').read_text())
    with gzip.open(directory/'replicates.csv.gz', 'rt') as stream:
        records = list(csv.DictReader(stream))
    by_cell = {}
    for row in records:
        key = (row['model'], float(row['true_b']), float(row['lower_mw']))
        by_cell.setdefault(key, []).append(row)
    expected_cells = len(cfg['models'])*len(cfg['true_b'])*len(cfg['true_lower_mw'])
    assert len(by_cell) == len(summary['cells']) == expected_cells
    expected_keys = {(m['name'],b,lo) for m in cfg['models'] for b in cfg['true_b'] for lo in cfg['true_lower_mw']}
    assert set(by_cell) == expected_keys
    failed = 0
    max_se_difference = 0
    spec = importlib.util.spec_from_file_location('original', ROOT/'experiments/run_volumetric_b.py')
    old = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(old)
    for cell in summary['cells']:
        rows = by_cell[(cell['model'], cell['true_b'], cell['lower_mw'])]
        assert sorted(int(r['repeat']) for r in rows) == list(range(cfg['replicates']))
        valid = [r for r in rows if r['eligible'] == 'True']
        estimates = [float(r['b']) for r in valid]
        count = sum(float(r['ci_low']) <= cell['true_b'] <= float(r['ci_high']) for r in valid)
        for r in valid:
            assert (r['covered'] == 'True') == (float(r['ci_low']) <= cell['true_b'] <= float(r['ci_high']))
        bias = statistics.mean(estimates)-cell['true_b'] if estimates else None
        coverage = count/len(valid) if valid else None
        assert len(valid) == cell['eligible']
        assert abs(bias-cell['mean_bias']) < 1e-12
        assert coverage == cell['coverage']
        gate = cfg['gate']
        passes = (len(valid)/len(rows) >= gate['minimum_eligibility_rate']
                  and abs(bias) <= gate['max_absolute_mean_bias'] and coverage >= gate['minimum_coverage'])
        assert passes == cell['passes_cell']
        failed += bool(cell['included_in_gate'] and not passes)

        # Reconstruct the first sample independently and use the unchanged old
        # completeness/b routines, including literal event-vector resampling.
        mi = next(i for i,m in enumerate(cfg['models']) if m['name'] == cell['model'])
        model = cfg['models'][mi]
        bi = cfg['true_b'].index(cell['true_b'])
        li = cfg['true_lower_mw'].index(cell['lower_mw'])
        rng = np.random.default_rng(np.random.SeedSequence([cfg['seed'],mi,bi,li,0]))
        true = cell['lower_mw'] + rng.exponential(np.log10(np.e)/cell['true_b'], cfg['events_per_replicate'])
        source = (true-model['intercept'])/model.get('true_slope',model['slope'])
        if model['source_sigma']:
            source += rng.normal(0,model['source_sigma'],len(source))
        ticks = np.rint(np.round(source,1)/.1).astype(np.int64)
        proxy = np.round(model['intercept']+model['slope']*.1*ticks,2)
        m = np.round(proxy,1)
        mc = old.completeness(m)
        above = m[m >= mc-1e-9]
        first = next(r for r in rows if int(r['repeat']) == 0)
        assert abs(mc-float(first['mc'])) < 1e-12 and len(above) == int(first['n_complete'])
        if len(above) >= cfg['minimum_complete_events']:
            point, se = old.b_value(above, mc, rng, cfg['bootstrap_resamples'])
            assert abs(point-float(first['b'])) < 1e-12
            relative = abs(se/float(first['se'])-1)
            # Two independently sampled bootstrap SEs each have Monte Carlo
            # variation. This generous bound detects a different distribution.
            assert relative < .20, (cell['model'],relative)
            max_se_difference = max(max_se_difference,relative)
    assert failed == summary['n_failed_gate_cells']
    assert (failed == 0) == summary['passes_gate']
    result = dict(verified=True, replicates=len(records), cells=len(by_cell),
                  failed_gate_cells=failed, original_runner_samples_verified=expected_cells,
                  max_relative_bootstrap_se_difference=max_se_difference,
                  note='Source/artifact hashes; CSV-derived decisions; original point/MAXC and independent event bootstrap on first sample in every cell. Population integration is separately tested against exact geometric tails.')
    (directory/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--directory',type=Path,required=True)
    verify(ap.parse_args().directory)
