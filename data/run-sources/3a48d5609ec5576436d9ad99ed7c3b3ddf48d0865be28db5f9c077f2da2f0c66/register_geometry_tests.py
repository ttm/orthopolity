"""Append the 9 October flare/global-lake/regional-lake analyses to the registry.

Large HydroLAKES geometries are externally restorable. The registry retains their
acquisition digest and exact selected fitting table; fetch_hydrolakes.py verifies
the large source separately. Existing records are never replaced.
"""
import json
from pathlib import Path

from orthopolity.run_registry import archive_reference, file_reference, register_run, verify_registry

ROOT = Path(__file__).resolve().parents[1]


def register(name, title, resource, configs, algorithms, inputs, seeds, qualification, relationships=None):
    directory = Path('results') / name
    result = json.loads((ROOT / directory / 'result.json').read_text())
    execution = json.loads((ROOT / directory / 'execution.json').read_text())
    entry = dict(
        schema_version=1, run_id=name, evidence_kind='actual_measurement',
        resources=[dict(name=title, definition=resource, units='Area in cm^2 for flare ribbons; radius in km and dimensionless survival exponent for lakes')],
        data_inputs=[file_reference(ROOT, path) for path in inputs],
        configs=[archive_reference(ROOT, path) for path in configs],
        algorithms=[dict(name=title, sources=[archive_reference(ROOT, path) for path in
                    algorithms + ['experiments/register_geometry_tests.py']])],
        artifacts=[file_reference(ROOT, path.relative_to(ROOT).as_posix())
                   for path in sorted((ROOT / directory).iterdir()) if path.is_file()],
        generated_seeds=seeds,
        hardware_metadata=dict(runtime={key: execution[key] for key in
                               ['python', 'numpy', 'scipy', 'platform'] if key in execution},
                               cpu_model=None, total_ram_bytes=None, runtime_thread_count_verified=False),
        relationships=relationships or [],
        summary=dict(result=result, qualification=qualification,
                     inference_scope='Reanalysis of public observations; local protocol/source freeze, not external registration'),
    )
    return register_run(ROOT, entry)


def main():
    flare = 'results/flare-ribbons-2026-10-09/implementation/'
    lake = 'results/lake-gyration-2026-10-09/implementation/'
    entries = [register(
        'flare-ribbons-2026-10-09', 'Ribbon area and magnetic-flux exponent comparison',
        'Cumulative observed ribbon area per flare; proposed equal-area allocation per logarithmic area class; reconnection flux secondary',
        [flare+'configs/prereg_2026-10-08_flare_ribbons.json', 'results/flare-ribbons-2026-10-09/before-run.json'],
        [flare+'experiments/run_flare_ribbons.py', flare+'src/gof.py'],
        ['data/dataset-audit/2026-10-09/flare/ribbondb_v1.0.csv',
         'data/dataset-audit/2026-10-09/flare/ribbondb_v1.0.csv.receipt.json'],
        dict(seed=20261008, derivation='Original script: 2000 bootstrap draws; 500 GOF draws'),
        'Both area predictions excluded by original iid interval; registered rule says inconclusive. Bounded GOF support differs from primary unbounded fit; active-region dependence unmodelled.'),
        register(
        'lake-gyration-2026-10-09', 'Global projected lake-radius exponent',
        'Area-weighted largest-ring radius in EPSG6933, compared across log-radius classes with territory prediction zeta=2',
        [lake+'configs/prereg_2026-10-08_lake_gyration.json',
         'docs/lake-gyration-run-plan-2026-10-09.md', 'results/lake-gyration-2026-10-09/encoding-amendment.json'],
        [lake+'experiments/run_lake_gyration_latin1.py', lake+'src/gof.py', 'experiments/fetch_hydrolakes.py'],
        ['data/hydrolakes/2026-10-09/acquisition.json', 'data/hydrolakes/2026-10-09/schema.json',
         'results/lake-gyration-2026-10-09/selected-lakes.csv'],
        dict(seed=20261008, derivation='Original 1000 iid and 500 unregistered Country resamples'),
        'Iid interval lies in equivalence band; Country interval does not. Basin interval absent, projection-dependent geometry and no adequacy gate. Registry verifies retained fit table/manifests; full 820MB archive is ignored and must be verified separately.'),
        register(
        'uk-lake-gyration-2026-10-09', 'Regional full-polygon lake-radius exponent',
        'Area-weighted full-multipolygon radius including holes in EPSG27700; proposed territory allocation per log-radius class',
        ['configs/uk_lake_gyration_2026-10-09.json', 'docs/uk-lake-gyration-protocol-2026-10-09.md'],
        ['experiments/run_uk_lake_gyration.py', 'src/orthopolity/lake_geometry.py',
         'src/orthopolity/goodness_of_fit.py', 'tests/test_lake_geometry.py'],
        ['data/dataset-audit/2026-10-09/lakes/uklakes_v3_6_poly.gpkg',
         'data/dataset-audit/2026-10-09/lakes/ukceh_receipt.json'],
        dict(seed=20261009, derivation='Independent SeedSequence streams; 1000 iid, 1000 fixed-grid and 1000 GOF draws'),
        'Either-interval rule calls a departure, but the spatial interval includes 2: not a spatially robust rejection. Regional and global inventories can overlap.',
        [dict(type='regional_comparison_of', run_id='lake-gyration-2026-10-09')])]
    print(json.dumps(dict(registered=[entry['run_id'] for entry in entries], audit=verify_registry(ROOT)), indent=2))


if __name__ == '__main__':
    main()
