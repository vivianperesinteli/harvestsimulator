# Harvest Simulator — Soy, Mato Grosso

**Bayer CropScience × Inteli · Module 6 · Group 2**

Web-based agricultural decision support tool for soybean producers in Mato Grosso. The producer enters field conditions and management decisions; the simulator calculates expected yield for each climate scenario, applies 6 economic decision criteria, and estimates the confidence interval via Monte Carlo simulation.

---

## Features

| Feature | Description |
|---|---|
| Payoff Matrix | 27 management combinations × 3 climate scenarios (sc/ha) |
| 6 Decision Criteria | Bayes EV, Wald, Laplace, Hurwicz, Maximax, Savage |
| Monte Carlo | 1,000–5,000 iterations, configurable triangular distributions |
| Risk Analysis | P(yield < threshold), P5/P95, standard deviation |
| Tornado Chart | Spearman correlation per stochastic variable |
| Alternative Comparison | Your selection vs. optimal path (Bayes EV) |
| Upgrade Potential | Impact of switching cultivar, seed treatment, or planter |
| Export | PDF (full report) + CSV per recommendation |
| Interactive Explainer | 10-step methodology with formulas and charts |

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
│   ├── models.py        # Pydantic models for request/response
│   └── data.py          # Constants: nodes, adjustments, rainfall probabilities
├── frontend/
│   ├── app.py           # Streamlit: authentication + router + sidebar
│   ├── auth.py          # Login/register with PBKDF2-SHA256
│   ├── api.py           # HTTP client for the backend
│   ├── styles.py        # Global CSS (visual identity)
│   ├── navigation.py    # Page router via session_state
│   └── views/
│       ├── input.py         # 3 steps: context → decisions → review
│       ├── results.py       # Recommendations, matrix, criteria, PDF/CSV export
│       ├── results_helpers.py  # Shared labels and text
│       ├── results_pdf.py      # PDF generator (fpdf2)
│       ├── dashboard.py     # Charts: waterfall, radar, bar, sensitivity
│       ├── monte_carlo.py   # Monte Carlo UI with histogram and tornado
│       ├── explainer.py     # Interactive explainer — 10 steps
│       └── history.py       # Session simulation history
├── data/
│   └── users.json       # Users (auto-generated)
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
- **90% interval:** between P5 and P95 of 2,000 Monte Carlo simulations
- **Risk:** probability of falling below the configurable threshold (default: regional reference)

---

## License

Academic project — Inteli · Bayer CropScience.  
Proprietary Bayer data is not included in this repository.
