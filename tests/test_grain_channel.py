"""Physics, estimator and response-isolation checks before real calibration."""
import csv
import math
from pathlib import Path
import shutil

import numpy as np
import tempfile
import unittest

from orthopolity.grain_channel import (read_predictors, wall_factors, shape_factor,
                                      transport, fit_transport, weights)

BASE = Path(__file__).resolve().parents[1]/'data/grain-channel/2026-10-15'


class GrainChannelTests(unittest.TestCase):
    def test_synthetic_law_recovery(self):
        for threshold in (0., .04, .13):
            x = np.linspace(.02, .4, 31)
            y = transport(x, 6.3, threshold)
            fit = fit_transport(x, y, np.ones(len(x)))
            np.testing.assert_allclose(fit['amplitude'], 6.3, rtol=1e-7)
            np.testing.assert_allclose(fit['threshold'], threshold, atol=1e-9)
            assert np.max(abs(transport(x, fit['amplitude'], fit['threshold'])-y)) < 1e-8


    def test_scaling_and_order_invariance(self):
        x = np.array([.1, .15, .2, .27, .33, .4])
        y = transport(x, 8, .06)*np.array([.9, 1.1, 1., 1.03, .98, 1.02])
        w = np.arange(1, 7)
        a = fit_transport(x, y, w)
        b = fit_transport(x[::-1]*4, y[::-1]*3, w[::-1])
        np.testing.assert_allclose(b['threshold'], a['threshold']*4, rtol=1e-6)
        np.testing.assert_allclose(b['amplitude'], a['amplitude']*3/8, rtol=1e-6)


    def test_shape_drag_ratio_and_neutral_spheres(self):
        rs, rf, g, d, ws, wo, corey = 2600., 995., 9.81, .004, .3, .4, .7
        cd, c0 = [4*(rs/rf-1)*g*d/(3*w*w) for w in (ws, wo)]
        value = shape_factor(corey, ws, wo, 35., .02)
        self.assertAlmostEqual(value['cstar'], corey*cd/c0)
        self.assertAlmostEqual(shape_factor(1, .4, .4, 24, .03)['shape'], 1)
        with self.assertRaises(ValueError):
            shape_factor(1, .4, .4, 24, 1)


    def test_wall_momentum_balance_and_complex_convention(self):
        p = wall_factors(.065, .05, .02, .00284, .0049)
        assert p['radius_factor'] <= p['guo'] <= 1
        # Recover wall stress from momentum balance, taking depth-slope stress=1.
        wall_stress = (1-p['guo'])*p['alpha']/2
        average = (2*.05*wall_stress + .065*p['guo'])/(2*.05+.065)
        self.assertAlmostEqual(average, p['radius_factor'])
        # A negative radicand remains explicit. Taking Re(sqrt(z)) is not Re(F).
        bad = wall_factors(.065, .05, .02, .02, .0049)
        assert bad['radicand'] < 0
        assert bad['guo'] > 1


    def test_source_response_poisoning_cannot_change_predictors(self):
        with tempfile.TemporaryDirectory() as directory:
            self._poison_check(Path(directory))

    def _poison_check(self, tmp_path):
        expected = read_predictors(BASE)
        shutil.copytree(BASE/'02_data', tmp_path/'02_data')
        prohibited = ('q8', 'dq8', 'mass_flux', 'dmass_flux', 'volume_flux', 'dvolume_flux',
                      'feed_flux', 'q8_feed', 'tau8', 'dtau8', 'tau8_corrected', 'dtau8_corrected',
                      'taub', 'dtaub', 'taub_bed', 'taub_water', 'taub_corrected', 'dtaub_corrected',
                      'shear_stress', 'reynolds_stress', 'tau_m', 'Fqs', 'FS', 'FG', 'FVB', 'FR')
        for path in (tmp_path/'02_data').rglob('*'):
            if path.suffix not in ('.csv', '.txt'):
                continue
            with path.open(newline='') as f:
                reader = csv.DictReader(f)
                fields, rows = reader.fieldnames, list(reader)
            for row in rows:
                for key in prohibited:
                    if key in row:
                        row[key] = 'RESPONSE_MUST_NOT_BE_CONVERTED'
            with path.open('w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader(); writer.writerows(rows)
        assert read_predictors(tmp_path) == expected


    def test_source_cohort_and_equal_material_measure(self):
        data = read_predictors(BASE)
        rows = data['rows']
        assert len(rows) == 38
        assert len(data['excluded']) == 3
        assert all(r['qualified_hydraulics'] for r in rows)
        new = [r for r in rows if r['cohort'] == 'wide']
        w = weights(new)
        assert math.isclose(sum(w[i] for i,r in enumerate(new) if r['grain']=='sphere'), .5)
        assert math.isclose(sum(w[i] for i,r in enumerate(new) if r['grain']=='gravel'), .5)


    def test_invalid_calibration_rejected(self):
        with self.assertRaises(ValueError):
            fit_transport([.1,.2,.3], [0,0,0], [1,1,1])
        with self.assertRaises(ValueError):
            fit_transport([.1,.2,.3], [1,-1,1], [1,1,1])
