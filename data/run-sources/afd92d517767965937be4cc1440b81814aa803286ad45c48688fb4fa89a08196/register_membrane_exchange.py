"""Register the complete frozen membrane qualification and pair transfer."""
import hashlib
import json
from pathlib import Path
import platform
import sys

import numpy as np

from orthopolity.run_registry import archive_reference, file_reference, register_run, verify_registry
from run_membrane_exchange import FROZEN as QUALIFICATION_FILES
from run_membrane_transfer import FROZEN, checked_qualification, checked_prediction, freeze
from verify_membrane_transfer import verify_result
from audit_membrane_released_targets import audit

ROOT = Path(__file__).resolve().parents[1]
QUALIFICATION = 'results/membrane-exchange-qualification-2026-10-20'
FORECAST = 'results/membrane-exchange-forecast-2026-10-22'
RESULT = 'results/membrane-exchange-transfer-2026-10-22'
CONFIG = 'configs/membrane_exchange_2026-10-20.json'


def main():
    qdoc, qraw = checked_qualification()
    cfg = qdoc['config']
    result_path = ROOT / RESULT / 'result.json'
    raw_result = result_path.read_bytes()
    result = json.loads(raw_result)
    implementation = freeze(result['implementation_commit'], FROZEN)
    prediction, prediction_raw, sealed = checked_prediction(
        implementation, qdoc, qraw, ROOT / FORECAST / 'predictions.json', result['prediction_commit'])
    checked = verify_result(result, prediction, qdoc)
    checked['result_sha256'] = hashlib.sha256(raw_result).hexdigest()
    if checked != json.loads((ROOT / RESULT / 'verification.json').read_text()):
        raise ValueError('Independent transfer verification differs')
    if audit() != json.loads((ROOT / RESULT / 'source-audit.json').read_text()):
        raise ValueError('Independent original-source cell audit differs')
    execution = json.loads((ROOT / RESULT / 'execution.json').read_text())
    for key, value in dict(stage='evaluate', artifact_sha256=hashlib.sha256(raw_result).hexdigest(),
            design_commit=qdoc['design_commit'], implementation_commit=implementation,
            prediction_commit=sealed, later_target_observations_decoded=56).items():
        if execution[key] != value:
            raise ValueError('Execution receipt differs: ' + key)
    registry = ROOT / 'results/run-registry.jsonl'
    prior = registry.read_bytes()
    if any(json.loads(line)['run_id'] == cfg['study'] for line in prior.decode().splitlines()):
        print(json.dumps(dict(appended=False, audit=verify_registry(ROOT)), indent=2))
        return
    sources = [p for p in [*QUALIFICATION_FILES, *FROZEN] if p != CONFIG and not p.startswith('results/')]
    sources += ['experiments/plot_membrane_exchange.py', 'experiments/register_membrane_exchange.py',
                'experiments/audit_membrane_released_targets.py',
                'docs/membrane-exchange-results-2026-10-22.md',
                'docs/exchange-source-followup-2026-10-20.md',
                'docs/exchange-observability-2026-10-20.md']
    evaluation = result['evaluation']
    stock = evaluation['total_stock']
    summary = dict(
        design_commit=qdoc['design_commit'], implementation_commit=implementation,
        prediction_commit=sealed, qualification_passed=qdoc['qualification']['passed'],
        calibration_observations=96, target_baseline_inputs=8, target_observations=56,
        heldout_transfer_evaluated=True,
        primary_errors={name: value['primary_contrast_mae'] for name, value in evaluation['scores'].items()},
        gains=evaluation['gains'], decision=evaluation['decision'],
        target_stock=dict(statistic=stock['statistic'], p_value=stock['p_value'], passed=stock['passed']),
        qualifications=[
            'Locally frozen retrospective analysis; published aggregate diffusivities and qualitative outcomes known',
            'Effective conductance transfers across four earlier and four later membranes; method, date and batch confounded',
            'Compartment volume is the reference measure; neither log-orthopolic nor linear-orthopolic size allocation',
            'Five standards per run do not establish independent common Gaussian optical errors',
            'Broad finite-rate confidence sets; non-rejection of the stock test is not proof of conservation',
            'Negative baseline estimates retained; source-derived concentrations and post-experiment geometry unused',
            'Sequential sampling timing and temporary volume differences remain approximated',
            'Ordinary diffusion predicts the same trajectories; no unique orthopolity mechanism established'],
        conclusion='Fixed exchange-model transfer and all predeclared benchmarks evaluated on four later pairs; separate stock and uncertainty diagnostics retained')
    source_directory = (ROOT / cfg['source']).parent
    entry = dict(schema_version=1, run_id=cfg['study'], evidence_kind='actual_measurement',
        resources=[dict(name='Dissolved dye amount and membrane exchange between equal-volume compartments',
            units='Raw absorbance; nominal micromolar standards; mL; inferred conductance in mL/hour',
            definition=cfg['reference_measure'])],
        data_inputs=[file_reference(ROOT, p.relative_to(ROOT).as_posix(), role='Public source or qualification receipt')
                     for p in sorted(source_directory.iterdir()) if p.is_file()],
        configs=[archive_reference(ROOT, CONFIG)],
        algorithms=[dict(name='Frozen exchange transfer with independent polynomial, ODE and complex-step verification',
            sources=[archive_reference(ROOT, name) for name in dict.fromkeys(sources)])],
        artifacts=[file_reference(ROOT, p.relative_to(ROOT).as_posix())
                   for directory in (QUALIFICATION, FORECAST, RESULT)
                   for p in sorted((ROOT / directory).iterdir()) if p.is_file()],
        generated_seeds=dict(generated_empirical_data=False, randomized_analysis=False),
        hardware_metadata=dict(python=sys.version, numpy=np.__version__, platform=platform.platform(),
                               runtime_thread_count_verified=False),
        relationships=[], summary=summary)
    print(json.dumps(register_run(ROOT, entry), indent=2))
    if not registry.read_bytes().startswith(prior):
        raise ValueError('Earlier registry bytes changed')
    print(json.dumps(verify_registry(ROOT), indent=2))


if __name__ == '__main__':
    main()
