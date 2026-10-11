"""Analytic cases for the independent, optimizer-free verification."""
import importlib.util
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location('verify_capacity', Path(__file__).resolve().parents[1]/'experiments/verify_chemostat_capacity.py')
VERIFY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFY)


class CapacityVerificationTests(unittest.TestCase):
    def test_interior_intersection_and_degenerate_segments(self):
        self.assertAlmostEqual(VERIFY.geometric_minimum([[1., 0., 0.], [0., 1., 0.]], [[.5, .5, 0.]]*2), 0.)
        self.assertAlmostEqual(VERIFY.geometric_minimum([[1., 0., 0.], [0., 1., 0.]], [[0., 0., 1.]]*2), 1.)
        self.assertAlmostEqual(VERIFY.geometric_minimum([[.2, .3, .5]]*2, [[.3, .4, .3]]*2), .2)

    def test_parallel_disjoint_segments(self):
        self.assertAlmostEqual(VERIFY.geometric_minimum([[.1, .1, .8], [.2, .1, .7]], [[.1, .3, .6], [.2, .3, .5]]), .2)

    def test_price_extremes_and_failed_checks(self):
        span, upper = VERIFY.corner_price_bound([[1., 1.], [9., 9.]], [[1., 1.], [9., 9.]])
        self.assertEqual(span, 9.)
        self.assertEqual(upper, .5)
        with self.assertRaises(ValueError):
            VERIFY.close([.1, .2], [.1, .21], 'changed outcome')


if __name__ == '__main__':
    unittest.main()
