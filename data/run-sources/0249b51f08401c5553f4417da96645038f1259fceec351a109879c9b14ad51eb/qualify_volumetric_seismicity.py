"""Apply frozen source, quality, completeness and resolution gates; no b or D2.

The protocol/config must be committed before execution. Source restoration is
separate; this analysis makes no network requests and never relaxes its gates.
"""
import argparse
import json
from pathlib import Path
import platform
import sys
import time
from datetime import datetime, timezone

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from orthopolity.seismic_catalogue import load_published, load_relocations
from orthopolity.seismic_qualification import qualify_cluster
from fetch_seismic_qualification import digest, verify

CONFIG_PATH = ROOT/'configs/seismic_qualification_2026-10-10.json'
CONFIG = json.loads(CONFIG_PATH.read_text())


def join_sources(published, relocated):
    """Validate the whole published cohort before any quality or outcome cut."""
    columns = ['event_id', 'latitude', 'longitude', 'depth_km', 'mag',
               'event_type', 'location_method', 'abs_horizontal_error_km', 'abs_vertical_error_km',
               'rel_horizontal_error_km', 'rel_vertical_error_km', 'waveform_cluster',
               'waveform_cluster_size', 'relocation_box']
    merged = published.merge(relocated[columns], on='event_id', how='left',
                             validate='one_to_one', suffixes=('', '_relocated'), indicator=True)
    if not (merged['_merge'] == 'both').all():
        raise ValueError('Published event absent from the matching source; no selective omissions')
    differences = {}
    for column, tolerance in [('latitude', .000005), ('longitude', .000005), ('depth_km', .0005), ('mag', .005)]:
        difference = np.abs(merged[column]-merged[column+'_relocated'])
        if not np.isfinite(difference).all() or (difference > tolerance).any():
            raise ValueError(f'Published {column} no longer agrees with original source')
        differences[column] = float(difference.max())
    return merged.drop(columns=['_merge']), differences


def quality_table(joined):
    """Frozen per-event criteria, retaining every source row and every reason."""
    table = joined.copy()
    conditions = {
        'not_cross_correlation_relocated': table.location_method != CONFIG['event_quality']['location_method'],
        'not_local_or_authoritative_earthquake': ~table.event_type.isin(CONFIG['event_quality']['event_types']),
        'unusable_absolute_horizontal_error': ~np.isfinite(table.abs_horizontal_error_km) | (table.abs_horizontal_error_km <= 0) | (table.abs_horizontal_error_km >= 99),
        'unusable_absolute_vertical_error': ~np.isfinite(table.abs_vertical_error_km) | (table.abs_vertical_error_km <= 0) | (table.abs_vertical_error_km >= 99),
    }
    table['quality_pass'] = ~np.column_stack(list(conditions.values())).any(axis=1)
    table['quality_reasons'] = [';'.join(name for name, mask in conditions.items() if mask.iloc[i])
                                for i in range(len(table))]
    table['cluster'] = table.published_cluster.astype(np.int64)
    table['loc_err_km'] = np.hypot(table.abs_horizontal_error_km, table.abs_vertical_error_km)
    table['complete_for_qualification'] = False
    table['sampled_for_range'] = False
    counts = {name: int(mask.sum()) for name, mask in conditions.items()}
    return table, counts


def analyse(table, directory):
    ledger, detailed, complete_ids, sampled_ids = [], [], set(), set()
    for cluster, group in table.groupby('cluster', sort=True):
        quality = group[group.quality_pass].copy()
        record = dict(cluster=int(cluster), n_raw=len(group), n_quality=len(quality),
                      eligible=False, n_complete=None, n_sampled=None, mc=None,
                      median_location_error_km=None, pair_floor_km=None, error_floor_km=None,
                      pair_q90_km=None, geometry_only_ratio=None, r_min_km=None,
                      r_max_km=None, scaling_ratio=None, n_waveform_components_complete=None,
                      largest_waveform_component_fraction=None)
        if len(group) < CONFIG['minimum_complete_events']:
            record['reason'] = 'fewer_than_200_raw_events'
        elif len(quality) < CONFIG['minimum_complete_events']:
            record['reason'] = 'fewer_than_200_quality_events'
        else:
            audit = qualify_cluster(quality, np.random.SeedSequence([CONFIG['seed'], int(cluster)]))
            for key in list(record):
                if key in audit:
                    record[key] = audit[key]
            record['reason'] = ';'.join(audit['reasons']) or 'qualified'
            if audit['mc'] is not None:
                complete = quality[np.round(quality.mag.to_numpy(), 1) >= audit['mc']-1e-9]
                complete_ids.update(complete.event_id)
                if len(complete):
                    counts = complete.groupby(['relocation_box', 'waveform_cluster'], dropna=False).size()
                    record['n_waveform_components_complete'] = int(len(counts))
                    record['largest_waveform_component_fraction'] = float(counts.max()/len(complete))
            sampled_ids.update(int(value) for value in audit['sampled_event_ids'])
            detailed.append(dict(cluster=int(cluster), **audit))
        ledger.append(record)
    table['complete_for_qualification'] = table.event_id.isin(complete_ids)
    table['sampled_for_range'] = table.event_id.isin(sampled_ids)
    columns = ['event_id', 'event_index', 'cluster', 'year', 'month', 'day', 'hour', 'minute',
               'second', 'clock_fields_valid', 'latitude', 'longitude', 'depth_km', 'mag',
               'event_type', 'location_method', 'abs_horizontal_error_km', 'abs_vertical_error_km',
               'rel_horizontal_error_km', 'rel_vertical_error_km', 'loc_err_km', 'waveform_cluster',
               'relocation_box', 'quality_pass', 'quality_reasons', 'complete_for_qualification', 'sampled_for_range']
    table[columns].sort_values('event_id').to_csv(directory/'event-selection.csv', index=False)
    frame = pd.DataFrame(ledger)
    frame.to_csv(directory/'cluster-ledger.csv', index=False)
    (directory/'range-details.json').write_text(json.dumps(detailed, indent=2, allow_nan=False)+'\n')
    n_eligible = int(frame.eligible.sum())
    out = dict(n_published_events=len(table), n_published_clusters=len(frame),
        n_quality_events=int(table.quality_pass.sum()),
        n_clusters_at_least_200_raw=int((frame.n_raw >= 200).sum()),
        n_clusters_at_least_200_quality=int((frame.n_quality >= 200).sum()),
        n_clusters_at_least_200_complete=int((frame.n_complete >= 200).sum()),
        n_resolution_qualified_clusters=n_eligible,
        minimum_clusters=CONFIG['minimum_clusters'],
        n_geometrically_possible_ignoring_error=int((frame.geometry_only_ratio >= 3).sum()),
        qualification_reasons={str(k): int(v) for k, v in frame.reason.value_counts().items()},
        qualified_cluster_ids=frame.loc[frame.eligible, 'cluster'].tolist(),
        b_D2_or_regression_computed=False,
        verdict='inconclusive (too few resolution-qualified clusters)' if n_eligible < CONFIG['minimum_clusters'] else 'qualified for response execution; no hypothesis verdict yet',
        inference='Eligibility assessment only. Failure cannot favour b=D2/2 or b=1. Preferred magnitudes and magnitude-dependent published clustering further qualify any later physical interpretation.')
    ranged = frame[frame.scaling_ratio.notna()]
    if len(ranged):
        out['resolution_diagnostics'] = dict(
            largest_scaling_ratio=float(ranged.scaling_ratio.max()),
            median_absolute_error_range_km=[float(ranged.median_location_error_km.min()), float(ranged.median_location_error_km.max())],
            all_ranged_sequences_span_multiple_waveform_components=bool((ranged.n_waveform_components_complete > 1).all()))
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'build/reproductions/seismic-qualification')
    args = parser.parse_args()
    start = time.monotonic()
    verification = verify()
    print(json.dumps(verification), flush=True)
    published = load_published(ROOT/CONFIG['published_catalogue'])
    relocated = load_relocations(ROOT/CONFIG['matching_relocations'])
    joined, differences = join_sources(published, relocated)
    table, quality_reasons = quality_table(joined)
    args.output.mkdir(parents=True, exist_ok=True)
    result = dict(config_sha256=digest(CONFIG_PATH), source_verification=verification,
                  max_join_differences=differences,
                  n_invalid_published_clock_fields=int((~published.clock_fields_valid).sum()),
                  n_original_relocation_events=len(relocated), event_quality_exclusion_counts=quality_reasons,
                  **analyse(table, args.output))
    (args.output/'result.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    import scipy
    execution = dict(completed_utc=datetime.now(timezone.utc).isoformat(), seconds=time.monotonic()-start,
                     python=platform.python_version(), platform=platform.platform(), numpy=np.__version__,
                     pandas=pd.__version__, scipy=scipy.__version__)
    (args.output/'execution.json').write_text(json.dumps(execution, indent=2)+'\n')
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
