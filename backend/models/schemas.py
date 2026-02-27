from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class OptimizeResponse(BaseModel):
    status: str
    clinics: list[dict[str, Any]]
    villages: list[dict[str, Any]]
    resources: dict[str, int]


class LocationUpdate(BaseModel):
    clinic_id: str = Field(..., description="Clinic identifier")
    lat: float
    lng: float


class TrackingEvent(BaseModel):
    clinic_id: str
    lat: float
    lng: float
    current_village: str
    eta_next_stop: int
