# Rural Medical Hub Logistic Agent

Full-stack hackathon-ready web app for rural health-camp routing, prioritization, resource allocation, and live clinic tracking.

## Features
- CSV upload for villages, outbreaks, and resources
- Risk scoring engine with configurable weights
- Greedy load-balanced clinic assignment
- Risk-aware route optimization with Haversine distance fallback
- Proportional resource allocation with baseline constraints
- WebSocket live tracking (simulated movement every 2 seconds)
- React + Leaflet operations dashboard
- Export JSON / CSV / print-to-PDF reports
- Mock-data generation fallback when CSV files are unavailable

## Quick Start (Docker)
```bash
docker-compose up --build
```

Frontend: http://localhost:5173
Backend docs: http://localhost:8000/docs

## Quick Start (Local)
### Backend
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## API
- `POST /upload-data` upload 3 CSV files (`villages`, `outbreaks`, `resources`)
- `POST /optimize?use_mock=true|false` run optimization and start simulation
- `GET /results` get latest output
- `POST /update-location` receive real GPS updates
- `WS /ws/locations` stream live clinic locations

## CSV Schemas
### villages.csv
`village_id,name,latitude,longitude,population,road_condition`

### outbreaks.csv
`village_id,active_cases,severity,trend`

### resources.csv
`resource_type,total_available`
