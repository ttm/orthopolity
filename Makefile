# Reproduce everything from the frozen snapshots.
#
#   make install   editable install, so `import orthopolity` works without PYTHONPATH
#   make all       verify data, run tests, run every analysis
#   make paper     typeset the main article and supporting material (needs pdflatex)
#
# Historical downloaded inputs live in checksummed data/raw/. Later studies
# retain their own measured/generated inputs and acquisition receipts. Analysis
# targets are offline; network acquisition is a separate explicit driver stage.

PY ?= python3
export PYTHONPATH := src
STUDY_OUTPUT_ROOT ?= build/reproductions

.PHONY: all install data restore-data test pilot gof independent ensemble strata variance theory resource gibrat catalogue aftershocks analyses paper clean
.PHONY: all install data restore-data test pilot gof independent ensemble strata variance theory models dependence attachment restrictions followup competition forecast interventions robustness workload-pilot workload-report workload-transfer workload-transfer-report scheduler-allocation run-registry registry-verify solar-resource-transfer aquatic-study-transfer resource-identification profile-tests profile-test-registry analyses paper clean
.PHONY: profile-calibration solar-validation dimensionality-intervention validation-round validation-round-registry
.PHONY: chemostat-sources restore-chemostat-bundle archived-cost-transfer available-data-registry chemostat-response chemostat-response-report
.PHONY: dunaliella-sources dunaliella-size-budget dunaliella-size-budget-report
.PHONY: plant-sources plant-biomass-profile plant-biomass-profile-report
.PHONY: law-observation-metadata
.PHONY: measure-intervention measure-candidates measure-calibration
.PHONY: ghedini-cost-calibration ghedini-cost-calibration-report
.PHONY: class-exchange class-exchange-report class-exchange-registry
.PHONY: thermal-sources thermal-radiation thermal-radiation-registry
.PHONY: inverse-resources inverse-resources-registry linguistic-sources linguistic-resources linguistic-resources-registry
.PHONY: cell-division-sources cell-division cell-division-registry
.PHONY: hydrolakes-sources restore-hydrolakes lake-gyration uk-lake-gyration
.PHONY: geometry-registry
.PHONY: hydrobasins-sources restore-hydrobasins lake-metric-followup metric-followup-registry
.PHONY: seismic-sources restore-seismic-sources seismic-qualification seismic-qualification-registry
.PHONY: seismic-candidate-sources restore-seismic-candidates seismic-candidate-audit
.PHONY: italian-magnitude-validation italian-magnitude-registry
.PHONY: chemostat-capacity chemostat-capacity-registry
.PHONY: paired-phosphorus paired-phosphorus-sources paired-phosphorus-registry
.PHONY: field-resources field-resources-sources field-resources-registry
.PHONY: cantilever-sources cantilever-transfer cantilever-registry
.PHONY: adsorption-sources adsorption-transfer adsorption-registry

PAPER_SRC := docs/paper.md
PAPER_TEX := build/paper.tex
PAPER_PDF := docs/paper.pdf
SUPPORT_SRC := docs/supporting-material.md
SUPPORT_TEX := build/supporting-material.tex
SUPPORT_PDF := docs/supporting-material.pdf

# The PDF is tracked, so its bytes must not change unless the manuscript does:
# date it from the manuscript's last commit rather than from the clock.
PAPER_EPOCH := $(shell git log -1 --format=%ct -- docs/paper.md 2>/dev/null)
ifeq ($(PAPER_EPOCH),)
PAPER_EPOCH := 0
endif
PAPER_ENV := SOURCE_DATE_EPOCH=$(PAPER_EPOCH) FORCE_SOURCE_DATE=1
SUPPORT_EPOCH := $(shell git log -1 --format=%ct -- $(SUPPORT_SRC) 2>/dev/null)
ifeq ($(SUPPORT_EPOCH),)
SUPPORT_EPOCH := 0
endif
SUPPORT_ENV := SOURCE_DATE_EPOCH=$(SUPPORT_EPOCH) FORCE_SOURCE_DATE=1

PAPER_IMAGES := results/class-exchange-presentation/class-exchange.png
SUPPORT_IMAGES := results/inverse-resources/inverse-resources.png \
 results/theory.png results/class-exchange-presentation/class-exchange.png \
 results/thermal-radiation/thermal-radiation.png \
 results/dunaliella-size-budget/size-budget.png \
 results/plant-biomass-profile/mass-profile.png \
 results/linguistic-resources/linguistic-resources.png \
 results/cell-division/cell-division.png \
 results/lake-metric-followup-2026-10-09/interval-comparison.png \
 results/lake-metric-followup-2026-10-09/survival.png \
 results/italian-magnitude-validation-2026-10-10/validation.png \
 results/chemostat-capacity-followup-2026-10-10/capacity.png \
 results/cantilever-transfer-2026-10-13/cantilever-presentation.png \
 results/adsorption-transfer-2026-10-13/adsorption.png

all: data test analyses

adsorption-sources: ## verify the pinned pure/binary chemical adsorption archive
	$(PY) experiments/fetch_adsorption.py --stage verify

adsorption-transfer: adsorption-sources ## replay sealed pure-to-mixture forecasts in fresh directories
	$(PY) experiments/run_adsorption.py --stage predict --freeze-commit 08efaa1 --output $(STUDY_OUTPUT_ROOT)/adsorption-forecast
	cmp results/adsorption-forecast-2026-10-13/predictions.json $(STUDY_OUTPUT_ROOT)/adsorption-forecast/predictions.json
	$(PY) experiments/run_adsorption.py --stage evaluate --freeze-commit 08efaa1 --prediction-commit 158a22c --predictions results/adsorption-forecast-2026-10-13/predictions.json --output $(STUDY_OUTPUT_ROOT)/adsorption-transfer
	cmp results/adsorption-transfer-2026-10-13/result.json $(STUDY_OUTPUT_ROOT)/adsorption-transfer/result.json
	$(PY) experiments/verify_adsorption.py --result $(STUDY_OUTPUT_ROOT)/adsorption-transfer/result.json --predictions results/adsorption-forecast-2026-10-13/predictions.json --output $(STUDY_OUTPUT_ROOT)/adsorption-transfer/verification.json
	cmp results/adsorption-transfer-2026-10-13/verification.json $(STUDY_OUTPUT_ROOT)/adsorption-transfer/verification.json
	$(PY) experiments/audit_adsorption_coverage.py --predictions results/adsorption-forecast-2026-10-13/predictions.json --output $(STUDY_OUTPUT_ROOT)/adsorption-transfer/coverage-audit.json
	cmp results/adsorption-transfer-2026-10-13/coverage-audit.json $(STUDY_OUTPUT_ROOT)/adsorption-transfer/coverage-audit.json
	MPLCONFIGDIR=build/matplotlib $(PY) experiments/plot_adsorption.py --result $(STUDY_OUTPUT_ROOT)/adsorption-transfer/result.json --output $(STUDY_OUTPUT_ROOT)/adsorption-transfer/adsorption.png
	cmp results/adsorption-transfer-2026-10-13/adsorption.png $(STUDY_OUTPUT_ROOT)/adsorption-transfer/adsorption.png

adsorption-registry: ## append the verified chemical competition transfer
	$(PY) experiments/register_adsorption.py

cantilever-sources: ## verify the pinned mechanical damping and thermal-noise archive
	$(PY) experiments/fetch_cantilever.py --stage verify

cantilever-transfer: cantilever-sources ## replay sealed cold-to-hot forecasts in fresh directories
	$(PY) experiments/run_cantilever.py --stage predict --freeze-commit 0428b64 --output $(STUDY_OUTPUT_ROOT)/cantilever-forecast
	cmp results/cantilever-forecast-2026-10-13/predictions.json $(STUDY_OUTPUT_ROOT)/cantilever-forecast/predictions.json
	$(PY) experiments/run_cantilever.py --stage evaluate --freeze-commit 0428b64 --prediction-commit 6733362 --predictions results/cantilever-forecast-2026-10-13/predictions.json --output $(STUDY_OUTPUT_ROOT)/cantilever-transfer
	$(PY) experiments/verify_cantilever.py --directory $(STUDY_OUTPUT_ROOT)/cantilever-transfer --write
	MPLCONFIGDIR=build/matplotlib $(PY) experiments/plot_cantilever.py --result $(STUDY_OUTPUT_ROOT)/cantilever-transfer/result.json --output $(STUDY_OUTPUT_ROOT)/cantilever-transfer/cantilever-presentation.png

cantilever-registry: ## append the retained comparison with all physical failures
	$(PY) experiments/register_cantilever.py

field-resources-sources: ## verify sorted quotas, ambient counts and bulk-stock sources
	$(PY) experiments/fetch_field_resources.py --stage verify

field-resources: field-resources-sources ## replay nominal matches and conditional stock bounds
	$(PY) experiments/run_field_resources.py --stage evaluate --freeze-commit 52d2cc2 --output $(STUDY_OUTPUT_ROOT)/field-resources
	$(PY) experiments/verify_field_resources.py --directory $(STUDY_OUTPUT_ROOT)/field-resources

field-resources-registry: ## register the retained audit with the post-run P unit qualification
	$(PY) experiments/register_field_resources.py

paired-phosphorus-sources: ## verify the two independently assayed phosphorus archives
	$(PY) experiments/fetch_paired_phosphorus.py --stage verify

paired-phosphorus: paired-phosphorus-sources ## replay the limited conditional count pilot
	$(PY) experiments/run_paired_phosphorus.py --output $(STUDY_OUTPUT_ROOT)/paired-phosphorus
	$(PY) experiments/verify_paired_phosphorus.py --directory $(STUDY_OUTPUT_ROOT)/paired-phosphorus

paired-phosphorus-registry: ## append the retained pilot, preserving prior runs
	$(PY) experiments/register_paired_phosphorus.py

install:
	$(PY) -m pip install -r requirements.txt -e ".[analyses,geospatial]"

data:            ## verify every raw input against data/snapshot_checksums.json
	$(PY) experiments/fetch_data.py

restore-data:    ## explicitly permit network restoration of missing snapshots
	$(PY) experiments/fetch_data.py --restore

test:            ## accounting, estimator, goodness-of-fit and meta-analysis checks
	MPLCONFIGDIR=build/matplotlib $(PY) -m unittest discover -s tests -v

analyses: pilot gof independent ensemble strata variance theory resource gibrat catalogue aftershocks

pilot:           ## the three original pilots -> results/results.json
	$(PY) experiments/run_pilot.py

gof: pilot       ## goodness of fit and flatness equivalence -> results/gof.json
	$(PY) experiments/run_gof.py

independent:     ## historically planned aquatic comparisons -> results/independent.json
	$(PY) experiments/run_independent.py

ensemble:        ## is the ensemble result real? -> results/ensemble.json
	$(PY) experiments/run_ensemble.py

strata:          ## class mixture and span/taxon confound -> results/strata.json
	$(PY) experiments/run_strata.py

variance:        ## between- vs within-ecosystem dispersion -> results/variance.json
	$(PY) experiments/run_variance.py

theory:          ## deterministic mathematical illustrations (not empirical evidence)
	$(PY) experiments/run_theory.py

resource:        ## post hoc: does the verdict depend on the resource? -> results/resource_choice.json
	$(PY) experiments/run_resource_choice.py

gibrat:          ## simulated check of the Gibrat deviation law (not empirical evidence) -> results/gibrat.json
	$(PY) experiments/run_gibrat.py

catalogue:       ## orthopolic rules against published exponents -> results/resource_catalogue.json
	$(PY) experiments/run_catalogue.py

aftershocks:     ## pre-registered productivity test (configs/prereg_2026-10-08_*) -> results/aftershock_productivity.json
	$(PY) experiments/run_aftershocks.py

hydrolakes-sources: ## offline verification of the separately retained global polygons
	$(PY) experiments/fetch_hydrolakes.py

restore-hydrolakes: ## explicitly download/extract missing HydroLAKES source bytes
	$(PY) experiments/fetch_hydrolakes.py --restore

lake-gyration: hydrolakes-sources ## original global calculation with recorded DBF decoding correction
	mkdir -p $(STUDY_OUTPUT_ROOT)/lake-gyration
	$(PY) experiments/run_lake_gyration.py --shapefile data/hydrolakes/2026-10-09/extracted/HydroLAKES_polys_v10_shp/HydroLAKES_polys_v10.shp --encoding latin1 --output $(STUDY_OUTPUT_ROOT)/lake-gyration/result.json

uk-lake-gyration: ## separate frozen regional replication; does not overwrite retained result
	$(PY) experiments/run_uk_lake_gyration.py --output $(STUDY_OUTPUT_ROOT)/uk-lake-gyration/result.json

geometry-registry: ## archive the retained flare and lake calculations
	$(PY) experiments/register_geometry_tests.py

hydrobasins-sources: ## verify local publisher basin archives without networking
	$(PY) experiments/fetch_hydrobasins.py

restore-hydrobasins: ## restore missing catchment archives from pinned publisher URLs
	$(PY) experiments/fetch_hydrobasins.py --restore

lake-metric-followup: hydrolakes-sources hydrobasins-sources ## frozen physical-geometry/catchment follow-up
	$(PY) experiments/run_lake_metric_followup.py --derive --output $(STUDY_OUTPUT_ROOT)/lake-metric-followup

metric-followup-registry: ## register retained follow-up without changing prior records
	$(PY) experiments/register_metric_followup.py

seismic-sources: ## verify all three pinned full catalogues offline
	$(PY) experiments/fetch_seismic_qualification.py

restore-seismic-sources: ## restore missing public earthquake catalogues by checksum
	$(PY) experiments/fetch_seismic_qualification.py --restore

seismic-qualification: seismic-sources ## replay frozen eligibility gates; never fit b or D2
	$(PY) experiments/qualify_volumetric_seismicity.py --output $(STUDY_OUTPUT_ROOT)/seismic-qualification
	$(PY) experiments/verify_seismic_qualification.py --directory $(STUDY_OUTPUT_ROOT)/seismic-qualification
	MPLCONFIGDIR=build/matplotlib $(PY) experiments/plot_seismic_qualification.py --directory $(STUDY_OUTPUT_ROOT)/seismic-qualification

seismic-qualification-registry: ## append the retained eligibility finding and verify history
	$(PY) experiments/register_seismic_qualification.py

seismic-candidate-sources: ## verify newer Italian/calibration and Northern California inputs
	$(PY) experiments/fetch_seismic_candidates.py

restore-seismic-candidates: ## retrieve missing exact source snapshots, refusing revised bytes
	$(PY) experiments/fetch_seismic_candidates.py --restore

seismic-candidate-audit: seismic-candidate-sources ## source compatibility only; no b or D2
	$(PY) experiments/audit_seismic_candidates.py --output $(STUDY_OUTPUT_ROOT)/seismic-candidates
	$(PY) experiments/verify_seismic_candidates.py --directory $(STUDY_OUTPUT_ROOT)/seismic-candidates

italian-magnitude-validation: ## synthetic prerequisite only; use an empty output directory
	OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 $(PY) experiments/validate_italian_magnitudes.py --output $(STUDY_OUTPUT_ROOT)/italian-magnitude-validation
	$(PY) experiments/verify_italian_magnitudes.py --directory $(STUDY_OUTPUT_ROOT)/italian-magnitude-validation
	MPLCONFIGDIR=build/matplotlib $(PY) experiments/plot_italian_magnitudes.py --directory $(STUDY_OUTPUT_ROOT)/italian-magnitude-validation

italian-magnitude-registry: ## append completed simulation without a real earthquake fit
	$(PY) experiments/register_italian_magnitudes.py

class-exchange:   ## conservative class exchange, constrained equilibrium, and recovery
	MPLCONFIGDIR=build/matplotlib $(PY) experiments/run_class_exchange.py --output $(STUDY_OUTPUT_ROOT)/class-exchange

class-exchange-registry: ## archive the retained demonstration and verify prior runs
	$(PY) experiments/register_class_exchange.py

class-exchange-report: ## manuscript figure from retained outputs, without resimulation
	MPLCONFIGDIR=build/matplotlib $(PY) experiments/report_class_exchange.py --output $(STUDY_OUTPUT_ROOT)/class-exchange-presentation

thermal-sources: ## offline: verify four retained FIRAS product and source documents
	$(PY) experiments/fetch_thermal_radiation.py

thermal-radiation: thermal-sources ## thermal mode calculation and retrospective FIRAS description
	MPLCONFIGDIR=build/matplotlib $(PY) experiments/run_thermal_radiation.py --output $(STUDY_OUTPUT_ROOT)/thermal-radiation

thermal-radiation-registry: ## archive the retained calculation without rerunning it
	$(PY) experiments/register_thermal_radiation.py

inverse-resources: ## conditional identification and synthetic cross-environment predictions
	MPLCONFIGDIR=build/matplotlib $(PY) experiments/run_inverse_resources.py --output $(STUDY_OUTPUT_ROOT)/inverse-resources

inverse-resources-registry: ## archive/audit the retained synthetic identification study
	$(PY) experiments/register_inverse_resources.py

cell-division-sources: ## offline: audit the published bacterial calibration/target figures
	$(PY) experiments/fetch_cell_division.py

cell-division: cell-division-sources ## replay the frozen published-summary transfer
	MPLCONFIGDIR=build/matplotlib $(PY) experiments/run_cell_division.py --stage evaluate --output-dir $(STUDY_OUTPUT_ROOT)/cell-division

cell-division-registry: ## archive/audit the retained bacterial summary comparison
	$(PY) experiments/register_cell_division.py

linguistic-sources: ## offline: verify pinned corpus and pronunciation source files
	$(PY) experiments/fetch_linguistic_resources.py

linguistic-resources: linguistic-sources ## replay frozen cross-genre forecasts offline
	MPLCONFIGDIR=build/matplotlib $(PY) experiments/run_linguistic_resources.py --stage evaluate --output-dir $(STUDY_OUTPUT_ROOT)/linguistic-resources

linguistic-resources-registry: ## archive/audit the retained corpus transfer comparison
	$(PY) experiments/register_linguistic_resources.py

models:          ## exploratory model comparisons (not empirical evidence)
	MPLCONFIGDIR=build/matplotlib $(PY) experiments/run_models.py --output $(STUDY_OUTPUT_ROOT)/models

dependence:      ## joint-resource dimensionality and independent forward predictions
	MPLCONFIGDIR=build/matplotlib $(PY) experiments/run_dependence.py --output $(STUDY_OUTPUT_ROOT)/dependence

attachment:      ## fixed-resource transfer across attachment dynamics
	MPLCONFIGDIR=build/matplotlib $(PY) experiments/run_attachment.py --output $(STUDY_OUTPUT_ROOT)/attachment

restrictions:    ## prospective profile responses under two resource budgets
	MPLCONFIGDIR=build/matplotlib $(PY) experiments/run_restrictions.py --output $(STUDY_OUTPUT_ROOT)/restrictions

followup: dependence attachment restrictions ## the three follow-up computational studies

competition:     ## negative coupling, finite support, and dimension corrections
	MPLCONFIGDIR=build/matplotlib $(PY) experiments/run_competition.py --output $(STUDY_OUTPUT_ROOT)/competition

forecast:        ## capacity-only selection, misspecification, and uncertainty
	MPLCONFIGDIR=build/matplotlib $(PY) experiments/run_forecast.py --output $(STUDY_OUTPUT_ROOT)/forecast

interventions:   ## sampling design and calibrated model discrimination
	MPLCONFIGDIR=build/matplotlib $(PY) experiments/run_interventions.py --output $(STUDY_OUTPUT_ROOT)/interventions

robustness: competition forecast interventions ## predictive reliability and observation design

workload-pilot:   ## execute or resume the controlled workload measurement stages
	MPLCONFIGDIR=build/matplotlib $(PY) experiments/run_workload_pilot.py --output $(STUDY_OUTPUT_ROOT)/workload-pilot

workload-report:  ## analyse the recorded workload observations without collecting new ones
	MPLCONFIGDIR=build/matplotlib $(PY) experiments/run_workload_pilot.py --stage analyse --output $(STUDY_OUTPUT_ROOT)/workload-pilot

workload-transfer: ## execute/resume the retained comparison; new collection needs new directories
	MPLCONFIGDIR=build/matplotlib $(PY) experiments/run_workload_transfer.py

workload-transfer-report: ## reuse recorded comparison outputs without launching workers
	MPLCONFIGDIR=build/matplotlib $(PY) experiments/run_workload_transfer.py --stage analyse

scheduler-allocation: ## inspect scarcity and simulate models; actual trials only on eligible hosts
	$(PY) experiments/run_scheduler_allocation.py

run-registry:     ## idempotently catalogue eight reference studies and audit every registered run
	$(PY) experiments/register_runs.py --catalogue
	$(PY) experiments/register_runs.py --verify

registry-verify:  ## check registry integrity, retained files, and lineage offline
	$(PY) experiments/register_runs.py --verify

solar-resource-transfer: ## retained measured-fluence forecasts and calendar-year holdout
	MPLCONFIGDIR=build/matplotlib $(PY) experiments/run_solar_resource_transfer.py

aquatic-study-transfer: ## exclude whole studies from fitting published-slope forecasts
	MPLCONFIGDIR=build/matplotlib $(PY) experiments/run_aquatic_study_transfer.py

resource-identification: ## exponent agreement versus complete profiles in growth/removal models
	MPLCONFIGDIR=build/matplotlib $(PY) experiments/run_resource_identification.py

profile-tests: solar-resource-transfer aquatic-study-transfer resource-identification

profile-test-registry: ## idempotently register the additional empirical/simulation tests
	MPLCONFIGDIR=build/matplotlib $(PY) experiments/run_aquatic_study_transfer.py --register
	$(PY) experiments/register_profile_tests.py

profile-calibration: ## audit/reuse the complete-profile repeated-sampling benchmark
	MPLCONFIGDIR=build/matplotlib $(PY) experiments/run_profile_calibration.py

solar-validation: ## evaluate/reuse the acquired 2025 snapshot without downloading
	MPLCONFIGDIR=build/matplotlib $(PY) experiments/run_solar_validation.py --stage analyse

dimensionality-intervention: ## audit measured CPU allocation without collecting new trials
	MPLCONFIGDIR=build/matplotlib $(PY) experiments/run_dimensionality_intervention.py --stage audit

validation-round: profile-calibration solar-validation dimensionality-intervention
	$(PY) experiments/audit_solar_validation.py

validation-round-registry: ## append/check the three completed studies idempotently
	$(PY) experiments/register_validation_round.py

chemostat-sources: ## offline: verify retained chemostat sources and replay the metadata audit
	$(PY) experiments/fetch_chemostat_sources.py --stage verify
	$(PY) experiments/fetch_chemostat_sources.py --stage audit

restore-chemostat-bundle: ## network: restore the untracked 98.7 MB author bundle by checksum
	$(PY) experiments/restore_chemostat_bundle.py
	$(PY) experiments/fetch_chemostat_sources.py --stage verify

archived-cost-transfer: ## offline audit of the frozen Synechococcus quota-transfer study
	MPLCONFIGDIR=build/matplotlib $(PY) experiments/run_archived_cost_transfer.py --stage audit

chemostat-response: ## offline audit: replay the frozen chemostat forecasts and held-out evaluation
	$(PY) experiments/run_chemostat_response.py --stage audit

chemostat-response-report: ## post-hoc diagnostics and figures from retained outputs; refuses changed bytes
	MPLCONFIGDIR=build/matplotlib $(PY) experiments/report_chemostat_response.py

dunaliella-sources: ## offline: verify the retained Dunaliella bundle and its header-only schema
	$(PY) experiments/fetch_dunaliella_sources.py --stage verify
	$(PY) experiments/fetch_dunaliella_sources.py --stage schema

dunaliella-size-budget: ## offline audit: replay the Dunaliella forecasts and held-out evaluation
	$(PY) experiments/run_dunaliella_size_budget.py --stage audit

dunaliella-size-budget-report: ## post-hoc diagnostics and figure from retained outputs; refuses changed bytes
	MPLCONFIGDIR=build/matplotlib $(PY) experiments/report_dunaliella_size_budget.py

available-data-registry: ## append/check completed available-data studies idempotently
	$(PY) experiments/register_available_data.py

plant-sources: ## offline: verify the ten pinned, directly weighed plant source files
	$(PY) experiments/fetch_plant_sources.py --stage verify

plant-biomass-profile: ## offline: replay the frozen plant forecasts, calibration and evaluation
	$(PY) experiments/run_plant_biomass_profile.py --stage audit

plant-biomass-profile-report: ## figure from retained outputs only; refuses changed bytes
	MPLCONFIGDIR=build/matplotlib $(PY) experiments/report_plant_biomass_profile.py

law-observation-metadata: ## offline: verify six retained methods/event metadata files
	$(PY) experiments/fetch_law_observation_metadata.py --stage verify

measure-intervention: ## analytic examples only: size-reference versus cost-reference allocation
	$(PY) experiments/illustrate_measure_intervention.py

measure-candidates: ## offline: verify candidate metadata, source checksums and text headers
	$(PY) experiments/fetch_measure_candidates.py --stage verify

measure-calibration: ## offline: qualify independent respiration data; no model fit or community score
	$(PY) experiments/inspect_measure_calibration.py

ghedini-cost-calibration: ## offline: exact replay of the frozen respiration calibration gate
	$(PY) experiments/run_ghedini_cost_calibration.py --stage audit

ghedini-cost-calibration-report: ## figures from retained calibration results; no refitting
	MPLCONFIGDIR=build/matplotlib $(PY) experiments/report_ghedini_cost_calibration.py --verify

chemostat-capacity: ## reproduce the retrospective diagnosis to an unused directory
	$(PY) experiments/run_chemostat_capacity.py --freeze-commit 13374c5 --output $(STUDY_OUTPUT_ROOT)/chemostat-capacity
	$(PY) experiments/verify_chemostat_capacity.py --directory $(STUDY_OUTPUT_ROOT)/chemostat-capacity
	MPLCONFIGDIR=build/matplotlib $(PY) experiments/plot_chemostat_capacity.py --directory $(STUDY_OUTPUT_ROOT)/chemostat-capacity

chemostat-capacity-registry: ## append/audit the retained conditional follow-up
	$(PY) experiments/register_chemostat_capacity.py

paper: $(PAPER_PDF) $(SUPPORT_PDF)  ## typeset both manuscripts; requires a TeX installation

# tools/md2tex.py handles the Markdown subset the manuscript uses, so no Pandoc
# is required. Two passes settle the PDF outline and any page references.
$(PAPER_PDF): $(PAPER_SRC) tools/md2tex.py Makefile $(PAPER_IMAGES)
	$(PY) tools/md2tex.py $(PAPER_SRC) $(PAPER_TEX)
	$(PAPER_ENV) pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build $(PAPER_TEX) > build/paper.pass1.log
	$(PAPER_ENV) pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build $(PAPER_TEX) > build/paper.pass2.log
	cp build/paper.pdf $@

$(SUPPORT_PDF): $(SUPPORT_SRC) tools/md2tex.py Makefile $(SUPPORT_IMAGES)
	$(PY) tools/md2tex.py $(SUPPORT_SRC) $(SUPPORT_TEX)
	$(SUPPORT_ENV) pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build $(SUPPORT_TEX) > build/supporting-material.pass1.log
	$(SUPPORT_ENV) pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build $(SUPPORT_TEX) > build/supporting-material.pass2.log
	cp build/supporting-material.pdf $@

clean:           ## remove generated exploration and typesetting output; never touches data/raw
	rm -rf results/exploration build __pycache__ src/orthopolity/__pycache__ tests/__pycache__
