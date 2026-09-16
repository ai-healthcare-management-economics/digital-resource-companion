from __future__ import annotations
from pathlib import Path
import json
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
from .io import ensure_output_dir, read_sheet, require_columns, write_metadata
from .plotting import save_figure

def run_analysis(input_path: Path, output_dir: Path, seed: int = 2026) -> dict:
    out=ensure_output_dir(output_dir)
    d=read_sheet(input_path,"Data")
    require_columns(d,["unit_id","time_period","treated_group","post_period","outcome"],"Data")
    d=d.copy()
    d["treated_group"]=d["treated_group"].astype(int);d["post_period"]=d["post_period"].astype(int)
    covariates=[c for c in d.columns if c not in ["unit_id","time_period","treated_group","post_period","outcome"]]
    formula="outcome ~ treated_group + post_period + treated_group:post_period"
    if covariates:
        formula+=" + "+" + ".join(covariates)
    model=smf.ols(formula,d).fit(cov_type="HC3")
    term="treated_group:post_period"
    coef=pd.DataFrame({"term":model.params.index,"coefficient":model.params.values,
                       "std_error":model.bse.values,"p_value":model.pvalues.values,
                       "ci_low":model.conf_int()[0].values,"ci_high":model.conf_int()[1].values})
    coef.to_csv(out/"did_regression.csv",index=False)
    means=d.groupby(["time_period","treated_group"],as_index=False)["outcome"].mean()
    means.to_csv(out/"group_time_means.csv",index=False)
    fig,ax=plt.subplots(figsize=(9,5))
    for treated,g in means.groupby("treated_group"):
        ax.plot(g["time_period"],g["outcome"],marker="o",label="Intervention" if treated else "Comparison")
    ax.set_xlabel("Time period");ax.set_ylabel("Mean outcome");ax.set_title("Difference-in-differences trends");ax.legend()
    save_figure(fig,out/"did_trends.png")
    payload={"did_estimate":float(model.params[term]),"standard_error":float(model.bse[term]),
             "p_value":float(model.pvalues[term]),"r_squared":float(model.rsquared)}
    (out/"summary.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
    write_metadata(out,"31_difference_in_differences",input_path,payload)
    return payload
