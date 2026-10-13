# Physics candidates for an independent prediction

12 October 2026. The author's requested search order is **physics, chemistry,
natural phenomena more broadly, biology, then human phenomena including
language and culture**. Selection requires independently fixed inputs to
predict another observable. Re-expressing an observation through a cost
estimated from that same observation does not qualify. The reference measure
in these thermal examples is counting measure on specified mechanical or
electrical modes; an instrument's frequency bins are not automatically modes.

| Candidate | Available material and decision |
|---|---|
| **Heated cantilevers, Fontana and Bellon (2023)** | [Article](https://arxiv.org/html/2208.08356); [Zenodo 7640708](https://zenodo.org/records/7640708). Small processed dataset (`data.mat`, 67,435 bytes), plotting code and functions. **Selected for a conditional departure prediction:** use measured dissipation versus temperature and the specified spatial loss model to predict fluctuation amplitude, without fitting to that amplitude. |
| Heated cantilever (2021) | [Article](https://arxiv.org/html/2101.09003); [Zenodo 4696490](https://zenodo.org/records/4696490). `Data.mat` is 267,794,797 bytes. Global damping alone does not identify the spatial dissipation weights needed to predict fluctuations; section II.3 makes this limitation material. Lower priority than the 2023 experiment. |
| Optical-tweezer calibration archive | [Zenodo 3333905](https://zenodo.org/records/3333905). Forced calibration offers a route separate from equilibrium variance. Live inventory has 134 bead archives, versus 153 in the narrative, and approximately 45.55 GB in total. Room temperature lacks a numerical value, drag is fixed in code, and a height comment has ambiguous units. Background variance and acquisition transfer information are not established. **Not qualified for an absolute equipartition test.** |
| Johnson-noise temperature interventions | [McKinney's JohnsonNoiseLab](https://github.com/hmckin/JohnsonNoiseLab). Separate driven transfer sweeps, two shorted-input baselines, measured resistances and thermometer readings, plus thermal spectra at two fixed nominal resistances. Accessible and small, but spectral units and calibration traceability remain insufficient for an absolute prediction. Retain as a follow-up candidate. |

The selected study is **not a fresh absolute test of equipartition**. Its
published fluctuation temperature uses an equilibrium baseline normalized
through equipartition. Temperature comes from resonance shifts; damping and
fluctuation amplitude come from the same spectra, so their errors need not
be independent. The proposed comparison tests whether independently specified
loss weighting predicts departures under heating, conditional on these
measurement and model assumptions. It cannot identify a spatial loss profile
from global damping without the declared constitutive restrictions.

For the electrical candidate, commit
`9fcb432ff801e73bfb3037bddb7edb967e9296c8` was inspected. The source fits

\[
A(f)=\frac{A_0(f/f_1)}{\sqrt{1+(f/f_1)^2}\sqrt{1+(f/f_2)^2}},\qquad
H(f,R)=\frac{A(f)}{\sqrt{1+(2\pi fRC_0)^2}}.
\]

The capacitance is fitted from **driven transfer measurements**, not thermal
noise. File headers only say `Freq`, `Mag` or `Chan2`; inspected frequency
columns span 0–39,062.5, interpreted as Hz by the source code. No window,
averaging or spectral-unit metadata appeared. Thermometer correction is
documented only in code; resistance is repeated within each temperature group,
not independently measured at each temperature. A within-resistor difference
would cancel a stable additive noise floor, but not unknown gain or drift.

**Exposure and provenance.** This is a candidate audit, not a preregistration.
The team read published findings and methods before selecting the cantilever
study, including reported discrepancies for C30 flexural mode 3 and C30C
torsional mode 1. Dataset inventories and calibration code were inspected.
For the resistor source, only predictor values, headers and frequency columns
were inspected; no numerical thermal-noise response or result figure was
opened. Download receipts and private inspection copies are under
`build/physics-noise-candidate/`; the unlicensed source code is not added to
the tracked archive. Any subsequent study must record its own freeze and
response-exposure chronology. Agreement would support the specified physical
realization and prediction, not distinguish it from established thermal
physics or establish universality across domains.
