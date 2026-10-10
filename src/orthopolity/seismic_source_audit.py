"""Source identity and magnitude provenance audit; no seismic response estimators."""
import gzip
import zipfile

import numpy as np
import pandas as pd

CLASS_COLUMNS = ('id_class id_ingv origintime latitude longitude depth magnitude_class '
    'magnitude_class_type magnitude_ingv_loc magnitude_ingv_loc_type magnitude_ingv_pref '
    'magnitude_ingv_pref_type rms errh errv nphs gap mindist pdfray locd qmd_cha qmd_num id').split()
TIME_COLUMNS = ['Year', 'Mo', 'Da', 'Ho', 'Mi', 'Se']
CATALOG_HEADER = TIME_COLUMNS + ['Lat', 'Lon', 'Depth', 'Mw', 'sigMw', 'Geo-Ita',
                                'Geo-CPTI15', 'Ev. type', 'Iside n.', '']
ORIGIN_HEADER = TIME_COLUMNS + ['Lat', 'Lon', 'Depth'] + [
    'source', 'ML-CSI', 'er', 'source', 'Ma', 'er', 'source', 'Md', 'er',
    'source', 'ML', 'er', 'source', 'Mw-MT', 'er', 'source', 'MI', 'er',
    'source', 'Mw/Mpry', 'er', 'Italia', 'CPTI15', 'ISIDe nr.', 'Ev. type', '']
ORIGIN_NAMES = TIME_COLUMNS + ['Lat', 'Lon', 'Depth'] + [
    'ml_csi_source', 'ml_csi', 'ml_csi_error', 'ma_source', 'ma', 'ma_error',
    'md_source', 'md', 'md_error', 'ml_source', 'ml', 'ml_error',
    'mt_source', 'mt_mw', 'mt_error', 'mi_source', 'mi', 'mi_error',
    'final_source', 'final_mw', 'final_error', 'Italia', 'CPTI15', 'event_id', 'event_type', 'empty']


def positive_ids(values):
    """Zero and blanks are absent IDs; invalid/nonintegral IDs must not silently join."""
    numeric = pd.to_numeric(values.replace(r'^\s*$', np.nan, regex=True), errors='raise')
    present = numeric.notna()
    if (~np.isfinite(numeric[present])).any() or (numeric[present] < 0).any() or (numeric[present] % 1 != 0).any():
        raise ValueError('Event identifiers must be nonnegative finite integers or missing')
    return numeric.where(numeric > 0).astype('Int64')


def read_class(path):
    frame = pd.read_csv(path, sep=';', na_values='NULL')
    if frame.columns.tolist() != CLASS_COLUMNS:
        raise ValueError('Unexpected CLASS schema')
    frame.insert(0, 'class_source_row', np.arange(2, len(frame)+2))
    frame['id_class'] = positive_ids(frame.id_class)
    frame['id_ingv'] = positive_ids(frame.id_ingv)
    return frame


def read_horus(path, origin=False):
    member = 'HORUS_Ita_DataOrigin_o.txt' if origin else 'HORUS_Ita_Catalog_o.txt'
    expected = ORIGIN_HEADER if origin else CATALOG_HEADER
    names = ORIGIN_NAMES if origin else TIME_COLUMNS + ['Lat', 'Lon', 'Depth', 'Mw', 'sigMw',
                'Geo-Ita', 'Geo-CPTI15', 'event_type', 'event_id', 'empty']
    keep = TIME_COLUMNS + ['Lat', 'Lon', 'Depth', 'event_id', 'event_type']
    keep += ['mt_source', 'mt_mw', 'mt_error', 'final_source', 'final_mw', 'final_error'] if origin else ['Mw', 'sigMw']
    with zipfile.ZipFile(path) as archive, archive.open(member) as stream:
        header = stream.readline().decode('ascii').rstrip('\r\n').split('\t')
        if header != expected:
            raise ValueError(f'Unexpected HORUS schema in {member}')
        frame = pd.read_csv(stream, sep='\t', names=names, usecols=keep,
                            skipinitialspace=True, low_memory=False)
    for column in ['event_type'] + (['mt_source', 'final_source'] if origin else []):
        frame[column] = frame[column].fillna('').astype(str).str.strip()
    frame['event_id'] = positive_ids(frame.event_id)
    frame.insert(0, 'source_row', np.arange(2, len(frame)+2))
    return frame


def source_times(frame):
    """Flag invalid clocks rather than silently carrying minute/second 60 forward."""
    fields = frame[TIME_COLUMNS].astype(float)
    integral = (fields[TIME_COLUMNS[:-1]] % 1 == 0).all(axis=1)
    clock_ok = integral & fields.Ho.between(0, 23) & fields.Mi.between(0, 59) & fields.Se.between(0, 60, inclusive='left')
    day = pd.to_datetime(dict(year=fields.Year, month=fields.Mo, day=fields.Da), errors='coerce', utc=True)
    seconds = fields.Ho*3600 + fields.Mi*60 + fields.Se
    return (day + pd.to_timedelta(seconds, unit='s')).where(clock_ok)


def unique_positive(frame, key):
    """Quarantine every occurrence of an ambiguous identifier, never keep-first."""
    present = frame[key].notna()
    return frame.loc[present & ~frame[key].duplicated(keep=False)].copy()


def crosswalk(class_frame, catalogue, provenance):
    """Retain every CLASS row and attach only unambiguous positive-ID matches.

    This establishes source compatibility, not a physical event/quality selection.
    Both advertised CLASS IDs are checked because duplicates can have different
    alternate identifiers. Source differences remain visible, not harmonized.
    """
    rows = class_frame.copy()
    rows['ambiguous_class_id'] = rows.id_class.notna() & rows.id_class.duplicated(keep=False)
    rows['ambiguous_ingv_id'] = rows.id_ingv.notna() & rows.id_ingv.duplicated(keep=False)
    rows['join_id'] = rows.id_ingv.mask(rows.ambiguous_class_id | rows.ambiguous_ingv_id)
    cat = unique_positive(catalogue, 'event_id')
    prov = unique_positive(provenance, 'event_id')
    cat['horus_time'] = source_times(cat)
    prov['provenance_time'] = source_times(prov)
    cat = cat.rename(columns={'event_id': 'join_id', 'source_row': 'horus_source_row',
        'Lat': 'horus_latitude', 'Lon': 'horus_longitude', 'Depth': 'horus_depth_km',
        'Mw': 'horus_mw', 'sigMw': 'horus_sigma_mw', 'event_type': 'horus_event_type'})
    prov = prov.rename(columns={'event_id': 'join_id', 'source_row': 'provenance_source_row',
                                'event_type': 'provenance_event_type'})
    rows = rows.merge(cat.drop(columns=TIME_COLUMNS), on='join_id', how='left', validate='many_to_one')
    rows = rows.merge(prov.drop(columns=TIME_COLUMNS+['Lat', 'Lon', 'Depth']),
                      on='join_id', how='left', validate='many_to_one')
    rows['join_status'] = np.select([
        rows.id_ingv.isna(), rows.ambiguous_class_id | rows.ambiguous_ingv_id,
        rows.horus_source_row.isna(), rows.provenance_source_row.isna()],
        ['missing_ingv_id', 'ambiguous_class_identifiers', 'no_unique_horus_match',
         'no_unique_provenance_match'], default='matched_catalogue_and_provenance')
    rows['has_direct_mt_provenance'] = (rows.mt_mw.notna() & rows.mt_source.fillna('').ne('')
        & rows.final_source.fillna('').str.startswith('Mw '))
    rows['has_proxy_provenance'] = (rows.final_source.fillna('').ne('') & ~rows.has_direct_mt_provenance)
    rows['class_horus_time_difference_s'] = (pd.to_datetime(rows.origintime, utc=True, errors='coerce')-rows.horus_time).dt.total_seconds()
    rows['horus_provenance_time_difference_s'] = (rows.horus_time-rows.provenance_time).dt.total_seconds()
    rows['horus_provenance_mw_difference'] = rows.horus_mw-rows.final_mw
    return rows.drop(columns='join_id')


def read_nocal(path):
    names = ['year', 'month', 'day', 'hour', 'minute', 'second', 'latitude', 'longitude',
             'depth_km', 'eh_major_95_km', 'eh_minor_95_km', 'ellipse_azimuth', 'ev_95_km',
             'magnitude_ml', 'event_id']
    with gzip.open(path, 'rt') as stream:
        for skipped, line in enumerate(stream):
            if line.lstrip().startswith('1984 '):
                if len(line.split()) != len(names):
                    raise ValueError('Unexpected NCA data schema')
                break
        else:
            raise ValueError('NCA data start not found')
        # Skip the prose physically, before CSV parsing. Its quotation marks
        # and punctuation are not CSV fields or logical CSV row boundaries.
        stream.seek(0)
        for _ in range(skipped):
            stream.readline()
        frame = pd.read_csv(stream, sep=r'\s+', names=names)
    if not len(frame):
        raise ValueError('NCA catalogue unexpectedly contains no events')
    frame['event_id'] = positive_ids(frame.event_id)
    return frame
