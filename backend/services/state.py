from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd


@dataclass
class AppState:
    villages_df: pd.DataFrame | None = None
    outbreaks_df: pd.DataFrame | None = None
    resources_df: pd.DataFrame | None = None
    merged_df: pd.DataFrame | None = None
    optimization_result: dict[str, Any] | None = None
    location_state: dict[str, dict[str, Any]] = field(default_factory=dict)


app_state = AppState()
