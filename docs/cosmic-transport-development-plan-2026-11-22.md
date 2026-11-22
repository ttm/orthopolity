# Fixed-bin TNG transport development plan

22 November 2026. The completed acquisition/inventory milestone is committed
and pushed as `3b198e7`. This plan executes the next D3 tasks using only those
retained files. The resource remains **log-orthopolic collisionless total-matter
mass**. The whole TNG50-4-Dark run is development-only; no target, plateau or
scientific acceptance threshold is assigned.

The [executable manifest](../configs/cosmic-transport-development-2026-11-22.json)
fixes the input hashes, estimands and grids before these new summaries are
computed (SHA-256
`25e2d33a25f1065b20b3a5b2ff624d7bfed3112ec4b68015379030b8584bfdc2`).
The global inventory, jump and cadence findings were already exposed
on 21 November. Fixing this analysis now does not make it an independent test.

## Domain and bins

Use exact host particle count N and x = ln(M/m_p) = ln(N), with the verified
single-particle mass m_p as reference. The common domain is
1 ≤ N < 2^26. The exponent 26 is the smallest positive even integer whose
power of two exceeds the known whole-box particle inventory, 19,683,000.
It therefore covers every possible positive host without selecting an interval
from its measured profile.

The primary grid has unit steps in log2(N), or width ln(2) in x: 26 bins.
Prespecified half-width and double-width grids have 52 and 13 bins over the
same domain. Bins are left-inclusive and right-exclusive. Classify hosts in
particle-count space so exact powers of two have unambiguous membership.
Retain empty bins. Stop on a positive host outside the declared domain.

Diffuse material is a separate state with no x coordinate. All positive hosts
are inside the domain, so no resolved-host outside reservoir is needed here.
Report exact host counts separately from particle stocks. Host numbers are not
estimated by dividing a stock by a representative mass.

## Exact endpoint accounting

For each output and grid, retain the particle stock in every host bin and the
diffuse state. For each of 97→98, 98→99 and 97→99, join persistent particle IDs
and count the full origin/destination matrix T. Verify its row and column sums
against the endpoint stocks using integers.

Among particles hosted at both endpoints (HH), count upward and downward
crossings of every mass edge, then subtract to obtain the signed current.
Let f_i be its integrated particle count at edge i. Let s_i be diffuse-to-bin
particles minus bin-to-diffuse particles. Require exactly

    n_i(end) − n_i(start) = f_i − f_(i+1) + s_i.

Multiply by m_p/V for stocks and transfers, and by m_p/(V Δt) for currents
and source rates. Reuse the verified comoving volume and declared flat
matter-plus-Lambda time convention. This identity checks the observation map;
it cannot establish local physical transport.

## Compare like quantities in the drift diagnostic

For a bin [a,b), width w, the exact cell average of the signed endpoint current
is

    Jbar = m_p/(V Δt w) × Σ_HH [clip(x_end−a,0,w) − clip(x_start−a,0,w)].

Use actual endpoint coordinates. Sampling currents only at bin edges misses
within-bin motion. Endpoint count/log-moment histograms evaluate this integral
without repeatedly scanning every particle for every edge.

The departure-localized approximation deposits each HH displacement Δx in
its starting bin:

    Jdeparture = m_p/(V Δt w) × Σ_(HH starting in bin) Δx.

Also retain its conditional drift v = mean(Δx)/Δt and matching starting
HH density r_HH = m_p N_HH/(V w), so their product is Jdeparture. Report the
full starting stock and HH retained fraction beside it. Particles leaving for
diffuse material have no defined endpoint Δx; their omitted contribution
prevents this conditional product from directly testing full-population J=vr.

A midpoint-localized moment deposits each displacement in the bin containing
its mean endpoint coordinate. It is a spatial-assignment sensitivity check,
not an inferred physical trajectory. Compare both deposits with Jbar, retaining
the per-bin residuals and width-weighted symmetric L1 discrepancies. Undefined
ratios are null. For currents A and B the discrepancy is
sum(w × |A−B|) / sum(w × (|A|+|B|)), in [0,1], with no factor of two;
it is undefined when the denominator is zero. Over the full domain, the integrated signed displacement
must agree for all three deposits to floating precision.

Call these **finite-time localization residuals**. They combine cadence,
binning, endpoint conditioning and spatial assignment; they are not bounds on
the physical continuum residual or a forecast uncertainty model.

## Sources, long displacements and cadence

Retain endpoint stock-rate changes and change divided by mean endpoint stock,
without declaring a stationarity threshold. Keep diffuse entry and exit
separate as well as their net contribution.

For every grid, report the contribution to boundary crossings from transitions
whose endpoint bin indices differ by at least two: a **skip-bin contribution**.
Use each edge's gross crossings as denominator, with null for a zero denominator.
Also report the displacement-based tail |Δx| ≥ ln(2). A grid-dependent skip is
not by itself evidence of physical nonlocality or a qualified local limit.

Combine rates only after multiplication by their unequal interval durations.
For adjacent-minus-coarse integrated currents D_f and sources D_s, require

    D_f(i) − D_f(i+1) + D_s(i) = 0.

Full-population HH gross differences may be negative: a host→diffuse→host path
can cross a mass edge between the outer endpoints while contributing to neither
adjacent HH pair. Do not label that signed difference a nonnegative loss.
Separately compute boundary currents on the common subset hosted at all three
outputs; its net counts telescope and its adjacent gross crossing count cannot
be smaller than the coarse count. This demonstrates coarsening effects, not
convergence at the finest available cadence.

## Execution and decision

Use the existing Python 3.11 environment and isolated HDF5 dependency. Keep the
3 GiB reader-memory and 1 GiB scratch ceilings. Verify frozen input and helper
hashes, raw file hashes, the ID sets, exact balances and manufactured long-jump,
within-bin, reversal, diffuse-excursion and unequal-duration fixtures before
interpreting real summaries. Retain the source/config snapshots and all grids
and pairs; no external acquisition is part of this step.

After execution, report what the residuals establish and what remains
unidentified. D4 is conditional on a defensible material-to-transport mapping;
D5 still requires separate calibrated inputs, rivals and a target fixed before
exposure. This development analysis does not by itself meet either requirement.
