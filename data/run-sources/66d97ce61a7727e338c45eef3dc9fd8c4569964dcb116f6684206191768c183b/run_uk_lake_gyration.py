"""Run the separately declared UKCEH regional lake-gyration replication.

Commit docs/uk-lake-gyration-protocol-2026-10-09.md and its config before running
on real data. Default input is the pinned, already downloaded UKCEH GeoPackage.
Use --synthetic 2 or --synthetic 2.3 to check simulated worlds without data access.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from orthopolity.goodness_of_fit import fit_powerlaw, powerlaw_gof, sample_powerlaw  # noqa: E402
from orthopolity.lake_geometry import read_ukceh, spatial_grid  # noqa: E402

CONFIG_PATH = ROOT / "configs/uk_lake_gyration_2026-10-09.json"
CONFIG = json.loads(CONFIG_PATH.read_text())


def exponent_decision(ci_iid, ci_block, n, n_blocks, config=CONFIG):
    """Apply the frozen sample gates before interpreting interval agreement."""
    analysis = config["analysis"]
    if (n < analysis["minimum_lakes"] or n_blocks < analysis["minimum_occupied_blocks"]
            or ci_iid is None or ci_block is None):
        return "insufficient"
    band = config["hypothesis"]["equivalence_band"]
    intervals = np.asarray([ci_iid, ci_block], float)
    if intervals.shape != (2, 2) or not np.isfinite(intervals).all() or np.any(intervals[:, 0] > intervals[:, 1]):
        raise ValueError("Two ordered finite intervals required")
    if all(band[0] <= lower and upper <= band[1] for lower, upper in intervals):
        return "supports H_territory"
    if any(upper < band[0] or lower > band[1] for lower, upper in intervals):
        return "against H_territory"
    return "inconclusive"


def analyse(radii_km, centroids_m, config=CONFIG):
    """Fixed selection and two bootstrap intervals, with no adaptive cutoffs."""
    settings = config["analysis"]
    radii = np.asarray(radii_km, float)
    centroids = np.asarray(centroids_m, float)
    if radii.ndim != 1 or centroids.shape != (len(radii), 2) or not np.isfinite(radii).all() or np.any(radii <= 0):
        raise ValueError("Aligned positive finite radii and 2D centroids required")
    lo, hi = settings["rg_range_km"]
    selected = (radii >= lo) & (radii <= hi)
    r = radii[selected]
    cells = spatial_grid(centroids[selected], settings["block_side_m"])
    labels, inverse, counts = np.unique(cells, axis=0, return_inverse=True, return_counts=True)
    n, k = len(r), len(labels)
    out = dict(n_input=len(radii), n_selected=n, n_occupied_blocks=k,
               rg_range_km=[lo, hi], zeta_R=None, iid_ci95=None, block_ci95=None,
               blocks=[dict(easting_index=int(label[0]), northing_index=int(label[1]), n=int(count))
                       for label, count in zip(labels, counts)],
               goodness_of_fit=None,
               uncertainty_note="Iid and occupied-grid-cell resampling intervals; neither models mapping error or guarantees spatial independence.")
    if n >= 2:
        fit = lambda values: fit_powerlaw(values, lo, hi)["params"]["alpha"] - 1
        out["zeta_R"] = fit(r)
        # Independent streams prevent a changed diagnostic from changing intervals.
        streams = np.random.SeedSequence(settings["seed"]).spawn(3)
        iid_rng, block_rng = (np.random.default_rng(stream) for stream in streams[:2])
        draws = [fit(iid_rng.choice(r, n, replace=True)) for _ in range(settings["iid_bootstrap_draws"])]
        out["iid_ci95"] = np.percentile(draws, settings["interval_percentiles"]).tolist()
        if k >= 2:
            groups = [r[inverse == i] for i in range(k)]
            draws = [fit(np.concatenate([groups[i] for i in block_rng.integers(k, size=k)]))
                     for _ in range(settings["block_bootstrap_draws"])]
            out["block_ci95"] = np.percentile(draws, settings["interval_percentiles"]).tolist()
        out["goodness_of_fit"] = powerlaw_gof(r, lo, hi, n_boot=settings["gof_bootstrap_draws"],
                                               seed=int(streams[2].generate_state(1)[0]))
        out["goodness_of_fit"]["interpretation"] = "Descriptive iid diagnostic; spatial dependence prevents treating this as a calibrated spatial significance test."
    out["exponent_verdict"] = exponent_decision(out["iid_ci95"], out["block_ci95"], n, k, config)
    out["qualified_verdict"] = out["exponent_verdict"]
    if out["exponent_verdict"] != "insufficient" and out["goodness_of_fit"]["ruled_out"]:
        out["qualified_verdict"] = "Fitted exponent is descriptive: power-law adequacy fails the iid diagnostic."
    elif out["exponent_verdict"] == "supports H_territory":
        out["qualified_verdict"] = "Conditional agreement with the regional exponent prediction; no evidence of the allocation mechanism from exponent agreement alone."
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / CONFIG["data"]["gpkg_path"])
    parser.add_argument("--output", type=Path, default=ROOT / "results/uk-lake-gyration-2026-10-09.json")
    parser.add_argument("--table-output", type=Path, default=ROOT / "data/derived/ukceh_rg_2026-10-09.csv")
    parser.add_argument("--synthetic", type=float, help="Bounded survival exponent; never opens real data")
    args = parser.parse_args(argv)
    if args.synthetic is not None:
        rng = np.random.default_rng(CONFIG["analysis"]["seed"])
        radii = sample_powerlaw(20000, args.synthetic + 1, 1, 20, rng)
        centroids = np.column_stack((np.arange(len(radii)) % 20 * 100000 + 50000,
                                    np.arange(len(radii)) % 13 * 100000 + 50000))
        out = dict(data_kind="synthetic only", true_zeta_R=args.synthetic, **analyse(radii, centroids))
    else:
        digest = hashlib.sha256(args.input.read_bytes()).hexdigest()
        if digest != CONFIG["data"]["gpkg_sha256"]:
            parser.error("GeoPackage does not match the frozen checksum")
        rows = read_ukceh(args.input)
        if len(rows) != CONFIG["data"]["expected_records"]:
            parser.error("Feature count differs from the frozen source")
        radii = np.array([row["rg_m"] / 1000 for row in rows])
        centroids = [[row["centroid_e_m"], row["centroid_n_m"]] for row in rows]
        out = dict(data_kind="UKCEH regional replication", input_sha256=digest,
                   config_sha256=hashlib.sha256(CONFIG_PATH.read_bytes()).hexdigest(),
                   protocol="docs/uk-lake-gyration-protocol-2026-10-09.md",
                   **analyse(radii, centroids))
        args.table_output.parent.mkdir(parents=True, exist_ok=True)
        with args.table_output.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(out, indent=2, allow_nan=False) + "\n")
    print(json.dumps(out, indent=2, allow_nan=False))
    return out


if __name__ == "__main__":
    main()
