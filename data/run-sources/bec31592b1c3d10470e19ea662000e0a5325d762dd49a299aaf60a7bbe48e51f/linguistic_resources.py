"""Fixed-vocabulary resource models; written length is not acoustic effort."""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
import hashlib
import re
import unicodedata

import numpy as np
from scipy.optimize import minimize
from scipy.special import logsumexp

WORD = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)*", re.UNICODE)
ASCII_WORD = re.compile(r"[a-z]+(?:'[a-z]+)*\Z")
GENRES = {"email", "weblog", "newsgroup", "reviews", "answers"}

@dataclass(frozen=True)
class Sentence:
    sent_id: str
    document: str
    genre: str
    text: str

    @property
    def text_hash(self):
        return hashlib.sha256(self.text.encode("utf-8")).hexdigest()

def parse_conllu(text):
    """Use original # text, never syntactic token pieces (e.g. ca + n't)."""
    records = []
    document = None
    seen = set()
    for block in re.split(r"\n\s*\n", text.strip()):
        metadata = {}
        for line in block.splitlines():
            if line.startswith("# ") and " = " in line:
                key, value = line[2:].split(" = ", 1)
                metadata[key] = value
        if "newdoc id" in metadata:
            document = metadata["newdoc id"]
        if not metadata:
            continue
        identifier, original = metadata["sent_id"], metadata["text"]
        # EWT source IDs use genre-originaldocument-sentence-number.
        genre = identifier.split("-", 1)[0]
        if genre not in GENRES:
            raise ValueError(f"Unrecognized EWT genre: {genre}")
        if document is None or not identifier.startswith(document + "-"):
            raise ValueError(f"Sentence lacks matching newdoc metadata: {identifier}")
        if identifier in seen:
            raise ValueError(f"Duplicate sentence identifier: {identifier}")
        seen.add(identifier)
        records.append(Sentence(identifier, document, genre, original))
    if not records:
        raise ValueError("No sentence text records")
    return records

def words(text):
    """Return accepted orthographic words and rejected non-ASCII letter runs.

    Punctuation and digits delimit runs; contractions remain a single word.
    Hyphenated strings are separate words. No stemming or lemmatization occurs.
    """
    candidates = WORD.findall(unicodedata.normalize("NFC", text))
    accepted, rejected = [], []
    for raw in candidates:
        word = raw.lower().replace("’", "'")
        (accepted if ASCII_WORD.fullmatch(word) else rejected).append(word)
    return accepted, rejected

def pronunciations(text):
    """Unnumbered CMU dictionary entries; stress digits do not add phonemes."""
    entries = {}
    for line in text.splitlines():
        line = line.split("#", 1)[0].strip()
        if not line or line.startswith(";;;"):
            continue
        fields = line.split()
        word = fields[0].lower()
        if "(" in word or not ASCII_WORD.fullmatch(word):
            continue
        phones = fields[1:]
        if not phones or any(not re.fullmatch(r"[A-Z]+[012]?", phone) for phone in phones):
            raise ValueError(f"Invalid pronunciation for {word}")
        if word in entries:
            raise ValueError(f"Repeated canonical pronunciation: {word}")
        entries[word] = len(phones)
    return entries

def training_vocabulary(sentences, dictionary, genres, minimum_count):
    if minimum_count < 1:
        raise ValueError("minimum count must be positive")
    count = Counter()
    for sentence in sentences:
        if sentence.genre in genres:
            count.update(words(sentence.text)[0])
    vocabulary = sorted(w for w, n in count.items() if n >= minimum_count and w in dictionary)
    if not vocabulary:
        raise ValueError("Empty training vocabulary")
    features = np.array([[len(w.replace("'", "")), dictionary[w]] for w in vocabulary], dtype=float)
    return vocabulary, np.array([count[w] for w in vocabulary], dtype=float), features, count

def log_probabilities(features, theta):
    x = np.asarray(features, dtype=float)
    theta = np.asarray(theta, dtype=float)
    if x.ndim != 2 or theta.shape != (x.shape[1],) or not np.isfinite(x).all() or not np.isfinite(theta).all():
        raise ValueError("Finite feature matrix and matching coefficient vector required")
    log_weight = -x @ theta
    return log_weight - logsumexp(log_weight)

def fit_positive_family(features, counts):
    """Convex conditional multinomial fit with nonnegative coefficients."""
    x, count = np.asarray(features, dtype=float), np.asarray(counts, dtype=float)
    if x.ndim != 2 or count.shape != (len(x),) or np.any(count < 0) or count.sum() <= 0 or not np.isfinite(count).all():
        raise ValueError("Feature rows need finite nonnegative counts with positive total")
    observed = count / count.sum()
    def objective(theta):
        lp = log_probabilities(x, theta)
        probability = np.exp(lp)
        return float(-observed @ lp), (observed - probability) @ x
    result = minimize(objective, np.ones(x.shape[1]), jac=True, method="L-BFGS-B",
                      bounds=[(0, None)] * x.shape[1], options={"ftol": 1e-14, "gtol": 1e-10, "maxiter": 10000})
    if not result.success:
        raise RuntimeError(f"Training optimization failed: {result.message}")
    theta = result.x
    lp = log_probabilities(x, theta)
    probability = np.exp(lp)
    centered = x - probability @ x
    hessian = (centered * probability[:, None]).T @ centered
    eigenvalues = np.linalg.eigvalsh(hessian)
    gradient = objective(theta)[1]
    projected = np.where(theta <= 1e-8, np.minimum(gradient, 0), gradient)
    if np.max(np.abs(projected)) > 1e-6:
        raise RuntimeError("Training optimum fails projected-gradient check")
    return dict(theta=theta.tolist(), log_probability=lp.tolist(), loss=objective(theta)[0],
                boundary=[bool(t <= 1e-8) for t in theta], gradient=gradient.tolist(),
                projected_gradient_max=float(np.max(np.abs(projected))),
                per_token_information=hessian.tolist(), information_eigenvalues=eigenvalues.tolist(),
                information_condition=float(eigenvalues[-1] / eigenvalues[0]) if eigenvalues[0] > 0 else None,
                optimizer=str(result.message))

def fitted_models(features, counts, smoothing=.5):
    features = np.asarray(features, float)
    if features.ndim != 2 or features.shape[1] != 2 or np.any(features <= 0) or smoothing <= 0:
        raise ValueError("Positive letter/phoneme features and smoothing required")
    logs = np.log(features)
    n = len(features)
    models = {
        "uniform": dict(theta=[], log_probability=np.full(n, -np.log(n)).tolist()),
        "inverse_letters": dict(theta=[1.], log_probability=log_probabilities(logs[:, :1], [1.]).tolist()),
        "letters_power": fit_positive_family(logs[:, :1], counts),
        "composite_power": fit_positive_family(logs, counts),
        "letters_exponential": fit_positive_family(features[:, :1], counts),
    }
    count = np.asarray(counts, float)
    probability = (count + smoothing) / (count.sum() + smoothing * n)
    models["training_unigram"] = dict(theta=[], smoothing=smoothing, log_probability=np.log(probability).tolist())
    return models

def document_bootstrap(loss_sums, token_counts, *, replicates, seed):
    """Paired ratio-of-sums document bootstrap, conditional on frozen models.

    Documents may have no retained vocabulary tokens. Replicates without any
    retained tokens are rejected rather than assigned a fictitious zero loss.
    """
    loss = np.asarray(loss_sums, dtype=float)
    count = np.asarray(token_counts, dtype=float)
    if loss.ndim != 2 or count.shape != (len(loss),) or np.any(count < 0) or count.sum() <= 0:
        raise ValueError("Document losses require matching nonnegative counts")
    rng = np.random.default_rng(seed)
    result = []
    for _ in range(replicates):
        indices = rng.integers(0, len(count), size=len(count))
        denominator = count[indices].sum()
        if denominator:
            result.append(loss[indices].sum(axis=0) / denominator)
    if not result:
        raise ValueError("No bootstrap replicate retained tokens")
    return np.asarray(result)
