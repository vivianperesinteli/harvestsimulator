"""Explainer Panel — How the simulator reaches its recommendations."""

from __future__ import annotations
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from frontend.navigation import go as nav_go
from frontend.i18n import t

# ── Step definitions ──────────────────────────────────────────────────────────
# Step titles/descs are now pulled from i18n at render time
_N = 10

# ── Helpers ───────────────────────────────────────────────────────────────────

def _step_key() -> int:
    if "explainer_step" not in st.session_state:
        st.session_state.explainer_step = 1
    return st.session_state.explainer_step


def _get_steps(lang: str) -> list[tuple[int, str, str]]:
    return [
        (i, t(f"expl_step{i}_title", lang), t(f"expl_step{i}_desc", lang))
        for i in range(1, _N + 1)
    ]


def _progress_bar(current: int, lang: str) -> None:
    pct = int((current / _N) * 100)
    steps = _get_steps(lang)
    steps_html = ""
    for num, title, _ in steps:
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


def _nav_buttons(current: int, lang: str) -> None:
    c_back, c_info, c_next = st.columns([1, 4, 1])
    with c_back:
        if current > 1:
            if st.button(t("expl_prev_btn", lang), use_container_width=True):
                st.session_state.explainer_step -= 1
                st.rerun()
    with c_info:
        st.markdown(
            f'<div style="text-align:center;font-size:0.78rem;color:#6b6b8a;padding-top:8px">'
            f'{t("expl_step_of", lang, current=current, total=_N)}</div>',
            unsafe_allow_html=True,
        )
    with c_next:
        if current < _N:
            if st.button(t("expl_next_btn", lang), type="primary", use_container_width=True):
                st.session_state.explainer_step += 1
                st.rerun()
        else:
            if st.button(t("expl_restart_btn", lang), use_container_width=True):
                st.session_state.explainer_step = 1
                st.rerun()


def _step_header(num: int, lang: str) -> None:
    title = t(f"expl_step{num}_title", lang)
    desc  = t(f"expl_step{num}_desc", lang)
    st.markdown(f"""
    <div class="exp-step-header">
        <div class="exp-step-number">{t("expl_step_label", lang)} {num}</div>
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

def _render_step_1(lang: str) -> None:
    _step_header(1, lang)

    c1, c2 = st.columns([1, 2], gap="large")
    with c1:
        st.markdown(f"""
        <div style="text-align:center;padding:40px 20px;background:#fff;border-radius:12px;border:1px solid #e4e4f0;box-shadow:0 2px 8px rgba(0,0,0,0.06)">
            <div style="font-size:0.7rem;font-weight:700;color:#6b6b8a;text-transform:uppercase;letter-spacing:0.1em">{t("expl_s1_baseline_label", lang)}</div>
            <div style="font-size:5rem;font-weight:900;color:#1a5c38;line-height:1">60</div>
            <div style="font-size:1rem;color:#3a3a5c;font-weight:600">sc/ha</div>
            <div style="font-size:0.72rem;color:#6b6b8a;margin-top:8px">{t("expl_s1_source", lang)}</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        _info_card(t("expl_s1_why_title", lang), t("expl_s1_why_body", lang))
        st.markdown("<br>", unsafe_allow_html=True)
        _formula_box(t("expl_s1_formula", lang), label=t("expl_s1_formula_label", lang))
        st.markdown("<br>", unsafe_allow_html=True)
        _info_card(t("expl_s1_adj_title", lang), t("expl_s1_adj_body", lang), color="#1565c0")


def _render_step_2(result: dict | None, lang: str) -> None:
    _step_header(2, lang)

    col_table, col_chart = st.columns([1, 1], gap="large")

    with col_table:
        st.markdown(f"**{t('expl_s2_table_title', lang)}**")
        labels = [
            ("C1", t("expl_s2_c1", lang),  "Favorável (Sorriso, Sinop...)", "+5", "Desafiador (Primavera, Querência)", "−6"),
            ("C2", t("expl_s2_c2", lang),  "Argila / bem estruturado",       "+5", "Arenoso / baixa retenção",          "−7"),
            ("C3", t("expl_s2_c3", lang),  "Adequado 5.5–6.5",               "+4", "Crítico <5.0 ou >6.8",              "−6"),
            ("C4", t("expl_s2_c4", lang),  "Sem encharcamento",              "+3", "Alagamento frequente",              "−8"),
            ("C5", t("expl_s2_c5", lang),  "Latossolo / Nitossolo",          "+5", "Neossolo / Gleissolo",              "−7"),
            ("C6", t("expl_s2_c6", lang),  "Acima de 200 ha",                "+2", "Até 50 ha",                         "−1"),
            ("C7", t("expl_s2_c7", lang),  "El Niño",                        "+3", "La Niña",                           "−3"),
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
        st.markdown(f"**{t('expl_s2_chart_title', lang)}**")
        nomes = [
            t("expl_s2_c1", lang), t("expl_s2_c2", lang), t("expl_s2_c3", lang),
            t("expl_s2_c4", lang), t("expl_s2_c5", lang), t("expl_s2_c6", lang),
            "ENSO",
        ]
        positivos = [5, 5, 4, 3, 5, 2, 3]
        negativos = [-6, -7, -6, -8, -7, -1, -3]

        fig = go.Figure()
        fig.add_bar(x=positivos, y=nomes, orientation="h",
                    marker_color="#2d8a56", name=t("expl_s2_max_gain", lang),
                    text=[f"+{v}" for v in positivos], textposition="outside")
        fig.add_bar(x=negativos, y=nomes, orientation="h",
                    marker_color="#c62828", name=t("expl_s2_max_penalty", lang),
                    text=[str(v) for v in negativos], textposition="outside")
        fig.update_layout(
            barmode="overlay", height=280, margin=dict(l=80, r=60, t=10, b=30),
            showlegend=True, plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(gridcolor="#d8d8e8", zeroline=True, zerolinecolor="#666",
                       tickfont=dict(color="#1a1a2e", size=11)),
            yaxis=dict(tickfont=dict(color="#1a1a2e", size=11)),
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
                <span style="font-size:0.75rem;color:#1a5c38;font-weight:700">{t("expl_s2_your_result", lang)}</span><br>
                <span style="font-size:1.4rem;font-weight:800;color:{color}">{sign}{ctx_adj:.1f} sc/ha</span>
                <span style="font-size:0.8rem;color:#3a3a5c"> {t("expl_s2_ctx_adj", lang)}</span><br>
                <span style="font-size:0.8rem;color:#1a5c38">{t("expl_s2_adj_base", lang)}: {result['context_base']:.0f} sc/ha</span>
            </div>
            """, unsafe_allow_html=True)


def _render_step_3(result: dict | None, lang: str) -> None:
    _step_header(3, lang)

    _formula_box(t("expl_s3_formula", lang))
    st.markdown("<br>", unsafe_allow_html=True)

    c_fixed, c_var = st.columns(2, gap="large")

    with c_fixed:
        st.markdown(f"""
        <div style="background:#fff8e1;border:1px solid #ffe082;border-radius:10px;padding:20px">
            <div style="font-size:0.7rem;font-weight:700;color:#b35c00;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:12px">
                🔒 {t("expl_s3_fixed_hdr", lang)}
            </div>
        """, unsafe_allow_html=True)
        for cod, nome_key, desc_key, faixa in [
            ("D2", "expl_s3_d2_name", "expl_s3_d2_desc", "−8 to +6 sc/ha"),
            ("D3", "expl_s3_d3_name", "expl_s3_d3_desc", "−5 to +3 sc/ha"),
            ("D6", "expl_s3_d6_name", "expl_s3_d6_desc", "−4 to +3 sc/ha"),
        ]:
            nome = t(nome_key, lang)
            desc = t(desc_key, lang)
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
                {t("expl_s3_fixed_adj", lang)}: {result['fixed_adj']:+.1f} sc/ha
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c_var:
        st.markdown(f"""
        <div style="background:#e8f5e9;border:1px solid #a5d6a7;border-radius:10px;padding:20px">
            <div style="font-size:0.7rem;font-weight:700;color:#1a5c38;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:12px">
                🔀 {t("expl_s3_var_hdr", lang)}
            </div>
        """, unsafe_allow_html=True)
        for cod, nome_key, desc_key, faixa, opts_key in [
            ("D1", "expl_s3_d1_name", "expl_s3_d1_desc", "−8 to +4 sc/ha", "expl_s3_3opts"),
            ("D4", "expl_s3_d4_name", "expl_s3_d4_desc", "−1 to +2 sc/ha", "expl_s3_3opts"),
            ("D5", "expl_s3_d5_name", "expl_s3_d5_desc", "−7 to +5 sc/ha", "expl_s3_3opts"),
        ]:
            nome = t(nome_key, lang)
            desc = t(desc_key, lang)
            opts = t(opts_key, lang)
            st.markdown(f"""
            <div style="padding:8px 0;border-bottom:1px solid #a5d6a7">
                <span style="font-weight:700;color:#1a1a2e">{cod} · {nome}</span><br>
                <span style="font-size:0.78rem;color:#3a3a5c">{desc}</span><br>
                <span style="font-size:0.72rem;color:#1a5c38;font-weight:600">{faixa} · {opts}</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown(f"""
        <div style="margin-top:10px;font-size:0.8rem;color:#1a5c38;font-weight:700">
            {t("expl_s3_combo_note", lang)}
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    _info_card(t("expl_s3_why_title", lang), t("expl_s3_why_body", lang), color="#1565c0")


def _render_step_4(result: dict | None, lang: str) -> None:
    _step_header(4, lang)

    c_tree, c_explain = st.columns([3, 2], gap="large")

    with c_tree:
        st.markdown(f"**{t('expl_s4_combo_title', lang)}**")

        # Labels for EN/PT depend on lang
        d1_opts = [t("expl_early", lang), t("expl_optimal", lang), t("expl_late", lang)]
        d4_opts = [t("expl_low", lang),   t("expl_medium", lang),  t("expl_high", lang)]
        d5_opts = [t("expl_intensive", lang), t("expl_standard", lang), t("expl_reduced", lang)]

        rows = []
        for i, d1 in enumerate(d1_opts):
            for j, d4 in enumerate(d4_opts):
                for k, d5 in enumerate(d5_opts):
                    path_num = i * 9 + j * 3 + k + 1
                    rows.append({"#": path_num,
                                 t("expl_s4_col_d1", lang): d1,
                                 t("expl_s4_col_d4", lang): d4,
                                 t("expl_s4_col_d5", lang): d5})

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
            st.caption(t("expl_s4_best_row", lang, row=highlight_idx))

    with c_explain:
        _info_card(t("expl_s4_what_title", lang), t("expl_s4_what_body", lang))
        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
        <div style="background:#ffffff;border:1.5px solid #c4c4d4;border-radius:10px;padding:16px;box-shadow:0 2px 8px rgba(0,0,0,0.08)">
            <div style="font-size:0.7rem;font-weight:700;color:#4a4a6a;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:10px">""" +
            t("expl_s4_logic_title", lang) +
            """</div>""", unsafe_allow_html=True)
        for num_val, label_key, sub_key in [
            ("3",  "expl_s4_window_opts", "expl_s4_window_sub"),
            ("×",  "",                    ""),
            ("3",  "expl_s4_density_opts","expl_s4_density_sub"),
            ("×",  "",                    ""),
            ("3",  "expl_s4_mgmt_opts",   "expl_s4_mgmt_sub"),
            ("=",  "",                    ""),
            ("27", "expl_s4_paths",       "expl_s4_paths_sub"),
        ]:
            if num_val in ("×", "="):
                st.markdown(f'<div style="text-align:center;font-size:1.4rem;color:#1a5c38;font-weight:700;line-height:1.2">{num_val}</div>', unsafe_allow_html=True)
            else:
                label = t(label_key, lang)
                sub   = t(sub_key, lang)
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:10px;padding:6px 0;border-bottom:1px solid #f0f0f0">
                    <div style="font-size:1.6rem;font-weight:800;color:#1a5c38;min-width:36px;text-align:right">{num_val}</div>
                    <div>
                        <div style="font-size:0.82rem;font-weight:600;color:#1a1a2e">{label}</div>
                        <div style="font-size:0.7rem;color:#6b6b8a">{sub}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)


def _render_step_5(result: dict | None, lang: str) -> None:
    _step_header(5, lang)

    from backend.data import RAIN_STATES, RAIN_PROBS

    c_prob, c_explain = st.columns([3, 2], gap="large")

    with c_prob:
        st.markdown(f"**{t('expl_s5_prob_title', lang)}**")
        enso_labels = {
            "El Niño (chuva regular em MT)":    "El Niño",
            "Neutro":                            t("expl_s5_neutral", lang),
            "La Niña (chuva concentrada/curta)": "La Niña",
        }
        rain_labels = {
            "Seca (<150 mm)":      t("expl_s5_dry", lang),
            "Normal (150–250 mm)": t("expl_s5_normal", lang),
            "Úmida (>250 mm)":     t("expl_s5_wet", lang),
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
            st.caption(t("expl_s5_enso_caption", lang, enso=user_enso))

        st.markdown("<br>", unsafe_allow_html=True)
        fig = go.Figure()
        colors = {
            t("expl_s5_dry", lang):    "#c62828",
            t("expl_s5_normal", lang): "#f57c00",
            t("expl_s5_wet", lang):    "#1565c0",
        }
        for enso_key, enso_short in enso_labels.items():
            for rain_key, rain_short in rain_labels.items():
                prob = RAIN_PROBS[enso_key][rain_key]
                fig.add_bar(
                    x=[enso_short], y=[prob],
                    name=rain_short,
                    marker_color=colors.get(rain_short, "#999"),
                    showlegend=(enso_short == "El Niño"),
                    text=f"{prob:.0%}", textposition="inside",
                )
        fig.update_layout(
            barmode="stack", height=220,
            margin=dict(l=20, r=20, t=10, b=30),
            plot_bgcolor="white", paper_bgcolor="white",
            legend=dict(orientation="h", y=-0.2, font=dict(color="#1a1a2e", size=11)),
            yaxis=dict(tickformat=".0%", gridcolor="#d8d8e8",
                       tickfont=dict(color="#1a1a2e", size=11)),
            xaxis=dict(tickfont=dict(color="#1a1a2e", size=11)),
            font=dict(color="#1a1a2e", size=11),
        )
        st.plotly_chart(fig, use_container_width=True)

    with c_explain:
        _info_card(t("expl_s5_why_enso_title", lang), t("expl_s5_why_enso_body", lang))
        st.markdown("<br>", unsafe_allow_html=True)
        _info_card(t("expl_s5_adj_title", lang), t("expl_s5_adj_body", lang), color="#1565c0")
        st.markdown("<br>", unsafe_allow_html=True)
        _info_card(t("expl_s5_result_title", lang), t("expl_s5_result_body", lang), color="#b35c00")


def _render_step_6(lang: str) -> None:
    _step_header(6, lang)

    st.markdown(f"""
    <div style="background:#fff3e0;border-left:4px solid #f57c00;padding:12px 16px;border-radius:0 8px 8px 0;margin-bottom:20px;font-size:0.85rem;color:#3a3a5c">
        <strong>{t("expl_s6_what_title", lang)}</strong> {t("expl_s6_what_body", lang)}
    </div>
    """, unsafe_allow_html=True)

    inter_data = [
        {
            "titulo": t("expl_s6_inter1_title", lang),
            "cor": "#1a5c38",
            "desc": t("expl_s6_inter1_desc", lang),
            "linhas": [
                (t("expl_s6_i1_r1", lang), "+2.0 sc/ha", "#2e7d32"),
                (t("expl_s6_i1_r2", lang), "−2.0 sc/ha", "#c62828"),
                (t("expl_s6_i1_r3", lang), "+0.5 sc/ha", "#2e7d32"),
                (t("expl_s6_i1_r4", lang), "−1.0 sc/ha", "#c62828"),
            ],
        },
        {
            "titulo": t("expl_s6_inter2_title", lang),
            "cor": "#1565c0",
            "desc": t("expl_s6_inter2_desc", lang),
            "linhas": [
                (t("expl_s6_i2_r1", lang), "−4.0 sc/ha", "#c62828"),
                (t("expl_s6_i2_r2", lang), "−1.5 sc/ha", "#f57c00"),
                (t("expl_s6_i2_r3", lang), "+4.0 sc/ha", "#2e7d32"),
                (t("expl_s6_i2_r4", lang), "−1.5 sc/ha", "#f57c00"),
                (t("expl_s6_i2_r5", lang), "+1.0 sc/ha", "#2e7d32"),
            ],
        },
        {
            "titulo": t("expl_s6_inter3_title", lang),
            "cor": "#b35c00",
            "desc": t("expl_s6_inter3_desc", lang),
            "linhas": [
                (t("expl_s6_i3_r1", lang), "−2.5 sc/ha", "#c62828"),
                (t("expl_s6_i3_r2", lang), "+1.0 sc/ha", "#2e7d32"),
                (t("expl_s6_i3_r3", lang), "+1.0 sc/ha", "#2e7d32"),
                (t("expl_s6_i3_r4", lang), "−1.0 sc/ha", "#f57c00"),
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


def _render_step_7(result: dict | None, lang: str) -> None:
    _step_header(7, lang)

    if not result:
        st.info(t("expl_s7_no_sim", lang))
        _formula_box("Payoff[path i, climate j] = effective_base + D1ᵢ + D4ᵢ + D5ᵢ + rainⱼ + interactions")
        return

    paths  = result["paths"]
    matrix = result["matrix"]
    states = result["rain_states"]
    ev_vals = result["criteria"]["bayes_ev"]["criterion_values"]
    opt_idx = result["criteria"]["bayes_ev"]["path_idx"]

    _formula_box("Payoff[path i, climate j] = effective_base + D1ᵢ + D4ᵢ + D5ᵢ + rainⱼ + interactions")
    st.markdown("<br>", unsafe_allow_html=True)

    d1_s = {"Precoce (até 15/out)": t("expl_early", lang), "Ótima (16/out – 10/nov)": t("expl_optimal", lang), "Tardia (após 10/nov)": t("expl_late", lang)}
    d4_s = {"Baixa (≤280k sementes/ha)": t("expl_low", lang), "Média (280k–340k)": t("expl_medium", lang), "Alta (>340k)": t("expl_high", lang)}
    d5_s = {"Alto (≥3 fung. + monitor ferrugem)": t("expl_intensive", lang), "Padrão (2 aplicações)": t("expl_standard", lang), "Baixo (1 ou nenhuma)": t("expl_reduced", lang)}
    rain_s = [s.split(" ")[0] for s in states]

    rows = []
    for i, path in enumerate(paths):
        row = {
            "#": i + 1,
            t("expl_s4_col_d1", lang): d1_s.get(path["d1"], path["d1"]),
            t("expl_s4_col_d4", lang): d4_s.get(path["d4"], path["d4"]),
            t("expl_s4_col_d5", lang): d5_s.get(path["d5"], path["d5"]),
        }
        for j, rs in enumerate(rain_s):
            row[rs] = matrix[i][j]
        row[t("expl_s7_ev_col", lang)] = round(ev_vals[i], 1)
        rows.append(row)

    df = pd.DataFrame(rows).set_index("#")

    def _hl(row):
        if row.name == opt_idx + 1:
            return ["background-color:#e8f5e9;font-weight:bold"] * len(row)
        return [""] * len(row)

    baseline = result["baseline"]
    ev_col   = t("expl_s7_ev_col", lang)
    styled = (
        df.style
        .apply(_hl, axis=1)
        .format({rs: "{:.1f}" for rs in rain_s} | {ev_col: "{:.1f}"})
        .background_gradient(subset=[ev_col], cmap="YlGn")
    )
    st.dataframe(styled, use_container_width=True, height=500)
    st.caption(t("expl_s7_caption", lang, ev=f"{ev_vals[opt_idx]:.1f}", baseline=baseline))

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(t("expl_s7_best_out", lang), f"{max(max(r) for r in matrix):.1f} sc/ha")
    with c2:
        st.metric(t("expl_s7_worst_out", lang), f"{min(min(r) for r in matrix):.1f} sc/ha")
    with c3:
        st.metric(t("expl_s7_range", lang), f"{max(max(r) for r in matrix) - min(min(r) for r in matrix):.1f} sc/ha")


def _render_step_8(result: dict | None, lang: str) -> None:
    _step_header(8, lang)

    criterios = [
        ("bayes_ev", t("expl_s8_bayes_name", lang),   t("expl_s8_bayes_desc", lang),   "#1a5c38", t("expl_s8_badge_primary", lang)),
        ("wald",     t("expl_s8_wald_name", lang),    t("expl_s8_wald_desc", lang),    "#1565c0", t("expl_s8_badge_conservative", lang)),
        ("maximax",  t("expl_s8_maximax_name", lang), t("expl_s8_maximax_desc", lang), "#b35c00", t("expl_s8_badge_optimistic", lang)),
        ("laplace",  t("expl_s8_laplace_name", lang), t("expl_s8_laplace_desc", lang), "#6b6b8a", t("expl_s8_badge_neutral", lang)),
        ("hurwicz",  t("expl_s8_hurwicz_name", lang), t("expl_s8_hurwicz_desc", lang), "#7b1fa2", t("expl_s8_badge_balanced", lang)),
        ("savage",   t("expl_s8_savage_name", lang),  t("expl_s8_savage_desc", lang),  "#c62828", t("expl_s8_badge_noregret", lang)),
    ]

    c_left, c_right = st.columns(2, gap="large")
    cols = [c_left, c_right]

    d1_s = {"Precoce (até 15/out)": t("expl_early", lang), "Ótima (16/out – 10/nov)": t("expl_optimal", lang), "Tardia (após 10/nov)": t("expl_late", lang)}
    d5_s = {"Alto (≥3 fung. + monitor ferrugem)": t("expl_intensive", lang), "Padrão (2 aplicações)": t("expl_standard", lang), "Baixo (1 ou nenhuma)": t("expl_reduced", lang)}

    for i, (key, nome, desc, cor, badge) in enumerate(criterios):
        with cols[i % 2]:
            winner_idx = None
            winner_val = None
            winner_label = ""
            if result:
                crit = result["criteria"].get(key, {})
                winner_idx = crit.get("path_idx")
                winner_val = crit.get("value")
                paths = result["paths"]
                if winner_idx is not None:
                    p = paths[winner_idx]
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
            st.success(t("expl_s8_all_agree", lang))
        else:
            st.info(t("expl_s8_differ", lang))


def _render_step_9(result: dict | None, lang: str) -> None:
    _step_header(9, lang)

    c_explain, c_result = st.columns([1, 1], gap="large")

    with c_explain:
        _info_card(t("expl_s9_how_title", lang), t("expl_s9_how_body", lang))
        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
        <div style="background:#ffffff;border:1.5px solid #c4c4d4;border-radius:10px;padding:16px;box-shadow:0 2px 8px rgba(0,0,0,0.08)">
            <div style="font-size:0.7rem;font-weight:700;color:#4a4a6a;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:10px">""" +
            t("expl_s9_stochastic", lang) +
            """</div>""", unsafe_allow_html=True)
        for var, dist in [
            (t("expl_s9_d2", lang),   "Triangular(−8, 0, +6)"),
            (t("expl_s9_d3", lang),   "Triangular(−5, 0, +3)"),
            (t("expl_s9_d6", lang),   "Triangular(−4, 0, +3)"),
            (t("expl_s9_rain", lang), "Discrete by P(rain|ENSO)"),
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
                st.markdown(f"**{t('expl_s9_dist_title', lang)}**")
                import numpy as np
                rng = np.random.default_rng(42)
                sim_yields = rng.normal(mc["mean"], mc["std"], 500)
                fig = go.Figure()
                fig.add_histogram(x=sim_yields, nbinsx=30, marker_color="#2d8a56",
                                  opacity=0.75, name=t("expl_s9_sim_label", lang))
                fig.add_vline(x=mc["p5"],  line_dash="dot", line_color="#c62828",
                              annotation_text=f"P5: {mc['p5']:.0f}", annotation_position="top left")
                fig.add_vline(x=mc["p95"], line_dash="dot", line_color="#1565c0",
                              annotation_text=f"P95: {mc['p95']:.0f}", annotation_position="top right")
                fig.add_vline(x=mc["mean"], line_dash="solid", line_color="#1a5c38",
                              annotation_text=f"{t('mc_stat_mean', lang)}: {mc['mean']:.0f}", annotation_position="top right")
                fig.update_layout(height=280, margin=dict(l=20, r=20, t=30, b=30),
                                  plot_bgcolor="white", paper_bgcolor="white", showlegend=False,
                                  xaxis_title="sc/ha", yaxis_title=t("mc_freq_axis", lang),
                                  xaxis=dict(gridcolor="#d8d8e8", tickfont=dict(color="#1a1a2e", size=11),
                                             title_font=dict(color="#1a1a2e")),
                                  yaxis=dict(gridcolor="#d8d8e8", tickfont=dict(color="#1a1a2e", size=11),
                                             title_font=dict(color="#1a1a2e")),
                                  font=dict(color="#1a1a2e", size=11))
                st.plotly_chart(fig, use_container_width=True)

                c_p5, c_mean, c_p95 = st.columns(3)
                with c_p5:
                    st.metric(t("mc_unit_worst", lang), f"{mc['p5']:.0f} sc/ha")
                with c_mean:
                    st.metric(t("mc_stat_mean", lang), f"{mc['mean']:.0f} sc/ha")
                with c_p95:
                    st.metric(t("mc_unit_best", lang), f"{mc['p95']:.0f} sc/ha")

                risk = mc.get("p_below", 0)
                risk_color = "🔴" if risk > 0.25 else "🟡" if risk > 0.10 else "🟢"
                st.markdown(f"""
                <div style="background:#f8f9fa;border-radius:8px;padding:12px 16px;margin-top:8px;font-size:0.84rem">
                    {risk_color} <strong>{risk:.0%} {t("expl_s9_risk_chance", lang)}</strong>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info(t("expl_s9_no_sim", lang))
            _info_card(t("expl_s9_results_title", lang), t("expl_s9_results_body", lang))


def _render_step_10(result: dict | None, lang: str) -> None:
    _step_header(10, lang)

    _formula_box(
        "Recommendation = argmax<sub>i</sub> Σⱼ [ Payoff(i,j) + Interactions(i,j) ] × P(rainⱼ | ENSO)"
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"**{t('expl_s10_pipeline_title', lang)}**")

    pipeline = [
        ("60 sc/ha",         t("expl_s10_p1", lang),  "#e8f5e9", "#1a5c38"),
        ("+ Context",        t("expl_s10_p2", lang),  "#e3f2fd", "#1565c0"),
        ("+ " + t("expl_s10_p3_label", lang), t("expl_s10_p3", lang), "#fff8e1", "#b35c00"),
        ("× 27 " + t("expl_s10_p4_label", lang), t("expl_s10_p4", lang), "#f3e5f5", "#7b1fa2"),
        ("× 3 " + t("expl_s10_p5_label", lang), t("expl_s10_p5", lang), "#e0f2f1", "#00695c"),
        ("+ " + t("expl_s10_p6_label", lang), t("expl_s10_p6", lang), "#fce4ec", "#c62828"),
        ("→ 27×3 " + t("expl_s10_p7_label", lang), t("expl_s10_p7", lang), "#fff3e0", "#e65100"),
        ("→ Bayes EV",       t("expl_s10_p8", lang),  "#e8f5e9", "#1a5c38"),
        ("→ Monte Carlo",    t("expl_s10_p9", lang),  "#e3f2fd", "#1565c0"),
        ("🎯 " + t("expl_s10_p10_label", lang), t("expl_s10_p10", lang), "#1a5c38", "#ffffff"),
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
        st.markdown(f"**{t('expl_s10_your_result', lang)}**")

        opt_idx  = result["criteria"]["bayes_ev"]["path_idx"]
        opt_path = result["paths"][opt_idx]
        opt_ev   = result["criteria"]["bayes_ev"]["value"]
        baseline = result["baseline"]
        mc       = opt_path.get("mc") or {}

        d1_s = {"Precoce (até 15/out)": t("expl_early", lang), "Ótima (16/out – 10/nov)": t("expl_optimal", lang), "Tardia (após 10/nov)": t("expl_late", lang)}
        d4_s = {"Baixa (≤280k sementes/ha)": t("expl_low", lang), "Média (280k–340k)": t("expl_medium", lang), "Alta (>340k)": t("expl_high", lang)}
        d5_s = {"Alto (≥3 fung. + monitor ferrugem)": t("expl_intensive", lang), "Padrão (2 aplicações)": t("expl_standard", lang), "Baixo (1 ou nenhuma)": t("expl_reduced", lang)}

        delta = opt_ev - baseline
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#0d2b18,#1a5c38);border-radius:12px;
                    padding:28px 32px;color:#fff;margin-top:8px">
            <div style="font-size:0.7rem;font-weight:700;color:#76c442;text-transform:uppercase;
                        letter-spacing:0.12em;margin-bottom:10px">🎯 {t("expl_s10_primary_rec", lang)}</div>
            <div style="display:flex;gap:40px;flex-wrap:wrap">
                <div>
                    <div style="font-size:0.7rem;color:rgba(255,255,255,0.6)">{t("expl_s10_window_label", lang)}</div>
                    <div style="font-size:1rem;font-weight:700">{d1_s.get(opt_path["d1"], opt_path["d1"])}</div>
                </div>
                <div>
                    <div style="font-size:0.7rem;color:rgba(255,255,255,0.6)">{t("expl_s10_density_label", lang)}</div>
                    <div style="font-size:1rem;font-weight:700">{d4_s.get(opt_path["d4"], opt_path["d4"])}</div>
                </div>
                <div>
                    <div style="font-size:0.7rem;color:rgba(255,255,255,0.6)">{t("expl_s10_mgmt_label", lang)}</div>
                    <div style="font-size:1rem;font-weight:700">{d5_s.get(opt_path["d5"], opt_path["d5"])}</div>
                </div>
                <div>
                    <div style="font-size:0.7rem;color:rgba(255,255,255,0.6)">{t("expl_s10_ev_label", lang)}</div>
                    <div style="font-size:1.6rem;font-weight:900;color:#76c442">{opt_ev:.1f} sc/ha</div>
                    <div style="font-size:0.75rem;color:rgba(255,255,255,0.7)">{delta:+.1f} sc/ha {t("expl_s10_vs_ref", lang)}</div>
                </div>
                {f'<div><div style="font-size:0.7rem;color:rgba(255,255,255,0.6)">{t("expl_s10_interval_label", lang)}</div><div style="font-size:0.92rem;font-weight:600">{mc["p5"]:.0f} – {mc["p95"]:.0f} sc/ha</div></div>' if mc else ""}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(t("expl_s10_view_results", lang), type="primary"):
            nav_go("results")
    else:
        st.info(t("expl_s10_no_sim", lang))
        if st.button(t("expl_s10_go_sim", lang), type="primary"):
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
    lang = st.session_state.get("lang", "en")
    st.markdown(_EXPLAINER_CSS, unsafe_allow_html=True)

    result = st.session_state.get("sim_result")

    st.markdown(f'<div class="page-title">{t("expl_title", lang)}</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="page-subtitle">{t("expl_subtitle", lang)}</div>',
        unsafe_allow_html=True,
    )

    if result:
        st.caption(t("expl_has_sim", lang))
    else:
        st.caption(t("expl_no_sim_caption", lang))

    st.markdown("<br>", unsafe_allow_html=True)

    current = _step_key()
    _progress_bar(current, lang)
    st.markdown("---")

    step_map = {
        1:  lambda: _render_step_1(lang),
        2:  lambda: _render_step_2(result, lang),
        3:  lambda: _render_step_3(result, lang),
        4:  lambda: _render_step_4(result, lang),
        5:  lambda: _render_step_5(result, lang),
        6:  lambda: _render_step_6(lang),
        7:  lambda: _render_step_7(result, lang),
        8:  lambda: _render_step_8(result, lang),
        9:  lambda: _render_step_9(result, lang),
        10: lambda: _render_step_10(result, lang),
    }
    step_map[current]()

    st.markdown("---")
    _nav_buttons(current, lang)
