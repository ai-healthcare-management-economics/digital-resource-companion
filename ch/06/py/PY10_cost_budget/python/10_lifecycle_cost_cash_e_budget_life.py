"""AIHE-PY10 - Lifecycle cost, cash expenditure, accounting expense, and budget-incidence analysis
Digital Resource Companion V1.0. Synthetic demonstration only.
"""
from __future__ import annotations

from dataclasses import dataclass

@dataclass
class CostItem:
    name: str
    economic_cost: float
    cash_expenditure: float
    accounting_expense: float
    year: int
    budget_holder: str

def summarize(items: list[CostItem]) -> dict[str, float]:
    return {
        "economic_cost": sum(x.economic_cost for x in items),
        "cash_expenditure": sum(x.cash_expenditure for x in items),
        "accounting_expense": sum(x.accounting_expense for x in items),
    }

if __name__ == "__main__":
    demo=[CostItem("Integration",120000,120000,40000,0,"Hospital"),CostItem("Staff time",30000,0,30000,0,"Clinical service"),CostItem("Monitoring",20000,20000,20000,1,"Hospital")]
    print(summarize(demo))
