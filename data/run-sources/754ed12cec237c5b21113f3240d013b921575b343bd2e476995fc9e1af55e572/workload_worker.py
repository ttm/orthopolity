"""One actual workload in a fresh process; parent fixes threads before import."""
from __future__ import annotations

import argparse
import json

from orthopolity.workload import run_workload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--size', type=int, required=True)
    parser.add_argument('--repeats', type=int, default=3)
    parser.add_argument('--warmup-size', type=int, default=64)
    parser.add_argument('--memory-budget-bytes', type=int)
    parser.add_argument('--cpu-budget-seconds', type=float)
    args = parser.parse_args()
    result = run_workload(
        args.size, repeats=args.repeats, warmup_size=args.warmup_size,
        memory_budget_bytes=args.memory_budget_bytes,
        cpu_budget_seconds=args.cpu_budget_seconds,
    )
    print(json.dumps(result, allow_nan=False), flush=True)


if __name__ == '__main__':
    main()
