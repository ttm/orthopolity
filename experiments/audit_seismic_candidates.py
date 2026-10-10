"""Audit new catalogues and exact-ID calibration links without fitting b or D2."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from orthopolity.seismic_source_audit import read_class, read_horus, read_nocal, crosswalk
from fetch_seismic_candidates import verify, digest

BASE = ROOT/'data/seismic-candidates/2026-10-10'


def counts(series):
    return {str(key): int(value) for key, value in series.fillna('missing').value_counts().sort_index().items()}


def finite_summary(series):
    values = series[np.isfinite(series)].to_numpy()
    return dict(n=int(len(values)), minimum=float(values.min()) if len(values) else None,
                median=float(np.median(values)) if len(values) else None,
                maximum=float(values.max()) if len(values) else None)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'build/reproductions/seismic-candidates')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    source_check = verify()
    with zipfile.ZipFile(BASE/'raw/HORUS_Ita_Catalog.zip') as archive:
        for item in json.loads((BASE/'horus-members.json').read_text()):
            with archive.open(item['member']) as stream:
                observed = hashlib.file_digest(stream, 'sha256').hexdigest()
            assert observed == item['sha256']
            assert archive.getinfo(item['member']).file_size == item['bytes']
        assert archive.read('README.txt') == (BASE/'metadata/HORUS-README.txt').read_bytes()
    class_frame = read_class(BASE/'raw/CLASS1.0_full.csv.gz')
    catalogue = read_horus(BASE/'raw/HORUS_Ita_Catalog.zip')
    provenance = read_horus(BASE/'raw/HORUS_Ita_Catalog.zip', origin=True)
    linked = crosswalk(class_frame, catalogue, provenance)
    assert len(linked) == len(class_frame)
    complete = linked[linked.join_status == 'matched_catalogue_and_provenance']
    direct = complete[complete.has_direct_mt_provenance]
    # These are schema/availability descriptions, not chosen inference filters.
    positive_errors = (np.isfinite(complete.errh) & np.isfinite(complete.errv)
                       & (complete.errh > 0) & (complete.errv > 0))
    quality = {label: dict(n=int(len(g)), numeric_quality=finite_summary(g.qmd_num))
               for label, g in class_frame.groupby('qmd_cha', dropna=False)}
    nocal = read_nocal(BASE/'raw/NCAeqDD.v202112.1.gz')
    error_columns = ['eh_major_95_km', 'eh_minor_95_km', 'ev_95_km']
    nocal_errors = nocal[error_columns]
    all_positive_errors = np.isfinite(nocal_errors).all(axis=1) & (nocal_errors > 0).all(axis=1)
    structural = dict(
        scope='Source structure and exact-ID compatibility audit, not a qualified seismic cohort',
        source_verification=source_check, horus_archive_members_verified=5,
        class_catalogue=dict(n_rows=len(class_frame),
            time_range=[class_frame.origintime.min(), class_frame.origintime.max()],
            duplicate_class_id_rows=int(linked.ambiguous_class_id.sum()),
            duplicate_positive_ingv_id_rows=int(linked.ambiguous_ingv_id.sum()),
            missing_ingv_id_rows=int(class_frame.id_ingv.isna().sum()),
            magnitude_type_counts=counts(class_frame.magnitude_class_type),
            preferred_ingv_magnitude_type_counts=counts(class_frame.magnitude_ingv_pref_type),
            quality_classes=quality,
            quality_documentation_caveat='Observed A:0..0.25 through D:0.75..1 matches the page narrative, while its qmd_num field description reverses the direction. Preserve letter classes; no numerical-quality eligibility cut selected.'),
        horus=dict(n_catalogue_rows=len(catalogue), n_provenance_rows=len(provenance),
            year_range=[int(catalogue.Year.min()), int(catalogue.Year.max())],
            n_catalogue_positive_ids=int(catalogue.event_id.notna().sum()),
            n_provenance_positive_ids=int(provenance.event_id.notna().sum()),
            n_duplicate_catalogue_id_rows=int((catalogue.event_id.notna() & catalogue.event_id.duplicated(False)).sum()),
            n_duplicate_provenance_id_rows=int((provenance.event_id.notna() & provenance.event_id.duplicated(False)).sum()),
            variant='Original input (_o); no random magnitude decimal jitter'),
        crosswalk=dict(status_counts=counts(linked.join_status),
            n_matched_catalogue_and_provenance=len(complete),
            n_direct_mt_provenance=len(direct), n_proxy_provenance=int(complete.has_proxy_provenance.sum()),
            n_missing_magnitude_provenance=int((~complete.has_direct_mt_provenance & ~complete.has_proxy_provenance).sum()),
            direct_mt_maximum_disjoint_200_event_groups=len(direct)//200,
            direct_mt_bound_caveat='Upper bound before completeness, quality, sequence independence and resolution; not a cluster count',
            n_positive_finite_location_errors=int(positive_errors.sum()),
            n_letters_A_or_B_and_positive_errors=int((complete.qmd_cha.isin(['A','B']) & positive_errors).sum()),
            n_direct_mt_letters_A_or_B=int(direct.qmd_cha.isin(['A','B']).sum()),
            final_provenance_counts=counts(complete.final_source),
            n_horus_non_earthquake_flag=int(complete.horus_event_type.eq('x').sum()),
            non_earthquake_flag_caveat='HORUS records this flag only since May 2012; blank before then is not a verified earthquake classification',
            class_horus_absolute_time_difference_s=finite_summary(complete.class_horus_time_difference_s.abs()),
            n_class_horus_time_difference_above_60s=int((complete.class_horus_time_difference_s.abs() > 60).sum()),
            n_invalid_class_or_horus_times=int(complete.class_horus_time_difference_s.isna().sum()),
            n_horus_provenance_time_disagreements=int((complete.horus_provenance_time_difference_s.abs() > 1e-6).sum()),
            n_invalid_horus_or_provenance_times=int(complete.horus_provenance_time_difference_s.isna().sum()),
            n_horus_provenance_mw_difference_above_half_cent=int((complete.horus_provenance_mw_difference.abs() > .00500001).sum()),
            horus_provenance_mw_absolute_difference=finite_summary(complete.horus_provenance_mw_difference.abs())),
        northern_california=dict(n_rows=len(nocal), n_unique_event_ids=int(nocal.event_id.nunique()),
            year_range=[int(nocal.year.min()), int(nocal.year.max())],
            n_all_positive_finite_relative_error_fields=int(all_positive_errors.sum()),
            n_any_missing_negative_or_zero_error=int((~all_positive_errors).sum()),
            n_negative_depth=int((nocal.depth_km < 0).sum()),
            error_confidence='95 percent relative-location ellipses and vertical errors; not converted to absolute or one-sigma precision',
            magnitude='Publisher documents NCSN ML, not a homogeneous Mw scale',
            physical_sequence_labels=False),
        fitted_responses=dict(completeness=False, b=False, D2=False, regression=False),
        next_design='CLASS/HORUS offers documented absolute location errors and independent magnitude calibration, but requires duplicate reconciliation, justified physical sequence labels and validation of proxy-magnitude uncertainty/rounding before registered response fitting.')
    columns = ['class_source_row','id_class','id_ingv','origintime','latitude','longitude','depth',
        'errh','errv','qmd_cha','qmd_num','magnitude_class','magnitude_class_type',
        'magnitude_ingv_pref','magnitude_ingv_pref_type','ambiguous_class_id','ambiguous_ingv_id',
        'join_status','horus_source_row','provenance_source_row','horus_time','horus_mw',
        'horus_sigma_mw','horus_event_type','mt_source','mt_mw','mt_error',
        'final_source','final_mw','final_error','has_direct_mt_provenance','has_proxy_provenance',
        'class_horus_time_difference_s','horus_provenance_time_difference_s','horus_provenance_mw_difference']
    table_path = args.output/'class-horus-crosswalk.csv.gz'
    linked[columns].to_csv(table_path, index=False, compression={'method':'gzip','mtime':0})
    linked[linked.ambiguous_class_id | linked.ambiguous_ingv_id][columns].to_csv(
        args.output/'class-identifier-collisions.csv', index=False)
    # A human-readable identity diagnostic only, not a new inclusion threshold.
    linked[linked.class_horus_time_difference_s.abs() > 60][columns].to_csv(
        args.output/'class-horus-time-discrepancies.csv', index=False)
    yearly = linked.assign(year=linked.origintime.str[:4]).groupby(['year','join_status']).size()
    yearly.rename('n').reset_index().to_csv(args.output/'crosswalk-by-year.csv', index=False)
    structural['crosswalk_sha256'] = digest(table_path)
    (args.output/'audit.json').write_text(json.dumps(structural, indent=2, allow_nan=False)+'\n')
    print(json.dumps(structural, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
