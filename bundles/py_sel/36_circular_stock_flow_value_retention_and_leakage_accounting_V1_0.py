"""AIHE-PY36 - Circular stock-flow, value-retention, and leakage accounting
Digital Resource Companion V1.0. Synthetic demonstration only.
"""
from __future__ import annotations

def stock_flow(opening: float, inflow: float, reuse_inflow: float, outflow: float, recovery: float) -> dict[str,float]:
    closing=opening+inflow+reuse_inflow-outflow
    leakage=max(0.0,outflow-recovery)
    return {"opening_stock":opening,"closing_stock":closing,"recovered_outflow":recovery,"circular_leakage":leakage}

if __name__ == "__main__": print(stock_flow(120,35,8,28,19))
