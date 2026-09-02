"""AIHE-PY38 - Circularity-adjusted evaluation of an AI-assisted remote diagnostic pathway
Digital Resource Companion V1.0. Synthetic demonstration only.
"""
from __future__ import annotations

def pathway_value(health_nmb: float, lifecycle_cost: float, monetized_environmental_effect: float, residual_value: float, resilience_value: float) -> float:
    return health_nmb-lifecycle_cost+monetized_environmental_effect+residual_value+resilience_value

def double_count_check(items: list[dict[str,object]]) -> list[str]:
    seen={}; issues=[]
    for item in items:
        key=str(item.get("effect_id"))
        if key in seen: issues.append(f"Potential double count: {key} in {seen[key]} and {item.get('category')}")
        seen[key]=item.get("category")
    return issues

if __name__ == "__main__":
    options={"regional_remote":pathway_value(410000,275000,-18000,25000,45000),"local_only":pathway_value(360000,300000,-12000,18000,70000)}; print({"options":options,"preferred":max(options,key=options.get),"non_monetized":["equity of effective access","intertemporal burden transfer"]})
