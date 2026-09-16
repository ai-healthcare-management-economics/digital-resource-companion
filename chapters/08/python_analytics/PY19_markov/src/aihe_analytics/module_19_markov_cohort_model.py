from __future__ import annotations
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from .io import ensure_output_dir, read_sheet, require_columns, write_metadata
from .plotting import save_figure

def _matrix(df, states, name):
    if df.columns[0] != "from_state":
        raise ValueError(f"{name} first column must be 'from_state'.")
    m=df.set_index("from_state").loc[states,states].astype(float).to_numpy()
    if not np.allclose(m.sum(axis=1),1,atol=1e-6):
        raise ValueError(f"Every row in {name} must sum to 1.")
    return m

def _simulate(states_df, matrix, cycles, dr_cost, dr_effect, initial_index, cohort):
    states=states_df["state"].astype(str).tolist()
    dist=np.zeros(len(states));dist[initial_index]=1.0
    rows=[];pv_cost=0.0;pv_qaly=0.0
    for cycle in range(cycles+1):
        cost=float(np.dot(dist,states_df["cost_per_cycle"])) * cohort
        qaly=float(np.dot(dist,states_df["utility"])) * cohort
        pv_cost += cost/((1+dr_cost)**cycle)
        pv_qaly += qaly/((1+dr_effect)**cycle)
        row={"cycle":cycle,"cycle_cost":cost,"cycle_qaly":qaly}
        row.update({state:dist[i] for i,state in enumerate(states)})
        rows.append(row)
        dist=dist@matrix
    return pd.DataFrame(rows),pv_cost,pv_qaly

def run_analysis(input_path: Path, output_dir: Path, seed: int = 2026) -> dict:
    out=ensure_output_dir(output_dir)
    states_df=read_sheet(input_path,"States")
    require_columns(states_df,["state","cost_per_cycle","utility"],"States")
    params=read_sheet(input_path,"Parameters")
    require_columns(params,["parameter","value"],"Parameters")
    p=dict(zip(params["parameter"].astype(str),params["value"]))
    states=states_df["state"].astype(str).tolist()
    usual=_matrix(read_sheet(input_path,"Usual_Transitions"),states,"Usual_Transitions")
    ai=_matrix(read_sheet(input_path,"AI_Transitions"),states,"AI_Transitions")
    cycles=int(p.get("cycles",10)); drc=float(p.get("discount_rate_cost",.03)); dre=float(p.get("discount_rate_effect",.03))
    cohort=float(p.get("cohort_size",1000)); initial=str(p.get("initial_state",states[0]))
    wtp=float(p.get("willingness_to_pay",50000))
    if initial not in states: raise ValueError(f"initial_state must be one of {states}")
    u,uc,uq=_simulate(states_df,usual,cycles,drc,dre,states.index(initial),cohort)
    a,ac,aq=_simulate(states_df,ai,cycles,drc,dre,states.index(initial),cohort)
    u.to_csv(out/"usual_care_trace.csv",index=False);a.to_csv(out/"ai_trace.csv",index=False)
    dc=ac-uc;de=aq-uq;icer=dc/de if de!=0 else np.nan;inmb=wtp*de-dc
    summary=pd.DataFrame({"strategy":["Usual care","AI"],"pv_cost":[uc,ac],"pv_qaly":[uq,aq]})
    summary.to_csv(out/"strategy_summary.csv",index=False)
    fig,ax=plt.subplots(figsize=(9,5))
    for state in states:
        ax.plot(a["cycle"],a[state],marker="o",label=state)
    ax.set_xlabel("Cycle");ax.set_ylabel("Proportion of cohort");ax.set_title("AI strategy Markov trace");ax.legend()
    save_figure(fig,out/"ai_markov_trace.png")
    payload={"incremental_cost":float(dc),"incremental_qaly":float(de),
             "icer":None if np.isnan(icer) else float(icer),"incremental_nmb":float(inmb)}
    (out/"summary.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
    write_metadata(out,"19_markov_cohort_model",input_path,payload)
    return payload
