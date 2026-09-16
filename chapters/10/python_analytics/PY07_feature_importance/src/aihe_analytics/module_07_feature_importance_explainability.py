from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.inspection import PartialDependenceDisplay, permutation_importance
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from .io import ensure_output_dir, read_sheet, require_columns, write_metadata
from .plotting import save_figure

MODULE_ID="07"
FEATURES=["age","comorbidity_index","lab_value","prior_admissions"]

def run_analysis(input_path: Path, output_dir: Path, seed: int = 2026) -> None:
    out=ensure_output_dir(output_dir)
    data=read_sheet(input_path,"Data")
    require_columns(data,["outcome",*FEATURES],"Data")
    X=data[FEATURES].apply(pd.to_numeric,errors="coerce")
    y=pd.to_numeric(data["outcome"],errors="coerce")
    valid=y.notna(); X=X.loc[valid]; y=y.loc[valid].astype(int)
    X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=.3,stratify=y,random_state=seed)
    model=Pipeline([("imputer",SimpleImputer(strategy="median")),("model",RandomForestClassifier(n_estimators=300,min_samples_leaf=5,random_state=seed))])
    model.fit(X_train,y_train)
    auc=roc_auc_score(y_test,model.predict_proba(X_test)[:,1])
    imp=permutation_importance(model,X_test,y_test,scoring="roc_auc",n_repeats=15,random_state=seed)
    imp_df=pd.DataFrame({"feature":FEATURES,"mean_importance":imp.importances_mean,"sd":imp.importances_std}).sort_values("mean_importance",ascending=False)
    imp_df.to_csv(out/"permutation_importance.csv",index=False)
    fig,ax=plt.subplots(figsize=(7.5,4.8))
    p=imp_df.sort_values("mean_importance")
    ax.barh(p["feature"],p["mean_importance"],xerr=p["sd"])
    ax.set_xlabel("Decrease in AUC after permutation")
    ax.set_title("Permutation feature importance")
    save_figure(fig,out/"permutation_importance.png")
    top=str(imp_df.iloc[0]["feature"])
    fig,ax=plt.subplots(figsize=(7,5))
    PartialDependenceDisplay.from_estimator(model,X_test,[top],ax=ax)
    ax.set_title(f"Partial dependence: {top}")
    save_figure(fig,out/"partial_dependence.png")
    summary={"rows_used":int(len(X)),"test_auc":float(auc),"top_feature":top,"top_importance":float(imp_df.iloc[0]["mean_importance"])}
    (out/"summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    write_metadata(out,MODULE_ID,input_path,summary)
    print(pd.Series(summary).to_string())
