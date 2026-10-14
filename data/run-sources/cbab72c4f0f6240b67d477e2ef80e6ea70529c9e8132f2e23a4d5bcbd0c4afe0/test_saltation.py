"""Synthetic recovery, constrained global fitting and response-column isolation."""
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile

import numpy as np
from scipy.optimize import minimize_scalar

from orthopolity.saltation import (read_wind, day_weights, flux, fit_flux,
                                   lognormal_factors, split_wind)


class SaltationTests(unittest.TestCase):
    def test_exact_recovery_both_laws_and_threshold_regimes(self):
        x = np.linspace(.01,.4,31)
        w = np.ones(len(x))/len(x)
        for exponent in (0,.5):
            for threshold in (0,.08,.12,.39):
                y = flux(x,3.,threshold,exponent)
                fit = fit_flux(x,y,w,exponent)
                np.testing.assert_allclose(flux(x,fit['coefficient'],fit['threshold'],exponent),y,atol=1e-12)
                if threshold < .39:
                    self.assertAlmostEqual(fit['threshold'],threshold,places=12)
                    self.assertAlmostEqual(fit['coefficient'],3.,places=10)

    def test_global_fit_matches_independent_bounded_search_each_interval(self):
        rng = np.random.default_rng(410)
        for exponent in (0,.5):
            x = np.sort(rng.uniform(.01,.4,24))
            w = rng.uniform(.5,2,len(x)); w /= w.sum()
            y = flux(x,2,.08,exponent)*rng.lognormal(0,.5,len(x))
            def objective(t):
                h = flux(x,1,t,exponent)
                c = max(0,np.dot(w*y,h)/np.dot(w*h,h)) if np.any(h) else 0
                return np.sum(w*(c*h-y)**2)
            knots = np.r_[0,x]
            scores = [objective(t) for t in knots]
            scores += [minimize_scalar(objective,bounds=(a,b),method='bounded',
                                       options={'xatol':1e-14}).fun for a,b in zip(knots[:-1],knots[1:])]
            self.assertAlmostEqual(fit_flux(x,y,w,exponent)['mse'],min(scores),places=14)

    def test_zero_response_and_nonnegative_bound(self):
        x = np.linspace(.01,.4,10)
        fit = fit_flux(x,np.zeros(10),np.ones(10),.5)
        self.assertEqual(fit['coefficient'],0)
        self.assertEqual(fit['mse'],0)
        fit = fit_flux(x,np.ones(10),np.ones(10),0)
        self.assertEqual(fit['threshold'],0)

    def test_wrong_law_has_nonzero_extrapolation_error_without_noise(self):
        x = np.linspace(.1,.4,25)
        for truth in (0,.5):
            y = flux(x,2,.08,truth)
            fit = fit_flux(x,y,np.ones(25),.5-truth)
            held = np.linspace(.4,.8,12)
            err = flux(held,fit['coefficient'],fit['threshold'],.5-truth)-flux(held,2,.08,truth)
            self.assertGreater(float(np.mean(err**2)),1e-5)

    def test_invalid_inputs_stop(self):
        for x,y,w in [([0,1],[1,2],[1,1]),([1,2],[-1,1],[1,1]),
                      ([1,2],[1,2],[0,1]),([1,2],[1,np.nan],[1,1])]:
            with self.assertRaises(ValueError):
                fit_flux(x,y,w,0)

    def test_day_weights_do_not_treat_rows_as_independent_days(self):
        w = day_weights(['a','a','b'])
        np.testing.assert_allclose(w,[.25,.25,.5])

    def test_noise_is_mean_one_with_declared_cv_and_shared_days(self):
        a = lognormal_factors(np.random.default_rng(2),['a','a','b'],.5,100000)
        np.testing.assert_allclose(a.mean(axis=0),1,atol=.008)
        np.testing.assert_allclose(a.std(axis=0)/a.mean(axis=0),.5,atol=.01)
        self.assertGreater(np.corrcoef(a.T)[0,1],.2)
        self.assertLess(abs(np.corrcoef(a.T)[0,2]),.02)
        np.testing.assert_array_equal(lognormal_factors(np.random.default_rng(2),['a','b'],0,3),np.ones((3,2)))

    def test_date_split_precedes_predictor_filter(self):
        config = dict(primary_site='x',max_abs_theta_degrees=20,max_abs_zL=.15,minimum_days_per_split=1)
        rows = [dict(site='x',date=str(d),tau=.1,theta=0 if d!=1 else 30,zL=0) for d in range(4)]
        a,b = split_wind(rows,config)
        self.assertEqual([r['date'] for r in a],['0'])
        self.assertEqual([r['date'] for r in b],['2','3'])

    def test_real_reader_ignores_poisoned_response_cells(self):
        source = Path('data/saltation/2026-10-14/SaltationWind_ThreeSites_30minute.xlsx')
        if not source.exists():
            self.skipTest('Source acquisition pending')
        import xml.etree.ElementTree as ET
        ns = {'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
        expected = read_wind(source)
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)/'poison.xlsx'
            with ZipFile(source) as old, ZipFile(target,'w') as new:
                for item in old.infolist():
                    data = old.read(item.filename)
                    if item.filename.startswith('xl/worksheets/sheet'):
                        root = ET.fromstring(data)
                        for row in root.findall('s:sheetData/s:row',ns):
                            if row.get('r') == '1':
                                continue
                            for cell in row:
                                if cell.get('r').rstrip('0123456789') in ['J','K','L','M','N']:
                                    node = cell.find('s:v',ns)
                                    if node is not None:
                                        cell.attrib.pop('t',None)
                                        node.text = 'WITHHELD_RESPONSE'
                        data = ET.tostring(root)
                    new.writestr(item,data)
            self.assertEqual(read_wind(target),expected)


if __name__ == '__main__':
    unittest.main()
