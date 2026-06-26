"""Shared constants and text generators for the results page."""

from __future__ import annotations

_D1_SHORT = {
    "Precoce (até 15/out)":    "Early",
    "Ótima (16/out – 10/nov)": "Optimal",
    "Tardia (após 10/nov)":    "Late",
}
_D4_SHORT = {
    "Baixa (≤280k sementes/ha)": "Low density",
    "Média (280k–340k)":          "Mid density",
    "Alta (>340k)":               "High density",
}
_D5_SHORT = {
    "Alto (≥3 fung. + monitor ferrugem)": "Intensive management",
    "Padrão (2 aplicações)":              "Standard management",
    "Baixo (1 ou nenhuma)":               "Reduced management",
}
_D2_SHORT = {
    "Alto potencial (P98R30, NK6727, BMX Foco; pós-2020)": "Post-2020 cultivar",
    "Intermediário (2015–2019)":                            "2015–2019 cultivar",
    "Limitado (legados pré-2015)":                         "Pre-2015 cultivar",
}
_D3_SHORT = {
    "Premium (fung+inset+nemat+inoc)":    "Premium seed treatment",
    "Standard (fungicida + inoculante)":  "Standard seed treatment",
    "Sem TSI":                            "No treatment",
}
_D6_SHORT = {
    "Alta precisão (RTK + pneumática moderna)": "High precision",
    "Padrão":                                   "Standard precision",
    "Baixa (espaçamento irregular)":            "Low precision",
}

_CRITERIA_LABELS = {
    "bayes_ev": "Best expected outcome",
    "wald":     "Safest in worst case",
    "laplace":  "Average across all scenarios",
    "hurwicz":  "Risk/opportunity balance",
    "maximax":  "Maximum yield potential",
    "savage":   "Minimum regret",
}


def _pdf_safe(text: str) -> str:
    """Replace characters outside Latin-1 so fpdf2 does not raise an encoding error."""
    return (str(text)
        .replace("–", "-")
        .replace("—", "-")
        .replace("…", "...")
        .replace("“", '"')
        .replace("”", '"')
        .replace("‘", "'")
        .replace("’", "'")
        .replace("·", ".")
    )


def _shorten(path: dict) -> str:
    return (
        f"{_D1_SHORT.get(path['d1'], path['d1'])} · "
        f"{_D4_SHORT.get(path['d4'], path['d4'])} · "
        f"{_D5_SHORT.get(path['d5'], path['d5'])}"
    )


def _get_criteria_tags(path_idx: int, criteria: dict) -> list[str]:
    return [
        label
        for key, label in _CRITERIA_LABELS.items()
        if criteria[key]["path_idx"] == path_idx
    ]


def _gen_card_summary(
    path: dict, ev: float, mc: dict | None, baseline: float,
    states: list, probs: list, yields_row: list, rank: int,
) -> str:
    d1_txt = {
        "Early":    "planting before October 15",
        "Optimal":  "planting between October 16 and November 10",
        "Late":     "planting after November 10",
    }.get(_D1_SHORT.get(path["d1"], ""), path["d1"])

    d4_txt = {
        "Low density":  "density below 280 thousand seeds/ha",
        "Mid density":  "density between 280 and 340 thousand seeds/ha",
        "High density": "density above 340 thousand seeds/ha",
    }.get(_D4_SHORT.get(path["d4"], ""), path["d4"])

    d5_txt = {
        "Intensive management": "3 or more fungicide applications with rust monitoring",
        "Standard management":  "2 fungicide applications",
        "Reduced management":   "1 or no fungicide application",
    }.get(_D5_SHORT.get(path["d5"], ""), path["d5"])

    delta = ev - baseline
    delta_str = f"+{delta:.1f}" if delta >= 0 else f"{delta:.1f}"

    summary = (
        f"Combination with {d1_txt}, {d4_txt} and {d5_txt}. "
        f"Expected yield of <strong>{ev:.1f} sc/ha</strong> "
        f"({delta_str} sc/ha relative to the regional reference). "
    )
    if mc:
        summary += (
            f"Accounting for climate and input variability, 90% of simulations project between "
            f"<strong>{mc['p5']:.0f} and {mc['p95']:.0f} sc/ha</strong>."
        )
    return summary


def _janela_guidance(d1: str) -> str:
    return {
        "Ótima (16/out – 10/nov)":
            "Plan planting between October 16 and November 10. "
            "Avoid heavy rainfall in the first 7 days after emergence.",
        "Precoce (até 15/out)":
            "Early planting can be viable with a predictable start of rains, "
            "but it increases the risk of water deficit during the vegetative stage. Monitor INMET forecasts.",
        "Tardia (após 10/nov)":
            "Late planting places grain filling in February/March, with higher risk "
            "of high humidity and disease pressure. Reconsider the date if possible.",
    }.get(d1, "")


def _densidade_guidance(d4: str) -> str:
    return {
        "Média (280k–340k)":
            "Use 280–340 thousand viable seeds per hectare "
            "(adjust for germination rate). Recommended row spacing: 45–50 cm.",
        "Baixa (≤280k sementes/ha)":
            "Consider increasing density to the recommended range (280–340 thousand). "
            "Densities below 250 thousand may reduce stand establishment.",
        "Alta (>340k)":
            "Densities above 340 thousand increase plant height and lodging risk. "
            "Reassess whether the cultivar tolerates high density.",
    }.get(d4, "")


def _manejo_guidance(d5: str) -> str:
    return {
        "Alto (≥3 fung. + monitor ferrugem)":
            "Carry out bi-weekly monitoring from R1. Apply fungicide at V6–R1, "
            "second application at R3, and third at R5.1 if needed. Rotate chemical groups.",
        "Padrão (2 aplicações)":
            "Apply at R1 and R3. Strengthen rust monitoring and adjust if pressure is high.",
        "Baixo (1 ou nenhuma)":
            "Insufficient management in regions with high disease pressure. "
            "At least 2 applications are recommended for most fields in MT.",
    }.get(d5, "")
