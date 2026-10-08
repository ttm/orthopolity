import unittest
import numpy as np
from orthopolity import resource_exponents, simple_rationals, chance_match


class ResourceExponents(unittest.TestCase):
    def test_density_kind(self):
        # p(k) ∝ k^-3: linear-orthopolic in k^3, log-orthopolic in k^2.
        r = resource_exponents(3, 'density')
        self.assertEqual((r['alpha'], r['d_log'], r['d_lin']), (3, 2, 3))

    def test_survival_and_rank_conversions(self):
        self.assertAlmostEqual(resource_exponents(1.0, 'survival')['alpha'], 2.0)
        self.assertAlmostEqual(resource_exponents(0.5, 'rank')['alpha'], 3.0)
        # Zipf rank exponent 1 is zeta = 1, alpha = 2: log-orthopolic in the size itself.
        self.assertAlmostEqual(resource_exponents(1.0, 'rank')['d_log'], 1.0)

    def test_invalid(self):
        for args in [(0, 'density'), (np.nan, 'density'), (2, 'spectrum')]:
            with self.assertRaises(ValueError):
                resource_exponents(*args)


class ChanceMatch(unittest.TestCase):
    def test_integers(self):
        # Within 0.1 of 1, 2 or 3 covers 0.6 of [0.5, 3.5].
        self.assertAlmostEqual(chance_match([1, 2, 3], 0.1, 0.5, 3.5), 0.2)

    def test_overlap_and_clipping(self):
        self.assertAlmostEqual(chance_match([1.0, 1.05], 0.1, 0, 2), 0.125)
        self.assertAlmostEqual(chance_match([-5, 9, 1], 0.5, 0, 2), 0.5)
        self.assertEqual(chance_match([], 0.1, 0, 1), 0.0)

    def test_small_denominators_cover_the_range(self):
        q = simple_rationals(4, 1.5, 4)
        self.assertIn(7 / 4, q)
        self.assertEqual(len(q), len(set(np.round(q, 12))))
        # Halves, thirds and quarters within ±0.1 cover 90% of the range; sixths leave no gap.
        self.assertAlmostEqual(chance_match(q, 0.1, 1.5, 4), 0.9)
        self.assertAlmostEqual(chance_match(simple_rationals(6, 1.5, 4), 0.1, 1.5, 4), 1.0)
        self.assertLess(chance_match(simple_rationals(1, 1.5, 4), 0.02, 1.5, 4), 0.05)


if __name__ == '__main__':
    unittest.main()
