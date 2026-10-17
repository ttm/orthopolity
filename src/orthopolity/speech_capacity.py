"""Independent-entropy forecasts of pause-filtered speech duration."""
from collections import defaultdict
import csv
import math

import numpy as np

FAMILIES = {
    'CAT': 'Indo-European', 'DEU': 'Indo-European', 'ENG': 'Indo-European',
    'FRA': 'Indo-European', 'ITA': 'Indo-European', 'SPA': 'Indo-European',
    'SRP': 'Indo-European', 'CMN': 'Sino-Tibetan', 'YUE': 'Sino-Tibetan',
    'FIN': 'Uralic', 'HUN': 'Uralic', 'EUS': 'Basque', 'JPN': 'Japanese',
    'KOR': 'Korean', 'THA': 'Tai-Kadai', 'TUR': 'Turkic', 'VIE': 'Austroasiatic',
}
MODELS = ('conditional', 'syllabic', 'unigram', 'power', 'same_text')


def positive(value):
    x = float(value)
    if not math.isfinite(x) or x <= 0:
        raise ValueError('Nonpositive or nonfinite measurement')
    return x


def read_rows(path, stage='predictors'):
    """Never numerically decode Duration outside the stage's authorized rows."""
    if stage not in ('predictors', 'calibration', 'evaluation'):
        raise ValueError('Unknown access stage')
    rows, seen, entropies, counts = [], set(), {}, {}
    with open(path, newline='') as stream:
        for line, raw in enumerate(csv.DictReader(stream, delimiter='\t'), 2):
            lang = raw['Language']
            family = FAMILIES[lang]
            key = (lang, raw['Speaker'], raw['Text'])
            if key in seen:
                raise ValueError('Duplicate speaker/text identity')
            seen.add(key)
            row = dict(line=line, language=lang, family=family,
                       speaker=raw['Speaker'], text=raw['Text'],
                       ns=positive(raw['NS']), id=positive(raw['ID']), she=positive(raw['ShE']))
            pair = (row['id'], row['she'])
            if entropies.setdefault(lang, pair) != pair:
                raise ValueError('Within-language entropy changed')
            if counts.setdefault((lang, row['text']), row['ns']) != row['ns']:
                raise ValueError('Canonical syllable count changed')
            if stage == 'evaluation' or (stage == 'calibration' and family == 'Indo-European'):
                row['duration'] = positive(raw['Duration'])
            rows.append(row)
    return rows


def weights(rows):
    """Equal families, languages within family, speakers, then available texts."""
    tree = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for i, row in enumerate(rows):
        tree[row['family']][row['language']][row['speaker']].append(i)
    if not tree:
        raise ValueError('Empty cohort')
    w = np.zeros(len(rows))
    for languages in tree.values():
        for speakers in languages.values():
            for indices in speakers.values():
                w[indices] = 1 / (len(tree)*len(languages)*len(speakers)*len(indices))
    return w


def fit_models(training):
    w = weights(training)
    y = np.log([positive(r['duration']) for r in training])
    ns = np.log([r['ns'] for r in training])
    x = np.log([r['id'] for r in training])
    sh = np.log([r['she'] for r in training])
    fits = {}
    for name, cost in [('conditional', ns+x), ('syllabic', ns), ('unigram', ns+sh)]:
        fits[name] = dict(log_scale=float(w@(y-cost)))
    design = np.column_stack([np.ones(len(x)), x])
    if np.linalg.matrix_rank(design) != 2:
        raise ValueError('Density power is unidentified')
    coef = np.linalg.lstsq(design*np.sqrt(w[:, None]), (y-ns)*np.sqrt(w), rcond=None)[0]
    fits['power'] = dict(log_scale=float(coef[0]), exponent=float(coef[1]))
    text_values = {}
    for text in sorted({r['text'] for r in training}):
        subset = [r for r in training if r['text'] == text]
        text_values[text] = float(weights(subset)@np.log([r['duration'] for r in subset]))
    fits['same_text'] = dict(log_duration_by_text=text_values)
    return fits


def predict(model, fit, rows):
    if model == 'same_text':
        out = np.array([fit['log_duration_by_text'][r['text']] for r in rows])
    else:
        out = np.log([r['ns'] for r in rows])+fit['log_scale']
        if model == 'conditional':
            out += np.log([r['id'] for r in rows])
        elif model == 'unigram':
            out += np.log([r['she'] for r in rows])
        elif model == 'power':
            out += fit['exponent']*np.log([r['id'] for r in rows])
        elif model != 'syllabic':
            raise ValueError('Unknown model')
    if not np.isfinite(out).all():
        raise ValueError('Nonfinite forecast')
    return out


def score(log_forecast, outcomes):
    residual = np.asarray(log_forecast)-np.log([positive(r['duration']) for r in outcomes])
    if residual.shape != (len(outcomes),) or not np.isfinite(residual).all():
        raise ValueError('Invalid forecast shape or value')
    per_language = {}
    for lang in sorted({r['language'] for r in outcomes}):
        ix = [i for i, r in enumerate(outcomes) if r['language'] == lang]
        subset = [outcomes[i] for i in ix]
        w = weights(subset)
        bias = float(w@residual[ix])
        per_language[lang] = dict(family=subset[0]['family'], mean_log_error=bias,
            duration_ratio=math.exp(bias), reading_log_mae=float(w@abs(residual[ix])),
            observed_geometric_rate=math.exp(float(w@np.log([r['ns']/r['duration'] for r in subset]))),
            forecast_geometric_rate=math.exp(float(w@(np.log([r['ns'] for r in subset])-np.asarray(log_forecast)[ix]))))
    family_errors = {}
    for family in sorted({r['family'] for r in outcomes}):
        values = [v['mean_log_error'] for v in per_language.values() if v['family'] == family]
        family_errors[family] = float(np.mean(np.abs(values)))
    return dict(family_balanced_language_log_mae=float(np.mean(list(family_errors.values()))),
        language_balanced_log_mae=float(np.mean([abs(v['mean_log_error']) for v in per_language.values()])),
        family_balanced_reading_log_mae=float(weights(outcomes)@abs(residual)),
        max_language_absolute_log_error=max(abs(v['mean_log_error']) for v in per_language.values()),
        per_family=family_errors, per_language=per_language)
