"""Expose design fields only from a pinned public exchange archive.

No absorbance, concentration, calibration-standard values or fitted transport
coefficients are converted to numbers or returned. CSV fields outside the
explicit design whitelist are discarded. Source notebooks are not executed.
This is source qualification, not an empirical analysis or a preregistration.
"""
import csv
import hashlib
import io
import json
from collections import Counter
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'data/chemistry-candidates/2026-10-20/membrane-diffusion'
ARCHIVE = SOURCE / 'Membrane-Diffusion-Testing.zip'
MEMBERS = (
    '20250505_ot2_PES_PEG25_AO_metadata.csv',
    '20250603_manual_PES_PEG25_AO_metadata.csv',
)
DESIGN_FIELDS = ('Time', 'Hcell', 'Sample', 'Total_Volume_mL',
                 'Radius_cm', 'Membrane_cm')


def design_summary(stream):
    reader = csv.DictReader(stream)
    if not set(DESIGN_FIELDS).issubset(reader.fieldnames or ()):
        raise ValueError('Expected design fields are missing')
    rows = [{k: row[k] for k in DESIGN_FIELDS} for row in reader]
    counts = Counter((r['Sample'], r['Hcell']) for r in rows)
    return {
        'n_rows': len(rows),
        'times_hours': sorted({float(r['Time']) for r in rows}),
        'sample_ids': sorted({r['Sample'] for r in rows}),
        'chamber_labels': sorted({r['Hcell'] for r in rows}),
        'total_volume_mL_values': sorted({float(r['Total_Volume_mL']) for r in rows}),
        'radius_cm_values': sorted({float(r['Radius_cm']) for r in rows}),
        'thickness_entries_with_unresolved_csv_units': sorted({r['Membrane_cm'] for r in rows}),
        'rows_per_sample_chamber': [
            {'sample': sample, 'chamber': chamber, 'rows': n}
            for (sample, chamber), n in sorted(counts.items())],
    }


def check_response_field_exclusion():
    header = ','.join(DESIGN_FIELDS) + ',Abs_raw,Abs,C_sample,C_original\n'
    design = '0,donor,S1,22,0.81,0.12,'
    # Invalid numerical strings in every outcome field must remain unparsed.
    a = design_summary(io.StringIO(header + design + 'POISON,POISON,POISON,POISON\n'))
    b = design_summary(io.StringIO(header + design + '1,2,3,4\n'))
    assert a == b


def main():
    check_response_field_exclusion()
    raw = ARCHIVE.read_bytes()
    assert hashlib.md5(raw).hexdigest() == '92c9c740602a1f274a2e4550ca98409d'
    result = {
        'kind': 'Design-only source inventory; no empirical result or preregistration',
        'source_commit': '12be95974a58e1971483823948eff8802e06b729',
        'archive_sha256': hashlib.sha256(raw).hexdigest(),
        'inspected_sample_fields': list(DESIGN_FIELDS),
        'response_field_exclusion_check': 'passed',
        'selected_runs': [],
    }
    with ZipFile(ARCHIVE) as archive:
        result['archive_member_count'] = len(archive.namelist())
        result['sample_file_count'] = sum(
            n.startswith('Diffusion Testing/Sample Data/') and n.endswith('.csv')
            for n in archive.namelist())
        for name in MEMBERS:
            member = 'Diffusion Testing/Sample Data/' + name
            with archive.open(member) as handle:
                summary = design_summary(io.TextIOWrapper(handle, encoding='utf-8-sig'))
            summary['member'] = member
            result['selected_runs'].append(summary)
        result['calibration_files'] = []
        for name in ('20250505_ot2_calibration_AO.csv', '20250603_manual_calibration_AO.csv'):
            member = 'Diffusion Testing/UV_Vis_Calibration_Curves/' + name
            with archive.open(member) as handle:
                reader = csv.reader(io.TextIOWrapper(handle, encoding='utf-8-sig'))
                header = next(reader)
                n_rows = sum(1 for _ in reader)
            result['calibration_files'].append(dict(member=member, header=header, n_rows=n_rows))
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
