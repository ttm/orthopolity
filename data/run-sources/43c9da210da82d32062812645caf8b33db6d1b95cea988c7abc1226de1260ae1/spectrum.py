"""Resource spectra and bounded power-law diagnostics.

All densities explicitly use natural-log intervals. This module contains no
automatic range selection and no universal-law classification.
"""
import numpy as np
from scipy.optimize import minimize_scalar
from scipy.special import logsumexp


def resource_spectrum(k, q, edges, weights=None):
    """Sum additive per-object resources, keeping empty and final-edge bins.

    Weights can represent inverse inclusion probabilities or survey weights.
    Missing/invalid observations raise; the caller must document exclusions.
    Observations outside the explicit domain are counted as excluded.
    """
    k, q, edges = (np.asarray(v, dtype=float) for v in (k, q, edges))
    w = np.ones_like(k) if weights is None else np.asarray(weights, dtype=float)
    if k.ndim != 1 or q.shape != k.shape or w.shape != k.shape:
        raise ValueError('k, q and weights must be aligned one-dimensional arrays')
    if not (np.all(np.isfinite(k)) and np.all(np.isfinite(q)) and np.all(np.isfinite(w))):
        raise ValueError('Missing values require an explicit exclusion policy')
    if np.any(k <= 0) or np.any(q < 0) or np.any(w < 0):
        raise ValueError('Positive scales and nonnegative additive resources/weights required')
    if edges.ndim != 1 or len(edges) < 2 or not np.all(np.isfinite(edges)) or np.any(edges <= 0) or np.any(np.diff(edges) <= 0):
        raise ValueError('Bin edges must be finite, positive and strictly increasing')
    inside = (k >= edges[0]) & (k <= edges[-1])
    k, q, w = k[inside], q[inside], w[inside]
    counts = np.histogram(k, bins=edges)[0]
    weighted_n = np.histogram(k, bins=edges, weights=w)[0]
    total_q = np.histogram(k, bins=edges, weights=w*q)[0]
    log_edges = np.log(edges)
    width = np.diff(log_edges)
    occupancy = total_q / width
    c = total_q.sum() / (log_edges[-1] - log_edges[0])
    mean_q = np.divide(total_q, weighted_n, out=np.full_like(total_q,np.nan), where=weighted_n>0)
    phi = occupancy/c if c > 0 else np.full_like(occupancy,np.nan)
    return dict(lower=edges[:-1], upper=edges[1:], center=np.exp((log_edges[:-1]+log_edges[1:])/2),
                log_width=width, count=counts, weighted_count=weighted_n,
                mean_resource=mean_q, resource_sum=total_q,
                multiplicity_log=weighted_n/width, occupancy=occupancy, phi=phi,
                C=float(c), excluded=int((~inside).sum()))


def bounded_power_mle(k, lo, hi):
    """Continuous PDF p(k) proportional to k^-alpha on [lo,hi].

    This is a descriptive fit, not a power-law goodness-of-fit test.
    """
    k=np.asarray(k,float)
    if not np.isfinite([lo,hi]).all() or lo<=0 or hi<=lo or k.ndim!=1 or len(k)<2 or np.any(~np.isfinite(k)) or np.any((k<lo)|(k>hi)):
        raise ValueError('At least two finite observations within a positive domain required')
    z=np.log(k/lo); L=np.log(hi/lo)
    def log_z(t):
        if abs(t)<1e-7: return np.log(L)-t*L/2+t*t*L*L/24
        return np.log(abs(-np.expm1(-t*L)/t))
    fit=minimize_scalar(lambda t: t*z.mean()+log_z(t), bounds=(-5,10),method='bounded')
    if not fit.success: raise RuntimeError('Bounded power-law fit failed')
    return float(1+fit.x)


def mean_resource_exponent(k,q,reference=1.0):
    """Fit E[q|k]=A*(k/reference)^d by a Gamma quasi-likelihood.

    Fits an arithmetic conditional mean, unlike OLS on log(q). Constant
    coefficient of variation is a working assumption; block bootstrap is
    used outside this function. A flexible mean model is needed for final work.
    """
    k,q=np.asarray(k,float),np.asarray(q,float)
    if k.ndim!=1 or k.shape!=q.shape or len(k)<3 or np.any(k<=0) or np.any(q<=0) or not (np.all(np.isfinite(k)) and np.all(np.isfinite(q))):
        raise ValueError('Aligned positive finite paired measurements required')
    if not np.isfinite(reference) or reference<=0 or np.ptp(np.log(k))==0:
        raise ValueError('Positive finite reference and varying scale measurements required')
    z=np.log(k/reference); logq=np.log(q)
    def log_a(d): return logsumexp(logq-d*z)-np.log(len(k))
    fit=minimize_scalar(lambda d: log_a(d)+d*z.mean(),bounds=(-4,6),method='bounded')
    if not fit.success: raise RuntimeError('Resource scaling fit failed')
    return float(fit.x),float(np.exp(log_a(fit.x)))


def rounded_gr_b(magnitudes, threshold, step=0.1):
    """Geometric-tail likelihood for magnitudes rounded to a fixed step.

    Round to the nearest step before thresholding; recorded extra precision is
    deliberately coarsened. Assumes an unbounded Gutenberg-Richter tail.
    """
    m=np.asarray(magnitudes,float)
    if m.ndim!=1 or not np.all(np.isfinite(m)): raise ValueError('Finite magnitudes required')
    if not np.isfinite([threshold,step]).all() or step<=0 or not np.isclose(threshold/step,np.round(threshold/step),rtol=0,atol=1e-8):
        raise ValueError('Positive finite step and finite threshold on the magnitude grid required')
    mr=np.round(m/step)*step
    t=np.round((mr[mr>=threshold-1e-8]-threshold)/step)
    if len(t)<2 or t.mean()<=0: raise ValueError('Insufficient tail variation')
    return float(np.log10(1+1/t.mean())/step),len(t)


def residual_audio(phi, sample_rate=22050, seconds_per_bin=0.3):
    """Illustrative mapping only: one octave per factor 2 in Phi, 440 Hz at 1.

    Values are clipped to [1/4,4] for pitch; empty bins are silent. Equal
    duration per bin is meaningful only for equal-log-width bins. No autoplay.
    """
    phi=np.asarray(phi,float)
    n=int(sample_rate*seconds_per_bin)
    t=np.arange(n)/sample_rate
    envelope=np.sin(np.pi*np.arange(n)/max(1,n-1))**2
    segments=[]
    for v in phi:
        f=440*np.clip(v,.25,4) if np.isfinite(v) and v>0 else 0
        segments.append(.15*np.sin(2*np.pi*f*t)*envelope if f else np.zeros(n))
    return np.concatenate(segments) if segments else np.array([],float)
