"""FastAPI backend — Decision Tree Simulator v7."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models import SimulateRequest, SimulateResponse, MonteCarloRequest, MonteCarloResponse
from engine import compute_simulation
from data import CONTEXT_NODES, DECISION_NODES

app = FastAPI(title="Decision Tree Simulator API", version="2.0.0")

_raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:8501")
_allowed_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)


@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0.0"}


@app.get("/api/nodes")
def get_nodes():
    """Returns available options for all nodes C1-C7 and D1-D6."""
    return {
        "context":   {k: {"label": v["label"], "options": list(v["options"].keys())} for k, v in CONTEXT_NODES.items()},
        "decisions": {k: {"label": v["label"], "options": list(v["options"].keys())} for k, v in DECISION_NODES.items()},
    }


@app.post("/api/simulate", response_model=SimulateResponse)
def simulate(req: SimulateRequest):
    # Validate that all required keys are present
    missing_ctx = [k for k in CONTEXT_NODES if k not in req.context]
    missing_dec = [k for k in DECISION_NODES if k not in req.decisions]
    if missing_ctx or missing_dec:
        raise HTTPException(
            status_code=422,
            detail=f"Missing keys — context: {missing_ctx}, decisions: {missing_dec}",
        )

    # Validate that values are valid options
    for k, v in req.context.items():
        if k in CONTEXT_NODES and v not in CONTEXT_NODES[k]["options"]:
            raise HTTPException(status_code=422, detail=f"Invalid value for {k}: '{v}'")
    for k, v in req.decisions.items():
        if k in DECISION_NODES and v not in DECISION_NODES[k]["options"]:
            raise HTTPException(status_code=422, detail=f"Invalid value for {k}: '{v}'")

    return compute_simulation(req.context, req.decisions)


@app.post("/api/monte_carlo", response_model=MonteCarloResponse)
def monte_carlo(req: MonteCarloRequest):
    from monte_carlo import run_monte_carlo
    params = {k: v.model_dump() for k, v in req.params.items()}
    return run_monte_carlo(
        context=req.context,
        decisions=req.decisions,
        params=params,
        n_iter=req.n_iter,
        threshold=req.threshold,
    )
