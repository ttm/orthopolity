"""Synthetic scientific/staging checks; no raw impedance observations read."""
import importlib.util
import json
from pathlib import Path
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('rlc', ROOT/'experiments/run_rlc_boundary.py')
rlc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rlc)
CFG = json.loads((ROOT/rlc.CONFIG).read_text())
v_spec = importlib.util.spec_from_file_location('rlc_verify', ROOT/'experiments/verify_rlc_boundary.py')
verify = importlib.util.module_from_spec(v_spec)
v_spec.loader.exec_module(verify)


class TestRLCBoundary(unittest.TestCase):
    def test_schema_does_not_expose_numeric_strings(self):
        result = rlc.schema({'z': ['1234-5678i'], 'other': 'sensitive1234'})
        self.assertNotIn('1234', json.dumps(result))
        self.assertEqual(result['z'], {'length': 1, 'item_types': ['str']})

    def test_state_equations_and_energy_balance(self):
        r, l, c = 9.7, .005, 2.2e-6
        for f in (100, 700, 1480, 1700, 10000):
            omega = 2*np.pi*f
            # Current input 1: C Vdot=1-i; L idot=V-Ri.
            v, current = np.linalg.solve([[1j*omega*c, 1], [-1, r+1j*omega*l]], [1, 0])
            np.testing.assert_allclose(v, rlc.impedance(f, r, l, c), rtol=2e-14)
        v, current, source = 1.3, -.2, .4
        energy_rate = c*v*((source-current)/c)+l*current*((v-r*current)/l)
        self.assertAlmostEqual(energy_rate, v*source-r*current**2)

    def test_rc_sign_and_shared_nullspace(self):
        g = np.array([[2., -1., 0.], [-1., 3., -1.], [0., -1., 2.]])
        c = np.diag([.4, .8, 1.2])
        b = np.array([1., 0., -1.])
        for omega in (.001, 1., 1000.):
            v = np.linalg.solve(g+1j*omega*c, b)
            self.assertLessEqual((b@v).imag, 0)
            self.assertAlmostEqual((b@v).imag, -omega*np.vdot(v, c@v).real)
        # Both have a common constant null vector; the differential port is orthogonal.
        g = np.array([[1., -1.], [-1., 1.]])
        b = np.array([1., -1.])
        v = np.linalg.pinv(g+1j*.3*g)@b
        self.assertAlmostEqual((b@v).imag, -.3*np.vdot(v, g@v).real)

    def test_noncollocated_output_does_not_have_sign_guarantee(self):
        v = np.linalg.solve(np.eye(2)+1j*np.eye(2), [1, 0])
        self.assertGreater((np.array([-1, 0])@v).imag, 0)

    def test_tolerance_corners_bound_interior_and_classify_signs(self):
        interval, union = rlc.intervals(CFG)
        for l in np.linspace(.00495, .00505, 7):
            for c in np.linspace(1.98e-6, 2.42e-6, 7):
                x = rlc.crossing(9.7, l, c)
                self.assertTrue(interval[0]-1e-10 <= x <= interval[1]+1e-10)
                self.assertGreater(rlc.impedance(interval[0]*.9, 9.7, l, c).imag, 0)
                self.assertLess(rlc.impedance(interval[1]*1.1, 9.7, l, c).imag, 0)
        self.assertLessEqual(union[0], interval[0])
        self.assertGreater(union[1], interval[1])

    def test_quadrature_and_rc_distance_bound(self):
        f = np.array([100., 1000., 10000.])
        np.testing.assert_allclose(rlc.quadrature(f), [.25, .5, .25])
        observed = np.array([3+4j, 2-5j, 1+2j])
        for candidate in (np.ones(3), np.full(3, -3j), observed.real+1j*np.minimum(observed.imag, 0)):
            self.assertGreaterEqual(float(np.sum(np.abs(candidate-observed)**2)),
                                    float(np.sum(np.maximum(observed.imag, 0)**2)))

    def test_crossing_failures_are_retained(self):
        f = np.array([100., 1000., 1500., 2000., 10000.])
        unique = rlc.crossing_report(f, np.array([1j, 2j, 1j, -1j, -2j]), [1400, 1600])
        self.assertTrue(unique['single_crossing_bracket_intersects_interval'])
        multiple = rlc.crossing_report(f, np.array([1j, -2j, 1j, -1j, -2j]), [1400, 1600])
        self.assertFalse(multiple['single_crossing_bracket_intersects_interval'])
        exact = rlc.crossing_report(f, np.array([1j, 2j, 0j, -1j, -2j]), [1400, 1600])
        self.assertEqual(exact['exact_zero_hz'], [1500.])

    def test_synthetic_forecast_and_wrong_sign(self):
        f = np.geomspace(100, 10000, 81)
        interval, union = rlc.intervals(CFG)
        z = rlc.impedance(f, 9.7, .005, 2.2e-6)
        rows = [dict(row=i, frequency_hz=float(x), real_ohm=float(y.real), imag_ohm=float(y.imag),
                sign_table_s3=int(rlc.signs(x, interval)), sign_unit_union=int(rlc.signs(x, union)))
                for i, (x, y) in enumerate(zip(f, z))]
        good = rlc.score(rows, z, CFG)
        self.assertEqual(good['rlc_relative_rms'], 0.)
        self.assertTrue(good['rlc_error_below_rc_lower_bound'])
        self.assertTrue(good['signs']['table_s3']['all_classified_signs_agree'])
        z[0] = z[0].conjugate()
        bad = rlc.score(rows, z, CFG)
        self.assertEqual(bad['signs']['table_s3']['disagreement_rows'], [0])

    def test_redundant_encoding_stops_on_wrong_sign(self):
        f = np.geomspace(100, 10000, 81)
        z = rlc.impedance(f, 9.7, .005, 2.2e-6)
        doc = dict(omega=(2*np.pi*f).tolist(), z_real=z.real.tolist(), z_imag=z.imag.tolist(),
                   z_modulus=np.abs(z).tolist(), z_phase=np.angle(z, deg=True).tolist(),
                   z=[str(x).strip('()').replace('j', 'i') for x in z])
        actual, check = rlc.decode(doc, f, CFG)
        np.testing.assert_array_equal(actual, z)
        self.assertEqual(check['phase_units'], 'degrees')
        doc['z_imag'][0] *= -1
        with self.assertRaisesRegex(ValueError, 'encoding'):
            rlc.decode(doc, f, CFG)

    def test_independent_verification_and_changed_forecast(self):
        f = np.geomspace(100, 10000, 81)
        z = rlc.impedance(f, 9.7, .005, 2.2e-6)
        a, b = rlc.intervals(CFG)
        prediction = dict(config=CFG, crossing_hz_nominal=rlc.crossing(9.7, .005, 2.2e-6),
            crossing_hz_interval=a, crossing_hz_unit_union=b,
            rows=[dict(row=i, frequency_hz=float(x), real_ohm=float(y.real), imag_ohm=float(y.imag),
                sign_table_s3=int(rlc.signs(x, a)), sign_unit_union=int(rlc.signs(x, b)))
                for i, (x, y) in enumerate(zip(f, z))])
        stats = dict(numerical_comparisons=0, maximum_absolute_difference=0.)
        verify.verify_prediction(prediction, stats)
        self.assertEqual(stats['numerical_comparisons'], 167)
        prediction['rows'][0]['sign_table_s3'] *= -1
        with self.assertRaisesRegex(AssertionError, 'sign classification'):
            verify.verify_prediction(prediction, stats)

    def test_independent_scores_use_same_frequency_measure(self):
        f = np.array([100., 230., 1300., 1700., 10000.])
        z = rlc.impedance(f, 9.7, .005, 2.2e-6)
        a, b = rlc.intervals(CFG)
        rows = [dict(row=i, frequency_hz=float(x), real_ohm=float(y.real), imag_ohm=float(y.imag),
                     sign_table_s3=int(rlc.signs(x, a)), sign_unit_union=int(rlc.signs(x, b)))
                for i, (x, y) in enumerate(zip(f, z))]
        altered = z+np.array([1., -2j, 3., 4j, -5.])
        observations = [dict(row=i, frequency_hz=float(x), real_ohm=float(y.real), imag_ohm=float(y.imag))
                        for i, (x, y) in enumerate(zip(f, altered))]
        primary = rlc.score(rows, altered, CFG)
        for key, value in verify.independent_scores(observations, CFG).items():
            self.assertAlmostEqual(value, primary[key], places=12)
        self.assertEqual(verify.independent_signs(observations, a), primary['signs']['table_s3'])
