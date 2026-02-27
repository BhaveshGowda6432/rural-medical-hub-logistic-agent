from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from typing import Any

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self.connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.connections:
            self.connections.remove(websocket)

    async def broadcast(self, payload: dict[str, Any]) -> None:
        stale: list[WebSocket] = []
        for connection in self.connections:
            try:
                await connection.send_json(payload)
            except Exception:
                stale.append(connection)
        for connection in stale:
            self.disconnect(connection)


def interpolate_points(
    start: tuple[float, float], end: tuple[float, float], steps: int = 10
) -> list[tuple[float, float]]:
    return [
        (
            start[0] + (end[0] - start[0]) * i / steps,
            start[1] + (end[1] - start[1]) * i / steps,
        )
        for i in range(1, steps + 1)
    ]


async def simulate_clinic_route(
    clinic_id: str,
    villages: list[dict[str, Any]],
    manager: ConnectionManager,
    location_state: dict[str, dict[str, Any]],
) -> AsyncGenerator[dict[str, Any], None]:
    if not villages:
        return

    for idx in range(len(villages) - 1):
        current = villages[idx]
        nxt = villages[idx + 1]
        points = interpolate_points(
            (current["latitude"], current["longitude"]),
            (nxt["latitude"], nxt["longitude"]),
            steps=6,
        )
        for step, (lat, lng) in enumerate(points):
            event = {
                "clinic_id": clinic_id,
                "lat": lat,
                "lng": lng,
                "current_village": current["name"],
                "eta_next_stop": (len(points) - step) * 2,
            }
            location_state[clinic_id] = event
            await manager.broadcast(event)
            yield event
            await asyncio.sleep(2)


async def run_simulation(
    optimized: list[dict[str, Any]], manager: ConnectionManager, location_state: dict[str, dict[str, Any]]
) -> None:
    tasks = []
    for clinic in optimized:
        route_villages = clinic.get("route_coordinates", [])
        tasks.append(simulate_clinic_route(clinic["clinic_id"], route_villages, manager, location_state))

    for task in tasks:
        async for _ in task:
            pass
