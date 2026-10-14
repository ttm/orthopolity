"""Post-response domain audit of sealed predictors; never changes forecasts."""
import argparse
import json
from pathlib import Path

import numpy as np


def audit(path):
    prediction = json.loads(Path(path).read_text())
    output = dict(post_response=True,meaning='Coverage description only; frozen upper-IAST flags and all forecasts remain unchanged',analyses=[])
    for analysis in prediction['analyses']:
        cases = []
        for case in analysis['cases']:
            lower = np.array([min(g['fugacity_MPa']) for g in case['pure_data']])
            upper = np.array([max(g['fugacity_MPa']) for g in case['pure_data']])
            f = np.array([r['fugacity_MPa'] for r in case['rows']])
            f0 = np.array([r['iast_f0_MPa'] for r in case['rows']])
            b = np.array(case['shared_fit']['affinities'])
            item = dict(temperature_K=case['temperature_K'],pure_fugacity_min_MPa=lower.tolist(),
                pure_fugacity_max_MPa=upper.tolist(),
                shared_occupancy_at_pure_min=(b*lower/(1+b*lower)).tolist())
            for name,values in [('mixture',f),('iast_standard_state',f0)]:
                item[name] = dict(below_rows_by_gas=[(np.flatnonzero(values[:,i]<lower[i])+1).tolist() for i in range(2)],
                    above_rows_by_gas=[(np.flatnonzero(values[:,i]>upper[i])+1).tolist() for i in range(2)],
                    largest_ratio_to_pure_max=np.max(values/upper,axis=0).tolist())
            cases.append(item)
        output['analyses'].append(dict(name=analysis['name'],cases=cases))
    return output


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--predictions',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args = p.parse_args()
    if args.output.exists():
        raise ValueError('Use an unused output path')
    args.output.write_text(json.dumps(audit(args.predictions),indent=2,sort_keys=True,allow_nan=False)+'\n')
