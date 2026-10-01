"""Held-out power and adequacy for two frozen budget-intervention models."""
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
from orthopolity.interventions import (
    decision_outcomes, expected_log_likelihood_ratio, intervention_allocations,
    log_likelihood_ratio, monte_carlo_rank_pvalue, multinomial_deviance,
    multinomial_samples, observation_probabilities, resource_probability_from_sample,
    wilson_interval,
)

ROOT=Path(__file__).resolve().parents[1]


def serializable(value):
    if isinstance(value,np.ndarray):return value.tolist()
    if isinstance(value,np.generic):return value.item()
    if isinstance(value,dict):return {k:serializable(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [serializable(v) for v in value]
    return value


def rate(value,level):
    value=np.asarray(value,dtype=bool)
    return dict(rate=float(value.mean()),successes=int(value.sum()),replicates=len(value),
                monte_carlo_interval=list(wilson_interval(int(value.sum()),len(value),level)))


def study(config):
    if config['candidate_alpha']*2>config['familywise_alpha']:
        raise ValueError('Candidate tests must respect the declared two-test error bound')
    edges=np.geomspace(*config['domain'],config['classes']+1)
    k=np.exp((np.log(edges[:-1])+np.log(edges[1:]))/2)
    widths=np.diff(np.log(edges));q1=k**config['primary_cost_exponent'];q2=k**config['auxiliary_cost_exponent']
    costs=np.vstack([q1,q2]);budgets=config['auxiliary_intervention']
    phase=2*np.pi*np.log(k/config['domain'][0])/np.log(config['domain'][1]/config['domain'][0])
    extra_weights=widths*np.exp(config['extra_objective_log_weight_amplitude']*np.cos(phase))
    physical=intervention_allocations(costs,widths,config['primary_budget'],budgets,extra_weights=extra_weights)
    patterns=np.random.default_rng(np.random.SeedSequence([config['seed'],90])).standard_normal(len(k))
    patterns-=patterns.mean()
    level=config['monte_carlo_interval_level'];reps=config['heldout_replicates'];alpha=config['candidate_alpha']
    calibrations=[];scenarios=[];cost_conditions=[]
    def rng(*stream):return np.random.default_rng(np.random.SeedSequence([config['seed'],*stream]))
    for error_index,sigma in enumerate(config['auxiliary_cost_log_error_sd']):
        measured_costs=np.vstack([q1,q2*np.exp(sigma*patterns)])
        predicted=intervention_allocations(measured_costs,widths,config['primary_budget'],budgets)
        cost_conditions.append(dict(auxiliary_log_error_sd=sigma,measured_costs=measured_costs,
                                    frozen_predictions=predicted))
        for design_index,design in enumerate(config['sampling_designs']):
            candidates={name:observation_probabilities(predicted[name]['counts'],q1,sampling=design)
                        for name in ('pf','kl')}
            for n_index,n in enumerate(config['samples_per_cohort']):
                calibration={}
                for model_index,model in enumerate(('pf','kl')):
                    p=candidates[model]
                    null=multinomial_samples(p,n,config['null_calibration_replicates'],rng(10,error_index,design_index,n_index,model_index))
                    calibration[model]=multinomial_deviance(null,p)
                    validation=multinomial_samples(p,n,reps,rng(20,error_index,design_index,n_index,model_index))
                    null_p=monte_carlo_rank_pvalue(multinomial_deviance(validation,p),calibration[model])
                    admissible_rank=int(np.floor(alpha*(len(calibration[model])+1)))
                    critical=(float(np.sort(calibration[model])[len(calibration[model])-admissible_rank])
                              if admissible_rank>0 else None)
                    calibrations.append(dict(auxiliary_log_error_sd=sigma,sampling=design,samples_per_cohort=n,
                        candidate=model,candidate_alpha=alpha,
                        calibrated_deviance_critical_value=critical,
                        rejection_rule='Joint deviance strictly exceeds calibrated critical value; ties do not reject.',
                        heldout_null_rejection=rate(null_p<=alpha,level),
                        calibration_replicates=config['null_calibration_replicates'],
                        minimum_rank_pvalue=1/(config['null_calibration_replicates']+1)))
                for truth_index,truth in enumerate(('pf','kl','extra')):
                    true_counts=physical[truth]['counts']
                    truth_p=observation_probabilities(true_counts,q1,sampling=design)
                    observed=multinomial_samples(truth_p,n,reps,rng(30,error_index,design_index,n_index,truth_index))
                    pvalues={model:monte_carlo_rank_pvalue(multinomial_deviance(observed,candidates[model]),calibration[model])
                             for model in ('pf','kl')}
                    outcome=decision_outcomes(pvalues['pf'],pvalues['kl'],alpha)
                    cohort_llr=log_likelihood_ratio(observed,candidates['pf'],candidates['kl'],by_cohort=True)
                    joint_llr=cohort_llr.sum(axis=-1)
                    genuine_candidate=(sigma==0 and truth!='extra')
                    target=truth if genuine_candidate else 'both_rejected'
                    expected=expected_log_likelihood_ratio(truth_p,candidates['pf'],candidates['kl'],n)
                    resource=resource_probability_from_sample(observed,q1,sampling=design)
                    true_resource=observation_probabilities(true_counts,q1,sampling='primary_resource')
                    resource_tv=.5*np.abs(resource-true_resource).sum(axis=-1)
                    physical_sample_totals=(observed*q1).sum(axis=-1)
                    rates={name:rate(outcome==name,level) for name in ('pf','kl','ambiguous','both_rejected')}
                    scenarios.append(dict(truth=truth,auxiliary_log_error_sd=sigma,sampling=design,samples_per_cohort=n,
                        exact_frozen_candidate_is_true=genuine_candidate,
                        correct_decision_target=target,correct_decision=rate(outcome==target,level),
                        decision_rates=rates,
                        rejection_rates={model:rate(pvalues[model]<=alpha,level) for model in ('pf','kl')},
                        forced_likelihood_pf_fraction=dict(before=float(np.mean(cohort_llr[:,0]>=0)),
                            after=float(np.mean(cohort_llr[:,1]>=0)),joint=float(np.mean(joint_llr>=0))),
                        forced_likelihood_matching_truth_rate=(rate(joint_llr>=0 if truth=='pf' else joint_llr<0,level)
                            if genuine_candidate else None),
                        expected_log_likelihood_ratio=expected,
                        observed_log_likelihood_ratio_mean=float(joint_llr.mean()),
                        observed_log_likelihood_ratio_variance=float(joint_llr.var(ddof=1)),
                        primary_resource_probability_total_variation=dict(before_mean=float(resource_tv[:,0].mean()),
                            after_mean=float(resource_tv[:,1].mean()),
                            after_quantile_90=float(np.quantile(resource_tv[:,1],.9))),
                        physical_sample_resource_total=dict(before_mean=float(physical_sample_totals[:,0].mean()),
                            before_sd=float(physical_sample_totals[:,0].std(ddof=1)),
                            after_mean=float(physical_sample_totals[:,1].mean()),after_sd=float(physical_sample_totals[:,1].std(ddof=1))),
                        mean_zero_count_classes_per_cohort=np.mean((observed==0).sum(axis=-1),axis=0)))
            print(f"cost log-SD {sigma:g}; {design}: complete",flush=True)
    requirements=[]
    for design in config['sampling_designs']:
        for truth in ('pf','kl'):
            selected=[s for s in scenarios if s['sampling']==design and s['truth']==truth and s['auxiliary_log_error_sd']==0]
            passing=[s['samples_per_cohort'] for s in selected
                     if s['correct_decision']['monte_carlo_interval'][0]>=config['identification_target_rate']]
            requirements.append(dict(sampling=design,truth=truth,target=config['identification_target_rate'],
                first_tested_n_with_conditional_mc_lower_bound_above_target=min(passing) if passing else None,
                range_tested=config['samples_per_cohort'],criterion='Unique acceptance of the true frozen candidate; 95% conditional Monte Carlo lower bound reaches target. No interpolation between grid values.'))
    return dict(config=config,classes=dict(edges=edges,centers=k,log_widths=widths,true_costs=costs,
        extra_objective_weights=extra_weights),physical_truths=physical,auxiliary_cost_error_pattern=patterns,
        cost_conditions=cost_conditions,calibrations=calibrations,scenarios=scenarios,sampling_requirements=requirements)


def figures(result,output):
    config=result['config'];rows=result['scenarios']
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'svg.fonttype':'none'})
    fig,axes=plt.subplots(2,2,figsize=(11.8,8),layout='constrained')
    model_colors={'pf':'#28669b','kl':'#ba5c22','extra':'#6a4c93'}
    for ax,design,title in zip(axes.flat[:2],config['sampling_designs'],['Uniform object opportunities','Resource-proportional opportunities']):
        for truth in ('pf','kl'):
            subset=[s for s in rows if s['sampling']==design and s['truth']==truth and s['auxiliary_log_error_sd']==0]
            x=[s['samples_per_cohort'] for s in subset]
            rates=[s['correct_decision']['rate'] for s in subset]
            lo=[s['correct_decision']['monte_carlo_interval'][0] for s in subset]
            hi=[s['correct_decision']['monte_carlo_interval'][1] for s in subset]
            ax.plot(x,rates,'o-',color=model_colors[truth],label=f'{truth.upper()} truth: unique acceptance',ms=4)
            ax.fill_between(x,lo,hi,color=model_colors[truth],alpha=.12)
            ax.plot(x,[s['forced_likelihood_matching_truth_rate']['rate'] for s in subset],':',color=model_colors[truth],lw=1.2)
        ax.axhline(config['identification_target_rate'],ls='--',color='gray',lw=.8)
        ax.set(xscale='log',ylim=(-.02,1.02),xlabel='Independent draws in each cohort',ylabel='Correct model fraction',title=title)
        ax.legend(fontsize=7,frameon=False)
    ax=axes[1,0]
    for truth,sigma,label in [('extra',0,'Extra objective'),('pf',.25,'PF + auxiliary cost error'),('kl',.25,'KL + auxiliary cost error')]:
        if sigma not in config['auxiliary_cost_log_error_sd']:continue
        for design,style in zip(config['sampling_designs'],['-','--']):
            subset=[s for s in rows if s['sampling']==design and s['truth']==truth and s['auxiliary_log_error_sd']==sigma]
            x=[s['samples_per_cohort'] for s in subset]
            ax.plot(x,[s['decision_rates']['both_rejected']['rate'] for s in subset],style,color=model_colors[truth],lw=1.5,
                    label=f"{label}; {'objects' if design=='objects' else 'resource'}")
    ax.set(xscale='log',ylim=(-.02,1.02),xlabel='Independent draws in each cohort',ylabel='Both candidates rejected',title='Misspecification can reject both models')
    ax.legend(fontsize=7,frameon=False)
    ax=axes[1,1]
    for truth in ('pf','kl'):
        for design,style in zip(config['sampling_designs'],['-','--']):
            subset=[s for s in rows if s['sampling']==design and s['truth']==truth and s['auxiliary_log_error_sd']==0]
            ax.plot([s['samples_per_cohort'] for s in subset],
                    [s['primary_resource_probability_total_variation']['after_mean'] for s in subset],style,
                    color=model_colors[truth],label=f"{truth.upper()}; {'objects weighted by q' if design=='objects' else 'resource design'}")
    ax.set(xscale='log',yscale='log',xlabel='Independent draws in each cohort',ylabel='Mean resource-profile total variation',title='Known costs: resource diagnostic precision')
    ax.legend(fontsize=7,frameon=False)
    for ax in axes.flat:ax.spines[['top','right']].set_visible(False);ax.grid(alpha=.2)
    fig.suptitle('Frozen 12→8 budget intervention: held-out sampling design\nSolid in top panels: unique calibrated acceptance; dotted: forced likelihood winner. Bands: conditional Monte Carlo intervals.',fontsize=10)
    for suffix in ('png','svg'):save_figure(fig,output/f'power.{suffix}',dpi=190)
    plt.close(fig)

    fig,axes=plt.subplots(1,2,figsize=(10.5,4),layout='constrained')
    for ax,design in zip(axes,config['sampling_designs']):
        for model,color in model_colors.items():
            if model=='extra':continue
            for sigma,style in zip(config['auxiliary_cost_log_error_sd'],['-','--']):
                subset=[c for c in result['calibrations'] if c['sampling']==design and c['candidate']==model and c['auxiliary_log_error_sd']==sigma]
                x=[c['samples_per_cohort'] for c in subset];v=[c['heldout_null_rejection']['rate'] for c in subset]
                low=[c['heldout_null_rejection']['monte_carlo_interval'][0] for c in subset]
                high=[c['heldout_null_rejection']['monte_carlo_interval'][1] for c in subset]
                ax.errorbar(x,v,yerr=[np.array(v)-low,np.array(high)-v],fmt='o'+style,color=color,lw=1,capsize=2,
                            label=f'{model.upper()} null, cost log-SD {sigma:g}')
        ax.axhline(config['candidate_alpha'],color='gray',ls=':',lw=1)
        ax.set(xscale='log',ylim=(0,.065),xlabel='Independent draws in each cohort',ylabel='Held-out null rejection rate',title=design.replace('_',' ').capitalize())
        ax.legend(fontsize=7,frameon=False);ax.grid(alpha=.2);ax.spines[['top','right']].set_visible(False)
    fig.suptitle('Independent null calibration and held-out verification\nIntervals quantify validation Monte Carlo error conditional on the frozen calibration; nominal candidate alpha = 0.025.',fontsize=10)
    for suffix in ('png','svg'):save_figure(fig,output/f'calibration.{suffix}',dpi=190)
    plt.close(fig)

    fig,axes=plt.subplots(2,2,figsize=(11,7),layout='constrained')
    k=np.asarray(result['classes']['centers']);q1=np.asarray(result['classes']['true_costs'])[0]
    for row,design in enumerate(config['sampling_designs']):
        for model,truth in result['physical_truths'].items():
            probability=observation_probabilities(np.asarray(truth['counts']),q1,sampling=design)
            for cohort in range(2):axes[row,cohort].plot(k,probability[cohort],color=model_colors[model],label=model.upper() if model!='extra' else 'Extra objective',lw=1.5)
        for cohort,ax in enumerate(axes[row]):
            ax.set(xscale='log',yscale='log',xlabel='Class size k',ylabel='Sampling probability per class',title=f"{design.replace('_',' ').capitalize()}; auxiliary budget {config['auxiliary_intervention'][cohort]:g}")
            ax.legend(frameon=False,fontsize=8);ax.grid(alpha=.2);ax.spines[['top','right']].set_visible(False)
    fig.suptitle('Same physical resource predictions, different observation opportunities',fontsize=11)
    for suffix in ('png','svg'):save_figure(fig,output/f'sampling-targets.{suffix}',dpi=190)
    plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,default=ROOT/'configs/intervention_study_2026-10-01.json')
    parser.add_argument('--output',type=Path,default=ROOT/'results/interventions')
    args=parser.parse_args();specification=args.config.read_bytes();config=json.loads(specification)
    started=time.perf_counter();result=study(config)
    result['config_sha256']=hashlib.sha256(specification).hexdigest()
    result['versions']=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,matplotlib=matplotlib.__version__)
    result['interpretation']=config['interpretation']
    result['calibration_method']='Upper-tail Monte Carlo rank p=(1+#null>=observed)/(R+1); independent calibration and evaluation streams.'
    args.output.mkdir(parents=True,exist_ok=True)
    (args.output/'study.json').write_text(json.dumps(serializable(result),indent=2,allow_nan=False)+'\n')
    with (args.output/'power.csv').open('w',newline='') as handle:
        writer=csv.writer(handle,lineterminator='\n');writer.writerow(['truth','cost_log_error_sd','sampling','samples_per_cohort','exact_candidate_true','correct_target','correct_decision_rate','conditional_mc_low','conditional_mc_high','pf_only','kl_only','ambiguous','both_rejected','forced_likelihood_pf_fraction','mean_resource_tv_after'])
        for s in result['scenarios']:
            writer.writerow([s['truth'],s['auxiliary_log_error_sd'],s['sampling'],s['samples_per_cohort'],s['exact_frozen_candidate_is_true'],s['correct_decision_target'],s['correct_decision']['rate'],*s['correct_decision']['monte_carlo_interval'],
                             *[s['decision_rates'][name]['rate'] for name in ('pf','kl','ambiguous','both_rejected')],s['forced_likelihood_pf_fraction']['joint'],s['primary_resource_probability_total_variation']['after_mean']])
    with (args.output/'calibration.csv').open('w',newline='') as handle:
        writer=csv.writer(handle,lineterminator='\n');writer.writerow(['cost_log_error_sd','sampling','samples_per_cohort','candidate','alpha','deviance_critical_value','heldout_null_rejection','conditional_mc_low','conditional_mc_high'])
        for c in result['calibrations']:writer.writerow([c['auxiliary_log_error_sd'],c['sampling'],c['samples_per_cohort'],c['candidate'],c['candidate_alpha'],c['calibrated_deviance_critical_value'],c['heldout_null_rejection']['rate'],*c['heldout_null_rejection']['monte_carlo_interval']])
    figures(result,args.output)
    print(json.dumps(result['sampling_requirements'],indent=2))
    print(f'Saved {len(result["scenarios"])} held-out scenarios and {len(result["calibrations"])} null checks in {time.perf_counter()-started:.2f}s to {args.output}')


if __name__=='__main__':main()
