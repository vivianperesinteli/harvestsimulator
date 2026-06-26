"""Results page — simulation outcomes and recommendations for the producer."""

from __future__ import annotations
import io
import streamlit as st
import plotly.graph_objects as go_plotly
import plotly.express as px
import pandas as pd
from datetime import datetime

from frontend.navigation import go
from frontend.i18n import t
from frontend.plots_store import load_plots, add_simulation
from frontend.views.results_helpers import (
    _D1_SHORT, _D2_SHORT, _D3_SHORT, _D4_SHORT, _D5_SHORT, _D6_SHORT,
    _CRITERIA_LABELS,
    _pdf_safe, _shorten, _get_criteria_tags, _gen_card_summary,
    _janela_guidance, _densidade_guidance, _manejo_guidance,
)
from frontend.views.results_pdf import _build_pdf

_STATE_DISP = {
    "Seca":   {"en": "Dry",    "pt": "Seca"},
    "Normal": {"en": "Normal", "pt": "Normal"},
    "Úmida":  {"en": "Wet",    "pt": "Úmida"},
}

def _state_label(state: str, lang: str) -> str:
    short = state.split(" ")[0]
    return _STATE_DISP.get(short, {}).get(lang, short)


# ── Página principal ──────────────────────────────────────────────────────────

def render() -> None:
    lang   = st.session_state.get("lang", "en")
    result = st.session_state.get("sim_result")
    if not result:
        st.warning(t("res_no_result", lang))
        if st.button(t("res_go_sim", lang)):
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

    risk_criterion = st.session_state.get("risk_criterion", "bayes_ev")
    optimal_idx = criteria[risk_criterion]["path_idx"]
    ev_vals     = criteria["bayes_ev"]["criterion_values"]

    user_row = next(
        (i + 1 for i, p in enumerate(paths)
         if p["d1"] == user_sel["d1"] and p["d4"] == user_sel["d4"] and p["d5"] == user_sel["d5"]),
        None,
    )

    # ── Pre-compute shared values ─────────────────────────────────────────────
    _rp_display = st.session_state.get("risk_profile", "balanced")
    _rp_colors  = {"conservative": "#1565c0", "balanced": "#2e7d32", "aggressive": "#e65100"}
    _rp_crit_names = {"conservative": "Wald · Maximin", "balanced": "Bayes EV", "aggressive": "Maximax"}
    _rp_color   = _rp_colors.get(_rp_display, "#2e7d32")
    _rp_label   = t(f"inp_risk_{_rp_display}", lang)
    _rp_crit    = _rp_crit_names.get(_rp_display, "Bayes EV")

    user_ev_color = "#2e7d32" if user_sel['ev'] >= baseline else "#c62828"
    user_mc = next(
        (p.get("mc") for p in paths
         if p["d1"] == user_sel["d1"] and p["d4"] == user_sel["d4"] and p["d5"] == user_sel["d5"]),
        None,
    )
    user_idx_hero = next(
        (i for i, p in enumerate(paths)
         if p["d1"] == user_sel["d1"] and p["d4"] == user_sel["d4"] and p["d5"] == user_sel["d5"]),
        None,
    )
    d1_short_str = _D1_SHORT.get(user_sel['d1'], user_sel['d1'])
    interval_str = (
        t("res_m3_interval", lang, p5=user_mc['p5'], p95=user_mc['p95'])
        if user_mc else ""
    )
    best_path  = paths[optimal_idx]
    best_mc    = best_path.get("mc") or {}
    best_short = _D1_SHORT.get(best_path["d1"], best_path["d1"])
    best_interval = (
        t("res_m4_interval", lang, p5=best_mc['p5'], p95=best_mc['p95'])
        if best_mc else ""
    )
    ev_gain    = criteria[risk_criterion]['value'] - user_sel['ev']
    gain_sign  = "+" if ev_gain >= 0 else ""
    gain_color = "#2e7d32" if ev_gain > 0 else "#c62828" if ev_gain < 0 else "#555"
    is_optimal = (user_idx_hero == optimal_idx)
    user_delta  = user_sel['ev'] - baseline
    user_d_sign = "+" if user_delta >= 0 else ""
    user_d_col  = "#2e7d32" if user_delta >= 0 else "#c62828"
    best_delta  = criteria[risk_criterion]['value'] - baseline
    best_d_sign = "+" if best_delta >= 0 else ""

    # ── Header: título (esq) + 4 mini-cards (dir) ────────────────────────────
    col_title, col_cards = st.columns([5, 4], gap="large")

    with col_title:
        st.markdown(f'<div class="page-title" style="margin-bottom:2px">{t("res_page_title", lang)}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="page-subtitle" style="margin-bottom:8px">{t("res_page_subtitle", lang)}</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div style="display:inline-block;background:rgba(0,0,0,0.04);border:1px solid {_rp_color}33;'
            f'border-radius:20px;padding:3px 12px;font-size:0.72rem;font-weight:600;color:{_rp_color}">'
            f'{t("res_risk_profile_label", lang)}: {_rp_label} · {_rp_crit}</div>',
            unsafe_allow_html=True,
        )

    with col_cards:
        opt_badge = ""
        if is_optimal:
            opt_badge = f'<span style="font-size:0.55rem;color:#6b6b8a;font-weight:600">✓ {"optimal" if lang=="en" else "ótimo"}</span>'
        else:
            opt_badge = f'<span style="font-size:0.55rem;color:#6b6b8a">{gain_sign}{ev_gain:.1f} sc/ha {"vs yours" if lang=="en" else "vs você"}</span>'

        st.markdown(f"""
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:4px">

          <div style="background:#f8f9fb;border:1px solid #e4e4f0;border-radius:8px;
                      padding:8px 10px;border-top:2px solid #bdbdce">
            <div style="font-size:0.5rem;color:#9e9e9e;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:2px">
              {t("res_m1_label", lang)}
            </div>
            <div style="font-size:1.1rem;font-weight:800;color:#1a1a2e;line-height:1">{baseline:.0f}</div>
            <div style="font-size:0.55rem;color:#9e9e9e;margin-top:2px">{t("res_m1_sub", lang)}</div>
          </div>

          <div style="background:#f8f9fb;border:1px solid #e4e4f0;border-radius:8px;
                      padding:8px 10px;border-top:2px solid #bdbdce">
            <div style="font-size:0.5rem;color:#9e9e9e;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:2px">
              {t("res_m2_label", lang)}
            </div>
            <div style="font-size:1.1rem;font-weight:800;color:#1a1a2e;line-height:1">{result['base_effective']:.0f}</div>
            <div style="font-size:0.55rem;color:#9e9e9e;margin-top:2px">{t("res_m2_sub", lang)}</div>
          </div>

          <div style="background:#f8f9fb;border:1px solid #e4e4f0;border-radius:8px;
                      padding:8px 10px;border-top:2px solid {user_ev_color}">
            <div style="font-size:0.5rem;color:#9e9e9e;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:2px">
              {t("res_m3_label", lang)}
            </div>
            <div style="font-size:1.1rem;font-weight:800;color:#1a1a2e;line-height:1">{user_sel['ev']:.1f}</div>
            <div style="font-size:0.55rem;color:#9e9e9e;margin-top:2px">
              {user_d_sign}{user_delta:.1f} vs ref · {d1_short_str}
            </div>
          </div>

          <div style="background:linear-gradient(145deg,#f4fdf6,#f8fff8);border:1px solid #c8e6c9;border-radius:8px;
                      padding:8px 10px;border-top:2px solid #2e7d32">
            <div style="font-size:0.5rem;color:#9e9e9e;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:2px">
              {t("res_m4_label", lang)}
            </div>
            <div style="font-size:1.1rem;font-weight:800;color:#1a1a2e;line-height:1">{criteria[risk_criterion]['value']:.1f}</div>
            <div style="font-size:0.55rem;margin-top:2px">{opt_badge}</div>
          </div>

        </div>
        """, unsafe_allow_html=True)

    # ── Salvar em talhão — linha fina e discreta ──────────────────────────────
    _plots_quick = load_plots(auth.get("email", auth.get("id", "default")))
    _saved_key   = "res_quick_save_done"
    st.markdown('<div style="border-top:1px solid #eeeeee;margin:10px 0 4px 0"></div>', unsafe_allow_html=True)

    if _plots_quick:
        _plot_names  = {p["id"]: p["nome"] for p in _plots_quick}
        _save_label  = "Save to field:" if lang == "en" else "Salvar em talhão:"
        _sbtn_lbl    = "Save" if lang == "en" else "Salvar"
        sa, sb, sc = st.columns([2, 4, 1])
        with sa:
            st.markdown(
                f'<div style="padding:6px 0;font-size:0.72rem;color:#6b6b8a">💾 {_save_label}</div>',
                unsafe_allow_html=True,
            )
        with sb:
            _sel_plot_id = st.selectbox(
                "field", options=list(_plot_names.keys()),
                format_func=lambda k: _plot_names[k],
                key="res_quick_plot_sel", label_visibility="collapsed",
            )
        with sc:
            if st.button(_sbtn_lbl, key="res_quick_save_btn", use_container_width=True):
                add_simulation(
                    plot_id=_sel_plot_id,
                    c7_enso=st.session_state.get("sim_context", {}).get("c7_enso", ""),
                    decisions=dict(decisions),
                    risk_profile=st.session_state.get("risk_profile", "balanced"),
                    ev_simulated=user_sel["ev"],
                )
                st.session_state[_saved_key] = _plot_names[_sel_plot_id]
                st.rerun()
        if st.session_state.get(_saved_key):
            st.caption(f"✓ {'Saved to' if lang == 'en' else 'Salvo em'} \"{st.session_state[_saved_key]}\"")
    else:
        _go_lbl = "💾 Save to a field — add fields first" if lang == "en" \
                  else "💾 Salvar em talhão — cadastre talhões primeiro"
        if st.button(_go_lbl, key="res_go_fields_btn"):
            go("farm")

    st.markdown('<div style="border-bottom:1px solid #eeeeee;margin-bottom:14px"></div>', unsafe_allow_html=True)

    # Layout: recomendações (65%) + painel lateral (35%)
    col_main, col_sidebar = st.columns([13, 7], gap="large")

    with col_sidebar:
        _render_scenario_sidebar(display, lang)
        _render_comparison_charts(paths, ev_vals, matrix, states, probs, criteria, baseline, optimal_idx, user_sel, lang)

    with col_main:
        # ── Recomendações ──────────────────────────────────────────────────────
        st.markdown(f'<div class="section-hdr">{t("res_section_rec", lang)}</div>', unsafe_allow_html=True)
        _render_recommendations(
            paths, criteria, ev_vals, states, probs,
            decisions, display, matrix, user_sel, optimal_idx, user_row,
            baseline, result, auth, lang,
        )

    # ── Seções em largura total — fora das colunas ─────────────────────────────
    upgrade = result.get("upgrade_potential")
    if upgrade:
        st.markdown("<br>", unsafe_allow_html=True)
        _render_upgrade_potential(upgrade, decisions, lang)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div class="section-hdr">{t("res_section_export", lang)}</div>', unsafe_allow_html=True)
    _render_global_actions(result, display, auth, paths, ev_vals, states, probs, matrix, criteria, baseline, lang)
    _render_save_to_plot(result, lang)

    # ── Cálculos detalhados (colapsado) ───────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander(t("res_expander_calc", lang)):
        st.caption(t("res_calc_caption", lang))
        tab_matrix, tab_criteria, tab_tree = st.tabs([
            t("res_tab_matrix", lang), t("res_tab_criteria", lang), t("res_tab_tree", lang)
        ])
        with tab_matrix:
            _render_matrix(paths, matrix, criteria, ev_vals, states, probs, optimal_idx, user_row, lang)
        with tab_criteria:
            _render_criteria(paths, criteria, ev_vals, optimal_idx, user_row, lang)
        with tab_tree:
            _render_tree(paths, matrix, states, probs, ev_vals, optimal_idx, user_row, lang)

    # ── Navegação ──────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    col_back, _, col_dash, col_new = st.columns([1, 3, 1, 1])
    with col_back:
        if st.button(t("res_btn_edit", lang), use_container_width=True):
            go("input")
    with col_dash:
        if st.button(t("res_btn_dashboard", lang), use_container_width=True):
            go("dashboard")
    with col_new:
        if st.button(t("res_btn_new", lang), type="primary", use_container_width=True):
            st.session_state.sim_result = None
            st.session_state.input_step = 1
            go("input")


# ── Potencial de upgrade D2/D3/D6 ────────────────────────────────────────────

_UPGRADE_LABELS = {
    "d2_cultivar":   "Cultivar",
    "d3_tsi":        "Seed Treatment",
    "d6_tecnologia": "Planter",
}

_UPGRADE_SHORT = {
    **{k: v for k, v in _D2_SHORT.items()},
    **{k: v for k, v in _D3_SHORT.items()},
    **{k: v for k, v in _D6_SHORT.items()},
}


def _render_upgrade_potential(upgrade: dict, decisions: dict, lang: str = "en") -> None:
    st.markdown(f'<div class="section-hdr">{t("res_upgrade_title", lang)}</div>', unsafe_allow_html=True)
    st.caption(t("res_upgrade_caption", lang))

    any_gain = False
    cols = st.columns(3)

    for col, node_key in zip(cols, ["d2_cultivar", "d3_tsi", "d6_tecnologia"]):
        label     = _UPGRADE_LABELS[node_key]
        node_data = upgrade.get(node_key, {})
        current_val = node_data.get("current", decisions.get(node_key, "—"))
        options   = node_data.get("options", [])

        best_gain = options[0]["delta"] if options else 0.0

        with col:
            st.markdown(f"**{label}**")
            cur_short = _UPGRADE_SHORT.get(current_val, current_val)
            st.caption(t("res_upgrade_current", lang, short=cur_short))

            if not options:
                st.info(t("res_upgrade_already", lang))
                continue

            if best_gain > 0:
                any_gain = True
                best_opt = _UPGRADE_SHORT.get(options[0]["option"], options[0]["option"])
                st.success(t("res_upgrade_gain", lang, opt=best_opt, gain=best_gain))
            elif best_gain < 0:
                st.info(t("res_upgrade_worse", lang))
            else:
                st.info(t("res_upgrade_nosig", lang))

            # Compact table with all alternatives
            if len(options) > 1:
                with st.expander(t("res_upgrade_view_all", lang, label=label.lower())):
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
        st.info(t("res_upgrade_tip", lang))


# ── Sidebar de resumo do cenário ──────────────────────────────────────────────

def _render_scenario_sidebar(display: dict, lang: str = "en") -> None:
    ctx_keys = ["Region", "Texture", "pH", "Drainage", "Soil Type", "Area", "Climate Forecast"]
    dec_keys = ["Planting Period", "Cultivar", "Seed Treatment", "Density", "Disease Management", "Planter"]

    html = '<div class="scenario-sidebar">'
    html += f'<div class="scenario-sidebar-title">{t("res_sidebar_title", lang)}</div>'

    html += f'<div style="font-size:0.6rem;font-weight:700;color:#6b6b8a;text-transform:uppercase;letter-spacing:0.1em;margin:8px 0 4px 0">{t("res_sidebar_field", lang)}</div>'
    for k in ctx_keys:
        v = display.get(k, "—")
        if v:
            html += (
                f'<div class="scenario-row">'
                f'<span class="scenario-key">{k}</span>'
                f'<span class="scenario-val">{v}</span>'
                f'</div>'
            )

    html += f'<div style="font-size:0.6rem;font-weight:700;color:#6b6b8a;text-transform:uppercase;letter-spacing:0.1em;margin:12px 0 4px 0">{t("res_sidebar_decisions", lang)}</div>'
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

def _render_comparison_charts(paths, ev_vals, matrix, states, probs, criteria, baseline, optimal_idx, user_sel, lang: str = "en"):
    """Comparison chart: user choice vs recommended path per climate scenario."""

    state_shorts = [_state_label(s, lang) for s in states]
    ranked = sorted(enumerate(paths), key=lambda x: ev_vals[x[0]], reverse=True)
    top3   = ranked[:3]

    # Find user's path in matrix
    user_idx = next(
        (i for i, p in enumerate(paths)
         if p["d1"] == user_sel["d1"] and p["d4"] == user_sel["d4"] and p["d5"] == user_sel["d5"]),
        None,
    )

    # ── Gráfico: gap por cenário climático (dumbbell / dot-plot) ─────────────
    st.markdown(
        f'<div style="font-size:0.65rem;font-weight:700;color:#4a8a6a;'
        f'text-transform:uppercase;letter-spacing:0.1em;margin:14px 0 6px 0">'
        f'{t("res_chart_vs_title", lang)}</div>',
        unsafe_allow_html=True,
    )

    opt_yields = list(matrix[optimal_idx])

    if user_idx is not None and user_idx != optimal_idx:
        user_yields = list(matrix[user_idx])

        _user_lbl = t("res_chart_vs_user", lang)
        _rec_lbl  = t("res_chart_vs_rec", lang)

        fig = go_plotly.Figure()

        # Connector lines between user and optimal per scenario
        for i, (s, uy, oy) in enumerate(zip(state_shorts, user_yields, opt_yields)):
            fig.add_trace(go_plotly.Scatter(
                x=[uy, oy], y=[s, s],
                mode="lines",
                line=dict(color="#c8ddc8", width=3),
                showlegend=False,
                hoverinfo="skip",
            ))

        # User choice dots
        fig.add_trace(go_plotly.Scatter(
            name=_user_lbl,
            x=user_yields,
            y=state_shorts,
            mode="markers+text",
            marker=dict(color="rgba(90,130,180,0.9)", size=12, symbol="circle",
                        line=dict(color="white", width=1.5)),
            text=[f"{v:.1f}" for v in user_yields],
            textposition="bottom center",
            textfont=dict(size=8, color="#3a4a7a"),
            hovertemplate=f"<b>{_user_lbl}</b><br>%{{y}} · %{{x:.1f}} sc/ha<extra></extra>",
        ))

        # Optimal dots
        fig.add_trace(go_plotly.Scatter(
            name=_rec_lbl,
            x=opt_yields,
            y=state_shorts,
            mode="markers+text",
            marker=dict(color="#1a5c38", size=14, symbol="diamond",
                        line=dict(color="white", width=1.5)),
            text=[f"{v:.1f}" for v in opt_yields],
            textposition="top center",
            textfont=dict(size=8, color="#0d2b18"),
            hovertemplate=f"<b>{_rec_lbl}</b><br>%{{y}} · %{{x:.1f}} sc/ha<extra></extra>",
        ))

        # Probability + gap annotations
        for s, uy, oy, p in zip(state_shorts, user_yields, opt_yields, probs):
            gap_s = oy - uy
            g_sign = "+" if gap_s >= 0 else ""
            g_col  = "#2e7d32" if gap_s > 0 else "#c62828" if gap_s < 0 else "#888"
            fig.add_annotation(
                x=max(uy, oy), y=s,
                text=f"<b style='color:{g_col}'>{g_sign}{gap_s:.1f}</b> · {p:.0%}",
                showarrow=False,
                xanchor="left", xshift=8,
                font=dict(size=8, color="#3a3a5c"),
            )

        all_y = user_yields + opt_yields + [baseline]
        fig.add_vline(
            x=baseline, line_color="#f4a024", line_dash="dot", line_width=1.5,
            annotation_text=f"Ref {baseline:.0f}",
            annotation_font_size=7, annotation_position="top",
            annotation_font_color="#b35c00",
        )
        fig.update_layout(
            height=200,
            margin=dict(t=8, l=0, r=70, b=4),
            xaxis=dict(
                showgrid=True, gridcolor="#d4eedd", zeroline=False,
                tickfont=dict(size=8, color="#1a3a2a"),
                title=dict(text="sc/ha", font=dict(size=8, color="#4a8a6a")),
                range=[min(all_y) * 0.87, max(all_y) * 1.18],
            ),
            yaxis=dict(tickfont=dict(size=9, color="#1a3a2a"), showgrid=False),
            plot_bgcolor="#f4faf7",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#1a3a2a", size=9),
            legend=dict(font=dict(size=8), orientation="h", y=1.14, x=0.5, xanchor="center"),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        user_ev_val = ev_vals[user_idx]
        opt_ev_val  = ev_vals[optimal_idx]
        gap         = opt_ev_val - user_ev_val
        if gap > 0.2:
            _gap_msg   = t("res_chart_vs_gap_better", lang, gap=gap)
            _gap_color = "#2e7d32"
        elif gap < -0.2:
            _gap_msg   = t("res_chart_vs_gap_worse", lang, gap=abs(gap))
            _gap_color = "#c62828"
        else:
            _gap_msg   = t("res_chart_vs_gap_equal", lang)
            _gap_color = "#4a8a6a"
        st.markdown(
            f'<div style="font-size:0.72rem;color:{_gap_color};font-weight:700;'
            f'text-align:center;padding:2px 0 10px 0">{_gap_msg}</div>',
            unsafe_allow_html=True,
        )
    else:
        # User chose optimal path — show yields by climate as lollipop
        fig = go_plotly.Figure()
        bar_colors = ["#1a5c38" if y >= baseline else "#c62828" for y in opt_yields]
        for s, y, c in zip(state_shorts, opt_yields, bar_colors):
            fig.add_trace(go_plotly.Scatter(
                x=[baseline, y], y=[s, s],
                mode="lines",
                line=dict(color="#c8e0c8", width=3),
                showlegend=False, hoverinfo="skip",
            ))
        fig.add_trace(go_plotly.Scatter(
            x=opt_yields, y=state_shorts,
            mode="markers+text",
            marker=dict(color=bar_colors, size=14, symbol="diamond",
                        line=dict(color="white", width=1.5)),
            text=[f"<b>{y:.1f}</b>" for y in opt_yields],
            textposition="top center",
            textfont=dict(size=9, color="#0d2b18"),
            showlegend=False,
            hovertemplate="%{y}: %{x:.1f} sc/ha<extra></extra>",
        ))
        for s, p in zip(state_shorts, probs):
            fig.add_annotation(
                x=max(opt_yields), y=s,
                text=f"{p:.0%}", showarrow=False,
                xanchor="left", xshift=8,
                font=dict(size=8, color="#4a8a6a"),
            )
        fig.add_vline(
            x=baseline, line_color="#f4a024", line_dash="dot", line_width=1.5,
            annotation_text=f"Ref {baseline:.0f}",
            annotation_font_size=7, annotation_position="top",
            annotation_font_color="#b35c00",
        )
        fig.update_layout(
            height=200,
            margin=dict(t=8, l=0, r=50, b=4),
            xaxis=dict(showgrid=True, gridcolor="#d4eedd", zeroline=False,
                       tickfont=dict(size=8, color="#1a3a2a"),
                       title=dict(text="sc/ha", font=dict(size=8, color="#4a8a6a")),
                       range=[min(opt_yields + [baseline]) * 0.88, max(opt_yields + [baseline]) * 1.16]),
            yaxis=dict(tickfont=dict(size=9, color="#1a3a2a"), showgrid=False),
            plot_bgcolor="#f4faf7",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#1a3a2a", size=9),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.success(t("res_chart_vs_optimal", lang), icon="✅")

    # ── Cards de risco — top 3 ────────────────────────────────────────────────
    st.markdown(
        f'<div style="font-size:0.65rem;font-weight:700;color:#4a8a6a;'
        f'text-transform:uppercase;letter-spacing:0.1em;margin:14px 0 6px 0">'
        f'{t("res_chart_risk_label", lang)}</div>',
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
            _risk_below_label = t("res_risk_below", lang)
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
            f'<div style="font-size:0.68rem;color:#6b6b8a;margin-top:2px">{_risk_below_label} <b style="color:#1a3a2a">{risk_txt}</b></div>'
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
                             baseline, result, auth, lang: str = "en"):
    ranked = sorted(enumerate(paths), key=lambda x: ev_vals[x[0]], reverse=True)
    top3   = ranked[:3]
    d2 = decisions.get("d2_cultivar", "")
    d3 = decisions.get("d3_tsi", "")
    d6 = decisions.get("d6_tecnologia", "")

    for rank_num, (path_idx, path) in enumerate(top3, start=1):
        rank_cls   = f"rank-{rank_num}" if rank_num <= 3 else ""
        rank_label = {
            1: t("res_rank_1", lang),
            2: t("res_rank_2", lang),
            3: t("res_rank_3", lang),
        }.get(rank_num, f"#{rank_num}")

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
                f'<div class="rec-yield-interval">{t("res_interval", lang, p5=mc["p5"], p95=mc["p95"])}</div>'
                f'<div class="rec-risk-label" style="color:{risk_color}">{t("res_risk_label", lang, pct=mc["p_below"])}</div>'
            )
        else:
            mc_html = ""

        # ── Constrói cenários html — sem newlines ─────────────────────────────
        scenarios_html = ""
        for i_s, state in enumerate(states):
            y_val = yields_row[i_s]
            bar_color = "#2e7d32" if y_val >= baseline else "#c62828"
            state_short = _state_label(state, lang)
            scenarios_html += (
                f'<div style="display:flex;justify-content:space-between;align-items:center;'
                f'padding:5px 0;border-bottom:1px solid #f0f0f0;font-size:0.84rem">'
                f'<span style="color:#3a3a5c"><strong>{state_short}</strong> ({probs[i_s]:.0%})</span>'
                f'<span style="color:{bar_color};font-weight:700">{y_val:.1f} sc/ha</span></div>'
            )

        # ── Constrói tags html ────────────────────────────────────────────────
        tags_html = ""
        if tags:
            tags_inner = "".join(f'<span class="crit-tag">{tg}</span>' for tg in tags[:3])
            tags_html = f'<div class="rec-criteria-row" style="margin-top:12px">{tags_inner}</div>'

        # ── Constrói grid de decisões html ────────────────────────────────────
        d1_short = _D1_SHORT.get(path["d1"], path["d1"])
        d4_short = _D4_SHORT.get(path["d4"], path["d4"])
        d5_short = _D5_SHORT.get(path["d5"], path["d5"])
        d2_short = _D2_SHORT.get(d2, d2)
        d3_short = _D3_SHORT.get(d3, d3)
        d6_short = _D6_SHORT.get(d6, d6)

        # ── Renderiza o card — HTML concatenado sem linhas em branco ────────────
        decisions_grid = (
            f'<div class="rec-decisions-grid">'
            f'<div class="dec-item"><div class="dec-label">{t("res_dec_window", lang)}</div><div class="dec-value">{d1_short}</div></div>'
            f'<div class="dec-item"><div class="dec-label">{t("res_dec_density", lang)}</div><div class="dec-value">{d4_short}</div></div>'
            f'<div class="dec-item"><div class="dec-label">{t("res_dec_disease", lang)}</div><div class="dec-value">{d5_short}</div></div>'
            f'<div class="dec-item"><div class="dec-label">{t("res_dec_cultivar", lang)}</div><div class="dec-value">{d2_short}</div></div>'
            f'<div class="dec-item"><div class="dec-label">{t("res_dec_seed", lang)}</div><div class="dec-value">{d3_short}</div></div>'
            f'<div class="dec-item"><div class="dec-label">{t("res_dec_planter", lang)}</div><div class="dec-value">{d6_short}</div></div>'
            f'</div>'
        )
        yield_col = (
            f'<div style="min-width:150px">'
            f'<div class="rec-yield-big">{ev:.1f}</div>'
            f'<div class="rec-yield-unit">{t("res_yield_unit", lang)}</div>'
            f'<div class="rec-yield-range" style="color:{delta_color};font-weight:600">{t("res_vs_ref", lang, delta_sign=delta_sign, delta=delta)}</div>'
            f'{mc_html}'
            f'</div>'
        )
        scenario_col = (
            f'<div style="flex:1;min-width:200px;border-left:1px solid #e4e4f0;padding-left:20px">'
            f'<div style="font-size:0.68rem;font-weight:700;color:#6b6b8a;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:8px">{t("res_by_climate", lang)}</div>'
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
        with st.expander(t("res_expander_how", lang, n=rank_num)):
            g1, g2 = st.columns(2)
            with g1:
                st.markdown(t("res_why_title", lang))
                if tags:
                    st.markdown(t("res_why_tagged", lang, tags=', '.join(tags[:2])))
                delta_str = f"+{ev - baseline:.1f}" if ev >= baseline else f"{ev - baseline:.1f}"
                st.markdown(t("res_why_yield", lang, ev=ev, delta=delta_str))
                if mc:
                    st.markdown(t("res_why_mc", lang, p5=mc['p5'], p95=mc['p95']))
            with g2:
                st.markdown(t("res_guidance_title", lang))
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
                    t("res_pdf_btn", lang, n=rank_num),
                    data=pdf_bytes,
                    file_name=f"recommendation_{rank_num}.pdf",
                    mime="application/pdf",
                    key=f"pdf_rec_{rank_num}",
                    use_container_width=True,
                )
            except Exception as e:
                st.caption(t("res_pdf_unavail", lang, e=e))
        with col_csv:
            rows = [{
                "path": path_idx + 1,
                "D1_window": path["d1"],
                "D4_density": path["d4"],
                "D5_management": path["d5"],
                "EV_sc_ha": ev,
                **{_state_label(states[j], lang): matrix[path_idx][j] for j in range(len(states))},
                **({"MC_mean": mc["mean"], "MC_P5": mc["p5"], "MC_P95": mc["p95"]} if mc else {}),
            }]
            csv_data = pd.DataFrame(rows).to_csv(index=False).encode("utf-8")
            st.download_button(
                t("res_csv_btn", lang),
                data=csv_data,
                file_name=f"cenario_{rank_num}.csv",
                mime="text/csv",
                key=f"csv_rec_{rank_num}",
                use_container_width=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)

    # ── Comparação com seleção do usuário ──────────────────────────────────────
    if user_row and user_row - 1 != optimal_idx:
        risk_criterion_local = st.session_state.get("risk_criterion", "bayes_ev")
        gap_user = user_sel["ev"] - criteria[risk_criterion_local]["value"]
        st.info(t("res_user_gap", lang, ev=user_sel['ev'], gap=gap_user))


# ── Salvar simulação em talhão ────────────────────────────────────────────────

def _render_save_to_plot(result: dict, lang: str = "en") -> None:
    auth    = st.session_state.get("auth", {})
    user_id = auth.get("id", "default")
    plots   = load_plots(user_id)

    if not plots:
        return

    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander(f"💾 {t('plts_save_hdr', lang)}"):
        context   = st.session_state.get("sim_context", {})
        decisions = st.session_state.get("sim_decisions", {})
        if not context or not decisions:
            st.caption(t("plts_save_no_res", lang))
            return

        plot_names = {p["id"]: p["nome"] for p in plots}
        sel_id = st.selectbox(
            t("plts_save_select", lang),
            options=list(plot_names.keys()),
            format_func=lambda k: plot_names[k],
            key="res_save_plot_sel",
        )
        if st.button(t("plts_save_btn", lang), type="primary", key="res_btn_save_plot"):
            add_simulation(
                plot_id=sel_id,
                c7_enso=context.get("c7_enso", ""),
                decisions=dict(decisions),
                risk_profile=st.session_state.get("risk_profile", "balanced"),
                ev_simulated=result["user_selection"]["ev"],
            )
            st.success(t("plts_save_ok", lang, nome=plot_names[sel_id]))


# ── Ações globais (PDF completo + exportação geral) ───────────────────────────

def _render_global_actions(result, display, auth, paths, ev_vals, states, probs, matrix, criteria, baseline, lang: str = "en"):
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        try:
            user_name = auth.get("name", "Farmer")
            pdf_bytes = _build_pdf(
                result, display, user_name, paths, ev_vals,
                states, probs, matrix, criteria, baseline,
            )
            st.download_button(
                t("res_pdf_full", lang),
                data=pdf_bytes,
                file_name="season_report.pdf",
                mime="application/pdf",
                key="pdf_global",
                use_container_width=True,
                type="primary",
            )
        except Exception as e:
            st.error(t("res_pdf_err", lang, e=e))

    with col2:
        rows = []
        for i, path in enumerate(paths):
            mc = path.get("mc") or {}
            row = {
                "#": i + 1,
                t("res_col_window", lang):     path["d1"],
                t("res_col_density", lang):    path["d4"],
                t("res_col_management", lang): path["d5"],
                t("res_col_exp_yield", lang):  ev_vals[i],
            }
            for j, s in enumerate(states):
                row[_state_label(s, lang)] = matrix[i][j]
            if mc:
                row[t("res_col_mc_mean", lang)] = mc["mean"]
                row[t("res_col_mc_p5", lang)]   = mc["p5"]
                row[t("res_col_mc_p95", lang)]  = mc["p95"]
                row[t("res_col_risk", lang)]     = round(mc["p_below"] * 100, 1)
            rows.append(row)
        df = pd.DataFrame(rows)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            t("res_csv_full", lang),
            data=csv,
            file_name="full_simulation.csv",
            mime="text/csv",
            key="csv_global",
            use_container_width=True,
        )

    with col3:
        st.button(
            t("res_btn_print", lang),
            key="btn_print",
            use_container_width=True,
            on_click=lambda: st.markdown(
                "<script>window.print();</script>", unsafe_allow_html=True
            ),
        )

    with col4:
        if st.button(t("res_btn_share", lang), key="btn_share", use_container_width=True):
            st.info(t("res_share_info", lang))


# ── Análise de Cenários (Payoff Matrix) ───────────────────────────────────────

def _render_matrix(paths, matrix, criteria, ev_vals, states, probs, optimal_idx, user_row, lang: str = "en"):
    prob_str = " · ".join(f"{_state_label(s, lang)} {p:.0%}" for s, p in zip(states, probs))
    st.markdown(t("res_matrix_probs", lang, prob_str=prob_str))
    st.caption(t("res_matrix_caption", lang))

    max_vals = criteria["maximax"]["criterion_values"]
    min_vals = criteria["wald"]["criterion_values"]
    rows = []
    for i, path in enumerate(paths):
        row = {
            "#": i + 1,
            t("res_col_window", lang):     _D1_SHORT.get(path["d1"], path["d1"]),
            t("res_col_density", lang):    _D4_SHORT.get(path["d4"], path["d4"]),
            t("res_col_management", lang): _D5_SHORT.get(path["d5"], path["d5"]),
        }
        rain_short = [_state_label(s, lang) for s in states]
        for j, rs in enumerate(rain_short):
            row[rs] = matrix[i][j]
        row["Exp. Yield"] = ev_vals[i]
        row["Best case"]  = max_vals[i]
        row["Worst case"] = min_vals[i]
        rows.append(row)

    df = pd.DataFrame(rows).set_index("#")
    rain_short = [_state_label(s, lang) for s in states]

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

    st.markdown(t("res_matrix_heatmap", lang))
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

def _render_criteria(paths, criteria, ev_vals, optimal_idx, user_row, lang: str = "en"):
    st.markdown(t("res_crit_intro", lang))

    crit_rows = []
    for key, label in _CRITERIA_LABELS.items():
        c = criteria[key]
        p = paths[c["path_idx"]]
        crit_rows.append({
            t("res_crit_col_persp", lang): label,
            t("res_crit_col_best", lang):  _shorten(p),
            t("res_crit_col_val", lang):   c["value"],
        })
    st.dataframe(pd.DataFrame(crit_rows), use_container_width=True, hide_index=True)

    st.markdown(f"<br>{t('res_crit_ev_title', lang)}", unsafe_allow_html=True)
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
    st.caption(t("res_crit_caption", lang))


# ── Visualização Hierárquica ──────────────────────────────────────────────────

def _render_tree(paths, matrix, states, probs, ev_vals, optimal_idx, user_row, lang: str = "en"):
    st.markdown(t("res_tree_intro", lang))

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
    st.caption(t("res_tree_caption", lang))

    rain_short = [_state_label(s, lang) for s in states]
    tree_rows  = []
    for i, path in enumerate(paths):
        row = {
            "#":       i + 1,
            t("res_col_window", lang):     _D1_SHORT.get(path["d1"], path["d1"]),
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
