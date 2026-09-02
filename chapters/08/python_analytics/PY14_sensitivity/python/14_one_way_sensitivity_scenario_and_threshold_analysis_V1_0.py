"""AIHE-PY14 - One-way sensitivity, scenario, and threshold analysis
Digital Resource Companion V1.0. Synthetic demonstration only.
"""
from __future__ import annotations

def net_monetary_benefit(effect: float, cost: float, threshold: float) -> float:
    return threshold * effect - cost

def one_way(base: dict[str,float], ranges: dict[str,tuple[float,float]]) -> list[dict[str,float]]:
    rows=[]
    for name,(low,high) in ranges.items():
        for label,value in (("low",low),("high",high)):
            p=base|{name:value}
            nmb=net_monetary_benefit(p["effect"],p["cost"],p["threshold"])
            rows.append({"parameter":name,"scenario":label,"value":value,"nmb":nmb})
    return rows

if __name__ == "__main__":
    print(one_way({"effect":8.2,"cost":145000,"threshold":30000},{"effect":(5.5,10.0),"cost":(110000,200000),"threshold":(20000,40000)}))
