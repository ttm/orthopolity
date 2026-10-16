"""Retrospective transfer of separately assayed protein-expression burden.

Numerical workbook cells are decoded only through an explicit allowlist. This
module never modifies the publisher workbook or evaluates its Excel formulas.
"""
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import numpy as np
from scipy.optimize import minimize_scalar

NS = {'x': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
TARGETS = [('Viob', 'Viob'), ('V1', 'Viob'), ('V2', 'Viob'), ('V3', 'Viob'),
           ('URA3', 'URA3'), ('aspA', 'aspA'), ('Leu2', 'Leu2'),
           ('SuhB', 'SuhB'), ('Ste12', 'Ste12'), ('atf1', 'atf1')]
MODELS = ('pool', 'linear_burden', 'affine', 'constant', 'direct_assay')


class SourceSheet:
    def __init__(self, path, allowed):
        self.allowed = set(allowed)
        self.decoded = []
        with ZipFile(path) as z:
            strings = ET.fromstring(z.read('xl/sharedStrings.xml'))
            self.strings = [''.join(e.itertext()) for e in strings.findall('x:si', NS)]
            root = ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
            self.cells = {c.get('r'): c for c in root.findall('.//x:c', NS)}

    def label(self, ref):
        cell = self.cells[ref]
        if cell.get('t') != 's':
            raise ValueError('Expected string label: ' + ref)
        return self.strings[int(cell.find('x:v', NS).text)]

    def number(self, ref):
        if ref not in self.allowed:
            raise ValueError('Numerical cell not permitted in this stage: ' + ref)
        cell = self.cells[ref]
        if cell.get('t') not in (None, 'n') or cell.find('x:f', NS) is not None:
            raise ValueError('Expected original numeric observation: ' + ref)
        value = float(cell.find('x:v', NS).text)
        if not np.isfinite(value):
            raise ValueError('Nonfinite observation: ' + ref)
        self.decoded.append(ref)
        return value


def cells(columns, rows):
    return [f'{c}{r}' for r in rows for c in columns]


def read_inputs(path):
    allowed = cells('CDEKLM', range(35, 47)) + cells('CDE', range(55, 65))
    sheet = SourceSheet(path, allowed)
    training, targets = [], []
    for r in range(35, 47):
        identity = 'Rand' + str(r-34)
        for col in ('B', 'J'):
            if sheet.label(f'{col}{r}').replace(' ', '') != 'Capacitymonitor+'+identity:
                raise ValueError('Calibration identity mismatch')
        x = [sheet.number(f'{c}{r}') for c in 'CDE']
        y = [sheet.number(f'{c}{r}') for c in 'KLM']
        training.append(dict(id=identity, row=r, assay_replicates=x,
                             cell_replicates=y, assay=float(np.mean(x)), cell=float(np.mean(y))))
    for r, (identity, family) in zip(range(55, 65), TARGETS):
        for col in ('B', 'J'):
            if sheet.label(f'{col}{r}').replace(' ', '') != 'Capacitymonitor+BCD2'+identity:
                raise ValueError('Target identity mismatch')
        x = [sheet.number(f'{c}{r}') for c in 'CDE']
        targets.append(dict(id=identity, family=family, row=r,
                            assay_replicates=x, assay=float(np.mean(x))))
    return dict(training=training, targets=targets, decoded_cells=sheet.decoded)


def read_outcomes(path):
    sheet = SourceSheet(path, cells('KLMNO', range(55, 65)))
    outcomes = []
    for r, (identity, family) in zip(range(55, 65), TARGETS):
        if sheet.label(f'J{r}').replace(' ', '') != 'Capacitymonitor+BCD2'+identity:
            raise ValueError('Outcome identity mismatch')
        yy = [sheet.number(f'{c}{r}') for c in 'KLM']
        outcomes.append(dict(id=identity, family=family, row=r, replicates=yy,
            observed=float(np.mean(yy)), sample_sd=float(np.std(yy, ddof=1)),
            reported_mean=sheet.number(f'N{r}'), reported_spread=sheet.number(f'O{r}')))
    return outcomes


def predict(model, x, parameters):
    x = np.asarray(x, dtype=float)
    if np.any(~np.isfinite(x)) or np.any(x <= 0) or np.any(x > 1):
        raise ValueError('Assay means must be in (0, 1]; no clipping or exclusions')
    if model == 'pool':
        return 1/(1+parameters['k']*(1/x-1))
    if model == 'linear_burden':
        return 1-parameters['k']*(1-x)
    if model == 'affine':
        return parameters['intercept']+parameters['slope']*x
    if model == 'constant':
        return np.full(x.shape, parameters['mean'])
    if model == 'direct_assay':
        return x.copy()
    raise ValueError('Unknown model')


def fit_models(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    predict('direct_assay', x, {})
    if x.ndim != 1 or x.shape != y.shape or len(x) < 3 or np.ptp(x) <= 1e-10:
        raise ValueError('Insufficient calibration support')
    if np.any(~np.isfinite(y)) or np.any(y <= 0):
        raise ValueError('Calibration cell means must be positive')
    load = 1/x-1
    if np.any(load <= 0):
        raise ValueError('Calibration must show positive assayed burden')
    # Beyond this bound all predictions are below their observations, so SSE
    # cannot decrease. Search every sampled local minimum, not a single start.
    upper = float(max(0., np.max((1/y-1)/load)))
    loss = lambda k: float(np.mean((1/(1+k*load)-y)**2))
    candidates = [(loss(0.), 0.), (loss(upper), upper)]
    if upper > 0:
        grid = np.unique(np.r_[np.linspace(0, upper, 2049),
                              np.geomspace(max(upper*1e-12, 1e-15), upper, 2049)])
        values = np.array([loss(k) for k in grid])
        for i in range(1, len(grid)-1):
            if values[i] <= values[i-1] and values[i] <= values[i+1]:
                opt = minimize_scalar(loss, bounds=(grid[i-1], grid[i+1]), method='bounded',
                                      options={'xatol': 1e-13})
                candidates.append((float(opt.fun), float(opt.x)))
    _, k = min(candidates)
    d = 1-x
    linear_k = float(max(0., np.dot(d, 1-y)/np.dot(d, d)))
    intercept, slope = np.linalg.lstsq(np.column_stack([np.ones(len(x)), x]), y, rcond=None)[0]
    parameters = dict(pool=dict(k=k, search_upper=upper), linear_burden=dict(k=linear_k),
                      affine=dict(intercept=float(intercept), slope=float(slope)),
                      constant=dict(mean=float(np.mean(y))), direct_assay={})
    return {model: dict(parameters=par, calibration_rmse=float(np.sqrt(np.mean(
                (predict(model, x, par)-y)**2)))) for model, par in parameters.items()}


def family_weights(rows):
    counts = Counter(r['family'] for r in rows)
    return np.array([1/(len(counts)*counts[r['family']]) for r in rows])


def score(predictions, outcomes):
    if len(predictions) != len(outcomes):
        raise ValueError('Outcome count mismatch')
    values = np.asarray(predictions, float)
    errors = values-np.array([o['observed'] for o in outcomes])
    weights = family_weights(outcomes)
    return dict(family_balanced_mae=float(np.dot(weights, abs(errors))),
        construct_mae=float(np.mean(abs(errors))),
        family_balanced_bias=float(np.dot(weights, errors)),
        maximum_absolute_error=float(np.max(abs(errors))),
        physically_negative_predictions=int(sum(values < 0)),
        errors=errors.tolist())
