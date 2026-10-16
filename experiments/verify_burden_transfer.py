"""Independent workbook, optimization and scoring check; no runner imports."""
import argparse
from collections import Counter
import hashlib
from io import BytesIO
import json
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import numpy as np
import openpyxl
from scipy.optimize import least_squares

ROOT = Path(__file__).resolve().parents[1]


def verify(predictions, result=None):
    # Mask prohibited numeric XML payloads BEFORE openpyxl decodes the file.
    # Thus its eager loading cannot inadvertently decode target responses in
    # the forecast-only stage. The original archive is never modified.
    permitted = {f'{c}{r}' for r in range(35, 47) for c in 'CDEKLM'}
    permitted |= {f'{c}{r}' for r in range(55, 65) for c in 'CDE'}
    if result is not None:
        permitted |= {f'{c}{r}' for r in range(55, 65) for c in 'KLMNO'}
    masked = BytesIO()
    ns = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    with ZipFile(ROOT/predictions['config']['source']) as src, ZipFile(masked, 'w') as dst:
        for item in src.infolist():
            blob = src.read(item.filename)
            if item.filename.startswith('xl/worksheets/sheet') and item.filename.endswith('.xml'):
                xml = ET.fromstring(blob)
                for cell in xml.findall('.//m:c', ns):
                    if cell.get('t') not in ('s', 'inlineStr') and not (
                            item.filename == 'xl/worksheets/sheet1.xml' and cell.get('r') in permitted):
                        value = cell.find('m:v', ns)
                        if value is not None: value.text = '0'
                        formula = cell.find('m:f', ns)
                        if formula is not None: cell.remove(formula)
                blob = ET.tostring(xml)
            dst.writestr(item, blob)
    masked.seek(0)
    sheet = openpyxl.load_workbook(masked, data_only=True)['Figure1']
    differences = []

    def check(actual, expected):
        aa, bb = np.asarray(actual, float), np.asarray(expected, float)
        if aa.shape != bb.shape or not np.allclose(aa, bb, rtol=2e-6, atol=2e-8):
            raise ValueError('Independent numerical verification disagrees')
        differences.extend(np.ravel(abs(aa-bb)).tolist())

    x, y, xp = [], [], []
    for record, row in zip(predictions['inputs']['training'], range(35, 47)):
        xx = [sheet[f'{c}{row}'].value for c in 'CDE']
        yy = [sheet[f'{c}{row}'].value for c in 'KLM']
        check(xx, record['assay_replicates']); check(yy, record['cell_replicates'])
        x.append(sum(xx)/3); y.append(sum(yy)/3)
        check([x[-1], y[-1]], [record['assay'], record['cell']])
    for record, row in zip(predictions['inputs']['targets'], range(55, 65)):
        xx = [sheet[f'{c}{row}'].value for c in 'CDE']
        check(xx, record['assay_replicates'])
        xp.append(sum(xx)/3); check(xp[-1], record['assay'])
    x, y, xp = np.array(x), np.array(y), np.array(xp)
    # Separate multi-start least-squares formulation in log(1+k), rather than
    # the runner's bounded objective profile.
    solutions = []
    for start in np.linspace(0, 10, 41):
        fun = lambda a: x/(x+np.expm1(a[0])*(1-x))-y
        fit = least_squares(fun, [max(1e-9, start)], bounds=(0, 30),
                            gtol=1e-13, ftol=1e-13, xtol=1e-13, max_nfev=2000)
        solutions.append((float(np.mean(fit.fun**2)), float(np.expm1(fit.x[0]))))
    _, k = min(solutions)
    klinear = max(0., sum((1-x)*(1-y))/sum((1-x)**2))
    slope = sum((x-x.mean())*(y-y.mean()))/sum((x-x.mean())**2)
    intercept = y.mean()-slope*x.mean()
    check(k, predictions['fits']['pool']['parameters']['k'])
    check(klinear, predictions['fits']['linear_burden']['parameters']['k'])
    check([intercept, slope], [predictions['fits']['affine']['parameters'][key]
                              for key in ['intercept', 'slope']])
    calculate = lambda xx: dict(pool=xx/(xx+k*(1-xx)),
        linear_burden=1-klinear*(1-xx), affine=intercept+slope*xx,
        constant=np.full(len(xx), y.mean()), direct_assay=xx)
    old, new = calculate(x), calculate(xp)
    for model in old:
        check(np.sqrt(np.mean((old[model]-y)**2)), predictions['fits'][model]['calibration_rmse'])
        check(new[model], predictions['fits'][model]['forecasts'])
    if result is not None:
        yy = []
        for record, row in zip(result['outcomes'], range(55, 65)):
            values = [sheet[f'{c}{row}'].value for c in 'KLM']
            check(values, record['replicates'])
            mean = sum(values)/3
            sd = np.sqrt(sum((v-mean)**2 for v in values)/2)
            check([mean, sd, sheet[f'N{row}'].value, sheet[f'O{row}'].value],
                  [record[k] for k in ['observed', 'sample_sd', 'reported_mean', 'reported_spread']])
            yy.append(mean)
        families = [r['family'] for r in predictions['inputs']['targets']]
        totals = Counter(families)
        family_maes = {}
        for model, values in new.items():
            error = values-np.array(yy)
            by_family = [sum(abs(error[i]) for i, f in enumerate(families) if f == group)/n
                         for group, n in totals.items()]
            family_maes[model] = sum(by_family)/len(by_family)
            check(error, result['scores'][model]['errors'])
            check(family_maes[model], result['scores'][model]['family_balanced_mae'])
            check(np.mean(abs(error)), result['scores'][model]['construct_mae'])
            check(max(abs(error)), result['scores'][model]['maximum_absolute_error'])
        gains = {m: 1-family_maes['pool']/family_maes[m] for m in result['gains']}
        for m, value in gains.items():
            check(value, result['gains'][m])
        accuracy = family_maes['pool'] <= predictions['config']['maximum_family_balanced_mae']
        advantages = {m: value >= predictions['config']['minimum_relative_gain'] for m, value in gains.items()}
        if result['decision'] != dict(absolute_accuracy=accuracy, relative_advantages=advantages,
                                      joint_rule=accuracy and all(advantages.values())):
            raise ValueError('Decision disagreement')
    return dict(numeric_checks=len(differences), maximum_absolute_difference=max(differences),
        numerical_outcomes_checked=result is not None,
        independent_methods=['openpyxl extraction', '41-start log-parameter least squares',
                             'centered affine regression', 'explicit family-first averaging'])


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--predictions', type=Path, required=True)
    p.add_argument('--result', type=Path)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    answer = verify(json.loads(a.predictions.read_text()), json.loads(a.result.read_text()) if a.result else None)
    answer['prediction_sha256'] = hashlib.sha256(a.predictions.read_bytes()).hexdigest()
    if a.result:
        answer['result_sha256'] = hashlib.sha256(a.result.read_bytes()).hexdigest()
    a.output.write_text(json.dumps(answer, indent=2, sort_keys=True, allow_nan=False)+'\n')
    print(json.dumps(answer))
