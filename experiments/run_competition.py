"""Forward predictions for negatively coupled resources and finite support."""
from __future__ import annotations

import argparse
import csv
import json
import platform
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import scipy

from orthopolity.competition import (
    competing_capacities, forward_resource_profile, local_dimensions,
    minimum_survival,
)
from orthopolity.figures import save_figure
from orthopolity.spectrum import resource_spectrum

ROOT=Path(__file__).resolve().parents[1]


def run(config):
    rows=[]
    for index,scenario in enumerate(config['scenarios']):
        rho=scenario['rho']
        edges=np.geomspace(*scenario['domain'],config['bins']+1)
        widths=np.diff(np.log(edges))
        prediction=forward_resource_profile(edges,rho,cost_exponent=config['cost_exponent'])
        raw=[];marginals=[];survivals=[];counts=[]
        grid=np.geomspace(edges[0],edges[-1],25)
        for rep in range(config['replicates']):
            rng=np.random.default_rng(np.random.SeedSequence([config['seed'],index,rep]))
            capacities=competing_capacities(config['samples'],rho,rng)
            size=capacities.min(axis=1)
            spectrum=resource_spectrum(size,size**config['cost_exponent'],edges)
            raw.append(spectrum['occupancy']);counts.append(spectrum['count'])
            marginals.append(np.mean(capacities>=2,axis=0))
            survivals.append(np.mean(size[:,None]>=grid[None,:],axis=0))
        raw=np.asarray(raw)
        pooled=raw.mean(axis=0)
        scale=np.dot(pooled,widths)/widths.sum()
        phi=pooled/scale
        expected_survival=minimum_survival(grid,rho)
        local_grid=np.geomspace(1.02,1.98,70) if rho==-1 else np.geomspace(1.02,10000,90)
        dimensions=local_dimensions(local_grid,rho)
        tail_grid=np.asarray(config['tail_thresholds'],float)
        observed_survival=np.mean(survivals,axis=0)
        row=dict(scenario=scenario,
            resource=dict(cost_exponent=config['cost_exponent'],definition='q(K)=K**d; fixed across all coupling settings'),
            status='known Gaussian copula constructions; K=min capacities by definition',
            marginal_survival_at_2=np.mean(marginals,axis=0).tolist(),
            unlimited_tail_dimension=None if rho==-1 else 2/(1+rho),
            finite_upper_support=2 if rho==-1 else None,
            tail_reference=dict(thresholds=tail_grid.tolist(),survival=minimum_survival(tail_grid,rho).tolist(),
                status='forward calculation; finite simulated counts do not validate arbitrarily deep tails'),
            profile=dict(edges=edges.tolist(),centers=np.sqrt(edges[:-1]*edges[1:]).tolist(),
                pooled_phi=phi.tolist(),forward_phi=prediction['phi'].tolist(),
                run_quantile_10=np.quantile(raw/scale,.1,axis=0).tolist(),
                run_quantile_90=np.quantile(raw/scale,.9,axis=0).tolist()),
            prediction_error=dict(log_profile_rmse=float(np.sqrt(np.mean(np.log(phi/prediction['phi'])**2))),
                maximum_absolute_survival_error=float(np.max(abs(observed_survival-expected_survival)))),
            empty_count_bins=int(np.sum(np.asarray(counts)==0)),
            survival=dict(thresholds=grid.tolist(),pooled=observed_survival.tolist(),forward=expected_survival.tolist()),
            local_dimensions=dict(thresholds=local_grid.tolist(),feasibility=dimensions['feasibility'].tolist(),
                density_exponent=dimensions['density_exponent'].tolist(),
                resource_slope=(config['cost_exponent']+1-dimensions['density_exponent']).tolist()))
        rows.append(row)
        print(json.dumps(dict(scenario=scenario['id'],prediction_error=row['prediction_error'],tail_dimension=row['unlimited_tail_dimension'])),flush=True)
    return rows


def plot(rows,config,out):
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'svg.fonttype':'none'})
    fig,axes=plt.subplots(1,3,figsize=(14,4.4),layout='constrained')
    for row in rows:
        name=row['scenario']['id'];p=row['profile'];s=row['survival'];local=row['local_dimensions']
        line,=axes[0].plot(p['centers'],p['pooled_phi'],'o-',ms=3,label=name)
        axes[0].plot(p['centers'],p['forward_phi'],'--',color=line.get_color())
        axes[0].fill_between(p['centers'],p['run_quantile_10'],p['run_quantile_90'],color=line.get_color(),alpha=.13)
        axes[1].plot(s['thresholds'],s['forward'],label=name)
        if row['scenario']['rho']!=-1:
            axes[2].plot(local['thresholds'],local['feasibility'],label=f"{name}: survival")
    axes[0].axhline(1,color='gray',ls=':',lw=1)
    axes[0].set(xscale='log',yscale='log',xlabel='Feasible size K',ylabel='Resource per log size / mean',title='A  Same marginal resources, changed coupling')
    axes[1].set(xscale='log',yscale='log',xlabel='Threshold k',ylabel='Predicted joint survival',title='B  Opposed capacities end at K=2')
    axes[2].set(xscale='log',xlabel='Threshold k',ylabel='Joint-feasibility elasticity',title='C  Negative coupling exceeds two inputs')
    for ax in axes:
        ax.legend(fontsize=7,frameon=False);ax.spines[['top','right']].set_visible(False);ax.grid(alpha=.2)
    d=config['cost_exponent']
    description='opposed resources can be log-neutral on bounded support' if d==1 else 'opposed capacities retain bounded support'
    fig.suptitle(f'Fixed cost q(K)=K^{d:g}; {description}\nProfiles: simulation with forward dashed curves; bands: run quantiles, not confidence bands',fontsize=11)
    for ext in ('png','svg'):save_figure(fig,out/f'competition-study.{ext}',dpi=160)
    plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,default=ROOT/'configs/competition_study_2026-10-01.json')
    parser.add_argument('--output',type=Path,default=ROOT/'results/competition')
    args=parser.parse_args();config=json.loads(args.config.read_text())
    rows=run(config);args.output.mkdir(parents=True,exist_ok=True)
    report=dict(kind='constructed-model competition benchmark; no natural-system observations',config=config,
        versions=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,matplotlib=matplotlib.__version__),
        reference='https://arxiv.org/abs/0912.2816',
        aggregation='mean raw bounded-domain resource density normalized once',
        uncertainty='run quantiles summarize independent simulation variation; no empirical equivalence test',scenarios=rows)
    (args.output/'competition-study.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    with (args.output/'profiles.csv').open('w',newline='') as handle:
        writer=csv.writer(handle,lineterminator='\n')
        writer.writerow(['scenario','rho','lower','upper','pooled_phi','forward_phi'])
        for row in rows:
            p=row['profile']
            for index,(lo,hi) in enumerate(zip(p['edges'][:-1],p['edges'][1:])):
                writer.writerow([row['scenario']['id'],row['scenario']['rho'],lo,hi,p['pooled_phi'][index],p['forward_phi'][index]])
    plot(rows,config,args.output)
    print(f'Saved {len(rows)} scenarios to {args.output}')


if __name__=='__main__':main()
