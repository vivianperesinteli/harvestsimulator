"""Motor de Monte Carlo — Decision Tree Simulator v7."""

from __future__ import annotations
import numpy as np
from data import BASELINE, CONTEXT_NODES, DECISION_NODES, RAIN_STATES, RAIN_PROBS


def _adj(node_dict: dict, key: str, value: str) -> float:
    return float(node_dict[key]["options"][value])


# Parâmetros padrão das distribuições triangulares (fonte: colega, Excel v7)
TRIANGULAR_DEFAULTS: dict[str, dict] = {
    "d3_tsi":        {"label": "IST · D3",                  "min": -5, "mode": 0, "max": 3},
    "d6_tecnologia": {"label": "Planting Technique · D6",   "min": -4, "mode": 0, "max": 3},
    "d2_cultivar":   {"label": "Genetic Yield Potential · D2", "min": -8, "mode": 0, "max": 6},
}


def run_monte_carlo(
    context:   dict[str, str],
    decisions: dict[str, str],
    params:    dict[str, dict],   # {"d2": {min, mode, max}, "d3": ..., "d6": ...}
    n_iter:    int = 2000,
    threshold: float = 60.0,
) -> dict:
    """
    Executa n_iter iterações do Monte Carlo.

    Fixos:      contexto (C1–C7), D1, D4, D5 (escolhas do usuário)
    Estocásticos: D2, D3, D6 → Triangular(min, mode, max)
                  Chuva R3–R6 → amostrada de P(chuva | ENSO)

    Retorna: yields simulados + estatísticas + dados para tornado.
    """

    # ── Base fixa ──────────────────────────────────────────────────────────
    context_adj = sum(_adj(CONTEXT_NODES, k, v) for k, v in context.items())
    d1_adj = _adj(DECISION_NODES, "d1_janela",    decisions["d1_janela"])
    d4_adj = _adj(DECISION_NODES, "d4_densidade", decisions["d4_densidade"])
    d5_adj = _adj(DECISION_NODES, "d5_manejo",    decisions["d5_manejo"])
    fixed_base = BASELINE + context_adj + d1_adj + d4_adj + d5_adj

    # ── Configuração da chuva ──────────────────────────────────────────────
    enso_key        = context["c7_enso"]
    rain_probs_map  = RAIN_PROBS[enso_key]
    rain_state_names = list(RAIN_STATES.keys())
    rain_probs_arr  = np.array([rain_probs_map[s] for s in rain_state_names])
    rain_adjs_arr   = np.array([RAIN_STATES[s] for s in rain_state_names])

    # ── Amostragem vetorizada ──────────────────────────────────────────────
    rng = np.random.default_rng()

    d2_samples = rng.triangular(params["d2"]["min"], params["d2"]["mode"], params["d2"]["max"], n_iter)
    d3_samples = rng.triangular(params["d3"]["min"], params["d3"]["mode"], params["d3"]["max"], n_iter)
    d6_samples = rng.triangular(params["d6"]["min"], params["d6"]["mode"], params["d6"]["max"], n_iter)

    rain_idx     = rng.choice(len(rain_state_names), size=n_iter, p=rain_probs_arr)
    rain_samples = rain_adjs_arr[rain_idx]

    yields = fixed_base + d2_samples + d3_samples + d6_samples + rain_samples

    # ── Estatísticas ───────────────────────────────────────────────────────
    mean  = float(np.mean(yields))
    std   = float(np.std(yields))
    p5    = float(np.percentile(yields, 5))
    p95   = float(np.percentile(yields, 95))
    p_below = float(np.mean(yields < threshold))

    # ── Tornado — correlação de Spearman de cada input com o output ────────
    inputs = {
        "D2 · Cultivar (Genetic)":       d2_samples,
        "D3 · TSI (IST)":                d3_samples,
        "D6 · Tecnologia (Planting)":    d6_samples,
        "Chuva R3–R6":                   rain_samples.astype(float),
    }
    tornado = {}
    for name, inp in inputs.items():
        corr = float(np.corrcoef(inp, yields)[0, 1])
        variance_share = float(np.var(inp) / max(np.var(yields), 1e-9))
        tornado[name] = {"correlation": round(corr, 4), "variance_share": round(variance_share, 4)}

    return {
        "yields":    yields.tolist(),
        "n_iter":    n_iter,
        "fixed_base": round(fixed_base, 2),
        "mean":      round(mean, 2),
        "std":       round(std, 2),
        "p5":        round(p5, 2),
        "p95":       round(p95, 2),
        "threshold": threshold,
        "p_below":   round(p_below, 4),
        "tornado":   tornado,
    }


def run_for_all_paths(
    context_base: float,
    paths: list[dict],
    enso_key: str,
    n_iter: int = 1000,
) -> list[dict]:
    """
    MC vetorizado para todos os paths (D1×D4×D5).
    Compartilha as mesmas amostras de D2/D3/D6/chuva entre todos os paths.
    Retorna lista de {mean, std, p5, p95, p_below} por path.
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
