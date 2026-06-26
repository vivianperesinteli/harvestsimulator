"""Monte Carlo page — risk simulation with triangular distributions."""

from __future__ import annotations
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import io
from frontend.navigation import go as navigate
from frontend.api import monte_carlo as run_mc
from frontend.i18n import t

# Default triangular parameters — sourced from Decision_Tree_v7_Baseline_Adjusted.xlsx
# sheet "Baseline & Nós": min/max = worst/best option adjustments (sc/ha), mode = 0
_DEFAULTS = {
    "d3": {"label_key": "mc_param_d3", "min": -5.0, "mode": 0.0, "max": 3.0},
    "d6": {"label_key": "mc_param_d6", "min": -4.0, "mode": 0.0, "max": 3.0},
    "d2": {"label_key": "mc_param_d2", "min": -8.0, "mode": 0.0, "max": 6.0},
}


def render() -> None:
    lang = st.session_state.get("lang", "en")
    result    = st.session_state.get("sim_result")
    context   = st.session_state.get("sim_context")
    decisions = st.session_state.get("sim_decisions")

    if not result or not context or not decisions:
        st.warning(t("mc_no_sim", lang))
        if st.button(t("mc_go_sim", lang)):
            navigate("input")
        return

    st.markdown(f'<div class="page-title">{t("mc_title", lang)}</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="page-subtitle">{t("mc_subtitle", lang)}</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Configuration ─────────────────────────────────────────────────────
    st.markdown(f'<div class="section-hdr">{t("mc_config_hdr", lang)}</div>', unsafe_allow_html=True)

    col_iter, col_thresh = st.columns(2)
    with col_iter:
        n_iter = st.slider(t("mc_n_iter", lang), 1000, 5000, 2000, 500)
    with col_thresh:
        fixed_base = result["base_effective"] - result["fixed_adj"]
        threshold = st.slider(
            t("mc_threshold", lang),
            min_value=float(int(fixed_base - 20)),
            max_value=float(int(fixed_base + 30)),
            value=float(int(result["baseline"])),
            step=1.0,
            help=t("mc_threshold_help", lang),
        )

    st.markdown(f"**{t('mc_tri_params', lang)}**")
    st.caption(t("mc_tri_caption", lang))

    params = {}
    for key, meta in _DEFAULTS.items():
        with st.expander(t(meta["label_key"], lang), expanded=False):
            c1, c2, c3 = st.columns(3)
            with c1:
                vmin = st.number_input(t("mc_minimum", lang), value=meta["min"], step=0.5, key=f"mc_{key}_min")
            with c2:
                vmode = st.number_input(t("mc_mode", lang), value=meta["mode"], step=0.5, key=f"mc_{key}_mode")
            with c3:
                vmax = st.number_input(t("mc_maximum", lang), value=meta["max"], step=0.5, key=f"mc_{key}_max")

            if not (vmin <= vmode <= vmax):
                st.error(t("mc_param_error", lang))
            else:
                params[key] = {"min": vmin, "mode": vmode, "max": vmax}

    valid = len(params) == 3

    st.markdown("<br>", unsafe_allow_html=True)

    if not valid:
        st.warning(t("mc_fix_params", lang))
        return

    if st.button(t("mc_run_btn", lang), type="primary", use_container_width=True):
        with st.spinner(t("mc_spinner", lang, n=f"{n_iter:,}")):
            mc = run_mc(context, decisions, params, n_iter, threshold)

        if mc:
            st.session_state["mc_result"] = mc

    mc = st.session_state.get("mc_result")
    if not mc:
        return

    # ── Results ───────────────────────────────────────────────────────────
    st.markdown(f'<div class="section-hdr">{t("mc_results_hdr", lang)}</div>', unsafe_allow_html=True)

    # Statistics cards
    m1, m2, m3, m4, m5 = st.columns(5)
    risk_color = "#c62828" if mc["p_below"] > 0.20 else "#f57c00" if mc["p_below"] > 0.10 else "#2e7d32"
    for col, label, value, sub, color in [
        (m1, t("mc_stat_mean", lang),  mc["mean"], t("mc_unit", lang), "#111"),
        (m2, t("mc_stat_std", lang),   mc["std"],  t("mc_unit", lang), "#111"),
        (m3, t("mc_stat_p5", lang),    mc["p5"],   t("mc_unit_worst", lang), "#c62828"),
        (m4, t("mc_stat_p95", lang),   mc["p95"],  t("mc_unit_best", lang), "#2e7d32"),
        (m5, t("mc_stat_risk", lang, threshold=f"{threshold:.0f}"), f"{mc['p_below']:.1%}", t("mc_risk_sub", lang), risk_color),
    ]:
        with col:
            st.markdown(f"""<div class="metric-card">
                <div class="mc-label">{label}</div>
                <div class="mc-value" style="color:{color};font-size:1.4rem">{value}</div>
                <div class="mc-sub">{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_hist, col_tornado = st.columns([3, 2])

    # ── Histogram + density ────────────────────────────────────────────────
    with col_hist:
        st.markdown(f"**{t('mc_hist_title', lang)}**")

        yields_arr = np.array(mc["yields"])

        fig_hist = go.Figure()

        fig_hist.add_trace(go.Histogram(
            x=yields_arr,
            nbinsx=50,
            name=t("mc_hist_freq", lang),
            marker_color="rgba(21,101,192,0.5)",
            marker_line=dict(color="rgba(21,101,192,0.8)", width=0.5),
        ))

        fig_hist.add_trace(go.Histogram(
            x=yields_arr,
            nbinsx=50,
            histnorm="probability density",
            name=t("mc_hist_density", lang),
            marker_color="rgba(21,101,192,0.0)",
            marker_line=dict(color="rgba(21,101,192,0)", width=0),
            showlegend=False,
            yaxis="y2",
            visible=False,
        ))

        # Vertical reference lines
        for val, label, color, dash in [
            (mc["mean"],  t("mc_stat_mean", lang),      "#111",    "solid"),
            (mc["p5"],    t("mc_stat_p5", lang),        "#c62828", "dash"),
            (mc["p95"],   t("mc_stat_p95", lang),       "#2e7d32", "dash"),
            (threshold,   t("mc_threshold_label", lang),"#f57c00", "dot"),
        ]:
            fig_hist.add_vline(
                x=val, line_color=color, line_dash=dash, line_width=1.5,
                annotation_text=f"{label}: {val:.1f}",
                annotation_position="top",
                annotation_font_size=10,
            )

        # Risk area (below threshold)
        x_risk = yields_arr[yields_arr < threshold]
        if len(x_risk):
            fig_hist.add_trace(go.Histogram(
                x=x_risk,
                nbinsx=50,
                name=t("mc_hist_below", lang, threshold=f"{threshold:.0f}"),
                marker_color="rgba(198,40,40,0.35)",
                marker_line=dict(color="rgba(198,40,40,0.5)", width=0.5),
            ))

        fig_hist.update_layout(
            height=380,
            barmode="overlay",
            xaxis_title=t("mc_yield_axis", lang),
            yaxis_title=t("mc_freq_axis", lang),
            margin=dict(t=20, l=20, r=20, b=40),
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(color="#1a1a2e", size=11),
            xaxis=dict(gridcolor="#f0f0f0"),
            yaxis=dict(gridcolor="#f0f0f0"),
        )
        st.plotly_chart(fig_hist, use_container_width=True)
        st.caption(
            t("mc_hist_caption", lang,
              mean=f"{mc['mean']:.1f}",
              p5=f"{mc['p5']:.1f}",
              p95=f"{mc['p95']:.1f}",
              std=f"{mc['std']:.1f}",
              n=f"{n_iter:,}")
        )

    # ── Tornado chart ──────────────────────────────────────────────────────
    with col_tornado:
        st.markdown(f"**{t('mc_tornado_title', lang)}**")
        st.caption(t("mc_tornado_caption", lang))

        tornado = mc["tornado"]
        t_df = pd.DataFrame([
            {"Variable": name, "Correlation": v["correlation"]}
            for name, v in tornado.items()
        ]).sort_values("Correlation", key=abs, ascending=True)

        colors_t = ["#2e7d32" if c >= 0 else "#c62828" for c in t_df["Correlation"]]

        fig_tornado = go.Figure(go.Bar(
            x=t_df["Correlation"],
            y=t_df["Variable"],
            orientation="h",
            marker_color=colors_t,
            text=[f"{c:+.3f}" for c in t_df["Correlation"]],
            textposition="outside",
        ))
        fig_tornado.add_vline(x=0, line_color="#999", line_width=1)
        fig_tornado.update_layout(
            height=380,
            xaxis_title=t("mc_corr_axis", lang),
            xaxis_range=[-1, 1],
            margin=dict(t=10, l=10, r=60, b=40),
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(color="#1a1a2e", size=11),
            xaxis=dict(gridcolor="#f0f0f0"),
            showlegend=False,
        )
        st.plotly_chart(fig_tornado, use_container_width=True)
        st.caption(t("mc_tornado_sub", lang))

    # ── Comparison with optimal path ───────────────────────────────────────
    st.markdown(f'<div class="section-hdr">{t("mc_comp_hdr", lang)}</div>', unsafe_allow_html=True)
    st.caption(t("mc_comp_caption", lang))

    optimal_idx = result["criteria"]["bayes_ev"]["path_idx"]
    optimal_path = result["paths"][optimal_idx]

    optimal_decisions = {
        **decisions,
        "d1_janela":    optimal_path["d1"],
        "d4_densidade": optimal_path["d4"],
        "d5_manejo":    optimal_path["d5"],
    }

    user_d1 = decisions["d1_janela"]
    opt_d1  = optimal_path["d1"]
    same_path = (
        user_d1 == opt_d1
        and decisions["d4_densidade"] == optimal_path["d4"]
        and decisions["d5_manejo"]    == optimal_path["d5"]
    )

    if same_path:
        st.info(t("mc_same_path", lang))
    else:
        with st.spinner(t("mc_comp_spinner", lang)):
            mc_opt = run_mc(context, optimal_decisions, params, n_iter, threshold)

        if mc_opt:
            fig_comp = go.Figure()
            for yields_list, name, color in [
                (mc["yields"],     t("mc_comp_your", lang),    "rgba(21,101,192,0.5)"),
                (mc_opt["yields"], t("mc_comp_optimal", lang), "rgba(46,125,50,0.5)"),
            ]:
                fig_comp.add_trace(go.Histogram(
                    x=yields_list, nbinsx=50, name=name,
                    marker_color=color,
                    marker_line=dict(color=color.replace("0.5", "0.8"), width=0.5),
                ))

            fig_comp.add_vline(x=mc["mean"], line_color="#1565c0", line_dash="dash", line_width=1.5,
                               annotation_text=t("mc_comp_sel_mean", lang, mean=f"{mc['mean']:.1f}"),
                               annotation_font_size=10)
            fig_comp.add_vline(x=mc_opt["mean"], line_color="#2e7d32", line_dash="dash", line_width=1.5,
                               annotation_text=t("mc_comp_opt_mean", lang, mean=f"{mc_opt['mean']:.1f}"),
                               annotation_font_size=10,
                               annotation_position="top left")

            fig_comp.update_layout(
                barmode="overlay",
                height=360,
                xaxis_title=t("mc_yield_axis", lang),
                yaxis_title=t("mc_freq_axis", lang),
                margin=dict(t=10, l=20, r=20, b=40),
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
                plot_bgcolor="white",
                paper_bgcolor="white",
                font=dict(color="#1a1a2e", size=11),
                xaxis=dict(gridcolor="#f0f0f0"),
                yaxis=dict(gridcolor="#f0f0f0"),
            )
            st.plotly_chart(fig_comp, use_container_width=True)

            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"""<div class="metric-card">
                    <div class="mc-label">{t("mc_mean_gap", lang)}</div>
                    <div class="mc-value" style="color:#2e7d32">+{mc_opt['mean'] - mc['mean']:.1f}</div>
                    <div class="mc-sub">{t("mc_mean_gap_sub", lang)}</div>
                </div>""", unsafe_allow_html=True)
            with c2:
                risk_gap = mc["p_below"] - mc_opt["p_below"]
                st.markdown(f"""<div class="metric-card">
                    <div class="mc-label">{t("mc_risk_gap", lang, threshold=f"{threshold:.0f}")}</div>
                    <div class="mc-value" style="color:#c62828">{risk_gap:+.1%}</div>
                    <div class="mc-sub">{t("mc_risk_gap_sub", lang)}</div>
                </div>""", unsafe_allow_html=True)

    # ── Export CSV ─────────────────────────────────────────────────────────
    st.markdown(f'<div class="section-hdr">{t("mc_export_hdr", lang)}</div>', unsafe_allow_html=True)

    df_export = pd.DataFrame({"yield_sc_ha": mc["yields"]})
    df_export.index.name = "iteration"
    df_export.index += 1

    csv_bytes = df_export.to_csv().encode("utf-8")
    st.download_button(
        label=t("mc_download_btn", lang),
        data=csv_bytes,
        file_name="monte_carlo_results.csv",
        mime="text/csv",
        use_container_width=True,
    )
