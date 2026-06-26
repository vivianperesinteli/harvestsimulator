"""Adaptive learning module — stores confirmed season outcomes and calibrates distribution parameters."""

from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

_OUTCOMES_FILE = Path(__file__).parent.parent / "data" / "outcomes.json"

# Default triangular parameters (mirrors TRIANGULAR_DEFAULTS in monte_carlo.py)
_DEFAULT_PARAMS: dict[str, dict] = {
    "d2": {"label": "Genetic Yield Potential · D2 (Cultivar)",  "min": -8.0, "mode": 0.0, "max": 6.0},
    "d3": {"label": "Seed Treatment · D3 (IST)",                "min": -5.0, "mode": 0.0, "max": 3.0},
    "d6": {"label": "Planting Technology · D6",                 "min": -4.0, "mode": 0.0, "max": 3.0},
}

# Fallback variance shares when no tornado data is available
_DEFAULT_VAR_SHARES: dict[str, float] = {"d2": 0.35, "d3": 0.25, "d6": 0.20}


def _load_all() -> list[dict]:
    if not _OUTCOMES_FILE.exists():
        return []
    with open(_OUTCOMES_FILE) as f:
        return json.load(f)


def load_outcomes(user_id: str) -> list[dict]:
    return [o for o in _load_all() if o.get("user_id") == user_id]


def save_outcome(
    user_id:        str,
    season:         str,
    simulation_id:  Optional[int],
    context:        dict,
    decisions:      dict,
    simulated_mean: float,
    actual_yield:   float,
    tornado_shares: Optional[dict] = None,
) -> None:
    all_outcomes = _load_all()
    all_outcomes.append({
        "user_id":        user_id,
        "season":         season,
        "simulation_id":  simulation_id,
        "timestamp":      datetime.now().isoformat(),
        "context":        context,
        "decisions":      decisions,
        "simulated_mean": simulated_mean,
        "actual_yield":   actual_yield,
        "gap":            round(actual_yield - simulated_mean, 2),
        "tornado_shares": tornado_shares or _DEFAULT_VAR_SHARES,
    })
    _OUTCOMES_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(_OUTCOMES_FILE, "w") as f:
        json.dump(all_outcomes, f, indent=2)


def get_calibrated_params(user_id: str) -> dict:
    """
    Returns updated triangular distribution parameters based on confirmed outcomes.

    Algorithm: compute the mean prediction gap (actual - simulated) across all
    recorded seasons, then apportion the correction to D2/D3/D6 proportionally
    to each variable's historical average variance share from the tornado chart.
    Falls back to defaults when fewer than 3 outcomes exist.
    """
    outcomes = load_outcomes(user_id)
    if len(outcomes) < 3:
        return {k: {**v} for k, v in _DEFAULT_PARAMS.items()}

    gaps      = [o["gap"] for o in outcomes]
    mean_gap  = sum(gaps) / len(gaps)

    # Average variance shares from stored tornado data
    all_shares = [o.get("tornado_shares", _DEFAULT_VAR_SHARES) for o in outcomes]
    avg_shares: dict[str, float] = {}
    for key in ["d2", "d3", "d6"]:
        avg_shares[key] = sum(s.get(key, _DEFAULT_VAR_SHARES[key]) for s in all_shares) / len(all_shares)

    total_share = sum(avg_shares.values()) or 1.0

    params: dict[str, dict] = {}
    for key in ["d2", "d3", "d6"]:
        base      = _DEFAULT_PARAMS[key].copy()
        share     = avg_shares[key] / total_share
        delta     = mean_gap * share
        new_mode  = round(base["mode"] + delta, 2)
        new_mode  = max(base["min"], min(base["max"], new_mode))
        params[key] = {
            **base,
            "mode":       new_mode,
            "calibrated": True,
            "n_outcomes": len(outcomes),
            "mean_gap":   round(mean_gap, 2),
        }
    return params


def get_learning_stats(user_id: str) -> dict:
    """Summary statistics for the learning curve display."""
    outcomes = load_outcomes(user_id)
    if not outcomes:
        return {"n": 0, "mean_gap": None, "rmse": None, "improving": None, "outcomes": []}

    gaps     = [o["gap"] for o in outcomes]
    n        = len(gaps)
    mean_gap = sum(gaps) / n
    rmse     = (sum(g ** 2 for g in gaps) / n) ** 0.5

    improving = None
    if n >= 4:
        half  = n // 2
        rmse1 = (sum(g ** 2 for g in gaps[:half]) / half) ** 0.5
        rmse2 = (sum(g ** 2 for g in gaps[half:]) / (n - half)) ** 0.5
        improving = rmse2 < rmse1

    return {
        "n":         n,
        "mean_gap":  round(mean_gap, 2),
        "rmse":      round(rmse, 2),
        "improving": improving,
        "outcomes":  outcomes,
    }
