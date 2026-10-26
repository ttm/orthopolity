"""Preserve the amended wall transfer, including failed qualification, in the registry."""
import hashlib
import json
from pathlib import Path
import platform
import sys

import numpy as np

from orthopolity.run_registry import archive_reference, file_reference, register_run, verify_registry
from run_hotbox_transfer import CONFIG, FROZEN, freeze
from verify_hotbox_transfer import verify
from audit_hotbox_transfer import audit

ROOT = Path(__file__).resolve().parents[1]
FORECAST = 'results/hotbox-forecast-2026-10-26'
RESULT = 'results/hotbox-transfer-2026-10-26'
RUN = 'hotbox-profile-transfer-2026-10-26'


def main():
    raw = (ROOT/FORECAST/'predictions.json').read_bytes()
    prediction = json.loads(raw)
    result_raw = (ROOT/RESULT/'result.json').read_bytes()
    result = json.loads(result_raw)
    freeze(prediction['design_commit'], FROZEN)
    freeze(result['prediction_commit'], [FORECAST+'/'+name for name in
           ('predictions.json', 'verification.json', 'source-audit.json')])
    checked = verify(prediction)
    source_checked = audit(prediction, result, prediction_sha256=hashlib.sha256(raw).hexdigest())
    source_report = json.loads((ROOT/RESULT/'source-audit.json').read_text())
    for key, value in source_checked.items():
        if source_report[key] != value:
            raise ValueError('Changed independent audit: '+key)
    if source_report['result_sha256'] != hashlib.sha256(result_raw).hexdigest():
        raise ValueError('Result does not match audited bytes')
    registry = ROOT/'results/run-registry.jsonl'
    prior = registry.read_bytes()
    if any(json.loads(line)['run_id'] == RUN for line in prior.decode().splitlines()):
        print(json.dumps(dict(appended=False, audit=verify_registry(ROOT)), indent=2))
        return
    sources = [name for name in FROZEN if name != CONFIG]
    sources += ['experiments/audit_hotbox_transfer.py', 'experiments/register_hotbox_transfer.py',
                'docs/hotbox-forecast-2026-10-26.md', 'docs/hotbox-transfer-results-2026-10-26.md']
    data_paths = [prediction['config']['source'],
                  'data/physics-candidates/2026-10-25/storage/hotbox-metadata.json',
                  'data/physics-candidates/2026-10-25/storage/acquisition.json',
                  'results/hotbox-qualification-2026-10-26/availability.json']
    entry = dict(schema_version=1, run_id=RUN, evidence_kind='actual_measurement',
        resources=[dict(name='Temperature profile and thermal-resistance coordinate', units='degree C; m',
                        definition=prediction['config']['reference_measure']+'; no complete energy budget measured')],
        data_inputs=[file_reference(ROOT, p) for p in data_paths],
        configs=[archive_reference(ROOT, CONFIG)],
        algorithms=[dict(name='Frozen normalized profile transfer, fixed additive rival and full qualification audit',
                         sources=[archive_reference(ROOT, p) for p in sources])],
        artifacts=[file_reference(ROOT, p.relative_to(ROOT).as_posix())
                   for folder in (FORECAST, RESULT) for p in sorted((ROOT/folder).iterdir()) if p.is_file()],
        generated_seeds=dict(generated_empirical_data=False, randomized_analysis=False),
        hardware_metadata=dict(python=sys.version, numpy=np.__version__, platform=platform.platform(),
                               runtime_thread_count_verified=False), relationships=[],
        summary=dict(design_commit=result['design_commit'], forecast_commit=result['prediction_commit'],
            verdict=result['verdict'], groups=result['groups'],
            forecast_numerical_checks=checked['numeric_checks'], source_numerical_checks=source_checked['numeric_checks'],
            qualifications=[
                'Original 15-position qualification stopped; whole position 8 excluded by dated input-availability amendment',
                'Published convection conclusions known; only local numerical withholding, not external preregistration',
                'Conditional sensor-error scenario; some inputs outside calibration range and one case contains constant archived records',
                'Five forcing conditions of one wall, not 210 independent replicates',
                '61/174 gate-qualified means outside transfer envelopes; full-cohort qualification incomplete',
                'Neither conserved heat throughput nor unique general-law confirmation measured'],
            conclusion='Mean error improves against all frozen comparisons but absolute accuracy scenario fails on qualified profiles',
            registration_scope='Amended locally frozen retrospective public-data transfer; all failures retained'))
    print(json.dumps(register_run(ROOT, entry), indent=2))
    if not registry.read_bytes().startswith(prior):
        raise ValueError('Earlier registry bytes changed')
    print(json.dumps(verify_registry(ROOT), indent=2))


if __name__ == '__main__':
    main()
