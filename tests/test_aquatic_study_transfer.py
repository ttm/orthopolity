"""Study weighting, leakage checks and uncertainty-source selection."""
from copy import deepcopy
import csv
import io
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from orthopolity.aquatic_study_transfer import (
    fit_training, leave_study_out, point_forecast, select_rows, study_weights,
)


ROOT=Path(__file__).resolve().parents[1]


class AquaticTransferChecks(unittest.TestCase):
    def setUp(self):
        self.config=json.loads((ROOT/'configs/aquatic_study_transfer_2026-10-01.json').read_text())
        self.rows=[dict(study=study,slope=slope,direct_se=.1,sensitivity_se=.1,log_span=np.log(100))
                   for study,slope in [('a',-1.),('a',-.8),('b',-.5),('c',-1.3)]]

    def test_study_duplication_does_not_change_weighted_training_parameters(self):
        fit=fit_training([-1,-.8,-.5],[.1]*3,['a','a','b'])
        repeated=fit_training([-1,-.8]*20+[-.5],[.1]*41,['a']*40+['b'])
        self.assertAlmostEqual(fit['mean'],-.7)
        self.assertAlmostEqual(fit['mean'],repeated['mean'])
        self.assertAlmostEqual(fit['tau_squared'],repeated['tau_squared'])
        np.testing.assert_allclose(study_weights(['a','a','b']),[.25,.25,.5])

    def test_changed_held_out_outcome_cannot_change_its_training_model(self):
        original=leave_study_out(self.rows,'direct_se',self.config)
        changed=deepcopy(self.rows)
        for row in changed:
            if row['study']=='a':row['slope']=5.
        altered=leave_study_out(changed,'direct_se',self.config)
        self.assertEqual(original['folds'][0]['training'],altered['folds'][0]['training'])
        self.assertNotEqual(original['folds'][0]['models'],altered['folds'][0]['models'])
        self.assertNotIn('a',original['folds'][0]['training_studies'])

    def test_primary_pair_uses_identical_scatter_and_study_level_aggregation(self):
        result=leave_study_out(self.rows,'direct_se',self.config)
        for fold in result['folds']:
            models=fold['models']
            self.assertEqual(models['fixed_neutral_shared_scatter']['tau_squared'],models['training_location_shared_scatter']['tau_squared'])
        manual=np.mean([f['fixed_minus_training_location_log_score'] for f in result['folds']])
        self.assertEqual(manual,result['comparison']['equal_study_mean_fixed_minus_training_log_score'])

    def test_no_error_is_imputed_for_point_forecast(self):
        rows=[dict(r,direct_se=None,sensitivity_se=None) for r in self.rows]
        result=point_forecast(rows,-1.)
        self.assertEqual(result['rows'],4)
        with self.assertRaises(ValueError):leave_study_out(rows,'direct_se',self.config)

    def test_invalid_bounds_study_and_uncertainty_routes_are_explicit(self):
        fieldnames=['StudyID','SampleID','XaxisParameterType','SizeSpectrumMethod','Slope','SizeRangeMinimum',
                    'SizeRangeMaximum','SlopeSE','SlopeSD','SlopeConfIntLow','SlopeConfIntUp']
        base=dict(StudyID='one',SampleID='fit',XaxisParameterType='body mass',
            SizeSpectrumMethod='Normalized biomass spectrum (linear)',Slope='-1',
            SizeRangeMinimum='1',SizeRangeMaximum='100',SlopeSE='NA',SlopeSD='.2',
            SlopeConfIntLow='NA',SlopeConfIntUp='NA')
        table=io.StringIO();writer=csv.DictWriter(table,fieldnames=fieldnames,delimiter=' ',quoting=csv.QUOTE_ALL)
        writer.writeheader();writer.writerow(base)
        writer.writerow(dict(base,StudyID='two',SlopeConfIntLow='-1.392',SlopeConfIntUp='-.608'))
        writer.writerow(dict(base,StudyID='three',SlopeSE='.1',SlopeConfIntLow='-1.392',SlopeConfIntUp='-.608'))
        writer.writerow(dict(base,StudyID='StudyID_07',SlopeSE='.1'))
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'data.txt';path.write_text(table.getvalue())
            rows,membership=select_rows(path,self.config)
        self.assertIsNone(rows[0]['direct_se']);self.assertIsNone(rows[0]['sensitivity_se'])
        self.assertIsNone(rows[1]['direct_se']);self.assertAlmostEqual(rows[1]['sensitivity_se'],.2)
        self.assertEqual(rows[2]['direct_se'],.1);self.assertEqual(rows[2]['sensitivity_se'],.1)
        self.assertEqual(membership[-1]['exclusion_reason'],'known_invalid_study_bounds')

    def test_frozen_dataset_counts_distinguish_direct_and_assumed_errors(self):
        rows,membership=select_rows(ROOT/self.config['input'],self.config)
        direct=[r for r in rows if r['direct_se'] is not None]
        augmented=[r for r in rows if r['sensitivity_se'] is not None]
        self.assertEqual((len(direct),len({r['study'] for r in direct})),(103,8))
        self.assertEqual((len(augmented),len({r['study'] for r in augmented})),(747,11))
        self.assertEqual((len(rows),len({r['study'] for r in rows})),(923,15))
        self.assertTrue(all(r['body_mass_units'] is not None and r['biomass_units'] is not None for r in rows))
        self.assertTrue(any(r['body_mass_unit_specification'] not in (None,'NA') for r in rows))
        self.assertEqual(sum(m['exclusion_reason']=='known_invalid_study_bounds' for m in membership),377)


if __name__=='__main__':unittest.main()
