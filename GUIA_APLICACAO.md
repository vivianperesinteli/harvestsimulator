# Deployment & Application Guide — Decision Tree Simulator v3

## Overview

Web-based **agricultural decision support** tool for soybean producers in Mato Grosso, Brazil. The user enters field characteristics and management decisions; the simulator calculates which combination maximises expected productivity, applies six economic decision criteria, runs a Monte Carlo risk analysis, and now surfaces the outputs in a contextual BI Intelligence Dashboard — all quantified in **sc/ha**.

- **Scope:** Summer Soybean · Mato Grosso · Baseline = 60 sc/ha (CONAB Jan/2024)
- **Model:** Decision Tree v7 (Baseline-Adjusted) — additive, 13 nodes + 3 interaction effects
- **Unit:** sc/ha exclusively — no monetary references

---

## Running Locally

### Prerequisites

- Python 3.10+
- Git

### Setup

```bash
# Clone the repository
git clone <repo-url>
cd simulator

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
.venv\Scripts\activate           # Windows PowerShell

# Install dependencies
pip install -r requirements.txt
```

### Start the application

Open **two terminals** in the project root:

```bash
# Terminal 1 — backend (FastAPI)
uvicorn backend.main:app --reload --port 8000

# Terminal 2 — frontend (Streamlit)
streamlit run frontend/app.py
```

Streamlit opens automatically at `http://localhost:8501`.  
Quick login: user `demo` / password `demo123`.

### Environment variables

Copy `.env.example` to `.env` and adjust as needed:

```env
BACKEND_URL=http://localhost:8000
ALLOWED_ORIGINS=http://localhost:8501
```

---

## Architecture

```
simulator/
├── backend/
│   ├── main.py          # FastAPI application + API routes
│   ├── engine.py        # Decision tree + 6 criteria engine
│   ├── monte_carlo.py   # Triangular sampling + ENSO rain sampling
│   ├── learning.py      # Adaptive Bayesian calibration (v3)
│   ├── data.py          # Model data: BASELINE, CONTEXT_NODES, DECISION_NODES, RAIN_PROBS
│   └── models.py        # Pydantic request/response schemas
├── frontend/
│   ├── app.py           # Streamlit entry point + router + sidebar
│   ├── api.py           # HTTP client for backend API
│   ├── auth.py          # Session-based authentication
│   ├── navigation.py    # Page routing helper
│   ├── styles.py        # Global CSS injection
│   └── views/
│       ├── input.py          # Multi-step input form (C1–C7 + D1–D6)
│       ├── results.py        # Simulation results + recommendations
│       ├── dashboard.py      # Waterfall + radar decomposition
│       ├── bi_dashboard.py   # BI layer: historical benchmarks, health monitor (v3)
│       ├── monte_carlo.py    # Monte Carlo configuration + distribution charts
│       ├── adaptive_planner.py # Season learning + what-if explorer (v3)
│       ├── history.py        # Session history + comparison
│       └── explainer.py      # Model methodology explainer
├── data/
│   ├── users.json       # User credentials
│   └── outcomes.json    # Confirmed season outcomes for adaptive learning (v3)
├── tests/               # pytest test suite (21 Monte Carlo tests + engine/API tests)
├── requirements.txt
└── README.md
```

---

## Data Pipeline

```
Field inputs (C1–C7, D1–D6)
        │
        ▼
POST /api/simulate (FastAPI)
        │
        ▼
Decision Tree Engine (engine.py)
  • Evaluates all 27 D1 × D4 × D5 paths
  • Additive adjustments + 3 interaction effects (D2×D5, C4×Rain, D1×ENSO)
  • 6 criteria: Bayes EV, Wald, Maximax, Laplace, Hurwicz, Savage
        │
        ▼
Monte Carlo (monte_carlo.py)
  • D2, D3, D6 → Triangular(min, mode, max)  [2,000 iterations]
  • Rainfall R3–R6 → sampled from P(rain | ENSO)
  • Outputs: mean, std, P5, P95, P(yield < threshold), tornado
        │
        ▼
BI Intelligence Dashboard (bi_dashboard.py)
  • Overlays EV on IMEA/CONAB historical benchmarks
  • Variable health monitor (traffic lights per node)
  • Risk-return quadrant across all 27 paths
  • Season planning calendar
        │
        ▼
Adaptive Planner (learning.py + adaptive_planner.py)
  • User confirms actual yield after harvest
  • System computes mean prediction gap
  • Triangular mode updated proportionally to variance shares
  • Calibrated parameters improve next season's simulation
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/api/nodes` | All node options (C1–C7, D1–D6) |
| POST | `/api/simulate` | Run decision tree for all paths |
| POST | `/api/monte_carlo` | Run Monte Carlo for a specific path |

Interactive docs available at `http://localhost:8000/docs` when running locally.

---

## Running Tests

```bash
pytest tests/ -v
```

The test suite covers: Monte Carlo engine (21 tests), decision criteria, API contracts, authentication, and data consistency.

---

## Deployment (Railway / cloud)

The application is configured for Railway deployment via `railpack.toml`. Set the following environment variables in the Railway dashboard:

```
BACKEND_URL=https://<your-backend-service>.railway.app
ALLOWED_ORIGINS=https://<your-frontend-service>.railway.app
```

See `README.md` for live deployment URLs.

---

## Version History

| Version | Key additions |
|---------|---------------|
| v1 | Decision tree engine, 6 criteria, single-path simulation |
| v2 | Monte Carlo (triangular + ENSO rain sampling), tornado chart, PDF/CSV export |
| v3 | BI Intelligence Dashboard, Variable Health Monitor, Adaptive Planner (Bayesian calibration), What-if Explorer, audit trail |
