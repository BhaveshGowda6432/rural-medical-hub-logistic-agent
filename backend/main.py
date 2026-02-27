from __future__ import annotations

import asyncio
from io import StringIO

import pandas as pd
from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from backend.services.pipeline import generate_mock_data, run_optimization
from backend.services.state import app_state
from backend.services.tracking import ConnectionManager, run_simulation

app = FastAPI(title="Rural Medical Hub Logistic Agent")
manager = ConnectionManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _read_csv(upload: UploadFile) -> pd.DataFrame:
    content = upload.file.read().decode("utf-8")
    return pd.read_csv(StringIO(content))


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/upload-data")
async def upload_data(
    villages: UploadFile = File(...), outbreaks: UploadFile = File(...), resources: UploadFile = File(...)
) -> dict[str, str]:
    app_state.villages_df = _read_csv(villages)
    app_state.outbreaks_df = _read_csv(outbreaks)
    app_state.resources_df = _read_csv(resources)
    return {"status": "uploaded"}


@app.post("/optimize")
async def optimize(use_mock: bool = False) -> dict:
    if use_mock or any(df is None for df in [app_state.villages_df, app_state.outbreaks_df, app_state.resources_df]):
        villages_df, outbreaks_df, resources_df = generate_mock_data()
    else:
        villages_df = app_state.villages_df
        outbreaks_df = app_state.outbreaks_df
        resources_df = app_state.resources_df

    app_state.optimization_result = run_optimization(villages_df, outbreaks_df, resources_df, hub=(20.5937, 78.9629))
    asyncio.create_task(run_simulation(app_state.optimization_result["clinics"], manager, app_state.location_state))
    return app_state.optimization_result


@app.get("/results")
def results() -> dict:
    if app_state.optimization_result:
        return app_state.optimization_result
    villages_df, outbreaks_df, resources_df = generate_mock_data()
    app_state.optimization_result = run_optimization(villages_df, outbreaks_df, resources_df, hub=(20.5937, 78.9629))
    return app_state.optimization_result


@app.post("/update-location")
def update_location(payload: dict) -> dict[str, str]:
    clinic_id = str(payload.get("clinic_id", ""))
    if not clinic_id:
        return {"status": "ignored"}
    app_state.location_state[clinic_id] = payload
    return {"status": "updated"}


@app.websocket("/ws/locations")
async def ws_locations(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    try:
        for location in app_state.location_state.values():
            await websocket.send_json(location)
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
