"""Predictor-only saltation source audit and constrained flux-law calibration.

The workbook reader deliberately never converts response columns J:N.
No real saltation response is used by the qualification experiment.
"""
from collections import Counter
import datetime as dt
from pathlib import PurePosixPath
import xml.etree.ElementTree as ET
from zipfile import ZipFile

import numpy as np

NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
HEADERS = ['Date', 'StartTime', 'EndTime', 'ust', 'sigma_ust', 'tau',
           'sigma_tau', 'theta', 'zL', 'zq', 'sigma_zq', 'Q', 'sigma_Q', 'fQ']


def read_wind(path):
    """Return source identities and A:I predictors only, including missingness."""
    with ZipFile(path) as book:
        wb = ET.fromstring(book.read('xl/workbook.xml'))
        if wb.find('s:workbookPr', NS).get('date1904', '0') not in ('0', 'false'):
            raise ValueError('Unexpected workbook date epoch')
        relationships = ET.fromstring(book.read('xl/_rels/workbook.xml.rels'))
        targets = {r.get('Id'): r.get('Target') for r in relationships}
        strings = [''.join(t.itertext()) for t in
                   ET.fromstring(book.read('xl/sharedStrings.xml')).findall('s:si', NS)]
        rows = []
        for sheet in wb.findall('s:sheets/s:sheet', NS):
            name = sheet.get('name')
            if name == 'Notes':
                continue
            rid = sheet.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
            target = targets[rid]
            filename = target.lstrip('/') if target.startswith('/') else str(PurePosixPath('xl') / target)
            root = ET.fromstring(book.read(filename))
            source_rows = root.findall('s:sheetData/s:row', NS)
            headings = {c.get('r').rstrip('0123456789'): strings[int(c.find('s:v', NS).text)]
                        for c in source_rows[0] if c.get('t') == 's'}
            if [headings.get(c) for c in 'ABCDEFGHIJKLMN'] != HEADERS:
                raise ValueError('Unexpected source header')
            for source_row in source_rows[1:]:
                values = {}
                for cell in source_row:
                    col = cell.get('r').rstrip('0123456789')
                    if col not in 'ABCDEFGHI' or len(col) != 1:
                        continue  # Never decode or convert numerical response values.
                    if cell.find('s:f', NS) is not None:
                        raise ValueError('Predictor is a formula; dependency audit required')
                    node = cell.find('s:v', NS)
                    raw = '' if node is None else node.text
                    if cell.get('t') == 's':
                        raw = strings[int(raw)]
                    values[col] = float(raw) if raw else float('nan')
                date = values['A']
                if not np.isfinite(date) or date != int(date):
                    raise ValueError('Nonintegral or missing source date')
                record = dict(site=name, source_row=int(source_row.get('r')),
                              date=(dt.date(1899, 12, 30) + dt.timedelta(days=date)).isoformat())
                for col, key in zip('BCDEFGHI', HEADERS[1:9]):
                    value = values.get(col, float('nan'))
                    record[key] = float(value) if np.isfinite(value) else None
                rows.append(record)
    identities = [(r['site'], r['date'], r['StartTime']) for r in rows]
    if len(set(identities)) != len(rows):
        raise ValueError('Repeated source interval')
    return rows


def eligible(row, config):
    return (all(row[k] is not None for k in ('tau', 'theta', 'zL'))
            and row['tau'] > 0 and abs(row['theta']) <= config['max_abs_theta_degrees']
            and abs(row['zL']) <= config['max_abs_zL'])


def split_wind(rows, config):
    """Split calendar dates before eligibility; no activity-based day selection."""
    site_rows = [r for r in rows if r['site'] == config['primary_site']]
    dates = sorted({r['date'] for r in site_rows})
    cut = len(dates) // 2
    calibration_dates = set(dates[:cut])
    usable = [r for r in site_rows if eligible(r, config)]
    calibration = [r for r in usable if r['date'] in calibration_dates]
    prediction = [r for r in usable if r['date'] not in calibration_dates]
    for group in (calibration, prediction):
        if len({r['date'] for r in group}) < config['minimum_days_per_split']:
            raise ValueError('Insufficient calendar-day support')
    return calibration, prediction


def day_weights(dates):
    counts = Counter(dates)
    return np.array([1 / (len(counts) * counts[day]) for day in dates])


def flux(tau, coefficient, threshold, exponent):
    x = np.asarray(tau, dtype=float)
    if np.any(~np.isfinite(x)) or np.any(x <= 0):
        raise ValueError('Stress must be finite and positive')
    return coefficient * x ** exponent * np.maximum(x - threshold, 0)


def fit_flux(tau, response, weights, exponent):
    """Global weighted least-squares hinge fit, C>=0 and 0<=threshold<=max(tau).

    Within each active-set interval, profile out C. The resulting rational
    objective has at most one nontrivial stationary threshold. Evaluate every
    such point and every knot, including zero flux at the upper boundary.
    """
    x, y, w = map(lambda v: np.asarray(v, dtype=float), (tau, response, weights))
    if (x.ndim != 1 or y.shape != x.shape or w.shape != x.shape or len(x) < 2
            or not all(np.all(np.isfinite(v)) for v in (x, y, w))
            or np.any(x <= 0) or np.any(y < 0) or np.any(w <= 0)
            or exponent not in (0, .5)):
        raise ValueError('Invalid calibration arrays or exponent')
    knots = np.r_[0., np.unique(x)]
    candidates = list(knots)
    for lo, hi in zip(knots[:-1], knots[1:]):
        use = x > lo
        v, z, ww, yy = x[use] ** exponent, x[use], w[use], y[use]
        a, b = np.sum(ww * yy * v * z), np.sum(ww * yy * v)
        d, e, f = np.sum(ww * v*v * z*z), np.sum(ww * v*v * z), np.sum(ww * v*v)
        denom = b * e - a * f
        if denom != 0:
            t = (b * d - a * e) / denom
            if lo < t < hi:
                candidates.append(float(t))
    thresholds = np.asarray(candidates)
    h = x[None, :] ** exponent * np.maximum(x[None, :] - thresholds[:, None], 0)
    denominators = (h*h) @ w
    coefficients = np.divide(h @ (w*y), denominators,
                             out=np.zeros_like(denominators), where=denominators > 0)
    coefficients = np.maximum(coefficients, 0)
    errors = np.sum(w * (coefficients[:, None]*h - y)**2, axis=1)
    best = int(np.argmin(errors))
    return dict(coefficient=float(coefficients[best]), threshold=float(thresholds[best]),
                exponent=float(exponent), mse=float(errors[best]))


def lognormal_factors(rng, dates, total_cv, replicates):
    """Mean-one day-shared and interval-specific factors; marginal CV is exact."""
    labels, inverse = np.unique(dates, return_inverse=True)
    day_variance = np.log1p((total_cv / 2)**2)
    residual_variance = np.log1p(total_cv**2) - day_variance
    day = rng.normal(-day_variance/2, np.sqrt(day_variance), (replicates, len(labels)))
    residual = rng.normal(-residual_variance/2, np.sqrt(residual_variance), (replicates, len(dates)))
    return np.exp(day[:, inverse] + residual)
