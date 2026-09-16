from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, brier_score_loss, roc_auc_score, roc_curve
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from .io import ensure_output_dir, read_sheet, require_columns, write_metadata
from .plotting import save_figure

MODULE_ID = "04"
FEATURES = ["age","comorbidity_index","lab_value","prior_admissions"]

def run_analysis(input_path: Path, output_dir: Path, seed: int = 2026) -> None:
    out = ensure_output_dir(output_dir)
    data = read_sheet(input_path, "Data")
    require_columns(data, ["outcome",*FEATURES], "Data")
    X = data[FEATURES].apply(pd.to_numeric, errors="coerce")
    y = pd.to_numeric(data["outcome"], errors="coerce")
    valid = y.notna()
    X, y = X.loc[valid], y.loc[valid].astype(int)
    if y.nunique() < 2:
        raise ValueError("Outcome must contain both 0 and 1.")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.30, stratify=y, random_state=seed
    )
    models = {
        "Logistic regression": Pipeline([
            ("imputer",SimpleImputer(strategy="median")),
            ("scale",StandardScaler()),
            ("model",LogisticRegression(max_iter=1000, random_state=seed))
        ]),
        "Random forest": Pipeline([
            ("imputer",SimpleImputer(strategy="median")),
            ("model",RandomForestClassifier(n_estimators=250,min_samples_leaf=5,random_state=seed))
        ])
    }

    rows = []
    predictions = pd.DataFrame({"actual":y_test.to_numpy()}, index=y_test.index)
    fig, ax = plt.subplots(figsize=(7.2,5))
    for name, model in models.items():
        model.fit(X_train,y_train)
        score = model.predict_proba(X_test)[:,1]
        pred = (score>=0.5).astype(int)
        auc = roc_auc_score(y_test,score)
        rows.append({"model":name,"auc":auc,"brier_score":brier_score_loss(y_test,score),"accuracy":accuracy_score(y_test,pred)})
        predictions[name.lower().replace(" ","_")+"_score"] = score
        fpr,tpr,_ = roc_curve(y_test,score)
        ax.plot(fpr,tpr,label=f"{name} (AUC={auc:.3f})")
    ax.plot([0,1],[0,1],linestyle="--",label="Chance")
    ax.set_xlabel("False-positive rate"); ax.set_ylabel("True-positive rate")
    ax.set_title("Model discrimination comparison"); ax.legend()
    save_figure(fig,out/"roc_comparison.png")

    logit = models["Logistic regression"].fit(X_train,y_train)
    coefficients = pd.DataFrame({"feature":FEATURES,"standardized_coefficient":logit.named_steps["model"].coef_[0]}).sort_values("standardized_coefficient",key=np.abs,ascending=False)
    forest = models["Random forest"].fit(X_train,y_train)
    importance = pd.DataFrame({"feature":FEATURES,"importance":forest.named_steps["model"].feature_importances_}).sort_values("importance",ascending=False)

    comparison = pd.DataFrame(rows).sort_values("auc",ascending=False)
    comparison.to_csv(out/"model_comparison.csv",index=False)
    predictions.to_csv(out/"test_predictions.csv",index_label="source_row")
    coefficients.to_csv(out/"logistic_coefficients.csv",index=False)
    importance.to_csv(out/"random_forest_importance.csv",index=False)
    summary = {"rows_used":int(len(X)),"test_rows":int(len(X_test)),"best_model":str(comparison.iloc[0]["model"]),"best_auc":float(comparison.iloc[0]["auc"])}
    (out/"summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    write_metadata(out,MODULE_ID,input_path,summary)
    print(comparison.to_string(index=False))
