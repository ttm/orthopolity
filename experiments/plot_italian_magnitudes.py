"""Presentation of retained simulations only; no fitting or new simulations."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def plot(directory):
    result = json.loads((directory/'summary.json').read_text())
    cfg = json.loads((directory/'config.json').read_text())
    names = [m['name'] for m in cfg['models']]
    labels = ['Direct Mw control', 'ML before 2011', 'ML from 2011', 'Md before Apr 2013',
              'Md from Apr 2013', 'ML before 2011 + error', 'ML from 2011 + error',
              'ML shared slope −1.96 SE*', 'ML shared slope +1.96 SE*']
    rows = [[c for c in result['cells'] if c['model'] == name] for name in names]
    bias = np.array([[c['mean_bias'] for c in row] for row in rows])
    coverage = np.array([[c['coverage'] for c in row] for row in rows])
    fig, axes = plt.subplots(1,2,figsize=(14,6.6), layout='constrained',sharey=True)
    for ax,values,title,cmap,limits in zip(axes,[bias,coverage],
            ['Mean bias in estimated b','Coverage of nominal 95% intervals'],
            ['RdBu_r','YlGnBu'],[(-.4,.4),(0,1)]):
        picture=ax.imshow(values,cmap=cmap,vmin=limits[0],vmax=limits[1],aspect='auto')
        for i in range(len(names)):
            for j in range(8):
                label=f'{values[i,j]:+.2f}' if ax is axes[0] else f'{100*values[i,j]:.0f}%'
                dark = abs(values[i,j])>.24 if ax is axes[0] else values[i,j]>.60
                ax.text(j,i,label,ha='center',va='center',fontsize=9,color='white' if dark else '#17202a')
        ax.axhline(6.5,color='black',lw=1.4,ls='--')
        ax.axvline(3.5,color='black',lw=1.2)
        ax.set_xticks(range(8),['1.0','1.5','2.0','2.5']*2)
        ax.set_xlabel('True lower Mw support\nb = 1 (left four columns)     b = 1.5 (right four columns)')
        ax.set_yticks(range(len(names)),labels)
        ax.set_title(title,loc='left',fontsize=13)
        fig.colorbar(picture,ax=ax,shrink=.75,pad=.02)
    fig.suptitle('Italian magnitude pre-fit check: conversion and rounding can invalidate the estimator',fontsize=15)
    fig.supxlabel('400 repetitions × 7,000 events per cell; 500 conditional bootstrap resamples.\n'
                  '45 of 56 required cells fail. *Shared-slope sensitivities are outside the gate. Synthetic results only.',fontsize=10)
    fig.savefig(directory/'validation.png',dpi=180)
    plt.close(fig)


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--directory',type=Path,required=True)
    plot(ap.parse_args().directory)
