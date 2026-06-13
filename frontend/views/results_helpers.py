"""Constantes e geradores de texto compartilhados pela página de resultados."""

from __future__ import annotations

_D1_SHORT = {
    "Precoce (até 15/out)":    "Precoce",
    "Ótima (16/out – 10/nov)": "Ótima",
    "Tardia (após 10/nov)":    "Tardia",
}
_D4_SHORT = {
    "Baixa (≤280k sementes/ha)": "Dens. baixa",
    "Média (280k–340k)":          "Dens. média",
    "Alta (>340k)":               "Dens. alta",
}
_D5_SHORT = {
    "Alto (≥3 fung. + monitor ferrugem)": "Manejo intensivo",
    "Padrão (2 aplicações)":              "Manejo padrão",
    "Baixo (1 ou nenhuma)":               "Manejo reduzido",
}
_D2_SHORT = {
    "Alto potencial (P98R30, NK6727, BMX Foco; pós-2020)": "Cultivar pós-2020",
    "Intermediário (2015–2019)":                            "Cultivar 2015–2019",
    "Limitado (legados pré-2015)":                         "Cultivar pré-2015",
}
_D3_SHORT = {
    "Premium (fung+inset+nemat+inoc)":    "TSI Premium",
    "Standard (fungicida + inoculante)":  "TSI Standard",
    "Sem TSI":                            "Sem tratamento",
}
_D6_SHORT = {
    "Alta precisão (RTK + pneumática moderna)": "Alta precisão",
    "Padrão":                                   "Precisão padrão",
    "Baixa (espaçamento irregular)":            "Baixa precisão",
}

_CRITERIA_LABELS = {
    "bayes_ev": "Melhor resultado esperado",
    "wald":     "Mais seguro no pior cenário",
    "laplace":  "Média entre todos os cenários",
    "hurwicz":  "Equilíbrio risco/oportunidade",
    "maximax":  "Máximo potencial produtivo",
    "savage":   "Menor arrependimento possível",
}


def _pdf_safe(text: str) -> str:
    """Substitui caracteres fora do Latin-1 para o fpdf2 não quebrar."""
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
        "Precoce":  "plantar antes de 15 de outubro",
        "Ótima":    "plantar entre 16 de outubro e 10 de novembro",
        "Tardia":   "plantar após 10 de novembro",
    }.get(_D1_SHORT.get(path["d1"], ""), path["d1"])

    d4_txt = {
        "Dens. baixa":  "densidade abaixo de 280 mil sementes/ha",
        "Dens. média":  "densidade entre 280 e 340 mil sementes/ha",
        "Dens. alta":   "densidade acima de 340 mil sementes/ha",
    }.get(_D4_SHORT.get(path["d4"], ""), path["d4"])

    d5_txt = {
        "Manejo intensivo": "3 ou mais aplicações de fungicida com monitoramento de ferrugem",
        "Manejo padrão":    "2 aplicações de fungicida",
        "Manejo reduzido":  "1 ou nenhuma aplicação de fungicida",
    }.get(_D5_SHORT.get(path["d5"], ""), path["d5"])

    delta = ev - baseline
    delta_str = f"+{delta:.1f}" if delta >= 0 else f"{delta:.1f}"

    summary = (
        f"Combinação com {d1_txt}, {d4_txt} e {d5_txt}. "
        f"Produtividade esperada de <strong>{ev:.1f} sc/ha</strong> "
        f"({delta_str} sc/ha em relação à referência regional). "
    )
    if mc:
        summary += (
            f"Considerando variações climáticas e de insumos, 90% das simulações projetam entre "
            f"<strong>{mc['p5']:.0f} e {mc['p95']:.0f} sc/ha</strong>."
        )
    return summary


def _janela_guidance(d1: str) -> str:
    return {
        "Ótima (16/out – 10/nov)":
            "Planeje o plantio entre 16 de outubro e 10 de novembro. "
            "Evite chuvas intensas nos primeiros 7 dias após a emergência.",
        "Precoce (até 15/out)":
            "Plantio precoce pode ser viável com início previsível de chuvas, "
            "mas aumenta o risco de déficit hídrico na fase vegetativa. Acompanhe o INMET.",
        "Tardia (após 10/nov)":
            "Plantios tardios colocam o enchimento de grão em fevereiro/março, com maior risco "
            "de alta umidade e pressão de doenças. Reavalie a data se possível.",
    }.get(d1, "")


def _densidade_guidance(d4: str) -> str:
    return {
        "Média (280k–340k)":
            "Trabalhe com 280–340 mil sementes germinávéis por hectare "
            "(ajuste pelo poder germinativo). Espaçamento recomendado de 45–50 cm entre linhas.",
        "Baixa (≤280k sementes/ha)":
            "Considere aumentar a densidade para a faixa recomendada (280–340 mil). "
            "Densidades abaixo de 250 mil podem reduzir o estande.",
        "Alta (>340k)":
            "Densidades acima de 340 mil aumentam a estatura e o risco de acamamento. "
            "Reavalie se o cultivar suporta alta densidade.",
    }.get(d4, "")


def _manejo_guidance(d5: str) -> str:
    return {
        "Alto (≥3 fung. + monitor ferrugem)":
            "Faça monitoramento quinzenal a partir de R1. Aplique fungicida em V6–R1, "
            "segundo em R3 e terceiro em R5.1 se necessário. Alterne grupos químicos.",
        "Padrão (2 aplicações)":
            "Aplique em R1 e R3. Reforce o monitoramento de ferrugem e ajuste se a pressão for alta.",
        "Baixo (1 ou nenhuma)":
            "Manejo insuficiente em regiões com alta pressão de doenças. "
            "Ao menos 2 aplicações são recomendadas na maioria dos talhões do MT.",
    }.get(d5, "")
