"""Explainer Panel — How the simulator reaches its recommendations."""

from __future__ import annotations
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from frontend.navigation import go as nav_go

# ── Step definitions ──────────────────────────────────────────────────────────

_STEPS = [
    (1,  "Starting Point",         "Historical average yield as the model baseline"),
    (2,  "Field Context",          "7 field factors adjust the baseline"),
    (3,  "Producer Decisions",     "6 decisions — fixed and variable"),
    (4,  "27 Possible Paths",      "Combinations of variable decisions"),
    (5,  "Weather & ENSO",         "Climate scenarios and their probabilities"),
    (6,  "Interaction Effects",    "Combinations that amplify or penalize the outcome"),
    (7,  "Payoff Matrix",          "27 paths × 3 climates = all possible outcomes"),
    (8,  "Decision Criteria",      "6 perspectives for choosing the best path"),
    (9,  "Risk Analysis",          "10,000 simulations estimate the confidence interval"),
    (10, "Final Recommendation",   "The model identifies the combination with the highest expected return"),
]

_N = len(_STEPS)

# ── Helpers ───────────────────────────────────────────────────────────────────

def _step_key() -> int:
    if "explainer_step" not in st.session_state:
        st.session_state.explainer_step = 1
    return st.session_state.explainer_step


def _progress_bar(current: int) -> None:
    pct = int((current / _N) * 100)
    steps_html = ""
    for num, title, _ in _STEPS:
        if num < current:
            cls = "exp-step-done"
            icon = "✓"
        elif num == current:
            cls = "exp-step-active"
            icon = str(num)
        else:
            cls = "exp-step-todo"
            icon = str(num)
        steps_html += f'<div class="exp-step-dot {cls}" title="{title}">{icon}</div>'
        if num < _N:
            line_cls = "exp-step-line-done" if num < current else "exp-step-line-todo"
            steps_html += f'<div class="exp-step-line {line_cls}"></div>'

    st.markdown(f"""
    <div class="exp-progress-wrap">
        <div class="exp-step-row">{steps_html}</div>
        <div class="exp-progress-bar-bg">
            <div class="exp-progress-bar-fill" style="width:{pct}%"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _nav_buttons(current: int) -> None:
    c_back, c_info, c_next = st.columns([1, 4, 1])
    with c_back:
        if current > 1:
            if st.button("← Previous", use_container_width=True):
                st.session_state.explainer_step -= 1
                st.rerun()
    with c_info:
        st.markdown(
            f'<div style="text-align:center;font-size:0.78rem;color:#6b6b8a;padding-top:8px">'
            f'Step {current} of {_N}</div>',
            unsafe_allow_html=True,
        )
    with c_next:
        if current < _N:
            if st.button("Next →", type="primary", use_container_width=True):
                st.session_state.explainer_step += 1
                st.rerun()
        else:
            if st.button("Restart", use_container_width=True):
                st.session_state.explainer_step = 1
                st.rerun()


def _step_header(num: int, title: str, desc: str) -> None:
    st.markdown(f"""
    <div class="exp-step-header">
        <div class="exp-step-number">Step {num}</div>
        <div class="exp-step-title">{title}</div>
        <div class="exp-step-desc">{desc}</div>
    </div>
    """, unsafe_allow_html=True)


def _formula_box(formula: str, label: str = "") -> None:
    st.markdown(f"""
    <div class="exp-formula">
        {f'<div class="exp-formula-label">{label}</div>' if label else ""}
        <div class="exp-formula-text">{formula}</div>
    </div>
    """, unsafe_allow_html=True)


def _info_card(title: str, body: str, color: str = "#1a5c38") -> None:
    st.markdown(f"""
    <div class="exp-info-card" style="border-left-color:{color}">
        <div class="exp-info-title">{title}</div>
        <div class="exp-info-body">{body}</div>
    </div>
    """, unsafe_allow_html=True)


# ── Steps ─────────────────────────────────────────────────────────────────────

def _render_step_1() -> None:
    _step_header(1, "Starting Point", "Mato Grosso's historical average yield serves as the model anchor")

    c1, c2 = st.columns([1, 2], gap="large")
    with c1:
        st.markdown("""
        <div style="text-align:center;padding:40px 20px;background:#fff;border-radius:12px;border:1px solid #e4e4f0;box-shadow:0 2px 8px rgba(0,0,0,0.06)">
            <div style="font-size:0.7rem;font-weight:700;color:#6b6b8a;text-transform:uppercase;letter-spacing:0.1em">Baseline</div>
            <div style="font-size:5rem;font-weight:900;color:#1a5c38;line-height:1">60</div>
            <div style="font-size:1rem;color:#3a3a5c;font-weight:600">sc/ha</div>
            <div style="font-size:0.72rem;color:#6b6b8a;margin-top:8px">Source: CONAB · MT 2023/24</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        _info_card("Why 60 sc/ha?",
            "The average yield in Mato Grosso for the 2023/24 season was 60 bags per hectare, "
            "according to CONAB's survey. This figure represents the performance of an average "
            "producer in the region — before any adjustments for specific field conditions.")

        st.markdown("<br>", unsafe_allow_html=True)
        _formula_box(
            "Yield = <strong>60</strong> + context adjustments + decision adjustments + climate adjustment",
            label="Model general equation"
        )

        st.markdown("<br>", unsafe_allow_html=True)
        _info_card("How adjustments work",
            "Each factor — soil, climate, management, cultivar — adds or subtracts bags per hectare "
            "relative to this reference. Producers with conditions better than average receive a "
            "positive adjustment; worse conditions receive a negative adjustment.",
            color="#1565c0")


def _render_step_2(result: dict | None) -> None:
    _step_header(2, "Field Context",
        "7 factors outside the producer's control describe the field conditions")

    col_table, col_chart = st.columns([1, 1], gap="large")

    with col_table:
        st.markdown("**The 7 context factors and their impact (sc/ha):**")
        labels = [
            ("C1", "Region",          "Favorable (Sorriso, Sinop...)", "+5", "Challenging (Primavera, Querência)", "−6"),
            ("C2", "Soil Texture",    "Clay / well-structured",        "+5", "Sandy / low retention",              "−7"),
            ("C3", "Soil pH",         "Adequate 5.5–6.5",              "+4", "Critical <5.0 or >6.8",              "−6"),
            ("C4", "Drainage",        "No waterlogging",               "+3", "Frequent flooding",                  "−8"),
            ("C5", "Soil Type",       "Latosol / Nitosol",             "+5", "Neosol / Gleisol",                   "−7"),
            ("C6", "Area",            "Above 200 ha",                  "+2", "Up to 50 ha",                        "−1"),
            ("C7", "Climate Outlook", "El Niño",                       "+3", "La Niña",                            "−3"),
        ]
        for cod, nome, melhor, val_m, pior, val_p in labels:
            st.markdown(f"""
            <div style="padding:8px 0;border-bottom:1px solid #e4e4f0;font-size:0.8rem">
                <span style="color:#6b6b8a;font-weight:600;min-width:28px;display:inline-block">{cod}</span>
                <span style="color:#1a1a2e;font-weight:600">{nome}</span><br>
                <span style="color:#2e7d32">▲ {melhor} ({val_m} sc/ha)</span>
                &nbsp;&nbsp;
                <span style="color:#c62828">▼ {pior} ({val_p} sc/ha)</span>
            </div>
            """, unsafe_allow_html=True)

    with col_chart:
        st.markdown("**Adjustment range per factor:**")
        nomes = ["Region", "Texture", "pH", "Drainage", "Soil Type", "Area", "ENSO"]
        positivos = [5, 5, 4, 3, 5, 2, 3]
        negativos = [-6, -7, -6, -8, -7, -1, -3]

        fig = go.Figure()
        fig.add_bar(x=positivos, y=nomes, orientation="h",
                    marker_color="#2d8a56", name="Max gain",
                    text=[f"+{v}" for v in positivos], textposition="outside")
        fig.add_bar(x=negativos, y=nomes, orientation="h",
                    marker_color="#c62828", name="Max penalty",
                    text=[str(v) for v in negativos], textposition="outside")
        fig.update_layout(
            barmode="overlay", height=280, margin=dict(l=80, r=60, t=10, b=30),
            showlegend=True, plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(
                gridcolor="#d8d8e8", zeroline=True, zerolinecolor="#666",
                tickfont=dict(color="#1a1a2e", size=11),
            ),
            yaxis=dict(
                tickfont=dict(color="#1a1a2e", size=11),
            ),
            legend=dict(orientation="h", y=-0.18, font=dict(color="#1a1a2e", size=11)),
            font=dict(color="#1a1a2e", size=11),
        )
        st.plotly_chart(fig, use_container_width=True)

        if result:
            ctx_adj = result.get("context_adj", 0)
            color = "#2e7d32" if ctx_adj >= 0 else "#c62828"
            sign = "+" if ctx_adj >= 0 else ""
            st.markdown(f"""
            <div style="background:#f1f8f3;border-left:3px solid #1a5c38;padding:10px 14px;border-radius:0 8px 8px 0;margin-top:8px">
                <span style="font-size:0.75rem;color:#1a5c38;font-weight:700">YOUR SIMULATION RESULT</span><br>
                <span style="font-size:1.4rem;font-weight:800;color:{color}">{sign}{ctx_adj:.1f} sc/ha</span>
                <span style="font-size:0.8rem;color:#3a3a5c"> context adjustment</span><br>
                <span style="font-size:0.8rem;color:#1a5c38">Adjusted base: {result['context_base']:.0f} sc/ha</span>
            </div>
            """, unsafe_allow_html=True)


def _render_step_3(result: dict | None) -> None:
    _step_header(3, "Producer Decisions",
        "6 management decisions — three shift all scenarios equally, three create the scenarios")

    _formula_box(
        "Effective base = 60 + context + <strong style='color:#b35c00'>D2 (cultivar) + D3 (seed treatment) + D6 (planter)</strong> "
        "+ <strong style='color:#1a5c38'>D1 (window) + D4 (density) + D5 (disease management)</strong>"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    c_fixed, c_var = st.columns(2, gap="large")

    with c_fixed:
        st.markdown("""
        <div style="background:#fff8e1;border:1px solid #ffe082;border-radius:10px;padding:20px">
            <div style="font-size:0.7rem;font-weight:700;color:#b35c00;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:12px">
                🔒 Fixed Decisions — shift all 27 scenarios equally
            </div>
        """, unsafe_allow_html=True)
        for cod, nome, desc, faixa in [
            ("D2", "Cultivar",       "Genetic potential of the variety",        "−8 to +6 sc/ha"),
            ("D3", "Seed Treatment", "Industrial seed treatment (TSI)",          "−5 to +3 sc/ha"),
            ("D6", "Planter",        "Planting technology and precision",        "−4 to +3 sc/ha"),
        ]:
            st.markdown(f"""
            <div style="padding:8px 0;border-bottom:1px solid #ffe082">
                <span style="font-weight:700;color:#1a1a2e">{cod} · {nome}</span><br>
                <span style="font-size:0.78rem;color:#3a3a5c">{desc}</span><br>
                <span style="font-size:0.72rem;color:#b35c00;font-weight:600">{faixa}</span>
            </div>
            """, unsafe_allow_html=True)
        if result:
            st.markdown(f"""
            <div style="margin-top:10px;font-size:0.8rem;color:#b35c00;font-weight:700">
                Fixed adjustment in your simulation: {result['fixed_adj']:+.1f} sc/ha
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c_var:
        st.markdown("""
        <div style="background:#e8f5e9;border:1px solid #a5d6a7;border-radius:10px;padding:20px">
            <div style="font-size:0.7rem;font-weight:700;color:#1a5c38;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:12px">
                🔀 Variable Decisions — each combination generates a different scenario
            </div>
        """, unsafe_allow_html=True)
        for cod, nome, desc, faixa, opts in [
            ("D1", "Planting Window",    "Sowing period",              "−8 to +4 sc/ha", "3 options"),
            ("D4", "Density",            "Seeds per hectare",          "−1 to +2 sc/ha", "3 options"),
            ("D5", "Disease Management", "Number of fungicide sprays", "−7 to +5 sc/ha", "3 options"),
        ]:
            st.markdown(f"""
            <div style="padding:8px 0;border-bottom:1px solid #a5d6a7">
                <span style="font-weight:700;color:#1a1a2e">{cod} · {nome}</span><br>
                <span style="font-size:0.78rem;color:#3a3a5c">{desc}</span><br>
                <span style="font-size:0.72rem;color:#1a5c38;font-weight:600">{faixa} · {opts}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("""
        <div style="margin-top:10px;font-size:0.8rem;color:#1a5c38;font-weight:700">
            3 × 3 × 3 = 27 combinations evaluated simultaneously
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    _info_card("Why separate fixed from variable?",
        "Fixed decisions (D2, D3, D6) shift all 27 paths by the same value — "
        "they don't change which combination is best, only the absolute yield level. "
        "Variable decisions (D1, D4, D5) change the ranking among paths because each "
        "interacts differently with climate scenarios.", color="#1565c0")


def _render_step_4(result: dict | None) -> None:
    _step_header(4, "27 Possible Paths",
        "D1 × D4 × D5 = 3 × 3 × 3 = 27 combinations evaluated in parallel")

    c_tree, c_explain = st.columns([3, 2], gap="large")

    with c_tree:
        st.markdown("**Combination structure:**")

        rows = []
        for i, d1 in enumerate(["Early", "Optimal", "Late"]):
            for j, d4 in enumerate(["Low", "Medium", "High"]):
                for k, d5 in enumerate(["Intensive", "Standard", "Reduced"]):
                    path_num = i * 9 + j * 3 + k + 1
                    rows.append({"#": path_num, "D1 · Window": d1, "D4 · Density": d4, "D5 · Management": d5})

        df = pd.DataFrame(rows).set_index("#")
        highlight_idx = None
        if result:
            opt_idx = result.get("criteria", {}).get("bayes_ev", {}).get("path_idx", None)
            highlight_idx = opt_idx + 1 if opt_idx is not None else None

        def _hl(row):
            if highlight_idx and row.name == highlight_idx:
                return ["background-color:#e8f5e9;font-weight:bold"] * len(row)
            return [""] * len(row)

        st.dataframe(df.style.apply(_hl, axis=1), use_container_width=True, height=400)
        if highlight_idx:
            st.caption(f"★ row {highlight_idx} = best path in your simulation")

    with c_explain:
        _info_card("What are these 27 paths?",
            "Each row in the table represents a complete management strategy: "
            "a specific planting window, a specific density, and a specific level "
            "of disease protection. The simulator evaluates all of them simultaneously.")

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
        <div style="background:#ffffff;border:1.5px solid #c4c4d4;border-radius:10px;padding:16px;box-shadow:0 2px 8px rgba(0,0,0,0.08)">
            <div style="font-size:0.7rem;font-weight:700;color:#4a4a6a;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:10px">Combination logic</div>
        """, unsafe_allow_html=True)
        for n, label, sub in [
            ("3", "window options",     "Early · Optimal · Late"),
            ("×", "", ""),
            ("3", "density options",    "Low · Medium · High"),
            ("×", "", ""),
            ("3", "management options", "Intensive · Standard · Reduced"),
            ("=", "", ""),
            ("27", "paths evaluated",  "in parallel, for each climate scenario"),
        ]:
            if n in ("×", "="):
                st.markdown(f'<div style="text-align:center;font-size:1.4rem;color:#1a5c38;font-weight:700;line-height:1.2">{n}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:10px;padding:6px 0;border-bottom:1px solid #f0f0f0">
                    <div style="font-size:1.6rem;font-weight:800;color:#1a5c38;min-width:36px;text-align:right">{n}</div>
                    <div>
                        <div style="font-size:0.82rem;font-weight:600;color:#1a1a2e">{label}</div>
                        <div style="font-size:0.7rem;color:#6b6b8a">{sub}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


def _render_step_5(result: dict | None) -> None:
    _step_header(5, "Weather & ENSO",
        "Each of the 27 paths is evaluated under 3 climate states with probabilities conditional on ENSO")

    from backend.data import RAIN_STATES, RAIN_PROBS

    c_prob, c_explain = st.columns([3, 2], gap="large")

    with c_prob:
        st.markdown("**Rainfall probabilities during R3–R6 (grain filling):**")
        enso_labels = {
            "El Niño (chuva regular em MT)":    "El Niño",
            "Neutro":                            "Neutral",
            "La Niña (chuva concentrada/curta)": "La Niña",
        }
        rain_labels = {
            "Seca (<150 mm)":      "Dry",
            "Normal (150–250 mm)": "Normal",
            "Úmida (>250 mm)":     "Wet",
        }
        rain_adjs = {k: v for k, v in RAIN_STATES.items()}

        rows = []
        for enso_key, enso_short in enso_labels.items():
            row = {"ENSO": enso_short}
            for rain_key, rain_short in rain_labels.items():
                prob = RAIN_PROBS[enso_key][rain_key]
                adj  = rain_adjs[rain_key]
                sign = "+" if adj > 0 else ""
                row[f"{rain_short}\n({sign}{adj:.0f} sc/ha)"] = f"{prob:.0%}"
            rows.append(row)

        df_prob = pd.DataFrame(rows).set_index("ENSO")
        user_enso = None
        if result:
            ctx = st.session_state.get("sim_context", {})
            user_enso = enso_labels.get(ctx.get("c7_enso", ""), None)

        def _hl_enso(row):
            if user_enso and row.name == user_enso:
                return ["background-color:#e8f5e9;font-weight:bold"] * len(row)
            return [""] * len(row)

        st.dataframe(df_prob.style.apply(_hl_enso, axis=1), use_container_width=True)
        if user_enso:
            st.caption(f"★ highlighted row = ENSO in your simulation ({user_enso})")

        st.markdown("<br>", unsafe_allow_html=True)
        fig = go.Figure()
        colors = {"Dry": "#c62828", "Normal": "#f57c00", "Wet": "#1565c0"}
        for enso_key, enso_short in enso_labels.items():
            for rain_key, rain_short in rain_labels.items():
                prob = RAIN_PROBS[enso_key][rain_key]
                fig.add_bar(
                    x=[enso_short], y=[prob],
                    name=rain_short,
                    marker_color=colors[rain_short],
                    showlegend=(enso_short == "El Niño"),
                    text=f"{prob:.0%}", textposition="inside",
                )
        fig.update_layout(
            barmode="stack", height=220,
            margin=dict(l=20, r=20, t=10, b=30),
            plot_bgcolor="white", paper_bgcolor="white",
            legend=dict(orientation="h", y=-0.2, font=dict(color="#1a1a2e", size=11)),
            yaxis=dict(
                tickformat=".0%", gridcolor="#d8d8e8",
                tickfont=dict(color="#1a1a2e", size=11),
            ),
            xaxis=dict(tickfont=dict(color="#1a1a2e", size=11)),
            font=dict(color="#1a1a2e", size=11),
        )
        st.plotly_chart(fig, use_container_width=True)

    with c_explain:
        _info_card("Why use ENSO?",
            "El Niño and La Niña significantly alter rainfall distribution in Mato Grosso "
            "during grain filling (R3–R6). In La Niña years, the probability of drought "
            "rises to 50% — completely changing which strategy is safest.")

        st.markdown("<br>", unsafe_allow_html=True)
        _info_card("Adjustment per climate state",
            "• Dry (<150 mm): −8 sc/ha\n"
            "• Normal (150–250 mm): +2 sc/ha\n"
            "• Wet (>250 mm): +4 sc/ha\n\n"
            "These values are applied on top of each path to generate the final matrix.",
            color="#1565c0")

        st.markdown("<br>", unsafe_allow_html=True)
        _info_card("Result",
            "Each of the 27 paths is evaluated under 3 climates → "
            "a matrix of 27 × 3 = 81 possible outcomes.",
            color="#b35c00")


def _render_step_6() -> None:
    _step_header(6, "Interaction Effects",
        "Some variable combinations produce effects that go beyond the sum of their parts")

    st.markdown("""
    <div style="background:#fff3e0;border-left:4px solid #f57c00;padding:12px 16px;border-radius:0 8px 8px 0;margin-bottom:20px;font-size:0.85rem;color:#3a3a5c">
        <strong>What is an interaction?</strong> The additive model assumes each factor contributes independently.
        But in practice, a high-potential cultivar + poor disease management is <em>more</em> damaging than the sum of the two.
        Interaction terms capture these effects.
    </div>
    """, unsafe_allow_html=True)

    inter_data = [
        {
            "titulo": "Interaction 1 — Cultivar × Disease Management (D2 × D5)",
            "cor": "#1a5c38",
            "desc": "High genetic potential cultivars are more susceptible to rust. With adequate management, they deliver their potential. With poor management, high potential becomes a liability.",
            "linhas": [
                ("High potential + Intensive management", "+2.0 sc/ha", "#2e7d32"),
                ("High potential + Reduced management",   "−2.0 sc/ha", "#c62828"),
                ("Intermediate + Intensive management",   "+0.5 sc/ha", "#2e7d32"),
                ("Legacy + Intensive management",         "−1.0 sc/ha", "#c62828"),
            ],
        },
        {
            "titulo": "Interaction 2 — Drainage × Rainfall (C4 × Climate)",
            "cor": "#1565c0",
            "desc": "Poor drainage doesn't penalize in dry years — it can even help by retaining moisture. The problem appears in wet years, when waterlogging causes root asphyxiation.",
            "linhas": [
                ("Poor drainage + Wet year",      "−4.0 sc/ha", "#c62828"),
                ("Poor drainage + Normal year",   "−1.5 sc/ha", "#f57c00"),
                ("Poor drainage + Dry year",      "+4.0 sc/ha", "#2e7d32"),
                ("Moderate drainage + Wet",       "−1.5 sc/ha", "#f57c00"),
                ("Good drainage + Wet",           "+1.0 sc/ha", "#2e7d32"),
            ],
        },
        {
            "titulo": "Interaction 3 — Planting Window × ENSO (D1 × C7)",
            "cor": "#b35c00",
            "desc": "Late planting in a La Niña year is the riskiest combination: grain filling falls during peak dry spells. In El Niño, planting late has fewer consequences.",
            "linhas": [
                ("Late + La Niña",    "−2.5 sc/ha", "#c62828"),
                ("Late + El Niño",    "+1.0 sc/ha", "#2e7d32"),
                ("Optimal + El Niño", "+1.0 sc/ha", "#2e7d32"),
                ("Early + La Niña",   "−1.0 sc/ha", "#f57c00"),
            ],
        },
    ]

    for inter in inter_data:
        with st.expander(inter["titulo"], expanded=True):
            c_desc, c_vals = st.columns([2, 1], gap="large")
            with c_desc:
                st.markdown(f'<p style="font-size:0.84rem;color:#3a3a5c;line-height:1.6">{inter["desc"]}</p>', unsafe_allow_html=True)
            with c_vals:
                for combo, val, cor in inter["linhas"]:
                    st.markdown(f"""
                    <div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid #f0f0f0;font-size:0.78rem">
                        <span style="color:#3a3a5c">{combo}</span>
                        <span style="color:{cor};font-weight:700">{val}</span>
                    </div>
                    """, unsafe_allow_html=True)


def _render_step_7(result: dict | None) -> None:
    _step_header(7, "Payoff Matrix",
        "Each path × climate combination produces an expected yield value")

    if not result:
        st.info("Run a simulation to see your payoff matrix here.")
        _formula_box("Payoff[path i, climate j] = effective_base + D1ᵢ + D4ᵢ + D5ᵢ + rainⱼ + interactions")
        return

    paths  = result["paths"]
    matrix = result["matrix"]
    states = result["rain_states"]
    ev_vals = result["criteria"]["bayes_ev"]["criterion_values"]
    opt_idx = result["criteria"]["bayes_ev"]["path_idx"]

    _formula_box("Payoff[path i, climate j] = effective_base + D1ᵢ + D4ᵢ + D5ᵢ + rainⱼ + interactions")
    st.markdown("<br>", unsafe_allow_html=True)

    d1_s = {"Precoce (até 15/out)": "Early", "Ótima (16/out – 10/nov)": "Optimal", "Tardia (após 10/nov)": "Late"}
    d4_s = {"Baixa (≤280k sementes/ha)": "Low", "Média (280k–340k)": "Medium", "Alta (>340k)": "High"}
    d5_s = {"Alto (≥3 fung. + monitor ferrugem)": "Intensive", "Padrão (2 aplicações)": "Standard", "Baixo (1 ou nenhuma)": "Reduced"}
    rain_s = [s.split(" ")[0] for s in states]

    rows = []
    for i, path in enumerate(paths):
        row = {
            "#": i + 1,
            "Window": d1_s.get(path["d1"], path["d1"]),
            "Density": d4_s.get(path["d4"], path["d4"]),
            "Management": d5_s.get(path["d5"], path["d5"]),
        }
        for j, rs in enumerate(rain_s):
            row[rs] = matrix[i][j]
        row["Exp. Yield"] = round(ev_vals[i], 1)
        rows.append(row)

    df = pd.DataFrame(rows).set_index("#")

    def _hl(row):
        if row.name == opt_idx + 1:
            return ["background-color:#e8f5e9;font-weight:bold"] * len(row)
        return [""] * len(row)

    baseline = result["baseline"]
    styled = (
        df.style
        .apply(_hl, axis=1)
        .format({rs: "{:.1f}" for rs in rain_s} | {"Exp. Yield": "{:.1f}"})
        .background_gradient(subset=["Exp. Yield"], cmap="YlGn")
    )
    st.dataframe(styled, use_container_width=True, height=500)
    st.caption(f"★ green row = best path (Exp. Yield = {ev_vals[opt_idx]:.1f} sc/ha) · Reference: {baseline} sc/ha")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Best possible outcome", f"{max(max(r) for r in matrix):.1f} sc/ha")
    with c2:
        st.metric("Worst possible outcome", f"{min(min(r) for r in matrix):.1f} sc/ha")
    with c3:
        st.metric("Total range", f"{max(max(r) for r in matrix) - min(min(r) for r in matrix):.1f} sc/ha")


def _render_step_8(result: dict | None) -> None:
    _step_header(8, "Decision Criteria",
        "6 different perspectives for choosing the best path in the matrix")

    criterios = [
        ("bayes_ev", "Best expected outcome",
         "Weights each outcome by its climate probability. The primary criterion — maximizes expected value.",
         "#1a5c38", "⭐ Primary"),
        ("wald", "Safest in worst case",
         "Selects the path guaranteeing the highest outcome even in the worst possible climate. Conservative profile.",
         "#1565c0", "🛡️ Conservative"),
        ("maximax", "Maximum yield potential",
         "Selects the path with the highest possible outcome, ignoring risk. Optimistic profile.",
         "#b35c00", "🚀 Optimistic"),
        ("laplace", "Average across all scenarios",
         "Treats all climates as equally likely. An unbiased reference.",
         "#6b6b8a", "⚖️ Neutral"),
        ("hurwicz", "Risk/opportunity balance",
         "Weights 50% best case + 50% worst case. Compromise between optimism and caution.",
         "#7b1fa2", "🎯 Balanced"),
        ("savage", "Minimum regret",
         "Minimizes how much the producer would lose by not having chosen the optimal strategy for each climate.",
         "#c62828", "😌 No regret"),
    ]

    c_left, c_right = st.columns(2, gap="large")
    cols = [c_left, c_right]

    for i, (key, nome, desc, cor, badge) in enumerate(criterios):
        with cols[i % 2]:
            winner_idx = None
            winner_val = None
            if result:
                crit = result["criteria"].get(key, {})
                winner_idx = crit.get("path_idx")
                winner_val = crit.get("value")
                paths = result["paths"]
                if winner_idx is not None:
                    p = paths[winner_idx]
                    d1_s = {"Precoce (até 15/out)": "Early", "Ótima (16/out – 10/nov)": "Optimal", "Tardia (após 10/nov)": "Late"}
                    d5_s = {"Alto (≥3 fung. + monitor ferrugem)": "Intensive", "Padrão (2 aplicações)": "Standard", "Baixo (1 ou nenhuma)": "Reduced"}
                    winner_label = f"{d1_s.get(p['d1'], p['d1'])} · {d5_s.get(p['d5'], p['d5'])}"

            st.markdown(f"""
            <div style="background:#ffffff;border:1.5px solid #c4c4d4;border-left:4px solid {cor};
                        border-radius:8px;padding:14px 16px;margin-bottom:12px;
                        box-shadow:0 2px 6px rgba(0,0,0,0.08)">
                <div style="display:flex;justify-content:space-between;align-items:flex-start">
                    <span style="font-size:0.82rem;font-weight:700;color:#1a1a2e">{nome}</span>
                    <span style="font-size:0.65rem;background:{cor}22;color:{cor};border:1px solid {cor}66;
                                 padding:2px 8px;border-radius:20px;font-weight:700">{badge}</span>
                </div>
                <div style="font-size:0.75rem;color:#2a2a4a;margin-top:6px;line-height:1.5">{desc}</div>
                {f'<div style="margin-top:8px;padding-top:8px;border-top:1px solid #d4d4e4;font-size:0.78rem;color:{cor};font-weight:600">→ {winner_label} · {winner_val:.1f} sc/ha</div>' if result and winner_idx is not None else ""}
            </div>
            """, unsafe_allow_html=True)

    if result:
        opt_idx = result["criteria"]["bayes_ev"]["path_idx"]
        all_same = all(result["criteria"][k]["path_idx"] == opt_idx for k in ["bayes_ev", "wald", "laplace"])
        if all_same:
            st.success("✓ All primary criteria point to the same path — robust recommendation.")
        else:
            st.info("ℹ️ Different criteria point to different paths — the model uses Bayes EV as the primary criterion.")


def _render_step_9(result: dict | None) -> None:
    _step_header(9, "Risk Analysis",
        "10,000 simulations per path estimate the yield confidence interval")

    c_explain, c_result = st.columns([1, 1], gap="large")

    with c_explain:
        _info_card("How Monte Carlo works",
            "For each path, the model draws 10,000 scenarios where D2 (cultivar), "
            "D3 (seed treatment) and D6 (planter) vary randomly — because even with a "
            "choice made, the actual result can vary due to execution conditions, "
            "seed lot quality, field response, etc.")

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
        <div style="background:#ffffff;border:1.5px solid #c4c4d4;border-radius:10px;padding:16px;box-shadow:0 2px 8px rgba(0,0,0,0.08)">
            <div style="font-size:0.7rem;font-weight:700;color:#4a4a6a;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:10px">Stochastic variables</div>
        """, unsafe_allow_html=True)
        for var, dist in [
            ("D2 · Cultivar",        "Triangular(−8, 0, +6)"),
            ("D3 · Seed Treatment",  "Triangular(−5, 0, +3)"),
            ("D6 · Planter",         "Triangular(−4, 0, +3)"),
            ("Rainfall R3–R6",       "Discrete by P(rain|ENSO)"),
        ]:
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid #f0f0f0;font-size:0.78rem">
                <span style="color:#1a1a2e;font-weight:600">{var}</span>
                <span style="color:#1565c0;font-family:monospace">{dist}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c_result:
        if result:
            opt_idx = result["criteria"]["bayes_ev"]["path_idx"]
            mc = result["paths"][opt_idx].get("mc") or {}
            if mc:
                st.markdown("**Simulated distribution — best path:**")
                import numpy as np
                rng = np.random.default_rng(42)
                sim_yields = rng.normal(mc["mean"], mc["std"], 500)
                fig = go.Figure()
                fig.add_histogram(x=sim_yields, nbinsx=30, marker_color="#2d8a56",
                                  opacity=0.75, name="Simulations")
                fig.add_vline(x=mc["p5"],  line_dash="dot", line_color="#c62828",
                              annotation_text=f"P5: {mc['p5']:.0f}", annotation_position="top left")
                fig.add_vline(x=mc["p95"], line_dash="dot", line_color="#1565c0",
                              annotation_text=f"P95: {mc['p95']:.0f}", annotation_position="top right")
                fig.add_vline(x=mc["mean"], line_dash="solid", line_color="#1a5c38",
                              annotation_text=f"Mean: {mc['mean']:.0f}", annotation_position="top right")
                fig.update_layout(height=280, margin=dict(l=20, r=20, t=30, b=30),
                                  plot_bgcolor="white", paper_bgcolor="white", showlegend=False,
                                  xaxis_title="sc/ha", yaxis_title="Frequency",
                                  xaxis=dict(gridcolor="#d8d8e8", tickfont=dict(color="#1a1a2e", size=11),
                                             title_font=dict(color="#1a1a2e")),
                                  yaxis=dict(gridcolor="#d8d8e8", tickfont=dict(color="#1a1a2e", size=11),
                                             title_font=dict(color="#1a1a2e")),
                                  font=dict(color="#1a1a2e", size=11))
                st.plotly_chart(fig, use_container_width=True)

                c_p5, c_mean, c_p95 = st.columns(3)
                with c_p5:
                    st.metric("P5 (worst 5%)", f"{mc['p5']:.0f} sc/ha")
                with c_mean:
                    st.metric("Mean", f"{mc['mean']:.0f} sc/ha")
                with c_p95:
                    st.metric("P95 (best 5%)", f"{mc['p95']:.0f} sc/ha")

                risk = mc.get("p_below", 0)
                risk_color = "🔴" if risk > 0.25 else "🟡" if risk > 0.10 else "🟢"
                st.markdown(f"""
                <div style="background:#f8f9fa;border-radius:8px;padding:12px 16px;margin-top:8px;font-size:0.84rem">
                    {risk_color} <strong>{risk:.0%} chance</strong> of falling below the 60 sc/ha reference
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Run a simulation to see the Monte Carlo distribution here.")
            _info_card("What the results show",
                "P5 = in 95% of simulations, yield exceeded this value\n"
                "P95 = in 95% of simulations, yield stayed below this value\n"
                "The P5–P95 range is the 90% confidence interval.")


def _render_step_10(result: dict | None) -> None:
    _step_header(10, "Final Recommendation",
        "The model combines all previous steps to identify the strategy with the highest expected return")

    _formula_box(
        "Recommendation = argmax<sub>i</sub> Σⱼ [ Payoff(i,j) + Interactions(i,j) ] × P(rainⱼ | ENSO)"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("**Complete pipeline — from field to recommendation:**")

    pipeline = [
        ("60 sc/ha",         "CONAB Baseline",                    "#e8f5e9", "#1a5c38"),
        ("+ Context",        "C1–C7 · soil, region, climate",     "#e3f2fd", "#1565c0"),
        ("+ Fixed decisions","D2 · D3 · D6",                      "#fff8e1", "#b35c00"),
        ("× 27 paths",       "D1 × D4 × D5",                      "#f3e5f5", "#7b1fa2"),
        ("× 3 climates",     "Dry · Normal · Wet by ENSO",         "#e0f2f1", "#00695c"),
        ("+ Interactions",   "3 amplification terms",              "#fce4ec", "#c62828"),
        ("→ 27×3 Matrix",    "81 possible outcomes",               "#fff3e0", "#e65100"),
        ("→ Bayes EV",       "Probability-weighted scoring",        "#e8f5e9", "#1a5c38"),
        ("→ Monte Carlo",    "10,000 sim. · P5/P95",               "#e3f2fd", "#1565c0"),
        ("🎯 Recommendation","Best strategy for your field",        "#1a5c38", "#ffffff"),
    ]

    cols_pipe = st.columns(5)
    for idx, (val, label, bg, fg) in enumerate(pipeline):
        with cols_pipe[idx % 5]:
            st.markdown(f"""
            <div style="background:{bg};border-radius:8px;padding:12px 10px;text-align:center;
                        margin-bottom:8px;min-height:72px;display:flex;flex-direction:column;
                        align-items:center;justify-content:center">
                <div style="font-size:0.82rem;font-weight:800;color:{fg};line-height:1.2">{val}</div>
                <div style="font-size:0.65rem;color:{'#ffffff99' if bg=='#1a5c38' else '#6b6b8a'};margin-top:4px">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    if result:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Your simulation result:**")

        opt_idx  = result["criteria"]["bayes_ev"]["path_idx"]
        opt_path = result["paths"][opt_idx]
        opt_ev   = result["criteria"]["bayes_ev"]["value"]
        baseline = result["baseline"]
        mc       = opt_path.get("mc") or {}

        d1_s = {"Precoce (até 15/out)": "Early", "Ótima (16/out – 10/nov)": "Optimal", "Tardia (após 10/nov)": "Late"}
        d4_s = {"Baixa (≤280k sementes/ha)": "Low", "Média (280k–340k)": "Medium", "Alta (>340k)": "High"}
        d5_s = {"Alto (≥3 fung. + monitor ferrugem)": "Intensive", "Padrão (2 aplicações)": "Standard", "Baixo (1 ou nenhuma)": "Reduced"}

        delta = opt_ev - baseline
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#0d2b18,#1a5c38);border-radius:12px;
                    padding:28px 32px;color:#fff;margin-top:8px">
            <div style="font-size:0.7rem;font-weight:700;color:#76c442;text-transform:uppercase;
                        letter-spacing:0.12em;margin-bottom:10px">🎯 Primary Recommendation</div>
            <div style="display:flex;gap:40px;flex-wrap:wrap">
                <div>
                    <div style="font-size:0.7rem;color:rgba(255,255,255,0.6)">Planting Window</div>
                    <div style="font-size:1rem;font-weight:700">{d1_s.get(opt_path["d1"], opt_path["d1"])}</div>
                </div>
                <div>
                    <div style="font-size:0.7rem;color:rgba(255,255,255,0.6)">Density</div>
                    <div style="font-size:1rem;font-weight:700">{d4_s.get(opt_path["d4"], opt_path["d4"])}</div>
                </div>
                <div>
                    <div style="font-size:0.7rem;color:rgba(255,255,255,0.6)">Disease Management</div>
                    <div style="font-size:1rem;font-weight:700">{d5_s.get(opt_path["d5"], opt_path["d5"])}</div>
                </div>
                <div>
                    <div style="font-size:0.7rem;color:rgba(255,255,255,0.6)">Expected Yield</div>
                    <div style="font-size:1.6rem;font-weight:900;color:#76c442">{opt_ev:.1f} sc/ha</div>
                    <div style="font-size:0.75rem;color:rgba(255,255,255,0.7)">{delta:+.1f} sc/ha vs. reference</div>
                </div>
                {f'<div><div style="font-size:0.7rem;color:rgba(255,255,255,0.6)">90% Interval</div><div style="font-size:0.92rem;font-weight:600">{mc["p5"]:.0f} – {mc["p95"]:.0f} sc/ha</div></div>' if mc else ""}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("View full results →", type="primary"):
            nav_go("results")
    else:
        st.info("Run a simulation to see the final recommendation here.")
        if st.button("Go to New Simulation →", type="primary"):
            nav_go("input")


# ── Explainer-specific CSS ────────────────────────────────────────────────────

_EXPLAINER_CSS = """
<style>
.exp-progress-wrap { margin: 0 0 24px 0; }
.exp-step-row { display:flex; align-items:center; margin-bottom:8px; }
.exp-step-dot {
  width:28px; height:28px; border-radius:50%;
  display:inline-flex; align-items:center; justify-content:center;
  font-size:0.68rem; font-weight:800; flex-shrink:0;
}
.exp-step-done  { background:#2d8a56; color:#fff; }
.exp-step-active{ background:#0d2b18; color:#76c442; border:2px solid #76c442; }
.exp-step-todo  { background:#9090aa; color:#ffffff; }
.exp-step-line  { flex:1; height:2px; margin:0 2px; }
.exp-step-line-done { background:#2d8a56; }
.exp-step-line-todo { background:#aaaabc; }
.exp-progress-bar-bg  { background:#b0b0c4; border-radius:4px; height:4px; }
.exp-progress-bar-fill{ background:linear-gradient(90deg,#1a5c38,#76c442); border-radius:4px; height:4px; transition:width 0.4s ease; }

.exp-step-header { margin-bottom:24px; }
.exp-step-number { font-size:0.65rem; font-weight:700; color:#5a5a7a; text-transform:uppercase; letter-spacing:0.15em; }
.exp-step-title  { font-size:1.5rem; font-weight:800; color:#1a1a2e; margin:4px 0 6px 0; letter-spacing:-0.02em; }
.exp-step-desc   { font-size:0.84rem; color:#3a3a5c; line-height:1.5; }

.exp-formula {
  background:#ffffff; border:1.5px solid #c0c0d0; border-left:4px solid #1a5c38;
  border-radius:0 8px 8px 0; padding:12px 18px; margin:8px 0;
  font-family:monospace; font-size:0.85rem; color:#1a1a2e;
  box-shadow: 0 1px 4px rgba(0,0,0,0.07);
}
.exp-formula-label { font-size:0.65rem; font-weight:700; color:#5a5a7a; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:4px; font-family:sans-serif; }

.exp-info-card {
  background:#ffffff; border:1.5px solid #c4c4d4; border-left:4px solid #1a5c38;
  border-radius:0 8px 8px 0; padding:12px 16px; margin:4px 0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.exp-info-title { font-size:0.78rem; font-weight:700; color:#1a1a2e; margin-bottom:4px; }
.exp-info-body  { font-size:0.78rem; color:#2a2a4a; line-height:1.55; white-space:pre-line; }
</style>
"""


# ── Main render ───────────────────────────────────────────────────────────────

def render() -> None:
    st.markdown(_EXPLAINER_CSS, unsafe_allow_html=True)

    result = st.session_state.get("sim_result")

    st.markdown('<div class="page-title">How We Calculate</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Understand each step of the model — from baseline to final recommendation</div>',
        unsafe_allow_html=True,
    )

    if result:
        st.caption("✓ Using data from your last simulation")
    else:
        st.caption("ℹ️ Run a simulation to see your real data at each step")

    st.markdown("<br>", unsafe_allow_html=True)

    current = _step_key()
    _progress_bar(current)
    st.markdown("---")

    step_map = {
        1:  lambda: _render_step_1(),
        2:  lambda: _render_step_2(result),
        3:  lambda: _render_step_3(result),
        4:  lambda: _render_step_4(result),
        5:  lambda: _render_step_5(result),
        6:  lambda: _render_step_6(),
        7:  lambda: _render_step_7(result),
        8:  lambda: _render_step_8(result),
        9:  lambda: _render_step_9(result),
        10: lambda: _render_step_10(result),
    }
    step_map[current]()

    st.markdown("---")
    _nav_buttons(current)
