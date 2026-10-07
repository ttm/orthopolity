"""Fit, freeze, and evaluate symbolic word-resource forecasts on EWT offline."""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import platform

import numpy as np
import scipy
from orthopolity.linguistic_resources import (
    document_bootstrap, fitted_models, parse_conllu, pronunciations, training_vocabulary, words,
)

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "configs/linguistic_resources_2026-10-07.json"
FETCH_SPEC = importlib.util.spec_from_file_location("linguistic_fetch", ROOT / "experiments/fetch_linguistic_resources.py")
FETCH = importlib.util.module_from_spec(FETCH_SPEC)
FETCH_SPEC.loader.exec_module(FETCH)
ALGORITHM = ["configs/linguistic_resources_2026-10-07.json", "docs/linguistic-protocol.md",
             "src/orthopolity/linguistic_resources.py", "experiments/run_linguistic_resources.py",
             "experiments/fetch_linguistic_resources.py", "tests/test_linguistic_resources.py"]

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")

def write_csv(path, rows, columns=None):
    if columns is None:
        columns = list(rows[0])
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

def verify_sources(directory, stage):
    FETCH.verify(stage, directory)
    manifest = json.loads((directory / "sources.json").read_text())
    wanted = [row for row in manifest["sources"] if stage == "all" or row["stage"] == stage]
    expected = 7 if stage == "all" else 6
    if len(wanted) != expected:
        raise ValueError("Unexpected source membership")
    for row in wanted:
        path = directory / row["filename"]
        if digest(path) != row["sha256"] or path.stat().st_size != row["size_bytes"]:
            raise ValueError(f"Source failed hash/size check: {path}")
    return {str((directory / row["filename"]).relative_to(ROOT)): row["sha256"] for row in wanted}

def train(config, directory):
    hashes = verify_sources(directory, "train")
    sentences = parse_conllu((directory / "en_ewt-ud-train.conllu").read_text())
    dictionary = pronunciations((directory / "cmudict.dict").read_text())
    vocabulary, counts, features, all_count = training_vocabulary(
        sentences, dictionary, config["training_genres"], config["minimum_training_count"])
    models = fitted_models(features, counts, config["unigram_smoothing"])
    selected = [s for s in sentences if s.genre in config["training_genres"]]
    logs = np.log(features)
    diagnostics = dict(vocabulary_size=len(vocabulary), retained_training_tokens=int(counts.sum()),
        selected_training_sentences=len(selected), selected_training_documents=len({s.document for s in selected}),
        all_training_sentences=len(sentences), all_training_documents=len({s.document for s in sentences}),
        sentence_counts_by_genre=dict(sorted(Counter(s.genre for s in sentences).items())),
        ascii_training_tokens=sum(all_count.values()),
        non_ascii_training_letter_runs=sum(len(words(s.text)[1]) for s in selected),
        unweighted_log_feature_correlation=float(np.corrcoef(logs.T)[0, 1]),
        distinct_feature_pairs=len({tuple(f) for f in features}),
        interpretation="Parameters define a symbolic-cost candidate, not sonority or physical effort.")
    frozen = dict(schema_version=1, config_run_id=config["run_id"], vocabulary=vocabulary,
                  training_counts=counts.astype(int).tolist(), features=features.astype(int).tolist(),
                  models=models, diagnostics=diagnostics,
                  training_word_counts=dict(sorted(all_count.items())),
                  all_training_sentence_hashes=sorted({s.text_hash for s in sentences}),
                  all_training_documents=sorted({s.document for s in sentences}),
                  fitted_training_documents=sorted({s.document for s in selected}),
                  source_hashes=hashes)
    return frozen

def freeze_training(config, directory):
    if config != json.loads(CONFIG.read_text()):
        raise ValueError("Only the frozen default configuration is supported")
    freeze_path = directory / "freeze.json"
    if freeze_path.exists():
        raise ValueError("An existing freeze is immutable; use evaluate for offline replay")
    if (directory / "en_ewt-ud-test.conllu").exists():
        raise ValueError("Cannot create a pre-test freeze after test acquisition")
    frozen = train(config, directory)
    fit_path = directory / "frozen-fit.json"
    write_json(fit_path, frozen)
    files = {p: digest(ROOT / p) for p in ALGORITHM}
    files.update(frozen["source_hashes"])
    files[str(fit_path.relative_to(ROOT))] = digest(fit_path)
    write_json(freeze_path, dict(schema_version=1, frozen_at_utc=datetime.now(timezone.utc).isoformat(),
        stage="training complete; official test file not acquired or decoded",
        exposure=config["exposure_status"], files=files))
    print(json.dumps(frozen["diagnostics"], indent=2))
    print(json.dumps({name: row.get("theta") for name, row in frozen["models"].items()}, indent=2))

def check_freeze(directory):
    freeze = json.loads((directory / "freeze.json").read_text())
    for relative, checksum in freeze["files"].items():
        if digest(ROOT / relative) != checksum:
            raise ValueError(f"Frozen source or fit changed: {relative}")
    return freeze

def sentence_counts(sentence, vocabulary_index, dictionary, training_counts):
    accepted, rejected = words(sentence.text)
    vector = np.zeros(len(vocabulary_index), dtype=int)
    excluded = Counter()
    for word in accepted:
        if word in vocabulary_index:
            vector[vocabulary_index[word]] += 1
        elif word not in dictionary:
            excluded[("dictionary_absent", word)] += 1
        elif word not in training_counts:
            excluded[("unseen_in_fitting_genres", word)] += 1
        else:
            excluded[("training_count_below_five", word)] += 1
    for word in rejected:
        excluded[("non_ascii_letter_run", word)] += 1
    return vector, excluded, len(accepted) + len(rejected), len(accepted)

def score_group(label, docs, model_names, probabilities, features, config):
    matrix = np.stack([row["counts"] for row in docs])
    token_count = matrix.sum(axis=1)
    total = matrix.sum(axis=0)
    n = int(total.sum())
    if n == 0:
        raise ValueError(f"No retained tokens in {label}")
    logp = np.log(probabilities)
    loss_sums = -matrix @ logp.T
    losses = loss_sums.sum(axis=0) / n
    replicates = document_bootstrap(loss_sums, token_count,
        replicates=config["bootstrap_replicates"], seed=config["bootstrap_seed"])
    baseline = model_names.index("letters_power")
    delta = replicates - replicates[:, baseline, None]
    empirical = total / n
    letter_mass = total * features[:, 0]
    letter_shares = letter_mass / letter_mass.sum()
    composite_theta = np.array(config["composite_theta"])
    composite_cost = np.exp(np.log(features) @ composite_theta)
    effective_mass = total * composite_cost
    effective_shares = effective_mass / effective_mass.sum()
    uniform = 1 / len(total)
    model_rows = []
    for m, name in enumerate(model_names):
        low, high = np.quantile(delta[:, m], [.025, .975])
        predicted_letters = probabilities[m] * features[:, 0]
        predicted_letters /= predicted_letters.sum()
        model_rows.append(dict(group=label, model=name, tokens=n,
            loss_nats=float(losses[m]), perplexity=float(np.exp(losses[m])),
            loss_minus_letters_power=float(losses[m] - losses[baseline]),
            bootstrap_delta_low=float(low), bootstrap_delta_high=float(high),
            count_total_variation=float(.5 * np.abs(empirical-probabilities[m]).sum()),
            letter_share_total_variation=float(.5 * np.abs(letter_shares-predicted_letters).sum())))
    excluded = sum(row["candidate_tokens"] - int(row["counts"].sum()) for row in docs)
    coverage = dict(group=label, documents=len(docs), zero_retained_token_documents=int(np.sum(token_count == 0)),
        sentences=sum(row["sentences"] for row in docs), tokens=n,
        candidate_letter_runs=sum(row["candidate_tokens"] for row in docs), excluded_tokens=excluded,
        coverage=n / sum(row["candidate_tokens"] for row in docs),
        bootstrap_replicates_retained=len(replicates),
        bootstrap_zero_token_replicates=config["bootstrap_replicates"]-len(replicates),
        letter_resource_tv_from_uniform=float(.5 * np.abs(letter_shares-uniform).sum()),
        composite_resource_tv_from_uniform=float(.5 * np.abs(effective_shares-uniform).sum()))
    type_rows = [dict(group=label, word=word, letters=int(features[i, 0]), phonemes=int(features[i, 1]),
        count=int(total[i]), empirical_probability=float(empirical[i]),
        letter_resource_share=float(letter_shares[i]), composite_resource_share=float(effective_shares[i]))
        for i, word in enumerate(config["vocabulary"])]
    profile_rows = []
    for length in sorted(set(features[:, 0].astype(int))):
        mask = features[:, 0] == length
        row = dict(group=label, letters=length, vocabulary_types=int(mask.sum()),
            uniform_type_share=float(mask.mean()), count_share=float(empirical[mask].sum()),
            letter_resource_share=float(letter_shares[mask].sum()), composite_resource_share=float(effective_shares[mask].sum()))
        for m, name in enumerate(model_names):
            row[name + "_count_share"] = float(probabilities[m, mask].sum())
        profile_rows.append(row)
    return model_rows, coverage, type_rows, profile_rows

def figures(output, scores, profiles):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 9, "svg.fonttype": "none", "svg.hashsalt": "linguistic-resources-2026-10-07"})
    fig, axes = plt.subplots(1, 2, figsize=(8.1, 3.5), layout="constrained")
    primary = [r for r in scores if r["group"] == "primary"]
    labels = ["Uniform", "Inverse letters", "Letter power", "Composite power", "Exponential letters", "Training unigram"]
    values = [r["loss_nats"] for r in primary]
    axes[0].barh(np.arange(len(labels)), values, color=["#999999", "#777777", "#31688e", "#b45a35", "#5d9c91", "#5c537e"])
    axes[0].set_yticks(np.arange(len(labels)), labels)
    axes[0].invert_yaxis()
    axes[0].set(xlabel="Held-out loss (nats/token; lower is better)", title="a  Reviews + answers: frozen forecasts")
    for i, value in enumerate(values):
        axes[0].text(value+.03, i, f"{value:.3f}", va="center", fontsize=8)
    axes[0].set_xlim(0, max(values)+.65)
    rows = [r for r in profiles if r["group"] == "primary"]
    x = [r["letters"] for r in rows]
    axes[1].plot(x, [r["uniform_type_share"] for r in rows], "k--", label="Equal allocation across word types")
    axes[1].plot(x, [r["letter_resource_share"] for r in rows], "o-", ms=3, label="Observed letter allocation")
    axes[1].plot(x, [r["composite_resource_share"] for r in rows], "s-", ms=3, label="Observed inferred-cost allocation")
    axes[1].set(xlabel="Letters per word", ylabel="Resource share in length class", title="b  Descriptive allocation profiles")
    axes[1].legend(frameon=False, fontsize=7)
    fig.savefig(output / "linguistic-resources.png", dpi=180, metadata={"Software": "orthopolity"})
    fig.savefig(output / "linguistic-resources.svg", metadata={"Date": None, "Creator": "orthopolity"})
    plt.close(fig)

def evaluate(config, directory, output):
    if config != json.loads(CONFIG.read_text()):
        raise ValueError("Only the frozen default configuration is supported")
    freeze = check_freeze(directory)
    hashes = verify_sources(directory, "all")
    provenance_path = output / "provenance.json"
    if provenance_path.exists():
        retained = json.loads(provenance_path.read_text())
        if (retained["source_hashes"] != hashes or retained["frozen_files"] != freeze["files"]
                or retained["freeze_sha256"] != digest(directory / "freeze.json")):
            raise ValueError("Retained inputs changed; preserve this run and choose another output directory")
        if (set(retained["outputs"]) != {p.name for p in output.iterdir() if p.is_file() and p.name != "provenance.json"}
                or not all((output / name).is_file() and digest(output / name) == checksum
                           for name, checksum in retained["outputs"].items())):
            raise ValueError("Retained outputs changed; preserve this run and choose another output directory")
        print(json.dumps(dict(action="audited_existing_run", output=str(output))))
        return
    if output.exists() and any(output.iterdir()):
        raise ValueError("Output directory is not empty; preserve it and choose another output directory")
    frozen = json.loads((directory / "frozen-fit.json").read_text())
    # Recompute training independently before any held-out decoding; verify exact fit.
    if train(config, directory) != frozen:
        raise ValueError("Offline refit differs from the frozen training artifact")
    sentences = parse_conllu((directory / "en_ewt-ud-test.conllu").read_text())
    dictionary = pronunciations((directory / "cmudict.dict").read_text())
    vocabulary = frozen["vocabulary"]
    indices = {w: i for i, w in enumerate(vocabulary)}
    features = np.array(frozen["features"], dtype=float)
    model_names = config["models"]
    probability = np.array([np.exp(frozen["models"][name]["log_probability"]) for name in model_names])
    training_hashes = set(frozen["all_training_sentence_hashes"])
    docs = {}
    duplicates, excluded_words = [], Counter()
    for sentence in sentences:
        count, excluded, candidates, ascii_count = sentence_counts(sentence, indices, dictionary, frozen["training_word_counts"])
        if sentence.text_hash in training_hashes:
            duplicates.append(dict(sent_id=sentence.sent_id, document=sentence.document, genre=sentence.genre,
                text_sha256=sentence.text_hash, candidate_letter_runs=candidates, vocabulary_tokens=int(count.sum()),
                reason="exact_original_text_in_official_training"))
            continue
        if sentence.document not in docs:
            docs[sentence.document] = dict(document=sentence.document, genre=sentence.genre, counts=np.zeros(len(vocabulary), dtype=int),
                sentences=0, candidate_tokens=0, ascii_tokens=0, exclusions=Counter())
        row = docs[sentence.document]
        row["counts"] += count
        row["sentences"] += 1
        row["candidate_tokens"] += candidates
        row["ascii_tokens"] += ascii_count
        row["exclusions"].update({reason: sum(n for (r, w), n in excluded.items() if r == reason) for reason in {r for r, w in excluded}})
        excluded_words.update({(sentence.genre, reason, word): n for (reason, word), n in excluded.items()})
    docs_list = [docs[key] for key in sorted(docs)]
    groups = {"primary": config["primary_genres"], "secondary": config["secondary_genres"]}
    groups.update({genre: [genre] for genre in sorted(set(s.genre for s in sentences))})
    analysis_config = dict(config, vocabulary=vocabulary, composite_theta=frozen["models"]["composite_power"]["theta"])
    scores, coverage, type_rows, profiles = [], [], [], []
    for label, genres in groups.items():
        rows, cover, types, profile = score_group(label, [r for r in docs_list if r["genre"] in genres],
            model_names, probability, features, analysis_config)
        scores.extend(rows); coverage.append(cover); type_rows.extend(types); profiles.extend(profile)
    document_rows = []
    for row in docs_list:
        item = dict(document=row["document"], genre=row["genre"], sentences=row["sentences"],
            candidate_letter_runs=row["candidate_tokens"], ascii_tokens=row["ascii_tokens"], vocabulary_tokens=int(row["counts"].sum()))
        for reason in ("dictionary_absent", "unseen_in_fitting_genres", "training_count_below_five", "non_ascii_letter_run"):
            item[reason] = row["exclusions"][reason]
        for i, name in enumerate(model_names):
            item[name + "_loss_sum"] = float(-row["counts"] @ np.log(probability[i]))
        document_rows.append(item)
    test_documents = {s.document for s in sentences}
    summary = dict(schema_version=1, run_id=config["run_id"], diagnostics=frozen["diagnostics"],
        parameters={name: {k: v for k, v in row.items() if k != "log_probability"} for name, row in frozen["models"].items()},
        coverage=coverage, scores=scores,
        official_test_sentences=len(sentences), official_test_documents=len(test_documents),
        exact_training_duplicate_sentences=len(duplicates), duplicate_candidate_letter_runs=sum(r["candidate_letter_runs"] for r in duplicates),
        duplicate_vocabulary_tokens=sum(r["vocabulary_tokens"] for r in duplicates),
        all_training_document_overlap=sorted(test_documents & set(frozen["all_training_documents"])),
        fitted_training_document_overlap=sorted(test_documents & set(frozen["fitted_training_documents"])),
        bootstrap="Paired document resampling; conditional on frozen fit and corpus, not token-iid or training uncertainty",
        feature_limitation="Identical letter/phoneme pairs imply identical model probabilities; semantic, lexical and contextual heterogeneity is not modeled.",
        exposure=config["exposure_status"])
    output.mkdir(parents=True, exist_ok=True)
    write_json(output / "config.json", config)
    write_json(output / "summary.json", summary)
    write_csv(output / "scores.csv", scores)
    write_csv(output / "coverage.csv", coverage)
    write_csv(output / "documents.csv", document_rows)
    write_csv(output / "type-profiles.csv", type_rows)
    write_csv(output / "length-profiles.csv", profiles)
    write_csv(output / "duplicate-exclusions.csv", duplicates,
        ["sent_id", "document", "genre", "text_sha256", "candidate_letter_runs", "vocabulary_tokens", "reason"])
    exclusions = [dict(genre=g, reason=r, word=w, occurrences=n) for (g, r, w), n in sorted(excluded_words.items())]
    write_csv(output / "word-exclusions.csv", exclusions, ["genre", "reason", "word", "occurrences"])
    vocabulary_rows = []
    for i, word in enumerate(vocabulary):
        row = dict(word=word, training_count=frozen["training_counts"][i], letters=int(features[i,0]), phonemes=int(features[i,1]))
        row.update({name: float(probability[m, i]) for m, name in enumerate(model_names)})
        vocabulary_rows.append(row)
    write_csv(output / "vocabulary-and-forecasts.csv", vocabulary_rows)
    figures(output, scores, profiles)
    paths = sorted(p for p in output.iterdir() if p.is_file() and p.name != "provenance.json")
    write_json(output / "provenance.json", dict(run_id=config["run_id"], completed_at_utc=datetime.now(timezone.utc).isoformat(),
        python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__,
        source_hashes=hashes, freeze_sha256=digest(directory / "freeze.json"), frozen_files=freeze["files"],
        outputs={p.name: digest(p) for p in paths}))
    print(json.dumps(dict(parameters={name: row.get("theta") for name, row in frozen["models"].items()},
                          coverage=coverage[:2], primary_scores=scores[:6],
                          duplicate_sentences=len(duplicates), document_overlap=summary["all_training_document_overlap"]), indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=CONFIG)
    parser.add_argument("--stage", choices=["train", "evaluate"], required=True)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    directory = ROOT / config["source_directory"]
    if args.stage == "train":
        freeze_training(config, directory)
    else:
        evaluate(config, directory, args.output_dir or ROOT / config["output_directory"])
