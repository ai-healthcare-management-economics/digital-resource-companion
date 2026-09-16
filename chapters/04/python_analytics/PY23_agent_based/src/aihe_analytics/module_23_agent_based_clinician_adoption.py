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
    agents=read_sheet(input_path,"Agents");params=read_sheet(input_path,"Parameters")
    require_columns(agents,["agent_id","role","adopted","trust","digital_skill","peer_influence","workload"],"Agents")
    require_columns(params,["parameter","value"],"Parameters")
    p=dict(zip(params["parameter"].astype(str),params["value"]))
    periods=int(p.get("periods",24));training=float(p.get("training_effect",.5))
    usefulness=float(p.get("perceived_usefulness",.6));incident_rate=float(p.get("incident_rate",.03))
    incident_penalty=float(p.get("incident_penalty",.35));rng=np.random.default_rng(seed)
    state=agents.copy();state["adopted"]=state["adopted"].astype(int);rows=[]
    for period in range(periods+1):
        adoption_rate=float(state["adopted"].mean())
        for _,a in state.iterrows():
            rows.append({"period":period,"agent_id":a["agent_id"],"role":a["role"],"adopted":a["adopted"],
                         "trust":a["trust"],"workload":a["workload"]})
        if period==periods: break
        incident=rng.random()<incident_rate
        new=[]
        for i,a in state.iterrows():
            score=-1.2 + training*float(a["digital_skill"]) + usefulness*float(a["trust"])
            score += float(a["peer_influence"])*adoption_rate - .5*float(a["workload"])
            if incident: score-=incident_penalty
            prob=1/(1+np.exp(-score))
            adopted=int(a["adopted"] or rng.random()<prob)
            new.append(adopted)
            state.at[i,"trust"]=np.clip(float(a["trust"])+(.02 if adopted else -.005)-(.08 if incident else 0),0,1)
        state["adopted"]=new
    history=pd.DataFrame(rows);history.to_csv(out/"agent_history.csv",index=False)
    trajectory=history.groupby("period",as_index=False)["adopted"].mean().rename(columns={"adopted":"adoption_rate"})
    role=history[history["period"]==periods].groupby("role",as_index=False)["adopted"].mean().rename(columns={"adopted":"final_adoption_rate"})
    trajectory.to_csv(out/"adoption_trajectory.csv",index=False);role.to_csv(out/"role_summary.csv",index=False)
    fig,ax=plt.subplots(figsize=(8,5));ax.plot(trajectory["period"],trajectory["adoption_rate"],marker="o")
    ax.set_ylim(0,1);ax.set_xlabel("Period");ax.set_ylabel("Adoption rate");ax.set_title("Agent-based adoption trajectory")
    save_figure(fig,out/"adoption_trajectory.png")
    payload={"final_adoption_rate":float(trajectory.iloc[-1]["adoption_rate"]),
             "lowest_adoption_role":str(role.sort_values("final_adoption_rate").iloc[0]["role"])}
    (out/"summary.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
    write_metadata(out,"23_agent_based_clinician_adoption",input_path,payload)
    return payload
