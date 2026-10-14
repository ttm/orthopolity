"""Plot all primary sealed component forecasts against archived observations."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np


def plot(result_path, output):
    data = json.loads(Path(result_path).read_text())['analyses'][0]
    fig, axes = plt.subplots(2,3,figsize=(10.6,6.8),sharey='row',sharex='row')
    colors = dict(shared='#2166ac',ablation='#999999',iast='#d55e00')
    markers = dict(shared='o',ablation='x',iast='s')
    labels = dict(shared='Shared capacity',ablation='No competition',iast='IAST')
    limits = []
    for gas in range(2):
        maximum = max(max([r['observed_mmol_g'][gas]+r['expanded_U_mmol_g'][gas]]+
                    [r['predictions'][m][gas] for m in colors]) for c in data['cases'] for r in c['rows'])
        limits.append(maximum*1.08)
    for col, case in enumerate(data['cases']):
        for gas in range(2):
            ax = axes[gas,col]
            obs = np.array([r['observed_mmol_g'][gas] for r in case['rows']])
            u = np.array([r['expanded_U_mmol_g'][gas] for r in case['rows']])
            ax.plot([0,limits[gas]],[0,limits[gas]],color='.3',lw=.8,zorder=0)
            ax.errorbar(obs,[r['predictions']['shared'][gas] for r in case['rows']],xerr=u,
                fmt='none',ecolor=colors['shared'],alpha=.3,lw=.7,zorder=1)
            for model in ['ablation','iast','shared']:
                values = [r['predictions'][model][gas] for r in case['rows']]
                ax.scatter(obs,values,s=25 if model=='shared' else 28,marker=markers[model],
                    c=colors[model] if model!='iast' else 'none',
                    edgecolors=colors[model] if model=='iast' else None,linewidths=.9,zorder=2)
            ax.set(xlim=(0,limits[gas]),ylim=(0,limits[gas]))
            ax.grid(alpha=.15)
            if gas==0:
                ax.set_title(f"{case['temperature_K']} K",fontsize=12)
            if col==0:
                ax.set_ylabel(('CO$_2$' if gas==0 else 'CH$_4$')+' forecast (mmol/g)')
            ax.text(.05,.95,'MAE (mmol/g)\n'+'\n'.join(
                f"{labels[m]}: {case['scores'][m]['component_mae_mmol_g'][gas]:.3f}"
                for m in ['shared','ablation','iast']),transform=ax.transAxes,va='top',fontsize=8,
                bbox=dict(facecolor='white',alpha=.85,edgecolor='none',pad=2))
    handles = [Line2D([],[],color=colors[m],marker=markers[m],linestyle='none',
        markerfacecolor='none' if m=='iast' else colors[m],label=labels[m]) for m in colors]
    handles.append(Line2D([],[],color='.3',lw=.8,label='Exact prediction'))
    fig.legend(handles=handles,loc='upper center',ncol=4,bbox_to_anchor=(.5,.955),frameon=False,fontsize=10)
    fig.suptitle('Pure-gas calibration predicts mixture uptake',fontsize=14,y=.992)
    fig.supxlabel('Observed absolute uptake (mmol/g)',y=.035,fontsize=11)
    fig.subplots_adjust(left=.085,right=.99,top=.855,bottom=.11,hspace=.19,wspace=.1)
    output = Path(output)
    if output.exists():
        raise ValueError('Refusing to overwrite presentation artifact')
    fig.savefig(output,dpi=180,metadata={'Software':'Orthopolity adsorption transfer'})
    plt.close(fig)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--result',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    args = p.parse_args()
    plot(args.result,args.output)
