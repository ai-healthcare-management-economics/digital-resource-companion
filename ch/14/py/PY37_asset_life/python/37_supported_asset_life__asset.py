"""AIHE-PY37 - Supported asset life, eligibility, equivalent annual cost, and residual value
Digital Resource Companion V1.0. Synthetic demonstration only.
"""
from __future__ import annotations

def equivalent_annual_cost(present_value_cost: float, discount_rate: float, supported_years: int) -> float:
    if supported_years<=0: raise ValueError("supported_years must be positive")
    factor=discount_rate*(1+discount_rate)**supported_years/((1+discount_rate)**supported_years-1) if discount_rate else 1/supported_years
    return present_value_cost*factor

def assess_option(eligible: bool, pv_cost: float, residual_value: float, supported_years: int, rate: float) -> dict[str,object]:
    if not eligible: return {"eligible":False,"eac":None,"reason":"Mandatory serviceability requirement not met"}
    return {"eligible":True,"eac":equivalent_annual_cost(pv_cost-residual_value,rate,supported_years)}

if __name__ == "__main__":
    for name,args in {"refurbish":(True,420000,35000,5,.035),"replace":(True,650000,80000,8,.035),"maintain":(False,180000,0,3,.035)}.items(): print(name,assess_option(*args))
