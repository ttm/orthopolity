# Public optical-mode data: allocation qualification

28 October 2026. **Four public workbooks are accessible, but they do not yet
supply the independent experimental inputs required for a new allocation
forecast.** This bounded follow-up examines two closely related optical
papers under the [allocation specification](allocation-prediction-specification-2026-10-28.md).
It adds no empirical registry run. The reference measure is optical-mode
counting, with degeneracy weights for groups: **neither log-orthopolic nor
linear-orthopolic size allocation**.

## 1. Measured power allocation among fibre modes

[Pourbeyram et al. (2022)](https://doi.org/10.1038/s41567-022-01579-y),
*Direct observations of thermalization to a Rayleigh–Jeans distribution in
multimode optical fibres*, is the strongest physics lead in this search.
The [author preprint](https://arxiv.org/abs/2012.12110v2) is public. The publisher
supplies a methods supplement and four source-data workbooks; its data
statement assigns other data to author request. The linked
[simulation solver](https://github.com/WiseLabAEP/GMMNLSE-Solver-FINAL) does not
by itself supply measured initial fields.

The four downloaded workbooks have the following verified contents. Dimensions
are stored sheet ranges, not counts of independent experimental observations.

| Source file | Sheets and ranges | What it supplies |
| --- | --- | --- |
| `MOESM2` | Experimental B1:D16; RJ theory A1:B1002 | Fig. 2b final experimental allocation, error column and theoretical curve |
| `MOESM3` | Experiment A1:B29; Theory A1:B1001 | Fig. 3e final allocation and theoretical curve |
| `MOESM4` | Three summary sheets, A1:I21 or A1:G21 | Fig. 4 modal/fit summary trends |
| `MOESM5` | 5(a) A1:K42; 5 (b) A1:F17; 5 (b) RJ A1:B1001 | Fig. 5 simulated evolution, final simulation/experiment comparison and theory |

The [Fig. 2 caption](https://www.nature.com/articles/s41567-022-01579-y/figures/2)
identifies the lowest-power output in panel a as the initial modal distribution;
the deposited experimental sheet covers panel b. The
[Fig. 3 caption](https://www.nature.com/articles/s41567-022-01579-y/figures/3)
describes averaging over 14 input speckles. Individual initial fields and
paired replicate output arrays are not supplied in these inspected workbooks.
Published fitted and theoretical temperatures/chemical potentials are already
exposed; copying them is not a newly independent prediction.

The [methods supplement](https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41567-022-01579-y/MediaObjects/41567_2022_1579_MOESM1_ESM.pdf)
explains further qualifications. Its section 6 distinguishes the full 15-group
fibre from eight effectively thermalizing groups; both polarizations give 72
active modes. Its section 9 derives the equilibrium from initial total power
and a propagation-weighted invariant. Sections 5 and 20 describe image-calibration
uncertainty and the weak-nonlinearity approximation. These are useful methods,
but the inspected deposition lacks the independent input measurements and
their covariance needed to reproduce a full experimental forecast.

**Decision:** accessible final allocations, incomplete input qualification.
The missing object is a measured initial profile or equivalent independently
measured invariants, together with a justified active-mode boundary and its
budget. A simulation's initial row is not automatically the experimental input.
Digitizing a published plot would need a separate extraction/error protocol
and would not repair undocumented covariance or an uncertain subsystem budget.
This audit does not dispute the published experiment or claim no additional
public inputs exist elsewhere.

## What this candidate teaches the prediction design

Write the conventional Rayleigh–Jeans model, using an explicit sign convention,
as $n_i=-T/(\beta_i+\mu)$, with
$P=\sum_i n_i$ and $H=\sum_i\beta_i n_i$. Then
$H+\mu P=-MT$. The source's section 9 supplies this model; the following is
our allocation interpretation, not a new optical law.

On the positive-temperature branch, define $q_i=-(\beta_i+\mu)>0$.
The equality $q_i n_i=T$ is a finite-class realization of constrained equal
allocation. For a degenerate group, the predicted total is proportional to
$g_i/q_i$. Crucially, this is a **state-dependent shifted propagation weight**,
not simply photon energy or the unshifted $\beta_i$. Both the reference and
the sign/gauge convention must be stated. For fixed $\mu$,
$\sum_iq_i n_i=-H-\mu P$ combines the assumed invariants; its physical
conservation inherits the approximation used for linear $H$. This does not
independently establish photon-energy equipartition. Other temperature branches
require their own explicit positive-weight formulation.

Independently measured initial $P,H$, mode constants and an active mode set
could determine $T,\mu$ before final occupations. Reconstructing the input
invariants from final occupations, fitting $\mu$ from them, or selecting the
thermalizing cutoff afterwards would defeat that test. Error propagation must include uncertainty
in these inputs and their shared calibration. This would establish a scoped
allocation transfer compatible with optical statistical mechanics; agreement
alone would not distinguish the general law from that established theory.

## 2. The related universality paper supplies simulations

[Zhong et al. (2023)](https://doi.org/10.1038/s41467-023-35891-9),
*Universality of light thermalization in multimoded nonlinear optical systems*,
has [public full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC9871037/).
Its new results are simulations averaging 400 random-phase realizations with
common input intensities. Experimental references include the 2022 study
above. Data are available by request; the directly linked supplement is a
methods PDF, with no deposited numerical archive identified here.

**Decision:** theoretical context, not a new experimental input/output cohort.
Full-text methods, captions and reported results were read; no arrays were
downloaded or figures digitized. The follow-up stayed within this paper and
its direct links. No authors were contacted.

## Reproduction, exposure and search boundary

The repository retains a [source receipt](../data/physics-candidates/2026-10-28/allocation/source-receipt.json)
with exact URLs, byte counts and SHA-256 hashes, and a derived
[workbook inventory](../data/physics-candidates/2026-10-28/allocation/optical-schema.json).
Original PDFs/workbooks remain in ignored `build/`; their redistribution
license was not established in this audit. No source content is relicensed.

An independent schema check caught a provisional mapping error: sheet names
had been paired with XML members by their order. Resolving workbook relationship
IDs correctly maps the Fig. 4 and Fig. 5 sheets and removes the apparent panel
mismatch. This was corrected before any numerical analysis or committed record.
The verifier reproduces all four hashes and ten sheet schemas:

```sh
build/main-venv-2026-10-09/bin/python experiments/audit_optical_allocation_schema.py \
  --source-dir build/physics-allocation-audit-2026-10-27
```

For a fresh checkout, download the four `.xlsx` URLs in the receipt to a local
directory and pass it as `--source-dir`. The script parses XML, counts stored
rows and reads header strings; numerical cell payloads are never converted to
numbers or reported. Possession of archives is not global blinding. Captions,
methods, published aggregate outcomes and fitted parameters were exposed.

This report records the completed optical qualification, not an exhaustive
physics search. The parallel [chemistry audit](chemistry-allocation-source-audit-2026-10-27.md)
also finds no ready cohort. Stop this search round here. The next admissible
step is a specifically identified public deposition of separate initial and
final allocations with qualified resource inputs; neither another fit to
these final curves nor another transport response fills the missing test.
