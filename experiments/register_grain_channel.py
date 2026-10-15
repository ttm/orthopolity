"""Archive the bounded grain/channel transfer without modifying earlier runs."""
import hashlib
import json
from pathlib import Path
import platform
import sys

import numpy as np
import scipy

from audit_grain_channel import verify_sources
from orthopolity.run_registry import archive_reference, file_reference, register_run, verify_registry
from verify_grain_channel import verify

ROOT = Path(__file__).resolve().parents[1]
BASE = 'data/grain-channel/2026-10-15'
FORECAST = 'results/grain-channel-forecast-2026-10-15'
DIRECTORY = 'results/grain-channel-transfer-2026-10-15'
CONFIG = 'configs/grain_channel_2026-10-15.json'


def main():
    verify_sources()
    forecast_path, result_path = ROOT/FORECAST/'predictions.json', ROOT/DIRECTORY/'result.json'
    predictions, result = (json.loads(p.read_text()) for p in (forecast_path,result_path))
    verified = verify(predictions, ROOT/BASE, result)
    verified['prediction_sha256'] = hashlib.sha256(forecast_path.read_bytes()).hexdigest()
    verified['result_sha256'] = hashlib.sha256(result_path.read_bytes()).hexdigest()
    if verified != json.loads((ROOT/DIRECTORY/'verification.json').read_text()):
        raise ValueError('Independent verification changed')
    registry = ROOT/'results/run-registry.jsonl'
    prior = registry.read_bytes()
    if any(json.loads(line)['run_id'] == result['study'] for line in prior.decode().splitlines()):
        print(json.dumps(dict(appended=False,audit=verify_registry(ROOT))))
        return
    sources = ['src/orthopolity/grain_channel.py','experiments/audit_grain_channel.py',
        'experiments/run_grain_channel.py','experiments/verify_grain_channel.py',
        'experiments/plot_grain_channel.py','experiments/register_grain_channel.py',
        'tests/test_grain_channel.py','docs/grain-channel-protocol-2026-10-15.md',
        'docs/grain-channel-design-review-2026-10-15.md','docs/grain-channel-results-2026-10-15.md']
    entry = dict(schema_version=1,run_id=result['study'],evidence_kind='actual_measurement',
        resources=[dict(name='Fluid momentum throughput partitioned by channel boundary and grain resistance',
            units='Pa; kg/s; dimensionless transport',
            definition='Constitutive transport forecast; material-balanced counting measure over runs, neither log-orthopolic nor linear-orthopolic size allocation')],
        data_inputs=[file_reference(ROOT,p.relative_to(ROOT).as_posix(),role='Publisher original or documented response-isolated predictor audit')
                     for p in sorted((ROOT/BASE).rglob('*')) if p.is_file()],
        configs=[archive_reference(ROOT,CONFIG)],
        algorithms=[dict(name='Narrow-only profile fits, shape/wall rivals, independent real-algebra and two-parameter verification',
                         sources=[archive_reference(ROOT,p) for p in sources])],
        artifacts=[file_reference(ROOT,p.relative_to(ROOT).as_posix()) for d in (FORECAST,DIRECTORY)
                   for p in sorted((ROOT/d).iterdir()) if p.is_file()],
        generated_seeds=dict(generated_empirical_data=False,randomized_analysis=False),
        hardware_metadata=dict(python=sys.version,numpy=np.__version__,scipy=scipy.__version__,
                               platform=platform.platform(),runtime_thread_count_verified=False),relationships=[],
        summary=dict(design_commit=result['design_commit'],prediction_commit=result['prediction_commit'],
            primary_calibration_n=19,sensitivity_calibration_n=29,prediction_n=9,
            numerically_withheld_targets=8,decision=result['decision'],relative_gains=result['primary_relative_gains'],
            balanced_mae={m:s['balanced_mae'] for m,s in result['scores']['sphere'].items()},
            material_label_mae=result['scores']['material_label']['balanced_mae'],
            qualifications=['Published qualitative results and one target value exposed before freeze',
                'Old-maximum accuracy tolerance exceeds all wide observations; factor-four low-flux errors remain',
                'Shared measurement uncertainty not propagated; established material-label benchmark predicts better',
                'Diameter, slope, density and width conventions fixed before fitting'],
            conclusion='Measured constraints improve the frozen sphere-calibrated transfer versus two ablations; permissive accuracy gate; no universal neutrality or novel sediment-law confirmation'))
    print(json.dumps(register_run(ROOT,entry),indent=2))
    if not registry.read_bytes().startswith(prior):
        raise ValueError('Earlier registry bytes changed')
    print(json.dumps(verify_registry(ROOT),indent=2))


if __name__ == '__main__':
    main()
