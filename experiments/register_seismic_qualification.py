"""Append the frozen earthquake eligibility assessment, retaining all earlier runs."""
import json
from pathlib import Path

from orthopolity.run_registry import archive_reference, file_reference, register_run, verify_registry

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = Path('results/seismic-qualification-2026-10-10')


def main():
    result = json.loads((ROOT/DIRECTORY/'result.json').read_text())
    execution = json.loads((ROOT/DIRECTORY/'execution.json').read_text())
    configs = ['configs/prereg_2026-10-08_volumetric_seismicity.json',
               'configs/seismic_qualification_2026-10-10.json',
               'docs/seismic-qualification-protocol-2026-10-10.md']
    sources = ['src/orthopolity/seismic_catalogue.py', 'src/orthopolity/seismic_qualification.py',
               'experiments/qualify_volumetric_seismicity.py', 'experiments/fetch_seismic_qualification.py',
               'experiments/verify_seismic_qualification.py', 'experiments/plot_seismic_qualification.py',
               'experiments/register_seismic_qualification.py', 'experiments/run_volumetric_b.py',
               'tests/test_seismic_catalogue.py', 'tests/test_seismic_qualification.py',
               'tests/test_seismic_qualification_runner.py']
    inputs = ['data/seismic-regional/2026-10-09/acquisition.json',
              'data/seismic-regional/2026-10-09/ZBZ_JGR2020_data_description.txt',
              'data/seismic-regional/2026-10-09/hs_1981_2011_catalog_v01.format']
    entry = dict(schema_version=1, run_id=DIRECTORY.name, evidence_kind='actual_measurement',
        resources=[dict(name='Earthquake hypocentre support resolution',
                        units='km; counts; preferred catalogue magnitude',
                        definition='Eligibility for a comparison of log-orthopolic territory allocation with b=1; no resource-response exponent estimated')],
        data_inputs=[file_reference(ROOT, path) for path in inputs],
        configs=[archive_reference(ROOT, path) for path in configs],
        algorithms=[dict(name='Fixed published membership, quality, completeness and resolution gates',
                         sources=[archive_reference(ROOT, path) for path in sources])],
        artifacts=[file_reference(ROOT, path.relative_to(ROOT).as_posix())
                   for path in sorted((ROOT/DIRECTORY).iterdir()) if path.is_file()],
        generated_seeds=dict(base_seed=202610092, streams='SeedSequence([base_seed, published_cluster_id])',
                             use='Hypocentre cap only; no bootstrap or response fitting'),
        hardware_metadata=dict(runtime=execution, cpu_model=None, total_ram_bytes=None,
                               runtime_thread_count_verified=False),
        relationships=[],
        summary=dict(result=result, protocol_commit='6ae7a8c',
                     inference_scope='Eligibility finding only; six qualified sequences fail the registered minimum ten; neither physical hypothesis is favoured',
                     source_verification='Full ignored raw files are pinned in acquisition.json and require the separate offline source verifier'))
    print(json.dumps(register_run(ROOT, entry), indent=2))
    print(json.dumps(verify_registry(ROOT), indent=2))


if __name__ == '__main__':
    main()
