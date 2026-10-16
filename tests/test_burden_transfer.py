"""Synthetic estimator checks and tests that withheld cells stay unread."""
from pathlib import Path
import importlib.util
import tempfile
import unittest
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import numpy as np
from orthopolity.burden_transfer import (fit_models, predict, read_inputs, SourceSheet,
                                        cells, family_weights, score, NS, TARGETS)

SOURCE = Path(__file__).resolve().parents[1]/'data/biology-candidates/2026-10-16/borkowski2018/source-data.xlsx'


class BurdenTransferTests(unittest.TestCase):
    def test_recovery_in_both_model_worlds(self):
        x = np.linspace(.15, .9, 12)
        for model, k in [('pool', .35), ('pool', 3.8), ('linear_burden', .7)]:
            y = predict(model, x, {'k': k})
            fit = fit_models(x, y)[model]
            self.assertAlmostEqual(fit['parameters']['k'], k, places=6)
            self.assertLess(fit['calibration_rmse'], 1e-7)
            xx = np.array([.12, .4, .8, .95])
            np.testing.assert_allclose(predict(model, xx, fit['parameters']),
                                       predict(model, xx, {'k': k}), atol=1e-7)

    def test_boundary_and_order_invariance(self):
        x = np.linspace(.2, .9, 12)
        self.assertEqual(fit_models(x, np.ones(12))['pool']['parameters']['k'], 0.)
        y = predict('pool', x, {'k': 1.7})*np.linspace(.98, 1.02, 12)
        a, b = fit_models(x, y), fit_models(x[::-1], y[::-1])
        self.assertAlmostEqual(a['pool']['parameters']['k'], b['pool']['parameters']['k'], places=6)

    def test_resource_balance_and_no_clipping(self):
        x, k = np.array([.2, .5, .9]), 2.3
        free = predict('pool', x, {'k': k})
        np.testing.assert_allclose(free+free*k*(1/x-1), np.ones(3))
        self.assertLess(predict('linear_burden', [.1], {'k': 2})[0], 0)
        with self.assertRaises(ValueError):
            predict('pool', [1.01], {'k': 1})
        with self.assertRaises(ValueError):
            fit_models([.2, .5, .8], [1, 0, .5])

    def test_family_measure_and_scores(self):
        rows = [dict(id=i, family=f, observed=.4) for i, f in TARGETS]
        w = family_weights(rows)
        self.assertAlmostEqual(sum(w[:4]), 1/7)
        self.assertAlmostEqual(sum(w), 1)
        result = score([.5]*4+[.4]*6, rows)
        self.assertAlmostEqual(result['family_balanced_mae'], .1/7)
        self.assertAlmostEqual(result['construct_mae'], .04)

    def test_response_poisoning_and_explicit_access_control(self):
        # Every numeric cell is replaced before parsing; no real response is
        # used by this synthetic workbook test before the design is committed.
        with tempfile.TemporaryDirectory() as directory:
            safe, poison = [Path(directory)/name for name in ['safe.xlsx', 'poison.xlsx']]
            with ZipFile(SOURCE) as original, ZipFile(safe, 'w') as z1, ZipFile(poison, 'w') as z2:
                for item in original.infolist():
                    blob = original.read(item.filename)
                    if item.filename == 'xl/worksheets/sheet1.xml':
                        root = ET.fromstring(blob)
                        for c in root.findall('.//x:c', NS):
                            if c.get('t') not in ('s', 'inlineStr'):
                                v = c.find('x:v', NS)
                                if v is not None: v.text = '.5'
                        z1.writestr(item.filename, ET.tostring(root))
                        denied = set(cells('KLMNO', range(55, 65)))
                        for c in root.findall('.//x:c', NS):
                            if c.get('r') in denied: c.find('x:v', NS).text = 'WITHHELD'
                        z2.writestr(item.filename, ET.tostring(root))
                    else:
                        z1.writestr(item.filename, blob); z2.writestr(item.filename, blob)
            self.assertEqual(read_inputs(safe), read_inputs(poison))
            with self.assertRaises(ValueError):
                SourceSheet(poison, ['C55']).number('K55')

    def test_independent_verifier_on_synthetic_inputs_with_poisoned_targets(self):
        spec = importlib.util.spec_from_file_location('independent_burden_check',
            SOURCE.parents[4]/'experiments/verify_burden_transfer.py')
        verifier = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(verifier)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'synthetic.xlsx'
            values = {}
            for row in range(35, 47):
                x = .2+.06*(row-35)
                y = 1/(1+.6*(1/x-1))
                values.update({f'{c}{row}': x for c in 'CDE'})
                values.update({f'{c}{row}': y for c in 'KLM'})
            for row in range(55, 65):
                values.update({f'{c}{row}': .12+.08*(row-55) for c in 'CDE'})
            with ZipFile(SOURCE) as original, ZipFile(path, 'w') as new:
                for item in original.infolist():
                    blob = original.read(item.filename)
                    if item.filename == 'xl/worksheets/sheet1.xml':
                        root = ET.fromstring(blob)
                        for cell in root.findall('.//x:c', NS):
                            if cell.get('t') not in ('s', 'inlineStr'):
                                value = cell.find('x:v', NS)
                                if value is not None:
                                    value.text = str(values.get(cell.get('r'), 'WITHHELD'))
                        blob = ET.tostring(root)
                    new.writestr(item.filename, blob)
            inputs = read_inputs(path)
            fits = fit_models([r['assay'] for r in inputs['training']],
                              [r['cell'] for r in inputs['training']])
            for model, fit in fits.items():
                fit['forecasts'] = predict(model, [r['assay'] for r in inputs['targets']],
                                           fit['parameters']).tolist()
            answer = verifier.verify(dict(config=dict(source=str(path)), inputs=inputs, fits=fits))
            self.assertGreater(answer['numeric_checks'], 100)
            self.assertFalse(answer['numerical_outcomes_checked'])


if __name__ == '__main__':
    unittest.main()
