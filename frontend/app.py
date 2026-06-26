"""
Decision Tree Simulator — Frontend Streamlit
Soy · Mato Grosso

Start backend:  uvicorn backend.main:app --reload --port 8000
Start frontend: streamlit run frontend/app.py
"""

import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import streamlit as st
import streamlit.components.v1 as components
from frontend.styles    import inject_styles
from frontend.auth      import is_authenticated, render_auth, logout
from frontend.navigation import go
from frontend.i18n      import t

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
    "page":             "home",
    "lang":             "en",
    "sim_result":       None,
    "sim_context":      None,
    "sim_decisions":    None,
    "sim_display":      None,
    "mc_result":        None,
    "sim_history":      [],
    "input_step":       1,
    "talhao_id":        None,
    "talhao_nome":      None,
    "talhao_prefill":   None,
    "_plot_delete_id":  None,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ── Página Home ───────────────────────────────────────────────────────────────
def _render_home():
    auth = st.session_state.auth
    lang = st.session_state.lang
    st.markdown(
        f'<div class="page-title">{t("home_hello", lang, name=auth["name"].split()[0])}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="page-subtitle">{t("home_sub", lang)}</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Hero ──────────────────────────────────────────────────────────────
    st.markdown(f"""
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

      <div class="landing-tag">{t("home_tag", lang)}</div>
      <div class="landing-title">{t("home_title", lang)}</div>
      <div class="landing-desc">{t("home_desc", lang)}</div>
    </div>
    """, unsafe_allow_html=True)

    btn_col, farm_col, _ = st.columns([2, 2, 3])
    with btn_col:
        if st.button(t("home_cta", lang), type="primary", use_container_width=True):
            st.session_state.input_step = 1
            go("input")
    with farm_col:
        _farm_lbl = "🗺️ Meus Talhões" if lang == "pt" else "🗺️ My Fields"
        if st.button(_farm_lbl, use_container_width=True):
            go("farm")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── How it works ───────────────────────────────────────────────────────
    st.markdown(f'<div class="section-hdr">{t("home_how", lang)}</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    for col, num, title, desc in [
        (c1, "1", t("how1_title", lang), t("how1_desc", lang)),
        (c2, "2", t("how2_title", lang), t("how2_desc", lang)),
        (c3, "3", t("how3_title", lang), t("how3_desc", lang)),
        (c4, "4", t("how4_title", lang), t("how4_desc", lang)),
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
    st.markdown(f'<div class="section-hdr">{t("home_how_sim", lang)}</div>', unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(f"""<div class="metric-card">
            <div class="mc-label">{t("home_ref", lang)}</div>
            <div class="mc-value">60 sc/ha</div>
            <div class="mc-sub">{t("home_ref_sub", lang)}</div>
        </div>""", unsafe_allow_html=True)
    with m2:
        st.markdown(f"""<div class="metric-card">
            <div class="mc-label">{t("home_factors", lang)}</div>
            <div class="mc-value" style="font-size:1.4rem;line-height:1.4">7 + 6</div>
            <div class="mc-sub">{t("home_fac_sub", lang)}</div>
        </div>""", unsafe_allow_html=True)
    with m3:
        st.markdown(f"""<div class="metric-card">
            <div class="mc-label">{t("home_risk", lang)}</div>
            <div class="mc-value">{t("home_sim_n", lang)}</div>
            <div class="mc-sub">{t("home_risk_sub", lang)}</div>
        </div>""", unsafe_allow_html=True)

    # ── Histórico rápido ───────────────────────────────────────────────────
    history = st.session_state.sim_history
    if history:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<div class="section-hdr">{t("home_recent", lang)}</div>', unsafe_allow_html=True)
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
                    <div class="hist-ev-unit">{t("home_sc_unit", lang)}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        col_h, _ = st.columns([1, 5])
        with col_h:
            if st.button(t("home_hist_btn", lang)):
                go("history")


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    auth = st.session_state.auth
    lang = st.session_state.lang

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

    # Language toggle — botões ocultos usados pelo toggle customizado via JS
    _cl, _cr = st.columns(2)
    with _cl:
        if st.button("EN", key="btn_lang_en", use_container_width=True):
            if lang != "en":
                st.session_state.lang = "en"
                st.rerun()
    with _cr:
        if st.button("PT", key="btn_lang_pt", use_container_width=True):
            if lang != "pt":
                st.session_state.lang = "pt"
                st.rerun()

    # Toggle visual customizado (flag deslizante)
    _is_en = "true" if lang == "en" else "false"
    components.html(f"""
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: transparent; overflow: hidden;
          font-family: 'Inter', system-ui, sans-serif; }}
  .wrap {{
    display: flex; align-items: center; justify-content: center;
    gap: 10px; height: 44px;
  }}
  .lbl {{
    font-size: 11px; font-weight: 700; letter-spacing: 0.08em;
    color: rgba(255,255,255,0.28); transition: color .3s; user-select: none;
  }}
  .lbl.on {{ color: rgba(255,255,255,0.92); }}
  .track {{
    width: 62px; height: 30px;
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.13);
    border-radius: 99px; position: relative; cursor: pointer;
    transition: background .3s;
  }}
  .track:hover {{ background: rgba(255,255,255,0.12); }}
  .thumb {{
    position: absolute; top: 3px;
    width: 24px; height: 24px; border-radius: 50%;
    background: #fff;
    display: flex; align-items: center; justify-content: center;
    font-size: 15px; line-height: 1;
    box-shadow: 0 2px 10px rgba(0,0,0,0.5);
    transition: left .3s cubic-bezier(.4,0,.2,1);
  }}
</style>
<div class="wrap">
  <span class="lbl" id="lbl-en">EN</span>
  <div class="track" id="track">
    <div class="thumb" id="thumb"></div>
  </div>
  <span class="lbl" id="lbl-pt">PT</span>
</div>
<script>
  const isEn0 = {_is_en};
  const thumb  = document.getElementById('thumb');
  const lblEn  = document.getElementById('lbl-en');
  const lblPt  = document.getElementById('lbl-pt');

  function setState(en) {{
    thumb.style.left  = en ? '3px' : '35px';
    thumb.textContent = en ? '🇺🇸' : '🇧🇷';
    lblEn.className = 'lbl' + (en  ? ' on' : '');
    lblPt.className = 'lbl' + (!en ? ' on' : '');
  }}
  setState(isEn0);

  document.getElementById('track').addEventListener('click', () => {{
    const goEn = thumb.style.left !== '3px';
    setState(goEn);
    const doc = window.parent.document;
    const target = goEn ? 'EN' : 'PT';
    for (const b of doc.querySelectorAll('[data-testid="stSidebar"] button')) {{
      if (b.textContent.trim() === target) {{ b.click(); break; }}
    }}
  }});
</script>
""", height=44)

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
    st.markdown(f'<div class="nav-section-label">{t("nav_main", lang)}</div>', unsafe_allow_html=True)
    _nav_btn(t("nav_home", lang),    "home",  "home")
    _nav_btn(t("nav_new_sim", lang), "input", "input")
    _nav_btn(t("nav_farm", lang),    "farm",  "farm")

    # Analysis
    has_result = st.session_state.sim_result is not None
    st.markdown(f'<div class="nav-section-label">{t("nav_analysis", lang)}</div>', unsafe_allow_html=True)
    _nav_btn(t("nav_results", lang),   "results",    "results")
    _nav_btn(t("nav_dashboard", lang), "dashboard",  "dashboard",  enabled=has_result)
    _nav_btn(t("nav_bi", lang),        "bi_dashboard","bi_dashboard", enabled=has_result)

    # Season Learning
    st.markdown(f'<div class="nav-section-label">{t("nav_learning", lang)}</div>', unsafe_allow_html=True)
    _nav_btn(t("nav_adaptive", lang), "adaptive_planner", "adaptive_planner")

    # About
    st.markdown(f'<div class="nav-section-label">{t("nav_about", lang)}</div>', unsafe_allow_html=True)
    _nav_btn(t("nav_how", lang), "explainer", "explainer")

    # History
    st.markdown(f'<div class="nav-section-label">{t("nav_history", lang)}</div>', unsafe_allow_html=True)
    n_hist = len(st.session_state.sim_history)
    label_hist = t("nav_hist_n", lang, n=n_hist) if n_hist else t("nav_history", lang)
    _nav_btn(label_hist, "history", "history")

    # Active scope
    st.markdown(f"""
    <div class="sidebar-scope">
        <div class="scope-label">{t("crop_label", lang)}</div>
        <div class="scope-value"><span class="scope-dot"></span>{t("crop_value", lang)}</div>
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
    if st.button(t("logout", lang), key="btn_logout", use_container_width=True):
        logout()



# ── Sidebar expand button (JS — mais confiável que CSS puro no Streamlit 1.58) ──
components.html("""
<script>
(function() {
  const doc = window.parent.document;

  function setup() {
    if (doc.getElementById('_sb_expand_btn')) return;

    const btn = doc.createElement('button');
    btn.id = '_sb_expand_btn';
    btn.setAttribute('aria-label', 'Expand sidebar');
    btn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>';
    btn.style.cssText = [
      'position:fixed','top:50%','left:0','transform:translateY(-50%)',
      'z-index:999999',
      'background:linear-gradient(180deg,#1a5c38,#0d2b18)',
      'border:none','border-radius:0 10px 10px 0',
      'color:rgba(255,255,255,0.92)',
      'width:28px','height:52px',
      'display:none','align-items:center','justify-content:center',
      'cursor:pointer','box-shadow:3px 0 14px rgba(0,0,0,0.3)',
      'transition:background .2s',
    ].join(';');

    btn.addEventListener('click', () => {
      const native =
        doc.querySelector('[data-testid="collapsedControl"] button') ||
        doc.querySelector('[data-testid="stSidebarCollapsedControl"] button') ||
        doc.querySelector('[data-testid="stSidebar"] ~ * button');
      if (native) native.click();
    });
    btn.addEventListener('mouseenter', () => {
      btn.style.background = 'linear-gradient(180deg,#2d8a56,#1a5c38)';
    });
    btn.addEventListener('mouseleave', () => {
      btn.style.background = 'linear-gradient(180deg,#1a5c38,#0d2b18)';
    });

    doc.body.appendChild(btn);

    function sync() {
      const sb = doc.querySelector('[data-testid="stSidebar"]');
      if (!sb) return;
      const collapsed = sb.getAttribute('aria-expanded') === 'false';
      btn.style.display = collapsed ? 'flex' : 'none';
    }

    new MutationObserver(sync).observe(doc.body, {
      attributes: true, subtree: true, attributeFilter: ['aria-expanded'],
    });
    sync();
  }

  if (doc.readyState === 'loading') doc.addEventListener('DOMContentLoaded', setup);
  else setup();
  setTimeout(setup, 800);
})();
</script>
""", height=0)

# ── Router ────────────────────────────────────────────────────────────────────
from frontend.views import input              as input_view
from frontend.views import results            as results_view
from frontend.views import dashboard          as dashboard_view
from frontend.views import bi_dashboard       as bi_dashboard_view
from frontend.views import adaptive_planner   as adaptive_planner_view
from frontend.views import history            as history_view
from frontend.views import explainer          as explainer_view
from frontend.views import plots              as plots_view

page = st.session_state.page

if page == "home":
    _render_home()
elif page == "input":
    input_view.render()
elif page == "results":
    results_view.render()
elif page == "dashboard":
    dashboard_view.render()
elif page == "bi_dashboard":
    bi_dashboard_view.render()
elif page == "adaptive_planner":
    adaptive_planner_view.render()
elif page == "history":
    history_view.render()
elif page == "explainer":
    explainer_view.render()
elif page == "farm":
    plots_view.render()
else:
    _render_home()
