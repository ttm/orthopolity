"""Withholding and score balancing from artificial source files only."""
import copy
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'experiments'))
import run_adsorption as runner
from orthopolity.adsorption import langmuir


class AdsorptionRunnerTests(unittest.TestCase):
    def test_forecast_never_parses_target_values(self):
        def reader(path,columns):
            if 'CO2_CH4' in path.name:
                self.assertEqual(columns,['_adsorp_pressure','_adsorp_molefraction1'])
                return np.array([[.1,.2],[1,.5],[2,.8]])
            f = np.geomspace(.01,10,12)
            b = 2 if '_CO2_' in path.name else .5
            return np.column_stack([f,langmuir(f,4,b),np.full(12,.02)])
        config = dict(temperatures_K=[333],critical_constants=[[304.1282,7377300,.22394],[190.564,4599200,.01142]])
        def source_table(label):
            f = np.geomspace(.01,10,12)
            q = langmuir(f,4,2 if label == 'Table 5' else .5)
            return [[333,p,0,a,0,.02] for p,a in zip(f,q)]
        with patch.object(runner,'read_aif',side_effect=reader),patch.object(runner,'table_rows',side_effect=source_table):
            prediction = runner.forecast(config)
        self.assertEqual(len(prediction['analyses']),2)
        self.assertEqual(len(prediction['analyses'][0]['cases'][0]['rows']),3)

    def test_scoring_balances_species_and_reports_total_and_composition(self):
        rows = [dict(predictions={'shared':[2,1]},observed_mmol_g=[1,1],expanded_U_mmol_g=[.1,.1]),
                dict(predictions={'shared':[2,1]},observed_mmol_g=[2,1],expanded_U_mmol_g=[.1,.1])]
        scores = runner.score_case(rows,'shared')
        self.assertEqual(scores['component_mae_mmol_g'],[.5,0])
        self.assertEqual(scores['within_reported_U'],3)
        self.assertEqual(scores['total_mae_mmol_g'],.5)
        self.assertAlmostEqual(scores['adsorbed_CO2_fraction_mae'],1/12)

    def test_target_evaluation_does_not_fit_or_mutate_seal(self):
        rows = [dict(predictions={m:[1.,2.] for m in ['shared','ablation','iast']}) for _ in range(3)]
        sealed = dict(analyses=[dict(name='ideal',cases=[dict(temperature_K=333,rows=rows,
            shared_fit=dict(locally_identified=True,pure_fit_adequate=True,pure_max_mmol_g=[3,4]))])])
        original = copy.deepcopy(sealed)
        paper = [['333','1','.5','1.1','2.2','0','0','.1','.1']]*3
        with patch.object(runner,'table_rows',return_value=paper),patch.object(runner,'read_aif',return_value=np.array([[1.1,2.2,.1,.1]]*3)),patch.object(runner,'fit_pure',side_effect=AssertionError('Refit')):
            result = runner.evaluate(sealed)
        self.assertEqual(sealed,original)
        self.assertFalse(result['analyses'][0]['summary']['declared_joint_transfer_pass'])
        self.assertEqual(result['analyses'][0]['summary']['scores']['shared']['component_targets'],6)


if __name__ == '__main__':
    unittest.main()
