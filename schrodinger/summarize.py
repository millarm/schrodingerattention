"""Reproducible descriptive Block 4 aggregation."""
from __future__ import annotations
import csv, json, statistics, hashlib
from pathlib import Path
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]

def main() -> None:
    rows=[]; records=[]
    for seed in (11,22,33):
      for mode in ("softmax","schrodinger"):
        base=ROOT/f"execution/results/measured/seed-{seed}/{mode}"
        final=json.loads((base/"final.json").read_text()); records.append((seed,mode,final))
        for condition, metric in final["metrics"].items():
          for op in ("xor","copy"):
            rows.append({"seed":seed,"mode":mode,"condition":condition,"op":op,"accuracy":metric[op],"correct":metric[f"{op}_correct"],"count":metric[f"{op}_count"],"cross_entropy":metric["cross_entropy"]})
    val={}; targets={}; scalars=[]; clocks=[]; interventions=[]; input_hashes={}; ce=[]; equal_time=[]; normal_max={}
    for seed,mode,final in records:
      data=[json.loads(x) for x in (ROOT/f"execution/results/measured/seed-{seed}/{mode}/training.jsonl").read_text().splitlines()]
      for path in (ROOT/f"execution/results/measured/seed-{seed}/{mode}/final.json",ROOT/f"execution/results/measured/seed-{seed}/{mode}/training.jsonl"):
        input_hashes[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
      points=[x for x in data if "validation" in x]
      inv=[x.get("invariants",{}) for x in points]+[final.get("invariants",{})]
      normal_max[f"{seed}-{mode}"]={key:max((item.get(key,0.0) for item in inv),default=0.0) for key in ("hermiticity","unitarity","row")}
      vx=[x["validation"]["validation_seen_d4"]["xor"] for x in points]
      cevals=[r["cross_entropy"] for r in rows if r["seed"]==seed and r["mode"]==mode]
      ce.append({"seed":seed,"mode":mode,"combined_condition_ce_mean":statistics.mean(cevals)})
      val[f"{seed}-{mode}"]=vx[-1]
      targets[f"{seed}-{mode}"]={str(t):next((x["examples"] for x in points if x["validation"]["validation_seen_d4"]["xor"]>=t),None) for t in (.9,.95)}
      scalars.append({"seed":seed,"mode":mode,"dt":final["dt"],"gamma":final["gamma"],"invariants":final["invariants"],"rss":max((x.get("rss_bytes",0) for x in data),default=0)})
      clocks.append({"seed":seed,"mode":mode,"training_seconds":final["training_seconds"],"valid_for_comparison":False})
      if mode=="schrodinger":
        for condition,metric in final["metrics"].items():
          for op in ("xor","copy"):
            interventions.append({"seed":seed,"condition":condition,"op":op,"normal":metric[op],"dt0":final["dt_zero"][condition][op],"drop":metric[op]-final["dt_zero"][condition][op]})
    baseline_val=[v for k,v in val.items() if k.endswith("softmax")]; sa_val=[v for k,v in val.items() if k.endswith("schrodinger")]
    for seed in (11,22,33):
      path=ROOT/f"execution/results/measured/seed-{seed}/equal-time.json"
      if path.exists():
        equal_time.append({"seed":seed,"valid_for_comparison":False,"raw":json.loads(path.read_text())})
        input_hashes[str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
    ce_aggregates=[]
    for mode in ("softmax","schrodinger"):
      values=[x["combined_condition_ce_mean"] for x in ce if x["mode"]==mode]; ce_aggregates.append({"mode":mode,"label":"combined operations/conditions CE","mean":statistics.mean(values),"sample_sd":statistics.stdev(values)})
    summary={"status":"INCONCLUSIVE","guards":{"learning_adequacy":max(statistics.mean(baseline_val),statistics.mean(sa_val))>=.8,"timing_valid":False,"sample_gate_eligible_90":all(x["0.9"] is not None for x in targets.values()),"sample_gate_eligible_95":all(x["0.95"] is not None for x in targets.values())},"reason":["failure-to-learn guard","timing/equal-time invalid due provenance"],"provenance":{"train_attempts":8,"pair_attempts":5,"pair_successes":4,"pair_failures":1,"timing_valid":False,"overwritten_prior_records":"unknown"},"rows":rows,"pairs":[],"validation_targets":targets,"scalars_invariants_rss":scalars,"recorded_clocks_invalid":clocks,"invalid_equal_time":equal_time,"combined_ce_aggregates":ce_aggregates,"interventions":interventions,"input_hashes":input_hashes}
    summary["normal_invariant_maxima"]=normal_max
    for path in (ROOT/"execution/logs/03-run-provenance.md",ROOT/"execution/reviews/03-comparison.md",ROOT/"execution/config.json",ROOT/"execution/experiment_contract.md",ROOT/"schrodinger/summarize.py"):
      summary["input_hashes"][str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
    exact=[value for key,value in normal_max.items() if key.endswith("schrodinger")]
    summary["normal_invariant_maxima_exact_overall"]={key:max(value[key] for value in exact) for key in ("hermiticity","unitarity","row")}
    for condition in sorted({r["condition"] for r in rows}):
      for op in ("xor","copy"):
        base=[r["accuracy"] for r in rows if r["condition"]==condition and r["op"]==op and r["mode"]=="softmax"]; sa=[r["accuracy"] for r in rows if r["condition"]==condition and r["op"]==op and r["mode"]=="schrodinger"]
        dif=[b-a for a,b in zip(base,sa)]
        summary["pairs"].append({"condition":condition,"op":op,"baseline_mean":statistics.mean(base),"baseline_sd":statistics.stdev(base),"schrodinger_mean":statistics.mean(sa),"schrodinger_sd":statistics.stdev(sa),"paired_differences":dif,"paired_difference_mean":statistics.mean(dif),"paired_difference_sd":statistics.stdev(dif),"accuracy_3pp_gate":statistics.mean(dif)>=.03 and sum(x>0 for x in dif)>=2,"copy_veto":op=="copy" and (statistics.mean(dif)<-.02 or min(dif)<-.05)})
    summary["intervention_aggregates"]=[]
    for condition in sorted({x["condition"] for x in interventions}):
      for op in ("xor","copy"):
        drops=[x["drop"] for x in interventions if x["condition"]==condition and x["op"]==op]
        gain=next(x["paired_difference_mean"] for x in summary["pairs"] if x["condition"]==condition and x["op"]==op)
        summary["intervention_aggregates"].append({"condition":condition,"op":op,"drop_mean":statistics.mean(drops),"drop_sd":statistics.stdev(drops),"dt0_mean":statistics.mean([x["dt0"] for x in interventions if x["condition"]==condition and x["op"]==op]),"dt0_sd":statistics.stdev([x["dt0"] for x in interventions if x["condition"]==condition and x["op"]==op]),"meaningful_effect":gain>0 and statistics.mean(drops)>=.01 and statistics.mean(drops)>=.5*gain})
    out=ROOT/"execution/results"; (out/"summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True))
    with (out/"summary.csv").open("w",newline="") as f: w=csv.DictWriter(f,fieldnames=rows[0]); w.writeheader(); w.writerows(rows)
    plt.figure(figsize=(8,6)); plt.subplot(2,1,1)
    for seed,mode,final in records:
      data=[json.loads(x) for x in (ROOT/f"execution/results/measured/seed-{seed}/{mode}/training.jsonl").read_text().splitlines()]
      points=[x for x in data if "validation" in x]; plt.plot([x["examples"] for x in points],[x["validation"]["validation_seen_d4"]["xor"] for x in points],label=f"{mode}-{seed}")
    plt.xlabel("training examples"); plt.ylabel("validation XOR accuracy"); plt.legend(fontsize=6); plt.subplot(2,1,2)
    for seed,mode,final in records:
      data=[json.loads(x) for x in (ROOT/f"execution/results/measured/seed-{seed}/{mode}/training.jsonl").read_text().splitlines()]; points=[x for x in data if "validation" in x]; plt.plot([x["examples"] for x in points],[x["validation"]["validation_seen_d4"]["cross_entropy"] for x in points],label=f"{mode}-{seed}")
    plt.xlabel("training examples"); plt.ylabel("validation CE"); plt.tight_layout(); plt.savefig(out/"learning_curves.png",dpi=160); plt.close()
    (out/"summary.md").write_text("# Block 4 summary\n\n**INCONCLUSIVE.** Mean validation XOR did not reach 0.80 and timing/equal-time evidence is invalid due duplicate/overlap provenance. Equal-update values are descriptive only; raw clocks are not comparative efficiency evidence.\n")
if __name__ == "__main__": main()
