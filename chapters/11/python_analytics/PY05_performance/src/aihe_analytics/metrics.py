
from __future__ import annotations
import numpy as np
import pandas as pd

def safe_divide(a: float, b: float) -> float:
    return float(a / b) if b not in (0, 0.0) else float("nan")

def confusion_metrics(actual, predicted) -> dict[str, float]:
    actual = np.asarray(actual).astype(int)
    predicted = np.asarray(predicted).astype(int)
    tp = int(((actual == 1) & (predicted == 1)).sum())
    tn = int(((actual == 0) & (predicted == 0)).sum())
    fp = int(((actual == 0) & (predicted == 1)).sum())
    fn = int(((actual == 1) & (predicted == 0)).sum())
    return {
        "tp": tp, "tn": tn, "fp": fp, "fn": fn,
        "sensitivity": safe_divide(tp, tp + fn),
        "specificity": safe_divide(tn, tn + fp),
        "ppv": safe_divide(tp, tp + fp),
        "npv": safe_divide(tn, tn + fn),
        "accuracy": safe_divide(tp + tn, tp + tn + fp + fn),
        "selection_rate": safe_divide(tp + fp, tp + tn + fp + fn),
    }

def psi(reference: pd.Series, current: pd.Series, bins: int = 10) -> float:
    ref = pd.to_numeric(pd.Series(reference), errors="coerce").dropna().to_numpy()
    cur = pd.to_numeric(pd.Series(current), errors="coerce").dropna().to_numpy()
    if len(ref) < 5 or len(cur) < 5:
        return float("nan")
    edges = np.unique(np.quantile(ref, np.linspace(0, 1, bins + 1)))
    if len(edges) < 3:
        return 0.0
    ref_hist, _ = np.histogram(ref, bins=edges)
    cur_hist, _ = np.histogram(cur, bins=edges)
    ref_pct = np.clip(ref_hist / max(ref_hist.sum(), 1), 1e-6, None)
    cur_pct = np.clip(cur_hist / max(cur_hist.sum(), 1), 1e-6, None)
    return float(np.sum((cur_pct - ref_pct) * np.log(cur_pct / ref_pct)))
