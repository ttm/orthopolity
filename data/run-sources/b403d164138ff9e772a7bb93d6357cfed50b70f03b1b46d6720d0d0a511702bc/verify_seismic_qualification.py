"""Audit retained eligibility with the original range rule, without fitting responses."""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist

from fetch_seismic_qualification import digest, verify
from run_volumetric_b import completeness, coordinates, fit_range

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT/'results/seismic-qualification-2026-10-10'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, default=DIRECTORY)
    args = parser.parse_args()
    directory = args.directory
    sources = verify()
    config_path = ROOT/'configs/seismic_qualification_2026-10-10.json'
    config = json.loads(config_path.read_text())
    result = json.loads((directory/'result.json').read_text())
    events = pd.read_csv(directory/'event-selection.csv', float_precision='round_trip')
    ledger = pd.read_csv(directory/'cluster-ledger.csv', float_precision='round_trip').set_index('cluster')
    details = {r['cluster']: r for r in json.loads((directory/'range-details.json').read_text())}
    assert digest(config_path) == result['config_sha256']
    assert not events.event_id.duplicated().any() and not ledger.index.duplicated().any()
    assert len(events) == result['n_published_events']
    assert len(ledger) == result['n_published_clusters']
    quality = ((events.location_method == 'ct') & events.event_type.isin(['le', 'eq'])
               & events.abs_horizontal_error_km.between(0, 99, inclusive='neither')
               & events.abs_vertical_error_km.between(0, 99, inclusive='neither'))
    assert (quality == events.quality_pass).all()
    errors = np.hypot(events.abs_horizontal_error_km, events.abs_vertical_error_km)
    np.testing.assert_allclose(errors, events.loc_err_km, rtol=0, atol=1e-12)
    assert int(quality.sum()) == result['n_quality_events']
    expected_complete, expected_sampled = set(), set()
    qualified, checked_mc, checked_range, capped = [], 0, 0, 0
    max_range_difference = 0.
    for cluster, group in events.groupby('cluster', sort=True):
        record = ledger.loc[cluster]
        clean = group[group.quality_pass].copy()
        assert len(group) == record.n_raw and len(clean) == record.n_quality
        if len(group) < 200 or len(clean) < 200:
            assert not record.eligible and cluster not in details
            continue
        clean['_key'] = clean.event_id.astype(str)
        clean = clean.sort_values('_key', kind='stable')
        mc = max(2., completeness(clean.mag.to_numpy()))
        assert mc == record.mc == details[cluster]['mc']
        complete = clean[np.round(clean.mag.to_numpy(), 1) >= mc-1e-9]
        assert len(complete) == record.n_complete
        expected_complete.update(complete.event_id)
        checked_mc += 1
        if len(complete) < 200:
            assert not record.eligible and not details[cluster]['sampled_event_ids']
            continue
        indices = np.arange(len(complete))
        if len(complete) > 3000:
            rng = np.random.default_rng(np.random.SeedSequence([config['seed'], int(cluster)]))
            indices = np.sort(rng.choice(len(complete), 3000, replace=False))
            capped += 1
        sampled = complete.iloc[indices]
        assert sampled.event_id.astype(str).tolist() == details[cluster]['sampled_event_ids']
        expected_sampled.update(sampled.event_id)
        assert len(sampled) == record.n_sampled
        # Call only the original coordinate conversion and interval calculation.
        # Neither correlation_dimension nor any magnitude-response estimator is called.
        pairs = pdist(coordinates(complete)[indices])
        positive = np.sort(pairs[pairs > 0])
        error = float(complete.loc_err_km.median())
        lo, hi = fit_range(positive, error)
        difference = max(abs(lo-record.r_min_km), abs(hi-record.r_max_km))
        max_range_difference = max(max_range_difference, difference)
        assert difference < 1e-10
        assert abs(error-record.median_location_error_km) < 1e-12
        assert abs(hi/lo-record.scaling_ratio) < 1e-10
        assert abs(hi/positive[199]-record.geometry_only_ratio) < 1e-9
        counts = complete.groupby(['relocation_box', 'waveform_cluster'], dropna=False).size()
        assert len(counts) == record.n_waveform_components_complete
        assert abs(counts.max()/len(complete)-record.largest_waveform_component_fraction) < 1e-12
        eligible = hi >= 3*lo
        assert bool(eligible) == bool(record.eligible)
        if eligible:
            qualified.append(int(cluster))
        checked_range += 1
    assert (events.complete_for_qualification == events.event_id.isin(expected_complete)).all()
    assert (events.sampled_for_range == events.event_id.isin(expected_sampled)).all()
    for field, column in [('n_clusters_at_least_200_raw', 'n_raw'),
                          ('n_clusters_at_least_200_quality', 'n_quality'),
                          ('n_clusters_at_least_200_complete', 'n_complete')]:
        assert int((ledger[column] >= 200).sum()) == result[field]
    assert qualified == result['qualified_cluster_ids']
    assert len(qualified) == result['n_resolution_qualified_clusters'] < result['minimum_clusters']
    assert not result['b_D2_or_regression_computed']
    verification = dict(source_verification=sources, unique_event_ids=True,
        event_quality_and_selection_flags_verified=len(events), cluster_counts_verified=len(ledger),
        completeness_checks_against_original=checked_mc,
        range_checks_against_original=checked_range, capped_samples_replayed=capped,
        maximum_range_bound_difference_km=max_range_difference,
        qualified_cluster_ids=qualified, b_D2_or_regression_computed=False,
        outcome='All retained selection and qualification checks pass')
    (directory/'verification.json').write_text(json.dumps(verification, indent=2)+'\n')
    print(json.dumps(verification, indent=2))


if __name__ == '__main__':
    main()
