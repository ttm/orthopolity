import numpy as np
import unittest
from scipy.integrate import quad

from orthopolity.cell_division import (
    density, resource_per_log_size, summary_predictions, crossing_envelope,
)


class CellDivisionTests(unittest.TestCase):
    def test_integrated_probability_and_moments(self):
        for mean, variance in [(1., 0.), (2.7391, .9419), (1.4913, .054)]:
            for sampling in ["population", "lineage"]:
                with self.subTest(mean=mean, variance=variance, sampling=sampling):
                    expected = summary_predictions(mean, variance, sampling)
                    limits = (mean, 2 * mean) if variance == 0 else (mean / 100, mean * 100)
                    moments = [quad(lambda x: x**k * float(density(x, mean, variance, sampling)),
                                    *limits, epsabs=1e-10)[0] for k in range(3)]
                    self.assertAlmostEqual(moments[0], 1., places=8)
                    self.assertAlmostEqual(moments[1], expected["mean"], places=8)
                    self.assertAlmostEqual(moments[2] - moments[1]**2, expected["variance"], places=7)

    def test_mass_weighted_population_is_lineage(self):
        x = np.geomspace(.1, 30, 100)
        avg = summary_predictions(2., .5)["mean"]
        np.testing.assert_allclose(x * density(x, 2., .5) / avg,
                                   density(x, 2., .5, "lineage"), rtol=1e-13)
        np.testing.assert_allclose(x**2 * density(x, 2., .5) / avg,
                                   resource_per_log_size(x, 2., .5), rtol=1e-13)


    def test_fixed_birth_inverse_square_and_resource_plateau(self):
        x = np.array([1., 1.25, 1.75])
        np.testing.assert_allclose(density(x, 1., 0.), 2 / x**2)
        np.testing.assert_allclose(resource_per_log_size(x, 1., 0.), 1 / np.log(2))
        np.testing.assert_array_equal(crossing_envelope([.5, 1., 2.], 1., 0.), [0, 1, 0])


    def test_physical_units_rescale_means_not_variability(self):
        a, b = summary_predictions(2., .3), summary_predictions(20., 30.)
        self.assertAlmostEqual(b["mean"], 10 * a["mean"])
        self.assertAlmostEqual(b["cv"], a["cv"])


    def test_invalid_calibration_rejected(self):
        for mean, variance in [(0., 1.), (-1., 1.), (1., -1.), (np.nan, 1.)]:
            with self.subTest(mean=mean, variance=variance):
                with self.assertRaises(ValueError):
                    summary_predictions(mean, variance)
