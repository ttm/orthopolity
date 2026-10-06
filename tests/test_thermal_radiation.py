"""Thermal partition, spectral conservation, units, and limiting regimes."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from scipy.integrate import quad

from orthopolity.thermal_radiation import (
    C_LIGHT, H_PLANCK, K_BOLTZMANN, dimensionless_frequency,
    dimensionless_mode_energy, intensity_to_energy_per_mode, mode_density,
    planck_intensity, radiation_energy_density, rayleigh_jeans_intensity,
    suppression_factor,
)


ROOT = Path(__file__).resolve().parents[1]
_SPEC = importlib.util.spec_from_file_location("thermal_runner_for_tests", ROOT / "experiments/run_thermal_radiation.py")
RUNNER = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(RUNNER)


class ThermalRadiationTests(unittest.TestCase):
    def test_exact_si_constants(self):
        self.assertEqual(H_PLANCK, 6.62607015e-34)
        self.assertEqual(K_BOLTZMANN, 1.380649e-23)
        self.assertEqual(C_LIGHT, 299792458.)

    def test_suppression_small_and_large_arguments_without_overflow(self):
        self.assertEqual(suppression_factor(0), 1)
        small = np.array([1e-14, 1e-9, 1e-4])
        np.testing.assert_allclose(suppression_factor(small), 1 - small / 2 + small**2 / 12,
                                   rtol=2e-15, atol=1e-16)
        with np.errstate(over="raise", invalid="raise"):
            actual = suppression_factor([100, 1000, 1e300, np.inf])
        self.assertAlmostEqual(actual[0] / (100 * np.exp(-100)), 1)
        np.testing.assert_array_equal(actual[1:], [0, 0, 0])
        grid = np.geomspace(1e-10, 700, 1000)
        self.assertTrue(np.all(np.diff(suppression_factor(grid)) < 0))

    def test_geometric_partition_gives_thermal_mode_energy(self):
        # Direct Boltzmann sums over n quanta, independently of the closed form.
        levels = np.arange(20000, dtype=float)
        for x in (.02, .2, 1., 5., 15.):
            weights = np.exp(-x * levels)
            energy_over_kT = np.dot(x * levels, weights) / weights.sum()
            self.assertAlmostEqual(energy_over_kT / suppression_factor(x), 1, places=12)

    def test_classical_and_wien_spectral_limits(self):
        temperature = 2.725
        frequency = K_BOLTZMANN * temperature / H_PLANCK * np.array([1e-8, 1., 100.])
        planck = planck_intensity(frequency, temperature)
        rj = rayleigh_jeans_intensity(frequency, temperature)
        np.testing.assert_allclose(planck / rj, suppression_factor([1e-8, 1., 100.]), rtol=1e-13)
        self.assertLess(abs(planck[0] / rj[0] - 1), 1e-8)
        wien = 2 * H_PLANCK * frequency[-1]**3 / C_LIGHT**2 * np.exp(-100)
        self.assertAlmostEqual(planck[-1] / wien, 1, places=12)
        self.assertEqual(planck_intensity(0, temperature), 0)
        self.assertEqual(rayleigh_jeans_intensity(0, temperature), 0)
        self.assertEqual(planck_intensity(1e300, temperature), 0)

    def test_stefan_boltzmann_integral_and_temperature_scaling(self):
        # Integrate B_nu with dnu=(k_B T/h) dx, then multiply by pi for exitance.
        sigma = 2 * np.pi**5 * K_BOLTZMANN**4 / (15 * H_PLANCK**3 * C_LIGHT**2)
        for temperature in (2.725, 300.):
            scale = K_BOLTZMANN * temperature / H_PLANCK
            dimensionless_integral = quad(
                lambda x: float(planck_intensity(scale * x, temperature))
                / (2 * (K_BOLTZMANN * temperature)**3 / (H_PLANCK**2 * C_LIGHT**2)),
                0, 100, epsabs=1e-11, epsrel=1e-11)[0]
            self.assertAlmostEqual(dimensionless_integral / (np.pi**4 / 15), 1, places=11)
            exitance = np.pi * scale * (2 * (K_BOLTZMANN * temperature)**3
                                        / (H_PLANCK**2 * C_LIGHT**2)) * dimensionless_integral
            self.assertAlmostEqual(exitance / (sigma * temperature**4), 1, places=11)

    def test_mode_density_energy_and_intensity_conversions(self):
        temperature = 4.1
        frequency = np.geomspace(1e8, 1e12, 20)
        intensity = planck_intensity(frequency, temperature)
        energy = intensity_to_energy_per_mode(frequency, intensity)
        np.testing.assert_allclose(mode_density(frequency) * energy,
                                   radiation_energy_density(frequency, temperature), rtol=1e-14)
        np.testing.assert_allclose(energy / (K_BOLTZMANN * temperature),
                                   suppression_factor(dimensionless_frequency(frequency, temperature)), rtol=2e-14)
        np.testing.assert_allclose(dimensionless_mode_energy(frequency, intensity, temperature),
                                   intensity / rayleigh_jeans_intensity(frequency, temperature), rtol=2e-14)
        np.testing.assert_allclose(intensity_to_energy_per_mode(frequency, -intensity), -energy)
        # One MJy/sr is 1e-20 W m^-2 sr^-1 Hz^-1, without a wavenumber Jacobian.
        expected = 1e-20 * C_LIGHT**2 / (2 * (100e9)**2)
        self.assertAlmostEqual(intensity_to_energy_per_mode(100e9, 1e-20) / expected, 1)

    def test_invalid_values_and_zero_frequency_mode_conversion(self):
        for bad in (-1, np.nan):
            with self.assertRaises(ValueError):
                suppression_factor(bad)
        for function in (planck_intensity, rayleigh_jeans_intensity, radiation_energy_density):
            for temperature in (0, -1, np.nan, np.inf, [2, 3]):
                with self.assertRaises(ValueError):
                    function(1e9, temperature)
            for frequency in (-1, np.nan, np.inf):
                with self.assertRaises(ValueError):
                    function(frequency, 3)
        with self.assertRaises(ValueError):
            intensity_to_energy_per_mode(0, 1)
        with self.assertRaises(ValueError):
            intensity_to_energy_per_mode(1, np.nan)
        with self.assertRaises(ValueError):
            mode_density(-1)


class PublishedThermalProductTests(unittest.TestCase):
    def test_all_published_rows_and_original_columns_are_preserved(self):
        config = json.loads((ROOT / "configs/thermal_radiation_2026-10-06.json").read_text())
        table, covariance, correlation, _ = RUNNER.load_inputs(config)
        original = np.loadtxt(ROOT / config["source_directory"] / config["spectrum_filename"])
        self.assertEqual(len(table), 43)
        np.testing.assert_array_equal(table, original)
        converted = RUNNER.convert(table, config["temperature_kelvin"])
        for index, name in enumerate(("wavenumber_cm_inverse", "monopole_MJy_sr",
                                       "reported_residual_kJy_sr", "marginal_sigma_kJy_sr",
                                       "modeled_galaxy_kJy_sr")):
            np.testing.assert_array_equal(converted[name], original[:, index])
        np.testing.assert_array_equal(converted["row"], np.arange(43))
        np.testing.assert_allclose(np.diag(covariance), original[:, 3]**2)
        np.testing.assert_array_equal(np.diag(correlation), np.ones(43))

    def test_known_two_channel_covariance_conversion_preserves_cross_terms(self):
        # Select T so one kJy/sr maps to 1 at nu_1 and 1/4 at nu_2=2*nu_1.
        frequency = np.array([1e11, 2e11])
        temperature = 1e-23 * C_LIGHT**2 / (2 * K_BOLTZMANN * frequency[0]**2)
        covariance = np.array([[4., 1.], [1., 9.]])
        converted = RUNNER.mode_ratio_covariance(frequency, temperature, covariance)
        np.testing.assert_allclose(converted, [[4., .25], [.25, .5625]], rtol=2e-14)
        # A difference of channels retains the nonzero covariance contribution.
        contrast = np.array([1., -1.])
        self.assertAlmostEqual(float(contrast @ converted @ contrast), 4.0625, places=12)

    def test_pinned_input_corruption_is_rejected_before_analysis(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            directory = root / "inputs"
            directory.mkdir()
            spectrum = directory / "spectrum.txt"
            spectrum.write_text("1 2 3 4 5\n2 3 4 5 6\n")
            article = directory / "source.pdf"
            article.write_bytes(b"known source bytes for loader integrity fixture")
            sources = [dict(filename=path.name, sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                            size_bytes=path.stat().st_size) for path in (spectrum, article)]
            (directory / "sources.json").write_text(json.dumps(dict(sources=sources)))
            correlation = dict(q=[1, .2], source_file=article.name, source_sha256=sources[1]["sha256"])
            (directory / "correlation.json").write_text(json.dumps(correlation))
            config = dict(source_directory="inputs", source_manifest="sources.json",
                          spectrum_filename=spectrum.name, correlation_filename="correlation.json", expected_rows=2)
            with patch.object(RUNNER, "ROOT", root):
                self.assertEqual(RUNNER.load_inputs(config)[0].shape, (2, 5))
                # Same length and shape: only the pinned digest can reveal this change.
                spectrum.write_text("1 8 3 4 5\n2 3 4 5 6\n")
                with self.assertRaisesRegex(ValueError, "pinned hash/size"):
                    RUNNER.load_inputs(config)
                spectrum.write_text("1 2 3 4 5\n2 3 4 5 6\n")
                correlation["source_sha256"] = "0" * 64
                (directory / "correlation.json").write_text(json.dumps(correlation))
                with self.assertRaisesRegex(ValueError, "pinned primary source"):
                    RUNNER.load_inputs(config)


if __name__ == "__main__":
    unittest.main()
