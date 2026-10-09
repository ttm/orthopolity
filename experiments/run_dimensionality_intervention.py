"""Freeze independent CPU-cost forecasts, measure runtime allocation, and audit."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random


ROOT=Path(__file__).resolve().parents[1]


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path,value):
    Path(path).write_text(json.dumps(value,indent=2,allow_nan=False)+"\n")


def sources():
    return [{"path":str(path.relative_to(ROOT)),"sha256":digest(path)} for path in
        (Path(__file__),ROOT/"src/orthopolity/dimensionality_intervention.py",ROOT/"src/orthopolity/figures.py")]


def audit(config_path,directory,output):
    plan=json.loads((directory/"frozen-plan.json").read_text())
    result=json.loads((output/"study.json").read_text())
    if plan["config_sha256"]!=digest(config_path) or plan["sources"]!=sources():
        raise ValueError("frozen configuration/source changed; preserve this run and use a new identifier")
    checks={"calibration":plan["calibration_sha256"]==digest(directory/"calibration.json"),
        "freeze":result["frozen_plan_sha256"]==digest(directory/"frozen-plan.json"),
        "trials":result["trials_sha256"]==digest(directory/"trials.json"),
        "artifacts":all(digest(ROOT/path)==checksum for path,checksum in result["artifact_sha256"].items())}
    if not all(checks.values()):raise ValueError("retained runtime run failed hash audit: "+repr(checks))
    print(json.dumps(dict(action="audited_existing_actual_run_without_new_measurements",run_id=plan["run_id"],checks=checks),indent=2))
    return result


def freeze(config,config_path,directory):
    from orthopolity.dimensionality_intervention import calibrate,calibration_summary,profile_predictions,runtime_metadata,validate_config
    validate_config(config)
    path=directory/"frozen-plan.json"
    if path.exists():
        plan=json.loads(path.read_text())
        if plan["config_sha256"]!=digest(config_path) or plan["sources"]!=sources() or plan["calibration_sha256"]!=digest(directory/"calibration.json"):
            raise ValueError("existing independent-cost freeze inputs changed")
        return plan
    if (directory/"trials.json").exists() or (directory/"calibration.json").exists():
        raise ValueError("an incomplete attempt already exists; preserve it and use a new run directory")
    environment=runtime_metadata()
    if not environment["gil_enabled"] or environment["implementation"]!="CPython":
        raise RuntimeError("this experiment needs a verified GIL-enabled CPython runtime")
    specification=dict(run_id=config["run_id"],config_reference=str(config_path.relative_to(ROOT)),
        config=config,config_sha256=digest(config_path),sources=sources(),started_utc=utc_now(),
        hardware_metadata=environment,seeds=dict(base=config["seed"],cost_bootstrap=config["seed"]+10000,
            worker_order={kernel:{condition:[config["seed"]+3000+100*r+10*ki+ci
                for r in range(config["trial_replicates_per_condition"])]
                for ci,condition in enumerate(config["conditions"])} for ki,kernel in enumerate(config["kernels"])}))
    archive=directory/"original-sources"
    archived=[]
    for source in specification["sources"]:
        destination=archive/source["path"]
        destination.parent.mkdir(parents=True,exist_ok=True)
        destination.write_bytes((ROOT/source["path"]).read_bytes())
        archived.append(dict(path=str(destination.relative_to(ROOT)),sha256=digest(destination)))
    (directory/"original-config.json").write_bytes(config_path.read_bytes())
    specification["original_source_snapshots"]=archived
    specification["original_configuration_snapshot"]=str((directory/"original-config.json").relative_to(ROOT))
    write_json(directory/"study-specification.json",specification)
    rows=calibrate(config)
    write_json(directory/"calibration.json",rows)
    summary=calibration_summary(rows,config)
    forecasts={kernel:{name:profile_predictions(config["sizes"],config["log_bin_edges"],
        summary[kernel]["q_cpu_seconds"],counts,cost_degree=summary[kernel]["independently_measured_cost_fit"]["degree"])
        for name,counts in config["conditions"].items()} for kernel in config["kernels"]}
    plan=dict(specification,frozen_utc=utc_now(),calibration_sha256=digest(directory/"calibration.json"),
        independent_cost_calibration=summary,forecasts=forecasts,
        exposure=dict(seconds_per_trial=config["trial_seconds"],replicates_per_condition=config["trial_replicates_per_condition"],
            process_count=1,runnable_threads_per_condition={name:sum(counts) for name,counts in config["conditions"].items()}),
        criteria=dict(cpu_profile_tolerance=config["maximum_absolute_cpu_share_error_tolerance"],
            count_profile_total_variation_tolerance=config["count_total_variation_tolerance"],
            scope="Predeclared engineering tolerances; not a calibrated equivalence or significance test"))
    write_json(path,plan)
    print(json.dumps(dict(action="forecasts_frozen_before_allocation",frozen_utc=plan["frozen_utc"],
        cost_dimensions={kernel:row["independently_measured_cost_fit"]["degree"] for kernel,row in summary.items()},
        intervals={kernel:row["degree_nominal_block_bootstrap_interval"] for kernel,row in summary.items()}),indent=2),flush=True)
    return plan


def validate(plan,directory):
    from orthopolity.dimensionality_intervention import run_trial,runtime_metadata
    config=plan["config"]
    if plan["sources"]!=sources():raise ValueError("sources changed after independent forecast freeze")
    metadata=runtime_metadata()
    for key in ("implementation","python","gil_enabled","switch_interval_seconds","thread_cpu_clock"):
        if metadata[key]!=plan["hardware_metadata"][key]:raise ValueError("runtime changed after freeze")
    path=directory/"trials.json"
    if path.exists():
        raise ValueError("allocation outcomes already exist; audit/reuse the run rather than execute again")
    freeze_hash=digest(directory/"frozen-plan.json")
    trials=[]
    write_json(path,trials)
    try:
        for replicate in range(config["trial_replicates_per_condition"]):
            tasks=[(kernel,condition) for kernel in config["kernels"] for condition in config["conditions"]]
            random.Random(config["seed"]+2000+replicate).shuffle(tasks)
            for order,(kernel,condition) in enumerate(tasks):
                measured=run_trial(kernel,config,config["conditions"][condition],
                    order_seed=plan["seeds"]["worker_order"][kernel][condition][replicate])
                trials.append(dict(measured,split="validation",kernel=kernel,condition=condition,replicate=replicate,
                    order_in_replicate=order,measured_utc=utc_now(),frozen_plan_sha256=freeze_hash))
                write_json(path,trials)
                print(f"Actual {kernel}/{condition}, replicate {replicate+1}; timing_valid={measured['timing_assumptions_satisfied']}",flush=True)
    except BaseException as error:
        write_json(directory/"interrupted-attempt.json",dict(error=repr(error),recorded_utc=utc_now(),
            frozen_plan_sha256=freeze_hash,retained_trials=len(trials)))
        raise
    return trials


def figures(result,output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from orthopolity.figures import save_figure
    config=result["config"];sizes=config["sizes"]
    plt.rcParams.update({"font.family":"DejaVu Sans","font.size":9,"svg.fonttype":"none"})
    fig,axes=plt.subplots(1,2,figsize=(10,4),layout="constrained")
    for ax,kernel in zip(axes,config["kernels"]):
        cost=result["independent_cost_calibration"][kernel]
        for row in cost["raw_block_costs"]:ax.plot(sizes,row,"o-",alpha=.2,color="#34699c",ms=3)
        ax.plot(sizes,cost["q_cpu_seconds"],"ko-",label="Independent mean CPU/job")
        ax.set(xscale="log",yscale="log",xlabel="Matrix side length",ylabel="Measured thread CPU seconds/job",
            title=f"{kernel}: D = {cost['independently_measured_cost_fit']['degree']:.3f}")
        ax.set_xticks(sizes,labels=[str(k) for k in sizes]);ax.minorticks_off();ax.legend(frameon=False,fontsize=8)
        ax.grid(alpha=.2);ax.spines[["top","right"]].set_visible(False)
    fig.suptitle("Measured non-unit CPU cost before all allocation outcomes\nFinite-grid slope; full mean-cost curve supplies the forecast")
    for ext in ("png","svg"):save_figure(fig,output/f"cost-calibration.{ext}",dpi=180)
    plt.close(fig)
    fig,axes=plt.subplots(2,2,figsize=(11,8),layout="constrained")
    for row,kernel in enumerate(config["kernels"]):
        for column,condition in enumerate(config["conditions"]):
            ax=axes[row,column];item=result["profiles"][kernel][condition]
            for trial in item["individual_trial_profiles"]:ax.plot(sizes,trial["measured_cpu_share"],"o-",alpha=.25,color="#30699c",lw=.8)
            ax.plot(sizes,item["measured_cpu_share"],"ko-",label="Measured pooled CPU share")
            for model,color,style,label in [("fair_thread_cpu","#30699c","--","Equal runnable-thread CPU"),
                ("equal_job_service","#bc652a",":","Equal job service"),("equal_active_class_cpu","#698b57","-.","Equal active-class CPU")]:
                ax.plot(sizes,item["forecasts"][model]["cpu_share"],style,color=color,label=label)
            ax.set(xscale="log",ylim=(-.025,1.025),xlabel="Fixed size class",ylabel="Share of all measured worker CPU",title=f"{kernel} / {condition.replace('_',' ')}")
            ax.set_xticks(sizes,labels=[str(k) for k in sizes]);ax.minorticks_off();ax.legend(frameon=False,fontsize=7)
            ax.grid(alpha=.2);ax.spines[["top","right"]].set_visible(False)
    fig.suptitle("Actual runtime allocation and frozen competing predictions\nAll partial-job and loop CPU retained; individual trials are shown")
    for ext in ("png","svg"):save_figure(fig,output/f"cpu-profiles.{ext}",dpi=180)
    plt.close(fig)
    fig,axes=plt.subplots(2,2,figsize=(11,8),layout="constrained")
    for row,kernel in enumerate(config["kernels"]):
        for column,condition in enumerate(config["conditions"]):
            ax=axes[row,column];item=result["profiles"][kernel][condition]
            ax.plot(sizes,item["count_share"],"ko-",label="Actual completed jobs")
            for model,color,style,label in [("fair_thread_cpu","#30699c","--","Measured full cost + fair CPU"),
                ("power_cost_fair_cpu","#885aa0","-.","Independent cost-degree approximation"),
                ("unit_cost_fair_cpu","#bc652a",":","Unit cost-degree alternative")]:
                ax.plot(sizes,item["forecasts"][model]["count_share"],style,color=color,label=label)
            ax.set(xscale="log",ylim=(-.025,1.025),xlabel="Fixed size class",ylabel="Share of all completed jobs",title=f"{kernel} / {condition.replace('_',' ')}")
            ax.set_xticks(sizes,labels=[str(k) for k in sizes]);ax.minorticks_off();ax.legend(frameon=False,fontsize=7)
            ax.grid(alpha=.2);ax.spines[["top","right"]].set_visible(False)
    fig.suptitle("Prospective completed-job profiles from independent costs\nCounts condition on observed total jobs; missing classes remain zero")
    for ext in ("png","svg"):save_figure(fig,output/f"count-profiles.{ext}",dpi=180)
    plt.close(fig)


def analyse(plan,directory,output):
    from orthopolity.dimensionality_intervention import summarize_trials
    config=plan["config"];trials=json.loads((directory/"trials.json").read_text())
    freeze_hash=digest(directory/"frozen-plan.json")
    expected={(kernel,condition,r) for kernel in config["kernels"] for condition in config["conditions"] for r in range(config["trial_replicates_per_condition"])}
    if len(trials)!=len(expected) or {(t["kernel"],t["condition"],t["replicate"]) for t in trials}!=expected:
        raise ValueError("all predeclared runtime allocation trials are required")
    if any(t["frozen_plan_sha256"]!=freeze_hash for t in trials):raise ValueError("trial references a different freeze")
    profiles={};contrasts={}
    for kernel in config["kernels"]:
        q=plan["independent_cost_calibration"][kernel]["q_cpu_seconds"]
        profiles[kernel]={}
        for condition,counts in config["conditions"].items():
            selected=[t for t in trials if t["kernel"]==kernel and t["condition"]==condition]
            predicted=plan["forecasts"][kernel][condition]
            summary=summarize_trials(selected,config,q,predicted,counts)
            summary["individual_trial_profiles"]=[summarize_trials([trial],config,q,predicted,counts) for trial in selected]
            summary["timing_valid_trials"]=sum(t["timing_assumptions_satisfied"] for t in selected)
            profiles[kernel][condition]=summary
        base,restricted=profiles[kernel]["equal_threads"],profiles[kernel]["restricted_classes"]
        actual=[b-a for a,b in zip(base["measured_cpu_share"],restricted["measured_cpu_share"])]
        predicted=[b-a for a,b in zip(base["forecasts"]["fair_thread_cpu"]["cpu_share"],restricted["forecasts"]["fair_thread_cpu"]["cpu_share"])]
        contrasts[kernel]=dict(observed_cpu_share_change=actual,frozen_predicted_cpu_share_change=predicted,
            maximum_absolute_change_error=max(abs(a-b) for a,b in zip(actual,predicted)))
    result=dict(run_id=plan["run_id"],kind="actual_cpython_runtime_allocation_with_independent_nonunit_costs",
        config_reference=plan["config_reference"],config=config,sources=plan["sources"],seeds=plan["seeds"],
        hardware_metadata=plan["hardware_metadata"],frozen_utc=plan["frozen_utc"],analysed_utc=utc_now(),
        frozen_plan_sha256=freeze_hash,calibration_sha256=plan["calibration_sha256"],trials_sha256=digest(directory/"trials.json"),
        independent_cost_calibration=plan["independent_cost_calibration"],profiles=profiles,contrasts=contrasts,
        accounting=dict(allocation_trials=len(trials),worker_records=sum(len(t["workers"]) for t in trials),
            calibration_completed_jobs=config["calibration_blocks"]*len(config["kernels"])*len(config["sizes"])*config["calibration_jobs_per_block"],
            completed_validation_jobs=sum(r["completed_jobs"] for t in trials for r in t["workers"]),
            censored_partial_jobs=sum(r["censored_partial_jobs"] for t in trials for r in t["workers"]),
            measured_worker_cpu_seconds=sum(t["worker_cpu_seconds"] for t in trials),
            enclosing_process_cpu_seconds=sum(t["process_control_envelope_cpu_seconds"] for t in trials),
            unassigned_process_cpu_seconds=sum(t["unassigned_process_cpu_seconds"] for t in trials)),
        conclusion_scope="Actual allocation and cost transfer under an engineered GIL/OS mechanism; no resource law for Nature, exact fairness guarantee, continuous tail exponent, or input-count dimension is identified")
    figures(result,output)
    result["artifact_sha256"]={str(path.relative_to(ROOT)):digest(path) for path in sorted(output.iterdir()) if path.suffix in (".png",".svg")}
    write_json(output/"study.json",result)
    print(json.dumps(dict(cost_dimensions={k:r["independently_measured_cost_fit"]["degree"] for k,r in result["independent_cost_calibration"].items()},
        errors={k:{c:r["errors"]["fair_thread_cpu"] for c,r in rows.items()} for k,rows in profiles.items()},contrasts=contrasts),indent=2),flush=True)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config",type=Path,default=ROOT/"configs/dimensionality_intervention_2026-10-02.json")
    parser.add_argument("--directory",type=Path,default=ROOT/"data/dimensionality-intervention/2026-10-02")
    parser.add_argument("--output",type=Path,default=ROOT/"results/dimensionality-intervention")
    parser.add_argument("--stage",choices=("freeze","validate","analyse","audit","all"),default="all")
    args=parser.parse_args();config=json.loads(args.config.read_text())
    args.directory.mkdir(parents=True,exist_ok=True);args.output.mkdir(parents=True,exist_ok=True)
    if args.stage=="audit" or (args.stage=="all" and (args.output/"study.json").exists()):
        audit(args.config,args.directory,args.output);return
    plan=freeze(config,args.config,args.directory)
    if args.stage in ("validate","all"):validate(plan,args.directory)
    if args.stage in ("analyse","all"):analyse(plan,args.directory,args.output)


if __name__=="__main__":main()
