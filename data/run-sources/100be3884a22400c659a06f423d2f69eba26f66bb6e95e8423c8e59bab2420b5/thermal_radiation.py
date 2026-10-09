"""Thermal photon energy per electromagnetic mode and spectral conversions.

Spectral intensities are per unit frequency, in W m^-2 sr^-1 Hz^-1. The mode
density includes both transverse polarizations. Thermal energy excludes the
temperature-independent zero-point term; all temperatures are positive kelvin.
"""
from __future__ import annotations

import numpy as np


# Exact values defining the SI (not fitted parameters).
H_PLANCK = 6.62607015e-34
K_BOLTZMANN = 1.380649e-23
C_LIGHT = 299792458.0


def _frequency(frequency_hz, *, positive=False):
    frequency = np.asarray(frequency_hz, dtype=float)
    if (not np.isfinite(frequency).all() or np.any(frequency < 0)
            or (positive and np.any(frequency == 0))):
        raise ValueError("frequency must be finite and nonnegative (positive for mode conversion)")
    return frequency


def _temperature(temperature_K):
    temperature = np.asarray(temperature_K, dtype=float)
    if temperature.ndim != 0 or not np.isfinite(temperature) or temperature <= 0:
        raise ValueError("temperature must be a finite positive scalar in kelvin")
    return float(temperature)


def _scalar_or_array(value):
    return float(value) if value.ndim == 0 else value


def suppression_factor(x):
    """Return x/(exp(x)-1), with f(0)=1 and f(+infinity)=0 by continuity.

    The large-x branch uses exp(-x) to avoid overflow. Negative values and NaNs
    have no meaning for positive-frequency thermal photons and are rejected.
    """
    x = np.asarray(x, dtype=float)
    if np.isnan(x).any() or np.any(x < 0):
        raise ValueError("x must be nonnegative and not NaN")
    result = np.zeros_like(x)
    result[x == 0] = 1
    small = (x > 0) & (x <= 50)
    result[small] = x[small] / np.expm1(x[small])
    large = (x > 50) & np.isfinite(x)
    decay = np.exp(-x[large])
    result[large] = x[large] * decay / (1 - decay)
    return _scalar_or_array(result)


def dimensionless_frequency(frequency_hz, temperature_K):
    """Return h nu / (k_B T); overflow represents the Wien-limit infinity."""
    frequency = _frequency(frequency_hz)
    temperature = _temperature(temperature_K)
    with np.errstate(over="ignore"):
        result = (H_PLANCK / K_BOLTZMANN) * frequency / temperature
    return _scalar_or_array(result)


def _log_rj(frequency, temperature):
    with np.errstate(divide="ignore"):
        return np.log(2 * K_BOLTZMANN) + np.log(temperature) + 2 * (np.log(frequency) - np.log(C_LIGHT))


def rayleigh_jeans_intensity(frequency_hz, temperature_K):
    """Classical B_nu = 2 k_B T nu²/c², including its zero-frequency limit."""
    frequency = _frequency(frequency_hz)
    temperature = _temperature(temperature_K)
    with np.errstate(over="ignore"):
        result = np.exp(_log_rj(frequency, temperature))
    if not np.isfinite(result).all():
        raise ValueError("Rayleigh--Jeans intensity exceeds floating-point range")
    return _scalar_or_array(result)


def planck_intensity(frequency_hz, temperature_K):
    """Planck B_nu, evaluated stably into the classical and Wien limits."""
    frequency = _frequency(frequency_hz)
    temperature = _temperature(temperature_K)
    x = np.asarray(dimensionless_frequency(frequency, temperature))
    log_suppression = np.full_like(x, -np.inf)
    small = x <= 50
    log_suppression[small] = np.log(suppression_factor(x[small]))
    large = (x > 50) & np.isfinite(x)
    log_suppression[large] = np.log(x[large]) - x[large] - np.log1p(-np.exp(-x[large]))
    with np.errstate(over="ignore"):
        result = np.exp(_log_rj(frequency, temperature) + log_suppression)
    if not np.isfinite(result).all():
        raise ValueError("Planck intensity exceeds floating-point range")
    return _scalar_or_array(result)


def mode_density(frequency_hz):
    """Electromagnetic modes per volume per Hz, g_nu=8 pi nu²/c³."""
    frequency = _frequency(frequency_hz)
    with np.errstate(over="ignore"):
        result = (8 * np.pi / C_LIGHT) * (frequency / C_LIGHT) ** 2
    if not np.isfinite(result).all():
        raise ValueError("mode density exceeds floating-point range")
    return _scalar_or_array(result)


def radiation_energy_density(frequency_hz, temperature_K):
    """Planck energy per volume per Hz, u_nu=4 pi B_nu/c."""
    result = (4 * np.pi / C_LIGHT) * np.asarray(planck_intensity(frequency_hz, temperature_K))
    return _scalar_or_array(result)


def intensity_to_energy_per_mode(frequency_hz, intensity_si):
    """Convert isotropic per-Hz intensity to thermal energy per mode in joules.

    Signed finite input is allowed so the same linear conversion also applies
    to measurement residuals. The frequency must be strictly positive.
    """
    frequency = _frequency(frequency_hz, positive=True)
    intensity = np.asarray(intensity_si, dtype=float)
    if not np.isfinite(intensity).all():
        raise ValueError("intensity must be finite")
    frequency, intensity = np.broadcast_arrays(frequency, intensity)
    with np.errstate(over="ignore", invalid="ignore"):
        result = intensity * .5 * (C_LIGHT / frequency) ** 2
    if not np.isfinite(result).all():
        raise ValueError("energy per mode exceeds floating-point range")
    return _scalar_or_array(result)


def dimensionless_mode_energy(frequency_hz, intensity_si, temperature_K):
    """Return E_mode/(k_B T)=I_nu/B_nu^RJ for a specified positive T."""
    temperature = _temperature(temperature_K)
    result = np.asarray(intensity_to_energy_per_mode(frequency_hz, intensity_si)) / (K_BOLTZMANN * temperature)
    return _scalar_or_array(result)
