"""AIHE-PY11 - Financial recognition, NPV, ROI, payback, and benefit-realization analysis
Digital Resource Companion V1.0. Synthetic demonstration only.
"""
from __future__ import annotations

def npv(cash_flows: list[float], discount_rate: float) -> float:
    return sum(value / ((1 + discount_rate) ** year) for year, value in enumerate(cash_flows))

def recognize_capacity(hours_released: float, cashable_fraction: float, hourly_cost: float) -> dict[str,float]:
    cashable_hours=max(0.0,min(hours_released,hours_released*cashable_fraction))
    return {"released_hours":hours_released,"cashable_hours":cashable_hours,"recognized_cash_benefit":cashable_hours*hourly_cost}

if __name__ == "__main__":
    benefits=recognize_capacity(2000,0.15,85)
    flows=[-180000,benefits["recognized_cash_benefit"]+60000,benefits["recognized_cash_benefit"]+85000]
    print({**benefits,"npv":npv(flows,0.035),"roi":(sum(flows[1:])-180000)/180000})
