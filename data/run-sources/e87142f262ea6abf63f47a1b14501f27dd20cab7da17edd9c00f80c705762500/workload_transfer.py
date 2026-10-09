"""Prospective transfer comparisons without changing original quota arrays."""
from __future__ import annotations

from copy import deepcopy

import numpy as np

from orthopolity.workload_analysis import observed_opportunities, profile_errors
from orthopolity.workload_prediction import calibration_profiles, forecast_largest, outcome_profile, resample_profiles

MODES = ('joint', 'median', 'memory_only', 'cpu_only', 'resource_independent', 'budget_independent')


def within_tolerance(error, tolerance):
    """Include mathematical equality without relaxing the scientific margin."""
    if not np.isfinite(error) or not np.isfinite(tolerance) or error < 0 or tolerance < 0:
        raise ValueError('Finite nonnegative error and tolerance required')
    slack = 8*np.finfo(float).eps*max(1.,abs(error),abs(tolerance))
    return bool(error <= tolerance+slack)


def forecasts_for_budgets(profile, memory, cpu):
    predictions = {mode:forecast_largest(profile,memory,cpu,mode=mode) for mode in MODES if mode!='budget_independent'}
    mb=np.asarray(memory);cb=np.asarray(cpu)
    predictions['budget_independent']=forecast_largest(profile,np.repeat(mb,len(mb)),np.tile(cb,len(cb)),mode='joint')
    return predictions


def transfer_plan(reference, config, local_rows):
    """Keep old predictions, budgets, and criterion; add local forecasts only."""
    physical = ('sizes','dtype','matrix_repeats','warmup_size','thread_environment',
                'conditions','validation_repetitions_per_budget_stratum',
                'permutation_shift','cpu_tightening_factor','memory_resource','cpu_resource')
    if any(config[key]!=reference['config'][key] for key in physical):
        raise ValueError('A transfer replication must retain physical tasks and quota observation design')
    expected={(block,size) for block in range(config['calibration_blocks']) for size in config['sizes']}
    if len(local_rows)!=len(expected) or {(r['block_id'],r['size']) for r in local_rows}!=expected:
        raise ValueError('Complete every declared local calibration block before freezing')
    local=calibration_profiles(local_rows,config['sizes'])
    plan=deepcopy(reference)
    plan['config']=deepcopy(config)
    plan['reference_frozen_utc']=reference['frozen_utc']
    plan['reference_profile']=deepcopy(reference['calibrated_profile'])
    plan['local_profile']=local
    for name,row in plan['conditions'].items():
        row['original_forecasts']=deepcopy(row['forecasts'])
        row['local_forecasts']=forecasts_for_budgets(local,row['memory_budgets_bytes'],row['cpu_budgets_seconds'])
    # The original quotas, all original forecasts, and the original tolerances
    # are copied, not estimated from the new calibration or validation.
    return plan


def analyse_transfer(plan, rows):
    config=plan['config'];sizes=np.asarray(config['sizes']);n=plan['validation_blocks']
    opportunities=observed_opportunities(plan,rows)
    names=list(plan['conditions'])
    outcomes={name:np.array([r['largest_completed_size'] for r in opportunities if r['condition']==name]) for name in names}
    empirical={name:outcome_profile(values,sizes) for name,values in outcomes.items()}
    result=dict(kind='Actual same-machine forecast transfer and prospective local recalibration comparison',
                config=config,reference_frozen_utc=plan['reference_frozen_utc'],comparison_frozen_utc=plan['frozen_utc'],
                opportunities=opportunities,reference_profile=plan['reference_profile'],local_profile=plan['local_profile'],
                conditions={},contrasts={},sample_counts=dict(new_calibration_tasks=len(plan['local_profile']['block_ids'])*len(sizes),
                    new_validation_tasks=len(rows),validation_opportunities_per_condition=n),
                uncertainty_method='Independent whole-block resampling of original and local calibration; the same paired validation-block resample for both forecasts, stratified by original quotas. Nominal pointwise conditional intervals; temporal drift and population coverage not identified.')
    status_counts={}
    for row in rows:status_counts[row['status']]=status_counts.get(row['status'],0)+1
    result['validation_status_counts']=status_counts
    for name in names:
        settings=plan['conditions'][name]
        original=settings['original_forecasts'];local=settings['local_forecasts']
        oe={mode:profile_errors(empirical[name],forecast) for mode,forecast in original.items()}
        le={mode:profile_errors(empirical[name],forecast) for mode,forecast in local.items()}
        tolerance=plan['design']['conditions'][name]['absolute_profile_error_tolerance']
        selected=[r for r in opportunities if r['condition']==name]
        result['conditions'][name]=dict(observed=empirical[name],original_forecasts=original,local_forecasts=local,
            original_errors=oe,local_errors=le,original_tolerance=tolerance,
            original_within_tolerance=within_tolerance(oe['joint']['maximum_absolute_survival_error'],tolerance),
            local_within_original_tolerance=within_tolerance(le['joint']['maximum_absolute_survival_error'],tolerance),
            local_mean_squared_error_improvement=oe['joint']['mean_squared_survival_error']-le['joint']['mean_squared_survival_error'],
            zero_completion_fraction=float(np.mean([r['zero_completion'] for r in selected])),
            upper_censor_fraction=float(np.mean([r['upper_censored'] for r in selected])),
            nonmonotone_opportunities=sum(r['nonmonotone_success_pattern'] for r in selected),
            memory_budgets_bytes=settings['memory_budgets_bytes'],cpu_budgets_seconds=settings['cpu_budgets_seconds'])
    original_profile=plan['reference_profile'];local_profile=plan['local_profile']
    rng=np.random.default_rng(np.random.SeedSequence([config['seed'],6]))
    residuals={name:{which:[] for which in ('original','local')} for name in names}
    gain_draws={name:[] for name in names}
    contrast_draws={name:[] for name in names if name!='aligned'}
    for _ in range(config['analysis_bootstrap_replicates']):
        original_boot=resample_profiles(original_profile,rng.integers(0,len(original_profile['block_ids']),len(original_profile['block_ids'])))
        local_boot=resample_profiles(local_profile,rng.integers(0,len(local_profile['block_ids']),len(local_profile['block_ids'])))
        index=np.concatenate([rng.choice(np.arange(stratum,n,plan['budget_strata']),config['validation_repetitions_per_budget_stratum'],replace=True)
                              for stratum in range(plan['budget_strata'])])
        actual={name:np.mean(outcomes[name][index,None]>=sizes,axis=0) for name in names}
        for name in names:
            settings=plan['conditions'][name]
            predictions={which:forecast_largest(profile,settings['memory_budgets_bytes'],settings['cpu_budgets_seconds'],mode='joint')['survival_at_sizes']
                         for which,profile in [('original',original_boot),('local',local_boot)]}
            for which,prediction in predictions.items():residuals[name][which].append(actual[name]-prediction)
            gain_draws[name].append(np.mean((actual[name]-predictions['original'])**2)-np.mean((actual[name]-predictions['local'])**2))
        for name in contrast_draws:contrast_draws[name].append(actual[name]-actual['aligned'])
    tail=(1-config['nominal_interval_level'])/2
    for name in names:
        result['conditions'][name]['paired_recalibration_gain_nominal_interval']=np.quantile(gain_draws[name],[tail,1-tail])
        result['conditions'][name]['residual_pointwise_nominal_intervals']={which:np.quantile(draws,[tail,1-tail],axis=0) for which,draws in residuals[name].items()}
    for name,draws in contrast_draws.items():
        actual=empirical[name]['survival_at_sizes']-empirical['aligned']['survival_at_sizes']
        predictions={which:np.asarray(plan['conditions'][name][which+'_forecasts']['joint']['survival_at_sizes'])-np.asarray(plan['conditions']['aligned'][which+'_forecasts']['joint']['survival_at_sizes'])
                     for which in ('original','local')}
        result['contrasts'][name]=dict(observed=actual,predictions=predictions,
            maximum_absolute_error={which:float(np.max(abs(actual-prediction))) for which,prediction in predictions.items()},
            observed_pointwise_nominal_interval=np.quantile(draws,[tail,1-tail],axis=0))
    result['cost_changes']={resource:dict(original_median=original_profile[key],local_median=local_profile[key],
        local_to_original_ratio=np.asarray(local_profile[key])/np.asarray(original_profile[key]))
        for resource,key in [('peak_rss_bytes','median_memory_bytes'),('cpu_seconds','median_cpu_seconds')]}
    result['summary']={name:dict(original_error=row['original_errors']['joint']['maximum_absolute_survival_error'],
        local_error=row['local_errors']['joint']['maximum_absolute_survival_error'],original_tolerance=row['original_tolerance'],
        original_pass=row['original_within_tolerance'],local_pass=row['local_within_original_tolerance'],
        local_mse_improvement=row['local_mean_squared_error_improvement']) for name,row in result['conditions'].items()}
    return result


def transfer_figures(result, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from orthopolity.figures import save_figure
    from pathlib import Path
    output=Path(output);sizes=np.asarray(result['config']['sizes'])
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'svg.fonttype':'none'})
    fig,axes=plt.subplots(2,2,figsize=(11,8),layout='constrained')
    for ax,(name,row) in zip(axes.flat,result['conditions'].items()):
        ax.plot(sizes,row['observed']['survival_at_sizes'],'ko-',label='Fresh observed outcomes',ms=4)
        ax.plot(sizes,row['original_forecasts']['joint']['survival_at_sizes'],'--',color='#28669b',label='Original frozen forecast')
        ax.plot(sizes,row['local_forecasts']['joint']['survival_at_sizes'],':',color='#ba5c22',label='Prospective local recalibration',lw=2)
        ax.set(xscale='log',ylim=(-.03,1.03),xlabel='Matrix side length',ylabel='P(largest completed size ≥ threshold)',title=name.replace('_',' '))
        ax.set_xticks(sizes,labels=[str(v) for v in sizes]);ax.minorticks_off();ax.legend(fontsize=7,frameon=False)
        ax.spines[['top','right']].set_visible(False);ax.grid(alpha=.2)
    n=result['sample_counts']['validation_opportunities_per_condition']
    fig.suptitle(f'Forecast transfer versus separately calibrated local prediction\nSame original quotas; {n} fresh full-grid opportunities per condition on the same machine/date')
    for suffix in ('png','svg'):save_figure(fig,output/f'comparison.{suffix}',dpi=180)
    plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(10,4),layout='constrained')
    for ax,(resource,row) in zip(axes,result['cost_changes'].items()):
        ax.plot(sizes,row['local_to_original_ratio'],'o-',color='#28669b')
        ax.axhline(1,color='gray',ls='--',lw=.8)
        ax.set(xscale='log',xlabel='Matrix side length',ylabel='Local / original median cost',title=resource.replace('_',' '))
        ax.set_xticks(sizes,labels=[str(v) for v in sizes]);ax.minorticks_off();ax.spines[['top','right']].set_visible(False);ax.grid(alpha=.2)
    fig.suptitle('Measured cost changes before fresh validation\nTotal resident-memory peak includes process overhead; CPU includes all worker threads')
    for suffix in ('png','svg'):save_figure(fig,output/f'cost-changes.{suffix}',dpi=180)
    plt.close(fig)
