"""Transfer a fixed wedge resource across one-link attachment dynamics.

Finite references are exact for constant and affine kernels. Sublinear curves
are limiting predictions; superlinear growth is assessed through concentration
and excluded resource, without inventing a stationary power-law reference.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import time
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import scipy

from orthopolity.figures import save_figure
from orthopolity.attachment import (
    attachment_tree_snapshots, finite_expected_degree_snapshots,
    stationary_degree_law,
)
from orthopolity.spectrum import resource_spectrum

ROOT = Path(__file__).resolve().parents[1]


def normalize_resource(totals, widths):
    resource = np.sum(totals)
    return totals / widths / (resource / np.sum(widths)) if resource > 0 else np.full_like(totals, np.nan)


def bin_reference(degree, counts, edges):
    q = degree * (degree - 1) / 2
    # Direct sums avoid rounding a tiny late-bin mass to zero after larger bins.
    masks = [(degree >= lo) & ((degree < hi) if j < len(edges)-2 else (degree <= hi))
             for j, (lo, hi) in enumerate(zip(edges[:-1], edges[1:]))]
    binned_count = np.array([counts[mask].sum() for mask in masks])
    binned_resource = np.array([(counts * q)[mask].sum() for mask in masks])
    return binned_count, binned_resource


def references(kernel, sizes, cutoff):
    gamma, a = kernel['gamma'], kernel['attractiveness']
    if gamma in (0, 1):
        return finite_expected_degree_snapshots(sizes, cutoff, gamma=gamma, attractiveness=a)
    if gamma < 1:
        law = stationary_degree_law(gamma, cutoff, attractiveness=a)
        k, p = law['degree'], law['probability']
        return {n: dict(degree=k, expected_count=n*p,
                       unrepresented_expected_count=n*law['unrepresented_probability'],
                       expected_full_wedges=n*np.dot(k*(k-1)/2, p),
                       normalizer=law['normalizer'],
                       kind='limiting discrete recurrence; not exact finite expectation')
                for n in sizes}
    return {}


def summarize(kernel, n, snapshots, reference, edges, cutoff):
    widths = np.diff(np.log(edges))
    runs, resources, counts, represented_counts = [], [], [], []
    for degree in snapshots:
        k = degree.astype(float)
        q = k * (k - 1) / 2
        spec = resource_spectrum(k, q, edges)
        resources.append(spec['resource_sum'])
        counts.append(spec['count'])
        represented_counts.append(np.bincount(degree, minlength=cutoff+1)[1:cutoff+1])
        full = q.sum()
        inside = (k >= edges[0]) & (k <= edges[-1])
        below, above = k < edges[0], k > edges[-1]
        top_n = max(1, int(np.ceil(n*.01)))
        top_one_percent = np.partition(q, n-top_n)[n-top_n:].sum()
        runs.append(dict(max_degree=int(degree.max()), max_degree_fraction=float(degree.max()/(n-1)),
            top_wedge_share=float(q.max()/full), top_one_percent_wedge_share=float(top_one_percent/full),
            full_wedges=float(full), domain_wedges=float(q[inside].sum()),
            domain_wedge_fraction=float(q[inside].sum()/full),
            included_vertices=int(inside.sum()), below_domain_vertices=int(below.sum()),
            above_domain_vertices=int(above.sum()), below_domain_wedges=float(q[below].sum()),
            above_domain_wedges=float(q[above].sum()),
            empty_bins=int(np.sum(spec['count']==0)),
            zero_resource_bins=int(np.sum(spec['resource_sum']==0))))
    raw = np.asarray(resources)
    pooled_resource = raw.mean(axis=0)
    pooled_count = np.asarray(counts).mean(axis=0)
    phi = normalize_resource(pooled_resource, widths)
    scale = pooled_resource.sum() / widths.sum()
    if scale <= 0:
        raise ValueError('No wedge resource remains in the declared comparison domain')
    relative_runs = raw / widths / scale
    summary = {}
    for key in runs[0]:
        values = np.array([run[key] for run in runs], dtype=float)
        summary[key] = dict(mean=float(values.mean()), quantile_10=float(np.quantile(values,.1)),
                            quantile_90=float(np.quantile(values,.9)))
    degree_count = np.asarray(represented_counts).mean(axis=0)
    row = dict(model=kernel['name'], nodes=n, gamma=kernel['gamma'], attractiveness=kernel['attractiveness'],
        resource='centered wedges k(k-1)/2', metrics=summary, replicates=runs,
        profile=dict(lower=edges[:-1].tolist(), upper=edges[1:].tolist(),
            center=np.exp((np.log(edges[:-1])+np.log(edges[1:]))/2).tolist(),
            log_width=widths.tolist(), pooled_mean_count=pooled_count.tolist(),
            pooled_mean_resource=pooled_resource.tolist(), pooled_phi=phi.tolist(),
            pooled_domain_wedge_fraction=float(pooled_resource.sum()/summary['full_wedges']['mean']),
            run_quantile_10=np.quantile(relative_runs,.1,axis=0).tolist(),
            run_quantile_90=np.quantile(relative_runs,.9,axis=0).tolist(),
            pooled_empty_bins=int(np.sum(pooled_count==0)),
            pooled_zero_resource_bins=int(np.sum(pooled_resource==0))),
        degree_reference_comparison=dict(max_degree=cutoff,
            pooled_mean_count=degree_count.tolist(),
            unrepresented_mean_count=float(n-degree_count.sum())), reference=None)
    if reference is not None:
        expected_count, expected_resource = bin_reference(reference['degree'], reference['expected_count'], edges)
        expected_phi = normalize_resource(expected_resource, widths)
        expected = reference['expected_count']/n
        observed = degree_count/n
        missing_expected = reference['unrepresented_expected_count']/n
        missing_observed = max(0.0,float(1-observed.sum()))
        node_tv = .5*(np.abs(expected-observed).sum()+abs(missing_expected-missing_observed))
        resource_tv = .5*np.abs(pooled_resource/pooled_resource.sum()-expected_resource/expected_resource.sum()).sum()
        reference_fraction = float(expected_resource.sum()/reference['expected_full_wedges'])
        if reference_fraction > 1 + 1e-10:
            raise FloatingPointError('Reference domain resource exceeds full resource')
        row['reference'] = dict(kind=reference['kind'],
            expected_count=expected_count.tolist(), expected_resource=expected_resource.tolist(),
            profile=expected_phi.tolist(), expected_full_wedges=float(reference['expected_full_wedges']),
            full_wedge_reference_kind=('exact finite expectation' if reference['kind'].startswith('exact')
                else 'cutoff-truncated limiting second moment multiplied by n; not a finite expectation'),
            ratio_of_expected_domain_to_full_wedges=min(1.0, reference_fraction),
            expected_degree_probability=expected.tolist(),
            unrepresented_expected_probability=float(missing_expected),
            degree_probability_total_variation=float(node_tv),
            fixed_domain_wedge_total_variation=float(resource_tv),
            normalizer=reference.get('normalizer'))
    return row


def run(config):
    sizes = config['graph_sizes']
    cutoff = config['reference_max_degree']
    if cutoff < config['degree_domain'][-1]:
        raise ValueError('Reference cutoff must cover the declared degree domain')
    edges = np.geomspace(*config['degree_domain'], config['logarithmic_bins']+1)
    rows = []
    for index, kernel in enumerate(config['kernels']):
        started = time.perf_counter()
        histories = []
        for rep in range(config['replicates']):
            rng = np.random.default_rng(np.random.SeedSequence([config['seed'], index, rep]))
            histories.append(attachment_tree_snapshots(sizes, kernel['gamma'], rng,
                             attractiveness=kernel['attractiveness']))
        prediction = references(kernel, sizes, cutoff)
        for n in sizes:
            rows.append(summarize(kernel, n, [h[n] for h in histories], prediction.get(n), edges, cutoff))
        print(f"{kernel['name']}: {config['replicates']} histories through n={sizes[-1]} in {time.perf_counter()-started:.2f}s", flush=True)
    return rows


def plots(rows, config, output):
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'svg.fonttype':'none'})
    fig, axes = plt.subplots(2,3,figsize=(14,8),layout='constrained')
    colors = plt.cm.viridis(np.linspace(.15,.85,len(config['graph_sizes'])))
    for ax,kernel in zip(axes.flat,config['kernels']):
        subset = [row for row in rows if row['model']==kernel['name']]
        observed_positive = np.concatenate([np.asarray(row['profile']['pooled_phi'])[np.asarray(row['profile']['pooled_phi'])>0] for row in subset])
        positive = observed_positive
        refs = [np.asarray(row['reference']['profile']) for row in subset if row['reference'] is not None]
        if refs:
            positive = np.concatenate([positive]+[r[r>0] for r in refs])
        floor = float((observed_positive if kernel['name']=='uniform' else positive).min()*.3)
        for color,row in zip(colors,subset):
            p = row['profile']; x=np.asarray(p['center']); y=np.asarray(p['pooled_phi'])
            displayed=np.where(y>0,y,np.nan)
            ax.plot(x,displayed,'o-',color=color,ms=3,label=f"n={row['nodes']:,}")
            ax.fill_between(x,p['run_quantile_10'],p['run_quantile_90'],color=color,alpha=.1)
            zero=y==0
            if zero.any(): ax.scatter(x[zero],np.full(zero.sum(),floor),marker='v',facecolors='none',edgecolors=color,s=22)
            if row['reference'] is not None:
                ax.plot(x,row['reference']['profile'],'--',color=color,lw=1)
        ax.axhline(1,color='gray',ls=':',lw=.8)
        formula=f"k^{kernel['gamma']:g}" if kernel['gamma'] not in (0,1) else ('1' if kernel['gamma']==0 else 'k')
        if kernel['attractiveness']: formula+=f" + {kernel['attractiveness']:g}"
        ax.set(xscale='log',yscale='log',title=f"{kernel['name'].capitalize()}: A(k)={formula}",xlabel='Degree k',ylabel='Wedges per log degree / domain mean')
        if kernel['name']=='uniform':
            # Restrict the drawing only; analytic and simulated values remain
            # unchanged in JSON/CSV, including the tiny analytic upper tail.
            ax.set_ylim(floor*.65,observed_positive.max()*1.35)
        ax.legend(fontsize=7,frameon=False)
        if any(row['profile']['pooled_empty_bins'] for row in subset):
            text='Open triangles: empty bins at display floor'
            if kernel['name']=='uniform':text+='\nReference continues below display range'
            ax.text(.02,.03,text,transform=ax.transAxes,fontsize=7)
    ax=axes.flat[-1]
    for kernel in config['kernels']:
        subset=[row for row in rows if row['model']==kernel['name']]
        x=[row['nodes'] for row in subset]
        mean=[row['metrics']['top_wedge_share']['mean'] for row in subset]
        lo=[row['metrics']['top_wedge_share']['quantile_10'] for row in subset]
        hi=[row['metrics']['top_wedge_share']['quantile_90'] for row in subset]
        line,=ax.plot(x,mean,'o-',label=kernel['name'],ms=4)
        ax.fill_between(x,lo,hi,color=line.get_color(),alpha=.12)
    ax.set(xscale='log',yscale='log',xlabel='Graph size n',ylabel='Largest vertex / full wedge resource',title='Resource concentration, including the tail')
    ax.legend(fontsize=7,frameon=False)
    for ax in axes.flat:
        ax.spines[['top','right']].set_visible(False);ax.grid(alpha=.2,which='both')
    fig.suptitle('Same wedge resource, changed attachment dynamics\nDashed: discrete model reference; shading: history 10–90% quantiles, not confidence intervals',fontsize=11)
    for extension in ('png','svg'):save_figure(fig, output/f'attachment-profiles.{extension}', dpi=160)
    plt.close(fig)

    fig,axes=plt.subplots(1,2,figsize=(11,4),layout='constrained')
    for kernel in config['kernels']:
        subset=[row for row in rows if row['model']==kernel['name']]
        x=[row['nodes'] for row in subset]
        for ax,key in zip(axes,['max_degree_fraction','domain_wedge_fraction']):
            mean=[row['metrics'][key]['mean'] for row in subset]
            lo=[row['metrics'][key]['quantile_10'] for row in subset]
            hi=[row['metrics'][key]['quantile_90'] for row in subset]
            line,=ax.plot(x,mean,'o-',label=kernel['name'],ms=4)
            ax.fill_between(x,lo,hi,color=line.get_color(),alpha=.12)
    axes[0].set(xscale='log',yscale='log',xlabel='Graph size n',ylabel='Maximum degree / (n−1)',title='Degree concentration')
    axes[1].set(xscale='log',yscale='log',xlabel='Graph size n',ylabel='Wedges in fixed domain / full wedges',title='Declared domain [2,64]: retained resource')
    for ax in axes:
        ax.legend(frameon=False,fontsize=8);ax.spines[['top','right']].set_visible(False);ax.grid(alpha=.2,which='both')
    fig.suptitle('Tail resource stays visible even when it leaves the fixed comparison domain',fontsize=11)
    for extension in ('png','svg'):save_figure(fig, output/f'attachment-concentration.{extension}', dpi=160)
    plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,default=ROOT/'configs/attachment_study_2026-10-01.json')
    parser.add_argument('--output',type=Path,default=ROOT/'results/attachment')
    args=parser.parse_args()
    specification=args.config.read_bytes();config=json.loads(specification)
    if config['new_edges_per_vertex']!=1:
        raise ValueError('This benchmark and its analytic references require one new link per vertex')
    rows=run(config)
    output=args.output;output.mkdir(parents=True,exist_ok=True)
    report=dict(kind='exploratory fixed-resource transfer benchmark; simulated model evidence',
        config=config,config_sha256=hashlib.sha256(specification).hexdigest(),
        versions=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,matplotlib=matplotlib.__version__),
        reference_source='https://arxiv.org/html/cond-mat/0005139v2',
        finite_reference='Exact discrete expected-count recursion for constant/affine kernels, derived for the seed-edge tree; nonlinear kernels do not receive a false exact finite closure.',
        aggregation='Mean raw wedge density across independent histories, normalized once on the declared domain.',
        scenarios=rows)
    (output/'attachment-study.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    with (output/'profiles.csv').open('w',newline='') as handle:
        writer=csv.writer(handle, lineterminator='\n');writer.writerow(['kernel','nodes','lower','upper','center','mean_count','mean_wedges','pooled_phi','run_q10','run_q90','reference_phi'])
        for row in rows:
            p=row['profile']
            for j in range(len(p['center'])):
                reference=row['reference']['profile'][j] if row['reference'] else ''
                writer.writerow([row['model'],row['nodes'],p['lower'][j],p['upper'][j],p['center'][j],p['pooled_mean_count'][j],p['pooled_mean_resource'][j],p['pooled_phi'][j],p['run_quantile_10'][j],p['run_quantile_90'][j],reference])
    plots(rows,config,output)
    for row in rows:
        print(json.dumps(dict(kernel=row['model'],nodes=row['nodes'],
            maximum_degree_fraction=row['metrics']['max_degree_fraction']['mean'],
            top_wedge_share=row['metrics']['top_wedge_share']['mean'],
            domain_wedge_fraction=row['metrics']['domain_wedge_fraction']['mean'],
            pooled_empty_bins=row['profile']['pooled_empty_bins'],
            reference=row['reference']['kind'] if row['reference'] else None)))
    print(f'Saved {len(rows)} scenarios to {output}')


if __name__=='__main__':main()
