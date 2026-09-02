"""AIHE-PY39 - Rebound, induced demand, and spatial/intertemporal burden-transfer analysis
Digital Resource Companion V1.0. Synthetic demonstration only.
"""
from __future__ import annotations

def rebound(base_volume: float, new_volume: float, base_intensity: float, new_intensity: float) -> dict[str,float]:
    before=base_volume*base_intensity; after=new_volume*new_intensity
    engineering_saving=base_volume*(base_intensity-new_intensity)
    realized_saving=before-after
    return {"before_total":before,"after_total":after,"engineering_saving":engineering_saving,"realized_saving":realized_saving,"rebound_amount":engineering_saving-realized_saving}

def burden_transfer(local_change: float, supplier_change: float, future_change: float) -> dict[str,float]:
    return {"local":local_change,"supplier_or_other_location":supplier_change,"future_period":future_change,"net":local_change+supplier_change+future_change}

if __name__ == "__main__": print(rebound(10000,14500,5.0,3.3),burden_transfer(-12000,9000,2500))
