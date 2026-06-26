"""
All model data for Decision Tree v7 (Baseline-Adjusted).
Source: Decision_Tree_v7_Baseline_Adjusted.xlsx — sheet "Baseline & Nós".
Scope: Summer Soybean MT · Baseline = 60 sc/ha.
"""

BASELINE: float = 60.0  # sc/ha — CONAB Jan/2024, MT 2023/24

# ── Context Nodes (C1–C7) ──────────────────────────────────────────────────
# Not controllable by the producer — reflect field/season characteristics.
# Value: additive adjustment in sc/ha over the baseline.

CONTEXT_NODES: dict = {
    "c1_regiao": {
        "label": "C1 · Região MT",
        "options": {
            "Favorável (Sorriso, Sinop, Lucas RV)": 5,
            "Intermediária (Sapezal, Campo Novo)": 0,
            "Desafiadora (Primavera Leste, Querência)": -6,
        },
    },
    "c2_textura": {
        "label": "C2 · Textura do Solo",
        "options": {
            "Favorável (argilosa / média bem estruturada)": 5,
            "Intermediária (textura média)": 0,
            "Desafiadora (arenosa / baixa retenção)": -7,
        },
    },
    "c3_ph": {
        "label": "C3 · pH do Solo",
        "options": {
            "Adequado (5,5 – 6,5)": 4,
            "Limítrofe (5,0–5,4 ou 6,6–6,8)": 0,
            "Crítico (<5,0 ou >6,8)": -6,
        },
    },
    "c4_drenagem": {
        "label": "C4 · Drenagem",
        "options": {
            "Boa (bem drenado)": 3,
            "Moderada (moderadamente/imperfeito)": 0,
            "Ruim (mal / excessivamente drenado)": -8,
        },
    },
    "c5_aptidao": {
        "label": "C5 · Aptidão Estrutural",
        "options": {
            "Alta (Latossolo, Nitossolo)": 5,
            "Média (Argissolo, Cambissolo)": 0,
            "Baixa (Neossolo, Gleissolo)": -7,
        },
    },
    "c6_area": {
        "label": "C6 · Área Plantada",
        "options": {
            "Pequena (≤50 ha)": -1,
            "Média (50–200 ha)": 0,
            "Grande (>200 ha)": 2,
        },
    },
    "c7_enso": {
        "label": "C7 · Forecast Climático (ENSO)",
        "options": {
            "El Niño (chuva regular em MT)": 3,
            "Neutro": 1,
            "La Niña (chuva concentrada/curta)": -3,
        },
    },
}

# ── Decision Nodes (D1–D6) ────────────────────────────────────────────────
# Controllable by the producer. Value: additive adjustment in sc/ha.

DECISION_NODES: dict = {
    "d1_janela": {
        "label": "D1 · Janela de Plantio",
        "options": {
            "Precoce (até 15/out)": -3,
            "Ótima (16/out – 10/nov)": 4,
            "Tardia (após 10/nov)": -8,
        },
    },
    "d2_cultivar": {
        "label": "D2 · Cultivar",
        "options": {
            "Alto potencial (P98R30, NK6727, BMX Foco; pós-2020)": 6,
            "Intermediário (2015–2019)": 0,
            "Limitado (legados pré-2015)": -8,
        },
    },
    "d3_tsi": {
        "label": "D3 · TSI (Tratamento de Sementes)",
        "options": {
            "Premium (fung+inset+nemat+inoc)": 3,
            "Standard (fungicida + inoculante)": 0,
            "Sem TSI": -5,
        },
    },
    "d4_densidade": {
        "label": "D4 · Densidade de Plantio",
        "options": {
            "Baixa (≤280k sementes/ha)": -1,
            "Média (280k–340k)": 2,
            "Alta (>340k)": -1,
        },
    },
    "d5_manejo": {
        "label": "D5 · Manejo de Doenças",
        "options": {
            "Alto (≥3 fung. + monitor ferrugem)": 5,
            "Padrão (2 aplicações)": 0,
            "Baixo (1 ou nenhuma)": -7,
        },
    },
    "d6_tecnologia": {
        "label": "D6 · Tecnologia de Plantio",
        "options": {
            "Alta precisão (RTK + pneumática moderna)": 3,
            "Padrão": 0,
            "Baixa (espaçamento irregular)": -4,
        },
    },
}

# ── Chance Node — State of Nature (Rainfall R3–R6) ────────────────────────
# Revealed ex-post. Additive adjustment in sc/ha.
# Source: INMET Sorriso/Sinop 2010–2024 + dataset rainfall_sum_R3_R6.

RAIN_STATES: dict[str, float] = {
    "Seca (<150 mm)": -8.0,
    "Normal (150–250 mm)": 2.0,
    "Úmida (>250 mm)": 4.0,
}

# P(chuva | ENSO) — probabilidades condicionais.
# Chave: valor do C7 (opção selecionada); valor: dict estado→probabilidade.

RAIN_PROBS: dict[str, dict[str, float]] = {
    "El Niño (chuva regular em MT)":     {"Seca (<150 mm)": 0.15, "Normal (150–250 mm)": 0.50, "Úmida (>250 mm)": 0.35},
    "Neutro":                             {"Seca (<150 mm)": 0.30, "Normal (150–250 mm)": 0.50, "Úmida (>250 mm)": 0.20},
    "La Niña (chuva concentrada/curta)":  {"Seca (<150 mm)": 0.50, "Normal (150–250 mm)": 0.30, "Úmida (>250 mm)": 0.20},
}

# ── Interaction Terms ─────────────────────────────────────────────────────────
# Additional adjustments (sc/ha) when two variables co-occur.
# Captures effects that the simple additive model cannot represent.
#
# Interaction 1 — Cultivar × Disease Management (D2 × D5)
#   High-potential cultivar needs management to deliver genetic potential.
#   With poor management, high susceptibility becomes a liability.
#
# Interaction 2 — Drainage × Rain State (C4 × Rain)
#   Waterlogging is only critical during heavy rainfall.
#   In drought conditions, poor drainage has little additional penalty.
#
# Interaction 3 — Planting Window × ENSO (D1 × C7)
#   Late planting in La Niña is the riskiest combination:
#   grain fill falls at the peak drought window.

INTERACTIONS: dict = {
    # Cultivar × Manejo (D2 × D5)
    ("d2_cultivar", "d5_manejo"): {
        ("Alto potencial (P98R30, NK6727, BMX Foco; pós-2020)", "Alto (≥3 fung. + monitor ferrugem)"): +2.0,
        ("Alto potencial (P98R30, NK6727, BMX Foco; pós-2020)", "Baixo (1 ou nenhuma)"):              -2.0,
        ("Intermediário (2015–2019)",                            "Alto (≥3 fung. + monitor ferrugem)"): +0.5,
        ("Limitado (legados pré-2015)",                         "Alto (≥3 fung. + monitor ferrugem)"): -1.0,
    },
    # Drenagem × Estado da Chuva (C4 × Rain)
    ("c4_drenagem", "rain_state"): {
        ("Ruim (mal / excessivamente drenado)", "Úmida (>250 mm)"):   -4.0,
        ("Ruim (mal / excessivamente drenado)", "Normal (150–250 mm)"): -1.5,
        ("Ruim (mal / excessivamente drenado)", "Seca (<150 mm)"):    +4.0,
        ("Moderada (moderadamente/imperfeito)", "Úmida (>250 mm)"):   -1.5,
        ("Boa (bem drenado)",                   "Úmida (>250 mm)"):   +1.0,
    },
    # Janela × ENSO (D1 × C7)
    ("d1_janela", "c7_enso"): {
        ("Tardia (após 10/nov)",    "La Niña (chuva concentrada/curta)"): -2.5,
        ("Tardia (após 10/nov)",    "El Niño (chuva regular em MT)"):     +1.0,
        ("Ótima (16/out – 10/nov)", "El Niño (chuva regular em MT)"):     +1.0,
        ("Precoce (até 15/out)",    "La Niña (chuva concentrada/curta)"): -1.0,
    },
}
