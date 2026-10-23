"""Synthetic checks before opening BioMe numerical measurements."""
import importlib.util
from pathlib import Path

import numpy as np
import unittest

spec = importlib.util.spec_from_file_location('biome', Path(__file__).resolve().parents[1]/'experiments/audit_biome_stocks.py')
biome = importlib.util.module_from_spec(spec)
spec.loader.exec_module(biome)


class TestBioMeStocks(unittest.TestCase):
    def test_calibration_keeps_distinct_dyes(self):
        concentrations = np.broadcast_to(np.arange(450., -1., -50.), (25, 3, 10))
        for intercept, slope in ((.1, .002), (.3, .007)):
            result = biome.calibrate(intercept+slope*concentrations)
            self.assertAlmostEqual(result['intercept'], intercept)
            self.assertAlmostEqual(result['slope'], slope)
            assert result['maximum_held_concentration_error_uM'] < 1e-9


    def test_stock_and_control_drift_have_different_meanings(self):
        t = np.linspace(0, 2, 289)
        concentrations = np.zeros((289, 3, 10))
        concentrations[:, :, 0] = 400
        for p in range(1, 5):
            concentrations[:, :, 2*p] = (200*(1+np.exp(-p*t)))[:, None]
            concentrations[:, :, 2*p+1] = (200*(1-np.exp(-p*t)))[:, None]
        gain = (1+.1*t)[:, None, None]
        offset = (.2+.03*t)[:, None, None]
        traces = biome.trace_metrics(offset+.002*gain*concentrations,
                                     {'intercept': .2, 'slope': .002})
        np.testing.assert_allclose(traces['control_ratio_initial'], 1, atol=2e-15)
        assert traces['recovery_initial'][-1, 0, 1] > 1.2
        # Losing material only in porous wells cannot be erased by stable controls.
        concentrations[:, :, 2:] *= np.exp(-.2*t)[:, None, None]
        traces = biome.trace_metrics(.2+.002*concentrations,
                                     {'intercept': .2, 'slope': .002})
        np.testing.assert_allclose(traces['control_ratio_initial'][-1, :, 1:], np.exp(-.4))


    def test_no_clipping_or_invalid_normalization(self):
        a = np.broadcast_to(np.tile([.9, .199], 5), (289, 3, 10)).copy()
        traces = biome.trace_metrics(a, {'intercept': .2, 'slope': .002})
        self.assertAlmostEqual(traces['concentration_uM'][0, 0, 1], -.5)
        a[:, :, 0] = .1
        with self.assertRaisesRegex(ValueError, 'Nonpositive'):
            biome.trace_metrics(a, {'intercept': .2, 'slope': .002})


    def test_matching_block_does_not_decode_other_wavelength_or_rows(self):
        # Real workbook cells are not read by this test. Distinct sentinel rows
        # make a wrong dye/wavelength mapping fail rather than silently pass.
        import xml.etree.ElementTree as ET
        cells = {}
        for row, dye in ((28, 0), (57, 1)):
            for c in range(4+30*dye, 34+30*dye):
                address = f'{biome.column(c)}{row}'
                cell = ET.Element('c')
                ET.SubElement(cell, '{'+biome.NS['s']+'}v').text = str(100*dye+c)
                cells[address] = cell
        first = biome.matching_block(cells, 28, 1, 0)
        second = biome.matching_block(cells, 57, 1, 1)
        assert first[0, 0, 0] == 4
        assert second[0, 0, 0] == 134


    def test_nominal_micromolar_to_nanomole_conversion(self):
        a = np.broadcast_to(np.tile([.9, .1], 5), (289, 3, 10)).copy()
        traces = biome.trace_metrics(a, {'intercept': .1, 'slope': .002})
        # 400 micromolar * 0.25 mL = 100 nmol, or unit nominal pair recovery.
        np.testing.assert_allclose(traces['recovery_nominal'], 1)
