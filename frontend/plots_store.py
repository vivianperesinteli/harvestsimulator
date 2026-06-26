"""Plot (talhão) persistence — reads/writes data/plots.json."""

from __future__ import annotations
import json
import uuid
from pathlib import Path
from datetime import datetime

_PLOTS_FILE = Path(__file__).parent.parent / "data" / "plots.json"


def _load_all() -> list[dict]:
    if not _PLOTS_FILE.exists():
        return []
    with open(_PLOTS_FILE, encoding="utf-8") as f:
        return json.load(f)


def _save_all(plots: list[dict]) -> None:
    _PLOTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(_PLOTS_FILE, "w", encoding="utf-8") as f:
        json.dump(plots, f, indent=2, ensure_ascii=False)


def load_plots(user_id: str) -> list[dict]:
    return [p for p in _load_all() if p.get("user_id") == user_id]


def save_plot(user_id: str, nome: str, area_ha: float, context: dict) -> dict:
    all_plots = _load_all()
    plot = {
        "id":          str(uuid.uuid4()),
        "user_id":     user_id,
        "nome":        nome,
        "area_ha":     area_ha,
        "created_at":  datetime.now().isoformat(),
        "context":     context,
        "simulations": [],
    }
    all_plots.append(plot)
    _save_all(all_plots)
    return plot


def delete_plot(plot_id: str) -> bool:
    all_plots = _load_all()
    filtered = [p for p in all_plots if p["id"] != plot_id]
    if len(filtered) == len(all_plots):
        return False
    _save_all(filtered)
    return True


def update_plot(plot_id: str, nome: str, area_ha: float, context: dict) -> bool:
    all_plots = _load_all()
    for p in all_plots:
        if p["id"] == plot_id:
            p["nome"]    = nome
            p["area_ha"] = area_ha
            p["context"] = context
            _save_all(all_plots)
            return True
    return False


def add_simulation(
    plot_id:      str,
    c7_enso:      str,
    decisions:    dict,
    risk_profile: str,
    ev_simulated: float,
) -> bool:
    all_plots = _load_all()
    for p in all_plots:
        if p["id"] == plot_id:
            sims = p.setdefault("simulations", [])
            sims.append({
                "id":           len(sims) + 1,
                "timestamp":    datetime.now().isoformat(),
                "c7_enso":      c7_enso,
                "decisions":    decisions,
                "risk_profile": risk_profile,
                "ev_simulated": ev_simulated,
                "yield_real":   None,
            })
            _save_all(all_plots)
            return True
    return False
