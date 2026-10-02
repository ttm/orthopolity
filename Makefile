# Reproduce everything from the frozen snapshots.
#
#   make install   editable install, so `import orthopolity` works without PYTHONPATH
#   make all       verify data, run tests, run every analysis
#   make paper     typeset docs/paper.md into docs/paper.pdf (needs pdflatex)
#
# Historical downloaded inputs live in checksummed data/raw/. Later studies
# retain their own measured/generated inputs and acquisition receipts. Analysis
# targets are offline; network acquisition is a separate explicit driver stage.

PY ?= python3
export PYTHONPATH := src
STUDY_OUTPUT_ROOT ?= build/reproductions

.PHONY: all install data restore-data test pilot gof independent ensemble strata variance theory models dependence attachment restrictions followup competition forecast interventions robustness workload-pilot workload-report workload-transfer workload-transfer-report scheduler-allocation run-registry registry-verify solar-resource-transfer aquatic-study-transfer resource-identification profile-tests profile-test-registry analyses paper clean
.PHONY: profile-calibration solar-validation dimensionality-intervention validation-round validation-round-registry
.PHONY: chemostat-sources restore-chemostat-bundle archived-cost-transfer available-data-registry chemostat-response chemostat-response-report
.PHONY: dunaliella-sources dunaliella-size-budget dunaliella-size-budget-report

PAPER_SRC := docs/paper.md
PAPER_TEX := build/paper.tex
PAPER_PDF := docs/paper.pdf

# The PDF is tracked, so its bytes must not change unless the manuscript does:
# date it from the manuscript's last commit rather than from the clock.
PAPER_EPOCH := $(shell git log -1 --format=%ct -- docs/paper.md 2>/dev/null)
ifeq ($(PAPER_EPOCH),)
PAPER_EPOCH := 0
endif
PAPER_ENV := SOURCE_DATE_EPOCH=$(PAPER_EPOCH) FORCE_SOURCE_DATE=1

all: data test analyses

install:
	$(PY) -m pip install -r requirements.txt -e ".[analyses]"

data:            ## verify every raw input against data/snapshot_checksums.json
	$(PY) experiments/fetch_data.py

restore-data:    ## explicitly permit network restoration of missing snapshots
	$(PY) experiments/fetch_data.py --restore

test:            ## accounting, estimator, goodness-of-fit and meta-analysis checks
	MPLCONFIGDIR=build/matplotlib $(PY) -m unittest discover -s tests -v

analyses: pilot gof independent ensemble strata variance theory

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

paper: $(PAPER_PDF)  ## typeset the manuscript; requires a TeX installation

# tools/md2tex.py handles the Markdown subset the manuscript uses, so no Pandoc
# is required. Two passes settle the PDF outline and any page references.
$(PAPER_PDF): $(PAPER_SRC) tools/md2tex.py results/theory.png
	$(PY) tools/md2tex.py $(PAPER_SRC) $(PAPER_TEX)
	$(PAPER_ENV) pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build $(PAPER_TEX) > build/paper.pass1.log
	$(PAPER_ENV) pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build $(PAPER_TEX) > build/paper.pass2.log
	cp build/paper.pdf $@

clean:           ## remove generated exploration and typesetting output; never touches data/raw
	rm -rf results/exploration build __pycache__ src/orthopolity/__pycache__ tests/__pycache__
