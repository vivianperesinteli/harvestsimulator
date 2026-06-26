"""Adaptive Season Planner — explore scenarios, record harvests, calibrate your farm model."""

from __future__ import annotations
import sys
from pathlib import Path
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from frontend.navigation import go as navigate
from frontend.i18n import t

_ROOT = Path(__file__).parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

try:
    from backend.learning import save_outcome, get_learning_stats, get_calibrated_params
    _LEARNING_OK = True
except Exception:
    _LEARNING_OK = False


def _calibration_progress(n: int, lang: str) -> None:
    pct   = min(100, int(n / 3 * 100))
    color = "#2e7d32" if n >= 3 else "#1565c0"
    label = (
        t("ap_progress_active", lang, n=n)
        if n >= 3
        else t("ap_progress_pending", lang, n=n, need=max(0, 3 - n))
    )
    st.markdown(f"""<div style="margin:4px 0 20px">
        <div style="font-size:0.82rem;color:#6b6b8a;margin-bottom:5px">{t("ap_progress_title", lang)}</div>
        <div style="background:#e0e0e0;border-radius:4px;height:8px;overflow:hidden">
            <div style="background:{color};width:{pct}%;height:8px"></div>
        </div>
        <div style="font-size:0.82rem;color:{color};margin-top:5px">{label}</div>
    </div>""", unsafe_allow_html=True)


def render() -> None:
    lang    = st.session_state.get("lang", "en")
    auth    = st.session_state.get("auth", {})
    user_id = auth.get("email", "demo")
    history = st.session_state.get("sim_history", [])

    st.markdown(f'<div class="page-title">{t("ap_title", lang)}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">{t("ap_subtitle", lang)}</div>', unsafe_allow_html=True)

    st.markdown(f"""<div style="background:linear-gradient(90deg,#f0f4ff,#e8f5e9);border-radius:8px;
        padding:12px 18px;margin:10px 0 16px;border-left:4px solid #1565c0">
        <span style="color:#1a1a2e;font-size:0.9rem">{t("ap_purpose", lang)}</span>
    </div>""", unsafe_allow_html=True)

    if not _LEARNING_OK:
        st.error(t("ap_learning_err", lang))
        return

    stats  = get_learning_stats(user_id)
    params = get_calibrated_params(user_id)
    n      = stats["n"]

    # ── Status cards ──────────────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.markdown(f"""<div class="metric-card">
            <div class="mc-label">{t("ap_confirmed_seasons", lang)}</div>
            <div class="mc-value">{n}</div>
            <div class="mc-sub">{t("ap_outcomes_recorded", lang)}</div>
        </div>""", unsafe_allow_html=True)

    with k2:
        if stats["mean_gap"] is not None:
            gc = "#2e7d32" if stats["mean_gap"] >= 0 else "#c62828"
            gs = f"{stats['mean_gap']:+.1f}"
        else:
            gc, gs = "#6b6b8a", "—"
        st.markdown(f"""<div class="metric-card">
            <div class="mc-label">{t("ap_mean_gap", lang)}</div>
            <div class="mc-value" style="color:{gc}">{gs}</div>
            <div class="mc-sub">{t("ap_mean_gap_sub", lang)}</div>
        </div>""", unsafe_allow_html=True)

    with k3:
        rmse_str = f"{stats['rmse']:.1f}" if stats["rmse"] is not None else "—"
        st.markdown(f"""<div class="metric-card">
            <div class="mc-label">{t("ap_rmse", lang)}</div>
            <div class="mc-value">{rmse_str}</div>
            <div class="mc-sub">{t("ap_rmse_sub", lang)}</div>
        </div>""", unsafe_allow_html=True)

    with k4:
        if stats["improving"] is True:
            imp, ic = t("ap_improving", lang), "#2e7d32"
        elif stats["improving"] is False:
            imp, ic = t("ap_not_converged", lang), "#f57c00"
        else:
            imp, ic = t("ap_need_seasons", lang), "#6b6b8a"
        st.markdown(f"""<div class="metric-card">
            <div class="mc-label">{t("ap_accuracy_trend", lang)}</div>
            <div class="mc-value" style="color:{ic};font-size:1.0rem">{imp}</div>
            <div class="mc-sub">{t("ap_accuracy_trend_sub", lang)}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    _calibration_progress(n, lang)

    tab_whatif, tab_confirm, tab_history, tab_model = st.tabs([
        t("ap_tab_whatif", lang),
        t("ap_tab_record", lang),
        t("ap_tab_history", lang),
        t("ap_tab_model", lang),
    ])

    # ── TAB 1: Explore Scenarios ──────────────────────────────────────────────
    with tab_whatif:
        st.markdown(f"### {t('ap_wi_title', lang)}")
        st.caption(t("ap_wi_caption", lang))

        result    = st.session_state.get("sim_result")
        context   = st.session_state.get("sim_context")
        decisions = st.session_state.get("sim_decisions")

        if not result or not context or not decisions:
            st.warning(t("ap_wi_no_sim", lang))
            if st.button(t("mc_go_sim", lang), key="wi_nav"):
                navigate("input")
        else:
            # Internal API values (Portuguese) — must match what sim_decisions stores
            _D_ADJ: dict[str, dict[str, float]] = {
                "d1_janela":     {"Precoce (até 15/out)": -3, "Ótima (16/out – 10/nov)": 4, "Tardia (após 10/nov)": -8},
                "d2_cultivar":   {"Alto potencial (P98R30, NK6727, BMX Foco; pós-2020)": 6, "Intermediário (2015–2019)": 0, "Limitado (legados pré-2015)": -8},
                "d3_tsi":        {"Premium (fung+inset+nemat+inoc)": 3, "Standard (fungicida + inoculante)": 0, "Sem TSI": -5},
                "d4_densidade":  {"Baixa (≤280k sementes/ha)": -1, "Média (280k–340k)": 2, "Alta (>340k)": -1},
                "d5_manejo":     {"Alto (≥3 fung. + monitor ferrugem)": 5, "Padrão (2 aplicações)": 0, "Baixo (1 ou nenhuma)": -7},
                "d6_tecnologia": {"Alta precisão (RTK + pneumática moderna)": 3, "Padrão": 0, "Baixa (espaçamento irregular)": -4},
            }
            # English display labels for each API value
            _D_OPT_EN: dict[str, str] = {
                "Precoce (até 15/out)":                               "Early — until Oct 15",
                "Ótima (16/out – 10/nov)":                            "Optimal — Oct 16 to Nov 10",
                "Tardia (após 10/nov)":                               "Late — after Nov 10",
                "Alto potencial (P98R30, NK6727, BMX Foco; pós-2020)":"High-potential cultivar (post-2020)",
                "Intermediário (2015–2019)":                          "Mid-range cultivar (2015–2019)",
                "Limitado (legados pré-2015)":                        "Legacy cultivar (pre-2015)",
                "Premium (fung+inset+nemat+inoc)":                    "Premium TSI — fungicide + insecticide + nematicide",
                "Standard (fungicida + inoculante)":                  "Standard TSI — fungicide + inoculant",
                "Sem TSI":                                            "No seed treatment",
                "Baixa (≤280k sementes/ha)":                         "Low density — ≤280k seeds/ha",
                "Média (280k–340k)":                                  "Medium density — 280k–340k seeds/ha",
                "Alta (>340k)":                                       "High density — >340k seeds/ha",
                "Alto (≥3 fung. + monitor ferrugem)":                 "High — ≥3 fungicide apps + rust monitoring",
                "Padrão (2 aplicações)":                              "Standard — 2 applications",
                "Baixo (1 ou nenhuma)":                               "Low — 1 or no application",
                "Alta precisão (RTK + pneumática moderna)":           "High precision — RTK + pneumatic planter",
                "Padrão":                                             "Standard precision",
                "Baixa (espaçamento irregular)":                      "Low precision — irregular spacing",
            }
            _fmt = (lambda v: _D_OPT_EN.get(v, v)) if lang == "en" else (lambda v: v)

            _D_DISPLAY = {
                "d1_janela":     t("ap_wi_d1", lang),
                "d2_cultivar":   t("ap_wi_d2", lang),
                "d3_tsi":        t("ap_wi_d3", lang),
                "d4_densidade":  t("ap_wi_d4", lang),
                "d5_manejo":     t("ap_wi_d5", lang),
                "d6_tecnologia": t("ap_wi_d6", lang),
            }

            current_ev = result["user_selection"]["ev"]
            baseline   = result["baseline"]

            st.markdown(f"**{t('ap_wi_instruction', lang)}**")
            st.caption(t("ap_wi_note", lang))

            wi_decisions: dict[str, str] = dict(decisions)
            impact_rows = []

            for key, display_label in _D_DISPLAY.items():
                opts    = list(_D_ADJ.get(key, {}).keys())
                cur_val = decisions.get(key, opts[0])
                cur_idx = opts.index(cur_val) if cur_val in opts else 0

                wi_val = st.selectbox(
                    display_label,
                    options=opts,
                    format_func=_fmt,
                    index=cur_idx,
                    key=f"wi_{key}",
                )
                wi_decisions[key] = wi_val

                cur_adj = _D_ADJ.get(key, {}).get(cur_val, 0)
                new_adj = _D_ADJ.get(key, {}).get(wi_val, 0)
                impact_rows.append({
                    t("ap_wi_col_node", lang):    display_label,
                    t("ap_wi_col_current", lang): _fmt(cur_val).split("—")[0].strip(),
                    t("ap_wi_col_whatif", lang):  _fmt(wi_val).split("—")[0].strip(),
                    "cur_adj": cur_adj,
                    "new_adj": new_adj,
                    "Impact":  new_adj - cur_adj,
                })

            d_delta  = sum(r["Impact"] for r in impact_rows)
            wi_ev    = current_ev + d_delta
            ev_delta = d_delta

            st.markdown("<br>", unsafe_allow_html=True)
            d1, d2 = st.columns(2)
            with d1:
                st.markdown(f"""<div class="metric-card">
                    <div class="mc-label">{t("ap_wi_ev_label", lang)}</div>
                    <div class="mc-value" style="color:{'#2e7d32' if wi_ev >= baseline else '#c62828'}">{wi_ev:.1f}</div>
                    <div class="mc-sub">sc/ha</div>
                </div>""", unsafe_allow_html=True)
            with d2:
                dc = "#2e7d32" if ev_delta > 0 else "#c62828" if ev_delta < 0 else "#6b6b8a"
                st.markdown(f"""<div class="metric-card">
                    <div class="mc-label">{t("ap_wi_change_label", lang)}</div>
                    <div class="mc-value" style="color:{dc}">{ev_delta:+.1f}</div>
                    <div class="mc-sub">sc/ha</div>
                </div>""", unsafe_allow_html=True)

            df_impact = pd.DataFrame(impact_rows)
            changed   = df_impact[df_impact["Impact"] != 0]
            if not changed.empty:
                fig_wi = go.Figure(go.Bar(
                    x=changed["Impact"],
                    y=changed[t("ap_wi_col_node", lang)],
                    orientation="h",
                    marker_color=["#2e7d32" if v > 0 else "#c62828" for v in changed["Impact"]],
                    text=[f"{v:+.0f} sc/ha" for v in changed["Impact"]],
                    textposition="outside",
                ))
                fig_wi.add_vline(x=0, line_color="#999", line_width=1)
                fig_wi.update_layout(
                    height=max(200, len(changed) * 55),
                    xaxis_title=t("ap_wi_impact_axis", lang),
                    margin=dict(t=10, l=10, r=80, b=20),
                    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#1a1a2e", size=11),
                    xaxis=dict(gridcolor="#c8c0b0"),
                    showlegend=False,
                )
                st.plotly_chart(fig_wi, use_container_width=True)
            else:
                st.info(t("ap_wi_no_changes", lang))

            st.markdown("---")
            if st.button(t("ap_wi_go_new_sim", lang), type="secondary", use_container_width=True):
                navigate("input")

    # ── TAB 2: Record Harvest ────────────────────────────────────────────────
    with tab_confirm:
        st.markdown(f"### {t('ap_rec_title', lang)}")
        st.caption(t("ap_rec_caption", lang))
        st.markdown("<br>", unsafe_allow_html=True)

        if not history:
            st.info(t("ap_rec_no_history", lang))
        else:
            sim_options = {
                f"#{h['id']} · {h['summary']} ({h['timestamp'][:10]})": h
                for h in reversed(history)
            }
            selected_label = st.selectbox(t("ap_rec_which_sim", lang), list(sim_options.keys()))
            selected_sim   = sim_options[selected_label]

            col_f1, col_f2 = st.columns(2)
            with col_f1:
                season_label = st.text_input(t("ap_rec_season_label", lang), value="2024/25")
            with col_f2:
                actual_yield = st.number_input(
                    t("ap_rec_actual_yield", lang), min_value=0.0, max_value=120.0,
                    value=60.0, step=0.5,
                )

            sim_result = selected_sim.get("result", {})
            try:
                sim_mean = sim_result["criteria"]["bayes_ev"]["value"]
            except (KeyError, TypeError):
                sim_mean = 60.0

            gap   = actual_yield - sim_mean
            gap_c = "#2e7d32" if gap >= 0 else "#c62828"

            # Visual comparison bar
            fig_cmp = go.Figure(go.Bar(
                x=[t("ap_rec_pred_ev", lang), t("ap_rec_actual_yield", lang)],
                y=[sim_mean, actual_yield],
                marker_color=["#1565c0", "#2e7d32" if gap >= 0 else "#c62828"],
                text=[f"{sim_mean:.1f} sc/ha", f"{actual_yield:.1f} sc/ha"],
                textposition="outside",
                width=0.4,
            ))
            fig_cmp.update_layout(
                height=240,
                margin=dict(t=30, l=10, r=10, b=20),
                yaxis=dict(title="sc/ha", range=[0, max(sim_mean, actual_yield) * 1.2]),
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#1a1a2e", size=12),
                showlegend=False,
            )
            st.plotly_chart(fig_cmp, use_container_width=True)

            col_p, col_g = st.columns(2)
            with col_p:
                st.markdown(f"""<div class="metric-card">
                    <div class="mc-label">{t("ap_rec_pred_ev", lang)}</div>
                    <div class="mc-value">{sim_mean:.1f}</div>
                    <div class="mc-sub">{t("ap_rec_pred_ev_sub", lang)}</div>
                </div>""", unsafe_allow_html=True)
            with col_g:
                st.markdown(f"""<div class="metric-card">
                    <div class="mc-label">{t("ap_rec_pred_gap", lang)}</div>
                    <div class="mc-value" style="color:{gap_c}">{gap:+.1f}</div>
                    <div class="mc-sub">{t("ap_rec_pred_gap_sub", lang)}</div>
                </div>""", unsafe_allow_html=True)

            # Collect tornado variance shares if a Monte Carlo was run
            tornado_shares = None
            mc_result = st.session_state.get("mc_result")
            if mc_result:
                tornado = mc_result.get("tornado", {})
                shares  = {}
                _KEY_MAP = {"D2": "d2", "D3": "d3", "D6": "d6"}
                for k, v in tornado.items():
                    for prefix, key in _KEY_MAP.items():
                        if prefix in k:
                            shares[key] = v.get("variance_share", 0)
                if shares:
                    tornado_shares = shares

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(t("ap_rec_confirm_btn", lang), type="primary", use_container_width=True):
                save_outcome(
                    user_id=user_id,
                    season=season_label,
                    simulation_id=selected_sim.get("id"),
                    context=selected_sim.get("context", {}),
                    decisions=selected_sim.get("decisions", {}),
                    simulated_mean=sim_mean,
                    actual_yield=actual_yield,
                    tornado_shares=tornado_shares,
                )
                remaining = max(0, 3 - n - 1)
                if remaining > 0:
                    note = t("ap_rec_note_more", lang, remaining=remaining)
                else:
                    note = t("ap_rec_note_done", lang)
                st.success(
                    t("ap_rec_success", lang,
                      season=season_label,
                      yield_val=f"{actual_yield:.1f}",
                      gap=f"{gap:+.1f}",
                      note=note)
                )
                st.rerun()

    # ── TAB 3: Season History ─────────────────────────────────────────────────
    with tab_history:
        outcomes = stats.get("outcomes", [])
        if not outcomes:
            st.info(t("ap_hist_no_outcomes", lang))
        else:
            seasons   = [o["season"] for o in outcomes]
            simulated = [o["simulated_mean"] for o in outcomes]
            actual    = [o["actual_yield"] for o in outcomes]
            gaps      = [o["gap"] for o in outcomes]

            st.markdown(f"### {t('ap_hist_chart_title', lang)}")

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=seasons, y=simulated, mode="lines+markers",
                name=t("ap_hist_simulated", lang),
                line=dict(color="#1565c0", width=2, dash="dash"), marker=dict(size=8),
            ))
            fig.add_trace(go.Scatter(
                x=seasons, y=actual, mode="lines+markers",
                name=t("ap_hist_actual", lang),
                line=dict(color="#2e7d32", width=2), marker=dict(size=8),
            ))
            fig.add_trace(go.Bar(
                x=seasons, y=gaps, name=t("ap_hist_gap", lang),
                marker_color=["#2e7d32" if g >= 0 else "#c62828" for g in gaps],
                opacity=0.45, yaxis="y2",
            ))
            fig.update_layout(
                height=380,
                yaxis=dict(title="sc/ha", gridcolor="#c8c0b0"),
                yaxis2=dict(title=t("ap_hist_gap_axis", lang), overlaying="y", side="right", showgrid=False),
                margin=dict(t=10, l=40, r=60, b=40),
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
                plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#1a1a2e", size=11),
                xaxis=dict(tickfont=dict(size=10)),
            )
            st.plotly_chart(fig, use_container_width=True)

            # Trend insight
            if stats["mean_gap"] is not None:
                mg = stats["mean_gap"]
                if abs(mg) <= 3:
                    st.success(t("ap_hist_trend_good", lang, gap=f"{abs(mg):.1f}"))
                elif mg < 0:
                    st.warning(t("ap_hist_trend_over", lang, gap=f"{abs(mg):.1f}"))
                else:
                    st.info(t("ap_hist_trend_under", lang, gap=f"{mg:.1f}"))

            st.markdown(f"**{t('ap_hist_table_title', lang)}**")
            df = pd.DataFrame([{
                t("ap_hist_col_season", lang):   o["season"],
                t("ap_hist_col_sim", lang):      o["simulated_mean"],
                t("ap_hist_col_actual", lang):   o["actual_yield"],
                t("ap_hist_col_gap", lang):      f"{o['gap']:+.1f}",
                t("ap_hist_col_recorded", lang): o["timestamp"][:10],
            } for o in outcomes])
            st.dataframe(df, use_container_width=True, hide_index=True)

    # ── TAB 4: Calibration ───────────────────────────────────────────────────
    with tab_model:
        is_calibrated = n >= 3

        # Confidence bar
        pct   = min(100, int(n / 3 * 100))
        color = "#2e7d32" if is_calibrated else "#1565c0"
        label = (
            t("ap_progress_active", lang, n=n)
            if is_calibrated
            else t("ap_progress_pending", lang, n=n, need=max(0, 3 - n))
        )
        st.markdown(f"""<div style="margin:4px 0 16px">
            <div style="font-size:0.82rem;color:#6b6b8a;margin-bottom:5px">{t("ap_progress_title", lang)}</div>
            <div style="background:#e0e0e0;border-radius:4px;height:10px;overflow:hidden">
                <div style="background:{color};width:{pct}%;height:10px"></div>
            </div>
            <div style="font-size:0.85rem;color:{color};margin-top:5px;font-weight:500">{label}</div>
        </div>""", unsafe_allow_html=True)

        if not is_calibrated:
            st.info(t("ap_model_need_more", lang, n=n, need=max(0, 3 - n)))
            st.caption(t("ap_model_need_caption", lang))
        else:
            st.success(t("ap_model_calibrated", lang, n=n, gap=f"{stats['mean_gap']:+.1f}"))

        st.markdown(f"### {t('ap_model_params_title', lang)}")
        st.caption(t("ap_model_params_caption", lang))

        try:
            from backend.monte_carlo import TRIANGULAR_DEFAULTS
            default_modes = {
                "d2": TRIANGULAR_DEFAULTS["d2_cultivar"]["mode"],
                "d3": TRIANGULAR_DEFAULTS["d3_tsi"]["mode"],
                "d6": TRIANGULAR_DEFAULTS["d6_tecnologia"]["mode"],
            }
        except Exception:
            default_modes = {"d2": 0.0, "d3": 0.0, "d6": 0.0}

        _LABEL_MAP = {
            "d2": t("mc_param_d2", lang),
            "d3": t("mc_param_d3", lang),
            "d6": t("mc_param_d6", lang),
        }

        for key in ["d2", "d3", "d6"]:
            p      = params[key]
            d_mode = default_modes[key]
            c_mode = p["mode"]
            delta  = c_mode - d_mode
            dc     = "#2e7d32" if delta > 0 else "#c62828" if delta < 0 else "#6b6b8a"
            calib  = p.get("calibrated", False)

            st.markdown(f"**{_LABEL_MAP[key]}**")
            ca, cb, cc = st.columns(3)
            with ca:
                st.metric(t("mc_minimum", lang), f"{p['min']:.1f} sc/ha")
            with cb:
                st.metric(
                    t("ap_model_mode_label", lang),
                    f"{c_mode:.2f} sc/ha",
                    delta=t("ap_model_mode_delta", lang, delta=f"{delta:+.2f}") if calib and delta != 0 else None,
                )
            with cc:
                st.metric(t("mc_maximum", lang), f"{p['max']:.1f} sc/ha")

            if calib and delta != 0:
                st.caption(
                    t("ap_model_shift_caption", lang,
                      default=f"{d_mode:.2f}",
                      calibrated=f"{c_mode:.2f}",
                      delta=f"{delta:+.2f}",
                      n=p["n_outcomes"])
                )
            st.markdown("---")

        if is_calibrated:
            st.info(t("ap_model_apply_hint", lang))
