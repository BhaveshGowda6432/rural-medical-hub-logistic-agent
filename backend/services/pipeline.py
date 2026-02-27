from __future__ import annotations

import random
from typing import Any

import pandas as pd

from backend.services.allocation import allocate_resources, summarize_clinics
from backend.services.risk_engine import compute_risk_scores
from backend.services.routing import assign_villages, optimize_route


REQUIRED_VILLAGE_COLUMNS = {
    "village_id",
    "name",
    "latitude",
    "longitude",
    "population",
    "road_condition",
}
REQUIRED_OUTBREAK_COLUMNS = {"village_id", "active_cases", "severity", "trend"}
REQUIRED_RESOURCE_COLUMNS = {"resource_type", "total_available"}


def validate_columns(df: pd.DataFrame, required: set[str], name: str) -> None:
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{name} missing columns: {', '.join(sorted(missing))}")


def resources_to_dict(resources_df: pd.DataFrame) -> dict[str, int]:
    return {
        str(row["resource_type"]): int(row["total_available"])
        for row in resources_df.to_dict(orient="records")
    }


def run_optimization(
    villages_df: pd.DataFrame,
    outbreaks_df: pd.DataFrame,
    resources_df: pd.DataFrame,
    hub: tuple[float, float],
) -> dict[str, Any]:
    validate_columns(villages_df, REQUIRED_VILLAGE_COLUMNS, "villages.csv")
    validate_columns(outbreaks_df, REQUIRED_OUTBREAK_COLUMNS, "outbreaks.csv")
    validate_columns(resources_df, REQUIRED_RESOURCE_COLUMNS, "resources.csv")

    merged = villages_df.merge(outbreaks_df, on="village_id", how="left").fillna(0)
    scored = compute_risk_scores(merged)

    resources = resources_to_dict(resources_df)
    clinic_count = max(1, resources.get("mobile_clinics", 1))

    assignments = assign_villages(scored, clinic_count)
    routes = {}
    for clinic, villages in assignments.items():
        route, distance = optimize_route(villages, hub=hub)
        routes[clinic] = {"route": route, "total_distance": distance}

    allocations = allocate_resources(assignments, resources)
    clinics = summarize_clinics(assignments, routes, allocations)

    for clinic in clinics:
        route_points = []
        for v in routes[clinic["clinic_id"]]["route"]:
            route_points.append(
                {
                    "name": v["name"],
                    "latitude": float(v["latitude"]),
                    "longitude": float(v["longitude"]),
                }
            )
        clinic["route_coordinates"] = route_points

    return {
        "status": "ok",
        "villages": scored.to_dict(orient="records"),
        "clinics": clinics,
        "resources": resources,
    }


def generate_mock_data(seed: int = 42) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    random.seed(seed)
    base_lat, base_lng = 20.59, 78.96
    villages = []
    outbreaks = []
    for i in range(15):
        villages.append(
            {
                "village_id": f"V{i+1}",
                "name": f"Village {i+1}",
                "latitude": round(base_lat + random.uniform(-0.6, 0.6), 5),
                "longitude": round(base_lng + random.uniform(-0.6, 0.6), 5),
                "population": random.randint(800, 6000),
                "road_condition": random.choice(["good", "average", "poor"]),
            }
        )
        outbreaks.append(
            {
                "village_id": f"V{i+1}",
                "active_cases": random.randint(5, 250),
                "severity": random.choice(["mild", "moderate", "severe"]),
                "trend": random.choice(["increasing", "stable", "decreasing"]),
            }
        )

    resources = [
        {"resource_type": "doctors", "total_available": 10},
        {"resource_type": "nurses", "total_available": 20},
        {"resource_type": "medicines", "total_available": 1000},
        {"resource_type": "test_kits", "total_available": 500},
        {"resource_type": "vaccines", "total_available": 300},
        {"resource_type": "mobile_clinics", "total_available": 3},
    ]

    return pd.DataFrame(villages), pd.DataFrame(outbreaks), pd.DataFrame(resources)
