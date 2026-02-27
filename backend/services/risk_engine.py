from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class RiskWeights:
    severity: float = 0.35
    cases: float = 0.30
    population: float = 0.20
    road: float = 0.15


SEVERITY_MAP = {"mild": 0.3, "moderate": 0.6, "severe": 1.0}
ROAD_RISK_MAP = {"good": 0.2, "average": 0.5, "poor": 1.0}


def _normalize(series: pd.Series) -> pd.Series:
    max_v = series.max()
    min_v = series.min()
    if max_v == min_v:
        return pd.Series([1.0] * len(series), index=series.index)
    return (series - min_v) / (max_v - min_v)


def compute_risk_scores(df: pd.DataFrame, weights: RiskWeights | None = None) -> pd.DataFrame:
    """Compute normalized risk scores for villages."""
    weights = weights or RiskWeights()
    scored = df.copy()

    scored["severity_score"] = scored["severity"].str.lower().map(SEVERITY_MAP).fillna(0.3)
    scored["road_risk"] = scored["road_condition"].str.lower().map(ROAD_RISK_MAP).fillna(0.5)
    scored["normalized_cases"] = _normalize(scored["active_cases"].fillna(0))
    scored["normalized_population"] = _normalize(scored["population"].fillna(0))

    scored["risk_score"] = (
        weights.severity * scored["severity_score"]
        + weights.cases * scored["normalized_cases"]
        + weights.population * scored["normalized_population"]
        + weights.road * scored["road_risk"]
    )
    return scored.sort_values("risk_score", ascending=False).reset_index(drop=True)
