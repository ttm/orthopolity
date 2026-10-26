"""Independent source and score audit of the public hotbox transfer study.

Without --result, numerical conversion is restricted to the permitted forecast
inputs: case 6/7 c..g and case 1..5 c/g. Supplying a released --result also
permits case 1..5 d/e/f. Dynamic files are never opened. This separate audit
uses split-line parsing and compensated sums, and imports no production code.
Local withholding of these public data is not external or global blinding.
"""

import argparse
import hashlib
import io
import json
import math
from pathlib import Path
import zipfile


ROOT = Path(__file__).resolve().parents[1]
MODELS = ('geometry', 'transfer', 'additive', 'persistence')


class Checks:
    def __init__(self):
        self.numeric = 0
        self.logical = 0
        self.maximum = 0.0

    def equal(self, actual, expected, path=''):
        if isinstance(expected, dict):
            if not isinstance(actual, dict) or set(actual) != set(expected):
                raise ValueError('Unexpected object fields: '+path)
            for name, value in expected.items():
                self.equal(actual[name], value, path+'.'+name)
        elif isinstance(expected, (list, tuple)):
            if not isinstance(actual, (list, tuple)) or len(actual) != len(expected):
                raise ValueError('Unexpected array shape: '+path)
            for i, (a, b) in enumerate(zip(actual, expected)):
                self.equal(a, b, f'{path}[{i}]')
        elif isinstance(expected, (int, float)) and not isinstance(expected, bool):
            if isinstance(actual, bool) or not isinstance(actual, (int, float)):
                raise ValueError('Wrong numeric type: '+path)
            if not math.isfinite(actual) or not math.isfinite(expected):
                raise ValueError('Nonfinite number: '+path)
            difference = abs(actual-expected)
            self.numeric += 1
            self.maximum = max(self.maximum, difference)
            if difference > 1e-10+1e-11*abs(expected):
                raise ValueError('Independent numerical mismatch: '+path)
        else:
            self.logical += 1
            if type(actual) is not type(expected) or actual != expected:
                raise ValueError('Independent logical mismatch: '+path)


def average(values):
    return math.fsum(values)/len(values)


def parse_selected(raw, columns, cfg):
    """Tokenize complete rows, but convert ONLY the explicit column allowlist.

In forecast-only mode target interior tokens are never passed to float or any
other numerical parser. Split-line parsing is independent of csv.reader in
the original runner. The source's unquoted, tab-separated header is required.
"""
    lines = raw.decode('utf-8').splitlines()
    header = lines[0].split('\t') if lines else []
    if len(header) != cfg['expected_columns'] or len(set(header)) != len(header):
        raise ValueError('Unexpected or duplicate source columns')
    if len(lines)-1 != cfg['expected_rows']:
        raise ValueError('Unexpected source row count')
    allowed = ['Time']+list(columns)
    if len(set(allowed)) != len(allowed):
        raise ValueError('Duplicate selected source columns')
    indices = [(name, header.index(name)) for name in allowed]
    values = {name: [] for name in allowed}
    for line in lines[1:]:
        tokens = line.split('\t')
        if len(tokens) != len(header):
            raise ValueError('Unexpected source row width')
        for name, index in indices:
            value = float(tokens[index])
            if not math.isfinite(value):
                raise ValueError('Nonfinite selected source cell')
            values[name].append(value)
    for earlier, later in zip(values['Time'], values['Time'][1:]):
        if abs((later-earlier)-cfg['time_step_seconds']) > 1e-7:
            raise ValueError('Clock disagrees with frozen sampling step')
    return values


def source_summaries(cfg, include_targets):
    raw = (ROOT/cfg['source']).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != cfg['source_sha256']:
        raise ValueError('Original source archive SHA-256 mismatch')
    summaries = {}
    temperature_cells = 0
    clock_cells = 0
    target_cells = 0
    window = cfg['drift_window_rows']
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        for case in range(1, 8):
            sensors = 'cdefg' if include_targets or case in (6, 7) else 'cg'
            columns = [f'{p}_{sensor}' for p in cfg['positions'] for sensor in sensors]
            difference = cfg['case_differences_c'][case-1]
            path = f'dataset/steady-state/SS_case_{case}_Temp_diff_{difference}.txt'
            selected = parse_selected(archive.read(path), columns, cfg)
            clock_cells += len(selected['Time'])
            for name in columns:
                p, sensor = name.split('_')
                values = selected[name]
                if not 0 < window <= len(values):
                    raise ValueError('Invalid window length')
                summaries[(case, int(p), sensor)] = {
                    'case': case, 'position': int(p), 'sensor': sensor,
                    'mean_c': average(values), 'min_c': min(values), 'max_c': max(values),
                    'drift_c': average(values[-window:])-average(values[:window]),
                }
                temperature_cells += len(values)
                if case in range(1, 6) and sensor in 'def':
                    target_cells += len(values)
    return summaries, {
        'source_sha256': digest,
        'temperature_cells_checked': temperature_cells,
        'clock_cells_checked': clock_cells,
        'numeric_source_cells_checked': temperature_cells+clock_cells,
        'target_interior_cells_checked': target_cells,
        'steady_files_checked': 7,
        'dynamic_files_opened': False,
    }


def qualified(row, cfg):
    lower, upper = cfg['internal_calibration_range_c']
    error = cfg['sensor_error_c']
    return (lower <= row['min_c']-error and row['max_c']+error <= upper
            and abs(row['drift_c']) <= cfg['maximum_window_drift_c'])


def evaluated_records(prediction, observed):
    cfg = prediction['config']
    inputs = {(r['case'], r['position'], r['sensor']): r
              for r in prediction['input_summary']}
    records = []
    for forecast in prediction['predictions']:
        case, p, sensor = (forecast[name] for name in ('case', 'position', 'sensor'))
        row = observed[(case, p, sensor)]
        profile_ok = all(qualified(observed[(case, p, s)], cfg) for s in cfg['interior'])
        if type(forecast['input_qualified']) is not bool:
            raise ValueError('Input qualification must be a boolean')
        residual = {name: row['mean_c']-forecast[name+'_prediction_c'] for name in MODELS}
        envelope = forecast['transfer_observation_interval_c']
        outside = None if envelope is None else not envelope[0] <= row['mean_c'] <= envelope[1]
        gap = abs(inputs[(case, p, 'c')]['mean_c']-inputs[(case, p, 'g')]['mean_c'])
        span = cfg['depth_m']['g']-cfg['depth_m']['c']
        base_error = 2*cfg['sensor_error_c']
        magnitude = abs(residual['geometry'])
        extra = max(magnitude-base_error, 0.0)
        required = (extra/(2*gap))*span if gap else None
        sensitivity = {}
        for allowance in cfg['geometry_sensitivity_m']:
            # The same independently specified position-error allowance is
            # applied to all three sensors; common datum shifts cancel.
            expanded_error = base_error+(allowance/span)*(2*gap)
            sensitivity[str(allowance)] = magnitude > expanded_error
        records.append({
            'case': case, 'position': p, 'sensor': sensor, 'observed': row,
            'residual_c': residual, 'qualified': forecast['input_qualified'] and profile_ok,
            'transfer_outside_envelope': outside,
            'geometry_outside_envelope': magnitude > base_error,
            'required_equal_position_allowance_m': required,
            'geometry_sensitivity_outside': sensitivity,
        })
    return records


def evaluated_groups(records, cfg):
    groups = {}
    subsets = [('all', records)]
    subsets += [(f'case_{case}', [row for row in records if row['case'] == case])
                for case in cfg['target_cases']]
    for name, rows in subsets:
        if not rows:
            raise ValueError('Empty evaluation group')
        groups[name] = {
            'target_means': len(rows),
            'qualified_target_means': sum(row['qualified'] for row in rows),
            'mae_c': {model: average([abs(row['residual_c'][model]) for row in rows])
                      for model in MODELS},
            'maximum_absolute_error_c': {
                model: max(abs(row['residual_c'][model]) for row in rows) for model in MODELS},
            'transfer_outside_all': sum(row['transfer_outside_envelope'] is True for row in rows),
            'transfer_envelopes_available': sum(row['transfer_outside_envelope'] is not None for row in rows),
            'transfer_outside_qualified': sum(row['qualified'] and row['transfer_outside_envelope'] is True
                                              for row in rows),
            'geometry_outside_all': sum(row['geometry_outside_envelope'] for row in rows),
        }
    return groups


def audit(prediction, result=None, *, prediction_sha256=None):
    checks = Checks()
    cfg = prediction['config']
    checks.equal(prediction['target_interior_temperatures_decoded'], False, 'forecast_target_access')
    # Fail closed on any change in the predeclared numerical release partition.
    checks.equal(cfg['target_cases'], [1, 2, 3, 4, 5], 'target_cases')
    checks.equal(cfg['positions'], [p for p in range(1, 16) if p != 8], 'positions')
    checks.equal(cfg['anchors'], ['c', 'g'], 'anchors')
    checks.equal(cfg['interior'], ['d', 'e', 'f'], 'interior')
    summaries, report = source_summaries(cfg, result is not None)
    positions = cfg['positions']
    expected_inputs = {(case, p, s) for case in (6, 7) for p in positions for s in 'cdefg'}
    expected_inputs.update((case, p, s) for case in range(1, 6)
                           for p in positions for s in 'cg')
    supplied_inputs = {}
    for row in prediction['input_summary']:
        key = row['case'], row['position'], row['sensor']
        if key in supplied_inputs or key not in expected_inputs:
            raise ValueError('Unexpected or duplicate input summary')
        supplied_inputs[key] = row
        checks.equal(row, summaries[key], 'input'+str(key))
    if set(supplied_inputs) != expected_inputs:
        raise ValueError('Incomplete input summaries')
    checks.equal(prediction['numeric_temperature_cells'], len(expected_inputs)*cfg['expected_rows'],
                 'forecast_cells')
    rows = prediction['predictions']
    identities = [(case, p, s) for case in range(1, 6) for p in positions for s in 'def']
    if len(rows) != len(identities):
        raise ValueError('Incomplete prediction vector')
    for row, identity in zip(rows, identities):
        checks.equal([row[k] for k in ('case', 'position', 'sensor')], identity,
                     'prediction_identity')
    if result is not None:
        records = evaluated_records(prediction, summaries)
        groups = evaluated_groups(records, cfg)
        if not all(row['qualified'] for row in records):
            verdict = 'qualification_incomplete'
        elif groups['all']['transfer_outside_all']:
            verdict = 'conditional_transfer_departure'
        else:
            verdict = 'not_excluded_by_marginal_bounds'
        checks.equal(result['records'], records, 'result.records')
        checks.equal(result['groups'], groups, 'result.groups')
        checks.equal(result['verdict'], verdict, 'result.verdict')
        checks.equal(result['no_target_refitting'], True, 'result.no_target_refitting')
        checks.equal(result['design_commit'], prediction['design_commit'], 'result.design_commit')
        checks.equal(result['scope'],
                     'Conditional thermal-resistance profile transfer; no unique convection or general-law identification',
                     'result.scope')
        commit = result['prediction_commit']
        if not isinstance(commit, str) or len(commit) != 40 or any(c not in '0123456789abcdef' for c in commit):
            raise ValueError('Invalid prediction commit identifier')
        if prediction_sha256 is not None:
            checks.equal(result['prediction_sha256'], prediction_sha256, 'result.prediction_sha256')
    report.update({
        'numeric_checks': checks.numeric,
        'logical_checks': checks.logical,
        'maximum_absolute_difference': checks.maximum,
        'input_summaries_checked': len(supplied_inputs),
        'target_summaries_checked': len(identities) if result is not None else 0,
        'target_interior_temperatures_decoded': result is not None,
        'source_archive_opened': True,
        'evaluation_checked': result is not None,
        'independent_methods': ['Allowlisted split-line numeric extraction',
                                'Compensated-sum means and window differences',
                                'Direct full-vector residual and qualification reconstruction',
                                'Explicit equal-weight score aggregation'],
        'exposure_scope': 'Public retrospective archive; local withholding is not external blinding',
    })
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prediction', type=Path, required=True)
    parser.add_argument('--result', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    prediction_raw = args.prediction.read_bytes()
    prediction_sha = hashlib.sha256(prediction_raw).hexdigest()
    result_raw = args.result.read_bytes() if args.result else None
    report = audit(json.loads(prediction_raw), json.loads(result_raw) if result_raw else None,
                   prediction_sha256=prediction_sha)
    report['prediction_sha256'] = prediction_sha
    if result_raw is not None:
        report['result_sha256'] = hashlib.sha256(result_raw).hexdigest()
    report['audit_source_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as stream:
        json.dump(report, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')
    print(json.dumps(report, sort_keys=True))


if __name__ == '__main__':
    main()
