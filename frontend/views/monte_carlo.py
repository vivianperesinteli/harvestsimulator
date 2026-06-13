"""Página Monte Carlo — simulação de risco com distribuições triangulares."""

from __future__ import annotations
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import io
from frontend.navigation import go as navigate
from frontend.api import monte_carlo as run_mc

# Parâmetros padrão (fonte: colega, Excel v7)
_DEFAULTS = {
    "d3": {"label": "IST · D3 (Tratamento de Sementes)", "min": -5.0, "mode": 0.0, "max": 3.0},
    "d6": {"label": "Planting Technique · D6 (Tecnologia)", "min": -4.0, "mode": 0.0, "max": 3.0},
    "d2": {"label": "Genetic Yield Potential · D2 (Cultivar)", "min": -8.0, "mode": 0.0, "max": 6.0},
}


def render() -> None:
    result    = st.session_state.get("sim_result")
    context   = st.session_state.get("sim_context")
    decisions = st.session_state.get("sim_decisions")

    if not result or not context or not decisions:
        st.warning("Run a simulation first to use Monte Carlo.")
        if st.button("← Go to Simulation"):
            navigate("input")
        return

    st.markdown('<div class="page-title">Monte Carlo Simulation</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Triangular distributions for D2 · D3 · D6 + ENSO rain sampling</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Configuração ──────────────────────────────────────────────────────
    st.markdown('<div class="section-hdr">Configuration</div>', unsafe_allow_html=True)

    col_iter, col_thresh = st.columns(2)
    with col_iter:
        n_iter = st.slider("Number of iterations", 1000, 5000, 2000, 500)
    with col_thresh:
        fixed_base = result["base_effective"] - result["fixed_adj"]
        threshold = st.slider(
            "Risk threshold (sc/ha)",
            min_value=float(int(fixed_base - 20)),
            max_value=float(int(fixed_base + 30)),
            value=float(int(result["baseline"])),
            step=1.0,
            help="P(yield < threshold) will be calculated — how far below this value is unacceptable?",
        )

    st.markdown("**Triangular distribution parameters**")
    st.caption(
        "Mode = central estimate (Excel v7 value). "
        "Min/Max = plausible limits for the real variation of each variable's effect."
    )

    params = {}
    for key, meta in _DEFAULTS.items():
        with st.expander(meta["label"], expanded=False):
            c1, c2, c3 = st.columns(3)
            with c1:
                vmin = st.number_input("Minimum", value=meta["min"], step=0.5, key=f"mc_{key}_min")
            with c2:
                vmode = st.number_input("Mode", value=meta["mode"], step=0.5, key=f"mc_{key}_mode")
            with c3:
                vmax = st.number_input("Maximum", value=meta["max"], step=0.5, key=f"mc_{key}_max")

            if not (vmin <= vmode <= vmax):
                st.error("Required: minimum ≤ mode ≤ maximum")
            else:
                params[key] = {"min": vmin, "mode": vmode, "max": vmax}

    valid = len(params) == 3

    st.markdown("<br>", unsafe_allow_html=True)

    if not valid:
        st.warning("Fix the parameters before running.")
        return

    if st.button("▶ Run Monte Carlo", type="primary", use_container_width=True):
        with st.spinner(f"Running {n_iter:,} iterations…"):
            mc = run_mc(context, decisions, params, n_iter, threshold)

        if mc:
            st.session_state["mc_result"] = mc

    mc = st.session_state.get("mc_result")
    if not mc:
        return

    # ── Resultados ────────────────────────────────────────────────────────
    st.markdown('<div class="section-hdr">Resultados</div>', unsafe_allow_html=True)

    # Cards de estatísticas
    m1, m2, m3, m4, m5 = st.columns(5)
    risk_color = "#c62828" if mc["p_below"] > 0.20 else "#f57c00" if mc["p_below"] > 0.10 else "#2e7d32"
    for col, label, value, sub, color in [
        (m1, "Mean",     mc["mean"], "sc/ha", "#111"),
        (m2, "Std Dev",  mc["std"],  "sc/ha", "#111"),
        (m3, "P5",       mc["p5"],   "sc/ha (worst 5%)", "#c62828"),
        (m4, "P95",      mc["p95"],  "sc/ha (best 5%)", "#2e7d32"),
        (m5, f"P(yield < {threshold:.0f})", f"{mc['p_below']:.1%}", "risk", risk_color),
    ]:
        with col:
            st.markdown(f"""<div class="metric-card">
                <div class="mc-label">{label}</div>
                <div class="mc-value" style="color:{color};font-size:1.4rem">{value}</div>
                <div class="mc-sub">{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_hist, col_tornado = st.columns([3, 2])

    # ── Histograma + densidade ─────────────────────────────────────────────
    with col_hist:
        st.markdown("**Simulated Yield Distribution**")

        yields_arr = np.array(mc["yields"])

        fig_hist = go.Figure()

        # Histograma
        fig_hist.add_trace(go.Histogram(
            x=yields_arr,
            nbinsx=50,
            name="Frequency",
            marker_color="rgba(21,101,192,0.5)",
            marker_line=dict(color="rgba(21,101,192,0.8)", width=0.5),
        ))

        # KDE (approximate density via histnorm)
        fig_hist.add_trace(go.Histogram(
            x=yields_arr,
            nbinsx=50,
            histnorm="probability density",
            name="Density",
            marker_color="rgba(21,101,192,0.0)",
            marker_line=dict(color="rgba(21,101,192,0)", width=0),
            showlegend=False,
            yaxis="y2",
            visible=False,
        ))

        # Vertical reference lines
        for val, label, color, dash in [
            (mc["mean"],      "Mean",      "#111",     "solid"),
            (mc["p5"],        "P5",        "#c62828",  "dash"),
            (mc["p95"],       "P95",       "#2e7d32",  "dash"),
            (threshold,       "Threshold", "#f57c00",  "dot"),
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
                name=f"Below {threshold:.0f} sc/ha",
                marker_color="rgba(198,40,40,0.35)",
                marker_line=dict(color="rgba(198,40,40,0.5)", width=0.5),
            ))

        fig_hist.update_layout(
            height=380,
            barmode="overlay",
            xaxis_title="Yield (sc/ha)",
            yaxis_title="Frequency",
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
            f"Mean: {mc['mean']:.1f} · P5: {mc['p5']:.1f} · P95: {mc['p95']:.1f} · "
            f"Std Dev: {mc['std']:.1f} sc/ha  —  {n_iter:,} iterations"
        )

    # ── Tornado chart ──────────────────────────────────────────────────────
    with col_tornado:
        st.markdown("**Tornado — Contribution to Variance**")
        st.caption("Pearson correlation between each stochastic input and the simulated yield.")

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
            xaxis_title="Correlation with yield",
            xaxis_range=[-1, 1],
            margin=dict(t=10, l=10, r=60, b=40),
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(color="#1a1a2e", size=11),
            xaxis=dict(gridcolor="#f0f0f0"),
            showlegend=False,
        )
        st.plotly_chart(fig_tornado, use_container_width=True)
        st.caption("The larger the absolute value, the more that variable impacts result uncertainty.")

    # ── Comparação com path ótimo ──────────────────────────────────────────
    st.markdown('<div class="section-hdr">Comparison — Your Selection vs Optimal Path (Bayes EV)</div>', unsafe_allow_html=True)
    st.caption("Monte Carlo also run for the highest EV path — distributions side by side.")

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
        st.info("Your selection is already the optimal path — no additional comparison.")
    else:
        with st.spinner("Calculating Monte Carlo for the optimal path…"):
            mc_opt = run_mc(context, optimal_decisions, params, n_iter, threshold)

        if mc_opt:
            fig_comp = go.Figure()
            for yields_list, name, color in [
                (mc["yields"],     "Your selection", "rgba(21,101,192,0.5)"),
                (mc_opt["yields"], "Optimal path",   "rgba(46,125,50,0.5)"),
            ]:
                fig_comp.add_trace(go.Histogram(
                    x=yields_list, nbinsx=50, name=name,
                    marker_color=color,
                    marker_line=dict(color=color.replace("0.5", "0.8"), width=0.5),
                ))

            fig_comp.add_vline(x=mc["mean"],     line_color="#1565c0", line_dash="dash", line_width=1.5,
                               annotation_text=f"Selection mean: {mc['mean']:.1f}", annotation_font_size=10)
            fig_comp.add_vline(x=mc_opt["mean"], line_color="#2e7d32", line_dash="dash", line_width=1.5,
                               annotation_text=f"Optimal mean: {mc_opt['mean']:.1f}", annotation_font_size=10,
                               annotation_position="top left")

            fig_comp.update_layout(
                barmode="overlay",
                height=360,
                xaxis_title="Yield (sc/ha)",
                yaxis_title="Frequency",
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
                    <div class="mc-label">Mean gap</div>
                    <div class="mc-value" style="color:#2e7d32">+{mc_opt['mean'] - mc['mean']:.1f}</div>
                    <div class="mc-sub">sc/ha favoring the optimal path</div>
                </div>""", unsafe_allow_html=True)
            with c2:
                risk_gap = mc["p_below"] - mc_opt["p_below"]
                st.markdown(f"""<div class="metric-card">
                    <div class="mc-label">Risk gap P(yield < {threshold:.0f})</div>
                    <div class="mc-value" style="color:#c62828">{risk_gap:+.1%}</div>
                    <div class="mc-sub">additional risk of your selection</div>
                </div>""", unsafe_allow_html=True)

    # ── Export CSV ─────────────────────────────────────────────────────────
    st.markdown('<div class="section-hdr">Export</div>', unsafe_allow_html=True)

    df_export = pd.DataFrame({"yield_sc_ha": mc["yields"]})
    df_export.index.name = "iteration"
    df_export.index += 1

    csv_bytes = df_export.to_csv().encode("utf-8")
    st.download_button(
        label="⬇ Download results (CSV)",
        data=csv_bytes,
        file_name="monte_carlo_results.csv",
        mime="text/csv",
        use_container_width=True,
    )
