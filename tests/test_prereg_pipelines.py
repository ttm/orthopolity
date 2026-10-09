import importlib.util
import unittest
from pathlib import Path

import numpy as np

from gof import csn_powerlaw

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'experiments' / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Pipelines(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.after = load('run_aftershocks')
        cls.lake = load('run_lake_gyration')
        cls.vol = load('run_volumetric_b')
        cls.ribbon = load('run_flare_ribbons')

    def test_csn_powerlaw_recovers_exponent(self):
        x = (1 - np.random.default_rng(1).random(20000)) ** (-1 / (2.3 - 1))
        self.assertAlmostEqual(csn_powerlaw(x)['alpha'], 2.3, delta=0.05)

    def test_poisson_productivity_slope(self):
        rng = np.random.default_rng(2)
        m = np.round(6.5 + rng.exponential(1 / np.log(10), 3000), 1)
        n = rng.poisson(0.3 * 10 ** (1.0 * (m - 6.5)))
        self.assertAlmostEqual(self.after.poisson_fit(m, n)[0], 1.0, delta=0.05)

    def test_gardner_knopoff_windows(self):
        self.assertAlmostEqual(float(self.after.gk_distance(7.0)), 10 ** (0.1238 * 7 + 0.983))
        self.assertAlmostEqual(float(self.after.gk_time(6.0)), 10 ** (0.5409 * 6 - 0.547))

    def test_ring_gyration(self):
        a, rg = self.lake.ring_gyration([0, 2, 2, 0], [0, 0, 2, 2])
        self.assertAlmostEqual(a, 4.0)
        self.assertAlmostEqual(rg, 2 / np.sqrt(6))
        th = np.linspace(0, 2 * np.pi, 4000, endpoint=False)
        self.assertAlmostEqual(self.lake.ring_gyration(np.cos(th), np.sin(th))[1], 1 / np.sqrt(2), places=4)

    def test_b_value_and_dimension(self):
        rng = np.random.default_rng(3)
        m = np.round(1.0 + rng.exponential(np.log10(np.e) / 1.5, 20000), 1)
        self.assertAlmostEqual(self.vol.b_value(m[m >= 1.2 - 1e-9], 1.2, rng, n_boot=20)[0], 1.5, delta=0.07)
        plane = np.column_stack([rng.uniform(0, 30, 2000), rng.uniform(0, 30, 2000), np.zeros(2000)])
        self.assertAlmostEqual(self.vol.correlation_dimension(plane)[0], 2.0, delta=0.12)

    def test_deming_exact_line(self):
        x = np.array([2.0, 2.2, 2.5, 2.8, 3.0])
        s, i = self.vol.deming(x, 0.5 * x, np.full(5, 0.01), np.full(5, 0.01))
        self.assertAlmostEqual(s, 0.5)
        self.assertAlmostEqual(i, 0.0)

    def test_ribbon_decision_rule(self):
        self.assertEqual(self.ribbon.verdict(1.9, 2.2, 0.5)[1], 'supports H_territory')
        self.assertEqual(self.ribbon.verdict(2.2, 2.5, 0.5)[1], 'supports H_fractal')
        self.assertEqual(self.ribbon.verdict(1.9, 2.5, 0.5)[1], 'inconclusive')
        self.assertTrue(self.ribbon.verdict(1.9, 2.2, 0.05)[1].startswith('inconclusive'))


if __name__ == '__main__':
    unittest.main()
