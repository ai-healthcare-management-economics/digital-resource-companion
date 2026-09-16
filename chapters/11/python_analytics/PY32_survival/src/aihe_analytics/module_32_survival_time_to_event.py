from __future__ import annotations
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import chi2
from .io import ensure_output_dir, read_sheet, require_columns, write_metadata
from .plotting import save_figure

def _km(group):
    g=group.sort_values("duration")
    times=np.sort(g.loc[g["event"].astype(int)==1,"duration"].unique())
    surv=1.0;rows=[{"time":0.0,"survival":1.0,"at_risk":len(g),"events":0}]
    for t in times:
        at_risk=int((g["duration"]>=t).sum())
        events=int(((g["duration"]==t)&(g["event"].astype(int)==1)).sum())
        if at_risk>0: surv*=1-events/at_risk
        rows.append({"time":float(t),"survival":surv,"at_risk":at_risk,"events":events})
    return pd.DataFrame(rows)

def _logrank(a,b):
    event_times=np.sort(pd.concat([a.loc[a.event==1,"duration"],b.loc[b.event==1,"duration"]]).unique())
    o1=e1=var=0.0
    for t in event_times:
        n1=(a.duration>=t).sum();n2=(b.duration>=t).sum();n=n1+n2
        d1=((a.duration==t)&(a.event==1)).sum();d2=((b.duration==t)&(b.event==1)).sum();d=d1+d2
        if n>1:
            exp=d*n1/n
            v=(n1*n2*d*(n-d))/(n**2*(n-1))
            o1+=d1;e1+=exp;var+=v
    stat=(o1-e1)**2/var if var>0 else 0
    return stat,1-chi2.cdf(stat,1)

def run_analysis(input_path: Path, output_dir: Path, seed: int = 2026) -> dict:
    out=ensure_output_dir(output_dir)
    d=read_sheet(input_path,"Data");require_columns(d,["patient_id","duration","event","group"],"Data")
    groups=d["group"].drop_duplicates().tolist()
    if len(groups)!=2: raise ValueError("This beginner example requires exactly two groups.")
    curves=[]
    fig,ax=plt.subplots(figsize=(8,5))
    medians={}
    for name,g in d.groupby("group"):
        curve=_km(g);curve["group"]=name;curves.append(curve)
        ax.step(curve["time"],curve["survival"],where="post",label=str(name))
        below=curve[curve["survival"]<=.5]
        medians[str(name)]=None if below.empty else float(below.iloc[0]["time"])
    curves_df=pd.concat(curves,ignore_index=True);curves_df.to_csv(out/"kaplan_meier_estimates.csv",index=False)
    ax.set_xlabel("Time");ax.set_ylabel("Survival probability");ax.set_ylim(0,1.02);ax.set_title("Kaplan-Meier survival curves");ax.legend()
    save_figure(fig,out/"kaplan_meier.png")
    a=d[d["group"]==groups[0]];b=d[d["group"]==groups[1]]
    stat,p=_logrank(a,b)
    payload={"groups":[str(x) for x in groups],"median_survival":medians,"logrank_statistic":float(stat),"logrank_p_value":float(p)}
    (out/"summary.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
    write_metadata(out,"32_survival_time_to_event",input_path,payload)
    return payload
