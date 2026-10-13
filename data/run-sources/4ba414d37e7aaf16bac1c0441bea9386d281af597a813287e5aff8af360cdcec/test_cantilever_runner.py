"""Withholding, missingness and scoring checks using only artificial arrays."""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'experiments'))
import run_cantilever as runner


def fixture():
    config=json.loads((ROOT/'configs/cantilever_2026-10-13.json').read_text())
    archive={}
    for sample,n,nd,nt in [('C30',11,5,1),('C30C',7,5,2)]:
        temp=np.linspace(310,450,n)
        delta=2*(temp-300)
        data=dict(AVG_TAVG=temp,AVG_TAVG_ERR=np.ones(n),AVG_TMAX=2*temp-300)
        for prefix,nmode,kind in [('D',nd,'flexural'),('T',nt,'torsional')]:
            phi=np.column_stack([1e-5+1e-8*delta for _ in range(nmode)])
            obs=np.column_stack([temp+index for index in range(nmode)])
            sigma=np.full_like(phi,1e-7)
            for field,array in [('PHI',phi),('PHI_ERR',sigma),('TFLUC',obs),('TFLUC_ERR',np.ones_like(obs))]:
                data[f'AVG_{prefix}_{field}']=array[:,0] if nmode==1 else array
        archive[sample]=data
    return archive,config


class CantileverRunnerTests(unittest.TestCase):
    def test_primary_does_not_use_heldout_damping_or_any_fluctuations(self):
        archive,config=fixture()
        expected=runner.forecast(archive,config)['analyses'][0]
        changed=copy.deepcopy(archive)
        for s,ntrain in [('C30',8),('C30C',5)]:
            for key,values in changed[s].items():
                if 'TFLUC' in key: values[:]=98765
                if key.endswith('_PHI'): values[ntrain:]*=100
        actual=runner.forecast(changed,config)['analyses'][0]
        self.assertEqual(expected,actual)
        # All-Phi secondary is deliberately a different, non-heldout diagnostic.
        self.assertNotEqual(runner.forecast(archive,config)['analyses'][3],
                            runner.forecast(changed,config)['analyses'][3])

    def test_all_modes_shapes_and_mask_preserve_targets(self):
        archive,config=fixture()
        pred=runner.forecast(archive,config)
        primary,_,masked,_=pred['analyses']
        self.assertEqual(len(primary['cases']),11)
        self.assertEqual(sum(len(c['rows']) for c in primary['cases']),28)
        for a,b in zip(primary['cases'],masked['cases']):
            self.assertEqual([r['row'] for r in a['rows']],[r['row'] for r in b['rows']])
        affected=[c for c in masked['cases'] if c['masked_train_rows']]
        self.assertEqual(len(affected),1)
        self.assertEqual(affected[0]['train_rows'],[2,3,4,5])

    def test_evaluation_never_refits_and_keeps_out_of_envelope_targets(self):
        archive,config=fixture()
        predictions=runner.forecast(archive,config)
        original=copy.deepcopy(predictions)
        archive['C30']['AVG_D_TFLUC'][8:,0]=-100
        with patch.object(runner,'fit_loss',side_effect=AssertionError('Refit')):
            result=runner.evaluate(predictions,archive)
        row=result['analyses'][0]['cases'][0]['rows'][0]
        self.assertTrue(row['qualified_temperature_target'])
        self.assertGreater(row['absolute_error_K'],400)
        self.assertEqual(predictions,original)

    def test_balancing_and_invalid_cases_are_visible(self):
        archive,config=fixture()
        predictions=runner.forecast(archive,config)
        predictions['analyses'][0]['cases'][0]['fit']['admissible']=False
        result=runner.evaluate(predictions,archive)['analyses'][0]
        self.assertEqual(result['summary']['attempted_modes'],11)
        self.assertEqual(result['summary']['admissible_modes'],10)
        self.assertEqual(result['summary']['qualified_temperature_targets'],25)
        self.assertIsNone(result['cases'][0]['temperature_mae_K'])
        cases=[dict(sample='A',rows=[{'error':0},{'error':0}]),
               dict(sample='A',rows=[{'error':10}]),dict(sample='B',rows=[{'error':20}])]
        self.assertEqual(runner.balanced(cases,'error')['equal_preparation_mean'],12.5)

    def test_temperature_tie_stops_before_split(self):
        archive,_=fixture()
        archive['C30']['AVG_TAVG'][8]=archive['C30']['AVG_TAVG'][7]
        with self.assertRaisesRegex(ValueError,'tie'):
            runner.predictor_audit(archive)

    def test_missing_training_rows_are_recorded(self):
        archive,config=fixture()
        archive['C30']['AVG_D_PHI'][0,0]=np.nan
        c=runner.forecast(archive,config)['analyses'][0]['cases'][0]
        self.assertEqual(c['missing_train_rows'],[1])
        self.assertEqual(c['train_rows'],list(range(2,9)))
        self.assertTrue(c['fit']['admissible'])


if __name__=='__main__': unittest.main()
