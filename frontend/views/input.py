"""Página de Input — contexto do campo, decisões e revisão."""

from __future__ import annotations
from datetime import date, datetime, timedelta
from typing import TypedDict
import calendar as _cal_mod

import streamlit as st
import streamlit.components.v1 as _stc
from frontend.navigation import go
from frontend.api import simulate


class ApiContext(TypedDict):
    c1_regiao: str
    c2_textura: str
    c3_ph: str
    c4_drenagem: str
    c5_aptidao: str
    c6_area: str
    c7_enso: str


class ApiDecisions(TypedDict):
    d1_janela: str
    d2_cultivar: str
    d3_tsi: str
    d4_densidade: str
    d5_manejo: str
    d6_tecnologia: str


def _build_calendar_html(start_iso: str, end_iso: str) -> str:
    """Calendário customizado HTML/CSS/JS — zero BaseUI."""
    s_iso = start_iso or ""
    e_iso = end_iso   or ""
    try:
        init_y, init_m = int(s_iso[:4]), int(s_iso[5:7])
    except (ValueError, IndexError):
        init_y, init_m = 2026, 10
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:transparent;padding:2px}}
.cal{{background:#fff;border:1px solid #b8dfc6;border-radius:14px;padding:14px 16px;
      box-shadow:0 4px 24px rgba(13,43,24,0.13);user-select:none;max-width:310px}}
.hdr{{display:flex;align-items:center;justify-content:space-between;margin-bottom:10px}}
.nav{{background:none;border:none;cursor:pointer;color:#1a5c38;font-size:1.3rem;
      padding:3px 10px;border-radius:6px;line-height:1;transition:background .12s}}
.nav:hover{{background:#e8f5e9}}.nav:disabled{{color:#c8e6d4;cursor:default}}
.nav:disabled:hover{{background:none}}
.title{{font-weight:700;color:#0d2b18;font-size:0.93rem}}
.grid{{display:grid;grid-template-columns:repeat(7,1fr);gap:2px}}
.dow{{text-align:center;font-size:0.6rem;font-weight:700;color:#2d8a56;
      padding:4px 0;text-transform:uppercase;letter-spacing:.05em}}
.day{{display:flex;align-items:center;justify-content:center;
      min-height:32px;min-width:32px;border-radius:50%;font-size:.82rem;
      cursor:pointer;color:#1a3a2a;background:#fff;border:none;transition:background .1s,color .1s}}
.day:not(.empty):not(.off):hover{{background:#e8f5e9;color:#0d2b18}}
.day.empty,.day.off{{cursor:default;pointer-events:none}}
.day.off{{color:rgba(45,138,86,.28)}}
.day.sel-s{{background:#1a5c38!important;color:#fff!important;font-weight:700;border-radius:50% 0 0 50%}}
.day.sel-e{{background:#1a5c38!important;color:#fff!important;font-weight:700;border-radius:0 50% 50% 0}}
.day.sel-s.sel-e{{border-radius:50%!important}}
.day.mid{{background:#e8f5e9;border-radius:0;color:#0d2b18}}
.foot{{margin-top:10px;padding-top:10px;border-top:1px solid #e8f5e9;
       font-size:.72rem;color:#4a8a6a;text-align:center;min-height:26px}}
.badge{{background:linear-gradient(135deg,#1a5c38,#2d8a56);color:#fff;border-radius:6px;
        padding:4px 10px;font-weight:600;font-size:.75rem;display:inline-block;margin-top:4px}}
</style></head><body><div class="cal">
<div class="hdr">
  <button class="nav" id="prev" onclick="nav(-1)">&#8249;</button>
  <div class="title" id="ttl"></div>
  <button class="nav" id="next" onclick="nav(1)">&#8250;</button>
</div>
<div class="grid" id="grid"></div>
<div class="foot" id="foot"></div>
</div>
<script>
const MN=['January','February','March','April','May','June','July','August','September','October','November','December'];
const DW=['Mon','Tue','Wed','Thu','Fri','Sat','Sun'];
const MINDT=new Date(2026,8,1), MAXDT=new Date(2026,11,15);
let cy={init_y}, cm={init_m}-1;
let ss=pi('{s_iso}'), se=pi('{e_iso}');
function pi(s){{if(!s||s.length<10)return null;const[y,m,d]=s.split('-').map(Number);return new Date(y,m-1,d);}}
function iso(d){{if(!d)return'';return d.getFullYear()+'-'+pad(d.getMonth()+1)+'-'+pad(d.getDate());}}
function pad(n){{return String(n).padStart(2,'0');}}
function same(a,b){{return a&&b&&a.getFullYear()===b.getFullYear()&&a.getMonth()===b.getMonth()&&a.getDate()===b.getDate();}}
function nav(d){{cm+=d;if(cm<0){{cy--;cm=11;}}if(cm>11){{cy++;cm=0;}}
  if(cy<2026||(cy===2026&&cm<8)){{cy=2026;cm=8;}}
  if(cy>2026||(cy===2026&&cm>11)){{cy=2026;cm=11;}}render();}}
function pick(y,m,d){{
  const p=new Date(y,m,d);if(p<MINDT||p>MAXDT)return;
  if(!ss||se){{ss=p;se=null;}}
  else{{if(p<ss){{se=ss;ss=p;}}else{{se=p;}}
    const diff=(se-ss)/86400000;if(diff>7)se=new Date(ss.getTime()+7*86400000);}}
  push();render();}}
function push(){{
  const doc=window.parent.document;
  const set=(ph,v)=>{{
    const inp=doc.querySelector('input[placeholder="'+ph+'"]');if(!inp)return;
    const ns=Object.getOwnPropertyDescriptor(window.parent.HTMLInputElement.prototype,'value').set;
    ns.call(inp,v);inp.dispatchEvent(new Event('input',{{bubbles:true}}));
  }};
  set('SIMCAL_S',iso(ss));set('SIMCAL_E',iso(se));
}}
function janela(d){{
  const p=new Date(2026,9,15),o=new Date(2026,10,10);
  return d<=p?'Early':d<=o?'Optimal':'Late';
}}
function render(){{
  document.getElementById('ttl').textContent=MN[cm]+' '+cy;
  document.getElementById('prev').disabled=(cy===2026&&cm===8);
  document.getElementById('next').disabled=(cy===2026&&cm===11);
  const g=document.getElementById('grid');g.innerHTML='';
  DW.forEach(d=>{{const el=document.createElement('div');el.className='dow';el.textContent=d;g.appendChild(el);}});
  const fd=new Date(cy,cm,1).getDay(),off=(fd===0)?6:fd-1;
  const dim=new Date(cy,cm+1,0).getDate();
  for(let i=0;i<off;i++){{const el=document.createElement('div');el.className='day empty';g.appendChild(el);}}
  for(let d=1;d<=dim;d++){{
    const dt=new Date(cy,cm,d);
    const el=document.createElement('div');el.textContent=d;
    const dis=dt<MINDT||dt>MAXDT;
    const cls=['day'];
    if(dis){{cls.push('off');}}else{{
      const iS=same(dt,ss),iE=same(dt,se);
      const inR=ss&&se&&dt>=ss&&dt<=se;
      if(iS)cls.push('sel-s');if(iE)cls.push('sel-e');
      if(inR&&!iS&&!iE)cls.push('mid');
      const dd=d,yy=cy,mm=cm;
      el.onclick=()=>pick(yy,mm,dd);
    }}
    el.className=cls.join(' ');g.appendChild(el);
  }}
  const ft=document.getElementById('foot');
  if(ss&&se){{
    const mid=new Date(ss.getTime()+(se-ss)/2);const j=janela(mid);
    const jc=j==='Optimal'?'#2e7d32':j==='Early'?'#f57c00':'#c62828';
    const fs=pad(ss.getDate())+'/'+MN[ss.getMonth()].substr(0,3);
    const fe=pad(se.getDate())+'/'+MN[se.getMonth()].substr(0,3);
    ft.innerHTML='<span class="badge" style="background:'+jc+'">📅 '+fs+' to '+fe+' → '+j+'</span>';
  }}else if(ss){{ft.textContent='Click to set the end of the period';}}
  else{{ft.textContent='Select the planting start date';}}
}}
render();
</script></body></html>"""

# ── Mapeamento: opções do usuário → labels internos da API ───────────────────

_C1_OPTIONS = {
    "Sorriso, Sinop, Lucas do Rio Verde":     "Favorável (Sorriso, Sinop, Lucas RV)",
    "Sapezal, Campo Novo do Parecis":         "Intermediária (Sapezal, Campo Novo)",
    "Primavera do Leste, Querência":          "Desafiadora (Primavera Leste, Querência)",
}
_C2_OPTIONS = {
    "Clay — more than 35% clay":              "Favorável (argilosa / média bem estruturada)",
    "Loam — 20 to 35% clay":                 "Intermediária (textura média)",
    "Sandy — less than 20% clay":            "Desafiadora (arenosa / baixa retenção)",
}
_C3_OPTIONS = {
    "pH between 5.5 and 6.5":               "Adequado (5,5 – 6,5)",
    "pH between 5.0–5.4 or 6.6–6.8":        "Limítrofe (5,0–5,4 ou 6,6–6,8)",
    "pH below 5.0 or above 6.8":            "Crítico (<5,0 ou >6,8)",
}
_C4_OPTIONS = {
    "No waterlogging":                       "Boa (bem drenado)",
    "With occasional flooding":              "Moderada (moderadamente/imperfeito)",
    "With frequent flooding":                "Ruim (mal / excessivamente drenado)",
}
_C5_OPTIONS = {
    "Latosol or Nitosol":                    "Alta (Latossolo, Nitossolo)",
    "Argisol or Cambisol":                   "Média (Argissolo, Cambissolo)",
    "Neosol or Gleysol":                     "Baixa (Neossolo, Gleissolo)",
}
_C6_OPTIONS = {
    "Up to 50 hectares":                     "Pequena (≤50 ha)",
    "Between 50 and 200 hectares":           "Média (50–200 ha)",
    "Above 200 hectares":                    "Grande (>200 ha)",
}
_C7_OPTIONS = {
    "El Niño — forecast of regular rainfall in MT":   "El Niño (chuva regular em MT)",
    "Neutral conditions — no defined forecast":        "Neutro",
    "La Niña — forecast of prolonged dry spells":      "La Niña (chuva concentrada/curta)",
}

_D2_OPTIONS = {
    "P98R30, NK6727 or BMX Foco (post-2020 releases)": "Alto potencial (P98R30, NK6727, BMX Foco; pós-2020)",
    "Cultivar released between 2015 and 2019":          "Intermediário (2015–2019)",
    "Cultivar released before 2015":                    "Limitado (legados pré-2015)",
}
_D6_OPTIONS = {
    "High precision — RTK, pneumatic planter":           "Alta precisão (RTK + pneumática moderna)",
    "Standard precision — controlled spacing":           "Padrão",
    "Low precision — irregular spacing":                 "Baixa (espaçamento irregular)",
}

# Limites da janela de plantio
_JANELA_PRECOCE_FIM = date(2026, 10, 15)
_JANELA_OTIMA_FIM   = date(2026, 11, 10)


def _map_janela(d: date) -> str:
    if d <= _JANELA_PRECOCE_FIM:
        return "Precoce (até 15/out)"
    if d <= _JANELA_OTIMA_FIM:
        return "Ótima (16/out – 10/nov)"
    return "Tardia (após 10/nov)"


def _map_tsi(components: list[str]) -> str:
    has_fung  = "Fungicida"   in components
    has_inoc  = "Inoculante"  in components
    has_inset = "Inseticida"  in components
    has_nemat = "Nematicida"  in components
    if has_inset and has_nemat and (has_fung or has_inoc):
        return "Premium (fung+inset+nemat+inoc)"
    if has_fung or has_inoc:
        return "Standard (fungicida + inoculante)"
    return "Sem TSI"


def _map_densidade(seeds: int) -> str:
    if seeds <= 280_000:
        return "Baixa (≤280k sementes/ha)"
    if seeds <= 340_000:
        return "Média (280k–340k)"
    return "Alta (>340k)"


def _map_manejo(n_apps: int, monitoring: bool) -> str:
    if n_apps >= 3 and monitoring:
        return "Alto (≥3 fung. + monitor ferrugem)"
    if n_apps >= 2:
        return "Padrão (2 aplicações)"
    return "Baixo (1 ou nenhuma)"


def _mid_date(start: date, end: date) -> date:
    return start + (end - start) // 2


# ── Indicador de etapas ───────────────────────────────────────────────────────

def _step_indicator(current: int) -> None:
    steps = [
        (1, "Field Context"),
        (2, "Decisions"),
        (3, "Review"),
    ]
    parts = []
    for i, (n, label) in enumerate(steps):
        if n < current:
            cls_circle = "done"; cls_item = "done"; icon = "✓"
        elif n == current:
            cls_circle = "active"; cls_item = "active"; icon = str(n)
        else:
            cls_circle = ""; cls_item = ""; icon = str(n)

        parts.append(
            f'<div class="step-item {cls_item}">'
            f'<div class="step-circle {cls_circle}">{icon}</div>'
            f'<span>{label}</span>'
            f'</div>'
        )
        if i < len(steps) - 1:
            line_cls = "done" if n < current else ""
            parts.append(f'<div class="step-line {line_cls}"></div>')

    st.markdown(
        '<div class="step-indicator">' + "".join(parts) + "</div>",
        unsafe_allow_html=True,
    )


# ── Renderização principal ────────────────────────────────────────────────────

def render() -> None:
    step = st.session_state.get("input_step", 1)

    st.markdown('<div class="page-title">New Simulation</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Soy · Mato Grosso</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    if step == 1:
        _step_indicator(1)
        _render_context_step()
    elif step == 2:
        _step_indicator(2)
        _render_decisions_step()
    else:
        _step_indicator(3)
        _render_review_step()


# ── Etapa 1: Contexto do campo ────────────────────────────────────────────────

def _render_context_step() -> None:
    st.markdown("""
    <div class="form-section">
        <div class="form-section-title">Field Context</div>
        <div class="form-section-desc">
            Enter the characteristics of your field and crop season.
            These factors determine the yield potential of the area.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("**What is the region of your farm?**")
        st.markdown('<div class="input-help">Regions with better climate and infrastructure tend to produce more.</div>', unsafe_allow_html=True)
        c1_disp = st.selectbox(
            "MT Region", list(_C1_OPTIONS.keys()),
            index=list(_C1_OPTIONS).index(st.session_state.get("c1_display", list(_C1_OPTIONS.keys())[0])),
            label_visibility="collapsed", key="sel_c1",
        )
        st.session_state.c1_display = c1_disp

        st.markdown("**What is the soil pH?**")
        st.markdown('<div class="input-help">A pH between 5.5 and 6.5 is ideal for soy. Outside this range, the plant loses efficiency in nutrient uptake.</div>', unsafe_allow_html=True)
        c3_disp = st.selectbox(
            "Soil pH", list(_C3_OPTIONS.keys()),
            index=list(_C3_OPTIONS).index(st.session_state.get("c3_display", list(_C3_OPTIONS.keys())[0])),
            label_visibility="collapsed", key="sel_c3",
        )
        st.session_state.c3_display = c3_disp

        st.markdown("**What is the soil type of the field?**")
        st.markdown('<div class="input-help">Latosols have better physical structure and drainage, promoting root development.</div>', unsafe_allow_html=True)
        c5_disp = st.selectbox(
            "Soil Type", list(_C5_OPTIONS.keys()),
            index=list(_C5_OPTIONS).index(st.session_state.get("c5_display", list(_C5_OPTIONS.keys())[0])),
            label_visibility="collapsed", key="sel_c5",
        )
        st.session_state.c5_display = c5_disp

        st.markdown("**What is the climate forecast for this season?**")
        st.markdown('<div class="input-help">The rainfall pattern during grain filling is the main climate risk factor for yield.</div>', unsafe_allow_html=True)
        c7_disp = st.selectbox(
            "Climate Forecast", list(_C7_OPTIONS.keys()),
            index=list(_C7_OPTIONS).index(st.session_state.get("c7_display", list(_C7_OPTIONS.keys())[1])),
            label_visibility="collapsed", key="sel_c7",
        )
        st.session_state.c7_display = c7_disp

    with col_b:
        st.markdown("**What is the soil texture?**")
        st.markdown('<div class="input-help">Clay soils retain more water and nutrients. Sandy soils have lower water storage capacity.</div>', unsafe_allow_html=True)
        c2_disp = st.selectbox(
            "Soil Texture", list(_C2_OPTIONS.keys()),
            index=list(_C2_OPTIONS).index(st.session_state.get("c2_display", list(_C2_OPTIONS.keys())[0])),
            label_visibility="collapsed", key="sel_c2",
        )
        st.session_state.c2_display = c2_disp

        st.markdown("**What is the drainage of the field?**")
        st.markdown('<div class="input-help">Prolonged waterlogging damages roots and can drastically reduce yield.</div>', unsafe_allow_html=True)
        c4_disp = st.selectbox(
            "Drainage", list(_C4_OPTIONS.keys()),
            index=list(_C4_OPTIONS).index(st.session_state.get("c4_display", list(_C4_OPTIONS.keys())[0])),
            label_visibility="collapsed", key="sel_c4",
        )
        st.session_state.c4_display = c4_disp

        st.markdown("**What is the size of the planted area?**")
        st.markdown('<div class="input-help">Larger areas benefit from operational scale and mechanization efficiency.</div>', unsafe_allow_html=True)
        c6_disp = st.selectbox(
            "Area", list(_C6_OPTIONS.keys()),
            index=list(_C6_OPTIONS).index(st.session_state.get("c6_display", list(_C6_OPTIONS.keys())[1])),
            label_visibility="collapsed", key="sel_c6",
        )
        st.session_state.c6_display = c6_disp

    st.markdown("<br>", unsafe_allow_html=True)
    _, col_next = st.columns([4, 1])
    with col_next:
        if st.button("Next: Decisions →", type="primary", use_container_width=True):
            st.session_state.ctx_c1 = c1_disp
            st.session_state.ctx_c2 = c2_disp
            st.session_state.ctx_c3 = c3_disp
            st.session_state.ctx_c4 = c4_disp
            st.session_state.ctx_c5 = c5_disp
            st.session_state.ctx_c6 = c6_disp
            st.session_state.ctx_c7 = c7_disp
            st.session_state.input_step = 2
            st.rerun()


# ── Etapa 2: Decisões do produtor ─────────────────────────────────────────────

def _render_decisions_step() -> None:
    st.markdown("""
    <div class="form-section">
        <div class="form-section-title">Management Decisions</div>
        <div class="form-section-desc">
            Configure how you plan to manage the season.
            The simulator will calculate the expected yield for each possible climate scenario.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Inputs ocultos para receber a seleção do calendário JS ──────────────────
    # O calendário (iframe) encontra estes inputs pelo placeholder e dispara
    # eventos React sintéticos para que o Streamlit capture os novos valores.
    if "d1_cal_s" not in st.session_state:
        st.session_state["d1_cal_s"] = "2026-10-20"
    if "d1_cal_e" not in st.session_state:
        st.session_state["d1_cal_e"] = "2026-10-22"

    _hc1, _hc2 = st.columns(2)
    with _hc1:
        st.text_input("_cs", placeholder="SIMCAL_S", key="d1_cal_s", label_visibility="collapsed")
    with _hc2:
        st.text_input("_ce", placeholder="SIMCAL_E", key="d1_cal_e", label_visibility="collapsed")

    # Esconde os inputs mas mantém no DOM para o JS encontrá-los
    st.markdown("""<style>
input[placeholder="SIMCAL_S"], input[placeholder="SIMCAL_E"] {
  position:absolute!important;opacity:0!important;
  height:1px!important;width:1px!important;pointer-events:none!important;
}
div:has(>div>div>input[placeholder="SIMCAL_S"]),
div:has(>div>div>input[placeholder="SIMCAL_E"]) {
  height:0!important;overflow:hidden!important;padding:0!important;margin:0!important;
}
</style>""", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:
        # D1 Planting Window — custom HTML calendar
        st.markdown("**When do you plan to plant?**")
        st.markdown(
            '<div class="input-help">Optimal window: Oct 16 to Nov 10. Click for start, click again for end (max. 7 days).</div>',
            unsafe_allow_html=True,
        )

        _s_iso = st.session_state.get("d1_cal_s") or "2026-10-20"
        _e_iso = st.session_state.get("d1_cal_e") or "2026-10-22"
        _stc.html(_build_calendar_html(_s_iso, _e_iso), height=340, scrolling=False)

        try:
            d1_start = date.fromisoformat(_s_iso)
        except ValueError:
            d1_start = date(2026, 10, 20)
        try:
            d1_end = date.fromisoformat(_e_iso)
        except ValueError:
            d1_end = d1_start

        if d1_end < d1_start:
            d1_end = d1_start

        d1_mid    = _mid_date(d1_start, d1_end)
        d1_janela = _map_janela(d1_mid)
        st.session_state.d1_date_start = d1_start
        st.session_state.d1_date_end   = d1_end

        # D3 TSI — multi-select
        st.markdown("<br>**Which seed treatment components will you use?**", unsafe_allow_html=True)
        st.markdown(
            '<div class="input-help">The premium treatment (fungicide + insecticide + nematicide + inoculant) protects the seed and improves initial stand.</div>',
            unsafe_allow_html=True,
        )
        d3_comps = st.multiselect(
            "Seed Treatment Components",
            ["Fungicida", "Inoculante", "Inseticida", "Nematicida"],
            default=st.session_state.get("d3_comps", ["Fungicida", "Inoculante"]),
            label_visibility="collapsed",
            key="d3_ms",
        )
        st.session_state.d3_comps = d3_comps
        d3_tsi   = _map_tsi(d3_comps)
        d3_color = "#2e7d32" if "Premium" in d3_tsi else "#f57c00" if "Standard" in d3_tsi else "#c62828"
        st.markdown(
            f'<div style="font-size:0.78rem;font-weight:600;color:{d3_color};margin-top:4px">→ {d3_tsi}</div>',
            unsafe_allow_html=True,
        )

        # D5 Disease Management
        st.markdown("<br>**How many fungicide applications are you planning?**", unsafe_allow_html=True)
        st.markdown(
            '<div class="input-help">3 or more applications with active Asian rust monitoring represents the most intensive management.</div>',
            unsafe_allow_html=True,
        )
        d5_apps = st.select_slider(
            "Fungicide applications",
            options=[0, 1, 2, 3, 4],
            value=st.session_state.get("d5_apps", 2),
            label_visibility="collapsed",
            key="d5_apps_sl",
        )
        st.session_state.d5_apps = d5_apps
        d5_monitor = st.checkbox(
            "Active Asian rust monitoring",
            value=st.session_state.get("d5_monitor", False),
            key="d5_mon_cb",
        )
        st.session_state.d5_monitor = d5_monitor
        d5_manejo = _map_manejo(d5_apps, d5_monitor)
        d5_color  = "#2e7d32" if "Alto" in d5_manejo else "#f57c00" if "Padrão" in d5_manejo else "#c62828"
        st.markdown(
            f'<div style="font-size:0.78rem;font-weight:600;color:{d5_color};margin-top:4px">→ {d5_manejo}</div>',
            unsafe_allow_html=True,
        )

    with col_b:
        # D2 Cultivar
        st.markdown("**Which cultivar will you use?**")
        st.markdown(
            '<div class="input-help">Cultivars released after 2020 have genetics more responsive to inputs and better disease resistance.</div>',
            unsafe_allow_html=True,
        )
        d2_disp = st.selectbox(
            "Cultivar", list(_D2_OPTIONS.keys()),
            index=list(_D2_OPTIONS).index(st.session_state.get("d2_display", list(_D2_OPTIONS.keys())[0])),
            label_visibility="collapsed", key="sel_d2",
        )
        st.session_state.d2_display = d2_disp

        # D4 Seeding Density
        st.markdown("<br>**What will the seeding density be?**", unsafe_allow_html=True)
        st.markdown(
            '<div class="input-help">Recommended range: 280 to 340 thousand viable seeds per hectare.</div>',
            unsafe_allow_html=True,
        )
        d4_seeds = st.number_input(
            "Seeds/ha",
            min_value=150_000, max_value=500_000,
            value=st.session_state.get("d4_seeds", 300_000),
            step=5_000,
            label_visibility="collapsed",
            key="d4_ni",
        )
        st.session_state.d4_seeds = d4_seeds
        d4_densidade = _map_densidade(d4_seeds)
        d4_color     = "#2e7d32" if "Média" in d4_densidade else "#f57c00"
        st.markdown(
            f'<div style="font-size:0.78rem;font-weight:600;color:{d4_color};margin-top:4px">'
            f'{d4_seeds:,} seeds/ha → {d4_densidade.split(" (")[0].strip()}</div>',
            unsafe_allow_html=True,
        )

        # D6 Planting Technology
        st.markdown("<br>**What is the capability of your planter?**", unsafe_allow_html=True)
        st.markdown(
            '<div class="input-help">Precision in seed placement and uniform spacing impact stand and inter-plant competition.</div>',
            unsafe_allow_html=True,
        )
        d6_disp = st.selectbox(
            "Planting Technology", list(_D6_OPTIONS.keys()),
            index=list(_D6_OPTIONS).index(st.session_state.get("d6_display", list(_D6_OPTIONS.keys())[1])),
            label_visibility="collapsed", key="sel_d6",
        )
        st.session_state.d6_display = d6_disp

    st.markdown("<br>", unsafe_allow_html=True)
    col_back, _, col_next = st.columns([1, 3, 1])
    with col_back:
        if st.button("← Context", use_container_width=True):
            st.session_state.input_step = 1
            st.rerun()
    with col_next:
        if st.button("Review →", type="primary", use_container_width=True):
            st.session_state.dec_d1_start    = d1_start
            st.session_state.dec_d1_end      = d1_end
            st.session_state.dec_d1_mid      = d1_mid
            st.session_state.dec_d1_janela   = d1_janela
            st.session_state.dec_d2_display  = d2_disp
            st.session_state.dec_d3_comps    = d3_comps
            st.session_state.dec_d3_tsi      = d3_tsi
            st.session_state.dec_d4_seeds    = d4_seeds
            st.session_state.dec_d4_densidade= d4_densidade
            st.session_state.dec_d5_apps     = d5_apps
            st.session_state.dec_d5_monitor  = d5_monitor
            st.session_state.dec_d5_manejo   = d5_manejo
            st.session_state.dec_d6_display  = d6_disp
            st.session_state.input_step      = 3
            st.rerun()


# ── Etapa 3: Revisão ──────────────────────────────────────────────────────────

def _render_review_step() -> None:
    c1 = st.session_state.get("ctx_c1", "")
    c2 = st.session_state.get("ctx_c2", "")
    c3 = st.session_state.get("ctx_c3", "")
    c4 = st.session_state.get("ctx_c4", "")
    c5 = st.session_state.get("ctx_c5", "")
    c6 = st.session_state.get("ctx_c6", "")
    c7 = st.session_state.get("ctx_c7", "")

    d1_start    = st.session_state.get("dec_d1_start",    date(2026, 10, 20))
    d1_end      = st.session_state.get("dec_d1_end",      date(2026, 10, 22))
    d1_mid      = st.session_state.get("dec_d1_mid",      _mid_date(d1_start, d1_end))
    d1_janela   = st.session_state.get("dec_d1_janela",   _map_janela(d1_mid))
    d2_disp     = st.session_state.get("dec_d2_display",  "")
    d3_comps    = st.session_state.get("dec_d3_comps",    [])
    d3_tsi      = st.session_state.get("dec_d3_tsi",      "")
    d4_seeds    = st.session_state.get("dec_d4_seeds",    300_000)
    d4_densidade= st.session_state.get("dec_d4_densidade","")
    d5_apps     = st.session_state.get("dec_d5_apps",     2)
    d5_monitor  = st.session_state.get("dec_d5_monitor",  False)
    d5_manejo   = st.session_state.get("dec_d5_manejo",   "")
    d6_disp     = st.session_state.get("dec_d6_display",  "")

    period_str = (
        f"{d1_start.strftime('%d/%b').lower()} a {d1_end.strftime('%d/%b').lower()}"
        if d1_start != d1_end else d1_start.strftime("%d/%b/%Y").lower()
    )

    st.markdown("""
    <div class="form-section">
        <div class="form-section-title">Review & Confirm</div>
        <div class="form-section-desc">
            Check all data before running the simulation.
            If you need to correct any item, go back to the corresponding step.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_ctx, col_dec = st.columns(2)

    with col_ctx:
        st.markdown('<div class="review-section-label">Field Context</div>', unsafe_allow_html=True)
        rows_ctx = [
            ("Region",              c1),
            ("Soil Texture",        c2),
            ("Soil pH",             c3),
            ("Drainage",            c4),
            ("Soil Type",           c5),
            ("Planted Area",        c6),
            ("Climate Forecast",    c7),
        ]
        html = '<div class="review-card">'
        for k, v in rows_ctx:
            html += f'<div class="review-row"><span class="review-key">{k}</span><span class="review-val">{v}</span></div>'
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)

    with col_dec:
        st.markdown('<div class="review-section-label">Management Decisions</div>', unsafe_allow_html=True)
        d5_summary = f"{d5_apps} application{'s' if d5_apps != 1 else ''}"
        if d5_monitor:
            d5_summary += " + monitoring"
        rows_dec = [
            ("Planting Period",      f"{period_str} → {d1_janela.split('(')[0].strip()}"),
            ("Cultivar",             d2_disp),
            ("Seed Treatment",       f"{', '.join(d3_comps) if d3_comps else 'None'} → {d3_tsi.split(' (')[0]}"),
            ("Density",              f"{d4_seeds:,} seeds/ha → {d4_densidade.split(' (')[0].strip()}"),
            ("Disease Management",   f"{d5_summary} → {d5_manejo.split(' (')[0].strip()}"),
            ("Planter",              d6_disp),
        ]
        html = '<div class="review-card">'
        for k, v in rows_dec:
            html += f'<div class="review-row"><span class="review-key">{k}</span><span class="review-val">{v}</span></div>'
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_back_ctx, col_back_dec, _, col_run = st.columns([1, 1, 2, 2])

    with col_back_ctx:
        if st.button("← Context", use_container_width=True):
            st.session_state.input_step = 1
            st.rerun()
    with col_back_dec:
        if st.button("← Decisions", use_container_width=True):
            st.session_state.input_step = 2
            st.rerun()
    with col_run:
        if st.button("Confirm & Simulate →", type="primary", use_container_width=True):
            _run_simulation(
                c1, c2, c3, c4, c5, c6, c7,
                d1_janela, d2_disp, d3_tsi,
                d4_densidade, d5_manejo, d6_disp,
                d1_start, d1_end, d1_mid, d3_comps, d4_seeds, d5_apps, d5_monitor,
            )


def _build_api_context(
    c1_disp: str, c2_disp: str, c3_disp: str, c4_disp: str,
    c5_disp: str, c6_disp: str, c7_disp: str,
) -> ApiContext:
    return ApiContext(
        c1_regiao=_C1_OPTIONS[c1_disp],
        c2_textura=_C2_OPTIONS[c2_disp],
        c3_ph=_C3_OPTIONS[c3_disp],
        c4_drenagem=_C4_OPTIONS[c4_disp],
        c5_aptidao=_C5_OPTIONS[c5_disp],
        c6_area=_C6_OPTIONS[c6_disp],
        c7_enso=_C7_OPTIONS[c7_disp],
    )


def _build_api_decisions(
    d1_janela: str, d2_disp: str, d3_tsi: str,
    d4_densidade: str, d5_manejo: str, d6_disp: str,
) -> ApiDecisions:
    return ApiDecisions(
        d1_janela=d1_janela,
        d2_cultivar=_D2_OPTIONS[d2_disp],
        d3_tsi=d3_tsi,
        d4_densidade=d4_densidade,
        d5_manejo=d5_manejo,
        d6_tecnologia=_D6_OPTIONS[d6_disp],
    )


def _build_display_dict(
    c1_disp: str, c2_disp: str, c3_disp: str, c4_disp: str,
    c5_disp: str, c6_disp: str, c7_disp: str,
    d1_janela: str, d1_start: date, d1_end: date,
    d2_disp: str, d3_tsi: str, d3_comps: list,
    d4_seeds: int, d5_manejo: str, d5_apps: int, d5_monitor: bool,
    d6_disp: str,
) -> dict:
    d5_summary = f"{d5_apps} application{'s' if d5_apps != 1 else ''}"
    if d5_monitor:
        d5_summary += " + monitoring"
    period_str = (
        f"{d1_start.strftime('%d/%m')} to {d1_end.strftime('%d/%m')}"
        if d1_start != d1_end else d1_start.strftime("%d/%m")
    )
    return {
        "Region":              c1_disp,
        "Texture":             c2_disp,
        "pH":                  c3_disp,
        "Drainage":            c4_disp,
        "Soil Type":           c5_disp,
        "Area":                c6_disp,
        "Climate Forecast":    c7_disp,
        "Planting Period":     f"{period_str} → {d1_janela.split('(')[0].strip()}",
        "Cultivar":            d2_disp,
        "Seed Treatment":      f"{', '.join(d3_comps) or 'None'} → {d3_tsi.split(' (')[0]}",
        "Density":             f"{d4_seeds:,} seeds/ha",
        "Disease Management":  d5_summary,
        "Planter":             d6_disp,
    }


def _save_to_history(
    context: ApiContext, decisions: ApiDecisions, display: dict,
    result: dict, c1_disp: str, d2_disp: str,
) -> None:
    history = st.session_state.get("sim_history", [])
    region_short   = c1_disp.split(",")[0].strip() if c1_disp else "—"
    cultivar_short = d2_disp.split(",")[0].strip()[:20] if d2_disp else "—"
    history.append({
        "id":        len(history) + 1,
        "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "summary":   f"{region_short} · {cultivar_short}",
        "display":   display,
        "context":   context,
        "decisions": decisions,
        "result":    result,
    })
    st.session_state.sim_history = history


def _run_simulation(
    c1_disp, c2_disp, c3_disp, c4_disp, c5_disp, c6_disp, c7_disp,
    d1_janela, d2_disp, d3_tsi, d4_densidade, d5_manejo, d6_disp,
    d1_start, d1_end, d1_mid, d3_comps, d4_seeds, d5_apps, d5_monitor,
) -> None:
    context   = _build_api_context(c1_disp, c2_disp, c3_disp, c4_disp, c5_disp, c6_disp, c7_disp)
    decisions = _build_api_decisions(d1_janela, d2_disp, d3_tsi, d4_densidade, d5_manejo, d6_disp)

    with st.spinner("Running your simulation…"):
        result = simulate(context, decisions)

    if result:
        display = _build_display_dict(
            c1_disp, c2_disp, c3_disp, c4_disp, c5_disp, c6_disp, c7_disp,
            d1_janela, d1_start, d1_end,
            d2_disp, d3_tsi, d3_comps,
            d4_seeds, d5_manejo, d5_apps, d5_monitor, d6_disp,
        )
        st.session_state.sim_result    = result
        st.session_state.sim_context   = context
        st.session_state.sim_decisions = decisions
        st.session_state.sim_display   = display
        _save_to_history(context, decisions, display, result, c1_disp, d2_disp)
        st.session_state.input_step = 1
        go("results")
