"""Audit identities first; compute field stocks only from committed sources."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from orthopolity.field_resources import audit, analyse
from fetch_field_resources import verify, encode

BASE = ROOT / "data/field-resources/2026-10-12"
CONFIG = "configs/field_resources_2026-10-12.json"
FROZEN = [CONFIG, "docs/field-resources-protocol-2026-10-12.md",
          "src/orthopolity/field_resources.py", "experiments/run_field_resources.py",
          "experiments/fetch_field_resources.py", "tests/test_field_resources.py",
          "data/field-resources/2026-10-12/qualification-before-response.json"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("audit", "evaluate"), default="audit")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--freeze-commit")
    args = parser.parse_args()
    verify()
    config = json.loads((ROOT / CONFIG).read_text())
    for item in config["inputs"]:
        if hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest() != item["sha256"]:
            raise ValueError("Input differs from frozen checksum")
    tables = {dataset: list(csv.DictReader((BASE / f"{dataset}.csv").open()))
              for dataset in ("849153", "829895", "538091")}
    qualification = audit(tables["849153"], tables, config["coordinate_tolerance_degrees"])
    for status, expected in config["expected_quota_rows"].items():
        if [r["quota_row"] for r in qualification["records"] if r["status"] == status] != expected:
            raise ValueError("Unexpected metadata qualification")
    if args.stage == "audit":
        if args.output.exists():
            raise ValueError("Refusing to replace audit")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes(encode(qualification))
        print(json.dumps(qualification["status_counts"], indent=2))
        return
    if not args.freeze_commit:
        raise ValueError("Evaluation requires the explicit pre-response freeze commit")
    freeze = subprocess.check_output(["git", "rev-parse", args.freeze_commit], cwd=ROOT, text=True).strip()
    sources = []
    for path in FROZEN:
        body = (ROOT / path).read_bytes()
        if body != subprocess.check_output(["git", "show", f"{freeze}:{path}"], cwd=ROOT):
            raise ValueError(f"Unfrozen analysis source: {path}")
        sources.append(dict(path=path, sha256=hashlib.sha256(body).hexdigest()))
    if qualification != json.loads((BASE / "qualification-before-response.json").read_text()):
        raise ValueError("Qualification differs from pre-response audit")
    if args.output.exists():
        raise ValueError("Use a new output directory")
    result = analyse(tables["849153"], tables, config)
    args.output.mkdir(parents=True)
    execution = dict(freeze_commit=freeze, sources=sources, inputs=config["inputs"],
                     python=sys.version, randomized_analysis=False,
                     chronology="Source metadata and published findings exposed before local freeze; raw numerical comparison after freeze")
    for name, value in (("result.json", result), ("execution.json", execution)):
        (args.output / name).write_bytes(encode(value))
    print(json.dumps(result["summaries"], indent=2))


if __name__ == "__main__":
    main()
