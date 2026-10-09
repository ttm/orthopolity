"""Size-law and restoration checks use synthetic lineages, never study outcomes."""
import importlib.util
import json
import math
import unittest
from pathlib import Path

import numpy as np

from orthopolity.size_budget import (
    absolute_errors, carrying_capacity, fit_line, pairwise_verdict, restoration_forecasts, size_law_forecasts,
)

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('dunaliella_runner', ROOT/'experiments/run_dunaliella_size_budget.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
CONFIG = json.loads((ROOT/'configs/dunaliella_size_budget_2026-10-02.json').read_text())
PARTITION = json.loads((ROOT/'configs/dunaliella_size_budget_2026-10-02_partition.json').read_text())


def synthetic(cost_dimension=.8, deficits=None, scramble=None):
    """Lineages under one budget: log K = 12 + (1-d) log V, with history offsets."""
    deficits = deficits or {'Replete': 0., 'N-Deplete': -.1, 'P-Deplete': .3}
    volumes = {'S': 85., 'C': 185., 'L': 900.}
    sizes, k = {}, {}
    for code, base in volumes.items():
        for rep in range(1, 11):
            lineage = f'{code}.{rep}'
            for history, deficit in deficits.items():
                log_volume = math.log(base*(1+.03*rep))+(.2 if history != 'Replete' else 0.)
                sizes[(lineage, history)] = log_volume
                k[(lineage, history)] = 12.+(1-cost_dimension)*sizes[(lineage, 'Replete')]+deficit
    if scramble:
        for key in k:
            if key[0].split('.')[0] in scramble:
                k[key] = 99.
    return sizes, k


class SizeBudgetChecks(unittest.TestCase):
    def test_carrying_capacity_requires_two_wells_per_day(self):
        wells = {'P1': {0.: 1., 1.: 3., 2.: 2.}, 'P2': {0.: 1., 1.: 5., 2.: math.nan}, 'P3': {0.: 1., 1.: math.nan}}
        self.assertEqual(carrying_capacity(wells), 4.)
        self.assertIsNone(carrying_capacity({'P1': {0.: 1.}}))

    def test_fit_line_and_degenerate_inputs(self):
        self.assertEqual(tuple(round(v, 12) for v in fit_line([0., 1., 2.], [1., 3., 5.])), (1., 2.))
        for x, y in [([1., 1.], [0., 1.]), ([1.], [1.]), ([0., np.nan], [1., 2.])]:
            with self.assertRaises(ValueError):
                fit_line(x, y)

    def test_size_law_recovers_cost_dimension_and_ignores_heldout_outcomes(self):
        development = {f'D{i}': dict(log_volume=math.log(v), log_k=12.+.2*math.log(v)) for i, v in enumerate([80., 100., 190., 210.])}
        held = {'H1': dict(log_volume=math.log(900.), log_k=-999.)}
        result = size_law_forecasts(development, held, {'assigned': .5})
        self.assertAlmostEqual(result['parameters']['size_law']['implied_cost_dimension'], .8)
        self.assertAlmostEqual(result['forecasts']['size_law']['H1'], 12.+.2*math.log(900.))
        self.assertAlmostEqual(result['parameters']['constant_cells']['slope'], 1.)
        self.assertEqual(result['parameters']['constant_biovolume']['slope'], 0.)
        self.assertEqual(result['parameters']['assigned']['slope'], .5)
        held['H1']['log_k'] = 5.
        self.assertEqual(size_law_forecasts(development, held, {'assigned': .5}), result)

    def test_restoration_anchors_only_when_replete_input_is_supplied(self):
        development = {f'D{i}': dict(log_k=10.3+.1*i, replete_log_k=10.+.1*i, log_volume=float(i)) for i in range(3)}
        result = restoration_forecasts(development, {'H': dict(log_volume=1.5, replete_log_k=11.), 'G': dict(log_volume=2.)})
        self.assertAlmostEqual(result['parameters']['development_mean_deficit'], .3)
        self.assertEqual(result['forecasts']['full_restoration'], {'H': 11.})
        self.assertAlmostEqual(result['forecasts']['history_offset']['H'], 11.3)
        self.assertEqual(set(result['forecasts']['constant_history']), {'G', 'H'})

    def test_errors_share_units_and_verdict_needs_both_folds(self):
        errors, units = absolute_errors({'a': {'x': 1., 'y': 2.}, 'b': {'x': 1.5, 'y': 2., 'z': 0.}},
                                        {'x': 1., 'y': 3., 'z': None})
        self.assertEqual(units, ['x', 'y'])
        self.assertEqual(errors['b'], {'x': .5, 'y': 1.})
        good = {'a': {'u1': .1, 'u2': .1, 'u3': .3}, 'b': {'u1': .3, 'u2': .3, 'u3': .2}}
        weak = {'a': {'u1': .1, 'u2': .2, 'u3': .2}, 'b': {'u1': .12, 'u2': .21, 'u3': .2}}
        self.assertEqual(pairwise_verdict([good, good], 'a', 'b', .05)['verdict'], 'a outperforms b')
        self.assertEqual(pairwise_verdict([good, weak], 'a', 'b', .05)['verdict'], 'not distinguished')
        self.assertEqual(pairwise_verdict([good, good], 'b', 'a', .05)['verdict'], 'a outperforms b')

    def test_runner_forecasts_depend_on_heldout_lineages_only_through_volume(self):
        sizes, k = synthetic()
        slopes = {'assigned_carbon_cost': .1, 'assigned_nitrogen_cost': .2}
        reference = runner.forecast_computation(k, sizes, CONFIG, PARTITION, slopes)
        for fold, held in (('A', 'L'), ('B', 'S')):
            _, scrambled = synthetic(scramble={held})
            changed = runner.forecast_computation(scrambled, sizes, CONFIG, PARTITION, slopes)
            self.assertEqual(changed[fold], reference[fold])
        self.assertAlmostEqual(reference['A']['size_law']['parameters']['size_law']['implied_cost_dimension'], .8)

    def test_runner_evaluation_scores_exact_law_and_full_restoration(self):
        sizes, k = synthetic(deficits={'Replete': 0., 'N-Deplete': 0., 'P-Deplete': 0.})
        slopes = {'assigned_carbon_cost': .2, 'assigned_nitrogen_cost': .5}
        frozen = json.loads(json.dumps(runner.forecast_computation(k, sizes, CONFIG, PARTITION, slopes)))
        result = runner.evaluation_computation(frozen, k, CONFIG)
        for fold in ('A', 'B'):
            e1 = result['folds'][fold]['E1']['mean_absolute_log_error']
            self.assertAlmostEqual(e1['size_law'], 0.)
            self.assertAlmostEqual(e1['assigned_carbon_cost'], 0.)
            self.assertGreater(e1['constant_cells'], .5)
            self.assertAlmostEqual(result['folds'][fold]['E2']['mean_absolute_log_error']['full_restoration'], 0.)
            self.assertEqual(len(result['folds'][fold]['E2']['scored_units']), 20)
        verdicts = {tuple(row['pair']): row['verdict'] for row in result['verdicts']['E1']}
        self.assertEqual(verdicts[('size_law', 'constant_cells')], 'size_law outperforms constant_cells')
        self.assertEqual(verdicts[('size_law', 'constant_biovolume')], 'size_law outperforms constant_biovolume')


if __name__ == '__main__':
    unittest.main()
