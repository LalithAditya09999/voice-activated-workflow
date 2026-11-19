"""Declarative eligibility rules.

schemes.json entries look like:
  {"id": "pm_kisan", "name": {...}, "benefit": {...}, "service": "pm_kisan",
   "rules": [{"field": "owns_land", "op": "eq", "value": true},
             {"field": "income_tax_payer", "op": "eq", "value": false, "why": {...}}]}

Each scheme comes back as eligible / maybe (a needed answer is missing) / not_eligible,
with the reasons, so the assistant can explain *why* and not just list names.
"""
from __future__ import annotations

from .forms import t

OPS = {
    "eq": lambda a, b: a == b,
    "ne": lambda a, b: a != b,
    "in": lambda a, b: a in b,
    "not_in": lambda a, b: a not in b,
    "lte": lambda a, b: a is not None and a <= b,
    "gte": lambda a, b: a is not None and a >= b,
    "lt": lambda a, b: a is not None and a < b,
    "gt": lambda a, b: a is not None and a > b,
}


def evaluate(schemes: list[dict], profile: dict, lang: str = "en") -> list[dict]:
    results = []
    for s in schemes:
        failed, missing = [], []
        for rule in s.get("rules", []):
            if rule["field"] not in profile:
                missing.append(rule["field"])
                continue
            if not OPS[rule["op"]](profile[rule["field"]], rule["value"]):
                failed.append(t(rule.get("why", {"en": rule["field"]}), lang))
        status = "not_eligible" if failed else ("maybe" if missing else "eligible")
        results.append({
            "id": s["id"],
            "name": t(s["name"], lang),
            "benefit": t(s.get("benefit", ""), lang),
            "service": s.get("service"),
            "status": status,
            "reasons": failed,
            "missing": sorted(set(missing)),
        })
    order = {"eligible": 0, "maybe": 1, "not_eligible": 2}
    results.sort(key=lambda r: order[r["status"]])
    return results
