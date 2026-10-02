"""Runner checks use synthetic vessels generated from a known reweighting."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import openpyxl

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('chemostat_response_runner', ROOT/'experiments/run_chemostat_response.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

CONFIG = json.loads((ROOT/'configs/chemostat_response_2026-10-02.json').read_text())
AMENDMENT = json.loads((ROOT/'configs/chemostat_response_2026-10-02_amendment-1.json').read_text())
# Densities (pmol per cubic micrometre) give C:N ratios Cr 9.1, Ca 13.5, Mo 9.76, Co 7.27.
NITROGEN = dict(Cr=.0045, Ca=.0017, Mo=.0021, Co=.0033)
CARBON = dict(Cr=.04095, Ca=.02295, Mo=.0205, Co=.024)
MIDPOINT_RATIOS = np.array([9.1, 13.5, (.0205+.024)/(.0021+.0033)])


def strength(time):
    return .3*max(time, 0.)


def volumes(baseline, time):
    """Exact two-budget reweighting with a common total growth factor."""
    return np.asarray(baseline)*(1.+.05*max(time, 0.))/(1.+strength(time)*MIDPOINT_RATIOS)


def table(rows, gated=0):
    return dict(sheet='Sheet1', date1904=False, rows=rows, gated_rows=gated, columns={})


def vessel_rows(start, category, treatment, chemostat, baseline, times, gate_after=None):
    headers = runner.group_headers(CONFIG)
    rows, gated = [], 0
    for offset, time in enumerate(times):
        metadata = dict(zip(runner.META, [category, treatment, chemostat, 45000+offset, time]))
        decoded = gate_after is None or time <= gate_after
        values = None
        if decoded:
            amount = volumes(baseline, time)
            values = {runner.TOTAL_HEADER: float(np.sum(amount)), **dict(zip(headers, map(float, amount)))}
        gated += not decoded
        rows.append(dict(source_row=start+offset, metadata=metadata, values=values, decoded=decoded))
    return rows, gated


def synthetic_tables(view):
    gate_after = 0 if view == 'freeze' else None
    main, gated, number = [], 0, 2
    development = {'D1': [3e6, 2e6, 5e6], 'D2': [1e6, 4e6, 4e6], 'D3': [2e6, 2e6, 2e6], 'D4': [5e6, 1e6, 3e6]}
    for name, baseline in development.items():
        rows, _ = vessel_rows(number, 'Monocultures', 'Bc', name, baseline, [-2, 0, 1, 2, 3, 4, 5, 6, 8, 11, 13])
        main += rows
        number += len(rows)
    for name, baseline in {'1': [2e6, 3e6, 4e6], '2': [4e6, 2e6, 1e6], '3': [1e6, 1e6, 6e6]}.items():
        rows, count = vessel_rows(number, 'Polycultures', '9d', name, baseline,
                                  [-2, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 12, 14], gate_after)
        main += rows
        gated += count
        number += len(rows)
    mixture = []
    for name in ('Mi1', 'Mi2', 'Cr1'):
        rows, _ = vessel_rows(len(mixture)+2, 'No herbivore', name[:2], name, [3e6, 1e5, 6e6],
                              [-2, 0, 1, 2, 3, 5, 7, 9, 12, 14])
        mixture += rows
    stoichiometry = []
    for species in ('Cr', 'Ca', 'Mo', 'Co'):
        for time, scale in ((-4, 1.), (0, 1.), (1, 1.5)):
            volume = 100.
            nitrogen, carbon = NITROGEN[species]*volume*scale, CARBON[species]*volume
            metadata = dict(zip(runner.STOICHIOMETRY_META, [45000, time, species]))
            values = dict(zip(runner.STOICHIOMETRY_VALUES, [nitrogen, carbon, carbon/nitrogen, volume, 1e5, 1e7]))
            stoichiometry.append(dict(source_row=len(stoichiometry)+2, metadata=metadata, values=values, decoded=True))
    return dict(main=table(main, gated), stoichiometry=table(stoichiometry), no_herbivore=table(mixture))


class ChemostatRunnerChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.frozen = runner.freeze_computation(synthetic_tables('freeze'), CONFIG, AMENDMENT)
        cls.evaluation = runner.evaluation_computation(cls.frozen, synthetic_tables('evaluation'), CONFIG, AMENDMENT)
        cls.nominal = {row['variant_id']: row for row in cls.evaluation['variants']}['nitrogen-midpoint']

    def test_freeze_refuses_decoded_heldout_postpulse_rows(self):
        with self.assertRaises(RuntimeError):
            runner.freeze_computation(synthetic_tables('evaluation'), CONFIG, AMENDMENT)

    def test_calibration_uses_prepulse_medians_and_scenario_cost_ratios(self):
        calibration = self.frozen['calibration']
        for species, value in NITROGEN.items():
            self.assertAlmostEqual(calibration['densities']['nitrogen'][species], value)
        variants = {row['variant_id']: row for row in self.frozen['variants']}
        self.assertEqual(len(variants), 7)
        self.assertEqual(variants['nitrogen-lower']['pooled_bound_species'], ['Mo', 'Co'])
        self.assertAlmostEqual(variants['nitrogen-lower']['densities'][2], NITROGEN['Mo'])
        self.assertAlmostEqual(variants['nitrogen-upper']['cost_ratios'][2], CARBON['Co']/NITROGEN['Co'])
        np.testing.assert_allclose(variants['nitrogen-midpoint']['cost_ratios'], MIDPOINT_RATIOS)
        self.assertEqual(variants['biovolume-reference']['densities'], [1., 1., 1.])
        self.assertEqual(self.frozen['no_herbivore_mixture_vessels'], ['Mi1', 'Mi2'])

    def test_frozen_forecasts_cover_heldout_days_and_recover_known_strength(self):
        variant = {row['variant_id']: row for row in self.frozen['variants']}['nitrogen-midpoint']
        self.assertEqual(sorted(variant['forecasts']), ['1', '2', '3'])
        self.assertEqual(variant['forecasts']['1']['times'], [0., 1., 2., 3., 4., 5., 6., 7., 8., 9., 12.])
        fitted = variant['two_budget']['strength']
        self.assertEqual(fitted[0], 0.)
        for day in (2, 6, 12):
            self.assertAlmostEqual(fitted[day], strength(day), delta=.025*strength(day))
        self.assertTrue(all(count == 4 for count in variant['development']['contributors']))

    def test_two_budget_model_transfers_exactly_generated_reweighting(self):
        primary = self.nominal['primary']
        self.assertLess(primary['two_budget_cost_ratio']['equal_vessel_mean_time_weighted_total_variation'], .005)
        self.assertGreater(primary['persistence']['equal_vessel_mean_time_weighted_total_variation'], .03)
        self.assertEqual(self.nominal['ranking'][0], 'two_budget_cost_ratio')
        self.assertEqual(self.nominal['ordinal']['satisfied'], 3)
        self.assertEqual(self.nominal['ordinal']['scored'], 3)
        self.assertEqual(self.nominal['two_budget_capacity'], dict(scored=3, observed_departure_exceeds=0))

    def test_verdicts_require_every_pooled_scenario_and_a_vessel_majority(self):
        verdicts = {tuple(row['pair']): row for row in self.evaluation['verdicts']}
        self.assertEqual(verdicts[('development_mean_response', 'persistence')]['verdict'],
                         'development_mean_response outperforms persistence')
        self.assertEqual(verdicts[('equal_group_stock', 'persistence')]['verdict'],
                         'persistence outperforms equal_group_stock')
        budget = verdicts[('two_budget_cost_ratio', 'persistence')]
        self.assertGreaterEqual(budget['improvement_by_scenario']['midpoint'], .02)
        self.assertLess(budget['improvement_by_scenario']['lower'], .02)
        self.assertEqual(budget['verdict'], 'not distinguished')

    def test_two_budget_capacity_bounds_every_strength(self):
        variant = {row['variant_id']: row for row in self.frozen['variants']}['nitrogen-midpoint']
        for forecast in variant['forecasts'].values():
            baseline = np.array(forecast['baseline_shares'])
            capacity = forecast['two_budget_capacity_total_variation']
            self.assertGreater(capacity, 0.)
            self.assertLess(capacity, .1)
            for row in forecast['models']['two_budget_cost_ratio']['shares']:
                self.assertLessEqual(.5*np.sum(np.abs(np.array(row)-baseline)), capacity+1e-12)

    def test_persistence_total_error_and_retained_json_round_trip(self):
        stock = self.nominal['total_stock_equal_vessel_mean_absolute_log_error']
        self.assertGreater(stock['persistence'], 0.)
        self.assertEqual(json.loads(json.dumps(self.evaluation, allow_nan=False)), self.evaluation)
        self.assertEqual(json.loads(json.dumps(self.frozen, allow_nan=False)), self.frozen)
        envelope = self.nominal['pooled_envelope']['two_budget_cost_ratio']
        self.assertLessEqual(envelope['equal_vessel_mean_lower'], envelope['equal_vessel_mean_upper'])

    def test_workbook_gate_skips_heldout_postpulse_cells(self):
        headers = runner.META + [runner.TOTAL_HEADER] + runner.group_headers(CONFIG)
        with tempfile.TemporaryDirectory() as directory:
            paths = {}
            for key, rows in {'main': [['Monocultures', 'Bc', 'D1', 45000, 0, 3., 1., 1., 1.],
                                       ['Polycultures', '9d', 1, 45000, 0, 3., 1., 1., 1.],
                                       ['Polycultures', '9d', 1, 45001, 1, '#N/A', 1., 1., 1.]]}.items():
                workbook = openpyxl.Workbook()
                workbook.active.append(headers)
                for row in rows:
                    workbook.active.append(row)
                paths[key] = Path(directory)/f'{key}.xlsx'
                workbook.save(paths[key])
            for key, header in (('stoichiometry', runner.STOICHIOMETRY_META+runner.STOICHIOMETRY_VALUES),
                                ('no_herbivore', headers)):
                workbook = openpyxl.Workbook()
                workbook.active.append(header)
                paths[key] = Path(directory)/f'{key}.xlsx'
                workbook.save(paths[key])
            frozen = runner.read_tables(paths, CONFIG, 'freeze')
            self.assertEqual(frozen['main']['gated_rows'], 1)
            with self.assertRaises(ValueError):
                runner.read_tables(paths, CONFIG, 'evaluation')
            with self.assertRaises(ValueError):
                runner.read_tables(paths, CONFIG, 'unknown')


if __name__ == '__main__':
    unittest.main()
