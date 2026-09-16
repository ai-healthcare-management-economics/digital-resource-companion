
from __future__ import annotations
from pathlib import Path
import matplotlib.pyplot as plt
from cycler import cycler
plt.rcParams["axes.prop_cycle"] = cycler(color=["#6B2230", "#BDA477", "#303236", "#877567", "#8A4752", "#D2C3A8"])

def save_figure(fig: plt.Figure, path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(target, dpi=180, bbox_inches="tight")
    plt.close(fig)
