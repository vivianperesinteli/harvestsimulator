"""
Decision Tree Simulator — Frontend Streamlit
Bayer CropScience × Inteli · Sprint 3 · Grupo 2

Iniciar backend:  uvicorn backend.main:app --reload --port 8000
Iniciar frontend: streamlit run frontend/app.py
"""

import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st
from frontend.styles    import inject_styles
from frontend.auth      import is_authenticated, render_auth, logout
from frontend.navigation import go

st.set_page_config(
    page_title="Harvest Simulator · Soy MT",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_styles()

# ── Autenticação ──────────────────────────────────────────────────────────────
if not is_authenticated():
    render_auth()
    st.stop()

# ── Session defaults ──────────────────────────────────────────────────────────
for k, v in {
    "page":          "home",
    "sim_result":    None,
    "sim_context":   None,
    "sim_decisions": None,
    "sim_display":   None,
    "mc_result":     None,
    "sim_history":   [],
    "input_step":    1,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ── Página Home ───────────────────────────────────────────────────────────────
def _render_home():
    auth = st.session_state.auth
    st.markdown(
        f'<div class="page-title">Hello, {auth["name"].split()[0]}!</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="page-subtitle">Harvest Simulator · Soy · Mato Grosso</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Hero ──────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="landing-hero" style="position:relative;overflow:hidden">

      <!-- Planta de soja DIREITA — principal, grande -->
      <svg style="position:absolute;right:-16px;bottom:-18px;opacity:0.20;pointer-events:none"
           width="290" height="310" viewBox="0 0 210 210" fill="none">
        <line x1="105" y1="205" x2="105" y2="28" stroke="white" stroke-width="5" stroke-linecap="round"/>
        <ellipse cx="105" cy="30" rx="11" ry="17" fill="white" transform="rotate(-8 105 30)"/>
        <ellipse cx="94"  cy="38" rx="9"  ry="14" fill="white" transform="rotate(12 94 38)"/>
        <ellipse cx="116" cy="38" rx="9"  ry="14" fill="white" transform="rotate(-12 116 38)"/>
        <path d="M105 78 C88 68 72 54 78 40 C88 50 100 66 105 78Z" fill="white"/>
        <path d="M105 78 C122 68 138 54 132 40 C122 50 110 66 105 78Z" fill="white"/>
        <ellipse cx="105" cy="78" rx="7" ry="5" fill="white" opacity="0.55"/>
        <path d="M105 122 C83 110 64 92 72 74 C85 88 100 108 105 122Z" fill="white"/>
        <path d="M105 122 C127 110 146 92 138 74 C125 88 110 108 105 122Z" fill="white"/>
        <ellipse cx="105" cy="122" rx="8" ry="5" fill="white" opacity="0.55"/>
        <ellipse cx="76"  cy="82" rx="7" ry="13" fill="white" transform="rotate(38 76 82)" opacity="0.75"/>
        <ellipse cx="134" cy="82" rx="7" ry="13" fill="white" transform="rotate(-38 134 82)" opacity="0.75"/>
        <path d="M105 165 C78 150 56 128 66 106 C82 124 98 148 105 165Z" fill="white" opacity="0.65"/>
        <path d="M105 165 C132 150 154 128 144 106 C128 124 112 148 105 165Z" fill="white" opacity="0.65"/>
        <ellipse cx="70"  cy="118" rx="7" ry="13" fill="white" transform="rotate(45 70 118)" opacity="0.6"/>
        <ellipse cx="140" cy="118" rx="7" ry="13" fill="white" transform="rotate(-45 140 118)" opacity="0.6"/>
        <ellipse cx="82"  cy="146" rx="6" ry="11" fill="white" transform="rotate(30 82 146)" opacity="0.5"/>
        <ellipse cx="128" cy="146" rx="6" ry="11" fill="white" transform="rotate(-30 128 146)" opacity="0.5"/>
      </svg>

      <!-- Planta de soja ESQUERDA — grande, espelhada -->
      <svg style="position:absolute;left:-16px;bottom:-18px;opacity:0.16;pointer-events:none;transform:scaleX(-1) rotate(-6deg)"
           width="240" height="270" viewBox="0 0 210 210" fill="none">
        <line x1="105" y1="205" x2="105" y2="45" stroke="white" stroke-width="5" stroke-linecap="round"/>
        <ellipse cx="105" cy="47" rx="10" ry="15" fill="white" transform="rotate(-5 105 47)"/>
        <ellipse cx="95"  cy="55" rx="8"  ry="13" fill="white" transform="rotate(10 95 55)"/>
        <ellipse cx="115" cy="55" rx="8"  ry="13" fill="white" transform="rotate(-10 115 55)"/>
        <path d="M105 92 C90 82 76 68 82 54 C92 66 102 82 105 92Z" fill="white"/>
        <path d="M105 92 C120 82 134 68 128 54 C118 66 108 82 105 92Z" fill="white"/>
        <ellipse cx="105" cy="92" rx="6" ry="4" fill="white" opacity="0.5"/>
        <ellipse cx="78"  cy="96" rx="6" ry="11" fill="white" transform="rotate(36 78 96)" opacity="0.72"/>
        <ellipse cx="132" cy="96" rx="6" ry="11" fill="white" transform="rotate(-36 132 96)" opacity="0.72"/>
        <path d="M105 136 C86 124 70 106 78 88 C90 104 100 124 105 136Z" fill="white" opacity="0.8"/>
        <path d="M105 136 C124 124 140 106 132 88 C120 104 110 124 105 136Z" fill="white" opacity="0.8"/>
        <path d="M105 176 C82 162 62 140 72 118 C88 136 102 158 105 176Z" fill="white" opacity="0.6"/>
        <path d="M105 176 C128 162 148 140 138 118 C122 136 108 158 105 176Z" fill="white" opacity="0.6"/>
        <ellipse cx="74"  cy="138" rx="6" ry="12" fill="white" transform="rotate(44 74 138)" opacity="0.55"/>
        <ellipse cx="136" cy="138" rx="6" ry="12" fill="white" transform="rotate(-44 136 138)" opacity="0.55"/>
      </svg>

      <!-- Planta de soja CENTRO-TOPO — média, decorativa -->
      <svg style="position:absolute;right:28%;top:-14px;opacity:0.10;pointer-events:none;transform:rotate(4deg)"
           width="120" height="150" viewBox="0 0 210 210" fill="none">
        <line x1="105" y1="205" x2="105" y2="40" stroke="white" stroke-width="5" stroke-linecap="round"/>
        <ellipse cx="105" cy="42" rx="10" ry="16" fill="white" transform="rotate(-6 105 42)"/>
        <ellipse cx="95"  cy="50" rx="8"  ry="13" fill="white" transform="rotate(10 95 50)"/>
        <ellipse cx="115" cy="50" rx="8"  ry="13" fill="white" transform="rotate(-10 115 50)"/>
        <path d="M105 90 C89 80 74 66 80 52 C90 62 102 78 105 90Z" fill="white"/>
        <path d="M105 90 C121 80 136 66 130 52 C120 62 108 78 105 90Z" fill="white"/>
        <ellipse cx="79"  cy="93" rx="6" ry="10" fill="white" transform="rotate(35 79 93)" opacity="0.7"/>
        <ellipse cx="131" cy="93" rx="6" ry="10" fill="white" transform="rotate(-35 131 93)" opacity="0.7"/>
        <path d="M105 135 C84 122 65 104 74 85 C87 100 101 120 105 135Z" fill="white" opacity="0.7"/>
        <path d="M105 135 C126 122 145 104 136 85 C123 100 109 120 105 135Z" fill="white" opacity="0.7"/>
      </svg>

      <!-- Grãos soltos espalhados -->
      <svg style="position:absolute;inset:0;width:100%;height:100%;opacity:0.08;pointer-events:none" viewBox="0 0 800 200" preserveAspectRatio="xMidYMid slice" fill="none">
        <ellipse cx="60"  cy="30"  rx="7" ry="11" fill="white" transform="rotate(20 60 30)"/>
        <ellipse cx="120" cy="15"  rx="5" ry="8"  fill="white" transform="rotate(-15 120 15)"/>
        <ellipse cx="200" cy="45"  rx="6" ry="9"  fill="white" transform="rotate(35 200 45)"/>
        <ellipse cx="680" cy="25"  rx="6" ry="10" fill="white" transform="rotate(-20 680 25)"/>
        <ellipse cx="740" cy="55"  rx="5" ry="8"  fill="white" transform="rotate(10 740 55)"/>
        <ellipse cx="760" cy="165" rx="7" ry="11" fill="white" transform="rotate(-30 760 165)"/>
        <ellipse cx="50"  cy="160" rx="6" ry="9"  fill="white" transform="rotate(25 50 160)"/>
        <ellipse cx="300" cy="10"  rx="4" ry="7"  fill="white" transform="rotate(-10 300 10)"/>
        <ellipse cx="500" cy="180" rx="5" ry="8"  fill="white" transform="rotate(15 500 180)"/>
      </svg>

      <div class="landing-tag">Soy &middot; Mato Grosso</div>
      <div class="landing-title">Simulate your harvest<br>before deciding</div>
      <div class="landing-desc">
          Enter your field conditions and management decisions.
          The simulator projects expected productivity for each climate scenario
          and identifies which combination delivers the best expected outcome.
      </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Start new simulation →", type="primary"):
        st.session_state.input_step = 1
        go("input")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── How it works ───────────────────────────────────────────────────────
    st.markdown('<div class="section-hdr">How it works</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    for col, num, title, desc in [
        (c1, "1", "Field context",
         "Enter region, soil type, pH, drainage, structural fitness, area and climate forecast."),
        (c2, "2", "Producer decisions",
         "Set planting window, cultivar, seed treatment, density, disease management and technology."),
        (c3, "3", "Review and confirmation",
         "See a full summary before simulating to make sure everything is correct."),
        (c4, "4", "Results and recommendations",
         "Receive ranked recommendations with expected productivity, risk analysis and a downloadable report."),
    ]:
        with col:
            st.markdown(f"""
            <div class="how-card">
                <div class="how-number">{num}</div>
                <div class="how-title">{title}</div>
                <div class="how-desc">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Model summary ──────────────────────────────────────────────────────
    st.markdown('<div class="section-hdr">How the simulator works</div>', unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown("""<div class="metric-card">
            <div class="mc-label">Regional reference</div>
            <div class="mc-value">60 sc/ha</div>
            <div class="mc-sub">Average productivity MT · CONAB 2023/24</div>
        </div>""", unsafe_allow_html=True)
    with m2:
        st.markdown("""<div class="metric-card">
            <div class="mc-label">Factors evaluated</div>
            <div class="mc-value" style="font-size:1.4rem;line-height:1.4">
                7 + 6
            </div>
            <div class="mc-sub">7 field factors + 6 producer decisions</div>
        </div>""", unsafe_allow_html=True)
    with m3:
        st.markdown("""<div class="metric-card">
            <div class="mc-label">Risk analysis</div>
            <div class="mc-value">10,000 sim.</div>
            <div class="mc-sub">90% confidence interval per scenario</div>
        </div>""", unsafe_allow_html=True)

    # ── Histórico rápido ───────────────────────────────────────────────────
    history = st.session_state.sim_history
    if history:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-hdr">Recent simulations</div>', unsafe_allow_html=True)
        for sim in reversed(history[-3:]):
            ev_val = sim["result"]["criteria"]["bayes_ev"]["value"]
            st.markdown(f"""
            <div class="hist-card" style="margin-bottom:8px">
                <div class="hist-number">#{sim['id']}</div>
                <div class="hist-main">
                    <div class="hist-title">{sim['summary']}</div>
                    <div class="hist-sub">{sim['timestamp']}</div>
                </div>
                <div class="hist-ev">
                    <div class="hist-ev-val">{ev_val:.1f}</div>
                    <div class="hist-ev-unit">sc/ha expected</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        col_h, _ = st.columns([1, 5])
        with col_h:
            if st.button("View full history →"):
                go("history")


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    auth = st.session_state.auth

    # Logo + brand
    st.markdown("""
    <div class="sidebar-logo-area">
        <div class="sidebar-logo-circle">
            <svg width="22" height="22" viewBox="0 0 36 36" fill="none" style="position:relative;z-index:1">
                <line x1="18" y1="31" x2="18" y2="11" stroke="white" stroke-width="2.5" stroke-linecap="round"/>
                <ellipse cx="18" cy="9" rx="4" ry="6.5" fill="rgba(255,255,255,0.95)"/>
                <path d="M18 22 C14 20 10 16 11 11 C14 13 17 17 18 22Z" fill="rgba(255,255,255,0.75)"/>
                <path d="M18 22 C22 20 26 16 25 11 C22 13 19 17 18 22Z" fill="rgba(255,255,255,0.75)"/>
                <path d="M18 27 C14 25 11 21 13 17 C15 19 17 23 18 27Z" fill="rgba(255,255,255,0.55)"/>
                <path d="M18 27 C22 25 25 21 23 17 C21 19 19 23 18 27Z" fill="rgba(255,255,255,0.55)"/>
            </svg>
        </div>
        <div>
            <span class="sidebar-brand">Harvest Simulator</span>
            <span class="sidebar-brand-sub">Soy · Mato Grosso</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    current = st.session_state.page

    def _nav_btn(label: str, key: str, page: str, enabled: bool = True) -> None:
        is_active = current == page
        clicked = st.button(
            label,
            key=f"nav_{key}",
            use_container_width=True,
            type="primary" if is_active else "secondary",
            disabled=(not enabled and not is_active),
        )
        if clicked and not is_active and enabled:
            if page == "input":
                st.session_state.input_step = 1
            go(page)

    # Main navigation
    st.markdown('<div class="nav-section-label">Main</div>', unsafe_allow_html=True)
    _nav_btn("Home", "home", "home")
    _nav_btn("New Simulation", "input", "input")

    # Analysis
    has_result = st.session_state.sim_result is not None
    st.markdown('<div class="nav-section-label">Analysis</div>', unsafe_allow_html=True)
    _nav_btn("Results", "results", "results")
    _nav_btn("Dashboard", "dashboard", "dashboard", enabled=has_result)

    # About
    st.markdown('<div class="nav-section-label">About</div>', unsafe_allow_html=True)
    _nav_btn("How We Calculate", "explainer", "explainer")

    # History
    st.markdown('<div class="nav-section-label">History</div>', unsafe_allow_html=True)
    n_hist = len(st.session_state.sim_history)
    label_hist = f"History ({n_hist})" if n_hist else "History"
    _nav_btn(label_hist, "history", "history")

    # Active scope
    st.markdown("""
    <div class="sidebar-scope">
        <div class="scope-label">Crop</div>
        <div class="scope-value"><span class="scope-dot"></span>Soy &middot; Mato Grosso</div>
    </div>
    """, unsafe_allow_html=True)

    # Usuário + logout
    st.markdown("""<hr style="border-color:rgba(255,255,255,0.07);margin:8px 0">""", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="sidebar-user">
        <div class="sidebar-user-name">{auth['name']}</div>
        <div class="sidebar-user-role">{auth['email']}</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Log out", key="btn_logout", use_container_width=True):
        logout()



# ── Roteador ──────────────────────────────────────────────────────────────────
from frontend.views import input      as input_view
from frontend.views import results    as results_view
from frontend.views import dashboard  as dashboard_view
from frontend.views import monte_carlo as mc_view
from frontend.views import history    as history_view
from frontend.views import explainer  as explainer_view

page = st.session_state.page

if page == "home":
    _render_home()
elif page == "input":
    input_view.render()
elif page == "results":
    results_view.render()
elif page == "dashboard":
    dashboard_view.render()
elif page == "monte_carlo":
    mc_view.render()
elif page == "history":
    history_view.render()
elif page == "explainer":
    explainer_view.render()
else:
    _render_home()
