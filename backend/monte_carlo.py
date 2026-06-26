"""Monte Carlo engine — Decision Tree Simulator v7."""

from __future__ import annotations
import numpy as np
from data import BASELINE, CONTEXT_NODES, DECISION_NODES, RAIN_STATES, RAIN_PROBS

# Single constant used by both entry points so distributions are always comparable
N_ITER_DEFAULT: int = 2000


def _adj(node_dict: dict, key: str, value: str) -> float:
    return float(node_dict[key]["options"][value])


# Triangular distribution defaults for the three stochastic decision variables.
# Source: Decision_Tree_v7_Baseline_Adjusted.xlsx, sheet "Baseline & Nós".
# Mapping: min = worst option value, mode = intermediate option value (0 in the
# additive model), max = best option value — all in sc/ha additive adjustments.
#   D2 cultivar:   Limitado → -8, Intermediário → 0, Alto potencial → +6
#   D3 seed treat: Sem TSI  → -5, Standard      → 0, Premium        → +3
#   D6 technology: Baixa    → -4, Padrão         → 0, Alta precisão  → +3
TRIANGULAR_DEFAULTS: dict[str, dict] = {
    "d3_tsi":        {"label": "Seed Treatment · D3",          "min": -5, "mode": 0, "max": 3},
    "d6_tecnologia": {"label": "Planting Technology · D6",     "min": -4, "mode": 0, "max": 3},
    "d2_cultivar":   {"label": "Genetic Yield Potential · D2", "min": -8, "mode": 0, "max": 6},
}


def run_monte_carlo(
    context:   dict[str, str],
    decisions: dict[str, str],
    params:    dict[str, dict],   # {"d2": {min, mode, max}, "d3": ..., "d6": ...}
    n_iter:    int = N_ITER_DEFAULT,
    threshold: float = 60.0,
) -> dict:
    """
    Run n_iter Monte Carlo iterations for a single decision path.

    Fixed inputs:     context (C1-C7), D1, D4, D5 (user choices)
    Stochastic inputs: D2, D3, D6 sampled from Triangular(min, mode, max)
                       Rainfall R3-R6 sampled from P(rain | ENSO)

    Returns: simulated yields + summary statistics + tornado data.
    """

    # Fixed base: sum of context adjustments + fixed decision adjustments
    context_adj = sum(_adj(CONTEXT_NODES, k, v) for k, v in context.items())
    d1_adj = _adj(DECISION_NODES, "d1_janela",    decisions["d1_janela"])
    d4_adj = _adj(DECISION_NODES, "d4_densidade", decisions["d4_densidade"])
    d5_adj = _adj(DECISION_NODES, "d5_manejo",    decisions["d5_manejo"])
    fixed_base = BASELINE + context_adj + d1_adj + d4_adj + d5_adj

    # Rainfall setup: ENSO-conditional probability vector
    enso_key         = context["c7_enso"]
    rain_probs_map   = RAIN_PROBS[enso_key]
    rain_state_names = list(RAIN_STATES.keys())
    rain_probs_arr   = np.array([rain_probs_map[s] for s in rain_state_names])
    rain_adjs_arr    = np.array([RAIN_STATES[s] for s in rain_state_names])

    # Vectorised sampling
    rng = np.random.default_rng()

    d2_samples = rng.triangular(params["d2"]["min"], params["d2"]["mode"], params["d2"]["max"], n_iter)
    d3_samples = rng.triangular(params["d3"]["min"], params["d3"]["mode"], params["d3"]["max"], n_iter)
    d6_samples = rng.triangular(params["d6"]["min"], params["d6"]["mode"], params["d6"]["max"], n_iter)

    rain_idx     = rng.choice(len(rain_state_names), size=n_iter, p=rain_probs_arr)
    rain_samples = rain_adjs_arr[rain_idx]

    yields = fixed_base + d2_samples + d3_samples + d6_samples + rain_samples

    # Summary statistics
    mean    = float(np.mean(yields))
    std     = float(np.std(yields))
    p5      = float(np.percentile(yields, 5))
    p95     = float(np.percentile(yields, 95))
    p_below = float(np.mean(yields < threshold))

    # Tornado: Pearson correlation and variance share of each stochastic input
    inputs = {
        "D2 · Cultivar (Genetic Yield Potential)": d2_samples,
        "D3 · Seed Treatment (IST)":               d3_samples,
        "D6 · Planting Technology":                d6_samples,
        "Rainfall R3–R6":                          rain_samples.astype(float),
    }
    tornado = {}
    for name, inp in inputs.items():
        corr           = float(np.corrcoef(inp, yields)[0, 1])
        variance_share = float(np.var(inp) / max(np.var(yields), 1e-9))
        tornado[name]  = {"correlation": round(corr, 4), "variance_share": round(variance_share, 4)}

    return {
        "yields":     yields.tolist(),
        "n_iter":     n_iter,
        "fixed_base": round(fixed_base, 2),
        "mean":       round(mean, 2),
        "std":        round(std, 2),
        "p5":         round(p5, 2),
        "p95":        round(p95, 2),
        "threshold":  threshold,
        "p_below":    round(p_below, 4),
        "tornado":    tornado,
    }


def run_for_all_paths(
    context_base: float,
    paths: list[dict],
    enso_key: str,
    n_iter: int = N_ITER_DEFAULT,
) -> list[dict]:
    """
    Vectorised Monte Carlo across all D1×D4×D5 paths.
    Shares the same D2/D3/D6/rainfall samples across paths (common random numbers)
    so alternative paths are compared on equal footing.
    Returns a list of {mean, std, p5, p95, p_below} per path.
    """
    path_bases = np.array([
        context_base + p["d1_adj"] + p["d4_adj"] + p["d5_adj"]
        for p in paths
    ])

    rain_probs_map   = RAIN_PROBS[enso_key]
    rain_state_names = list(RAIN_STATES.keys())
    rain_probs_arr   = np.array([rain_probs_map[s] for s in rain_state_names])
    rain_adjs_arr    = np.array([RAIN_STATES[s]    for s in rain_state_names])

    rng   = np.random.default_rng()
    d2_d  = TRIANGULAR_DEFAULTS["d2_cultivar"]
    d3_d  = TRIANGULAR_DEFAULTS["d3_tsi"]
    d6_d  = TRIANGULAR_DEFAULTS["d6_tecnologia"]

    d2_s  = rng.triangular(d2_d["min"], d2_d["mode"], d2_d["max"], n_iter)
    d3_s  = rng.triangular(d3_d["min"], d3_d["mode"], d3_d["max"], n_iter)
    d6_s  = rng.triangular(d6_d["min"], d6_d["mode"], d6_d["max"], n_iter)
    rain_s = rain_adjs_arr[rng.choice(len(rain_state_names), size=n_iter, p=rain_probs_arr)]

    stochastic  = d2_s + d3_s + d6_s + rain_s              # (n_iter,)
    all_yields  = path_bases[:, None] + stochastic[None, :] # (n_paths, n_iter)

    threshold = BASELINE
    return [
        {
            "mean":    round(float(np.mean(all_yields[i])), 2),
            "std":     round(float(np.std(all_yields[i])), 2),
            "p5":      round(float(np.percentile(all_yields[i], 5)), 2),
            "p95":     round(float(np.percentile(all_yields[i], 95)), 2),
            "p_below": round(float(np.mean(all_yields[i] < threshold)), 4),
        }
        for i in range(len(paths))
    ]
