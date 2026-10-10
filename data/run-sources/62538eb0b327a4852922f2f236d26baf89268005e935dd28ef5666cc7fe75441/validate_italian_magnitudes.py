"""Run the frozen synthetic gate. No real catalogue inputs or hypothesis verdict."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
from pathlib import Path
import subprocess
import time

import numpy as np
import pandas as pd
import scipy

from orthopolity.magnitude_validation import (
    gate_cell, observed_bins, population_limit, registered_summary,
    simulate_source_ticks, source_grid_estimate, wilson_interval,
)

ROOT = Path(__file__).resolve().parents[1]
CONFIG = 'configs/italian_magnitude_validation_2026-10-10.json'
SOURCES = ['src/orthopolity/magnitude_validation.py',
           'experiments/validate_italian_magnitudes.py',
           'tests/test_magnitude_validation.py', 'experiments/run_volumetric_b.py',
           'docs/italian-magnitude-validation-protocol-2026-10-10.md']


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(output):
    start = time.monotonic()
    cfg = json.loads((ROOT/CONFIG).read_text())
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise ValueError('Output directory must be empty; preserve completed runs')
    rows, cells = [], []
    for model_i, model in enumerate(cfg['models']):
        for b_i, true_b in enumerate(cfg['true_b']):
            for lower_i, lower in enumerate(cfg['true_lower_mw']):
                cell = dict(model=model['name'], true_b=true_b, lower_mw=lower,
                            included_in_gate=model['gate'])
                reps = []
                for repeat in range(cfg['replicates']):
                    seed = [cfg['seed'], model_i, b_i, lower_i, repeat]
                    rng = np.random.default_rng(np.random.SeedSequence(seed))
                    ticks = simulate_source_ticks(true_b, lower, cfg['events_per_replicate'], model, rng)
                    fit = registered_summary(observed_bins(ticks, model), rng,
                                             cfg['bootstrap_resamples'], cfg['minimum_complete_events'])
                    if fit['eligible']:
                        fit['covered'] = fit['ci_low'] <= true_b <= fit['ci_high']
                        fit['grid_b_diagnostic'] = source_grid_estimate(ticks, fit['mc'], model)
                    row = dict(cell, repeat=repeat, **fit)
                    rows.append(row)
                    reps.append(row)
                valid = [r for r in reps if r['eligible']]
                estimates = np.array([r['b'] for r in valid])
                count = len(valid)
                covered = sum(r['covered'] for r in valid)
                bias = float(estimates.mean()-true_b) if count else None
                coverage = covered/count if count else None
                cells.append(dict(cell, eligible=count, replicates=len(reps),
                    mean_b=float(estimates.mean()) if count else None, mean_bias=bias,
                    bias_mcse=float(estimates.std(ddof=1)/np.sqrt(count)) if count > 1 else None,
                    rmse=float(np.sqrt(np.mean((estimates-true_b)**2))) if count else None,
                    coverage=coverage, covered=covered, coverage_wilson95=wilson_interval(covered, count),
                    coverage_mcse=float(np.sqrt(coverage*(1-coverage)/count)) if count else None,
                    mean_bootstrap_se=float(np.mean([r['se'] for r in valid])) if count else None,
                    grid_mean_b_diagnostic=float(np.mean([r['grid_b_diagnostic'] for r in valid])) if count else None,
                    population=population_limit(true_b, lower, model),
                    passes_cell=gate_cell(count, len(reps), bias, coverage, cfg['gate'])))
        model_cells = [c for c in cells if c['model'] == model['name']]
        print(f"{model['name']}: {sum(c['passes_cell'] for c in model_cells)}/{len(model_cells)} cells pass", flush=True)
    gated = [c for c in cells if c['included_in_gate']]
    passed = all(c['passes_cell'] for c in gated)
    summary = dict(run_id=cfg['run_id'], evidence_kind='simulation',
        scope='Magnitude marginal validation only; no real Italian fit, D2 or physical hypothesis decision',
        passes_gate=passed, n_gate_cells=len(gated), n_failed_gate_cells=sum(not c['passes_cell'] for c in gated),
        next_stage_authorized_by_gate=passed,
        decision='magnitude gate passes; further design required' if passed else 'stop before real Italian sequence construction or response fitting',
        cells=cells)
    (output/'config.json').write_bytes((ROOT/CONFIG).read_bytes())
    (output/'summary.json').write_text(json.dumps(summary, indent=2, allow_nan=False)+'\n')
    pd.DataFrame(rows).to_csv(output/'replicates.csv.gz', index=False,
                            compression={'method': 'gzip', 'mtime': 0})
    flat = [{**{k:v for k,v in c.items() if k not in ('population','coverage_wilson95')},
             **{'population_'+k:v for k,v in c['population'].items()},
             'coverage_low':c['coverage_wilson95'][0], 'coverage_high':c['coverage_wilson95'][1]} for c in cells]
    pd.DataFrame(flat).to_csv(output/'cells.csv', index=False)
    execution = dict(config_sha256=digest(ROOT/CONFIG),
        source_sha256={p:digest(ROOT/p) for p in SOURCES},
        methods_pdf_sha256=digest(ROOT/cfg['source']['path']),
        git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        runtime=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,pandas=pd.__version__),
        elapsed_seconds=time.monotonic()-start,
        artifact_sha256={p.name:digest(p) for p in sorted(output.iterdir()) if p.is_file()})
    (output/'execution.json').write_text(json.dumps(execution,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k!='cells'},indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'build/reproductions/italian-magnitude-validation')
    run(parser.parse_args().output)
