"""Append the biological assay transfer, retaining its failed model rule."""
import hashlib
import json
from pathlib import Path
import platform
import sys

import numpy as np
import scipy

from run_burden_transfer import verify_sources
from verify_burden_transfer import verify
from orthopolity.run_registry import archive_reference, file_reference, register_run, verify_registry

ROOT = Path(__file__).resolve().parents[1]
BASE = 'data/biology-candidates/2026-10-16/borkowski2018'
FORECAST = 'results/burden-transfer-forecast-2026-10-16'
RESULT = 'results/burden-transfer-2026-10-16'


def main():
    verify_sources()
    fp, rp = ROOT/FORECAST/'predictions.json', ROOT/RESULT/'result.json'
    prediction, result = json.loads(fp.read_text()), json.loads(rp.read_text())
    verified = verify(prediction, result)
    verified.update(prediction_sha256=hashlib.sha256(fp.read_bytes()).hexdigest(),
                    result_sha256=hashlib.sha256(rp.read_bytes()).hexdigest())
    if verified != json.loads((ROOT/RESULT/'verification.json').read_text()):
        raise ValueError('Independent verification changed')
    registry = ROOT/'results/run-registry.jsonl'
    prior = registry.read_bytes()
    if any(json.loads(line)['run_id'] == result['study'] for line in prior.decode().splitlines()):
        print(json.dumps(dict(appended=False, audit=verify_registry(ROOT))))
        return
    sources = ['src/orthopolity/burden_transfer.py', 'experiments/run_burden_transfer.py',
        'experiments/verify_burden_transfer.py', 'experiments/plot_burden_transfer.py',
        'experiments/register_burden_transfer.py', 'tests/test_burden_transfer.py',
        'docs/burden-transfer-protocol-2026-10-16.md', 'docs/burden-transfer-results-2026-10-16.md',
        'docs/biology-intervention-source-audit-2026-10-16.md']
    entry = dict(schema_version=1, run_id=result['study'], evidence_kind='actual_measurement',
        resources=[dict(name='Protein expression capacity and inferred relative workload',
            units='Normalized reporter production capacity; inferred dimensionless load',
            definition=result['config']['reference_measure']+'; no absolute ribosome or energy assay')],
        data_inputs=[file_reference(ROOT, p.relative_to(ROOT).as_posix(), role='Publisher original or acquisition receipt')
                     for p in sorted((ROOT/BASE).iterdir()) if p.is_file()],
        configs=[archive_reference(ROOT, 'configs/burden_transfer_2026-10-16.json')],
        algorithms=[dict(name='Frozen free-pool and empirical transfer with independent numerical verification',
                         sources=[archive_reference(ROOT, p) for p in sources])],
        artifacts=[file_reference(ROOT, p.relative_to(ROOT).as_posix()) for d in (FORECAST, RESULT)
                   for p in sorted((ROOT/d).iterdir()) if p.is_file()],
        generated_seeds=dict(generated_empirical_data=False, randomized_analysis=False),
        hardware_metadata=dict(python=sys.version, numpy=np.__version__, scipy=scipy.__version__,
                               platform=platform.platform(), runtime_thread_count_verified=False),
        relationships=[], summary=dict(design_commit=result['design_commit'], prediction_commit=result['prediction_commit'],
            calibration_n=12, target_n=10, target_gene_families=7, numerically_withheld_targets=10,
            family_balanced_mae={m:s['family_balanced_mae'] for m,s in result['scores'].items()},
            decision=result['decision'], relative_gains=result['gains'],
            qualifications=['Published qualitative results known; locally frozen retrospective comparison',
                'Extract assay is a workload proxy, not independently assayed absolute resource cost',
                'Direct transfer is the reciprocal family at k=1; failure concerns the fitted correction',
                'Five target assays extrapolate; correlated normalized measurement errors unpropagated',
                'Source workbook spreads match sample SD, despite paper SEM captions'],
            conclusion='Assay information transfers, but reciprocal correction fails frozen accuracy and comparative-advantage criteria; no biological neutral-allocation confirmation'))
    print(json.dumps(register_run(ROOT, entry), indent=2))
    if not registry.read_bytes().startswith(prior):
        raise ValueError('Earlier registry bytes changed')
    print(json.dumps(verify_registry(ROOT), indent=2))


if __name__ == '__main__':
    main()
