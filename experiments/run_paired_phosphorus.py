"""Run the locally frozen, independently assayed phosphorus transfer pilot."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from orthopolity.paired_phosphorus import analyse
from fetch_paired_phosphorus import verify, encode

CONFIG = "configs/paired_phosphorus_2026-10-12.json"
FROZEN = [CONFIG, "docs/paired-phosphorus-protocol-2026-10-12.md",
          "src/orthopolity/paired_phosphorus.py", "experiments/run_paired_phosphorus.py",
          "experiments/fetch_paired_phosphorus.py", "tests/test_paired_phosphorus.py"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    config = json.loads((ROOT / CONFIG).read_text())
    verify()
    frozen_refs = []
    for name in FROZEN:
        body = (ROOT / name).read_bytes()
        committed = subprocess.check_output(["git", "show", f"HEAD:{name}"], cwd=ROOT)
        if body != committed:
            raise ValueError(f"Uncommitted analysis source: {name}")
        frozen_refs.append(dict(path=name, sha256=hashlib.sha256(body).hexdigest()))
    inputs = []
    tables = []
    for item in config["inputs"]:
        path = ROOT / item["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError("Source differs from frozen checksum")
        tables.append(list(csv.DictReader(path.open())))
        inputs.append(item)
    result = analyse(tables[1], tables[0], config)
    args.output.mkdir(parents=True, exist_ok=True)
    for filename, value in (("result.json", result), ("execution.json", dict(
            freeze_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            sources=frozen_refs, inputs=inputs, python=sys.version,
            randomized_analysis=False, outcomes_unopened_until_local_freeze=True))):
        path = args.output / filename
        if path.exists():
            raise ValueError(f"Refusing to replace existing output: {path}")
        path.write_bytes(encode(value))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
