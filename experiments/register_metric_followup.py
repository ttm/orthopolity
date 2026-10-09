"""Append the locally frozen metric/basin follow-up; never replace prior runs."""
import json
from pathlib import Path

from orthopolity.run_registry import archive_reference, file_reference, register_run, verify_registry

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = Path('results/lake-metric-followup-2026-10-09')


def main():
    result = json.loads((ROOT/DIRECTORY/'result.json').read_text())
    execution = json.loads((ROOT/DIRECTORY/'execution.json').read_text())
    config_paths = ['configs/lake_metric_followup_2026-10-09.json',
                    'docs/lake-metric-followup-protocol-2026-10-09.md']
    # Dated amendments, if any, are explicit artifacts alongside the result.
    sources = ['experiments/run_lake_metric_followup.py',
               'src/orthopolity/geodesic_lake_geometry.py',
               'src/orthopolity/lake_followup_statistics.py',
               'src/orthopolity/goodness_of_fit.py', 'experiments/fetch_hydrolakes.py',
               'experiments/fetch_hydrobasins.py', 'experiments/register_metric_followup.py',
               'experiments/verify_lake_metric_followup.py', 'tests/test_lake_metric_followup.py']
    sources.append('experiments/plot_lake_metric_comparison.py')
    entry = dict(schema_version=1, run_id=DIRECTORY.name, evidence_kind='actual_measurement',
        resources=[dict(name='Global local-metric lake radius', units='km; dimensionless survival exponent',
           definition='Area-weighted full polygon radius in per-feature WGS84 LAEA, compared with territory allocation per logarithmic radius class')],
        data_inputs=[file_reference(ROOT, p) for p in ['data/hydrolakes/2026-10-09/acquisition.json',
                      'data/hydrobasins/2026-10-09/acquisition.json',
                      'data/hydrobasins/2026-10-09/topology-audit.json',
                      'results/lake-gyration-2026-10-09/result.json',
                      (DIRECTORY/'selected-lakes.csv').as_posix()]],
        configs=[archive_reference(ROOT, p) for p in config_paths],
        algorithms=[dict(name='Local geometry and basin resampling', sources=[archive_reference(ROOT, p) for p in sources])],
        artifacts=[file_reference(ROOT, p.relative_to(ROOT).as_posix())
                   for p in sorted((ROOT/DIRECTORY).iterdir()) if p.is_file()],
        generated_seeds=dict(base_seed=202610091, draws_per_interval=1000, gof_draws=1000,
                             streams='Country/base, basin/base+1, sensitivities/base+2,+3; iid/block spawn separately; GOF/base+4'),
        hardware_metadata=dict(runtime=execution, cpu_model=None, total_ram_bytes=None,
                               runtime_thread_count_verified=False),
        relationships=[dict(type='metric_and_spatial_followup_of', run_id='lake-gyration-2026-10-09')],
        summary=dict(result=result, inference_scope='Prior outcomes known; prospective local freeze of follow-up methods; not independent confirmation',
                     source_verification='Registry retains source manifests and fitting table; ignored source archives require separate offline verifiers'))
    register_run(ROOT, entry)
    print(json.dumps(verify_registry(ROOT), indent=2))


if __name__ == '__main__':
    main()
