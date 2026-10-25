# Predicting allocation after changing storage

25 October 2026. **Changing a store's capacity and changing its coupling have
different endpoint predictions.** The distinction provides a more direct
allocation test than another driven response curve. It also exposes a precise
boundary: equalizing an intensive variable need not equalize resource per a
fixed capacity measure when storage is nonlinear.

This is a constructed analytic design, not an experimental result or a claim
of new network thermodynamics. The graph/constitutive-law formulation has
established foundations, including [van der Schaft and Maschke (2013)](https://doi.org/10.1137/110840091).
The contribution here is an explicit contrast for the project's next experiment,
including a case that agrees at baseline and in small-signal measurements but
predicts a different allocation after intervention. It follows the
[hidden-link qualification](topology-storage-2026-10-23.md) and
[circuit boundary result](rlc-boundary-results-2026-10-25.md).

## Resource, potential and reference measure

Let store i have resource R_i = F_i(x_i), where x_i is a common kind of
intensive variable and each independently measured F_i is continuously
differentiable and strictly increasing, with positive derivative on the
operating interval. A concrete realization is communicating vessels:
R_i is liquid volume, x_i is height above a common bottom, and F'_i is
horizontal cross-sectional area. The fluid has the same density in every
vessel, all free surfaces have the same external pressure, and the links
contain independently accounted volume. Gravity establishes the pressure
differences; liquid volume is the conserved resource. Gravitational energy
decreases through dissipation and is not that conserved resource.

Choose positive fixed reference weights w_i before observing the release.
For the example below these are the independently specified volumes at unit
height, F_i(1), including the known change of the first vessel. This is
**neither log-orthopolic nor linear-orthopolic size allocation**. Those size
measures must not be substituted for physical vessel/storage weights.

For a connected symmetric network with positive conductances on its edges,

$$\dot R_i=\sum_j g_{ij}(x_j-x_i),\qquad \sum_iR_i=B.$$

For vessels this assumes a linear hydraulic resistance regime. A passive
nonlinear link whose current vanishes only at equal heights has the same
endpoint condition; its transient law requires separate specification.

The potential range remains between its initial extremes. On that compact
range, positive continuous F'_i bounds the dynamics. The function

$$E(R)=\sum_i\int_0^{R_i} F_i^{-1}(u)\,du$$

has derivative

$$\dot E=-\sum_{\{i,j\}}g_{ij}(x_i-x_j)^2\le0.$$

For a storage domain with a different lower endpoint, replace zero in each
integral by any fixed allowed reference. In the hydraulic example E is
gravitational energy divided by density times gravitational acceleration.
Connectedness and strict monotonicity give the unique equilibrium

$$x_i=H,\qquad \sum_iF_i(H)=B,\qquad R_i^*=F_i(H). \tag{1}$$

Thus conservative passive exchange equalizes potential. It gives the neutral
allocation R_i^*/w_i = constant **for every budget in an operating interval
if and only if** F_i(H)/w_i is the same function f(H) for every store on
that interval. Equivalently, F_i(H)=w_i f(H). Necessity follows by selecting
B=Σ_iF_i(H) for each H; sufficiency follows by substitution into (1).
Agreement at a single budget does not establish proportional storage curves.
Proportional differential capacities alone also need compatible integration
constants; common zero-resource reference states provide them.

This condition includes nonlinear storage shared proportionally by every
store. Nonlinearity by itself is not a failure. Different independently
measured storage curves can instead predict departures from a fixed reference
allocation. Choosing new weights from the observed endpoint would erase the
test and is not allowed.

## Two interventions that separate storage from kinetics

Keep B and the storage functions fixed and change only conductances, preserving
connectedness. Equation (1) predicts the **same full endpoint vector**. If
every conductance is multiplied by γ, the complete trajectory from the same
initial stocks is R_γ(t)=R_1(γt). A different connected topology generally
changes the trajectory but still leaves the endpoint unchanged. Disconnecting
the graph creates separate budgets and is outside this comparison.

Instead change one storage function F_j(x;θ), while keeping the total
resource fixed. Write C_i=F'_i(H)>0 and s=∂_θF_j(H;θ), where the latter
derivative holds H fixed. Implicit differentiation of (1) gives

$$\frac{dH}{dθ}=-\frac{s}{\sum_kC_k},\qquad
\frac{dR_i^*}{dθ}=-\frac{C_i s}{\sum_kC_k}\quad(i\ne j),$$

$$\frac{dR_j^*}{dθ}=s\left(1-\frac{C_j}{\sum_kC_k}\right). \tag{2}$$

For increasing storage at fixed potential (s>0), every untouched store loses
resource. Its infinitesimal loss relative to another untouched store is C_i/C_k,
independent of the coupling rates. For a finite intervention, the losses are
integrals of their capacities over the common potential change, not generally
the initial differential-capacity ratio. This distinguishes an equilibrium
storage effect from a slower approach to the same equilibrium.

## Identical baseline and local kinetics, different finite forecasts

Use dimensionless resource and height; physical units R_0 and H_0 can be
restored. In system A all three storage curves are F_i(h)=h. In system B,

$$F_1(h)=F_2(h)=h,\qquad F_3(h)=h+2h(h-1)^2.$$

This is a physically admissible vessel profile on h≥0 because

$$F'_3(h)=3-8h+6h^2=6(h-2/3)^2+1/3>0.$$

At h=1 both systems have stocks (1,1,1) and differential capacities (1,1,1).
With identical couplings they therefore have identical equilibrium allocations
and identical **linearized**, small-signal dynamics about that baseline.
Their complete finite pair trajectories need not agree. Separate storage
assays away from h=1 distinguish them before the target experiment.

Now double the first storage curve to F_1(h)=2h, leaving the other two
unchanged, and prepare the same total B=3. One possible preparation is to
isolate the vessels, retain stock 1 in each while changing the first vessel,
then release the links. This preserves resource, not gravitational energy;
any setup work is outside the closed release stage. Both systems now have
the same fixed reference weights w=(2,1,1).

| Prediction | System A: linear | System B: measured nonlinear store |
| --- | ---: | ---: |
| Final common height | 0.750000 | 0.722120 |
| R_1^* | 1.500000 | 1.444240 |
| R_2^* | 0.750000 | 0.722120 |
| R_3^* | 0.750000 | 0.833640 |
| Loss from store 3 / loss from store 2 | 1.000000 | 0.598675 |

For B the root is 2h³−4h²+6h−3=0. Both systems conserve the whole budget
and equalize height. Only A retains equal resource per the stated fixed
weights after this intervention. B's independently specified storage curve
predicts both the departure and which unchanged vessel loses less resource.
A baseline equality and a successful local kinetic calibration would miss it.

The largest endpoint separation is 0.083640 R_0 in store 3. As an illustrative
design calculation, two forecasts with symmetric total error bounds smaller
than 0.041820 R_0 each would have disjoint intervals for that stock. This is
not a measured error, a power calculation or an empirical pass rule. Actual
geometry, budget, observation and leakage uncertainties must be propagated
before declaring that any real experiment can discriminate the forecasts.

## Qualification and release sequence for actual data

1. Measure each complete storage curve over the intended operating range
   independently of the release trajectories, including uncertainty and the
   physical reference datum. Fix the comparison weights and any object costs
   before target access. A manufacturer's nominal single capacity or a local
   baseline fit is insufficient for the nonlinear forecast.
2. Account for connector storage, dead volume, evaporation/leakage and sampling.
   A vessel change must not silently add or remove resource. A coupling change
   must not also alter stored volume, pressure datum or connectivity. Use the
   earlier common-mode control where link storage is not independently bounded.
3. Fix baseline, capacity-intervention and coupling-intervention cohorts, endpoint
   stopping rules and transient observations. Predeclare how failures of closure
   or observation calibration stop interpretation. Neither fractional shares
   alone nor one fitted decay rate establishes the complete stock balance.
4. Propagate the independent input uncertainties through the monotone scalar
   root in (1); seal predictions of the **entire stock vector** and the
   competing fixed-weight forecast before release. Require a useful separation
   after uncertainty. Estimate coupling only from separate calibration if a
   kinetic forecast is included; endpoint forecasts do not need a kinetic fit.
5. Measure endpoint stocks and potentials with a qualified observation model;
   independently recovered/weighed stocks are especially useful. If stocks are
   obtained from the same geometry curves as the predictor, propagate shared
   errors and do not call the derived stock relation independent confirmation.
   Do not refit storage functions or reference weights using target endpoints.

The [new source qualification](storage-source-audit-2026-10-25.md) retains two
accessible archives, but neither supplies this closed capacity-versus-coupling
cohort. The test remains unrun. Passing it would establish a specified
allocation mechanism and its constitutive boundary, shared with ordinary
hydrostatics/network theory; it would not uniquely identify orthopolity over
those theories.

## Verification

`experiments/check_storage_intervention.py` checks eight fixed cases using
resource-coordinate edge-flux integration and independently assembled
potential-coordinate integration (DOP853 and Radau). Maximum trajectory
disagreement is **1.21e−10**, budget drift **3.85e−12**, and endpoint error
**1.60e−12**. The polynomial and monotone-budget roots agree within **2.23e−16**.
Checks also verify energy dissipation, exact coupling-time rescaling and the
susceptibility formula against finite differences. They are included in
`make topology-design` and `make all`. These constructed calculations do not
add an empirical registry entry or a confirmatory simulation study.
