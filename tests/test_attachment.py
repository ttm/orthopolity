"""Structural and analytic checks for the one-link attachment benchmark."""
import unittest
import numpy as np

from orthopolity.attachment import (
    attachment_tree_degrees, attachment_tree_snapshots,
    finite_expected_degree_snapshots, stationary_degree_law,
)


class AttachmentChecks(unittest.TestCase):
    def test_tree_budget_snapshots_and_reproducibility(self):
        sizes = [2, 80, 500]
        a = attachment_tree_snapshots(sizes, .5, np.random.default_rng(172))
        b = attachment_tree_snapshots(sizes, .5, np.random.default_rng(172))
        for n in sizes:
            self.assertEqual(len(a[n]), n)
            self.assertEqual(a[n].sum(), 2 * (n - 1))
            self.assertTrue(np.all((a[n] >= 1) & (a[n] <= n - 1)))
            np.testing.assert_array_equal(a[n], b[n])
        self.assertTrue(np.all(a[500][:80] >= a[80]))

    def test_finite_linear_expectation_matches_enumerated_small_tree(self):
        # At n=4 a linear seed-edge tree is a 3-leaf star with probability 1/2
        # and a path with probability 1/2. Their wedge totals are 3 and 2.
        result = finite_expected_degree_snapshots([4], 4)[4]
        np.testing.assert_allclose(result['expected_count'], [2.5, 1, .5, 0])
        self.assertAlmostEqual(result['expected_full_wedges'], 2.5)
        self.assertAlmostEqual(result['unrepresented_expected_count'], 0)

    def test_truncated_counts_preserve_exact_lower_degree_reference(self):
        short = finite_expected_degree_snapshots([200], 8, attractiveness=.5)[200]
        full = finite_expected_degree_snapshots([200], 200, attractiveness=.5)[200]
        np.testing.assert_allclose(short['expected_count'], full['expected_count'][:8])
        self.assertAlmostEqual(full['expected_count'].sum(), 200, places=10)
        self.assertAlmostEqual(np.dot(full['degree'], full['expected_count']), 398, places=10)
        self.assertAlmostEqual(
            np.dot(full['degree'] * (full['degree'] - 1) / 2, full['expected_count']),
            full['expected_full_wedges'], places=9)
        self.assertAlmostEqual(short['unrepresented_expected_count'], full['expected_count'][8:].sum())

    def test_limiting_uniform_and_linear_laws(self):
        uniform = stationary_degree_law(0, 100)
        np.testing.assert_allclose(uniform['probability'], 2.0 ** -uniform['degree'])
        linear = stationary_degree_law(1, 1000)
        k = linear['degree']
        np.testing.assert_allclose(linear['probability'], 4 / (k * (k + 1) * (k + 2)), rtol=1e-12)
        # The missing probability is the exact telescoping upper tail.
        self.assertAlmostEqual(linear['unrepresented_probability'], 2 / (1001 * 1002), places=13)

    def test_sublinear_self_consistency_and_cutoff_stability(self):
        a = stationary_degree_law(.5, 512)
        b = stationary_degree_law(.5, 1024)
        self.assertTrue(1 < a['normalizer'] < np.sqrt(2))
        self.assertAlmostEqual(a['normalizer'], b['normalizer'], places=12)
        self.assertAlmostEqual(a['probability'].sum(), 1, places=11)
        self.assertAlmostEqual(a['represented_mean_degree'], 2, places=10)
        self.assertAlmostEqual(
            np.dot(np.sqrt(a['degree']), a['probability']), a['normalizer'], places=11)
        c = stationary_degree_law(.5, 2048)
        wedge_b = np.dot(b['degree']*(b['degree']-1)/2, b['probability'])
        wedge_c = np.dot(c['degree']*(c['degree']-1)/2, c['probability'])
        self.assertAlmostEqual(wedge_b, wedge_c, places=11)
        self.assertAlmostEqual(wedge_b, 2.64928949209306, places=11)

    def test_generator_matches_nontrivial_exact_linear_count_reference(self):
        n, reps = 300, 100
        counts = np.zeros(5)
        for rep in range(reps):
            degree = attachment_tree_degrees(n, 1, np.random.default_rng(1000 + rep))
            counts += np.bincount(degree, minlength=6)[1:6]
        expected = finite_expected_degree_snapshots([n], 5)[n]['expected_count']
        np.testing.assert_allclose(counts / reps, expected, atol=1.5)

    def test_nonlinear_growth_changes_condensation_with_resource_fixed(self):
        n = 3000
        sub = attachment_tree_degrees(n, .5, np.random.default_rng(81))
        sup = attachment_tree_degrees(n, 1.5, np.random.default_rng(81))
        self.assertLess(sub.max() / (n - 1), .05)
        self.assertGreater(sup.max() / (n - 1), .6)
        wedges_sub = sub * (sub - 1) / 2
        wedges_sup = sup * (sup - 1) / 2
        self.assertLess(wedges_sub.max() / wedges_sub.sum(), .1)
        self.assertGreater(wedges_sup.max() / wedges_sup.sum(), .9)

    def test_invalid_and_unclosed_reference_requests_are_rejected(self):
        rng = np.random.default_rng(12)
        for call in (
            lambda: attachment_tree_degrees(3, -1, rng),
            lambda: attachment_tree_degrees(3, 1, rng, attractiveness=-1),
            lambda: attachment_tree_snapshots([10, 5], 1, rng),
            lambda: finite_expected_degree_snapshots([100], 50, gamma=.5),
            lambda: stationary_degree_law(1.5, 100),
        ):
            with self.assertRaises(ValueError):
                call()


if __name__ == '__main__':
    unittest.main()
