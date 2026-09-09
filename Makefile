# Reproduce everything from the frozen snapshots.
#
#   make install   editable install, so `import gof` works without PYTHONPATH
#   make all       verify data, run tests, run every analysis
#
# Analyses depend only on data/raw/, which is checksummed; they never fetch.

PY ?= python
export PYTHONPATH := src

.PHONY: all install data test pilot gof independent ensemble strata variance analyses clean

all: data test analyses

install:
	$(PY) -m pip install -e ".[analyses]"

data:            ## verify every raw input against data/snapshot_checksums.json
	$(PY) experiments/fetch_data.py

test:            ## 54 accounting, estimator, goodness-of-fit and meta-analysis checks
	$(PY) -m unittest discover -s tests -v

analyses: pilot gof independent ensemble strata variance

pilot:           ## the three original pilots -> results/results.json
	$(PY) experiments/run_pilot.py

gof:             ## goodness of fit and flatness equivalence -> results/gof.json
	$(PY) experiments/run_gof.py

independent:     ## preregistered independent tests -> results/independent.json
	$(PY) experiments/run_independent.py

ensemble:        ## is the ensemble result real? -> results/ensemble.json
	$(PY) experiments/run_ensemble.py

strata:          ## class mixture and span/taxon confound -> results/strata.json
	$(PY) experiments/run_strata.py

variance:        ## between- vs within-ecosystem dispersion -> results/variance.json
	$(PY) experiments/run_variance.py

clean:           ## remove generated exploration output only; never touches data/raw
	rm -rf results/exploration __pycache__ src/__pycache__ tests/__pycache__
