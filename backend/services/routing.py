from __future__ import annotations

import math
from typing import Any

import pandas as pd

EPSILON = 1e-6
ROAD_PENALTY = {"good": 1.0, "average": 1.2, "poor": 1.5}


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lon / 2) ** 2
    )
    return 2 * r * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def assign_villages(scored_df: pd.DataFrame, clinics: int) -> dict[str, list[dict[str, Any]]]:
    assignments: dict[str, list[dict[str, Any]]] = {f"Clinic-{i+1}": [] for i in range(clinics)}
    load_map = {key: 0.0 for key in assignments}

    for row in scored_df.to_dict(orient="records"):
        target = min(load_map, key=load_map.get)
        assignments[target].append(row)
        load_map[target] += row["risk_score"]
    return assignments


def optimize_route(villages: list[dict[str, Any]], hub: tuple[float, float]) -> tuple[list[dict[str, Any]], float]:
    remaining = villages.copy()
    route: list[dict[str, Any]] = []
    total_distance = 0.0
    current = {"latitude": hub[0], "longitude": hub[1], "risk_score": 1.0, "road_condition": "good"}

    while remaining:
        def score(v: dict[str, Any]) -> float:
            distance = haversine_km(current["latitude"], current["longitude"], v["latitude"], v["longitude"])
            penalty = ROAD_PENALTY.get(str(v["road_condition"]).lower(), 1.2)
            return distance * penalty / (float(v["risk_score"]) + EPSILON)

        next_stop = min(remaining, key=score)
        leg_distance = haversine_km(current["latitude"], current["longitude"], next_stop["latitude"], next_stop["longitude"])
        total_distance += leg_distance
        route.append(next_stop)
        current = next_stop
        remaining.remove(next_stop)

    total_distance += haversine_km(current["latitude"], current["longitude"], hub[0], hub[1])
    return route, round(total_distance, 2)
