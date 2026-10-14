"""Show synthetic model selection, without plotting real sand responses."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--summary', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    if args.output.exists():
        raise FileExistsError('Use an unused figure path')
    result = json.loads(args.summary.read_text())
    fig, axes = plt.subplots(1,2,figsize=(9,3.6),sharey=True,layout='constrained')
    for ax, truth, label in zip(axes,[0,.5],['Linear law generates the data','3/2 law generates the data']):
        for threshold, color in zip([.04,.08,.12],['#2166ac','#b35806','#5e3c99']):
            rows = [s for s in result['scenarios'] if s['generating_exponent']==truth and s['threshold_Pa']==threshold]
            ax.errorbar([r['noise_cv'] for r in rows],[r['correct_fraction'] for r in rows],
                        yerr=[1.96*r['monte_carlo_standard_error'] for r in rows],
                        label=f'Threshold {threshold:.2f} Pa',color=color,marker='o',capsize=3,lw=1.5)
        ax.axhline(.8,color='.35',ls='--',lw=1)
        ax.set(title=label,xlabel='Synthetic marginal variability (CV)',ylim=(.45,1.04),xticks=[0,.1,.25,.5])
        ax.spines[['top','right']].set_visible(False)
        ax.grid(axis='y',alpha=.18)
    axes[0].set_ylabel('Fraction selecting the generating law')
    axes[0].legend(frameon=False,fontsize=8,loc='lower left')
    axes[1].text(.27,.812,'Frozen minimum: 80%',fontsize=8,color='.3')
    fig.suptitle('Chronological wind-to-flux design fails at field-scale variability',fontsize=12)
    fig.savefig(args.output,dpi=180,metadata={'Software':'Orthopolity saltation qualification'})
    plt.close(fig)


if __name__=='__main__':
    main()
