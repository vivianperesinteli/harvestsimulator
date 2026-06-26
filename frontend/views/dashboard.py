"""Dashboard — visual decomposition of simulated yield."""

from __future__ import annotations
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from frontend.navigation import go as navigate
from frontend.i18n import t

# Mapeamentos de labels curtos
_C_LABELS = {
    "c1_regiao":  "C1 · Region",
    "c2_textura": "C2 · Texture",
    "c3_ph":      "C3 · pH",
    "c4_drenagem":"C4 · Drainage",
    "c5_aptidao": "C5 · Aptitude",
    "c6_area":    "C6 · Area",
    "c7_enso":    "C7 · ENSO",
}
_D_LABELS = {
    "d1_janela":    "D1 · Window",
    "d2_cultivar":  "D2 · Cultivar",
    "d3_tsi":       "D3 · TSI",
    "d4_densidade": "D4 · Density",
    "d5_manejo":    "D5 · Management",
    "d6_tecnologia":"D6 · Technology",
}

# Ajustes de cada nó — espelho de backend/data.py
_C_OPTIONS = {
    "c1_regiao":  {"Favorável (Sorriso, Sinop, Lucas RV)": 5, "Intermediária (Sapezal, Campo Novo)": 0, "Desafiadora (Primavera Leste, Querência)": -6},
    "c2_textura": {"Favorável (argilosa / média bem estruturada)": 5, "Intermediária (textura média)": 0, "Desafiadora (arenosa / baixa retenção)": -7},
    "c3_ph":      {"Adequado (5,5 – 6,5)": 4, "Limítrofe (5,0–5,4 ou 6,6–6,8)": 0, "Crítico (<5,0 ou >6,8)": -6},
    "c4_drenagem":{"Boa (bem drenado)": 3, "Moderada (moderadamente/imperfeito)": 0, "Ruim (mal / excessivamente drenado)": -8},
    "c5_aptidao": {"Alta (Latossolo, Nitossolo)": 5, "Média (Argissolo, Cambissolo)": 0, "Baixa (Neossolo, Gleissolo)": -7},
    "c6_area":    {"Pequena (≤50 ha)": -1, "Média (50–200 ha)": 0, "Grande (>200 ha)": 2},
    "c7_enso":    {"El Niño (chuva regular em MT)": 3, "Neutro": 1, "La Niña (chuva concentrada/curta)": -3},
}
_D_OPTIONS = {
    "d1_janela":    {"Precoce (até 15/out)": -3, "Ótima (16/out – 10/nov)": 4, "Tardia (após 10/nov)": -8},
    "d2_cultivar":  {"Alto potencial (P98R30, NK6727, BMX Foco; pós-2020)": 6, "Intermediário (2015–2019)": 0, "Limitado (legados pré-2015)": -8},
    "d3_tsi":       {"Premium (fung+inset+nemat+inoc)": 3, "Standard (fungicida + inoculante)": 0, "Sem TSI": -5},
    "d4_densidade": {"Baixa (≤280k sementes/ha)": -1, "Média (280k–340k)": 2, "Alta (>340k)": -1},
    "d5_manejo":    {"Alto (≥3 fung. + monitor ferrugem)": 5, "Padrão (2 aplicações)": 0, "Baixo (1 ou nenhuma)": -7},
    "d6_tecnologia":{"Alta precisão (RTK + pneumática moderna)": 3, "Padrão": 0, "Baixa (espaçamento irregular)": -4},
}


def render() -> None:
    lang      = st.session_state.get("lang", "en")
    result    = st.session_state.get("sim_result")
    context   = st.session_state.get("sim_context")
    decisions = st.session_state.get("sim_decisions")

    if not result or not context or not decisions:
        st.warning(t("dash_no_result", lang))
        if st.button(t("dash_go_sim", lang)):
            navigate("input")
        return

    user_sel  = result["user_selection"]
    rain_states = result["rain_states"]
    rain_probs  = result["rain_probs"]
    ev_chuva    = sum(
        adj * p
        for adj, p in zip([-8.0, 2.0, 4.0], rain_probs)
    )

    st.markdown(f'<div class="page-title">{t("dash_page_title", lang)}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">{t("dash_page_subtitle", lang)}</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div style="background:rgba(21,101,192,0.06);border-left:3px solid #1565c0;'
        f'border-radius:0 8px 8px 0;padding:10px 16px;margin:10px 0 6px 0;'
        f'font-size:0.81rem;color:#1a1a2e;line-height:1.5">'
        f'{t("dash_purpose", lang)}</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Cards de resumo ───────────────────────────────────────────────────
    baseline      = result["baseline"]
    context_adj   = result["context_adj"]
    fixed_adj     = result["fixed_adj"]
    d1_adj = _D_OPTIONS["d1_janela"].get(decisions["d1_janela"], 0)
    d4_adj = _D_OPTIONS["d4_densidade"].get(decisions["d4_densidade"], 0)
    d5_adj = _D_OPTIONS["d5_manejo"].get(decisions["d5_manejo"], 0)
    variable_adj  = d1_adj + d4_adj + d5_adj
    ev_final      = user_sel["ev"]

    m1, m2, m3, m4, m5 = st.columns(5)
    for col, label_key, sub_key, value in [
        (m1, "dash_m_baseline", "dash_m_sub_baseline", baseline),
        (m2, "dash_m_context",  "dash_m_sub_context",  context_adj),
        (m3, "dash_m_decision", "dash_m_sub_decision",  fixed_adj + variable_adj),
        (m4, "dash_m_rain",     "dash_m_sub_rain",      round(ev_chuva, 2)),
        (m5, "dash_m_final",    "dash_m_sub_final",     ev_final),
    ]:
        label = t(label_key, lang)
        sub   = t(sub_key, lang)
        is_delta = label_key not in ("dash_m_baseline", "dash_m_final")
        color = "#2e7d32" if value > 0 else ("#c62828" if value < 0 else "#111")
        val_str = f"{value:+.1f}" if is_delta else f"{value:.1f}"
        val_color = color if is_delta else "#111"
        with col:
            st.markdown(f"""<div class="metric-card">
                <div class="mc-label">{label}</div>
                <div class="mc-value" style="color:{val_color}">{val_str}</div>
                <div class="mc-sub">{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Waterfall ─────────────────────────────────────────────────────────
    st.markdown(t("dash_waterfall_title", lang))
    st.caption(t("dash_waterfall_caption", lang))

    labels, measures, values, colors_wf, texts = [], [], [], [], []

    # Baseline
    labels.append(t("dash_wf_baseline", lang)); measures.append("absolute"); values.append(baseline)
    colors_wf.append("#455a64"); texts.append(f"{baseline:.0f}")

    # C1–C7
    for key, label in _C_LABELS.items():
        adj = _C_OPTIONS[key].get(context[key], 0)
        labels.append(label); measures.append("relative"); values.append(adj)
        colors_wf.append("#1565c0" if adj >= 0 else "#c62828")
        texts.append(f"{adj:+.0f}")

    # D2, D3, D6 (fixed)
    for key in ["d2_cultivar", "d3_tsi", "d6_tecnologia"]:
        adj = _D_OPTIONS[key].get(decisions[key], 0)
        labels.append(_D_LABELS[key]); measures.append("relative"); values.append(adj)
        colors_wf.append("#2e7d32" if adj >= 0 else "#c62828")
        texts.append(f"{adj:+.0f}")

    # D1, D4, D5 (variable)
    for key in ["d1_janela", "d4_densidade", "d5_manejo"]:
        adj = _D_OPTIONS[key].get(decisions[key], 0)
        labels.append(_D_LABELS[key]); measures.append("relative"); values.append(adj)
        colors_wf.append("#2e7d32" if adj >= 0 else "#c62828")
        texts.append(f"{adj:+.0f}")

    # Rain EV
    labels.append(t("dash_wf_rain", lang)); measures.append("relative"); values.append(round(ev_chuva, 2))
    colors_wf.append("#f57c00" if ev_chuva >= 0 else "#c62828")
    texts.append(f"{ev_chuva:+.1f}")

    # Total
    labels.append(t("dash_wf_final", lang)); measures.append("total"); values.append(ev_final)
    colors_wf.append("#111111"); texts.append(f"{ev_final:.1f}")

    fig_wf = go.Figure(go.Waterfall(
        orientation="v",
        measure=measures,
        x=labels,
        y=values,
        text=texts,
        textposition="outside",
        connector=dict(line=dict(color="#ccc", width=1, dash="dot")),
        increasing=dict(marker_color="#2e7d32"),
        decreasing=dict(marker_color="#c62828"),
        totals=dict(marker_color="#111"),
    ))
    fig_wf.update_layout(
        height=480,
        margin=dict(t=20, l=20, r=20, b=20),
        yaxis_title="sc/ha",
        showlegend=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#1a1a2e", size=11),
        xaxis=dict(tickfont=dict(color="#1a1a2e", size=11)),
        yaxis=dict(gridcolor="#c8c0b0", tickfont=dict(color="#1a1a2e", size=11),
                   title_font=dict(color="#1a1a2e")),
    )
    st.plotly_chart(fig_wf, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns(2)

    # ── Radar — Perfil de Contexto ────────────────────────────────────────
    with col_left:
        st.markdown(t("dash_radar_title", lang))
        st.caption(t("dash_radar_caption", lang))

        _C_RANGES = {
            "c1_regiao": (-6, 5), "c2_textura": (-7, 5), "c3_ph": (-6, 4),
            "c4_drenagem": (-8, 3), "c5_aptidao": (-7, 5), "c6_area": (-1, 2),
            "c7_enso": (-3, 3),
        }
        radar_labels = list(_C_LABELS.values())
        radar_values = []
        for key in _C_LABELS:
            adj = _C_OPTIONS[key].get(context[key], 0)
            lo, hi = _C_RANGES[key]
            span = hi - lo
            normalized = (adj - lo) / span if span else 0.5
            radar_values.append(round(normalized, 3))

        radar_values_closed = radar_values + [radar_values[0]]
        radar_labels_closed = radar_labels + [radar_labels[0]]

        fig_radar = go.Figure(go.Scatterpolar(
            r=radar_values_closed,
            theta=radar_labels_closed,
            fill="toself",
            fillcolor="rgba(21, 101, 192, 0.15)",
            line=dict(color="#1565c0", width=2),
            marker=dict(size=6, color="#1565c0"),
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 1], tickvals=[0, 0.5, 1],
                                ticktext=[t("dash_radar_min", lang), t("dash_radar_mid", lang), t("dash_radar_max", lang)],
                                tickfont=dict(color="#1a1a2e", size=10),
                                gridcolor="#c8c0b0", linecolor="#c8c0b0"),
                angularaxis=dict(linecolor="#c8c0b0", gridcolor="#c8c0b0",
                                 tickfont=dict(color="#1a1a2e", size=11)),
                bgcolor="rgba(0,0,0,0)",
            ),
            height=380,
            margin=dict(t=20, l=40, r=40, b=20),
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#1a1a2e", size=11),
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    # ── Yield por cenário de chuva ────────────────────────────────────────
    with col_right:
        st.markdown(t("dash_bar_title", lang))
        st.caption(t("dash_bar_caption", lang))

        optimal_idx   = result["criteria"]["bayes_ev"]["path_idx"]
        optimal_path  = result["paths"][optimal_idx]
        optimal_yields = result["matrix"][optimal_idx]

        rain_short = [s.split(" ")[0] for s in rain_states]

        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(
            name=t("dash_bar_your", lang),
            x=rain_short,
            y=user_sel["yields"],
            marker_color="#1565c0",
            text=[f"{v:.1f}" for v in user_sel["yields"]],
            textposition="outside",
        ))
        fig_bar.add_trace(go.Bar(
            name=t("dash_bar_best", lang),
            x=rain_short,
            y=optimal_yields,
            marker_color="#2e7d32",
            text=[f"{v:.1f}" for v in optimal_yields],
            textposition="outside",
        ))
        fig_bar.update_layout(
            barmode="group",
            height=380,
            yaxis_title="sc/ha",
            margin=dict(t=20, l=20, r=20, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02,
                        font=dict(color="#1a1a2e", size=11)),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#1a1a2e", size=11),
            xaxis=dict(tickfont=dict(color="#1a1a2e", size=11)),
            yaxis=dict(gridcolor="#c8c0b0", tickfont=dict(color="#1a1a2e", size=11),
                       title_font=dict(color="#1a1a2e")),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # ── Sensibilidade — ranking de impacto ────────────────────────────────
    st.markdown(t("dash_sens_title", lang))
    st.caption(t("dash_sens_caption", lang))

    sens_rows = []
    for key, label in {**_C_LABELS, **_D_LABELS}.items():
        opts = _C_OPTIONS.get(key) or _D_OPTIONS.get(key, {})
        val  = context.get(key) or decisions.get(key, "")
        adj  = opts.get(val, 0)
        tipo = t("dash_sens_type_ctx", lang) if key.startswith("c") else t("dash_sens_type_dec", lang)
        sens_rows.append({
            t("dash_sens_col_node", lang): label,
            t("dash_sens_col_adj", lang):  adj,
            t("dash_sens_col_abs", lang):  abs(adj),
            t("dash_sens_col_type", lang): tipo,
        })

    _abs_col  = t("dash_sens_col_abs", lang)
    _adj_col  = t("dash_sens_col_adj", lang)
    _node_col = t("dash_sens_col_node", lang)
    _type_col = t("dash_sens_col_type", lang)
    _ctx_val  = t("dash_sens_type_ctx", lang)

    df_sens = pd.DataFrame(sens_rows).sort_values(_abs_col, ascending=True)

    fig_sens = go.Figure(go.Bar(
        x=df_sens[_adj_col],
        y=df_sens[_node_col],
        orientation="h",
        marker_color=[
            "#1565c0" if tp == _ctx_val else "#2e7d32"
            if v >= 0 else "#c62828"
            for tp, v in zip(df_sens[_type_col], df_sens[_adj_col])
        ],
        text=[f"{v:+.0f}" for v in df_sens[_adj_col]],
        textposition="outside",
    ))
    fig_sens.add_vline(x=0, line_color="#999", line_width=1)
    fig_sens.update_layout(
        height=420,
        xaxis_title=t("dash_sens_col_adj", lang),
        margin=dict(t=10, l=20, r=60, b=20),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#1a1a2e", size=11),
        xaxis=dict(gridcolor="#c8c0b0", tickfont=dict(color="#1a1a2e", size=11),
                   title_font=dict(color="#1a1a2e")),
        yaxis=dict(tickfont=dict(color="#1a1a2e", size=11)),
        showlegend=False,
    )
    st.plotly_chart(fig_sens, use_container_width=True)
    st.caption(t("dash_sens_caption2", lang))

    # ── Cross-navigation ──────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    _, col_bi = st.columns([4, 1])
    with col_bi:
        if st.button(t("dash_goto_bi", lang), use_container_width=True):
            navigate("bi_dashboard")
