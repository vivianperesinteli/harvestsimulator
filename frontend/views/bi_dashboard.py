"""BI Intelligence Dashboard — contextual KPIs, health monitor, and historical benchmarks."""

from __future__ import annotations
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from frontend.navigation import go as navigate
from frontend.i18n import t

# ── Historical MT soybean yields — CONAB/IMEA 2018–2024 ──────────────────────
_MT_HISTORY: dict[str, float] = {
    "2018/19": 55.2,
    "2019/20": 57.8,
    "2020/21": 49.5,  # La Niña drought
    "2021/22": 44.5,  # severe La Niña drought
    "2022/23": 62.1,
    "2023/24": 60.0,  # CONAB Jan/2024 — model baseline
}

# ── Regional benchmarks — IMEA Regional Bulletin 2023/24 ─────────────────────
_REGION_BENCHMARKS: dict[str, float] = {
    "Sorriso":                62.0,
    "Lucas do Rio Verde":     64.0,
    "Sinop":                  61.0,
    "Sapezal":                58.0,
    "Campo Novo do Parecis":  56.0,
    "Primavera do Leste":     52.0,
    "Querência":               50.0,
}

_C1_TO_REGION: dict[str, str] = {
    "Favorável (Sorriso, Sinop, Lucas RV)":          "Sorriso",
    "Intermediária (Sapezal, Campo Novo)":            "Sapezal",
    "Desafiadora (Primavera Leste, Querência)":       "Primavera do Leste",
}

# ── ENSO drought risk (probability of "Seca" rain state) ─────────────────────
_ENSO_RISK: dict[str, dict] = {
    "El Niño (chuva regular em MT)":     {"risk": 15, "label": "Low",    "color": "#2e7d32"},
    "Neutro":                             {"risk": 30, "label": "Medium", "color": "#f57c00"},
    "La Niña (chuva concentrada/curta)":  {"risk": 50, "label": "High",   "color": "#c62828"},
}

# ── Node quality classification ───────────────────────────────────────────────
_C_QUALITY: dict[str, dict[str, str]] = {
    "c1_regiao":   {"Favorável (Sorriso, Sinop, Lucas RV)": "optimal", "Intermediária (Sapezal, Campo Novo)": "neutral", "Desafiadora (Primavera Leste, Querência)": "critical"},
    "c2_textura":  {"Favorável (argilosa / média bem estruturada)": "optimal", "Intermediária (textura média)": "neutral", "Desafiadora (arenosa / baixa retenção)": "critical"},
    "c3_ph":       {"Adequado (5,5 – 6,5)": "optimal", "Limítrofe (5,0–5,4 ou 6,6–6,8)": "neutral", "Crítico (<5,0 ou >6,8)": "critical"},
    "c4_drenagem": {"Boa (bem drenado)": "optimal", "Moderada (moderadamente/imperfeito)": "neutral", "Ruim (mal / excessivamente drenado)": "critical"},
    "c5_aptidao":  {"Alta (Latossolo, Nitossolo)": "optimal", "Média (Argissolo, Cambissolo)": "neutral", "Baixa (Neossolo, Gleissolo)": "critical"},
    "c6_area":     {"Pequena (≤50 ha)": "neutral", "Média (50–200 ha)": "neutral", "Grande (>200 ha)": "optimal"},
    "c7_enso":     {"El Niño (chuva regular em MT)": "optimal", "Neutro": "neutral", "La Niña (chuva concentrada/curta)": "critical"},
}
_D_QUALITY: dict[str, dict[str, str]] = {
    "d1_janela":    {"Precoce (até 15/out)": "neutral", "Ótima (16/out – 10/nov)": "optimal", "Tardia (após 10/nov)": "critical"},
    "d2_cultivar":  {"Alto potencial (P98R30, NK6727, BMX Foco; pós-2020)": "optimal", "Intermediário (2015–2019)": "neutral", "Limitado (legados pré-2015)": "critical"},
    "d3_tsi":       {"Premium (fung+inset+nemat+inoc)": "optimal", "Standard (fungicida + inoculante)": "neutral", "Sem TSI": "critical"},
    "d4_densidade": {"Baixa (≤280k sementes/ha)": "neutral", "Média (280k–340k)": "optimal", "Alta (>340k)": "neutral"},
    "d5_manejo":    {"Alto (≥3 fung. + monitor ferrugem)": "optimal", "Padrão (2 aplicações)": "neutral", "Baixo (1 ou nenhuma)": "critical"},
    "d6_tecnologia": {"Alta precisão (RTK + pneumática moderna)": "optimal", "Padrão": "neutral", "Baixa (espaçamento irregular)": "critical"},
}

_C_LABELS = {
    "c1_regiao": "C1 · Region", "c2_textura": "C2 · Soil Texture", "c3_ph": "C3 · Soil pH",
    "c4_drenagem": "C4 · Drainage", "c5_aptidao": "C5 · Soil Type", "c6_area": "C6 · Area",
    "c7_enso": "C7 · ENSO",
}
_D_LABELS = {
    "d1_janela": "D1 · Planting Window", "d2_cultivar": "D2 · Cultivar",
    "d3_tsi": "D3 · Seed Treatment", "d4_densidade": "D4 · Density",
    "d5_manejo": "D5 · Disease Management", "d6_tecnologia": "D6 · Planting Technology",
}

_C_ADJ: dict[str, dict[str, float]] = {
    "c1_regiao":   {"Favorável (Sorriso, Sinop, Lucas RV)": 5, "Intermediária (Sapezal, Campo Novo)": 0, "Desafiadora (Primavera Leste, Querência)": -6},
    "c2_textura":  {"Favorável (argilosa / média bem estruturada)": 5, "Intermediária (textura média)": 0, "Desafiadora (arenosa / baixa retenção)": -7},
    "c3_ph":       {"Adequado (5,5 – 6,5)": 4, "Limítrofe (5,0–5,4 ou 6,6–6,8)": 0, "Crítico (<5,0 ou >6,8)": -6},
    "c4_drenagem": {"Boa (bem drenado)": 3, "Moderada (moderadamente/imperfeito)": 0, "Ruim (mal / excessivamente drenado)": -8},
    "c5_aptidao":  {"Alta (Latossolo, Nitossolo)": 5, "Média (Argissolo, Cambissolo)": 0, "Baixa (Neossolo, Gleissolo)": -7},
    "c6_area":     {"Pequena (≤50 ha)": -1, "Média (50–200 ha)": 0, "Grande (>200 ha)": 2},
    "c7_enso":     {"El Niño (chuva regular em MT)": 3, "Neutro": 1, "La Niña (chuva concentrada/curta)": -3},
}
_D_ADJ: dict[str, dict[str, float]] = {
    "d1_janela":    {"Precoce (até 15/out)": -3, "Ótima (16/out – 10/nov)": 4, "Tardia (após 10/nov)": -8},
    "d2_cultivar":  {"Alto potencial (P98R30, NK6727, BMX Foco; pós-2020)": 6, "Intermediário (2015–2019)": 0, "Limitado (legados pré-2015)": -8},
    "d3_tsi":       {"Premium (fung+inset+nemat+inoc)": 3, "Standard (fungicida + inoculante)": 0, "Sem TSI": -5},
    "d4_densidade": {"Baixa (≤280k sementes/ha)": -1, "Média (280k–340k)": 2, "Alta (>340k)": -1},
    "d5_manejo":    {"Alto (≥3 fung. + monitor ferrugem)": 5, "Padrão (2 aplicações)": 0, "Baixo (1 ou nenhuma)": -7},
    "d6_tecnologia": {"Alta precisão (RTK + pneumática moderna)": 3, "Padrão": 0, "Baixa (espaçamento irregular)": -4},
}

_Q_ICON  = {"optimal": "🟢", "neutral": "🟡", "critical": "🔴"}
_Q_COLOR = {"optimal": "#2e7d32", "neutral": "#f57c00", "critical": "#c62828"}

# ── Critical combination alerts (from INTERACTIONS in data.py) ────────────────
_ALERTS = [
    {
        "condition": lambda c, d: d.get("d1_janela") == "Tardia (após 10/nov)" and c.get("c7_enso") == "La Niña (chuva concentrada/curta)",
        "title":     "Critical: Late Planting + La Niña",
        "message":   "Late planting in a La Niña year forces grain fill into the peak drought window. Combined drag: −10.5 sc/ha (D1 penalty + D1×ENSO interaction).",
        "kind":      "error",
    },
    {
        "condition": lambda c, d: d.get("d2_cultivar", "").startswith("Alto potencial") and d.get("d5_manejo", "").startswith("Baixo"),
        "title":     "Underutilised Genetic Potential",
        "message":   "A high-potential cultivar with low disease management forfeits its genetic advantage. Interaction penalty: −2 sc/ha on top of D5 drag.",
        "kind":      "warning",
    },
    {
        "condition": lambda c, d: c.get("c4_drenagem", "").startswith("Ruim") and c.get("c7_enso", "").startswith("El Niño"),
        "title":     "Poor Drainage in Wet ENSO Year",
        "message":   "Poor drainage in an El Niño year amplifies waterlogging risk during heavy rainfall periods. Interaction: −1.5 sc/ha (normal) to −4 sc/ha (wet).",
        "kind":      "warning",
    },
    {
        "condition": lambda c, d: d.get("d2_cultivar", "").startswith("Alto potencial") and d.get("d5_manejo", "").startswith("Alto"),
        "title":     "Elite Combination Active",
        "message":   "High-potential cultivar + intensive disease management unlocks a +2 sc/ha synergy bonus from the D2×D5 interaction.",
        "kind":      "success",
    },
]


def _quality_map(context: dict, decisions: dict) -> dict[str, str]:
    q: dict[str, str] = {}
    for k, opts in _C_QUALITY.items():
        q[k] = opts.get(context.get(k, ""), "neutral")
    for k, opts in _D_QUALITY.items():
        q[k] = opts.get(decisions.get(k, ""), "neutral")
    return q


def _quality_score(quality: dict) -> int:
    """0–100 score for controllable decisions (D nodes only)."""
    d_vals = [quality[k] for k in _D_LABELS if k in quality]
    weights = {"optimal": 2, "neutral": 1, "critical": 0}
    total   = sum(weights[v] for v in d_vals)
    return int(total / (len(d_vals) * 2) * 100) if d_vals else 0


def render() -> None:
    lang      = st.session_state.get("lang", "en")
    result    = st.session_state.get("sim_result")
    context   = st.session_state.get("sim_context")
    decisions = st.session_state.get("sim_decisions")

    if not result or not context or not decisions:
        st.warning(t("bi_no_result", lang))
        if st.button(t("bi_go_sim", lang)):
            navigate("input")
        return

    ev_user  = result["user_selection"]["ev"]
    baseline = result["baseline"]
    enso_key = context.get("c7_enso", "Neutro")
    c1_key   = context.get("c1_regiao", "")

    quality     = _quality_map(context, decisions)
    q_score     = _quality_score(quality)
    enso_info   = _ENSO_RISK.get(enso_key, {"risk": 30, "label": "Medium", "color": "#f57c00"})
    region_name = _C1_TO_REGION.get(c1_key, "MT")
    region_ref  = _REGION_BENCHMARKS.get(region_name, 60.0)

    d_quality_vals = [quality[k] for k in _D_LABELS if k in quality]
    opt_d  = d_quality_vals.count("optimal")
    crit_d = d_quality_vals.count("critical")

    # Compute active alerts early so they can be shown near the top
    active = [a for a in _ALERTS if a["condition"](context, decisions)]

    st.markdown(f'<div class="page-title">{t("bi_page_title", lang)}</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="page-subtitle">{t("bi_page_subtitle", lang)}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div style="background:rgba(46,125,50,0.06);border-left:3px solid #2e7d32;'
        f'border-radius:0 8px 8px 0;padding:10px 16px;margin:10px 0 6px 0;'
        f'font-size:0.81rem;color:#1a1a2e;line-height:1.5">'
        f'{t("bi_purpose", lang)}</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    # ── 3 CONTEXTUAL BI KPIs ─────────────────────────────────────────────────
    st.markdown(f'<div class="section-hdr">{t("bi_section_kpi", lang)}</div>', unsafe_allow_html=True)

    k1, k2, k3 = st.columns(3)

    # KPI 1: Regional Productivity Benchmark
    region_delta = ev_user - region_ref
    r_color = "#2e7d32" if region_delta >= 0 else "#c62828"
    r_sign  = "+" if region_delta >= 0 else ""
    with k1:
        st.markdown(f"""
        <div class="metric-card" style="border-left:4px solid #1565c0">
            <div class="mc-label">{t("bi_kpi1_label", lang)}</div>
            <div class="mc-value" style="color:{r_color};font-size:1.5rem">{r_sign}{region_delta:.1f} sc/ha</div>
            <div class="mc-sub">{t("bi_kpi1_sub", lang, region=region_name, ref=region_ref)}</div>
            <div class="mc-caption" style="margin-top:6px;font-size:0.72rem;color:#6b6b8a">
                {t("bi_kpi1_caption", lang, ev=ev_user)}
            </div>
        </div>""", unsafe_allow_html=True)

    # KPI 2: ENSO Drought Risk Index
    risk_pct = enso_info["risk"]
    enso_short = enso_key.split(' (')[0]
    risk_label = t(f"bi_kpi_{enso_info['label'].lower()}", lang)
    with k2:
        st.markdown(f"""
        <div class="metric-card" style="border-left:4px solid {enso_info['color']}">
            <div class="mc-label">{t("bi_kpi2_label", lang)}</div>
            <div class="mc-value" style="color:{enso_info['color']};font-size:1.5rem">{risk_pct}%</div>
            <div class="mc-sub">{t("bi_kpi2_sub", lang, risk_label=risk_label, enso_short=enso_short)}</div>
            <div class="mc-caption" style="margin-top:6px;font-size:0.72rem;color:#6b6b8a">
                {t("bi_kpi2_caption", lang)}
            </div>
        </div>""", unsafe_allow_html=True)

    # KPI 3: Decision Quality Score
    score_color = "#2e7d32" if q_score >= 70 else "#f57c00" if q_score >= 40 else "#c62828"
    with k3:
        st.markdown(f"""
        <div class="metric-card" style="border-left:4px solid {score_color}">
            <div class="mc-label">{t("bi_kpi3_label", lang)}</div>
            <div class="mc-value" style="color:{score_color};font-size:1.5rem">{q_score}/100</div>
            <div class="mc-sub">{t("bi_kpi3_sub", lang, opt=opt_d, crit=crit_d)}</div>
            <div class="mc-caption" style="margin-top:6px;font-size:0.72rem;color:#6b6b8a">
                {t("bi_kpi3_caption", lang)}
            </div>
        </div>""", unsafe_allow_html=True)

    # ── ACTIVE ALERTS (shown early — critical flags first) ────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div class="section-hdr">{t("bi_section_alerts_hdr", lang)}</div>', unsafe_allow_html=True)
    if active:
        for alert in active:
            msg = f"**{alert['title']}** — {alert['message']}"
            if alert["kind"] == "error":
                st.error(msg)
            elif alert["kind"] == "warning":
                st.warning(msg)
            else:
                st.success(msg)
    else:
        st.success(t("bi_no_alerts", lang))

    st.markdown("<br>", unsafe_allow_html=True)

    # ── HISTORICAL BENCHMARK CHART ────────────────────────────────────────────
    col_hist, col_reg = st.columns([3, 2])

    with col_hist:
        st.markdown(t("bi_hist_title", lang))
        st.caption(t("bi_hist_caption", lang))

        years  = list(_MT_HISTORY.keys()) + [t("bi_hist_your_sim", lang)]
        values = list(_MT_HISTORY.values()) + [ev_user]
        colors = ["#90a4ae"] * len(_MT_HISTORY) + ["#2e7d32"]

        fig_hist = go.Figure(go.Bar(
            x=years, y=values,
            marker_color=colors,
            text=[f"{v:.1f}" for v in values],
            textposition="outside",
        ))
        fig_hist.add_hline(
            y=baseline, line_dash="dot", line_color="#f57c00",
            annotation_text=f"Baseline {baseline:.0f} sc/ha", annotation_font_size=10,
        )
        fig_hist.update_layout(
            height=320, yaxis_title="sc/ha",
            margin=dict(t=10, l=10, r=30, b=20),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#1a1a2e", size=11),
            yaxis=dict(gridcolor="#c8c0b0", range=[0, max(values) * 1.15]),
            xaxis=dict(tickfont=dict(size=10)),
            showlegend=False,
        )
        st.plotly_chart(fig_hist, use_container_width=True)
        st.caption(t("bi_hist_source", lang))

    with col_reg:
        st.markdown(t("bi_reg_title", lang))
        st.caption(t("bi_reg_caption", lang, region=region_name))

        reg_names  = list(_REGION_BENCHMARKS.keys())
        reg_vals   = list(_REGION_BENCHMARKS.values())
        reg_colors = ["#1565c0" if r == region_name else "#90a4ae" for r in reg_names]

        fig_reg = go.Figure(go.Bar(
            x=reg_vals, y=reg_names,
            orientation="h",
            marker_color=reg_colors,
            text=[f"{v:.0f}" for v in reg_vals],
            textposition="outside",
        ))
        fig_reg.add_vline(
            x=ev_user, line_color="#2e7d32", line_dash="solid", line_width=2,
            annotation_text=t("bi_reg_your_sim", lang, ev=ev_user),
            annotation_font_size=10, annotation_font_color="#2e7d32",
        )
        fig_reg.update_layout(
            height=320, xaxis_title="sc/ha",
            margin=dict(t=10, l=0, r=60, b=20),
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#1a1a2e", size=11),
            yaxis=dict(tickfont=dict(size=10)),
            xaxis=dict(gridcolor="#c8c0b0"),
            showlegend=False,
        )
        st.plotly_chart(fig_reg, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── VARIABLE HEALTH MONITOR ───────────────────────────────────────────────
    st.markdown(f'<div class="section-hdr">{t("bi_section_health", lang)}</div>', unsafe_allow_html=True)
    st.caption(t("bi_health_caption", lang))

    col_c, col_d = st.columns(2)

    with col_c:
        st.markdown(t("bi_ctx_nodes", lang))
        for key, label in _C_LABELS.items():
            val   = context.get(key, "")
            q     = quality.get(key, "neutral")
            adj   = _C_ADJ.get(key, {}).get(val, 0)
            icon  = _Q_ICON[q]
            color = _Q_COLOR[q]
            sign  = "+" if adj > 0 else ""
            short = val.split("(")[0].strip() if "(" in val else val
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;align-items:center;'
                f'padding:7px 10px;margin-bottom:4px;background:#f8f8fc;border-radius:8px;'
                f'border-left:4px solid {color}">'
                f'<span style="font-size:0.82rem;font-weight:600;color:#1a1a2e">{icon} {label}</span>'
                f'<span style="font-size:0.73rem;color:#6b6b8a;max-width:140px;text-align:right">{short[:30]}</span>'
                f'<span style="font-size:0.82rem;font-weight:700;color:{color};min-width:60px;text-align:right">{sign}{adj:+.0f} sc/ha</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

    with col_d:
        st.markdown(t("bi_dec_nodes", lang))
        for key, label in _D_LABELS.items():
            val   = decisions.get(key, "")
            q     = quality.get(key, "neutral")
            adj   = _D_ADJ.get(key, {}).get(val, 0)
            icon  = _Q_ICON[q]
            color = _Q_COLOR[q]
            sign  = "+" if adj > 0 else ""
            short = val.split("(")[0].strip() if "(" in val else val
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;align-items:center;'
                f'padding:7px 10px;margin-bottom:4px;background:#f8f8fc;border-radius:8px;'
                f'border-left:4px solid {color}">'
                f'<span style="font-size:0.82rem;font-weight:600;color:#1a1a2e">{icon} {label}</span>'
                f'<span style="font-size:0.73rem;color:#6b6b8a;max-width:140px;text-align:right">{short[:30]}</span>'
                f'<span style="font-size:0.82rem;font-weight:700;color:{color};min-width:60px;text-align:right">{sign}{adj:+.0f} sc/ha</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # Agronomic Vulnerability Score
    all_adjs    = [_C_ADJ.get(k, {}).get(context.get(k, ""), 0) for k in _C_LABELS] + \
                  [_D_ADJ.get(k, {}).get(decisions.get(k, ""), 0) for k in _D_LABELS]
    max_possible = sum(max(_C_ADJ.get(k, {}).values(), default=0) for k in _C_LABELS) + \
                   sum(max(_D_ADJ.get(k, {}).values(), default=0) for k in _D_LABELS)
    min_possible = sum(min(_C_ADJ.get(k, {}).values(), default=0) for k in _C_LABELS) + \
                   sum(min(_D_ADJ.get(k, {}).values(), default=0) for k in _D_LABELS)
    total_adj    = sum(all_adjs)
    span         = max_possible - min_possible
    vuln_score   = int((1 - (total_adj - min_possible) / span) * 100) if span else 50
    vuln_color   = "#2e7d32" if vuln_score < 30 else "#f57c00" if vuln_score < 60 else "#c62828"
    vuln_label   = (
        t("bi_vuln_low", lang) if vuln_score < 30
        else t("bi_vuln_mod", lang) if vuln_score < 60
        else t("bi_vuln_high", lang)
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f'<div class="metric-card" style="border-left:4px solid {vuln_color}">'
        f'<div class="mc-label">{t("bi_vuln_label", lang)}</div>'
        f'<div class="mc-value" style="color:{vuln_color};font-size:1.8rem">{vuln_score}/100 · {vuln_label}</div>'
        f'<div class="mc-sub">{t("bi_vuln_sub", lang)}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── RISK-RETURN QUADRANT ──────────────────────────────────────────────────
    st.markdown(t("bi_risk_map_title", lang))
    st.caption(t("bi_risk_map_caption", lang))

    from frontend.views.results_helpers import _D1_SHORT, _D4_SHORT, _D5_SHORT

    paths       = result.get("paths", [])
    ev_vals     = result["criteria"]["bayes_ev"]["criterion_values"]
    min_vals    = result["criteria"]["wald"]["criterion_values"]
    user_sel    = result["user_selection"]
    risk_criterion = st.session_state.get("risk_criterion", "bayes_ev")
    optimal_idx = result["criteria"][risk_criterion]["path_idx"]

    point_colors, point_sizes, point_labels = [], [], []
    user_idx = None
    for i, path in enumerate(paths):
        is_user = (path.get("d1") == user_sel.get("d1") and
                   path.get("d4") == user_sel.get("d4") and
                   path.get("d5") == user_sel.get("d5"))
        is_best = i == optimal_idx
        if is_user:
            user_idx = i
            point_colors.append("#1565c0"); point_sizes.append(18)
        elif is_best:
            point_colors.append("#2e7d32"); point_sizes.append(18)
        else:
            point_colors.append("#90a4ae"); point_sizes.append(9)
        point_labels.append(
            f"{_D1_SHORT.get(path.get('d1',''),'')} · "
            f"{_D4_SHORT.get(path.get('d4',''),'')} · "
            f"{_D5_SHORT.get(path.get('d5',''),'')}"
        )

    fig_quad = go.Figure()
    fig_quad.add_trace(go.Scatter(
        x=min_vals, y=ev_vals,
        mode="markers+text",
        marker=dict(color=point_colors, size=point_sizes, line=dict(width=1, color="white")),
        text=["★" if i == optimal_idx else ("●" if i == user_idx else "") for i in range(len(paths))],
        textposition="top center",
        textfont=dict(size=13),
        hovertext=point_labels,
        hovertemplate="<b>%{hovertext}</b><br>EV: %{y:.1f} sc/ha<br>Worst case: %{x:.1f} sc/ha<extra></extra>",
        showlegend=False,
    ))
    fig_quad.add_hline(y=baseline, line_dash="dot", line_color="#f57c00", line_width=1,
                       annotation_text="Baseline", annotation_font_size=9)
    fig_quad.add_vline(x=baseline, line_dash="dot", line_color="#f57c00", line_width=1)
    fig_quad.update_layout(
        height=400,
        xaxis_title=t("bi_risk_xaxis", lang),
        yaxis_title=t("bi_risk_yaxis", lang),
        margin=dict(t=10, l=60, r=20, b=60),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#1a1a2e", size=11),
        xaxis=dict(gridcolor="#c8c0b0"), yaxis=dict(gridcolor="#c8c0b0"),
    )
    st.plotly_chart(fig_quad, use_container_width=True)
    st.caption(t("bi_risk_caption", lang))

    st.markdown("<br>", unsafe_allow_html=True)

    # ── SEASON PLANNING CALENDAR ──────────────────────────────────────────────
    st.markdown(t("bi_calendar_title", lang))
    st.caption(t("bi_calendar_caption", lang))

    planting = decisions.get("d1_janela", "")
    _WINDOW_COLORS = {
        "Precoce (até 15/out)":    "#ff9800",
        "Ótima (16/out – 10/nov)": "#2e7d32",
        "Tardia (após 10/nov)":    "#c62828",
    }

    stages = [
        (t("bi_cal_stage_soil", lang),    0.0,  1.8, "#78909c"),
        (t("bi_cal_stage_early", lang),   1.8,  2.0, _WINDOW_COLORS["Precoce (até 15/out)"] if planting.startswith("Precoce") else "#d0d0d0"),
        (t("bi_cal_stage_optimal", lang), 2.0,  2.7, _WINDOW_COLORS["Ótima (16/out – 10/nov)"] if planting.startswith("Ótima") else "#d0d0d0"),
        (t("bi_cal_stage_late", lang),    2.7,  3.2, _WINDOW_COLORS["Tardia (após 10/nov)"] if planting.startswith("Tardia") else "#d0d0d0"),
        (t("bi_cal_stage_veg", lang),     2.0,  4.5, "#81c784"),
        (t("bi_cal_stage_rain", lang),    4.5,  6.0, "#42a5f5"),
        (t("bi_cal_stage_grain", lang),   6.0,  7.5, "#ffd54f"),
        (t("bi_cal_stage_harvest", lang), 7.2,  8.5, "#a1887f"),
    ]

    fig_cal = go.Figure()
    for i, (label, x0, x1, color) in enumerate(stages):
        fig_cal.add_shape(
            type="rect", x0=x0, x1=x1, y0=i - 0.4, y1=i + 0.4,
            fillcolor=color, line=dict(width=0), opacity=0.85,
        )
        fig_cal.add_annotation(
            x=(x0 + x1) / 2, y=i, text=label,
            showarrow=False, font=dict(size=9, color="white"),
        )
    fig_cal.update_layout(
        height=300,
        xaxis=dict(
            tickvals=list(range(9)),
            ticktext=t("bi_cal_months", lang).split(","),
            showgrid=True, gridcolor="#e0e0e0", tickfont=dict(size=10),
        ),
        yaxis=dict(showticklabels=False, showgrid=False),
        margin=dict(t=10, l=10, r=10, b=30),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(fig_cal, use_container_width=True)
    window_short = planting.split("(")[0].strip() if "(" in planting else planting
    st.caption(t("bi_cal_footer", lang, window=window_short))

    st.markdown("<br>", unsafe_allow_html=True)

    # ── DATA PIPELINE ─────────────────────────────────────────────────────────
    with st.expander(t("bi_pipeline_title", lang)):
        st.markdown("""
| Stage | What happens | File |
|-------|-------------|------|
| **Field inputs** | User fills C1–C7 (context) + D1–D6 (decisions) | `frontend/views/input.py` |
| **API request** | `POST /api/simulate` with all inputs | `frontend/api.py` |
| **Decision tree** | Evaluates all 27 D1×D4×D5 paths; additive adjustments + interaction effects | `backend/engine.py` |
| **Monte Carlo** | Sample D2/D3/D6 from Triangular distributions + rain from P(rain\\|ENSO); 2,000 iterations | `backend/monte_carlo.py` |
| **6 Criteria** | Bayes EV, Wald, Maximax, Laplace, Hurwicz, Savage — each selects its optimal path | `backend/engine.py` |
| **BI Dashboard** | Overlays results on IMEA/CONAB historical data and regional benchmarks | `frontend/views/bi_dashboard.py` |
| **Adaptive Learning** | Confirmed actual yields calibrate triangular parameters for your farm | `backend/learning.py` |

**Data sources:**
- **Baseline (60 sc/ha):** CONAB Levantamento Jan/2024 — Safra Verão MT 2023/24
- **Node adjustments:** Decision_Tree_v7_Baseline_Adjusted.xlsx, sheet "Baseline & Nós"
- **ENSO rain probabilities:** INMET Sorriso/Sinop 2010–2024 + dataset `rainfall_sum_R3_R6`
- **Regional benchmarks:** IMEA Regional Productivity Bulletin 2023/24
- **Historical MT yields:** CONAB Levantamentos 2018–2024
        """)

    # ── Cross-navigation ──────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    col_back, _, col_res = st.columns([1, 3, 1])
    with col_back:
        if st.button(t("bi_goto_dash", lang), use_container_width=True):
            navigate("dashboard")
    with col_res:
        if st.button(t("bi_goto_results", lang), use_container_width=True):
            navigate("results")
