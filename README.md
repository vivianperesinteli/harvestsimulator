# Harvest Simulator — Soy, Mato Grosso

**Bayer CropScience × Inteli · Module 6 · Group 2**

Web-based agricultural decision support tool for soybean producers in Mato Grosso. The producer enters field conditions and management decisions; the simulator calculates expected yield for each climate scenario, applies 6 economic decision criteria, and estimates the confidence interval via Monte Carlo simulation. v3 adds a BI Intelligence Dashboard with regional benchmarks and variable health monitoring, plus an Adaptive Season Planner that learns from confirmed actual yields to improve model calibration over time.

---

## Live Demo

| Service | URL |
|---|---|
| **App (Streamlit)** | https://empathetic-passion-production.up.railway.app |
| **API (FastAPI)** | https://harvestsimulator-production.up.railway.app |

Login with: **Username:** `demo` · **Password:** `demo123`

---

## Features

### Simulation core
| Feature | Description |
|---|---|
| Payoff Matrix | 27 management combinations × 3 climate scenarios (sc/ha) |
| 6 Decision Criteria | Bayes EV, Wald, Laplace, Hurwicz, Maximax, Savage |
| Interaction Effects | 3 modelled interactions: D2×D5, C4×Rain, D1×ENSO |
| Monte Carlo | 2,000 iterations by default, configurable triangular distributions |
| Risk Analysis | P(yield < threshold), P5/P95, standard deviation |
| Tornado Chart | Pearson correlation + variance share per stochastic variable |
| Alternative Comparison | Your selection vs. optimal path (Bayes EV) — distributions side by side |
| Upgrade Potential | Impact of switching cultivar, seed treatment, or planter |
| Export | PDF (full report) + CSV per recommendation |
| Interactive Explainer | 10-step methodology with formulas and charts |

### BI Intelligence Dashboard *(v3)*
| Feature | Description |
|---|---|
| Regional Benchmark | Your simulated EV vs. IMEA 2023/24 regional productivity reference |
| ENSO Risk Index | Drought probability index (0–100%) derived from NOAA/CPC conditional probabilities |
| Decision Quality Score | 0–100 score: how many of D1–D6 are in their optimal zone |
| Historical Benchmark | Your simulation plotted against CONAB/IMEA MT yields 2018–2024 |
| Variable Health Monitor | Traffic-light status (🟢🟡🔴) for all 13 model nodes in real time |
| Agronomic Vulnerability Score | Composite risk exposure index across all context + decision nodes |
| Active Alerts | Automatic detection of critical combinations (e.g., Late Planting + La Niña → −10.5 sc/ha drag) |
| Risk–Return Map | Scatter of all 27 paths: expected yield (EV) vs. worst case (Wald) |
| Season Calendar | Gantt timeline of the MT soy season with your planting window highlighted |
| Data Pipeline | End-to-end documentation of inputs → processing → outputs |

### Adaptive Season Planner *(v3 — going beyond)*
| Feature | Description |
|---|---|
| Outcome Confirmation | Record actual harvest yield linked to a past simulation |
| Learning Curve | Season-by-season chart of simulated vs. actual, with gap trend |
| Bayesian Calibration | After ≥3 confirmed seasons, triangular distribution modes auto-adjust to your farm's historical pattern |
| What-if Explorer | Override any D1–D6 decision in real time and see the expected yield impact instantly |
| Audit Trail | All confirmed outcomes persisted in `data/outcomes.json` per user |

---

## Monte Carlo — How it works

The simulator treats three key variables as probability distributions rather than fixed values, running thousands of scenarios to produce a distribution of possible outcomes.

### Stochastic inputs

| Variable | Distribution | Range |
|---|---|---|
| D2 · Cultivar | Triangular(min, mode, max) | default: −8, 0, +6 sc/ha |
| D3 · Seed Treatment | Triangular(min, mode, max) | default: −5, 0, +3 sc/ha |
| D6 · Planter | Triangular(min, mode, max) | default: −4, 0, +3 sc/ha |
| Rainfall R3–R6 | Discrete by P(rain\|ENSO) | Dry / Normal / Wet |

### How to configure

In the **How We Calculate** page, set the number of iterations (1,000–10,000) and the risk threshold (sc/ha). The distribution parameters (min, mode, max) for each variable can be adjusted in the expanders. Click **Run Monte Carlo** to execute.

### How to read the output

- **Mean** — average simulated yield across all iterations
- **Std Dev** — spread of the distribution; higher = more uncertainty
- **P5** — in 95% of simulations, yield exceeded this value (worst-case bound)
- **P95** — in 95% of simulations, yield stayed below this value (best-case bound)
- **P(below threshold)** — probability the yield falls below the risk threshold you set
- **Tornado chart** — shows which variable drives the most output variance (Spearman correlation); the longer the bar, the more that variable matters

---

## Requirements

- Python 3.11+
- pip

---

## Local installation and setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Terminal 1 — FastAPI backend (port 8000)
uvicorn backend.main:app --port 8000

# 3. Terminal 2 — Streamlit frontend (port 8501)
streamlit run frontend/app.py
```

Access `http://localhost:8501` and log in with:
- **Username:** `demo`
- **Password:** `demo123`

---

## Environment variables (production)

| Variable | Default | Description |
|---|---|---|
| `BACKEND_URL` | `http://localhost:8000` | FastAPI backend URL |
| `ALLOWED_ORIGINS` | `http://localhost:8501` | Allowed CORS origins (comma-separated) |

---

## Project structure

```
simulator/
├── backend/
│   ├── main.py          # FastAPI — endpoints /health, /api/nodes, /api/simulate, /api/monte_carlo
│   ├── engine.py        # Compute simulation: payoff matrix, criteria, upgrade potential
│   ├── monte_carlo.py   # MC engine: triangular distributions + tornado chart
│   ├── learning.py      # [v3] Bayesian calibration + outcome persistence
│   ├── models.py        # Pydantic models for request/response
│   └── data.py          # Constants: nodes, adjustments, rainfall probabilities
├── frontend/
│   ├── app.py           # Streamlit: authentication + router + sidebar
│   ├── auth.py          # Login/register with PBKDF2-SHA256
│   ├── api.py           # HTTP client for the backend
│   ├── styles.py        # Global CSS (visual identity)
│   ├── navigation.py    # Page router via session_state
│   └── views/
│       ├── input.py            # 3 steps: context → decisions → review
│       ├── results.py          # Recommendations, matrix, criteria, PDF/CSV export
│       ├── results_helpers.py  # Shared labels and text
│       ├── results_pdf.py      # PDF generator (fpdf2)
│       ├── dashboard.py        # Charts: waterfall, radar, bar, sensitivity
│       ├── monte_carlo.py      # Monte Carlo UI with histogram and tornado
│       ├── bi_dashboard.py     # [v3] BI Intelligence Dashboard
│       ├── adaptive_planner.py # [v3] Adaptive Season Planner + What-if Explorer
│       ├── explainer.py        # Interactive explainer — 10 steps
│       └── history.py          # Session simulation history
├── data/
│   ├── users.json        # Users (auto-generated)
│   └── outcomes.json     # [v3] Confirmed harvest outcomes per user
├── tests/
│   └── test_monte_carlo.py
├── requirements.txt
├── runtime.txt
├── .env.example
└── README.md
```

---

## API

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Server status |
| GET | `/api/nodes` | Options for all nodes C1–C7 and D1–D6 |
| POST | `/api/simulate` | Runs the full simulation (payoff matrix + criteria + MC) |
| POST | `/api/monte_carlo` | Monte Carlo with configurable parameters |

---

## Model

- **Scope:** Soy · Mato Grosso · Baseline = 60 sc/ha (CONAB 2023/24)
- **Context variables (C1–C7):** region, texture, pH, drainage, soil type, area, ENSO
- **Decision variables (D1–D6):** planting window, cultivar, seed treatment, density, disease management, planter
- **Climate scenarios:** Dry, Normal, Wet — conditional probabilities on ENSO
- **Stochastic variables (MC):** D2 Triangular(−8, 0, +6), D3 Triangular(−5, 0, +3), D6 Triangular(−4, 0, +3), Rainfall R3–R6 discrete

---

## How to read the results

- **Regional reference:** 60 sc/ha — historical average yield for MT
- **Your field's starting point:** baseline adjusted by field context
- **Expected yield:** probability-weighted average across climate scenarios (Bayes EV)
- **90% interval:** between P5 and P95 of the Monte Carlo simulations
- **Risk:** probability of falling below the configurable threshold (default: regional reference)

---

## Version history

| Version | Highlights |
|---|---|
| v1 | Payoff matrix, 6 decision criteria, basic Monte Carlo |
| v2 | Dashboard (waterfall, radar, sensitivity), PDF/CSV export, interactive explainer, session history, PBKDF2 auth |
| v3 | BI Intelligence Dashboard (regional benchmarks, variable health monitor, ENSO risk, alerts), Adaptive Season Planner (outcome confirmation, Bayesian calibration, What-if Explorer), triangular distribution source traceability, N_ITER constant, full English translation |

---

## License

Academic project — Inteli · Bayer CropScience.  
Proprietary Bayer data is not included in this repository.
