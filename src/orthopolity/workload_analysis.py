"""Audit actual workload outcomes against forecasts frozen before validation."""
from __future__ import annotations

from pathlib import Path

import numpy as np

from orthopolity.workload_prediction import forecast_largest, outcome_profile, resample_profiles


def observed_opportunities(plan, rows):
    """Require a complete grid; use executed completion, never inverse costs."""
    config = plan['config']
    sizes = config['sizes']
    groups = {}
    for row in rows:
        if row.get('split') != 'validation':
            raise ValueError('Only validation measurements belong in the outcome audit')
        key = (row['block_id'], row['condition'])
        if row['condition'] not in plan['conditions'] or row['size'] not in sizes:
            raise ValueError('Unexpected validation condition or size')
        group = groups.setdefault(key, {})
        if row['size'] in group:
            raise ValueError('Duplicate size within a validation opportunity')
        if row['completed']:
            if not row['numerical_valid'] or row['peak_rss_bytes'] > row['memory_budget_bytes'] or row['cpu_seconds'] > row['cpu_budget_seconds']:
                raise ValueError('Completed outcome violates its measured acceptance rule')
        group[row['size']] = row
    expected = {(block, condition) for block in range(plan['validation_blocks']) for condition in plan['conditions']}
    if set(groups) != expected or any(set(group) != set(sizes) for group in groups.values()):
        raise ValueError('Every planned opportunity needs the full declared size grid')
    opportunities = []
    for block, condition in sorted(groups):
        group = groups[block, condition]
        stratum = block % plan['budget_strata']
        settings = plan['conditions'][condition]
        mb = settings['memory_budgets_bytes'][stratum]
        cb = settings['cpu_budgets_seconds'][stratum]
        for row in group.values():
            if row['budget_stratum'] != stratum or row['memory_budget_bytes'] != mb or row['cpu_budget_seconds'] != cb:
                raise ValueError('Observed opportunity does not match its frozen assigned quotas')
        success = np.array([group[size]['completed'] for size in sizes], dtype=bool)
        largest = max((size for size, passed in zip(sizes, success) if passed), default=0)
        opportunities.append(dict(block_id=block, condition=condition, budget_stratum=stratum,
            memory_budget_bytes=mb, cpu_budget_seconds=cb, largest_completed_size=largest,
            zero_completion=largest == 0, upper_censored=largest == sizes[-1],
            nonmonotone_success_pattern=bool(np.any(np.diff(success.astype(int)) > 0))))
    return opportunities


def profile_errors(observed, predicted):
    actual = np.asarray(observed['survival_at_sizes'])
    forecast = np.asarray(predicted['survival_at_sizes'])
    return dict(maximum_absolute_survival_error=float(np.max(np.abs(actual-forecast))),
                mean_squared_survival_error=float(np.mean((actual-forecast)**2)),
                probability_total_variation=float(.5*np.sum(np.abs(np.asarray(observed['probability'])-predicted['probability']))))


def analyse_pilot(plan, rows):
    config = plan['config']
    sizes = np.asarray(config['sizes'])
    opportunities = observed_opportunities(plan, rows)
    names = list(plan['conditions'])
    n = plan['validation_blocks']
    outcomes = {name: np.array([o['largest_completed_size'] for o in opportunities if o['condition']==name]) for name in names}
    empirical = {name: outcome_profile(value, sizes) for name,value in outcomes.items()}
    result = dict(kind='Actual measured computation under assigned cooperative resource-acceptance quotas',
                  config=config, frozen_utc=plan['frozen_utc'],
                  calibrated_profile=plan['calibrated_profile'], design=plan['design'],
                  opportunities=opportunities, conditions={}, contrasts={},
                  sample_counts=dict(calibration_tasks=len(plan['calibrated_profile']['block_ids'])*len(sizes),
                                     validation_tasks=len(rows), validation_opportunities_per_condition=n),
                  uncertainty_method='Whole calibration blocks and paired validation blocks; validation resampled within frozen budget strata. Nominal bootstrap intervals remain conditional and exploratory; serial drift is not identified.')
    status_counts = {}
    for row in rows:
        status_counts[row['status']] = status_counts.get(row['status'],0)+1
    result['validation_status_counts'] = status_counts
    for name in names:
        predicted = plan['conditions'][name]['forecasts']
        errors = {mode:profile_errors(empirical[name], value) for mode,value in predicted.items()}
        tolerance = plan['design']['conditions'][name]['absolute_profile_error_tolerance']
        selected = [o for o in opportunities if o['condition']==name]
        patterns = np.array([[next(row['completed'] for row in rows if row['block_id']==block and row['condition']==name and row['size']==size)
                              for size in sizes] for block in range(n)])
        result['conditions'][name] = dict(observed=empirical[name], forecasts=predicted, errors=errors,
            memory_budgets_bytes=plan['conditions'][name]['memory_budgets_bytes'],
            cpu_budgets_seconds=plan['conditions'][name]['cpu_budgets_seconds'],
            frozen_absolute_profile_tolerance=tolerance,
            within_frozen_tolerance=errors['joint']['maximum_absolute_survival_error'] <= tolerance,
            zero_completion_fraction=float(np.mean([o['zero_completion'] for o in selected])),
            upper_censor_fraction=float(np.mean([o['upper_censored'] for o in selected])),
            nonmonotone_opportunities=int(sum(o['nonmonotone_success_pattern'] for o in selected)),
            observed_per_size_completion_fraction=patterns.mean(axis=0),
            largest_survival_minus_size_completion=empirical[name]['survival_at_sizes']-patterns.mean(axis=0),
            joint_mean_squared_error_improvement={mode:errors[mode]['mean_squared_survival_error']-errors['joint']['mean_squared_survival_error']
                                                 for mode in errors if mode!='joint'})
    # Resample paired blocks, preserving the seven-stratum design and every
    # condition's within-block outcomes. Calibration and validation streams are
    # independent. Assigned budgets are fixed, not recalibrated after outcomes.
    rng = np.random.default_rng(np.random.SeedSequence([config['seed'],5]))
    reps = config['analysis_bootstrap_replicates']
    profile = plan['calibrated_profile']
    residual_draws = {name:[] for name in names}
    contrast_draws = {name:[] for name in names if name!='aligned'}
    gains = {name:{mode:[] for mode in ['memory_only','cpu_only','resource_independent','budget_independent']} for name in names}
    for _ in range(reps):
        cal_index=rng.integers(0,len(profile['block_ids']),len(profile['block_ids']))
        boot_profile=resample_profiles(profile,cal_index)
        observed_index=np.concatenate([rng.choice(np.arange(stratum,n,plan['budget_strata']),
            config['validation_repetitions_per_budget_stratum'],replace=True) for stratum in range(plan['budget_strata'])])
        actual={name:np.mean(outcomes[name][observed_index,None]>=sizes,axis=0) for name in names}
        predicted={}
        for name in names:
            settings=plan['conditions'][name]
            mb=np.asarray(settings['memory_budgets_bytes']);cb=np.asarray(settings['cpu_budgets_seconds'])
            predicted[name]=forecast_largest(boot_profile,mb,cb,mode='joint')['survival_at_sizes']
            residual_draws[name].append(actual[name]-predicted[name])
            main_error=np.mean((actual[name]-predicted[name])**2)
            for mode in gains[name]:
                if mode=='budget_independent':
                    baseline=forecast_largest(boot_profile,np.repeat(mb,len(mb)),np.tile(cb,len(cb)),mode='joint')['survival_at_sizes']
                else:
                    baseline=forecast_largest(boot_profile,mb,cb,mode=mode)['survival_at_sizes']
                gains[name][mode].append(np.mean((actual[name]-baseline)**2)-main_error)
        for name in contrast_draws:
            contrast_draws[name].append(actual[name]-actual['aligned'])
    tail=(1-config['nominal_interval_level'])/2
    for name in names:
        result['conditions'][name]['residual_pointwise_nominal_interval']=np.quantile(residual_draws[name],[tail,1-tail],axis=0)
        result['conditions'][name]['comparator_improvement_nominal_interval']={mode:np.quantile(draws,[tail,1-tail]) for mode,draws in gains[name].items()}
    for name,draws in contrast_draws.items():
        actual=empirical[name]['survival_at_sizes']-empirical['aligned']['survival_at_sizes']
        predicted=np.asarray(plan['conditions'][name]['forecasts']['joint']['survival_at_sizes'])-plan['conditions']['aligned']['forecasts']['joint']['survival_at_sizes']
        result['contrasts'][name]=dict(reference='aligned',observed_survival_difference=actual,
            frozen_predicted_survival_difference=predicted,
            maximum_absolute_contrast_error=float(np.max(abs(actual-predicted))),
            observed_difference_pointwise_nominal_interval=np.quantile(draws,[tail,1-tail],axis=0))
    result['summary']=dict(conditions={name:dict(maximum_absolute_survival_error=row['errors']['joint']['maximum_absolute_survival_error'],
        frozen_tolerance=row['frozen_absolute_profile_tolerance'],within_frozen_tolerance=row['within_frozen_tolerance'],
        zero_fraction=row['zero_completion_fraction'],upper_censor_fraction=row['upper_censor_fraction'],
        nonmonotone_opportunities=row['nonmonotone_opportunities']) for name,row in result['conditions'].items()},
        scope='Prospective transfer of independently measured workload costs; assigned quotas and acceptance rule do not establish autonomous allocation or a natural law.')
    return result


def pilot_figures(result, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from orthopolity.figures import save_figure
    output=Path(output)
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'svg.fonttype':'none'})
    sizes=np.asarray(result['config']['sizes'])
    profile=result['calibrated_profile']
    fig,axes=plt.subplots(1,2,figsize=(10,4),layout='constrained')
    for ax,key,median_key,scale,ylabel in [
        (axes[0],'memory_costs','median_memory_bytes',2**20,'Total child peak resident memory (MiB)'),
        (axes[1],'cpu_costs','median_cpu_seconds',1,'Workload user + system CPU (seconds)')]:
        costs=np.asarray(profile[key])/scale
        for row in costs:ax.plot(sizes,row,'o-',color='#3575a8',alpha=.22,ms=3,lw=.8)
        ax.plot(sizes,np.asarray(profile[median_key])/scale,'o-',color='black',label='Monotone median')
        ax.set(xscale='log',yscale='log',xlabel='Matrix side length',ylabel=ylabel)
        ax.set_xticks(sizes,labels=[str(v) for v in sizes]);ax.minorticks_off();ax.legend(frameon=False)
        ax.spines[['top','right']].set_visible(False);ax.grid(alpha=.2)
    fig.suptitle('Actual cost calibration: 12 randomized blocks in fresh processes\nMemory includes import and warm-up; workload CPU includes construction and verification')
    for suffix in ('png','svg'):save_figure(fig,output/f'calibration.{suffix}',dpi=180)
    plt.close(fig)
    fig,axes=plt.subplots(2,2,figsize=(11,8),layout='constrained')
    styles={'joint':('#28669b','-','Paired calibration forecast'),
            'memory_only':('#b56522',':','Memory alone'),
            'cpu_only':('#5b9364',':','CPU alone'),
            'budget_independent':('#8a5f9c','--','Independent budget marginals')}
    for ax,(name,row) in zip(axes.flat,result['conditions'].items()):
        ax.plot(sizes,row['observed']['survival_at_sizes'],'ko-',label='Observed largest completed size',ms=4)
        for mode,(color,style,label) in styles.items():
            ax.plot(sizes,row['forecasts'][mode]['survival_at_sizes'],style,color=color,label=label,lw=1.3)
        ax.set(xscale='log',ylim=(-.03,1.03),xlabel='Declared matrix size',ylabel='P(largest completed size ≥ threshold)',title=name.replace('_',' '))
        ax.set_xticks(sizes,labels=[str(v) for v in sizes]);ax.minorticks_off()
        ax.legend(fontsize=7,frameon=False);ax.grid(alpha=.2);ax.spines[['top','right']].set_visible(False)
    fig.suptitle('Frozen forecasts and actual cooperative-quota outcomes\n28 full-grid opportunities per condition; zero outcomes and upper censoring retained')
    for suffix in ('png','svg'):save_figure(fig,output/f'profiles.{suffix}',dpi=180)
    plt.close(fig)
    fig,axes=plt.subplots(1,len(result['contrasts']),figsize=(12,4),layout='constrained')
    for ax,(name,row) in zip(np.atleast_1d(axes),result['contrasts'].items()):
        lo,hi=np.asarray(row['observed_difference_pointwise_nominal_interval'])
        actual=np.asarray(row['observed_survival_difference'])
        ax.fill_between(sizes,lo,hi,color='#28669b',alpha=.2,label='Conditional pointwise bootstrap interval')
        ax.plot(sizes,actual,'o-',color='#28669b',label='Observed paired difference')
        ax.plot(sizes,row['frozen_predicted_survival_difference'],'k--',label='Frozen predicted difference')
        ax.axhline(0,color='gray',lw=.7)
        ax.set(xscale='log',xlabel='Declared matrix size',ylabel='Survival difference from aligned',title=name.replace('_',' '))
        ax.set_xticks(sizes,labels=[str(v) for v in sizes]);ax.minorticks_off()
        ax.legend(fontsize=6,frameon=False);ax.grid(alpha=.2);ax.spines[['top','right']].set_visible(False)
    fig.suptitle('Resource-pairing and CPU-budget interventions\nSerial temporal dependence remains a limitation; these are exploratory measurement results')
    for suffix in ('png','svg'):save_figure(fig,output/f'contrasts.{suffix}',dpi=180)
    plt.close(fig)
