"""Qualify the frozen pair-exchange design without decoding later targets."""
import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

from orthopolity.membrane_exchange import qualify
from orthopolity.membrane_exchange_source import read_membrane_archive


ROOT = Path(__file__).resolve().parents[1]
CONFIG = 'configs/membrane_exchange_2026-10-20.json'
FROZEN = [CONFIG, 'docs/membrane-exchange-protocol-2026-10-20.md',
          'src/orthopolity/membrane_exchange_source.py',
          'src/orthopolity/membrane_exchange.py',
          'experiments/run_membrane_exchange.py',
          'experiments/verify_membrane_exchange.py',
          'tests/test_membrane_exchange_source.py',
          'tests/test_membrane_exchange.py',
          'tests/test_membrane_exchange_verification.py']


def encode(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()


def verify_sources():
    cfg = json.loads((ROOT / CONFIG).read_text())
    source = ROOT / cfg['source']
    if hashlib.sha256(source.read_bytes()).hexdigest() != cfg['source_sha256']:
        raise ValueError('Source archive differs from the frozen configuration')
    receipt = json.loads((source.parent / 'acquisition.json').read_text())
    for item in receipt['files']:
        if hashlib.sha256((source.parent / item['file']).read_bytes()).hexdigest() != item['sha256']:
            raise ValueError('Changed original source: ' + item['file'])
    return cfg


def frozen_commit(ref):
    if not ref:
        raise ValueError('Numerical source access requires --freeze-commit')
    full = subprocess.check_output(['git', 'rev-parse', ref], cwd=ROOT, text=True).strip()
    for name in FROZEN:
        saved = subprocess.check_output(['git', 'show', f'{full}:{name}'], cwd=ROOT)
        if saved != (ROOT / name).read_bytes():
            raise ValueError('Frozen implementation changed: ' + name)
    return full


def qualification_document(design):
    cfg = verify_sources()
    source = read_membrane_archive(ROOT / cfg['source'])
    assert source.target_observations is None
    result = qualify(source, cfg)
    return dict(study=cfg['study'], config=cfg, design_commit=design,
                source_sha256=source.archive_sha256, inputs=asdict(source),
                qualification=result, withheld_target_response_count=56,
                target_later_responses_decoded=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=['verify', 'qualify'], required=True)
    parser.add_argument('--freeze-commit')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    verify_sources()
    if args.stage == 'verify':
        print('Original membrane-source bytes verified; no numerical responses decoded.')
        return
    if args.output is None:
        parser.error('--output is required for qualification')
    design = frozen_commit(args.freeze_commit)
    # Check output destination before reading even the authorized measurements.
    args.output.mkdir(parents=True, exist_ok=False)
    started = datetime.now(timezone.utc).isoformat()
    result = qualification_document(design)
    encoded = encode(result)
    (args.output / 'qualification.json').write_bytes(encoded)
    receipt = dict(started_utc=started, completed_utc=datetime.now(timezone.utc).isoformat(),
                   design_commit=design, numerical_stage='qualification',
                   qualification_sha256=hashlib.sha256(encoded).hexdigest(),
                   authorized_calibration_observations=96,
                   authorized_target_baseline_inputs=8,
                   later_target_observations_decoded=0)
    (args.output / 'execution.json').write_bytes(encode(receipt))
    print(json.dumps(dict(stage='qualification', passed=result['qualification']['passed'],
                          stop_reasons=result['qualification']['stop_reasons'],
                          later_target_observations_decoded=0,
                          output=str(args.output)), indent=2))


if __name__ == '__main__':
    main()
