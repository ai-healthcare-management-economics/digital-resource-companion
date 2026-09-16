from __future__ import annotations
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from .io import ensure_output_dir, read_sheet, require_columns, write_metadata
from .plotting import save_figure

def run_analysis(input_path: Path, output_dir: Path, seed: int = 2026) -> dict:
    out=ensure_output_dir(output_dir)
    scores=read_sheet(input_path,"Scores");params=read_sheet(input_path,"Parameters")
    require_columns(scores,["vendor","domain","score","weight","evidence_confidence","safeguard_pass","comment"],"Scores")
    require_columns(params,["parameter","value"],"Parameters")
    p=dict(zip(params["parameter"].astype(str),params["value"]))
    min_overall=float(p.get("minimum_overall_score",70));min_domain=float(p.get("minimum_domain_score",40))
    s=scores.copy()
    s["safeguard_pass"]=s["safeguard_pass"].astype(str).str.lower().isin(["true","yes","1","pass"])
    s["weighted_score"]=s["score"]*s["weight"]/100
    s["confidence_adjusted_score"]=s["weighted_score"]*s["evidence_confidence"]
    vendor=s.groupby("vendor",as_index=False).agg(
        weighted_score=("weighted_score","sum"),
        confidence_adjusted_score=("confidence_adjusted_score","sum"),
        safeguards_pass=("safeguard_pass","all"),
        minimum_domain_score=("score","min"))
    vendor["recommendation"]=np.select(
        [
            ~vendor["safeguards_pass"],
            vendor["minimum_domain_score"]<min_domain,
            vendor["confidence_adjusted_score"]>=min_overall
        ],
        ["STOP: mandatory safeguard failed","CONDITIONAL: remediate weak domain","PROCEED / negotiate conditions"],
        default="REVISE OR DELAY"
    )
    vendor=vendor.sort_values("confidence_adjusted_score",ascending=False)
    s.to_csv(out/"domain_scores.csv",index=False);vendor.to_csv(out/"vendor_ranking.csv",index=False)
    pivot=s.pivot(index="vendor",columns="domain",values="score")
    fig,ax=plt.subplots(figsize=(10,6));pivot.T.plot(marker="o",ax=ax)
    ax.set_ylabel("Score");ax.set_ylim(0,100);ax.set_title("Vendor evidence-domain comparison")
    ax.legend(title="Vendor",bbox_to_anchor=(1.02,1),loc="upper left")
    save_figure(fig,out/"vendor_domain_comparison.png")
    best=vendor.iloc[0]
    payload={"top_vendor":str(best["vendor"]),"top_confidence_adjusted_score":float(best["confidence_adjusted_score"]),
             "top_recommendation":str(best["recommendation"])}
    (out/"summary.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
    write_metadata(out,"25_procurement_mcda_scorecard",input_path,payload)
    return payload
