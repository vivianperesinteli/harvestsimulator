"""History Page — session simulations with comparison view."""

from __future__ import annotations
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from frontend.navigation import go as navigate


_D1_SHORT = {
    "Precoce (até 15/out)":    "Early",
    "Ótima (16/out – 10/nov)": "Optimal",
    "Tardia (após 10/nov)":    "Late",
}
_D4_SHORT = {
    "Baixa (≤280k sementes/ha)": "Low",
    "Média (280k–340k)":          "Medium",
    "Alta (>340k)":               "High",
}
_D5_SHORT = {
    "Alto (≥3 fung. + monitor ferrugem)": "Intensive",
    "Padrão (2 aplicações)":              "Standard",
    "Baixo (1 ou nenhuma)":               "Reduced",
}


def render() -> None:
    history: list = st.session_state.get("sim_history", [])

    st.markdown('<div class="page-title">Simulation History</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">All simulations run in this session</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    if not history:
        st.info("No simulations run in this session yet.")
        if st.button("Start simulation →", type="primary"):
            navigate("input")
        return

    # ── Summary ────────────────────────────────────────────────────────────
    evs = [h["result"]["criteria"]["bayes_ev"]["value"] for h in history]
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""<div class="metric-card">
            <div class="mc-label">Total simulations</div>
            <div class="mc-value">{len(history)}</div>
            <div class="mc-sub">this session</div>
        </div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""<div class="metric-card">
            <div class="mc-label">Best EV simulated</div>
            <div class="mc-value" style="color:#2e7d32">{max(evs):.1f}</div>
            <div class="mc-sub">sc/ha</div>
        </div>""", unsafe_allow_html=True)
    with m3:
        st.markdown(f"""<div class="metric-card">
            <div class="mc-label">Average EV</div>
            <div class="mc-value">{sum(evs)/len(evs):.1f}</div>
            <div class="mc-sub">sc/ha</div>
        </div>""", unsafe_allow_html=True)
    with m4:
        best_id = evs.index(max(evs)) + 1
        st.markdown(f"""<div class="metric-card">
            <div class="mc-label">Top simulation</div>
            <div class="mc-value">#{best_id}</div>
            <div class="mc-sub">{history[evs.index(max(evs))]['summary']}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Simulation list ────────────────────────────────────────────────────
    st.markdown('<div class="section-hdr">Simulations Run</div>', unsafe_allow_html=True)

    for sim in reversed(history):
        result   = sim["result"]
        ev_best  = result["criteria"]["bayes_ev"]["value"]
        ev_user  = result["user_selection"]["ev"]
        opt_path = result["paths"][result["criteria"]["bayes_ev"]["path_idx"]]

        opt_label = (
            f"{_D1_SHORT.get(opt_path['d1'], opt_path['d1'])} · "
            f"{_D4_SHORT.get(opt_path['d4'], opt_path['d4'])} · "
            f"{_D5_SHORT.get(opt_path['d5'], opt_path['d5'])}"
        )

        st.markdown(f"""
        <div class="hist-card">
            <div class="hist-number">#{sim['id']}</div>
            <div class="hist-main">
                <div class="hist-title">{sim['summary']}</div>
                <div class="hist-sub">{sim['timestamp']} &middot; Best path: {opt_label}</div>
            </div>
            <div class="hist-ev">
                <div class="hist-ev-val">{ev_best:.1f}</div>
                <div class="hist-ev-unit">sc/ha best EV</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander(f"Details — Simulation #{sim['id']}"):
            dcol, rcol = st.columns(2)
            with dcol:
                st.markdown("**Inputs**")
                display = sim.get("display", {})
                if display:
                    rows_html = '<div class="review-card">'
                    for k, v in display.items():
                        rows_html += f'<div class="review-row"><span class="review-key">{k}</span><span class="review-val">{v}</span></div>'
                    rows_html += "</div>"
                    st.markdown(rows_html, unsafe_allow_html=True)
                else:
                    st.caption("Display labels not available for this simulation.")
            with rcol:
                st.markdown("**Decision criteria**")
                criteria = result["criteria"]
                crit_data = []
                for key, (name, _) in {
                    "bayes_ev": ("Bayes EV", ""),
                    "wald":     ("Wald", ""),
                    "maximax":  ("Maximax", ""),
                    "laplace":  ("Laplace", ""),
                    "hurwicz":  ("Hurwicz", ""),
                    "savage":   ("Savage", ""),
                }.items():
                    c = criteria[key]
                    p = result["paths"][c["path_idx"]]
                    crit_data.append({
                        "Criterion": name,
                        "Recommendation": (
                            f"{_D1_SHORT.get(p['d1'],p['d1'])} · "
                            f"{_D4_SHORT.get(p['d4'],p['d4'])} · "
                            f"{_D5_SHORT.get(p['d5'],p['d5'])}"
                        ),
                        "Value (sc/ha)": f"{c['value']:.1f}",
                    })
                st.dataframe(pd.DataFrame(crit_data), use_container_width=True, hide_index=True)

            st.markdown(f"""
            <div style="display:flex;gap:16px;margin-top:12px">
                <div class="metric-card" style="flex:1;padding:12px 16px">
                    <div class="mc-label">Your selection EV</div>
                    <div class="mc-value" style="font-size:1.3rem">{ev_user:.1f}</div>
                    <div class="mc-sub">sc/ha</div>
                </div>
                <div class="metric-card" style="flex:1;padding:12px 16px">
                    <div class="mc-label">Best available EV</div>
                    <div class="mc-value" style="font-size:1.3rem;color:#2e7d32">{ev_best:.1f}</div>
                    <div class="mc-sub">sc/ha</div>
                </div>
                <div class="metric-card" style="flex:1;padding:12px 16px">
                    <div class="mc-label">Gap</div>
                    <div class="mc-value" style="font-size:1.3rem;color:#{'c62828' if ev_user < ev_best else '2e7d32'}">{ev_user - ev_best:+.1f}</div>
                    <div class="mc-sub">sc/ha</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"Restore this simulation", key=f"restore_{sim['id']}"):
                st.session_state.sim_result    = sim["result"]
                st.session_state.sim_context   = sim["context"]
                st.session_state.sim_decisions = sim["decisions"]
                st.session_state.sim_display   = sim.get("display")
                navigate("results")

        st.markdown("<br>", unsafe_allow_html=True)

    # ── Comparison chart ───────────────────────────────────────────────────
    if len(history) >= 2:
        st.markdown('<div class="section-hdr">Comparison — EV across simulations</div>', unsafe_allow_html=True)

        ids_list   = [f"#{h['id']} {h['summary'][:25]}" for h in history]
        ev_best_l  = [h["result"]["criteria"]["bayes_ev"]["value"] for h in history]
        ev_user_l  = [h["result"]["user_selection"]["ev"] for h in history]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            name="EV — Best path",
            x=ids_list,
            y=ev_best_l,
            marker_color="#2d8a56",
            text=[f"{v:.1f}" for v in ev_best_l],
            textposition="outside",
        ))
        fig.add_trace(go.Bar(
            name="EV — Your selection",
            x=ids_list,
            y=ev_user_l,
            marker_color="#1565c0",
            text=[f"{v:.1f}" for v in ev_user_l],
            textposition="outside",
        ))
        fig.add_hline(y=60, line_dash="dot", line_color="#999",
                      annotation_text="Baseline 60 sc/ha", annotation_font_size=10)
        fig.update_layout(
            barmode="group",
            height=380,
            yaxis_title="EV (sc/ha)",
            xaxis_title="Simulation",
            margin=dict(t=20, l=40, r=20, b=40),
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(color="#1a1a2e", size=11),
            yaxis=dict(gridcolor="#f0f0f0"),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Input comparison table
        st.markdown('<div class="section-hdr">Input Comparison</div>', unsafe_allow_html=True)
        comp_rows = {}
        all_keys = list(history[0].get("display", {}).keys())
        for k in all_keys:
            comp_rows[k] = [h.get("display", {}).get(k, "—") for h in history]
        comp_rows["EV Best (sc/ha)"] = [f"{ev:.1f}" for ev in ev_best_l]
        comp_rows["EV User (sc/ha)"] = [f"{ev:.1f}" for ev in ev_user_l]

        comp_df = pd.DataFrame(comp_rows, index=[f"#{h['id']}" for h in history]).T
        st.dataframe(comp_df, use_container_width=True)

    # ── Export history ─────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    export_rows = []
    for h in history:
        row = {"id": h["id"], "timestamp": h["timestamp"]}
        row.update(h.get("display", {}))
        row["ev_best"] = h["result"]["criteria"]["bayes_ev"]["value"]
        row["ev_user"] = h["result"]["user_selection"]["ev"]
        export_rows.append(row)
    df_exp = pd.DataFrame(export_rows)
    col_exp, _ = st.columns([1, 4])
    with col_exp:
        st.download_button(
            "⬇ Export history (CSV)",
            data=df_exp.to_csv(index=False).encode("utf-8"),
            file_name="simulation_history.csv",
            mime="text/csv",
            use_container_width=True,
        )
