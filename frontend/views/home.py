"""Home dashboard — season calendar, field overview, quick actions, and model status."""
from __future__ import annotations
from datetime import date, datetime
import streamlit as st
import plotly.graph_objects as go
from frontend.navigation import go as navigate

_MT_BASELINE = 60.0
_SEASON_MONTHS = ['Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr']
_MONTH_TO_X    = {8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 1: 5, 2: 6, 3: 7, 4: 8}


def _greeting(name: str, lang: str) -> str:
    h = datetime.now().hour
    if lang == "pt":
        greet = "Bom dia" if h < 12 else "Boa tarde" if h < 18 else "Boa noite"
    else:
        greet = "Good morning" if h < 12 else "Good afternoon" if h < 18 else "Good evening"
    return f"{greet}, {name}"


def _season_chart(lang: str) -> go.Figure:
    today = date.today()
    today_x = None
    if today.month in _MONTH_TO_X:
        today_x = _MONTH_TO_X[today.month] + (today.day - 1) / 30.0

    fig = go.Figure()

    zones = [
        (0.0, 2.0, "#e3f2fd", "#1565c0", "Pre-Season\nPreparation",   0.5),
        (2.0, 3.3, "#e8f5e9", "#2e7d32", "Planting\nWindow",          0.5),
        (3.3, 6.5, "#fff8e1", "#f9a825", "Growing\nSeason",            0.5),
        (6.5, 8.7, "#fce4ec", "#c62828", "Harvest",                    0.5),
    ]
    for x0, x1, fill, color, label, _ in zones:
        fig.add_shape(
            type="rect", x0=x0, x1=x1, y0=0.0, y1=1.0,
            fillcolor=fill, line=dict(color=color, width=1.2), layer="below",
        )
        fig.add_annotation(
            x=(x0 + x1) / 2, y=0.52, text=label,
            showarrow=False, font=dict(size=10, color=color), align="center",
        )

    # Planting sub-windows
    fig.add_shape(type="rect", x0=2.0, x1=2.5, y0=0.08, y1=0.92,
                  fillcolor="#c8e6c9", line=dict(color="#388e3c", width=1), layer="below")
    fig.add_annotation(x=2.25, y=0.78, text="Early", showarrow=False,
                       font=dict(size=8, color="#1b5e20"))

    fig.add_shape(type="rect", x0=2.5, x1=3.1, y0=0.04, y1=0.96,
                  fillcolor="#66bb6a", line=dict(color="#1b5e20", width=1.5), layer="below")
    fig.add_annotation(x=2.8, y=0.78, text="★ Optimal", showarrow=False,
                       font=dict(size=9, color="#1b5e20"))

    # Key date labels
    fig.add_annotation(x=2.5, y=-0.02, text="Oct 16", showarrow=False,
                       font=dict(size=8, color="#555"), yanchor="top")
    fig.add_annotation(x=3.1, y=-0.02, text="Nov 10", showarrow=False,
                       font=dict(size=8, color="#555"), yanchor="top")

    if today_x is not None:
        fig.add_shape(type="line", x0=today_x, x1=today_x, y0=-0.05, y1=1.1,
                      line=dict(color="#c62828", width=2, dash="dot"))
        fig.add_annotation(
            x=today_x, y=1.18,
            text=f"▼ Today · {today.strftime('%b %d')}",
            showarrow=False,
            font=dict(color="#c62828", size=10),
            bgcolor="rgba(255,255,255,0.85)",
        )

    fig.update_xaxes(
        tickvals=list(range(9)), ticktext=_SEASON_MONTHS,
        range=[-0.25, 8.85], tickfont=dict(size=11, color="#555"),
        gridcolor="#f0f0f0",
    )
    fig.update_yaxes(visible=False, range=[-0.12, 1.3])
    fig.update_layout(
        height=155,
        margin=dict(t=35, l=5, r=10, b=38),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
    )
    return fig


def _fields_chart(plots_with_sim: list, lang: str) -> go.Figure:
    names  = [p["nome"] for p in plots_with_sim]
    evs    = [p["simulations"][-1]["ev_simulated"] for p in plots_with_sim]
    areas  = [p["area_ha"] for p in plots_with_sim]
    colors = ["#2e7d32" if e >= _MT_BASELINE else "#e65100" for e in evs]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=evs, y=names,
        orientation="h",
        marker_color=colors,
        text=[f"{e:.1f}" for e in evs],
        textposition="outside",
        customdata=areas,
        hovertemplate="<b>%{y}</b><br>EV: %{x:.1f} sc/ha<br>Area: %{customdata:,.0f} ha<extra></extra>",
    ))
    fig.add_vline(x=_MT_BASELINE, line_color="#f57c00", line_dash="dot", line_width=1.5,
                  annotation_text="MT ref 60 sc/ha",
                  annotation_font_size=9, annotation_font_color="#b35c00",
                  annotation_position="top right")
    fig.update_layout(
        height=max(150, len(names) * 48 + 40),
        margin=dict(t=8, l=8, r=80, b=30),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(gridcolor="#f0f0f0", title="Expected yield (sc/ha)", tickfont=dict(size=10)),
        yaxis=dict(tickfont=dict(size=11)),
        showlegend=False,
        font=dict(color="#1a1a2e", size=11),
    )
    return fig


def _last_sim_chart(sim_result: dict, lang: str) -> go.Figure | None:
    try:
        paths    = sim_result.get("paths", [])
        criteria = sim_result.get("criteria", {})
        optimal  = criteria.get("bayes_ev", {}).get("path_idx", 0)
        ev_vals  = criteria.get("bayes_ev", {}).get("criterion_values", [])

        top3_idx = sorted(range(len(ev_vals)), key=lambda i: ev_vals[i], reverse=True)[:5]
        labels   = [f"Path {i+1}" for i in top3_idx]
        values   = [ev_vals[i] for i in top3_idx]
        colors   = ["#1565c0" if i == optimal else "#90a4ae" for i in top3_idx]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=values, y=labels,
            orientation="h",
            marker_color=colors,
            text=[f"{v:.1f}" for v in values],
            textposition="outside",
        ))
        fig.add_vline(x=_MT_BASELINE, line_color="#f57c00", line_dash="dot",
                      annotation_text="60 sc/ha", annotation_font_size=9)
        fig.update_layout(
            height=200,
            margin=dict(t=8, l=8, r=70, b=25),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(gridcolor="#f0f0f0", tickfont=dict(size=10)),
            yaxis=dict(tickfont=dict(size=10)),
            showlegend=False,
            font=dict(color="#1a1a2e", size=11),
        )
        return fig
    except Exception:
        return None


def render() -> None:
    lang = st.session_state.get("lang", "en")
    auth = st.session_state.get("auth", {})
    name = auth.get("name", "Produtor").split()[0]

    # ── Load data ──────────────────────────────────────────────────────────────
    try:
        from frontend.plots_store import load_plots
        plots = load_plots(auth.get("email", auth.get("id", "demo")))
    except Exception:
        plots = []

    sim_result  = st.session_state.get("sim_result")
    sim_history = st.session_state.get("sim_history", [])
    has_result  = sim_result is not None

    total_area      = sum(p["area_ha"] for p in plots)
    plots_with_sim  = [p for p in plots if p.get("simulations")]

    last_ev = None
    if has_result:
        rc = st.session_state.get("risk_criterion", "bayes_ev")
        try:
            last_ev = sim_result["criteria"][rc]["value"]
        except Exception:
            last_ev = sim_result.get("user_selection", {}).get("ev")
    elif plots_with_sim:
        last_ev = plots_with_sim[-1]["simulations"][-1]["ev_simulated"]

    try:
        from backend.learning import get_learning_stats
        n_seasons = get_learning_stats(auth.get("email", "demo"))["n"]
    except Exception:
        n_seasons = 0

    # ── HEADER ────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:flex-end;margin-bottom:12px">
      <div>
        <div class="page-title">{_greeting(name, lang)}</div>
        <div class="page-subtitle">{"Suporte à decisão de safra de soja · Mato Grosso" if lang == "pt" else "Soybean yield decision support · Mato Grosso"}</div>
      </div>
      <div style="color:#9e9e9e;font-size:0.82rem;text-align:right;line-height:1.6">
        {datetime.now().strftime("%A, %B %d · %Y")}
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI STRIP ─────────────────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)

    with k1:
        n_fields = len(plots)
        sub = f"{total_area:,.0f} ha total" if plots else ("Adicione seu primeiro talhão" if lang == "pt" else "Add your first field")
        st.markdown(f"""<div class="metric-card">
            <div class="mc-label">{"Talhões cadastrados" if lang == "pt" else "Registered fields"}</div>
            <div class="mc-value" style="font-size:1.8rem">{n_fields}</div>
            <div class="mc-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

    with k2:
        ev_color = "#2e7d32" if (last_ev or 0) >= _MT_BASELINE else "#c62828" if last_ev else "#6b6b8a"
        ev_disp  = f"{last_ev:.1f} sc/ha" if last_ev else "—"
        diff_str = ""
        if last_ev:
            diff = last_ev - _MT_BASELINE
            diff_str = f"({'▲' if diff >= 0 else '▼'} {abs(diff):.1f} vs MT ref)"
        st.markdown(f"""<div class="metric-card">
            <div class="mc-label">{"Último EV simulado" if lang == "pt" else "Latest simulated EV"}</div>
            <div class="mc-value" style="color:{ev_color}">{ev_disp}</div>
            <div class="mc-sub">{diff_str or "60 sc/ha MT reference"}</div>
        </div>""", unsafe_allow_html=True)

    with k3:
        n_sims = len(sim_history)
        st.markdown(f"""<div class="metric-card">
            <div class="mc-label">{"Simulações" if lang == "pt" else "Simulations"}</div>
            <div class="mc-value" style="font-size:1.8rem">{n_sims}</div>
            <div class="mc-sub">{"nesta sessão" if lang == "pt" else "this session"}</div>
        </div>""", unsafe_allow_html=True)

    with k4:
        pct = min(100, int(n_seasons / 3 * 100))
        cc  = "#2e7d32" if n_seasons >= 3 else "#1565c0"
        cl  = ("Calibrado ✓" if lang == "pt" else "Calibrated ✓") if n_seasons >= 3 else f"{n_seasons}/3 safras"
        st.markdown(f"""<div class="metric-card">
            <div class="mc-label">{"Calibração do modelo" if lang == "pt" else "Model calibration"}</div>
            <div class="mc-value" style="color:{cc};font-size:1rem;font-weight:700">{cl}</div>
            <div style="background:#e0e0e0;border-radius:4px;height:5px;margin-top:8px;overflow:hidden">
                <div style="background:{cc};width:{pct}%;height:5px"></div>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── MAIN GRID ──────────────────────────────────────────────────────────────
    chart_col, action_col = st.columns([5, 4], gap="large")

    with chart_col:
        # Season calendar
        _sec_hdr = "Calendário da Safra · Mato Grosso" if lang == "pt" else "Crop Calendar · Mato Grosso"
        st.markdown(f'<div class="section-hdr">{_sec_hdr}</div>', unsafe_allow_html=True)
        st.plotly_chart(_season_chart(lang), use_container_width=True)

        # Fields yield chart OR last simulation chart OR empty state
        if plots_with_sim:
            _fhdr = "Produtividade Esperada por Talhão" if lang == "pt" else "Expected Yield by Field"
            st.markdown(f'<div class="section-hdr">{_fhdr}</div>', unsafe_allow_html=True)
            st.plotly_chart(_fields_chart(plots_with_sim, lang), use_container_width=True)
        elif has_result:
            _shdr = "Melhores caminhos — última simulação" if lang == "pt" else "Top paths — last simulation"
            st.markdown(f'<div class="section-hdr">{_shdr}</div>', unsafe_allow_html=True)
            fig_sim = _last_sim_chart(sim_result, lang)
            if fig_sim:
                st.plotly_chart(fig_sim, use_container_width=True)
        else:
            st.markdown("""
            <div style="background:#f6f7fb;border:1.5px dashed #c8c0d8;border-radius:12px;
                        padding:28px 20px;text-align:center;margin-top:12px">
                <div style="font-size:2rem;margin-bottom:8px">🌾</div>
                <div style="font-size:0.92rem;font-weight:700;color:#3a3a5a">No data yet</div>
                <div style="font-size:0.78rem;color:#6b6b8a;margin-top:6px">
                    Run a simulation or add your first field to see charts here
                </div>
            </div>
            """, unsafe_allow_html=True)

    with action_col:
        _ahdr = "Ações Rápidas" if lang == "pt" else "Quick Actions"
        st.markdown(f'<div class="section-hdr">{_ahdr}</div>', unsafe_allow_html=True)

        if lang == "pt":
            actions = [
                ("🌱", "Nova Simulação",     "Rode um cenário de produtividade com as condições do seu campo",    "#1565c0", "input",            True),
                ("🗺️",  "Meus Talhões",       "Gerencie suas áreas e compare simulações entre talhões",            "#2e7d32", "farm",             True),
                ("📊",  "Decomposição",        "Analise caminhos de decisão e sensibilidade dos fatores",           "#6a1b9a", "dashboard",        has_result),
                ("🎲",  "Monte Carlo",         "Distribuição de produtividade e intervalos de risco estocástico",   "#e65100", "monte_carlo",      has_result),
                ("📈",  "Inteligência de Campo","Alertas de combinações críticas e benchmarks regionais",           "#00838f", "bi_dashboard",     has_result),
                ("🎯",  "Aprendizado de Safra","Registre colheitas reais e calibre o modelo da sua fazenda",        "#558b2f", "adaptive_planner", True),
            ]
        else:
            actions = [
                ("🌱", "New Simulation",     "Run a yield scenario with your field and climate conditions",       "#1565c0", "input",            True),
                ("🗺️",  "My Fields",          "Manage your plots and compare simulations across fields",           "#2e7d32", "farm",             True),
                ("📊",  "Yield Breakdown",    "Analyse decision paths and factor sensitivity",                     "#6a1b9a", "dashboard",        has_result),
                ("🎲",  "Monte Carlo Risk",   "Stochastic yield distribution and risk intervals",                  "#e65100", "monte_carlo",      has_result),
                ("📈",  "Field Intelligence", "Critical combination alerts and regional benchmarks",               "#00838f", "bi_dashboard",     has_result),
                ("🎯",  "Season Learning",    "Record actual yields and calibrate your farm model",                "#558b2f", "adaptive_planner", True),
            ]

        for emoji, title, desc, color, page, enabled in actions:
            opacity = "1" if enabled else "0.5"
            border_color = color if enabled else "#ddd"
            bg = "white" if enabled else "#f9f9f9"
            st.markdown(f"""
            <div style="background:{bg};border:1px solid #e4e4f0;border-radius:10px;
                        padding:11px 14px;border-left:4px solid {border_color};
                        margin-bottom:6px;opacity:{opacity}">
              <div style="display:flex;align-items:center;gap:10px">
                <span style="font-size:1.25rem;flex-shrink:0">{emoji}</span>
                <div>
                  <div style="font-size:0.85rem;font-weight:700;color:#1a1a2e;line-height:1.2">{title}</div>
                  <div style="font-size:0.7rem;color:#6b6b8a;line-height:1.3;margin-top:2px">{desc}</div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            btn_label = f"Open →" if enabled else ("Run a simulation first" if not has_result and page in ("dashboard", "monte_carlo", "bi_dashboard") else "Open →")
            if st.button(btn_label, key=f"home_act_{page}", use_container_width=True,
                         type="primary" if (page == "input" and not has_result) else "secondary",
                         disabled=not enabled):
                if page == "input":
                    st.session_state.input_step = 1
                navigate(page)

    # ── RECENT SIMULATIONS ─────────────────────────────────────────────────────
    if sim_history:
        st.markdown("<br>", unsafe_allow_html=True)
        _rhdr = "Simulações Recentes" if lang == "pt" else "Recent Simulations"
        st.markdown(f'<div class="section-hdr">{_rhdr}</div>', unsafe_allow_html=True)

        recent = list(reversed(sim_history))[:4]
        cols   = st.columns(len(recent))
        for col, sim in zip(cols, recent):
            with col:
                try:
                    ev       = sim["result"]["criteria"]["bayes_ev"]["value"]
                    ev_color = "#2e7d32" if ev >= _MT_BASELINE else "#c62828"
                    ev_str   = f"{ev:.1f}"
                    diff     = ev - _MT_BASELINE
                    diff_str = f"{'▲' if diff >= 0 else '▼'} {abs(diff):.1f}"
                    diff_c   = "#2e7d32" if diff >= 0 else "#c62828"
                except Exception:
                    ev_color = "#6b6b8a"
                    ev_str = "—"
                    diff_str = ""
                    diff_c = "#6b6b8a"

                st.markdown(f"""
                <div class="metric-card" style="text-align:left;padding:12px 14px">
                  <div style="font-size:0.68rem;color:#9e9e9e;margin-bottom:3px">
                    #{sim['id']} · {sim['timestamp'][:10]}
                  </div>
                  <div style="font-size:0.78rem;font-weight:600;color:#1a1a2e;
                              margin-bottom:6px;line-height:1.3;
                              white-space:nowrap;overflow:hidden;text-overflow:ellipsis">
                    {sim['summary']}
                  </div>
                  <div style="font-size:1.5rem;font-weight:800;color:{ev_color};line-height:1">
                    {ev_str} <span style="font-size:0.7rem;color:#9e9e9e;font-weight:400">sc/ha</span>
                  </div>
                  <div style="font-size:0.75rem;color:{diff_c};margin-top:3px">{diff_str} vs ref</div>
                </div>
                """, unsafe_allow_html=True)

        if len(sim_history) > 4:
            st.markdown("<br>", unsafe_allow_html=True)
            col_h, _ = st.columns([1, 4])
            with col_h:
                _hlbl = "Ver histórico completo →" if lang == "pt" else "View full history →"
                if st.button(_hlbl, key="home_hist_btn"):
                    navigate("history")
