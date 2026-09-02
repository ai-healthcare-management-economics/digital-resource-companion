from __future__ import annotations
from pathlib import Path
import heapq, json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from .io import ensure_output_dir, read_sheet, require_columns, write_metadata
from .plotting import save_figure

def _simulate(arrival_rate,service_rate,servers,hours,priority_accuracy,rng):
    horizon=hours*60
    arrivals=[];t=0.0;sequence=0
    while t<horizon:
        t+=rng.exponential(60/arrival_rate)
        if t<horizon:
            urgent=bool(rng.random()<.2)
            predicted_urgent=urgent if rng.random()<priority_accuracy else (not urgent)
            arrivals.append((t,urgent,predicted_urgent,sequence))
            sequence+=1
    i=0;time=0.0;busy=0
    waiting=[]          # (priority, sequence, arrival_time, urgent)
    completions=[]      # (completion_time, sequence, arrival_time, urgent, start_time, service_time)
    waits=[];urgent_waits=[];busy_minutes=0.0;throughput=0
    while i<len(arrivals) or completions or waiting:
        next_arrival=arrivals[i][0] if i<len(arrivals) else float("inf")
        next_completion=completions[0][0] if completions else float("inf")
        if next_arrival<=next_completion:
            time=next_arrival
            while i<len(arrivals) and arrivals[i][0]==time:
                arrival,urgent,predicted,seq=arrivals[i]
                heapq.heappush(waiting,(0 if predicted else 1,seq,arrival,urgent))
                i+=1
        else:
            time=next_completion
            while completions and completions[0][0]==time:
                end,seq,arrival,urgent,start,service=heapq.heappop(completions)
                busy-=1
                if end<=horizon: throughput+=1
                if start<horizon:
                    busy_minutes+=max(0.0,min(end,horizon)-start)
        while busy<servers and waiting:
            priority,seq,arrival,urgent=heapq.heappop(waiting)
            start=max(time,arrival)
            wait=start-arrival
            service=float(rng.exponential(60/service_rate))
            end=start+service
            heapq.heappush(completions,(end,seq,arrival,urgent,start,service))
            busy+=1
            waits.append(wait)
            if urgent: urgent_waits.append(wait)
    utilization=busy_minutes/(servers*horizon) if servers*horizon else 0
    return {"arrivals":len(arrivals),"throughput":throughput,
            "mean_wait_minutes":float(np.mean(waits) if waits else 0),
            "p90_wait_minutes":float(np.percentile(waits,90) if waits else 0),
            "urgent_mean_wait_minutes":float(np.mean(urgent_waits) if urgent_waits else 0),
            "utilization_proxy":float(np.clip(utilization,0,1))}

def run_analysis(input_path: Path, output_dir: Path, seed: int = 2026) -> dict:
    out=ensure_output_dir(output_dir)
    scenarios=read_sheet(input_path,"Scenarios");params=read_sheet(input_path,"Parameters")
    require_columns(scenarios,["scenario","arrival_rate_per_hour","service_rate_per_hour","servers","priority_accuracy","operating_hours"],"Scenarios")
    require_columns(params,["parameter","value"],"Parameters")
    p=dict(zip(params["parameter"].astype(str),params["value"]))
    reps=int(p.get("replications",200));delay_cost=float(p.get("cost_per_wait_hour",50))
    rows=[]
    for i,r in scenarios.iterrows():
        for rep in range(reps):
            res=_simulate(float(r["arrival_rate_per_hour"]),float(r["service_rate_per_hour"]),int(r["servers"]),
                          float(r["operating_hours"]),float(r["priority_accuracy"]),np.random.default_rng(seed+i*10000+rep))
            res.update({"scenario":r["scenario"],"replication":rep,
                        "wait_cost":res["mean_wait_minutes"]/60*delay_cost*res["arrivals"]})
            rows.append(res)
    detail=pd.DataFrame(rows)
    summary=detail.groupby("scenario",as_index=False).agg(
        mean_wait=("mean_wait_minutes","mean"),p90_wait=("p90_wait_minutes","mean"),
        urgent_wait=("urgent_mean_wait_minutes","mean"),throughput=("throughput","mean"),
        utilization=("utilization_proxy","mean"),mean_wait_cost=("wait_cost","mean"))
    detail.to_csv(out/"replication_results.csv",index=False);summary.to_csv(out/"scenario_summary.csv",index=False)
    fig,ax=plt.subplots(figsize=(8,5));ax.bar(summary["scenario"],summary["mean_wait"])
    ax.set_ylabel("Mean wait (minutes)");ax.set_title("Hospital-flow simulation comparison");ax.tick_params(axis="x",rotation=30)
    save_figure(fig,out/"mean_wait_by_scenario.png")
    best=summary.sort_values("mean_wait").iloc[0]
    payload={"replications":reps,"best_scenario_by_wait":str(best["scenario"]),
             "best_mean_wait_minutes":float(best["mean_wait"])}
    (out/"summary.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
    write_metadata(out,"21_discrete_event_hospital_flow",input_path,payload)
    return payload
