from __future__ import annotations
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import norm, chi2
from .io import ensure_output_dir, read_sheet, require_columns, write_metadata
from .plotting import save_figure

def _pool(d):
    y=d["effect_estimate"].astype(float).to_numpy()
    se=d["standard_error"].astype(float).to_numpy()
    v=se**2;w=1/v
    fixed=np.sum(w*y)/np.sum(w)
    q=np.sum(w*(y-fixed)**2);df=max(len(y)-1,1)
    c=np.sum(w)-np.sum(w**2)/np.sum(w)
    tau2=max(0,(q-df)/c) if c>0 else 0
    wr=1/(v+tau2);random=np.sum(wr*y)/np.sum(wr)
    se_random=np.sqrt(1/np.sum(wr))
    i2=max(0,(q-df)/q)*100 if q>0 else 0
    return {"fixed_effect":fixed,"random_effect":random,"random_se":se_random,
            "ci_low":random-1.96*se_random,"ci_high":random+1.96*se_random,
            "q":q,"q_p":1-chi2.cdf(q,df),"i2_percent":i2,"tau2":tau2,"weights":wr/np.sum(wr)}

def run_analysis(input_path: Path, output_dir: Path, seed: int = 2026) -> dict:
    out=ensure_output_dir(output_dir)
    d=read_sheet(input_path,"Studies")
    require_columns(d,["study_id","author_year","effect_estimate","standard_error","outcome","subgroup"],"Studies")
    if len(d)<2: raise ValueError("At least two studies are required.")
    res=_pool(d)
    s=d.copy();s["ci_low"]=s["effect_estimate"]-1.96*s["standard_error"];s["ci_high"]=s["effect_estimate"]+1.96*s["standard_error"];s["random_weight"]=res.pop("weights")
    s.to_csv(out/"study_effects_and_weights.csv",index=False)
    subgroup_rows=[]
    for subgroup,g in s.groupby("subgroup"):
        if len(g)>=2:
            pr=_pool(g);pr.pop("weights")
            subgroup_rows.append({"subgroup":subgroup,**pr})
    pd.DataFrame(subgroup_rows).to_csv(out/"subgroup_meta_analysis.csv",index=False)
    fig,ax=plt.subplots(figsize=(8,max(5,len(s)*.45)))
    y=np.arange(len(s))
    ax.errorbar(s["effect_estimate"],y,xerr=1.96*s["standard_error"],fmt="o")
    ax.axvline(0,linewidth=1)
    ax.axvline(res["random_effect"],linestyle="--",label="Random-effects pooled")
    ax.set_yticks(y,s["author_year"]);ax.invert_yaxis();ax.set_xlabel("Effect estimate")
    ax.set_title("Forest plot");ax.legend()
    save_figure(fig,out/"forest_plot.png")
    fig,ax=plt.subplots(figsize=(6,6));ax.scatter(s["effect_estimate"],1/s["standard_error"])
    ax.axvline(res["random_effect"],linestyle="--");ax.set_xlabel("Effect estimate");ax.set_ylabel("Precision (1/SE)");ax.set_title("Funnel plot")
    save_figure(fig,out/"funnel_plot.png")
    payload={k:float(v) for k,v in res.items()}
    (out/"summary.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
    write_metadata(out,"30_random_effects_meta_analysis",input_path,payload)
    return payload
