"""Página de Resultados — reformulada para o produtor rural."""

from __future__ import annotations
import io
import streamlit as st
import plotly.graph_objects as go_plotly
import plotly.express as px
import pandas as pd
from datetime import datetime

from frontend.navigation import go
from frontend.api import monte_carlo as run_mc_api
from frontend.views.results_helpers import (
    _D1_SHORT, _D2_SHORT, _D3_SHORT, _D4_SHORT, _D5_SHORT, _D6_SHORT,
    _CRITERIA_LABELS,
    _pdf_safe, _shorten, _get_criteria_tags, _gen_card_summary,
    _janela_guidance, _densidade_guidance, _manejo_guidance,
)
from frontend.views.results_pdf import _build_pdf


# ── Página principal ──────────────────────────────────────────────────────────

def render() -> None:
    result = st.session_state.get("sim_result")
    if not result:
        st.warning("No simulation found. Go back to the form.")
        if st.button("← Go to Simulation"):
            go("input")
        return

    paths     = result["paths"]
    criteria  = result["criteria"]
    states    = result["rain_states"]
    probs     = result["rain_probs"]
    user_sel  = result["user_selection"]
    matrix    = result["matrix"]
    baseline  = result["baseline"]
    decisions = st.session_state.get("sim_decisions", {})
    display   = st.session_state.get("sim_display", {})
    auth      = st.session_state.get("auth", {})

    optimal_idx = criteria["bayes_ev"]["path_idx"]
    ev_vals     = criteria["bayes_ev"]["criterion_values"]

    user_row = next(
        (i + 1 for i, p in enumerate(paths)
         if p["d1"] == user_sel["d1"] and p["d4"] == user_sel["d4"] and p["d5"] == user_sel["d5"]),
        None,
    )

    st.markdown('<div class="page-title">Simulation Results</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Soy · Mato Grosso</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Layout: conteúdo principal (75%) + resumo do cenário (25%)
    col_main, col_sidebar = st.columns([3, 1], gap="large")

    with col_sidebar:
        _render_scenario_sidebar(display)
        _render_comparison_charts(paths, ev_vals, matrix, states, probs, criteria, baseline)

    with col_main:
        # ── Métricas ──────────────────────────────────────────────────────────
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(f"""<div class="metric-card">
                <div class="mc-label">Regional reference</div>
                <div class="mc-value">{baseline:.0f}</div>
                <div class="mc-sub">sc/ha · average MT yield</div>
                <div class="mc-caption">Starting point before considering your field context</div>
            </div>""", unsafe_allow_html=True)
        with m2:
            st.markdown(f"""<div class="metric-card">
                <div class="mc-label">Your field's starting point</div>
                <div class="mc-value">{result['base_effective']:.0f}</div>
                <div class="mc-sub">sc/ha · after soil, cultivar and seed treatment</div>
                <div class="mc-caption">Reference adjusted for field context and your fixed choices</div>
            </div>""", unsafe_allow_html=True)
        with m3:
            user_ev_color = "#2e7d32" if user_sel['ev'] >= baseline else "#c62828"
            user_mc = next(
                (p.get("mc") for p in paths
                 if p["d1"] == user_sel["d1"] and p["d4"] == user_sel["d4"] and p["d5"] == user_sel["d5"]),
                None,
            )
            interval_str = (
                f"90% interval: {user_mc['p5']:.0f}–{user_mc['p95']:.0f} sc/ha"
                if user_mc else ""
            )
            st.markdown(f"""<div class="metric-card">
                <div class="mc-label">Expected yield — your choice</div>
                <div class="mc-value" style="color:{user_ev_color}">{user_sel['ev']:.1f}</div>
                <div class="mc-sub">sc/ha · {_D1_SHORT.get(user_sel['d1'], user_sel['d1'])}</div>
                <div class="mc-caption">{interval_str}</div>
            </div>""", unsafe_allow_html=True)
        with m4:
            best_path  = paths[optimal_idx]
            best_mc    = best_path.get("mc") or {}
            best_short = _D1_SHORT.get(best_path["d1"], best_path["d1"])
            best_interval = (
                f"90% interval: {best_mc['p5']:.0f}–{best_mc['p95']:.0f} sc/ha"
                if best_mc else ""
            )
            st.markdown(f"""<div class="metric-card">
                <div class="mc-label">Best recommended scenario</div>
                <div class="mc-value" style="color:#2e7d32">{criteria['bayes_ev']['value']:.1f}</div>
                <div class="mc-sub">sc/ha · {best_short}</div>
                <div class="mc-caption">{best_interval}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Recomendações ──────────────────────────────────────────────────────
        st.markdown('<div class="section-hdr">Recommendations for Your Season</div>', unsafe_allow_html=True)
        _render_recommendations(
            paths, criteria, ev_vals, states, probs,
            decisions, display, matrix, user_sel, optimal_idx, user_row,
            baseline, result, auth,
        )

    # ── Seções em largura total — fora das colunas ─────────────────────────────
    upgrade = result.get("upgrade_potential")
    if upgrade:
        st.markdown("<br>", unsafe_allow_html=True)
        _render_upgrade_potential(upgrade, decisions)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-hdr">Export / Share</div>', unsafe_allow_html=True)
    _render_global_actions(result, display, auth, paths, ev_vals, states, probs, matrix, criteria, baseline)

    # ── Cálculos detalhados (colapsado) ───────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("📊 Want to understand how we got these recommendations?"):
        st.caption(
            "This section shows the technical calculations behind the recommendations: "
            "payoff matrix, decision criteria and hierarchical view."
        )
        tab_matrix, tab_criteria, tab_tree = st.tabs([
            "Scenario Analysis", "Decision Criteria", "Hierarchical View"
        ])
        with tab_matrix:
            _render_matrix(paths, matrix, criteria, ev_vals, states, probs, optimal_idx, user_row)
        with tab_criteria:
            _render_criteria(paths, criteria, ev_vals, optimal_idx, user_row)
        with tab_tree:
            _render_tree(paths, matrix, states, probs, ev_vals, optimal_idx, user_row)

    # ── Navegação ──────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    col_back, _, col_dash, col_new = st.columns([1, 3, 1, 1])
    with col_back:
        if st.button("← Edit", use_container_width=True):
            go("input")
    with col_dash:
        if st.button("Dashboard →", use_container_width=True):
            go("dashboard")
    with col_new:
        if st.button("New simulation", type="primary", use_container_width=True):
            st.session_state.sim_result = None
            st.session_state.input_step = 1
            go("input")


# ── Potencial de upgrade D2/D3/D6 ────────────────────────────────────────────

_UPGRADE_LABELS = {
    "d2_cultivar":   ("Cultivar",        "Switching cultivar may change expected yield by:"),
    "d3_tsi":        ("Seed Treatment",  "Switching seed treatment may change expected yield by:"),
    "d6_tecnologia": ("Planter",         "Switching planting technology may change expected yield by:"),
}

_UPGRADE_SHORT = {
    **{k: v for k, v in _D2_SHORT.items()},
    **{k: v for k, v in _D3_SHORT.items()},
    **{k: v for k, v in _D6_SHORT.items()},
}


def _render_upgrade_potential(upgrade: dict, decisions: dict) -> None:
    st.markdown('<div class="section-hdr">What changes if you upgrade cultivar, seed treatment or planter?</div>', unsafe_allow_html=True)
    st.caption(
        "Below is the expected impact of switching each of these choices, "
        "keeping the best window, density and disease management options as reference."
    )

    any_gain = False
    cols = st.columns(3)

    for col, node_key in zip(cols, ["d2_cultivar", "d3_tsi", "d6_tecnologia"]):
        label, desc = _UPGRADE_LABELS[node_key]
        node_data   = upgrade.get(node_key, {})
        current_val = node_data.get("current", decisions.get(node_key, "—"))
        options     = node_data.get("options", [])

        best_gain = options[0]["delta"] if options else 0.0

        with col:
            st.markdown(f"**{label}**")
            cur_short = _UPGRADE_SHORT.get(current_val, current_val)
            st.caption(f"Current: {cur_short}")

            if not options:
                st.info("You already selected the best available option.")
                continue

            if best_gain > 0:
                any_gain = True
                best_opt = _UPGRADE_SHORT.get(options[0]["option"], options[0]["option"])
                st.success(
                    f"**Switching to {best_opt}** can add up to "
                    f"**+{best_gain:.1f} expected sc/ha**."
                )
            elif best_gain < 0:
                st.info("Available alternatives perform worse than your current choice.")
            else:
                st.info("No alternative shows significant gain.")

            # Compact table with all alternatives
            if len(options) > 1:
                with st.expander(f"View all {label.lower()} options"):
                    for opt in options:
                        short = _UPGRADE_SHORT.get(opt["option"], opt["option"])
                        delta = opt["delta"]
                        color = "#2e7d32" if delta > 0 else "#c62828" if delta < 0 else "#555"
                        sign  = "+" if delta >= 0 else ""
                        st.markdown(
                            f"**{short}** — "
                            f"<span style='color:{color};font-weight:600'>{sign}{delta:.1f} sc/ha</span>",
                            unsafe_allow_html=True,
                        )

    if any_gain:
        st.info(
            "💡 These gains are model-based estimates of cultivar × management interactions. "
            "Consult your trusted dealer or agronomist to evaluate cost-benefit before deciding."
        )


# ── Sidebar de resumo do cenário ──────────────────────────────────────────────

def _render_scenario_sidebar(display: dict) -> None:
    ctx_keys = ["Region", "Texture", "pH", "Drainage", "Soil Type", "Area", "Climate Forecast"]
    dec_keys = ["Planting Period", "Cultivar", "Seed Treatment", "Density", "Disease Management", "Planter"]

    html = '<div class="scenario-sidebar">'
    html += '<div class="scenario-sidebar-title">Scenario Summary</div>'

    html += '<div style="font-size:0.6rem;font-weight:700;color:#6b6b8a;text-transform:uppercase;letter-spacing:0.1em;margin:8px 0 4px 0">Field</div>'
    for k in ctx_keys:
        v = display.get(k, "—")
        if v:
            html += (
                f'<div class="scenario-row">'
                f'<span class="scenario-key">{k}</span>'
                f'<span class="scenario-val">{v}</span>'
                f'</div>'
            )

    html += '<div style="font-size:0.6rem;font-weight:700;color:#6b6b8a;text-transform:uppercase;letter-spacing:0.1em;margin:12px 0 4px 0">Decisions</div>'
    for k in dec_keys:
        v = display.get(k, "—")
        if v:
            short_v = str(v)[:30] + ("…" if len(str(v)) > 30 else "")
            html += (
                f'<div class="scenario-row">'
                f'<span class="scenario-key">{k}</span>'
                f'<span class="scenario-val">{short_v}</span>'
                f'</div>'
            )
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


# ── Gráficos comparativos (sidebar) ──────────────────────────────────────────

def _render_comparison_charts(paths, ev_vals, matrix, states, probs, criteria, baseline):
    """Dois gráficos compactos abaixo do resumo do cenário."""

    ranked = sorted(enumerate(paths), key=lambda x: ev_vals[x[0]], reverse=True)
    top3   = ranked[:3]

    # ── Gráfico 1: EV das 3 recomendações vs referência ──────────────────────
    labels = [
        f"#{i+1} · {_D1_SHORT.get(p['d1'], p['d1'])}<br>"
        f"<span style='font-size:9px'>{_D4_SHORT.get(p['d4'],p['d4'])}</span>"
        for i, (_, p) in enumerate(top3)
    ]
    values  = [ev_vals[idx] for idx, _ in top3]
    colors  = ["#1a5c38", "#2d8a56", "#76c442"]
    has_mc  = [paths[idx].get("mc") for idx, _ in top3]

    fig1 = go_plotly.Figure()

    x_labels = [f"#{i+1}" for i in range(3)]

    # Barras de EV — verticais
    fig1.add_trace(go_plotly.Bar(
        x=x_labels,
        y=values,
        marker=dict(
            color=colors,
            line=dict(width=0),
        ),
        text=[f"<b>{v:.1f}</b>" for v in values],
        textposition="inside",
        textfont=dict(color="white", size=10),
        showlegend=False,
        hovertemplate="%{x}: %{y:.1f} sc/ha<extra></extra>",
    ))

    # Intervalo MC (p5–p95) como barras de erro verticais
    for i, (mc, (idx, _)) in enumerate(zip(has_mc, top3)):
        if mc:
            fig1.add_shape(
                type="line",
                x0=i - 0.25, x1=i + 0.25,
                y0=mc["p5"], y1=mc["p5"],
                line=dict(color="rgba(13,43,24,0.35)", width=1.5),
            )
            fig1.add_shape(
                type="line",
                x0=i - 0.25, x1=i + 0.25,
                y0=mc["p95"], y1=mc["p95"],
                line=dict(color="rgba(13,43,24,0.35)", width=1.5),
            )
            fig1.add_shape(
                type="line",
                x0=i, x1=i,
                y0=mc["p5"], y1=mc["p95"],
                line=dict(color="rgba(13,43,24,0.25)", width=1, dash="dot"),
            )

    fig1.add_hline(
        y=baseline,
        line_color="#f4a024",
        line_dash="dot",
        line_width=1.5,
        annotation_text=f"Ref {baseline:.0f}",
        annotation_font_size=8,
        annotation_position="right",
        annotation_font_color="#b35c00",
    )

    all_vals = values + ([mc["p5"] for mc in has_mc if mc] + [mc["p95"] for mc in has_mc if mc] if any(has_mc) else [])
    y_min = min(all_vals + [baseline]) * 0.88
    y_max = max(all_vals + [baseline]) * 1.10

    fig1.update_layout(
        height=240,
        margin=dict(t=8, l=0, r=30, b=4),
        xaxis=dict(
            tickfont=dict(size=10, color="#1a3a2a"),
            showgrid=False,
        ),
        yaxis=dict(
            showgrid=True, gridcolor="#d4eedd", zeroline=False,
            tickfont=dict(size=8, color="#1a3a2a"),
            title=dict(text="sc/ha", font=dict(size=8, color="#4a8a6a")),
            range=[y_min, y_max],
        ),
        plot_bgcolor="#f4faf7",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#1a3a2a", size=9),
        bargap=0.35,
    )

    st.markdown(
        '<div style="font-size:0.65rem;font-weight:700;color:#4a8a6a;'
        'text-transform:uppercase;letter-spacing:0.1em;margin:14px 0 4px 0">'
        'Expected yield · top 3</div>',
        unsafe_allow_html=True,
    )
    st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})

    # ── Gráfico 2: Melhor recomendação × cenário climático ────────────────────
    optimal_idx    = criteria["bayes_ev"]["path_idx"]
    optimal_yields = matrix[optimal_idx]
    state_shorts   = [s.split(" ")[0] for s in states]
    bar_colors2    = ["#1a5c38" if y >= baseline else "#c62828" for y in optimal_yields]

    fig2 = go_plotly.Figure()
    fig2.add_trace(go_plotly.Bar(
        x=state_shorts,
        y=optimal_yields,
        marker=dict(color=bar_colors2, line=dict(width=0)),
        text=[f"<b>{y:.0f}</b>" for y in optimal_yields],
        textposition="outside",
        textfont=dict(size=9, color="#1a3a2a"),
        showlegend=False,
        hovertemplate="%{x}: %{y:.1f} sc/ha<extra></extra>",
    ))
    fig2.add_hline(
        y=baseline,
        line_color="#f4a024",
        line_dash="dot",
        line_width=1.5,
        annotation_text=f"Ref {baseline:.0f}",
        annotation_font_size=8,
        annotation_position="right",
        annotation_font_color="#b35c00",
    )
    # Labels de probabilidade abaixo dos estados
    for i, (s, p) in enumerate(zip(state_shorts, probs)):
        fig2.add_annotation(
            x=s, y=min(optimal_yields) * 0.92,
            text=f"{p:.0%}",
            showarrow=False,
            font=dict(size=8, color="#4a8a6a"),
        )
    fig2.update_layout(
        height=240,
        margin=dict(t=20, l=0, r=40, b=4),
        xaxis=dict(tickfont=dict(size=9, color="#1a3a2a"), showgrid=False),
        yaxis=dict(
            showgrid=True, gridcolor="#d4eedd", zeroline=False,
            tickfont=dict(size=8, color="#1a3a2a"),
            title=dict(text="sc/ha", font=dict(size=8, color="#4a8a6a")),
            range=[min(optimal_yields) * 0.85, max(optimal_yields) * 1.12],
        ),
        plot_bgcolor="#f4faf7",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#1a3a2a", size=9),
        bargap=0.4,
    )

    st.markdown(
        '<div style="font-size:0.65rem;font-weight:700;color:#4a8a6a;'
        'text-transform:uppercase;letter-spacing:0.1em;margin:8px 0 4px 0">'
        'Recommendation #1 · by climate</div>',
        unsafe_allow_html=True,
    )
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    # ── Gráfico 3: Radar — top 3 × cenários climáticos ───────────────────────
    st.markdown(
        '<div style="font-size:0.65rem;font-weight:700;color:#4a8a6a;'
        'text-transform:uppercase;letter-spacing:0.1em;margin:14px 0 4px 0">'
        'Climate scenario profile · top 3</div>',
        unsafe_allow_html=True,
    )

    radar_colors  = ["#1a5c38", "#2d8a56", "#76c442"]
    radar_fills   = ["rgba(26,92,56,0.12)", "rgba(45,138,86,0.10)", "rgba(118,196,66,0.10)"]
    theta_labels  = state_shorts + [state_shorts[0]]

    fig3 = go_plotly.Figure()
    for i, (idx, _) in enumerate(top3):
        r_vals = list(matrix[idx]) + [matrix[idx][0]]
        fig3.add_trace(go_plotly.Scatterpolar(
            r=r_vals,
            theta=theta_labels,
            fill="toself",
            fillcolor=radar_fills[i],
            line=dict(color=radar_colors[i], width=2),
            name=f"#{i+1}",
            hovertemplate=f"#{{i+1}} %{{theta}}: %{{r:.1f}} sc/ha<extra></extra>",
        ))
    fig3.add_trace(go_plotly.Scatterpolar(
        r=[baseline] * (len(state_shorts) + 1),
        theta=theta_labels,
        mode="lines",
        line=dict(color="#f4a024", width=1.5, dash="dot"),
        name="Ref",
        hovertemplate="Reference: %{r:.0f} sc/ha<extra></extra>",
    ))
    fig3.update_layout(
        height=230,
        margin=dict(t=12, l=0, r=0, b=8),
        polar=dict(
            bgcolor="#f4faf7",
            radialaxis=dict(
                visible=True, showticklabels=True,
                tickfont=dict(size=7, color="#4a8a6a"),
                gridcolor="#c8e6d4", linecolor="#c8e6d4",
                tickformat=".0f",
            ),
            angularaxis=dict(
                tickfont=dict(size=9, color="#1a3a2a"),
                linecolor="#c8e6d4", gridcolor="#c8e6d4",
            ),
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(font=dict(size=8, color="#1a3a2a"), orientation="h",
                    y=-0.08, x=0.5, xanchor="center"),
        showlegend=True,
        font=dict(color="#1a3a2a", size=9),
    )
    st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

    # ── Cards de risco — top 3 ────────────────────────────────────────────────
    st.markdown(
        '<div style="font-size:0.65rem;font-weight:700;color:#4a8a6a;'
        'text-transform:uppercase;letter-spacing:0.1em;margin:14px 0 6px 0">'
        'Risk of falling below reference</div>',
        unsafe_allow_html=True,
    )
    risk_html = ""
    for i, (idx, path) in enumerate(top3):
        mc   = path.get("mc") or {}
        ev   = ev_vals[idx]
        diff = ev - baseline
        diff_sign  = "+" if diff >= 0 else ""
        diff_color = "#2e7d32" if diff >= 0 else "#c62828"
        risk_pct   = mc.get("p_below", None)
        if risk_pct is not None:
            bar_w = int(risk_pct * 100)
            bar_color = "#c62828" if risk_pct > 0.25 else "#f57c00" if risk_pct > 0.10 else "#2e7d32"
            risk_txt  = f"{risk_pct:.0%}"
            risk_bar  = (
                f'<div style="background:#e8f5e9;border-radius:4px;height:5px;margin-top:3px">'
                f'<div style="background:{bar_color};width:{bar_w}%;height:5px;border-radius:4px;transition:width .3s"></div></div>'
            )
        else:
            risk_txt = "—"
            risk_bar = ""
        risk_html += (
            f'<div style="background:#fff;border:1px solid #e4e4f0;border-radius:8px;'
            f'padding:8px 10px;margin-bottom:6px">'
            f'<div style="display:flex;justify-content:space-between;align-items:center">'
            f'<span style="font-size:0.72rem;font-weight:700;color:#1a3a2a">#{i+1} — {ev:.1f} sc/ha</span>'
            f'<span style="font-size:0.7rem;font-weight:600;color:{diff_color}">{diff_sign}{diff:.1f}</span>'
            f'</div>'
            f'<div style="font-size:0.68rem;color:#6b6b8a;margin-top:2px">Risk below ref.: <b style="color:#1a3a2a">{risk_txt}</b></div>'
            f'{risk_bar}'
            f'</div>'
        )
    st.markdown(risk_html, unsafe_allow_html=True)

    # ── Ilustração de soja ────────────────────────────────────────────────────
    st.markdown("""
    <div style="margin-top:24px;display:flex;justify-content:center;align-items:flex-end;
                gap:6px;opacity:0.18;pointer-events:none">

      <!-- Planta esquerda — menor -->
      <svg width="52" height="90" viewBox="0 0 210 210" fill="none">
        <line x1="105" y1="205" x2="105" y2="70" stroke="#1a5c38" stroke-width="6" stroke-linecap="round"/>
        <ellipse cx="105" cy="72" rx="10" ry="15" fill="#1a5c38" transform="rotate(-5 105 72)"/>
        <ellipse cx="95"  cy="80" rx="8"  ry="12" fill="#1a5c38" transform="rotate(10 95 80)"/>
        <ellipse cx="115" cy="80" rx="8"  ry="12" fill="#1a5c38" transform="rotate(-10 115 80)"/>
        <path d="M105 110 C90 100 76 88 82 74 C92 84 102 100 105 110Z" fill="#1a5c38"/>
        <path d="M105 110 C120 100 134 88 128 74 C118 84 108 100 105 110Z" fill="#1a5c38"/>
        <path d="M105 152 C86 140 70 122 78 104 C90 118 100 138 105 152Z" fill="#1a5c38" opacity="0.8"/>
        <path d="M105 152 C124 140 140 122 132 104 C120 118 110 138 105 152Z" fill="#1a5c38" opacity="0.8"/>
      </svg>

      <!-- Planta central — maior -->
      <svg width="72" height="120" viewBox="0 0 210 210" fill="none">
        <line x1="105" y1="205" x2="105" y2="30" stroke="#0d2b18" stroke-width="6" stroke-linecap="round"/>
        <ellipse cx="105" cy="32" rx="11" ry="17" fill="#0d2b18" transform="rotate(-8 105 32)"/>
        <ellipse cx="94"  cy="42" rx="9"  ry="14" fill="#0d2b18" transform="rotate(12 94 42)"/>
        <ellipse cx="116" cy="42" rx="9"  ry="14" fill="#0d2b18" transform="rotate(-12 116 42)"/>
        <path d="M105 80 C88 68 72 54 78 40 C88 52 100 68 105 80Z" fill="#0d2b18"/>
        <path d="M105 80 C122 68 138 54 132 40 C122 52 110 68 105 80Z" fill="#0d2b18"/>
        <ellipse cx="76"  cy="84" rx="7" ry="12" fill="#0d2b18" transform="rotate(38 76 84)" opacity="0.8"/>
        <ellipse cx="134" cy="84" rx="7" ry="12" fill="#0d2b18" transform="rotate(-38 134 84)" opacity="0.8"/>
        <path d="M105 125 C84 112 65 94 74 76 C87 90 101 110 105 125Z" fill="#0d2b18"/>
        <path d="M105 125 C126 112 145 94 136 76 C123 90 109 110 105 125Z" fill="#0d2b18"/>
        <path d="M105 168 C80 153 58 132 68 110 C84 128 100 150 105 168Z" fill="#0d2b18" opacity="0.7"/>
        <path d="M105 168 C130 153 152 132 142 110 C126 128 110 150 105 168Z" fill="#0d2b18" opacity="0.7"/>
      </svg>

      <!-- Planta direita — menor, espelhada -->
      <svg width="52" height="90" viewBox="0 0 210 210" fill="none" style="transform:scaleX(-1)">
        <line x1="105" y1="205" x2="105" y2="70" stroke="#2d8a56" stroke-width="6" stroke-linecap="round"/>
        <ellipse cx="105" cy="72" rx="10" ry="15" fill="#2d8a56" transform="rotate(-5 105 72)"/>
        <ellipse cx="95"  cy="80" rx="8"  ry="12" fill="#2d8a56" transform="rotate(10 95 80)"/>
        <ellipse cx="115" cy="80" rx="8"  ry="12" fill="#2d8a56" transform="rotate(-10 115 80)"/>
        <path d="M105 110 C90 100 76 88 82 74 C92 84 102 100 105 110Z" fill="#2d8a56"/>
        <path d="M105 110 C120 100 134 88 128 74 C118 84 108 100 105 110Z" fill="#2d8a56"/>
        <path d="M105 152 C86 140 70 122 78 104 C90 118 100 138 105 152Z" fill="#2d8a56" opacity="0.8"/>
        <path d="M105 152 C124 140 140 122 132 104 C120 118 110 138 105 152Z" fill="#2d8a56" opacity="0.8"/>
      </svg>

    </div>
    <div style="text-align:center;font-size:0.6rem;color:#b0c8b8;margin-top:6px;letter-spacing:0.08em">
      SOY · MATO GROSSO
    </div>
    """, unsafe_allow_html=True)


# ── Recomendações ─────────────────────────────────────────────────────────────

def _render_recommendations(paths, criteria, ev_vals, states, probs, decisions,
                             display, matrix, user_sel, optimal_idx, user_row,
                             baseline, result, auth):
    ranked = sorted(enumerate(paths), key=lambda x: ev_vals[x[0]], reverse=True)
    top3   = ranked[:3]
    d2 = decisions.get("d2_cultivar", "")
    d3 = decisions.get("d3_tsi", "")
    d6 = decisions.get("d6_tecnologia", "")

    for rank_num, (path_idx, path) in enumerate(top3, start=1):
        rank_cls   = f"rank-{rank_num}" if rank_num <= 3 else ""
        rank_label = {1: "🥇 Top recommendation", 2: "🥈 Alternative", 3: "🥉 Alternative"}.get(rank_num, f"#{rank_num}")

        ev         = ev_vals[path_idx]
        mc         = path.get("mc")
        yields_row = matrix[path_idx]
        tags       = _get_criteria_tags(path_idx, criteria)
        delta      = ev - baseline
        delta_color = "#2e7d32" if delta >= 0 else "#c62828"
        delta_sign  = "+" if delta >= 0 else ""

        summary = _gen_card_summary(path, ev, mc, baseline, states, probs, yields_row, rank_num)

        # ── Constrói MC html — sem newlines para não quebrar o bloco CommonMark ──
        if mc:
            risk_color = "#c62828" if mc["p_below"] > 0.25 else "#f57c00" if mc["p_below"] > 0.10 else "#2e7d32"
            mc_html = (
                f'<div class="rec-yield-interval">90% interval: {mc["p5"]:.0f}–{mc["p95"]:.0f} sc/ha</div>'
                f'<div class="rec-risk-label" style="color:{risk_color}">{mc["p_below"]:.0%} chance of falling below reference</div>'
            )
        else:
            mc_html = ""

        # ── Constrói cenários html — sem newlines ─────────────────────────────
        scenarios_html = ""
        for i_s, state in enumerate(states):
            y_val = yields_row[i_s]
            bar_color = "#2e7d32" if y_val >= baseline else "#c62828"
            state_short = state.split(" ")[0]
            scenarios_html += (
                f'<div style="display:flex;justify-content:space-between;align-items:center;'
                f'padding:5px 0;border-bottom:1px solid #f0f0f0;font-size:0.84rem">'
                f'<span style="color:#3a3a5c"><strong>{state_short}</strong> ({probs[i_s]:.0%})</span>'
                f'<span style="color:{bar_color};font-weight:700">{y_val:.1f} sc/ha</span></div>'
            )

        # ── Constrói tags html ────────────────────────────────────────────────
        tags_html = ""
        if tags:
            tags_inner = "".join(f'<span class="crit-tag">{t}</span>' for t in tags[:3])
            tags_html = f'<div class="rec-criteria-row" style="margin-top:12px">{tags_inner}</div>'

        # ── Constrói grid de decisões html ────────────────────────────────────
        d1_short = _D1_SHORT.get(path["d1"], path["d1"])
        d4_short = _D4_SHORT.get(path["d4"], path["d4"])
        d5_short = _D5_SHORT.get(path["d5"], path["d5"])
        d2_short = _D2_SHORT.get(d2, d2)
        d3_short = _D3_SHORT.get(d3, d3)
        d6_short = _D6_SHORT.get(d6, d6)

        # ── Renderiza o card — HTML concatenado sem linhas em branco ────────────
        # (Linhas em branco no f-string encerram o bloco HTML do CommonMark)
        decisions_grid = (
            f'<div class="rec-decisions-grid">'
            f'<div class="dec-item"><div class="dec-label">Planting Window</div><div class="dec-value">{d1_short}</div></div>'
            f'<div class="dec-item"><div class="dec-label">Density</div><div class="dec-value">{d4_short}</div></div>'
            f'<div class="dec-item"><div class="dec-label">Disease Management</div><div class="dec-value">{d5_short}</div></div>'
            f'<div class="dec-item"><div class="dec-label">Cultivar</div><div class="dec-value">{d2_short}</div></div>'
            f'<div class="dec-item"><div class="dec-label">Seed Treatment</div><div class="dec-value">{d3_short}</div></div>'
            f'<div class="dec-item"><div class="dec-label">Planter</div><div class="dec-value">{d6_short}</div></div>'
            f'</div>'
        )
        yield_col = (
            f'<div style="min-width:150px">'
            f'<div class="rec-yield-big">{ev:.1f}</div>'
            f'<div class="rec-yield-unit">expected sc/ha</div>'
            f'<div class="rec-yield-range" style="color:{delta_color};font-weight:600">{delta_sign}{delta:.1f} sc/ha vs. reference</div>'
            f'{mc_html}'
            f'</div>'
        )
        scenario_col = (
            f'<div style="flex:1;min-width:200px;border-left:1px solid #e4e4f0;padding-left:20px">'
            f'<div style="font-size:0.68rem;font-weight:700;color:#6b6b8a;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:8px">By climate scenario</div>'
            f'{scenarios_html}'
            f'</div>'
        )
        card_html = (
            f'<div class="rec-card-v2 {rank_cls}">'
            f'<div class="rec-rank-badge {rank_cls}">{rank_label}</div>'
            f'<div class="rec-summary-text">{summary}</div>'
            f'<div style="display:flex;gap:24px;margin:16px 0;flex-wrap:wrap">{yield_col}{scenario_col}</div>'
            f'{tags_html}'
            f'{decisions_grid}'
            f'</div>'
        )
        st.markdown(card_html, unsafe_allow_html=True)

        # ── Expander e botões — fora do HTML mas logo abaixo do card ─────────
        with st.expander(f"📋 How to apply — recommendation {rank_num}"):
            g1, g2 = st.columns(2)
            with g1:
                st.markdown("**Why this combination?**")
                if tags:
                    st.markdown(f"This strategy is identified by the analysis as: **{', '.join(tags[:2])}**.")
                delta_str = f"+{ev - baseline:.1f}" if ev >= baseline else f"{ev - baseline:.1f}"
                st.markdown(
                    f"With **{ev:.1f} expected sc/ha** ({delta_str} sc/ha vs. regional reference), "
                    f"it represents the best balance between return and climate risk exposure for your context."
                )
                if mc:
                    st.markdown(
                        f"In 90% of simulations, yield would fall between "
                        f"**{mc['p5']:.0f} and {mc['p95']:.0f} sc/ha**."
                    )
            with g2:
                st.markdown("**Application guidance:**")
                for lbl, guidance in [
                    ("Planting Window:", _janela_guidance(path["d1"])),
                    ("Density:", _densidade_guidance(path["d4"])),
                    ("Disease Management:", _manejo_guidance(path["d5"])),
                ]:
                    if guidance:
                        st.markdown(f"**{lbl}** {guidance}")

        col_pdf, col_csv, _ = st.columns([1, 1, 3])
        with col_pdf:
            try:
                user_name = auth.get("name", "Produtor")
                pdf_bytes = _build_pdf(
                    result, display, user_name, paths, ev_vals,
                    states, probs, matrix, criteria, baseline,
                )
                st.download_button(
                    f"⬇ Download PDF #{rank_num}",
                    data=pdf_bytes,
                    file_name=f"recommendation_{rank_num}.pdf",
                    mime="application/pdf",
                    key=f"pdf_rec_{rank_num}",
                    use_container_width=True,
                )
            except Exception as e:
                st.caption(f"PDF unavailable: {e}")
        with col_csv:
            rows = [{
                "path": path_idx + 1,
                "D1_window": path["d1"],
                "D4_density": path["d4"],
                "D5_management": path["d5"],
                "EV_sc_ha": ev,
                **{states[j].split(" ")[0]: matrix[path_idx][j] for j in range(len(states))},
                **({"MC_mean": mc["mean"], "MC_P5": mc["p5"], "MC_P95": mc["p95"]} if mc else {}),
            }]
            csv_data = pd.DataFrame(rows).to_csv(index=False).encode("utf-8")
            st.download_button(
                "⬇ Download CSV",
                data=csv_data,
                file_name=f"cenario_{rank_num}.csv",
                mime="text/csv",
                key=f"csv_rec_{rank_num}",
                use_container_width=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)

    # ── Comparação com seleção do usuário ──────────────────────────────────────
    if user_row and user_row - 1 != optimal_idx:
        gap_user = user_sel["ev"] - criteria["bayes_ev"]["value"]
        st.info(
            f"Your chosen window/density/management has an expected yield of **{user_sel['ev']:.1f} sc/ha**, "
            f"a difference of **{gap_user:+.1f} sc/ha** compared to the top recommendation."
        )


# ── Ações globais (PDF completo + exportação geral) ───────────────────────────

def _render_global_actions(result, display, auth, paths, ev_vals, states, probs, matrix, criteria, baseline):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        try:
            user_name = auth.get("name", "Farmer")
            pdf_bytes = _build_pdf(
                result, display, user_name, paths, ev_vals,
                states, probs, matrix, criteria, baseline,
            )
            st.download_button(
                "📄 Full Report (PDF)",
                data=pdf_bytes,
                file_name="season_report.pdf",
                mime="application/pdf",
                key="pdf_global",
                use_container_width=True,
                type="primary",
            )
        except Exception as e:
            st.error(f"Error generating PDF: {e}")

    with col2:
        rows = []
        for i, path in enumerate(paths):
            mc = path.get("mc") or {}
            row = {
                "#": i + 1,
                "Window": path["d1"],
                "Density": path["d4"],
                "Management": path["d5"],
                "Expected yield (sc/ha)": ev_vals[i],
            }
            for j, s in enumerate(states):
                row[s.split(" ")[0]] = matrix[i][j]
            if mc:
                row["MC Mean"]   = mc["mean"]
                row["MC P5"]     = mc["p5"]
                row["MC P95"]    = mc["p95"]
                row["Risk (%)"]  = round(mc["p_below"] * 100, 1)
            rows.append(row)
        df = pd.DataFrame(rows)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇ Full Table (CSV)",
            data=csv,
            file_name="full_simulation.csv",
            mime="text/csv",
            key="csv_global",
            use_container_width=True,
        )

    with col3:
        st.button(
            "🖨 Imprimir",
            key="btn_print",
            use_container_width=True,
            on_click=lambda: st.markdown(
                "<script>window.print();</script>", unsafe_allow_html=True
            ),
        )

    with col4:
        if st.button("📤 Share", key="btn_share", use_container_width=True):
            st.info("Generate the PDF report and share the file with your team or agronomist.")


# ── Análise de Cenários (Payoff Matrix) ───────────────────────────────────────

def _render_matrix(paths, matrix, criteria, ev_vals, states, probs, optimal_idx, user_row):
    prob_str = " · ".join(f"{s.split(' ')[0]} {p:.0%}" for s, p in zip(states, probs))
    st.markdown(f"**Conditional probabilities given ENSO:** {prob_str}")
    st.caption("Green = best expected result  ·  Blue = your selection")

    max_vals = criteria["maximax"]["criterion_values"]
    min_vals = criteria["wald"]["criterion_values"]
    rows = []
    for i, path in enumerate(paths):
        row = {
            "#": i + 1,
            "Window":     _D1_SHORT.get(path["d1"], path["d1"]),
            "Density":    _D4_SHORT.get(path["d4"], path["d4"]),
            "Management": _D5_SHORT.get(path["d5"], path["d5"]),
        }
        rain_short = [s.split(" ")[0] for s in states]
        for j, rs in enumerate(rain_short):
            row[rs] = matrix[i][j]
        row["Exp. Yield"] = ev_vals[i]
        row["Best case"]  = max_vals[i]
        row["Worst case"] = min_vals[i]
        rows.append(row)

    df = pd.DataFrame(rows).set_index("#")
    rain_short = [s.split(" ")[0] for s in states]

    def _highlight(row):
        if row.name == optimal_idx + 1:
            return ["background-color: #e8f5e9; font-weight: bold"] * len(row)
        if row.name == user_row:
            return ["background-color: #e3f2fd"] * len(row)
        return [""] * len(row)

    styled = (
        df.style
        .apply(_highlight, axis=1)
        .format({**{c: "{:.1f}" for c in rain_short}, "Exp. Yield": "{:.2f}", "Best case": "{:.1f}", "Worst case": "{:.1f}"})
        .background_gradient(subset=["Exp. Yield"], cmap="YlGn")
    )
    st.dataframe(styled, use_container_width=True, height=620)

    st.markdown("**Scenario heatmap**")
    heat_df = pd.DataFrame(
        matrix,
        index=[f"#{i+1} {_shorten(p)}" for i, p in enumerate(paths)],
        columns=rain_short,
    )
    fig_heat = px.imshow(heat_df, color_continuous_scale="YlGn",
                         labels={"color": "sc/ha"}, aspect="auto")
    fig_heat.update_layout(
        height=650, margin=dict(l=220, r=20, t=20, b=20),
        paper_bgcolor="white", font=dict(color="#1a1a2e", size=11),
        xaxis=dict(tickfont=dict(color="#1a1a2e", size=11)),
        yaxis=dict(tickfont=dict(color="#1a1a2e", size=11)),
    )
    st.plotly_chart(fig_heat, use_container_width=True)


# ── Critérios de Decisão ──────────────────────────────────────────────────────

def _render_criteria(paths, criteria, ev_vals, optimal_idx, user_row):
    st.markdown("Each criterion identifies the best scenario from a different decision perspective.")

    crit_rows = []
    for key, label in _CRITERIA_LABELS.items():
        c = criteria[key]
        p = paths[c["path_idx"]]
        crit_rows.append({
            "Perspective":   label,
            "Best scenario": _shorten(p),
            "Value (sc/ha)": c["value"],
        })
    st.dataframe(pd.DataFrame(crit_rows), use_container_width=True, hide_index=True)

    st.markdown("<br>**Expected yield — all scenarios**", unsafe_allow_html=True)
    ev_df = pd.DataFrame({
        "Scenario": [f"#{i+1} {_shorten(p)}" for i, p in enumerate(paths)],
        "Exp. Yield": ev_vals,
        "color": [
            "#2e7d32" if i == optimal_idx
            else "#1565c0" if i + 1 == user_row
            else "#7a7a9a"
            for i in range(len(paths))
        ],
    }).sort_values("Exp. Yield", ascending=True)

    fig_bar = go_plotly.Figure(go_plotly.Bar(
        x=ev_df["Exp. Yield"], y=ev_df["Scenario"],
        orientation="h",
        marker_color=ev_df["color"].tolist(),
        text=[f"{v:.1f}" for v in ev_df["Exp. Yield"]],
        textposition="outside",
    ))
    fig_bar.update_layout(
        height=720, xaxis_title="Expected yield (sc/ha)", yaxis_title="",
        margin=dict(l=230, r=60, t=10, b=40), showlegend=False,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(color="#1a1a2e", size=11),
        xaxis=dict(
            gridcolor="#d0d0e0",
            tickfont=dict(color="#1a1a2e", size=11),
            title_font=dict(color="#1a1a2e"),
        ),
        yaxis=dict(tickfont=dict(color="#1a1a2e", size=11)),
    )
    st.plotly_chart(fig_bar, use_container_width=True)
    st.caption("Green = best expected result  ·  Blue = your selection")


# ── Visualização Hierárquica ──────────────────────────────────────────────────

def _render_tree(paths, matrix, states, probs, ev_vals, optimal_idx, user_row):
    st.markdown(
        "Hierarchical sunburst: **Window → Density → Management**. "
        "Color and size proportional to expected yield. Click to drill down."
    )

    ids, labels, parents, values, colors = [], [], [], [], []
    ids.append("root"); labels.append("Simulation"); parents.append(""); values.append(0); colors.append(0)

    d1_evs: dict[str, list] = {}
    for i, path in enumerate(paths):
        d1 = _D1_SHORT.get(path["d1"], path["d1"])
        d1_evs.setdefault(d1, []).append(ev_vals[i])
    for d1, evs in d1_evs.items():
        avg = sum(evs) / len(evs)
        ids.append(f"d1|{d1}"); labels.append(d1); parents.append("root"); values.append(avg); colors.append(avg)

    d1d4_evs: dict[str, list] = {}
    for i, path in enumerate(paths):
        d1 = _D1_SHORT.get(path["d1"], path["d1"])
        d4 = _D4_SHORT.get(path["d4"], path["d4"])
        d1d4_evs.setdefault(f"{d1}|{d4}", []).append(ev_vals[i])
    for key, evs in d1d4_evs.items():
        d1, d4 = key.split("|")
        avg = sum(evs) / len(evs)
        ids.append(f"d1d4|{key}"); labels.append(d4); parents.append(f"d1|{d1}"); values.append(avg); colors.append(avg)

    for i, path in enumerate(paths):
        d1 = _D1_SHORT.get(path["d1"], path["d1"])
        d4 = _D4_SHORT.get(path["d4"], path["d4"])
        d5 = _D5_SHORT.get(path["d5"], path["d5"])
        marker = " ★" if i == optimal_idx else (" ●" if i + 1 == user_row else "")
        ids.append(f"leaf|{i}"); labels.append(f"{d5}{marker}")
        parents.append(f"d1d4|{d1}|{d4}")
        values.append(max(ev_vals[i], 0.1)); colors.append(ev_vals[i])

    fig = go_plotly.Figure(go_plotly.Sunburst(
        ids=ids, labels=labels, parents=parents, values=values,
        marker=dict(colors=colors, colorscale="YlGn", showscale=True,
                    colorbar=dict(title="sc/ha")),
        branchvalues="total",
        hovertemplate="<b>%{label}</b><br>Expected yield: %{color:.1f} sc/ha<extra></extra>",
        maxdepth=3,
    ))
    fig.update_layout(
        height=580, margin=dict(t=10, l=10, r=10, b=10),
        paper_bgcolor="white", font=dict(color="#1a1a2e", size=11),
        legend=dict(font=dict(color="#1a1a2e", size=11)),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("★ = best expected result  ·  ● = your selection")

    rain_short = [s.split(" ")[0] for s in states]
    tree_rows  = []
    for i, path in enumerate(paths):
        row = {
            "#":       i + 1,
            "Window":  _D1_SHORT.get(path["d1"], path["d1"]),
            "Dens.":   _D4_SHORT.get(path["d4"], path["d4"]),
            "Mgmt.":   _D5_SHORT.get(path["d5"], path["d5"]),
        }
        for j, rs in enumerate(rain_short):
            row[rs] = matrix[i][j]
        row["Exp. Yield"] = ev_vals[i]
        row["Ref"] = "★" if i == optimal_idx else ("●" if i + 1 == user_row else "")
        tree_rows.append(row)

    df_tree = pd.DataFrame(tree_rows).set_index("#")
    st.dataframe(
        df_tree.style.format({rs: "{:.1f}" for rs in rain_short} | {"Exp. Yield": "{:.2f}"}),
        use_container_width=True,
        height=500,
    )
