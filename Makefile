# Reproduce everything from the frozen snapshots.
#
#   make install   editable install, so `import gof` works without PYTHONPATH
#   make all       verify data, run tests, run every analysis
#   make paper     typeset docs/paper.md into docs/paper.pdf (needs pdflatex)
#
# Analyses depend only on data/raw/, which is checksummed; they never fetch.

PY ?= python3
export PYTHONPATH := src

.PHONY: all install data restore-data test pilot gof independent ensemble strata variance theory analyses paper clean

PAPER_SRC := docs/paper.md
PAPER_TEX := build/paper.tex
PAPER_PDF := docs/paper.pdf

all: data test analyses

install:
	$(PY) -m pip install -r requirements.txt -e ".[analyses]"

data:            ## verify every raw input against data/snapshot_checksums.json
	$(PY) experiments/fetch_data.py

restore-data:    ## explicitly permit network restoration of missing snapshots
	$(PY) experiments/fetch_data.py --restore

test:            ## accounting, estimator, goodness-of-fit and meta-analysis checks
	$(PY) -m unittest discover -s tests -v

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

paper: $(PAPER_PDF)  ## typeset the manuscript; requires a TeX installation

# tools/md2tex.py handles the Markdown subset the manuscript uses, so no Pandoc
# is required. Two passes settle the PDF outline and any page references.
$(PAPER_PDF): $(PAPER_SRC) tools/md2tex.py results/theory.png
	$(PY) tools/md2tex.py $(PAPER_SRC) $(PAPER_TEX)
	pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build $(PAPER_TEX) > build/paper.pass1.log
	pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build $(PAPER_TEX) > build/paper.pass2.log
	cp build/paper.pdf $@

clean:           ## remove generated exploration and typesetting output; never touches data/raw
	rm -rf results/exploration build __pycache__ src/__pycache__ tests/__pycache__
