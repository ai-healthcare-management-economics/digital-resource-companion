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
    df=read_sheet(input_path,"Parameters");require_columns(df,["parameter","value"],"Parameters")
    p=dict(zip(df["parameter"].astype(str),df["value"]))
    horizon=float(p.get("horizon_months",36));dt=float(p.get("time_step_months",.25))
    training=float(p.get("initial_training",.2));trust=float(p.get("initial_trust",.4))
    adoption=float(p.get("initial_adoption",.1));capacity=float(p.get("initial_capacity",100))
    train_rate=float(p.get("training_rate",.04));trust_gain=float(p.get("trust_gain",.05))
    trust_loss=float(p.get("trust_loss_from_incidents",.03));incident=float(p.get("incident_rate",.02))
    adoption_rate=float(p.get("adoption_rate",.08));decay=float(p.get("adoption_decay",.02))
    cap_gain=float(p.get("capacity_gain_per_adoption",30));support=float(p.get("support_burden",10))
    times=np.arange(0,horizon+dt,dt);rows=[]
    for t in times:
        realized=adoption*capacity
        rows.append({"month":t,"training":training,"trust":trust,"adoption":adoption,
                     "capacity":capacity,"realized_value_proxy":realized})
        dtraining=train_rate*(1-training)
        dtrust=trust_gain*training*(1-trust)-trust_loss*incident*trust
        dadoption=adoption_rate*trust*training*(1-adoption)-decay*adoption
        dcapacity=cap_gain*adoption-support*adoption
        training=np.clip(training+dtraining*dt,0,1)
        trust=np.clip(trust+dtrust*dt,0,1)
        adoption=np.clip(adoption+dadoption*dt,0,1)
        capacity=max(0,capacity+dcapacity*dt)
    result=pd.DataFrame(rows);result.to_csv(out/"system_dynamics_trajectory.csv",index=False)
    fig,ax=plt.subplots(figsize=(9,5))
    ax.plot(result["month"],result["training"],label="Training")
    ax.plot(result["month"],result["trust"],label="Trust")
    ax.plot(result["month"],result["adoption"],label="Adoption")
    ax.set_xlabel("Month");ax.set_ylabel("Proportion");ax.set_title("Implementation feedback trajectories");ax.legend()
    save_figure(fig,out/"adoption_feedback.png")
    fig,ax=plt.subplots(figsize=(9,5));ax.plot(result["month"],result["capacity"],label="Capacity")
    ax.plot(result["month"],result["realized_value_proxy"],label="Value proxy")
    ax.set_xlabel("Month");ax.set_title("Capacity and realized-value trajectories");ax.legend()
    save_figure(fig,out/"capacity_value.png")
    final=result.iloc[-1]
    payload={"final_training":float(final["training"]),"final_trust":float(final["trust"]),
             "final_adoption":float(final["adoption"]),"final_capacity":float(final["capacity"])}
    (out/"summary.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
    write_metadata(out,"22_system_dynamics_adoption_capacity",input_path,payload)
    return payload
