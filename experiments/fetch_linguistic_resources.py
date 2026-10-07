"""Fetch pinned public linguistic sources in two stages, or verify offline."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "data/linguistic-resources/2026-10-07"
EWT = "https://raw.githubusercontent.com/UniversalDependencies/UD_English-EWT/b7711cce01cdd4f5fcc0a8199b8a50d951b16c0c/"
CMU = "https://raw.githubusercontent.com/cmusphinx/cmudict/74790861f652b15e4ac49015a90074ad62a27690/"
SOURCES = [
    ("ewt-README.md", EWT + "README.md", "train", "Corpus metadata and mixed underlying-text rights"),
    ("ewt-LICENSE.txt", EWT + "LICENSE.txt", "train", "CC BY-SA 4.0 annotations/database license"),
    ("en_ewt-ud-train.conllu", EWT + "en_ewt-ud-train.conllu", "train", "Official training split; selected genres only used for fitting"),
    ("cmudict.dict", CMU + "cmudict.dict", "train", "Independent canonical pronunciation features"),
    ("cmudict-LICENSE", CMU + "LICENSE", "train", "CMU dictionary redistribution license"),
    ("cmudict-README", CMU + "README", "train", "Dictionary metadata"),
    ("en_ewt-ud-test.conllu", EWT + "en_ewt-ud-test.conllu", "test", "Official test split, acquired after frozen fit")
]

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def verify(stage="all", directory=None):
    directory = DIRECTORY if directory is None else Path(directory)
    manifest = json.loads((directory / "sources.json").read_text())
    expected = {name: (url, s) for name, url, s, _ in SOURCES if stage == "all" or s == stage}
    selected = [r for r in manifest["sources"] if stage == "all" or r["stage"] == stage]
    records = {r["filename"]: r for r in selected}
    if set(records) != set(expected) or len(records) != len(selected):
        raise ValueError("Unexpected or duplicate source membership")
    for name, (url, source_stage) in expected.items():
        record = records[name]
        path = directory / name
        receipt = json.loads((directory / (name + ".receipt.json")).read_text())
        if (receipt != record or record["url"] != url or record["stage"] != source_stage
                or digest(path) != record["sha256"] or path.stat().st_size != record["size_bytes"]):
            raise ValueError(f"Source failed URL/hash/size check: {name}")
    return len(expected)

def acquire(stage):
    DIRECTORY.mkdir(parents=True, exist_ok=True)
    if stage == "test":
        freeze = json.loads((DIRECTORY / "freeze.json").read_text())
        for relative, checksum in freeze["files"].items():
            if digest(ROOT / relative) != checksum:
                raise ValueError(f"Frozen file changed before held-out acquisition: {relative}")
    for name, url, source_stage, role in SOURCES:
        if source_stage != stage:
            continue
        target = DIRECTORY / name
        receipt = DIRECTORY / (name + ".receipt.json")
        if receipt.exists():
            record = json.loads(receipt.read_text())
            if record["url"] != url or digest(target) != record["sha256"]:
                raise ValueError(f"Changed partial source: {name}")
            continue
        if target.exists():
            raise ValueError(f"Unreceipted source: {name}")
        with tempfile.TemporaryDirectory(dir=DIRECTORY) as scratch:
            temporary = Path(scratch) / name
            response = subprocess.run([
                "/usr/bin/curl", "--fail", "--location", "--silent", "--show-error", "--max-time", "90",
                "--output", str(temporary), "--write-out", "%{url_effective}\n%{content_type}\n", url
            ], check=True, capture_output=True, text=True)
            lines = response.stdout.strip().splitlines()
            record = dict(filename=name, url=url, final_url=lines[0], content_type=lines[1] if len(lines)>1 else "",
                          role=role, stage=stage, retrieved_at_utc=datetime.now(timezone.utc).isoformat(),
                          size_bytes=temporary.stat().st_size, sha256=digest(temporary))
            temporary.rename(target)
        receipt.write_text(json.dumps(record, indent=2) + "\n")
        print(name, record["size_bytes"], record["sha256"])
    records = [json.loads((DIRECTORY / (name + ".receipt.json")).read_text())
               for name, _, _, _ in SOURCES if (DIRECTORY / (name + ".receipt.json")).exists()]
    (DIRECTORY / "sources.json").write_text(json.dumps(dict(schema_version=1, sources=records), indent=2) + "\n")
    print(json.dumps(dict(verified_sources=verify(stage))))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch", action="store_true")
    parser.add_argument("--stage", choices=["train", "test", "all"], default="all")
    args = parser.parse_args()
    if args.fetch:
        if args.stage == "all":
            parser.error("Network retrieval requires an explicit train or test stage")
        acquire(args.stage)
    else:
        print(json.dumps(dict(verified_sources=verify(args.stage))))
