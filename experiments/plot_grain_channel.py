"""Show every sealed primary forecast and the fair calibration-only rivals."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def plot(result_path, output):
    result = json.loads(Path(result_path).read_text())
    scores = result['scores']['sphere']
    rows = scores['guo_shape']['rows']
    fig, (left, right) = plt.subplots(1, 2, figsize=(10.4, 4.2), gridspec_kw={'width_ratios':[1,1.25]})
    limit = max(max(r['observed_flux'], r['dimensionless_flux']) for r in rows)*1.08
    left.plot([0,limit],[0,limit],color='.45',lw=1,zorder=0)
    for grain, color, marker in [('sphere','#2471A3','o'),('gravel','#C56820','s')]:
        group = [r for r in rows if r['grain']==grain]
        left.scatter([r['observed_flux'] for r in group], [r['dimensionless_flux'] for r in group],
                     c=color,marker=marker,s=42,label=f'{grain.capitalize()} (n={len(group)})')
    left.set(xlim=(0,limit),ylim=(0,limit),xlabel='Observed dimensionless flux',
             ylabel='Forecast dimensionless flux',title='Primary Guo + measured shape')
    left.set_aspect('equal')
    left.legend(frameon=False,fontsize=9,loc='upper left')
    left.grid(alpha=.15)
    names = ['Guo + measured shape','Guo, no shape correction','Hydraulic radius + shape',
             'No wall correction + shape','Separate grain-type fits']
    models = ['guo_shape','guo_unity','radius_shape','depth_shape']
    values = [scores[m]['balanced_mae'] for m in models]+[result['scores']['material_label']['balanced_mae']]
    colors = ['#2471A3','#A1A7AC','#A1A7AC','#A1A7AC','#758B65']
    ys = np.arange(len(values))
    right.barh(ys,values,color=colors,height=.58)
    for y,v in zip(ys,values):
        right.text(v+.004,y,f'{v:.4f}',va='center',fontsize=9)
    right.set(yticks=ys,yticklabels=names,xlabel='Material-balanced mean absolute error',
              title='All nine wider-channel targets',xlim=(0,max(values)*1.24))
    right.invert_yaxis()
    right.grid(axis='x',alpha=.15)
    right.set_axisbelow(True)
    for ax in (left,right):
        ax.spines[['top','right']].set_visible(False)
    fig.suptitle('Old narrow-channel data predict a wider channel',fontsize=14,y=.99)
    fig.text(.5,.015,'Retrospective transfer; one target exposed before freeze. Shared assay errors are not propagated.',
             ha='center',fontsize=8,color='.3')
    fig.subplots_adjust(left=.075,right=.975,top=.84,bottom=.16,wspace=.77)
    output = Path(output)
    if output.exists():
        raise ValueError('Refusing presentation overwrite')
    fig.savefig(output,dpi=180,metadata={'Software':'Orthopolity grain/channel transfer'})
    plt.close(fig)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--result',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    plot(args.result,args.output)
