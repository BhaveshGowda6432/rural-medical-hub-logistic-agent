from __future__ import annotations

from typing import Any


def allocate_resources(
    assignments: dict[str, list[dict[str, Any]]], resources: dict[str, int], baseline: int = 1
) -> dict[str, dict[str, int]]:
    clinic_risk = {clinic: sum(v["risk_score"] for v in villages) for clinic, villages in assignments.items()}
    total_risk = sum(clinic_risk.values()) or 1

    alloc: dict[str, dict[str, int]] = {}
    tracked_resources = {k: v for k, v in resources.items() if k != "mobile_clinics"}

    for clinic, risk in clinic_risk.items():
        ratio = risk / total_risk
        alloc[clinic] = {}
        for resource, total in tracked_resources.items():
            assigned = max(baseline, int(total * ratio))
            alloc[clinic][resource] = assigned

    for resource, total in tracked_resources.items():
        assigned_total = sum(alloc[c][resource] for c in alloc)
        if assigned_total > total:
            excess = assigned_total - total
            for clinic in sorted(alloc, key=lambda c: alloc[c][resource], reverse=True):
                take = min(excess, max(0, alloc[clinic][resource] - baseline))
                alloc[clinic][resource] -= take
                excess -= take
                if excess == 0:
                    break

    return alloc


def summarize_clinics(
    assignments: dict[str, list[dict[str, Any]]], routes: dict[str, Any], allocations: dict[str, dict[str, int]]
) -> list[dict[str, Any]]:
    summary: list[dict[str, Any]] = []
    for clinic, villages in assignments.items():
        summary.append(
            {
                "clinic_id": clinic,
                "villages_assigned": [v["name"] for v in villages],
                "route": ["Hub", *[v["name"] for v in routes[clinic]["route"]], "Hub"],
                "total_distance": routes[clinic]["total_distance"],
                "coverage_score": round(sum(v["risk_score"] for v in villages), 3),
                "allocated_resources": allocations[clinic],
            }
        )
    return summary
