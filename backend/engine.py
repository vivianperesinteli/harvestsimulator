"""
Simulation engine — Decision Tree v7 with interaction terms.
Model: Yield = Baseline + Σ Context_adjustments(C1–C7) + Σ Decision_adjustments(D1–D6) + Rain_adjustment + Interactions
"""

from __future__ import annotations
from itertools import product as _product
import numpy as np
from data import BASELINE, CONTEXT_NODES, DECISION_NODES, RAIN_STATES, RAIN_PROBS, INTERACTIONS
from monte_carlo import run_for_all_paths


def _adj(node_dict: dict, key: str, value: str) -> float:
    return float(node_dict[key]["options"][value])


def _interaction(key1: str, val1: str, key2: str, val2: str) -> float:
    """Returns the interaction adjustment for the pair (key1=val1, key2=val2), or 0."""
    table = INTERACTIONS.get((key1, key2)) or INTERACTIONS.get((key2, key1))
    if not table:
        return 0.0
    return float(table.get((val1, val2)) or table.get((val2, val1)) or 0.0)


def compute_simulation(context: dict[str, str], decisions: dict[str, str]) -> dict:
    """
    Receives user choices and returns everything needed to display
    results, recommendations, and D2/D3/D6 upgrade analysis.
    """

    # 1. Context base
    context_adj  = sum(_adj(CONTEXT_NODES, k, v) for k, v in context.items())
    context_base = BASELINE + context_adj

    # 2. Fixed user decisions (D2, D3, D6)
    d2_val = decisions["d2_cultivar"]
    d3_val = decisions["d3_tsi"]
    d6_val = decisions["d6_tecnologia"]

    fixed_adj = (
        _adj(DECISION_NODES, "d2_cultivar",   d2_val)
        + _adj(DECISION_NODES, "d3_tsi",      d3_val)
        + _adj(DECISION_NODES, "d6_tecnologia", d6_val)
    )
    base_effective = context_base + fixed_adj

    # 3. ENSO-conditional rain probabilities
    enso_key       = context["c7_enso"]
    rain_probs_map = RAIN_PROBS[enso_key]
    rain_state_names = list(RAIN_STATES.keys())
    rain_probs     = [rain_probs_map[s] for s in rain_state_names]
    rain_adjs      = [RAIN_STATES[s] for s in rain_state_names]

    # 4. Payoff matrix 27 × 3 with interaction terms
    d1_items = list(DECISION_NODES["d1_janela"]["options"].items())
    d4_items = list(DECISION_NODES["d4_densidade"]["options"].items())
    d5_items = list(DECISION_NODES["d5_manejo"]["options"].items())
    drain_val = context["c4_drenagem"]

    paths:  list[dict]        = []
    matrix: list[list[float]] = []

    for d1_name, d1_adj in d1_items:
        for d4_name, d4_adj in d4_items:
            for d5_name, d5_adj in d5_items:
                path_base = base_effective + d1_adj + d4_adj + d5_adj

                # D2 × D5 interaction (cultivar × disease management)
                inter_d2_d5 = _interaction("d2_cultivar", d2_val, "d5_manejo", d5_name)

                # D1 × C7 interaction (planting window × ENSO) — constant across rain states
                inter_d1_enso = _interaction("d1_janela", d1_name, "c7_enso", enso_key)

                row = []
                for rain_name, r_adj in zip(rain_state_names, rain_adjs):
                    # C4 × rain state interaction (drainage × rain)
                    inter_drain = _interaction("c4_drenagem", drain_val, "rain_state", rain_name)

                    payoff = round(
                        path_base + r_adj
                        + inter_d2_d5
                        + inter_d1_enso
                        + inter_drain,
                        2,
                    )
                    row.append(payoff)

                matrix.append(row)
                paths.append({
                    "d1": d1_name, "d1_adj": d1_adj,
                    "d4": d4_name, "d4_adj": d4_adj,
                    "d5": d5_name, "d5_adj": d5_adj,
                    "path_base": round(path_base, 2),
                    "interactions": round(inter_d2_d5 + inter_d1_enso, 2),
                })

    # 5. Decision criteria across all 27 paths
    criteria = _compute_criteria(matrix, rain_probs)

    # 6. User's selection
    user_d1 = decisions["d1_janela"]
    user_d4 = decisions["d4_densidade"]
    user_d5 = decisions["d5_manejo"]
    user_d1_adj = _adj(DECISION_NODES, "d1_janela",    user_d1)
    user_d4_adj = _adj(DECISION_NODES, "d4_densidade", user_d4)
    user_d5_adj = _adj(DECISION_NODES, "d5_manejo",    user_d5)
    user_base   = base_effective + user_d1_adj + user_d4_adj + user_d5_adj

    inter_user_d2_d5  = _interaction("d2_cultivar", d2_val, "d5_manejo", user_d5)
    inter_user_d1_enso = _interaction("d1_janela", user_d1, "c7_enso", enso_key)
    user_yields = [
        round(
            user_base + r
            + inter_user_d2_d5
            + inter_user_d1_enso
            + _interaction("c4_drenagem", drain_val, "rain_state", rn),
            2,
        )
        for r, rn in zip(rain_adjs, rain_state_names)
    ]
    user_ev = round(sum(y * p for y, p in zip(user_yields, rain_probs)), 2)

    # 7. D2/D3/D6 upgrade potential
    upgrade_potential = _compute_upgrade_potential(
        context, decisions, context_base, rain_probs, rain_adjs,
        rain_state_names, drain_val, enso_key,
    )

    # 8. Integrated Monte Carlo
    mc_stats = run_for_all_paths(
        context_base=context_base,
        paths=paths,
        enso_key=enso_key,
        n_iter=10_000,
    )
    for i, mc in enumerate(mc_stats):
        paths[i]["mc"] = mc

    return {
        "baseline":           BASELINE,
        "context_adj":        round(context_adj, 2),
        "context_base":       round(context_base, 2),
        "fixed_adj":          round(fixed_adj, 2),
        "base_effective":     round(base_effective, 2),
        "rain_states":        rain_state_names,
        "rain_probs":         rain_probs,
        "paths":              paths,
        "matrix":             matrix,
        "criteria":           criteria,
        "upgrade_potential":  upgrade_potential,
        "user_selection": {
            "d1":     user_d1,
            "d4":     user_d4,
            "d5":     user_d5,
            "yields": user_yields,
            "ev":     user_ev,
        },
    }


def _compute_upgrade_potential(
    context, decisions, context_base,
    rain_probs, rain_adjs, rain_state_names,
    drain_val, enso_key,
) -> dict:
    """
    For each of D2, D3, D6, computes the expected gain of switching from the
    current option to each available alternative.
    Uses the Bayes-EV optimal D1/D4/D5 path as the reference.
    """

    # Find optimal D1/D4/D5 path using NumPy — vectorised over all 27 combinations
    combos = list(_product(
        DECISION_NODES["d1_janela"]["options"].items(),
        DECISION_NODES["d4_densidade"]["options"].items(),
        DECISION_NODES["d5_manejo"]["options"].items(),
    ))
    rain_arr   = np.array(rain_adjs)
    probs_arr  = np.array(rain_probs)
    drain_inter = np.array([
        _interaction("c4_drenagem", drain_val, "rain_state", rn) for rn in rain_state_names
    ])
    bases      = np.array([context_base + d1[1] + d4[1] + d5[1] for (d1, d4, d5) in combos])
    enso_inter = np.array([_interaction("d1_janela", d1[0], "c7_enso", enso_key) for (d1, d4, d5) in combos])
    # ev[i] = Σ_j (base[i] + rain[j] + enso[i] + drain[j]) * prob[j]
    ev_all = (bases[:, None] + rain_arr[None, :] + enso_inter[:, None] + drain_inter[None, :]) @ probs_arr
    best_idx = int(np.argmax(ev_all))
    best_d1  = combos[best_idx][0][0]
    best_d4  = combos[best_idx][1][0]
    best_d5  = combos[best_idx][2][0]

    def _ev_for_d2d3d6(d2, d3, d6) -> float:
        fa = (
            _adj(DECISION_NODES, "d2_cultivar",    d2)
            + _adj(DECISION_NODES, "d3_tsi",       d3)
            + _adj(DECISION_NODES, "d6_tecnologia", d6)
        )
        d1_adj   = _adj(DECISION_NODES, "d1_janela",    best_d1)
        d4_adj   = _adj(DECISION_NODES, "d4_densidade", best_d4)
        d5_adj   = _adj(DECISION_NODES, "d5_manejo",    best_d5)
        base = context_base + fa + d1_adj + d4_adj + d5_adj
        inter_d2_d5  = _interaction("d2_cultivar", d2, "d5_manejo", best_d5)
        inter_d1_enso = _interaction("d1_janela", best_d1, "c7_enso", enso_key)
        return sum(
            (base + r + inter_d2_d5 + inter_d1_enso
             + _interaction("c4_drenagem", drain_val, "rain_state", rn)) * p
            for r, rn, p in zip(rain_adjs, rain_state_names, rain_probs)
        )

    cur_d2 = decisions["d2_cultivar"]
    cur_d3 = decisions["d3_tsi"]
    cur_d6 = decisions["d6_tecnologia"]
    current_ev = _ev_for_d2d3d6(cur_d2, cur_d3, cur_d6)

    # Options sorted best to worst for each node
    d2_options = list(DECISION_NODES["d2_cultivar"]["options"].keys())
    d3_options = list(DECISION_NODES["d3_tsi"]["options"].keys())
    d6_options = list(DECISION_NODES["d6_tecnologia"]["options"].keys())

    def _best_option_gain(node_options, cur_val, node_key, other_d2, other_d3, other_d6) -> list[dict]:
        results = []
        for opt in node_options:
            if opt == cur_val:
                continue
            if node_key == "d2":
                ev = _ev_for_d2d3d6(opt, other_d3, other_d6)
            elif node_key == "d3":
                ev = _ev_for_d2d3d6(other_d2, opt, other_d6)
            else:
                ev = _ev_for_d2d3d6(other_d2, other_d3, opt)
            results.append({"option": opt, "ev": round(ev, 2), "delta": round(ev - current_ev, 2)})
        return sorted(results, key=lambda x: x["ev"], reverse=True)

    return {
        "current_ev": round(current_ev, 2),
        "d2_cultivar": {
            "current":  cur_d2,
            "options":  _best_option_gain(d2_options, cur_d2, "d2", cur_d2, cur_d3, cur_d6),
        },
        "d3_tsi": {
            "current":  cur_d3,
            "options":  _best_option_gain(d3_options, cur_d3, "d3", cur_d2, cur_d3, cur_d6),
        },
        "d6_tecnologia": {
            "current":  cur_d6,
            "options":  _best_option_gain(d6_options, cur_d6, "d6", cur_d2, cur_d3, cur_d6),
        },
        "best_d1d4d5": {"d1": best_d1, "d4": best_d4, "d5": best_d5},
    }


def _compute_criteria(matrix: list[list[float]], probs: list[float]) -> dict:
    n        = len(matrix)
    n_states = len(matrix[0])

    maximax_vals = [max(row) for row in matrix]
    maximax_idx  = maximax_vals.index(max(maximax_vals))

    wald_vals = [min(row) for row in matrix]
    wald_idx  = wald_vals.index(max(wald_vals))

    laplace_vals = [sum(row) / n_states for row in matrix]
    laplace_idx  = laplace_vals.index(max(laplace_vals))

    hurwicz_vals = [0.5 * max(row) + 0.5 * min(row) for row in matrix]
    hurwicz_idx  = hurwicz_vals.index(max(hurwicz_vals))

    ev_vals = [sum(y * p for y, p in zip(row, probs)) for row in matrix]
    ev_idx  = ev_vals.index(max(ev_vals))

    col_maxes   = [max(matrix[i][j] for i in range(n)) for j in range(n_states)]
    max_regrets = [max(col_maxes[j] - matrix[i][j] for j in range(n_states)) for i in range(n)]
    savage_idx  = max_regrets.index(min(max_regrets))

    def _fmt(vals): return [round(v, 2) for v in vals]

    return {
        "maximax": {"path_idx": maximax_idx, "value": round(max(maximax_vals), 2), "criterion_values": _fmt(maximax_vals)},
        "wald":    {"path_idx": wald_idx,    "value": round(max(wald_vals), 2),    "criterion_values": _fmt(wald_vals)},
        "laplace": {"path_idx": laplace_idx, "value": round(max(laplace_vals), 2), "criterion_values": _fmt(laplace_vals)},
        "hurwicz": {"path_idx": hurwicz_idx, "value": round(max(hurwicz_vals), 2), "criterion_values": _fmt(hurwicz_vals)},
        "bayes_ev":{"path_idx": ev_idx,      "value": round(max(ev_vals), 2),      "criterion_values": _fmt(ev_vals)},
        "savage":  {"path_idx": savage_idx,  "value": round(min(max_regrets), 2),  "criterion_values": _fmt(max_regrets)},
    }
