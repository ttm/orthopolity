"""Independently verify speech forecasts with decimal arithmetic and nested means.

Without --result, target Duration strings are never numerically decoded.
This verifier imports neither the analysis module nor its runner.
"""
import argparse
from decimal import Decimal, localcontext
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODELS = ('conditional', 'syllabic', 'unigram', 'power', 'same_text')
FAMILIES = {
    'CAT': 'Indo-European', 'DEU': 'Indo-European', 'ENG': 'Indo-European',
    'FRA': 'Indo-European', 'ITA': 'Indo-European', 'SPA': 'Indo-European',
    'SRP': 'Indo-European', 'CMN': 'Sino-Tibetan', 'YUE': 'Sino-Tibetan',
    'FIN': 'Uralic', 'HUN': 'Uralic', 'EUS': 'Basque', 'JPN': 'Japanese',
    'KOR': 'Korean', 'THA': 'Tai-Kadai', 'TUR': 'Turkic', 'VIE': 'Austroasiatic',
}


def mean(values):
    if not values:
        raise ValueError('Cannot average an empty group')
    return sum(values, Decimal(0)) / len(values)


def nested_mean(values, rows):
    """Average available texts, then speakers, languages, and families."""
    if len(values) != len(rows):
        raise ValueError('Value and row counts differ')
    tree = {}
    for value, row in zip(values, rows):
        tree.setdefault(row['family'], {}).setdefault(row['language'], {}).setdefault(
            row['speaker'], []).append(value)
    return mean([mean([mean([mean(v) for v in speakers.values()])
                        for speakers in languages.values()])
                 for languages in tree.values()])


def positive(text):
    value = Decimal(text)
    if not value.is_finite() or value <= 0:
        raise ValueError('Nonpositive or nonfinite source value')
    return value


def source_rows(config, evaluation):
    blob = (ROOT / config['source']).read_bytes()
    if hashlib.sha256(blob).hexdigest() != config['source_sha256']:
        raise ValueError('Source SHA-256 mismatch')
    lines = blob.decode('utf-8').splitlines()
    header = lines[0].split('\t')
    if len(header) != len(set(header)):
        raise ValueError('Duplicate source column')
    rows, seen, density, canonical = [], set(), {}, {}
    for number, line in enumerate(lines[1:], 2):
        fields = line.split('\t')
        if len(fields) != len(header):
            raise ValueError('Malformed source line')
        raw = dict(zip(header, fields))
        language = raw['Language']
        family = FAMILIES[language]
        identity = (language, raw['Speaker'], raw['Text'])
        if identity in seen:
            raise ValueError('Duplicate source identity')
        seen.add(identity)
        row = dict(line=number, language=language, family=family,
                   speaker=raw['Speaker'], text=raw['Text'],
                   ns=positive(raw['NS']), id=positive(raw['ID']), she=positive(raw['ShE']))
        pair = (row['id'], row['she'])
        if density.setdefault(language, pair) != pair:
            raise ValueError('Entropy varies within a language')
        if canonical.setdefault((language, row['text']), row['ns']) != row['ns']:
            raise ValueError('Syllable counts vary within language/text')
        if family == 'Indo-European' or evaluation:
            row['duration'] = positive(raw['Duration'])
        rows.append(row)
    if len(rows) != config['expected_rows']:
        raise ValueError('Source row count mismatch')
    return rows


def fit(training):
    y = [(r['duration'] / r['ns']).ln() for r in training]
    x = [r['id'].ln() for r in training]
    result = {}
    for model, feature in [('conditional', x), ('syllabic', [Decimal(0)] * len(x)),
                           ('unigram', [r['she'].ln() for r in training])]:
        result[model] = {'log_scale': nested_mean([a-b for a, b in zip(y, feature)], training)}
    mx, my = nested_mean(x, training), nested_mean(y, training)
    variance = nested_mean([(a-mx)**2 for a in x], training)
    if variance == 0:
        raise ValueError('Power slope is unidentified')
    slope = nested_mean([(a-mx)*(b-my) for a, b in zip(x, y)], training) / variance
    result['power'] = dict(log_scale=my-slope*mx, exponent=slope)
    by_text = {}
    for text in sorted({r['text'] for r in training}):
        group = [r for r in training if r['text'] == text]
        by_text[text] = nested_mean([r['duration'].ln() for r in group], group)
    result['same_text'] = dict(log_duration_by_text=by_text)
    return result


def forecasts(model, parameters, rows):
    if model == 'same_text':
        return [parameters['log_duration_by_text'][r['text']] for r in rows]
    return [r['ns'].ln() + parameters['log_scale'] + (
        r['id'].ln() if model == 'conditional' else r['she'].ln() if model == 'unigram'
        else parameters['exponent'] * r['id'].ln() if model == 'power' else Decimal(0))
        for r in rows]


def scores(predicted, rows):
    residuals = [p-r['duration'].ln() for p, r in zip(predicted, rows)]
    languages = {}
    for language in sorted({r['language'] for r in rows}):
        indices = [i for i, r in enumerate(rows) if r['language'] == language]
        group = [rows[i] for i in indices]
        errors = [residuals[i] for i in indices]
        bias = nested_mean(errors, group)
        languages[language] = dict(family=group[0]['family'], mean_log_error=bias,
            duration_ratio=bias.exp(), reading_log_mae=nested_mean([abs(e) for e in errors], group),
            observed_geometric_rate=nested_mean([(r['ns']/r['duration']).ln() for r in group], group).exp(),
            forecast_geometric_rate=nested_mean([rows[i]['ns'].ln()-predicted[i] for i in indices], group).exp())
    families = {family: mean([abs(v['mean_log_error']) for v in languages.values()
                             if v['family'] == family]) for family in sorted({r['family'] for r in rows})}
    return dict(family_balanced_language_log_mae=mean(list(families.values())),
        language_balanced_log_mae=mean([abs(v['mean_log_error']) for v in languages.values()]),
        family_balanced_reading_log_mae=nested_mean([abs(e) for e in residuals], rows),
        max_language_absolute_log_error=max(abs(v['mean_log_error']) for v in languages.values()),
        per_family=families, per_language=languages)


def verify(predictions, result=None):
    """Verify decoded artifacts; target numbers are accessed only with result."""
    count, maximum = 0, Decimal(0)

    def check(actual, expected, path):
        nonlocal count, maximum
        if isinstance(expected, dict):
            if not isinstance(actual, dict) or set(actual) != set(expected):
                raise ValueError('Field mismatch: '+path)
            for key, value in expected.items():
                check(actual[key], value, path+'.'+key)
        elif isinstance(expected, list):
            if not isinstance(actual, list) or len(actual) != len(expected):
                raise ValueError('List mismatch: '+path)
            for i, (a, e) in enumerate(zip(actual, expected)):
                check(a, e, path+f'[{i}]')
        elif isinstance(expected, (Decimal, int, float)) and not isinstance(expected, bool):
            if isinstance(actual, bool) or not isinstance(actual, (int, float, Decimal)):
                raise ValueError('Numeric type mismatch: '+path)
            value = Decimal(str(actual))
            if not value.is_finite():
                raise ValueError('Nonfinite value: '+path)
            difference = abs(value-Decimal(str(expected)))
            count += 1
            maximum = max(maximum, difference)
            if difference > Decimal('1e-10'):
                raise ValueError('Numeric mismatch: '+path)
        elif actual != expected or type(actual) is not type(expected):
            raise ValueError('Value mismatch: '+path)

    with localcontext() as context:
        context.prec = 50
        config = predictions['config']
        rows = source_rows(config, result is not None)
        training = [r for r in rows if r['family'] == 'Indo-European']
        targets = [{k: v for k, v in r.items() if k != 'duration'} for r in rows
                   if r['family'] != 'Indo-European']
        check(predictions['training'], training, 'training')
        check(predictions['targets'], targets, 'targets')
        check(predictions['target_numerical_durations_decoded'], False, 'target_decoding')
        check(predictions['study'], config['study'], 'study')
        lo, hi = min(r['id'] for r in training), max(r['id'] for r in training)
        outside = sorted({r['language'] for r in targets if not lo <= r['id'] <= hi})
        check(predictions['calibration_id_range'], [lo, hi], 'id_range')
        check(predictions['target_languages_outside_id_support'], outside, 'outside_support')
        fitted = fit(training)
        if set(predictions['fits']) != set(MODELS):
            raise ValueError('Model set mismatch')
        for model in MODELS:
            fitted[model]['log_forecasts'] = forecasts(model, fitted[model], targets)
            fitted[model]['calibration_score'] = scores(forecasts(model, fitted[model], training), training)
        check(predictions['fits'], fitted, 'fits')
        if result is not None:
            outcomes = [r for r in rows if r['family'] != 'Indo-European']
            calculated = {model: scores(fitted[model]['log_forecasts'], outcomes) for model in MODELS}
            key = 'family_balanced_language_log_mae'
            error = calculated['conditional'][key]
            gains = {m: 1-error/calculated[m][key] if calculated[m][key] != 0 else None
                     for m in MODELS if m != 'conditional'}
            accuracy = error <= Decimal(str(config['maximum_average_factor'])).ln()
            advantage = gains['syllabic'] is not None and gains['syllabic'] >= Decimal(str(config['minimum_syllabic_gain']))
            best = min(calculated[m][key] for m in ('unigram', 'power', 'same_text'))
            competitive = error <= Decimal(str(config['maximum_best_benchmark_ratio']))*best
            decisions = dict(accuracy=accuracy, syllabic_advantage=advantage, competitive=competitive,
                joint_rule=accuracy and advantage and competitive,
                contextual_advantage=gains['unigram'] is not None and gains['unigram'] >= Decimal(str(config['minimum_context_gain'])))
            for field, expected in dict(config=config, study=config['study'], design_commit=predictions['design_commit'],
                    outcomes=outcomes, scores=calculated, gains=gains, decision=decisions,
                    target_languages_outside_id_support=outside).items():
                check(result[field], expected, 'result.'+field)
    return dict(numeric_checks=count, max_abs_diff=float(maximum),
                target_numerical_durations_decoded=result is not None, source_sha256=config['source_sha256'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--predictions', required=True, type=Path)
    parser.add_argument('--result', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    prediction_bytes = args.predictions.read_bytes()
    result_bytes = args.result.read_bytes() if args.result else None
    report = verify(json.loads(prediction_bytes), json.loads(result_bytes) if result_bytes else None)
    report['prediction_sha256'] = hashlib.sha256(prediction_bytes).hexdigest()
    if result_bytes is not None:
        report['result_sha256'] = hashlib.sha256(result_bytes).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as stream:
        json.dump(report, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')
    print(json.dumps(report, sort_keys=True))


if __name__ == '__main__':
    main()
