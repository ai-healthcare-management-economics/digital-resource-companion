"""AIHE-PY15 - Probabilistic analysis, value of information, EVSI, and expected net benefit of sampling
Digital Resource Companion V1.0. Synthetic demonstration only.
"""
from __future__ import annotations

import random

def psa(iterations: int=5000, seed: int=23) -> dict[str,float]:
    rng=random.Random(seed); gains=[]
    for _ in range(iterations):
        effect=max(0,rng.gauss(8.0,1.6)); cost=max(0,rng.gauss(150000,25000)); gains.append(30000*effect-cost)
    evpi=sum(max(0,x) for x in gains)/iterations-max(0,sum(gains)/iterations)
    return {"mean_incremental_nmb":sum(gains)/iterations,"probability_cost_effective":sum(x>0 for x in gains)/iterations,"evpi_per_decision":evpi}

def expected_net_benefit_of_sampling(evsi: float, affected_decisions: int, research_cost: float, delay_cost: float) -> float:
    return evsi*affected_decisions-research_cost-delay_cost

if __name__ == "__main__":
    out=psa(); out["enbs"]=expected_net_benefit_of_sampling(420,600,120000,35000); print(out)
