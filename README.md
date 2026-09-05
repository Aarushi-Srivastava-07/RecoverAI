# RecoverAI

RecoverAI is a Razorpay Buildathon 2026 submission concept for safely improving failed subscription payment recovery. It will combine contextual recovery scoring and AI explanations with a deterministic policy layer that controls every bounded action.

## Phase 1 status

This repository currently contains only the application foundation:

- React + Vite + Tailwind client with a connection-status placeholder
- FastAPI health endpoint at `GET /api/health`
- SQLite and SQLAlchemy configuration foundation (no domain models yet)
- Environment and secret-handling examples
- A backend health-check test

No recovery workflow, ML, LLM, Razorpay integration, webhook, audit trail, dashboard metrics, or simulation functionality has been implemented yet.

## Architecture

`Event → Context → ML score → AI recommendation → deterministic policy gate → action executor → audit log → outcome`

The AI layer will be advisory only; it will never receive secrets or execute financial actions. The policy layer will make the final allow/block decision. See [architecture notes](docs/architecture.md).

## Local setup

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The Vite proxy forwards `/api/health` to port 8000.

## Checks

```powershell
cd backend; pytest
cd ../frontend; npm run lint; npm run build
```

## Next phase

Phase 2 will add the SQLAlchemy domain schema and a defensible synthetic failed-payment dataset, with no recovery execution behavior yet.
