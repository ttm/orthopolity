"""Study-excluded predictions; common fitted spread isolates location choice.

These working Gaussian forecasts score reported slopes, not individual organisms
or complete resource profiles. No measurement error is inferred from SlopeSD.
"""
from __future__ import annotations

import csv
import io
import math
from pathlib import Path

import numpy as np
from scipy.special import ndtr
from scipy.stats import norm


def number(value):
    try:
        parsed=float(value)
    except (TypeError,ValueError):
        return None
    return parsed if math.isfinite(parsed) else None


def select_rows(path, config):
    """Keep exact source row identifiers and a reason for every exclusion."""
    table=csv.DictReader(io.StringIO(Path(path).read_text('utf-8')),delimiter=' ',quotechar='"')
    accepted=[];membership=[]
    for source_row,row in enumerate(table,2):
        study=row['StudyID'].strip();slope=number(row['Slope'])
        lower=number(row['SizeRangeMinimum']);upper=number(row['SizeRangeMaximum'])
        reason=None
        if any(row[key].strip()!=value for key,value in config['inclusion'].items()
               if key!='finite_slope_and_positive_ordered_bounds'):
            reason='different_axis_or_spectrum_method'
        elif slope is None or lower is None or upper is None or not 0<lower<upper:
            reason='missing_or_invalid_slope_or_size_bounds'
        elif study in config['excluded_studies']:
            reason='known_invalid_study_bounds'
        se=number(row['SlopeSE']);se=se if se is not None and se>0 else None
        cl=number(row['SlopeConfIntLow']);cu=number(row['SlopeConfIntUp'])
        ci_se=(cu-cl)/3.92 if cl is not None and cu is not None and cu>cl else None
        sensitivity_se=se if se is not None else ci_se
        identifier=dict(source_row=source_row,study=study,sample_id=row['SampleID'].strip(),
            included_point_analysis=reason is None,included_primary=reason is None and se is not None,
            included_ci_sensitivity=reason is None and sensitivity_se is not None,
            exclusion_reason=reason,primary_se_source='SlopeSE' if se is not None else None,
            sensitivity_se_source=('SlopeSE' if se is not None else 'CI_width_assuming_95_percent_normal')
                                  if sensitivity_se is not None else None)
        membership.append(identifier)
        if reason is None:
            accepted.append(dict(identifier,slope=slope,size_minimum=lower,size_maximum=upper,
                log_span=math.log(upper)-math.log(lower),direct_se=se,sensitivity_se=sensitivity_se,
                body_mass_specification=row.get('XaxisParameterTypeSpecification'),
                body_mass_units=row.get('XaxisParameterUnit'),
                body_mass_unit_specification=row.get('XaxisParameterUnitSpecification'),
                biomass_units=row.get('YaxisParameterUnit'),
                biomass_specification=row.get('YaxisParameterTypeSpecification')))
    return accepted,membership


def study_weights(studies):
    values=np.asarray(studies)
    if values.ndim!=1 or len(values)==0:
        raise ValueError('At least one labelled study row is required')
    labels,counts=np.unique(values,return_counts=True)
    return np.asarray([1/(len(labels)*counts[np.flatnonzero(labels==s)[0]]) for s in values])


def fit_training(slopes, errors, studies):
    """Weighted moments use only supplied training rows and known errors."""
    y=np.asarray(slopes,float);se=np.asarray(errors,float)
    if y.ndim!=1 or y.shape!=se.shape or len(y)!=len(studies) or not len(y):
        raise ValueError('Aligned nonempty slopes, errors and study labels required')
    if not np.isfinite(y).all() or not np.isfinite(se).all() or np.any(se<=0):
        raise ValueError('Finite slopes and strictly positive standard errors required')
    weights=study_weights(studies)
    mean=float(weights@y)
    observed=float(weights@((y-mean)**2));measurement=float(weights@(se**2))
    return dict(mean=mean,tau_squared=max(0.,observed-measurement),
                observed_centered_variance=observed,weighted_measurement_variance=measurement,
                rows=len(y),studies=len(set(studies)))


def score_prediction(rows, error_key, mean, tau_squared, config):
    y=np.asarray([r['slope'] for r in rows]);se=np.asarray([r[error_key] for r in rows])
    spread=np.sqrt(tau_squared+se**2)
    z=(y-mean)/spread
    logpdf=-.5*np.log(2*np.pi)-np.log(spread)-.5*z**2
    quantile=float(norm.ppf((1+config['predictive_interval_level'])/2))
    endpoint={}
    spans=np.asarray([r['log_span'] for r in rows])
    for factor in config['endpoint_drift_factors']:
        tolerance=np.log(factor)/spans
        target=config['predicted_nbss_slope']
        probability=ndtr((target+tolerance-mean)/spread)-ndtr((target-tolerance-mean)/spread)
        endpoint[str(factor)]=dict(observed_point_fraction=float(np.mean(abs(y-target)<=tolerance)),
            forecast_reported_slope_fraction=float(np.mean(probability)),
            mean_absolute_calibration_gap=float(abs(np.mean(probability)-np.mean(abs(y-target)<=tolerance))))
    return dict(mean=float(mean),tau_squared=float(tau_squared),mean_log_predictive_density=float(np.mean(logpdf)),
                predictive_coverage_fraction=float(np.mean(abs(z)<=quantile)),
                mean_absolute_slope_error=float(np.mean(abs(y-mean))),endpoint_drift_checks=endpoint)


def leave_study_out(rows, error_key, config):
    usable=[r for r in rows if r[error_key] is not None]
    studies=sorted({r['study'] for r in usable})
    if len(studies)<3:raise ValueError('At least three eligible studies required')
    folds=[]
    for held in studies:
        train=[r for r in usable if r['study']!=held];test=[r for r in usable if r['study']==held]
        fit=fit_training([r['slope'] for r in train],[r[error_key] for r in train],[r['study'] for r in train])
        models={
            'fixed_neutral_shared_scatter':score_prediction(test,error_key,config['predicted_nbss_slope'],fit['tau_squared'],config),
            'training_location_shared_scatter':score_prediction(test,error_key,fit['mean'],fit['tau_squared'],config),
            'fixed_neutral_measurement_only':score_prediction(test,error_key,config['predicted_nbss_slope'],0.,config)}
        delta=models['fixed_neutral_shared_scatter']['mean_log_predictive_density']-models['training_location_shared_scatter']['mean_log_predictive_density']
        folds.append(dict(held_study=held,held_rows=len(test),training_studies=sorted(set(studies)-{held}),
            training=fit,models=models,fixed_minus_training_location_log_score=delta,
            observed_mean_slope=float(np.mean([r['slope'] for r in test])),
            observed_median_slope=float(np.median([r['slope'] for r in test]))))
    summary={model:dict(equal_study_mean_log_score=float(np.mean([fold['models'][model]['mean_log_predictive_density'] for fold in folds])),
        equal_study_predictive_coverage=float(np.mean([fold['models'][model]['predictive_coverage_fraction'] for fold in folds])))
        for model in config['models']}
    deltas=[fold['fixed_minus_training_location_log_score'] for fold in folds]
    return dict(rows=len(usable),studies=len(studies),folds=folds,models=summary,
        comparison=dict(equal_study_mean_fixed_minus_training_log_score=float(np.mean(deltas)),
                        median_fixed_minus_training_log_score=float(np.median(deltas)),
                        fixed_location_study_wins=sum(d>0 for d in deltas),ties=sum(d==0 for d in deltas),
                        inference='Overlapping training folds; descriptive scores without an independent-fold significance test'))


def point_forecast(rows, target):
    """No uncertainty imputation: robust study-median location transfer."""
    studies=sorted({r['study'] for r in rows});folds=[]
    if len(studies)<3:raise ValueError('At least three studies required')
    for held in studies:
        test=np.asarray([r['slope'] for r in rows if r['study']==held])
        medians=[np.median([r['slope'] for r in rows if r['study']==study]) for study in studies if study!=held]
        estimate=float(np.median(medians))
        folds.append(dict(held_study=held,held_rows=len(test),training_median_of_study_medians=estimate,
            fixed_location_mae=float(np.mean(abs(test-target))),training_location_mae=float(np.mean(abs(test-estimate)))))
    return dict(rows=len(rows),studies=len(studies),folds=folds,
        equal_study_fixed_mae=float(np.mean([r['fixed_location_mae'] for r in folds])),
        equal_study_training_mae=float(np.mean([r['training_location_mae'] for r in folds])))


def analyse(rows, config):
    return dict(kind='retrospective_leave_study_out_reported_slope_prediction',config=config,
        primary=leave_study_out(rows,'direct_se',config),
        ci_assumption_sensitivity=leave_study_out(rows,'sensitivity_se',config),
        uncertainty_free_point_sensitivity=point_forecast(rows,config['predicted_nbss_slope']),
        interpretation='A population-center forecast is distinct from universal individual flatness and complete resource-profile equivalence')
