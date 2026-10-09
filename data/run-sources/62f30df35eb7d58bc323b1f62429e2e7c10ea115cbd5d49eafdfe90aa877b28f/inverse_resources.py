"""Conditional identification of a shared product-resource composition.

For fixed constituent exponents D and known allocation offsets v, b=alpha-v
obeys b=D theta.  The linear algebra here does not select D, a reference
measure, or a resource family.  Coefficients are unrestricted real parameters;
additional boundary constraints require their own identification analysis.
"""
from __future__ import annotations

import numpy as np


DEFAULT_RCOND = 1e-12


def _matrix(values, name):
    result = np.asarray(values, dtype=float)
    if result.ndim != 2 or min(result.shape) == 0 or not np.isfinite(result).all():
        raise ValueError(f"{name} must be a nonempty finite matrix")
    return result


def _vector(values, length, name):
    result = np.asarray(values, dtype=float)
    if result.shape != (length,) or not np.isfinite(result).all():
        raise ValueError(f"{name} must be a finite vector of length {length}")
    return result


def _covariance(values, length, *, positive_definite=False):
    matrix = np.asarray(values, dtype=float)
    if matrix.shape != (length, length) or not np.isfinite(matrix).all():
        raise ValueError("covariance must be finite and match the observations")
    scale = max(float(np.max(np.abs(matrix))), np.finfo(float).tiny)
    if not np.allclose(matrix, matrix.T, rtol=0, atol=1e-12 * scale):
        raise ValueError("covariance must be symmetric")
    matrix = (matrix + matrix.T) / 2
    if positive_definite:
        try:
            np.linalg.cholesky(matrix)
        except np.linalg.LinAlgError as exc:
            raise ValueError("estimation requires a positive-definite covariance") from exc
    elif np.linalg.eigvalsh(matrix)[0] < -1e-12 * scale:
        raise ValueError("covariance must be positive semidefinite")
    return matrix


def design_geometry(design, *, rcond=DEFAULT_RCOND):
    """Return SVD rank, row/null spaces and Moore--Penrose inverse of fixed D.

    Singular values above rcond*s_max define numerical rank.  The returned
    bases have orthonormal columns; left_null_basis.T contains contrast rows.
    A small positive singular value remains identifiable but poorly conditioned.
    """
    matrix = _matrix(design, "design")
    if not np.isscalar(rcond) or not np.isfinite(rcond) or not 0 < rcond < 1:
        raise ValueError("rcond must be a finite scalar strictly between zero and one")
    u, singular_values, vh = np.linalg.svd(matrix, full_matrices=True)
    tolerance = float(rcond * singular_values[0])
    rank = int(np.sum(singular_values > tolerance))
    row_vectors = vh[:rank]
    inverse = ((vh[:rank].T / singular_values[:rank]) @ u[:, :rank].T
               if rank else np.zeros((matrix.shape[1], matrix.shape[0])))
    return dict(rank=rank, full_column_rank=rank == matrix.shape[1],
                singular_values=singular_values, rank_tolerance=tolerance,
                rcond=float(rcond), pseudoinverse=inverse,
                condition_number=(float(singular_values[0] / singular_values[-1])
                                  if rank == matrix.shape[1] else None),
                row_projector=row_vectors.T @ row_vectors,
                null_basis=vh[rank:].T, left_null_basis=u[:, rank:])


def _whitened_estimator(design, covariance, rcond):
    matrix = _matrix(design, "design")
    covariance = (np.eye(len(matrix)) if covariance is None
                  else _covariance(covariance, len(matrix), positive_definite=True))
    lower = np.linalg.cholesky(covariance)
    whitening = np.linalg.solve(lower, np.eye(len(matrix)))
    geometry = design_geometry(whitening @ matrix, rcond=rcond)
    estimator = geometry["pseudoinverse"] @ whitening
    return estimator, covariance, geometry


def fit_composition(design, slopes, *, offsets=None, covariance=None, rcond=DEFAULT_RCOND):
    """GLS composition estimate and covariance for a full-column-rank design.

    Covariance describes errors in corrected slopes b.  Exact known offsets
    alter the mean only.  This method rejects rank deficiency instead of
    presenting a minimum-norm solution as identified physical components.
    """
    matrix = _matrix(design, "design")
    slopes = _vector(slopes, len(matrix), "slopes")
    offsets = np.zeros(len(matrix)) if offsets is None else _vector(offsets, len(matrix), "offsets")
    geometry = design_geometry(matrix, rcond=rcond)
    if not geometry["full_column_rank"]:
        raise ValueError("composition is not identified: design lacks full column rank")
    estimator, covariance, whitened_geometry = _whitened_estimator(matrix, covariance, rcond)
    if not whitened_geometry["full_column_rank"]:
        raise ValueError("composition rank cannot be resolved after covariance whitening")
    corrected = slopes - offsets
    theta = estimator @ corrected
    parameter_covariance = estimator @ covariance @ estimator.T
    return dict(theta=theta, covariance=(parameter_covariance + parameter_covariance.T) / 2,
                estimator=estimator, corrected_slopes=corrected,
                residual=corrected - matrix @ theta, geometry=geometry)


def target_weights(design, target, *, covariance=None, rcond=DEFAULT_RCOND):
    """Find w with w D=target when that linear target is identifiable.

    Unlike individual components, a target can be identifiable under deficient
    rank.  The returned linear estimator has minimum variance for the supplied
    positive-definite covariance and fixed design.
    """
    matrix = _matrix(design, "design")
    target = _vector(target, matrix.shape[1], "target")
    geometry = design_geometry(matrix, rcond=rcond)
    tolerance = 20 * rcond * max(float(np.linalg.norm(target)), np.finfo(float).tiny)
    if np.linalg.norm(target - target @ geometry["row_projector"]) > tolerance:
        raise ValueError("target is not identified: target lies outside the design row space")
    estimator, _, _ = _whitened_estimator(matrix, covariance, rcond)
    weights = target @ estimator
    if np.linalg.norm(weights @ matrix - target) > tolerance:
        raise ValueError("target identification could not be resolved numerically")
    return weights


def heldout_prediction(design, target, slopes, *, offsets=None, joint_covariance,
                       rcond=DEFAULT_RCOND):
    """Predict the last slope from calibration slopes, retaining cross-covariance.

    Inputs slopes/offsets have n_calibration+1 entries.  The joint covariance
    is for the corresponding corrected slopes.  The residual contrast uses
    weights (-w,1), so correlated calibration/held-out errors are included.
    """
    matrix = _matrix(design, "design")
    size = len(matrix) + 1
    slopes = _vector(slopes, size, "slopes")
    offsets = np.zeros(size) if offsets is None else _vector(offsets, size, "offsets")
    covariance = _covariance(joint_covariance, size, positive_definite=True)
    weights = target_weights(matrix, target, covariance=covariance[:-1, :-1], rcond=rcond)
    corrected = slopes - offsets
    contrast_weights = np.r_[-weights, 1.]
    prediction = float(weights @ corrected[:-1] + offsets[-1])
    variance = float(contrast_weights @ covariance @ contrast_weights)
    return dict(prediction=prediction, residual=float(slopes[-1] - prediction),
                variance=variance, standard_error=float(np.sqrt(variance)),
                prediction_variance=float(weights @ covariance[:-1, :-1] @ weights),
                weights=weights, contrast_weights=contrast_weights)


def contrast_moments(contrasts, corrected_slopes, covariance):
    """Propagate any fixed contrast rows L: estimate L b, covariance L Sigma L^T."""
    contrasts = _matrix(contrasts, "contrasts")
    corrected = _vector(corrected_slopes, contrasts.shape[1], "corrected_slopes")
    covariance = _covariance(covariance, len(corrected))
    return dict(value=contrasts @ corrected, covariance=contrasts @ covariance @ contrasts.T)


def corrected_slope_covariance(slope_covariance, offset_covariance=None,
                               slope_offset_covariance=None):
    """Cov(alpha-v)=Cov(alpha)+Cov(v)-Cov(alpha,v)-Cov(v,alpha).

    Exact known offsets add no uncertainty.  Uncertain offsets and their cross
    covariance require an admissible joint covariance, checked here.  This does
    not propagate measurement error in the constituent-exponent design D.
    """
    slope = _matrix(slope_covariance, "slope covariance")
    slope = _covariance(slope, len(slope))
    if offset_covariance is None:
        if slope_offset_covariance is not None:
            raise ValueError("offset covariance is required when cross-covariance is supplied")
        return slope.copy()
    offset = _covariance(offset_covariance, len(slope))
    cross = (np.zeros_like(slope) if slope_offset_covariance is None
             else np.asarray(slope_offset_covariance, dtype=float))
    if cross.shape != slope.shape or not np.isfinite(cross).all():
        raise ValueError("slope-offset cross-covariance must match the slope covariance")
    _covariance(np.block([[slope, cross], [cross.T, offset]]), 2 * len(slope))
    return _covariance(slope + offset - cross - cross.T, len(slope))


def fixed_design_error_bound(design, perturbation, *, rcond=DEFAULT_RCOND):
    """OLS bound ||delta theta||_2 <= ||delta b||_2 / sigma_min(D).

    The design is fixed and full column rank.  Perturbation means the total
    error in b=alpha-v, including an offset error if one has been quantified.
    This bound does not include uncertainty in D or model misspecification.
    """
    matrix = _matrix(design, "design")
    perturbation = _vector(perturbation, len(matrix), "perturbation")
    geometry = design_geometry(matrix, rcond=rcond)
    if not geometry["full_column_rank"]:
        raise ValueError("a composition error bound requires full column rank")
    return float(np.linalg.norm(perturbation) / geometry["singular_values"][-1])
