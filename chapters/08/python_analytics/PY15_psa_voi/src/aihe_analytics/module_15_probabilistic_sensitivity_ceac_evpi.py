from __future__ import annotations
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from .io import ensure_output_dir, read_sheet, require_columns, write_metadata
from .plotting import save_figure

def run_analysis(input_path: Path, output_dir: Path, seed: int = 2026) -> dict:
    out = ensure_output_dir(output_dir)
    p = read_sheet(input_path, "Parameters")
    require_columns(p, ["parameter","value"], "Parameters")
    params = dict(zip(p["parameter"].astype(str), p["value"]))
    n = int(params.get("n_simulations", 5000))
    mean_cost = float(params.get("mean_incremental_cost", 300))
    sd_cost = float(params.get("sd_incremental_cost", 150))
    mean_eff = float(params.get("mean_incremental_effect", .02))
    sd_eff = float(params.get("sd_incremental_effect", .01))
    corr = float(params.get("correlation", .1))
    max_wtp = float(params.get("max_wtp", 100000))
    n_thresholds = int(params.get("n_thresholds", 41))
    cov = corr*sd_cost*sd_eff
    rng = np.random.default_rng(seed)
    draws = rng.multivariate_normal([mean_cost,mean_eff], [[sd_cost**2,cov],[cov,sd_eff**2]], size=n)
    sim = pd.DataFrame({"incremental_cost":draws[:,0],"incremental_effect":draws[:,1]})
    thresholds = np.linspace(0,max_wtp,n_thresholds)
    rows = []
    for wtp in thresholds:
        inmb = wtp*sim["incremental_effect"]-sim["incremental_cost"]
        ce_prob = float((inmb>0).mean())
        current = max(float(inmb.mean()),0.0)
        perfect = float(np.maximum(inmb,0).mean())
        rows.append({"wtp":wtp,"probability_cost_effective":ce_prob,"evpi_per_patient":perfect-current})
    ceac = pd.DataFrame(rows)
    sim.to_csv(out/"psa_draws.csv", index=False)
    ceac.to_csv(out/"ceac_evpi.csv", index=False)
    fig, ax = plt.subplots(figsize=(6,6))
    ax.scatter(sim["incremental_effect"],sim["incremental_cost"],s=6,alpha=.2)
    ax.axhline(0,linewidth=1); ax.axvline(0,linewidth=1)
    ax.set_xlabel("Incremental effect"); ax.set_ylabel("Incremental cost")
    ax.set_title("Probabilistic cost-effectiveness plane")
    save_figure(fig,out/"psa_cost_effectiveness_plane.png")
    fig, ax = plt.subplots(figsize=(8,5))
    ax.plot(ceac["wtp"],ceac["probability_cost_effective"])
    ax.set_ylim(0,1); ax.set_xlabel("Willingness-to-pay threshold")
    ax.set_ylabel("Probability AI is cost-effective"); ax.set_title("CEAC")
    save_figure(fig,out/"ceac.png")
    fig, ax = plt.subplots(figsize=(8,5))
    ax.plot(ceac["wtp"],ceac["evpi_per_patient"])
    ax.set_xlabel("Willingness-to-pay threshold"); ax.set_ylabel("EVPI per patient")
    ax.set_title("Expected value of perfect information")
    save_figure(fig,out/"evpi.png")
    mid = ceac.iloc[len(ceac)//2]
    payload={"n_simulations":n,"seed":seed,"probability_cost_effective_at_mid_threshold":float(mid["probability_cost_effective"]),
             "mid_threshold":float(mid["wtp"]),"evpi_at_mid_threshold":float(mid["evpi_per_patient"])}
    (out/"summary.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
    write_metadata(out,"15_probabilistic_sensitivity_ceac_evpi",input_path,payload)
    return payload
