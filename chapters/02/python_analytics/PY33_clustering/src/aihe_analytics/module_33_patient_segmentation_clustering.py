from __future__ import annotations
from pathlib import Path
import json
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from .io import ensure_output_dir, read_sheet, require_columns, write_metadata
from .plotting import save_figure

def run_analysis(input_path: Path, output_dir: Path, seed: int = 2026) -> dict:
    out=ensure_output_dir(output_dir)
    d=read_sheet(input_path,"Data");params=read_sheet(input_path,"Parameters")
    require_columns(d,["id"],"Data");require_columns(params,["parameter","value"],"Parameters")
    p=dict(zip(params["parameter"].astype(str),params["value"]))
    k=int(p.get("n_clusters",3));numeric=d.drop(columns=["id"]).select_dtypes(include="number")
    if numeric.shape[1]<2: raise ValueError("At least two numeric feature columns are required.")
    x=StandardScaler().fit_transform(numeric)
    model=KMeans(n_clusters=k,n_init=int(p.get("n_init",20)),random_state=seed)
    labels=model.fit_predict(x)
    out_data=d.copy();out_data["cluster"]=labels;out_data.to_csv(out/"cluster_assignments.csv",index=False)
    profiles=out_data.groupby("cluster")[numeric.columns].mean().reset_index()
    profiles["count"]=out_data.groupby("cluster").size().values
    profiles.to_csv(out/"cluster_profiles.csv",index=False)
    pca=PCA(n_components=2,random_state=seed);coords=pca.fit_transform(x)
    fig,ax=plt.subplots(figsize=(8,6))
    for cluster in sorted(set(labels)):
        mask=labels==cluster;ax.scatter(coords[mask,0],coords[mask,1],label=f"Cluster {cluster}",alpha=.7)
    ax.set_xlabel("Principal component 1");ax.set_ylabel("Principal component 2");ax.set_title("Patient/service segments");ax.legend()
    save_figure(fig,out/"cluster_plot.png")
    silhouette=float(silhouette_score(x,labels)) if k>1 and len(d)>k else None
    payload={"n_clusters":k,"silhouette_score":silhouette,"pca_variance_explained":pca.explained_variance_ratio_.tolist()}
    (out/"summary.json").write_text(json.dumps(payload,indent=2),encoding="utf-8")
    write_metadata(out,"33_patient_segmentation_clustering",input_path,payload)
    return payload
