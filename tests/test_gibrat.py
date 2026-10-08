import unittest
import numpy as np
from orthopolity import gibrat_zeta


def stationary_sizes(g, sigma2, d, h, n, rng):
    """Exact draw: GBM observed at an exponential age with rate d + h."""
    age = rng.exponential(1 / (d + h), n)
    return np.exp((g - sigma2 / 2) * age + np.sqrt(sigma2 * age) * rng.standard_normal(n))


class GibratChecks(unittest.TestCase):
    def test_balance_gives_zipf(self):
        # phi = d + h - g = 0: entry injects no share of the normalized total.
        for g, sigma2, d in [(0.03, 0.04, 0.0), (0.1, 0.5, 0.02), (0.05, 0.04, 0.01), (0.02, 0.2, 0.05)]:
            self.assertAlmostEqual(gibrat_zeta(g, sigma2, d=d, h=g - d), 1.0, places=12)

    def test_root_and_injection_identity(self):
        for g, sigma2, d, h in [(0.02, 0.04, 0.0, 0.05), (0.08, 0.3, 0.01, 0.02), (0.1, 0.1, 0.03, 0.12)]:
            z = gibrat_zeta(g, sigma2, d, h)
            self.assertAlmostEqual(sigma2 / 2 * z * z + (g - sigma2 / 2) * z - (d + h), 0, places=12)
            self.assertAlmostEqual((z - 1) * (g + sigma2 * z / 2), d + h - g, places=12)
            self.assertEqual(z > 1, d + h > g)

    def test_gabaix_barrier_limit(self):
        # Without drift relative to entrants, slow exit gives a Zipf-like tail.
        self.assertLess(abs(gibrat_zeta(-1e-9, 0.04, 0, 1e-9) - 1), 1e-6)

    def test_exact_sampler_matches_root(self):
        rng = np.random.default_rng(20261008)
        for g, sigma2, d, h in [(0.05, 0.1, 0.0, 0.05), (0.03, 0.1, 0.0, 0.05), (0.07, 0.1, 0.0, 0.05)]:
            x = stationary_sizes(g, sigma2, d, h, 400000, rng)
            tail = x[x > 1]  # the upper branch is exactly Pareto above the entry size
            zeta_hat = len(tail) / np.log(tail).sum()
            z = gibrat_zeta(g, sigma2, d, h)
            self.assertLess(abs(zeta_hat - z), 6 * z / np.sqrt(len(tail)))

    def test_invalid_rates(self):
        for args in [(0.1, 0, 0, 0.1), (0.1, 0.1, 0, 0), (np.nan, 0.1, 0, 0.1)]:
            with self.assertRaises(ValueError):
                gibrat_zeta(*args)


if __name__ == '__main__':
    unittest.main()
