"""A new-year solar forecast with declared resource-profile eligibility gates."""
import numpy as np

from orthopolity.solar_resource_transfer import (
    RESOURCES, MODELS, fixed_edges, pooled_edges, catalogue, membership,
    monthly_statistics, aggregate, forecast, bootstrap, profile_rows, analysis_summary,
)


def development(raw_directory, config):
    fine_edges = fixed_edges(config)
    rows = catalogue(raw_directory, config["training_years"], fine_edges)
    fine_statistics = {resource: monthly_statistics(rows, resource, fine_edges, config["training_years"])
                       for resource in RESOURCES}
    counts = [aggregate(fine_statistics[resource])["counts"] for resource in RESOURCES]
    edges = pooled_edges(counts, fine_edges, config["minimum_training_events_per_resource_per_pooled_bin"])
    rows = catalogue(raw_directory, config["training_years"], edges)
    statistics = {resource: monthly_statistics(rows, resource, edges, config["training_years"])
                  for resource in RESOURCES}
    predictions = {resource: forecast(aggregate(statistics[resource])["mean_cost"],
                                     aggregate(statistics[resource])["counts"], edges)
                   for resource in RESOURCES}
    return {"fine_edges": fine_edges, "fine_counts": dict(zip(RESOURCES, counts)),
            "edges": edges, "statistics": statistics, "forecasts": predictions,
            "membership": membership(rows)}


def development_diagnostics(statistics, log_widths):
    result = {}
    widths = np.asarray(log_widths, float)
    for resource, stats in statistics.items():
        totals = np.asarray(stats["resource_sums"], float)
        all_totals = totals.sum(axis=0)
        monthly_share = np.divide(totals, all_totals, out=np.zeros_like(totals), where=all_totals > 0)
        year_counts = []
        year_resource = []
        for i, year in enumerate(stats["years"]):
            count = stats["counts"][12*i:12*(i+1)].sum(axis=0)
            resource_total = totals[12*i:12*(i+1)].sum(axis=0)
            year_counts.append({"year": year, "complete_count": int(count.sum())})
            year_resource.append({"year": year, "total_fluence_J_m2": float(resource_total.sum()),
                                  "resource_share": (resource_total / resource_total.sum()).tolist()})
        phi = (all_totals / all_totals.sum()) / (widths / widths.sum())
        result[resource] = {
            "monthly_vectors": len(totals),
            "largest_month_fraction_by_class": monthly_share.max(axis=0).tolist(),
            "months_with_positive_resource_by_class": np.sum(totals > 0, axis=0).tolist(),
            "training_resource_density_relative_to_domain_mean": phi.tolist(),
            "year_counts": year_counts, "year_resources": year_resource,
            "interpretation": "Diagnostics of observed development support and temporal variability; no inferred physical upper bound or proof of independent exchangeable months.",
        }
    return result


def solar_application_gate(benchmark_gate, diagnostics, config):
    """Freeze suitability separately from validation outcomes and point estimates."""
    return {
        "benchmark_gate": benchmark_gate,
        "development_diagnostics": diagnostics,
        "expected_evaluation_monthly_blocks": 12 * len(config["evaluation_years"]),
        "independent_exchangeable_validation_months_established": False,
        "independent_physical_per_block_resource_bounds_available": False,
        "formal_profile_eligible": False,
        "formal_profile_ineligibility_reason": "This observational solar design does not independently establish the IID/exchangeable-month assumptions of bootstrap bands; no independently defensible physical per-block fluence bound is available. Benchmark success alone cannot establish solar sampling assumptions.",
        "allowed_use": "Frozen forecasts, measured full profiles, cost-transfer diagnostics and explicitly conditional candidate bands; formal neutrality verdict remains unresolved.",
    }


def gate_verdict(candidate, application_gate, *, primary_missing_count=0):
    conditional = candidate.get("centered_bootstrap", {}).get("decision", "unavailable")
    if not application_gate["formal_profile_eligible"]:
        return {"verdict": "unresolved", "reason": application_gate["formal_profile_ineligibility_reason"],
                "conditional_candidate_verdict": conditional}
    if primary_missing_count:
        return {"verdict": "unresolved", "reason": "Primary fluence is missing for eligible peak events; complete-case resource profile cannot establish the all-catalogue claim.",
                "conditional_candidate_verdict": conditional}
    return {"verdict": conditional if conditional != "unavailable" else "unresolved",
            "reason": "Candidate and observation eligibility gates satisfied"}


def evaluate(training, validation_rows, predictions, edges, config):
    evaluation = {resource: monthly_statistics(validation_rows, resource, edges, config["evaluation_years"])
                  for resource in RESOURCES}
    draws, intervals, invalid = bootstrap(training, evaluation, edges,
                                         replicates=config["score_bootstrap_replicates"], seed=config["score_seed"])
    profiles = {resource: profile_rows(training[resource], evaluation[resource], predictions[resource], edges, intervals[resource])
                for resource in RESOURCES}
    summary = analysis_summary(training, evaluation, predictions, draws, invalid)
    for resource, result in summary.items():
        n = result["evaluation_complete_n"]
        for model, scores in result["scores"].items():
            scores["sum_log_predictive_probability"] = -n * scores["count_cross_entropy_nats_per_event"]
        comparison = result["paired_cross_entropy_differences"]["historical_count_shape"]
        interval = comparison["ci"]
        result["paired_count_log_score"] = {
            "historical_minus_log_neutral_sum_log_probability": -n * comparison["value"],
            "historical_minus_log_neutral_nats_per_event": -comparison["value"],
            "nats_per_event_ci": [-interval[1], -interval[0]] if interval[0] is not None else [None, None],
            "interpretation": "Positive favors historical counts. Sum of event-category log forecasts conditional on observed complete-case N; the common multinomial combinatorial term is omitted. Month-bootstrap comparison is a conditional nominal score summary, not an independent-event likelihood-ratio test.",
        }
    return evaluation, draws, profiles, summary
