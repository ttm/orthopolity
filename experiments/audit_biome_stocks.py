"""Fixed BioMe source/stock diagnostic; no kinetic or capacity fit.

See docs/biome-stock-audit-protocol-2026-10-23.md. The inventory stage
converts only whitelisted labels and time cells, never response values.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'data/physics-candidates/2026-10-23/biome'
NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
DYES = ('phenol_red', 'bromocresol_purple')
PORES = (0., .03, .1, .2, .4)


def column(number):
    name = ''
    while number:
        number, remainder = divmod(number - 1, 26)
        name = chr(65 + remainder) + name
    return name


def source_cells(path):
    """Keep numeric cells as XML text until a specific caller selects them."""
    with ZipFile(path) as archive:
        workbook = ET.fromstring(archive.read('xl/workbook.xml'))
        sheets = workbook.findall('s:sheets/s:sheet', NS)
        if len(sheets) != 1 or sheets[0].get('name') != 'Plate 1 - Sheet1':
            raise ValueError('Unexpected workbook mapping')
        strings = [''.join(s.itertext()) for s in
                   ET.fromstring(archive.read('xl/sharedStrings.xml'))]
        sheet = ET.fromstring(archive.read('xl/worksheets/sheet1.xml'))
    return {c.get('r'): c for c in sheet.findall('s:sheetData/s:row/s:c', NS)}, strings


def number(cells, address):
    cell = cells[address]
    if cell.get('t') not in (None, 'n') or cell.find('s:f', NS) is not None:
        raise ValueError(f'Expected original numeric cell: {address}')
    value = float(cell.find('s:v', NS).text)
    if not np.isfinite(value):
        raise ValueError(f'Nonfinite cell: {address}')
    return value


def matching_block(cells, first_row, n_times, dye):
    # Each retained dye has three rows of ten wells; the other wavelength
    # and dye's rows are deliberately never decoded.
    start = 4 + 30 * dye
    return np.array([[number(cells, f'{column(c)}{r}')
                      for c in range(start, start + 30)]
                     for r in range(first_row, first_row + n_times)]).reshape(n_times, 3, 10)


def verify_sources():
    receipt = json.loads((SOURCE / 'acquisition.json').read_text())
    for entry in receipt['files']:
        path = SOURCE / entry['file']
        if path.parent != SOURCE:
            raise ValueError('Invalid source path')
        data = path.read_bytes()
        if len(data) != entry['bytes'] or hashlib.sha256(data).hexdigest() != entry['sha256']:
            raise ValueError(f'Source changed: {path}')
    return receipt


def inventory():
    receipt = verify_sources()
    output = {'repository_commit': receipt['repository_commit'],
              'verified_files': len(receipt['files']),
              'numerical_response_values_decoded': False, 'workbooks': {}}
    for filename, rows, n in [('optical-calibration.xlsx', (28, 57), 25),
                              ('dye-diffusion.xlsx', (28, 321), 289)]:
        cells, strings = source_cells(SOURCE / filename)
        blocks = []
        for start in rows:
            labels = []
            for c in range(4, 64):
                cell = cells[f'{column(c)}{start-1}']
                label = strings[int(cell.find('s:v', NS).text)]
                labels.append(label)
            expected = [f'{row}{c}' for row in 'ABCDEF' for c in range(1, 11)]
            if labels != expected:
                raise ValueError('Unexpected plate map')
            times = np.array([number(cells, f'B{r}') for r in range(start, start+n)]) * 24
            np.testing.assert_allclose(times-times[0], np.arange(n)/4, atol=1e-9, rtol=0)
            blocks.append({'rows': [start, start+n-1], 'times': n,
                           'instrument_hours': [float(times[0]), float(times[-1])],
                           'elapsed_hours': [0., (n-1)/4],
                           'plate_labels': labels})
        output['workbooks'][filename] = blocks
    return output


def calibrate(absorbance):
    levels = np.arange(450., -1., -50.)
    means = absorbance.mean(axis=0)
    c = np.tile(levels, 3)
    a = means.ravel()
    x = np.column_stack([np.ones(len(c)), c])
    intercept, slope = np.linalg.lstsq(x, a, rcond=None)[0]
    if slope <= 0:
        raise ValueError('Nonpositive optical slope')
    errors = []
    for level in levels:
        keep = c != level
        aa, bb = np.linalg.lstsq(x[keep], a[keep], rcond=None)[0]
        if bb <= 0:
            raise ValueError('Nonpositive held-concentration optical slope')
        errors.extend(((a[~keep] - aa)/bb - c[~keep]).tolist())
    return dict(intercept=float(intercept), slope=float(slope),
                rmse_uM=float(np.sqrt(np.mean(((a-intercept)/slope-c)**2))),
                maximum_held_concentration_error_uM=float(np.max(np.abs(errors))),
                maximum_temporal_deviation_uM=float(np.max(np.abs(absorbance-means))/slope),
                independent_wells=30, repeated_reads_per_well=25)


def trace_metrics(absorbance, calibration):
    conc = (absorbance-calibration['intercept'])/calibration['slope']
    recovery = (conc[:, :, 0::2] + conc[:, :, 1::2])/400
    if np.any(recovery[0] <= 0):
        raise ValueError('Nonpositive initial total')
    control_contrast = absorbance[:, :, 0] - absorbance[:, :, 1]
    relative_control = np.full(recovery.shape, np.nan)
    invalid_controls = []
    for replicate in range(3):
        if np.any(control_contrast[:, replicate] <= 0):
            invalid_controls.append({'replicate': replicate+1,
                                     'reason': 'nonpositive no-pore control contrast'})
            continue
        values = (absorbance[:, replicate, 0::2]+absorbance[:, replicate, 1::2]
                  - 2*absorbance[:, replicate, 1, None])/control_contrast[:, replicate, None]
        for pair in range(5):
            if values[0, pair] <= 0:
                invalid_controls.append({'replicate': replicate+1, 'pore_um': PORES[pair],
                                         'reason': 'nonpositive initial control ratio'})
            else:
                relative_control[:, replicate, pair] = values[:, pair]/values[0, pair]
    return dict(recovery_nominal=recovery, recovery_initial=recovery/recovery[0],
                control_ratio_initial=relative_control, invalid_controls=invalid_controls,
                concentration_uM=conc)


def summary(values):
    valid = values[np.isfinite(values)]
    return dict(replicates=[float(v) if np.isfinite(v) else None for v in values],
                valid_replicates=len(valid),
                mean=float(valid.mean()) if len(valid) else None,
                minimum=float(valid.min()) if len(valid) else None,
                maximum=float(valid.max()) if len(valid) else None)


def compute(calibration_blocks, response_blocks):
    result = {'scope': 'source qualification, not a confirmatory law or network test',
              'reference_measure': 'physical chamber volume; neither log-orthopolic nor linear-orthopolic size allocation',
              'hours': (np.arange(289)/4).tolist(), 'dyes': {}}
    for d, name in enumerate(DYES):
        calibration = calibrate(calibration_blocks[d])
        traces = trace_metrics(response_blocks[d], calibration)
        groups = []
        for p, pore in enumerate(PORES):
            group = {'pore_um': pore}
            for metric in ('recovery_nominal', 'recovery_initial', 'control_ratio_initial'):
                values = traces[metric][:, :, p]
                group[metric] = {'initial': summary(values[0]),
                                 'last_hour': summary(values[-5:].mean(axis=0))}
            groups.append(group)
        controls = traces['concentration_uM'][:, :, :2]
        result['dyes'][name] = dict(calibration=calibration, groups=groups,
            invalid_controls=traces['invalid_controls'],
            no_pore_changes_uM={side: summary(controls[-5:, :, i].mean(axis=0)-controls[0, :, i])
                               for i, side in enumerate(('donor', 'recipient'))},
            traces={k: np.where(np.isfinite(traces[k]), traces[k], None).tolist()
                    for k in ('recovery_nominal', 'recovery_initial', 'control_ratio_initial')})
    return result


def require_freeze(commit):
    # Check the protocol, analysis and acquisition receipt against the pushed
    # freeze. Later result/document commits may follow without changing them.
    for path in ('docs/biome-stock-audit-protocol-2026-10-23.md',
                 'experiments/audit_biome_stocks.py',
                 'data/physics-candidates/2026-10-23/biome/acquisition.json'):
        frozen = subprocess.check_output(['git', 'show', f'{commit}:{path}'], cwd=ROOT)
        if frozen != (ROOT / path).read_bytes():
            raise ValueError(f'Freeze differs: {path}')
    subprocess.run(['git', 'merge-base', '--is-ancestor', commit, 'origin/main'],
                   cwd=ROOT, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=('inventory', 'diagnose'), required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--freeze-commit')
    args = parser.parse_args()
    meta = inventory()
    if args.stage == 'inventory':
        result = meta
    else:
        if not args.freeze_commit:
            parser.error('Numerical decoding requires --freeze-commit')
        require_freeze(args.freeze_commit)
        standards, _ = source_cells(SOURCE / 'optical-calibration.xlsx')
        responses, _ = source_cells(SOURCE / 'dye-diffusion.xlsx')
        result = compute([matching_block(standards, r, 25, d) for d, r in enumerate((28, 57))],
                         [matching_block(responses, r, 289, d) for d, r in enumerate((28, 321))])
        result['freeze_commit'] = args.freeze_commit
        result['source_inventory'] = meta
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps({'stage': args.stage, 'output': str(args.output),
                      'numerical_response_values_decoded': args.stage == 'diagnose'}))


if __name__ == '__main__':
    main()
