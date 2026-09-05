# RecoverAI

RecoverAI is a Razorpay Buildathon 2026 submission concept for safely improving failed subscription payment recovery. It will combine contextual recovery scoring and AI explanations with a deterministic policy layer that controls every bounded action.

## Current MVP status

This repository currently contains only the application foundation:

- React + Vite + Tailwind client with a connection-status placeholder
- FastAPI health endpoint at `GET /api/health`
- SQLite and SQLAlchemy configuration foundation (no domain models yet)
- Environment and secret-handling examples
- A real local logistic-regression recovery model trained against a 5,000-row synthetic dataset with held-out evaluation
- Deterministic policy controls, idempotent simulated webhook ingestion, bounded demo recovery actions, SQLite audit records, and metrics
- A dashboard that can trigger and display the full simulated recovery workflow

All recovery actions currently run in clearly labelled **DEMO / SIMULATION MODE**. No real Razorpay payment action, customer communication, or LLM integration is implemented.

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

For a live integration, add Razorpay Test Mode credentials server-side, validate webhook signatures, and replace only the simulated executor behind the existing policy gate.
