# RecoverAI architecture

## Phase 1 boundary

The repository is a modular monorepo with a React client and a FastAPI service. The client talks only to `/api` through Vite's local development proxy. FastAPI owns server configuration and database access; its SQLite session foundation is deliberately model-free until the domain schema is introduced.

## Target recovery flow (future phases)

`Webhook/event → contextual data → ML score → LLM recommendation → deterministic policy gate → bounded executor → audit record → outcome and evaluation metrics`

The LLM is advisory only. It will not hold credentials or execute Razorpay calls. Razorpay test-mode work, all recovery actions, webhook processing, ML, audits, and simulations are intentionally out of scope for Phase 1.
