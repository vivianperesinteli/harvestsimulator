"""My Fields — manage farm plots and compare simulations across fields."""

from __future__ import annotations
import streamlit as st
import plotly.graph_objects as go

from frontend.navigation import go as navigate
from frontend.plots_store import load_plots, save_plot, delete_plot, add_simulation, update_plot

# ── Labels ────────────────────────────────────────────────────────────────────
_L = {
    "en": {
        "title":            "My Fields",
        "subtitle":         "Register your plots · Run simulations per field · Compare results",
        "no_plots":         "No fields registered yet. Add your first field using the form below.",
        "fields_title":     "Your Fields",
        "area_label":       "{area} ha",
        "last_ev":          "{ev} sc/ha",
        "no_sim":           "No simulations yet",
        "num_sims":         "{n} sim(s)",
        "btn_simulate":     "Simulate →",
        "btn_edit":         "Edit",
        "btn_history":      "History",
        "btn_delete":       "Remove",
        "deleted_ok":       "Field removed.",
        "chart_title":      "Expected Yield by Field",
        "chart_axis":       "Expected yield (sc/ha)",
        "chart_ref":        "MT reference — {ref} sc/ha",
        "add_title":        "＋ Add New Field",
        "add_name_label":   "Field name",
        "add_name_ph":      "e.g. North Block, South Area, Field B…",
        "add_area_label":   "Total area (hectares)",
        "add_ctx_title":    "Permanent field conditions",
        "add_ctx_note":     "Fixed field characteristics. The climate forecast (ENSO) is set per simulation run.",
        "add_region":       "Region (MT)",
        "add_texture":      "Soil Texture",
        "add_ph":           "Soil pH",
        "add_drainage":     "Drainage",
        "add_soil_type":    "Soil Aptitude",
        "add_field_size":   "Field Size Category",
        "add_btn":          "Save Field",
        "add_ok":           "Field \"{nome}\" saved!",
        "add_warn":         "Please enter a field name before saving.",
        "edit_title":       "Edit field",
        "edit_btn":         "Save changes",
        "edit_ok":          "Field updated.",
        "save_hdr":         "💾 Save current simulation to a field",
        "save_select":      "Choose a field",
        "save_btn":         "Save to this field",
        "save_ok":          "Simulation saved to \"{nome}\".",
        "save_no_plots":    "No fields registered yet — add one below.",
        "prefill_note":     "Field pre-filled from: {nome}. You can still change the climate forecast (ENSO).",
        "health_label":     "Soil health",
        "vs_ref":           "{sign}{delta:.1f} vs. ref",
        "trend_up":         "↗ trending up",
        "trend_down":       "↘ trending down",
        "trend_flat":       "→ stable",
        "bags_field":       "≈ {bags:,.0f} bags",
        "hist_title":       "Simulation history — {nome}",
        "hist_ev_label":    "EV (sc/ha)",
        "soil_region":      "Region",
        "soil_texture":     "Texture",
        "soil_ph":          "pH",
        "soil_drainage":    "Drainage",
        "soil_aptitude":    "Aptitude",
        "total_area":       "Total Area",
        "num_fields":       "Fields",
        "avg_yield":        "Farm Avg. EV",
        "total_bags":       "Projected Bags",
        "hero_title":       "Your farm, season by season",
        "hero_sub":         "Select a field to simulate or view its history.",
        "mosaic_sub":       "Tile size = area · color = EV vs. MT reference",
        "manage_lbl":       "Manage →",
        "enso_panel_title": "Climate Profile · ENSO",
        "total_bags_lbl":   "Total projected bags",
        "avg_yield_lbl":    "Farm avg. EV",
        "sims_done_lbl":    "{n} of {total} fields simulated",
        "climate_label":    "Climate",
        "hero_vs_ref":      "vs 24/25 ref",
        "fields_detail_sub":"Per-field context, history and actions",
        "mosaic_title":     "Field Mosaic",
        "no_sim_label":     "No sim",
    },
    "pt": {
        "title":            "Meus Talhões",
        "subtitle":         "Cadastre seus talhões · Rode simulações por área · Compare resultados",
        "no_plots":         "Nenhum talhão cadastrado ainda. Adicione o primeiro usando o formulário abaixo.",
        "fields_title":     "Seus Talhões",
        "area_label":       "{area} ha",
        "last_ev":          "{ev} sc/ha",
        "no_sim":           "Ainda não simulado",
        "num_sims":         "{n} sim(ões)",
        "btn_simulate":     "Simular →",
        "btn_edit":         "Editar",
        "btn_history":      "Histórico",
        "btn_delete":       "Remover",
        "deleted_ok":       "Talhão removido.",
        "chart_title":      "Produtividade Esperada por Talhão",
        "chart_axis":       "Produtividade esperada (sc/ha)",
        "chart_ref":        "Referência MT — {ref} sc/ha",
        "add_title":        "＋ Adicionar Talhão",
        "add_name_label":   "Nome do talhão",
        "add_name_ph":      "ex: Talhão Norte, Área Sul, Bloco B…",
        "add_area_label":   "Área total (hectares)",
        "add_ctx_title":    "Condições permanentes do campo",
        "add_ctx_note":     "Características fixas do talhão. A previsão climática (ENSO) é definida por simulação.",
        "add_region":       "Região (MT)",
        "add_texture":      "Textura do Solo",
        "add_ph":           "pH do Solo",
        "add_drainage":     "Drenagem",
        "add_soil_type":    "Aptidão do Solo",
        "add_field_size":   "Categoria de Tamanho",
        "add_btn":          "Salvar Talhão",
        "add_ok":           "Talhão \"{nome}\" salvo!",
        "add_warn":         "Informe o nome do talhão antes de salvar.",
        "edit_title":       "Editar talhão",
        "edit_btn":         "Salvar alterações",
        "edit_ok":          "Talhão atualizado.",
        "save_hdr":         "💾 Salvar simulação atual em um talhão",
        "save_select":      "Escolha um talhão",
        "save_btn":         "Salvar neste talhão",
        "save_ok":          "Simulação salva em \"{nome}\".",
        "save_no_plots":    "Nenhum talhão cadastrado ainda — adicione um abaixo.",
        "prefill_note":     "Entradas pré-preenchidas do talhão: {nome}.",
        "health_label":     "Saúde do solo",
        "vs_ref":           "{sign}{delta:.1f} vs. ref.",
        "trend_up":         "↗ crescente",
        "trend_down":       "↘ declínio",
        "trend_flat":       "→ estável",
        "bags_field":       "≈ {bags:,.0f} sacas",
        "hist_title":       "Histórico de simulações — {nome}",
        "hist_ev_label":    "EV (sc/ha)",
        "soil_region":      "Região",
        "soil_texture":     "Textura",
        "soil_ph":          "pH",
        "soil_drainage":    "Drenagem",
        "soil_aptitude":    "Aptidão",
        "total_area":       "Área Total",
        "num_fields":       "Talhões",
        "avg_yield":        "EV Médio da Fazenda",
        "total_bags":       "Sacas Projetadas",
        "hero_title":       "Sua fazenda, safra a safra",
        "hero_sub":         "Selecione um talhão para simular ou ver o histórico.",
        "mosaic_sub":       "Tamanho = área · cor = EV vs. referência MT",
        "manage_lbl":       "Gerir →",
        "enso_panel_title": "Perfil de Chuva · ENSO",
        "total_bags_lbl":   "Sacas totais projetadas",
        "avg_yield_lbl":    "EV médio da fazenda",
        "sims_done_lbl":    "{n} de {total} talhões simulados",
        "climate_label":    "Clima",
        "hero_vs_ref":      "vs ref 24/25",
        "fields_detail_sub":"Contexto, histórico e ações por talhão",
        "mosaic_title":     "Mosaico de Talhões",
        "no_sim_label":     "Sem sim",
    },
}

# ── Context option maps (display → API value) ─────────────────────────────────
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
    "pH 5.5 – 6.5 (ideal range)":            "Adequado (5,5 – 6,5)",
    "pH 5.0–5.4 or 6.6–6.8 (borderline)":   "Limítrofe (5,0–5,4 ou 6,6–6,8)",
    "pH below 5.0 or above 6.8 (critical)":  "Crítico (<5,0 ou >6,8)",
}
_C4_OPTIONS = {
    "Well drained — no waterlogging":         "Boa (bem drenado)",
    "Moderate drainage — occasional flooding":"Moderada (moderadamente/imperfeito)",
    "Poor drainage — frequent flooding":      "Ruim (mal / excessivamente drenado)",
}
_C5_OPTIONS = {
    "High aptitude — Latosol or Nitosol":     "Alta (Latossolo, Nitossolo)",
    "Medium aptitude — Argisol or Cambisol":  "Média (Argissolo, Cambissolo)",
    "Low aptitude — Neosol or Gleysol":       "Baixa (Neossolo, Gleissolo)",
}
_C6_OPTIONS = {
    "Small — up to 50 hectares":              "Pequena (≤50 ha)",
    "Medium — 50 to 200 hectares":            "Média (50–200 ha)",
    "Large — above 200 hectares":             "Grande (>200 ha)",
}

# Reverse maps for display
_C1_REV = {v: k for k, v in _C1_OPTIONS.items()}
_C2_REV = {v: k for k, v in _C2_OPTIONS.items()}
_C3_REV = {v: k for k, v in _C3_OPTIONS.items()}
_C4_REV = {v: k for k, v in _C4_OPTIONS.items()}
_C5_REV = {v: k for k, v in _C5_OPTIONS.items()}
_C6_REV = {v: k for k, v in _C6_OPTIONS.items()}

_MT_BASELINE = 60.0

_C_QUALITY = {
    "c1_regiao":   {"Favorável (Sorriso, Sinop, Lucas RV)": "optimal", "Intermediária (Sapezal, Campo Novo)": "neutral", "Desafiadora (Primavera Leste, Querência)": "critical"},
    "c2_textura":  {"Favorável (argilosa / média bem estruturada)": "optimal", "Intermediária (textura média)": "neutral", "Desafiadora (arenosa / baixa retenção)": "critical"},
    "c3_ph":       {"Adequado (5,5 – 6,5)": "optimal", "Limítrofe (5,0–5,4 ou 6,6–6,8)": "neutral", "Crítico (<5,0 ou >6,8)": "critical"},
    "c4_drenagem": {"Boa (bem drenado)": "optimal", "Moderada (moderadamente/imperfeito)": "neutral", "Ruim (mal / excessivamente drenado)": "critical"},
    "c5_aptidao":  {"Alta (Latossolo, Nitossolo)": "optimal", "Média (Argissolo, Cambissolo)": "neutral", "Baixa (Neossolo, Gleissolo)": "critical"},
}
_Q_COLOR = {"optimal": "#2e7d32", "neutral": "#f57c00", "critical": "#c62828"}
_Q_ICON  = {"optimal": "🟢", "neutral": "🟡", "critical": "🔴"}

_ENSO_MAP = {
    "El Niño (chuva regular em MT)": {
        "short_en": "El Niño", "short_pt": "El Niño",
        "oni": "+1.1", "dot": "#1565c0",
        "desc_en": "Regular rainfall forecast across MT. Optimal planting window extends into November.",
        "desc_pt": "Chuvas regulares em todo MT. Janela de plantio estende-se até novembro.",
    },
    "Neutro": {
        "short_en": "Neutral", "short_pt": "Neutro",
        "oni": "0.0", "dot": "#9e9e9e",
        "desc_en": "No defined ENSO signal. Standard seasonal variability expected for MT.",
        "desc_pt": "Sem sinal ENSO definido. Variabilidade sazonal padrão esperada.",
    },
    "La Niña (chuva concentrada/curta)": {
        "short_en": "La Niña", "short_pt": "La Niña",
        "oni": "−0.9", "dot": "#e65100",
        "desc_en": "Concentrated rainfall, risk of dry spells in Jan–Feb. October planting favored.",
        "desc_pt": "Chuvas concentradas, risco de veranico em jan-fev. Janela de outubro favorecida.",
    },
}


def _soil_health(context: dict) -> tuple[str, str]:
    vals = [_C_QUALITY.get(k, {}).get(context.get(k, ""), "neutral") for k in _C_QUALITY]
    if "critical" in vals:
        return _Q_ICON["critical"], _Q_COLOR["critical"]
    if vals.count("optimal") >= 3:
        return _Q_ICON["optimal"], _Q_COLOR["optimal"]
    return _Q_ICON["neutral"], _Q_COLOR["neutral"]


def _sim_trend(sims: list) -> str:
    if len(sims) < 2:
        return "flat"
    delta = sims[-1]["ev_simulated"] - sims[-2]["ev_simulated"]
    if delta > 0.5:
        return "up"
    if delta < -0.5:
        return "down"
    return "flat"


def _soil_badges_html(context: dict, lbl: dict) -> str:
    badges = ""
    cond_labels = {
        "c1_regiao":   lbl["soil_region"],
        "c2_textura":  lbl["soil_texture"],
        "c3_ph":       lbl["soil_ph"],
        "c4_drenagem": lbl["soil_drainage"],
    }
    for key, label in cond_labels.items():
        quality = _C_QUALITY.get(key, {}).get(context.get(key, ""), "neutral")
        dot_color = _Q_COLOR[quality]
        badges += (
            f'<span style="display:inline-flex;align-items:center;gap:3px;'
            f'font-size:0.62rem;color:#4a4a6a;margin-right:6px">'
            f'<span style="width:7px;height:7px;border-radius:50%;background:{dot_color};'
            f'flex-shrink:0;display:inline-block"></span>{label}</span>'
        )
    return badges


def _render_sim_history(plot: dict, lbl: dict) -> None:
    sims = plot.get("simulations", [])
    if not sims:
        return

    evs   = [s["ev_simulated"] for s in sims]
    dates = [s.get("timestamp", f"#{i+1}")[:10] for i, s in enumerate(sims)]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(1, len(sims) + 1)),
        y=evs,
        mode="lines+markers",
        line=dict(color="#1a5c38", width=2),
        marker=dict(size=7, color="#1a5c38"),
        text=dates,
        hovertemplate="%{text}: %{y:.1f} sc/ha<extra></extra>",
    ))
    fig.add_hline(
        y=_MT_BASELINE, line_color="#f57c00", line_dash="dot", line_width=1.2,
        annotation_text=f"Ref {_MT_BASELINE:.0f}",
        annotation_font_size=7, annotation_font_color="#b35c00",
        annotation_position="right",
    )
    fig.update_layout(
        height=140,
        margin=dict(t=6, l=0, r=36, b=20),
        xaxis=dict(showgrid=False, tickvals=list(range(1, len(sims) + 1)),
                   ticktext=[str(i) for i in range(1, len(sims) + 1)],
                   tickfont=dict(size=8)),
        yaxis=dict(showgrid=True, gridcolor="#e8f5e9", tickfont=dict(size=8),
                   title=dict(text=lbl["hist_ev_label"], font=dict(size=8))),
        plot_bgcolor="#f4faf7", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=8, color="#1a3a2a"),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    for i, s in enumerate(reversed(sims), start=1):
        enso = s.get("c7_enso", "—")
        rp   = s.get("risk_profile", "—")
        st.markdown(
            f'<div style="font-size:0.7rem;color:#3a3a5c;padding:3px 0;border-bottom:1px solid #f0f0f0">'
            f'<strong>#{len(sims)-i+1}</strong> — {s["ev_simulated"]:.1f} sc/ha'
            f'<span style="color:#9e9e9e;margin-left:8px">{enso} · {rp}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )


def _render_edit_form(plot: dict, user_id: str, lbl: dict, lang: str) -> None:
    """Inline edit form for a field."""
    ctx = plot.get("context", {})

    with st.form(key=f"edit_form_{plot['id']}"):
        st.markdown(f"**{lbl['edit_title']}: {plot['nome']}**")

        col_a, col_b = st.columns(2)
        with col_a:
            nome_ed = st.text_input(lbl["add_name_label"], value=plot["nome"])
        with col_b:
            area_ed = st.number_input(
                lbl["add_area_label"],
                min_value=1.0, max_value=50_000.0,
                value=float(plot["area_ha"]), step=10.0,
            )

        st.markdown(f"**{lbl['add_ctx_title']}**")
        st.caption(lbl["add_ctx_note"])

        ec1, ec2 = st.columns(2)
        with ec1:
            c1_cur = _C1_REV.get(ctx.get("c1_regiao", ""), list(_C1_OPTIONS.keys())[0])
            c1_sel = st.selectbox(lbl["add_region"],     list(_C1_OPTIONS.keys()),
                                  index=list(_C1_OPTIONS.keys()).index(c1_cur) if c1_cur in _C1_OPTIONS else 0,
                                  key=f"ec1_{plot['id']}")
            c3_cur = _C3_REV.get(ctx.get("c3_ph", ""), list(_C3_OPTIONS.keys())[0])
            c3_sel = st.selectbox(lbl["add_ph"],         list(_C3_OPTIONS.keys()),
                                  index=list(_C3_OPTIONS.keys()).index(c3_cur) if c3_cur in _C3_OPTIONS else 0,
                                  key=f"ec3_{plot['id']}")
            c5_cur = _C5_REV.get(ctx.get("c5_aptidao", ""), list(_C5_OPTIONS.keys())[0])
            c5_sel = st.selectbox(lbl["add_soil_type"],  list(_C5_OPTIONS.keys()),
                                  index=list(_C5_OPTIONS.keys()).index(c5_cur) if c5_cur in _C5_OPTIONS else 0,
                                  key=f"ec5_{plot['id']}")
        with ec2:
            c2_cur = _C2_REV.get(ctx.get("c2_textura", ""), list(_C2_OPTIONS.keys())[0])
            c2_sel = st.selectbox(lbl["add_texture"],    list(_C2_OPTIONS.keys()),
                                  index=list(_C2_OPTIONS.keys()).index(c2_cur) if c2_cur in _C2_OPTIONS else 0,
                                  key=f"ec2_{plot['id']}")
            c4_cur = _C4_REV.get(ctx.get("c4_drenagem", ""), list(_C4_OPTIONS.keys())[0])
            c4_sel = st.selectbox(lbl["add_drainage"],   list(_C4_OPTIONS.keys()),
                                  index=list(_C4_OPTIONS.keys()).index(c4_cur) if c4_cur in _C4_OPTIONS else 0,
                                  key=f"ec4_{plot['id']}")
            c6_cur = _C6_REV.get(ctx.get("c6_area", ""), list(_C6_OPTIONS.keys())[0])
            c6_sel = st.selectbox(lbl["add_field_size"], list(_C6_OPTIONS.keys()),
                                  index=list(_C6_OPTIONS.keys()).index(c6_cur) if c6_cur in _C6_OPTIONS else 0,
                                  key=f"ec6_{plot['id']}")

        save_col, cancel_col, _ = st.columns([2, 2, 4])
        with save_col:
            submitted = st.form_submit_button(lbl["edit_btn"], type="primary", use_container_width=True)
        with cancel_col:
            cancelled = st.form_submit_button("Cancel" if lang == "en" else "Cancelar", use_container_width=True)

    if submitted:
        new_ctx = {
            "c1_regiao":  _C1_OPTIONS[c1_sel],
            "c2_textura": _C2_OPTIONS[c2_sel],
            "c3_ph":      _C3_OPTIONS[c3_sel],
            "c4_drenagem":_C4_OPTIONS[c4_sel],
            "c5_aptidao": _C5_OPTIONS[c5_sel],
            "c6_area":    _C6_OPTIONS[c6_sel],
        }
        update_plot(plot["id"], nome_ed.strip() or plot["nome"], area_ed, new_ctx)
        st.session_state[f"_edit_open_{plot['id']}"] = False
        st.success(lbl["edit_ok"])
        st.rerun()
    elif cancelled:
        st.session_state[f"_edit_open_{plot['id']}"] = False
        st.rerun()


def _render_add_form(user_id: str, lbl: dict, lang: str) -> None:
    """Inline form for adding a new field — usable standalone or inside an expander."""
    nome_input = st.text_input(
        lbl["add_name_label"],
        placeholder=lbl["add_name_ph"],
        key="add_plot_nome",
    )
    area_input = st.number_input(
        lbl["add_area_label"],
        min_value=1.0, max_value=50_000.0, value=100.0, step=10.0,
        key="add_plot_area",
    )

    st.markdown(f"**{lbl['add_ctx_title']}**")
    st.caption(lbl["add_ctx_note"])

    ca, cb = st.columns(2)
    with ca:
        c1_sel = st.selectbox(lbl["add_region"],     list(_C1_OPTIONS.keys()), key="add_c1")
        c3_sel = st.selectbox(lbl["add_ph"],         list(_C3_OPTIONS.keys()), key="add_c3")
        c5_sel = st.selectbox(lbl["add_soil_type"],  list(_C5_OPTIONS.keys()), key="add_c5")
    with cb:
        c2_sel = st.selectbox(lbl["add_texture"],    list(_C2_OPTIONS.keys()), key="add_c2")
        c4_sel = st.selectbox(lbl["add_drainage"],   list(_C4_OPTIONS.keys()), key="add_c4")
        c6_sel = st.selectbox(lbl["add_field_size"], list(_C6_OPTIONS.keys()), key="add_c6")

    if st.button(lbl["add_btn"], type="primary", use_container_width=True, key="btn_add_plot"):
        if not nome_input.strip():
            st.warning(lbl["add_warn"])
        else:
            ctx = {
                "c1_regiao":  _C1_OPTIONS[c1_sel],
                "c2_textura": _C2_OPTIONS[c2_sel],
                "c3_ph":      _C3_OPTIONS[c3_sel],
                "c4_drenagem":_C4_OPTIONS[c4_sel],
                "c5_aptidao": _C5_OPTIONS[c5_sel],
                "c6_area":    _C6_OPTIONS[c6_sel],
            }
            save_plot(user_id, nome_input.strip(), area_input, ctx)
            st.success(lbl["add_ok"].format(nome=nome_input.strip()))
            st.rerun()


def render() -> None:
    lang    = st.session_state.get("lang", "en")
    auth    = st.session_state.get("auth", {})
    user_id = auth.get("email", auth.get("id", "default"))
    lbl     = _L.get(lang, _L["en"])

    st.markdown(f'<div class="page-title">{lbl["title"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-subtitle">{lbl["subtitle"]}</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    plots = load_plots(user_id)

    # ── Handle pending delete ─────────────────────────────────────────────────
    if st.session_state.get("_plot_delete_id"):
        delete_plot(st.session_state._plot_delete_id)
        st.session_state._plot_delete_id = None
        st.success(lbl["deleted_ok"])
        plots = load_plots(user_id)

    if not plots:
        # ── Empty state: destaque total no cadastro ───────────────────────────
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#0d2b18 0%,#1a5c38 60%,#2d8a56 100%);
                    border-radius:16px;padding:40px 36px;margin-bottom:28px;text-align:center">
          <div style="font-size:2.4rem;margin-bottom:12px">🌱</div>
          <div style="font-size:1.4rem;font-weight:800;color:#ffffff;margin-bottom:8px">
            {"Register your first field" if lang == "en" else "Cadastre seu primeiro talhão"}
          </div>
          <div style="font-size:0.88rem;color:rgba(255,255,255,0.65);max-width:420px;margin:0 auto;line-height:1.6">
            {"Add your fields once, then simulate each season — the simulator pre-fills your soil conditions automatically."
              if lang == "en" else
              "Cadastre seus talhões uma vez e simule cada safra — o simulador preenche as condições do solo automaticamente."}
          </div>
        </div>
        """, unsafe_allow_html=True)

        _render_add_form(user_id, lbl, lang)
        return
    else:
        plots_with_sim = [p for p in plots if p.get("simulations")]
        total_area     = sum(p["area_ha"] for p in plots)
        n_plots        = len(plots)

        if plots_with_sim:
            weighted_area = sum(p["area_ha"] for p in plots_with_sim)
            avg_ev   = sum(p["simulations"][-1]["ev_simulated"] * p["area_ha"] for p in plots_with_sim) / weighted_area if weighted_area else 0.0
            total_sc = sum(p["simulations"][-1]["ev_simulated"] * p["area_ha"] for p in plots_with_sim)
            all_sims_flat = [(s, p) for p in plots_with_sim for s in p.get("simulations", [])]
            last_enso = all_sims_flat[-1][0].get("c7_enso", "") if all_sims_flat else ""
        else:
            avg_ev = total_sc = 0.0
            last_enso = ""

        enso_info = _ENSO_MAP.get(last_enso, {
            "short_en": "—", "short_pt": "—", "oni": "—", "dot": "#9e9e9e",
            "desc_en": "Run a simulation to see the climate scenario.",
            "desc_pt": "Rode uma simulação para ver o cenário climático.",
        })
        enso_short = enso_info[f"short_{lang}"]
        enso_desc  = enso_info[f"desc_{lang}"]
        enso_oni   = enso_info["oni"]
        enso_dot   = enso_info["dot"]

        avg_ev_color = "#76c442" if avg_ev >= _MT_BASELINE else "#ff8a65"
        delta_farm   = avg_ev - _MT_BASELINE
        delta_sign   = "+" if delta_farm >= 0 else ""

        # ── Farm hero card ────────────────────────────────────────────────────
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#0d2b18 0%,#1a5c38 60%,#2d8a56 100%);
                    border-radius:16px;padding:28px 32px;margin-bottom:24px;
                    display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:20px">
          <div>
            <div style="font-size:0.65rem;font-weight:700;color:rgba(255,255,255,0.85)!important;
                        text-transform:uppercase;letter-spacing:0.14em;margin-bottom:10px">
              ◆ SOJA · MATO GROSSO
            </div>
            <div style="font-size:1.6rem;font-weight:800;color:#ffffff!important;line-height:1.2;margin-bottom:8px">
              {lbl["hero_title"]}
            </div>
            <div style="font-size:0.82rem;color:rgba(255,255,255,0.90)!important;max-width:360px;line-height:1.5">
              {lbl["hero_sub"]}
            </div>
          </div>
          <div style="display:flex;gap:28px;flex-wrap:wrap">
            <div style="text-align:center">
              <div style="font-size:0.6rem;font-weight:700;color:rgba(255,255,255,0.85)!important;text-transform:uppercase;letter-spacing:0.1em">{lbl["avg_yield_lbl"]}</div>
              <div style="font-size:2rem;font-weight:900;color:{avg_ev_color}!important;line-height:1">{f"{avg_ev:.1f}" if avg_ev else "—"}</div>
              <div style="font-size:0.62rem;color:rgba(255,255,255,0.80)!important">{delta_sign}{delta_farm:.1f} {lbl["hero_vs_ref"]}</div>
            </div>
            <div style="text-align:center">
              <div style="font-size:0.6rem;font-weight:700;color:rgba(255,255,255,0.85)!important;text-transform:uppercase;letter-spacing:0.1em">{lbl["climate_label"]}</div>
              <div style="display:flex;align-items:center;gap:6px;justify-content:center">
                <span style="width:10px;height:10px;border-radius:50%;background:{enso_dot};display:inline-block"></span>
                <span style="font-size:1.2rem;font-weight:800;color:#ffffff!important">{enso_short}</span>
              </div>
              <div style="font-size:0.72rem;color:rgba(255,255,255,0.85)!important">{enso_oni} ONI</div>
            </div>
            <div style="text-align:center">
              <div style="font-size:0.6rem;font-weight:700;color:rgba(255,255,255,0.85)!important;text-transform:uppercase;letter-spacing:0.1em">{lbl["num_fields"]} · {lbl["total_area"]}</div>
              <div style="font-size:1.8rem;font-weight:900;color:#ffffff!important;line-height:1">{n_plots}</div>
              <div style="font-size:0.62rem;color:rgba(255,255,255,0.80)!important">{total_area:,.0f} ha</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Mosaico + ENSO side panel ─────────────────────────────────────────
        col_mosaic, col_enso = st.columns([3, 2], gap="large")

        with col_mosaic:
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:4px">'
                f'<span class="section-hdr" style="margin:0">{lbl["mosaic_title"]}</span>'
                f'</div>'
                f'<div style="font-size:0.7rem;color:#6b6b8a;margin-bottom:10px">{lbl["mosaic_sub"]}</div>',
                unsafe_allow_html=True,
            )

            # Build per-plot arrays then sort by area descending to match
            # Plotly's internal treemap rendering order (avoids color mismatch)
            _tm_rows = []
            for p in plots:
                sims = p.get("simulations", [])
                if sims:
                    ev = sims[-1]["ev_simulated"]
                    delta = ev - _MT_BASELINE
                    d_sign = "+" if delta >= 0 else ""
                    text   = f"{p['nome']}<br>{ev:.1f} sc/ha<br>{d_sign}{delta:.1f}"
                    custom = [f"{ev:.1f}", p["area_ha"], len(sims), ev * p["area_ha"]]
                    if ev >= _MT_BASELINE + 5:
                        color = "#1a5c38"
                    elif ev >= _MT_BASELINE:
                        color = "#2d8a56"
                    elif ev >= _MT_BASELINE - 5:
                        color = "#f57c00"
                    else:
                        color = "#c62828"
                else:
                    text   = f"{p['nome']}<br>{lbl['no_sim_label']}<br>{p['area_ha']:,.0f} ha"
                    custom = ["—", p["area_ha"], 0, 0]
                    color  = "rgba(180,180,200,0.4)"
                _tm_rows.append((p["nome"], "", p["area_ha"], text, custom, color))

            _tm_rows.sort(key=lambda r: r[2], reverse=True)
            tm_labels, tm_parents, tm_values, tm_text, tm_custom, _tile_colors = (
                list(x) for x in zip(*_tm_rows)
            )

            fig_tm = go.Figure(go.Treemap(
                labels=tm_labels,
                parents=tm_parents,
                values=tm_values,
                text=tm_text,
                textinfo="text",
                textfont=dict(color="white", size=11, family="sans-serif"),
                marker=dict(
                    colors=_tile_colors,
                    line=dict(color="white", width=2),
                    pad=dict(t=4, l=4, r=4, b=4),
                ),
                customdata=tm_custom,
                hovertemplate=(
                    "<b>%{label}</b><br>"
                    "EV: %{customdata[0]} sc/ha<br>"
                    "Area: %{customdata[1]:,.0f} ha<br>"
                    "Sims: %{customdata[2]}<br>"
                    "Projected: %{customdata[3]:,.0f} bags<extra></extra>"
                ),
                root_color="#f4faf7",
            ))
            fig_tm.update_layout(
                height=340,
                margin=dict(t=4, l=0, r=0, b=4),
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white", size=11),
            )
            st.plotly_chart(fig_tm, use_container_width=True, config={"displayModeBar": False})

            st.markdown(
                '<div style="display:flex;gap:14px;font-size:0.62rem;color:#6b6b8a;margin-top:-8px;margin-bottom:4px">'
                '<span><span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:#1a5c38;margin-right:3px"></span>&gt;+5 sc/ha</span>'
                '<span><span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:#2d8a56;margin-right:3px"></span>above ref</span>'
                '<span><span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:#f57c00;margin-right:3px"></span>slightly below</span>'
                '<span><span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:#c62828;margin-right:3px"></span>&lt;−5 sc/ha</span>'
                '<span><span style="display:inline-block;width:10px;height:10px;border-radius:2px;background:rgba(180,180,200,0.5);margin-right:3px"></span>no sim</span>'
                '</div>',
                unsafe_allow_html=True,
            )

        with col_enso:
            st.markdown(f"""
            <div style="background:linear-gradient(160deg,#0d2b18 0%,#1a5c38 100%);
                        border-radius:14px;padding:20px 22px;margin-bottom:14px">
              <div style="font-size:0.58rem;font-weight:700;color:rgba(255,255,255,0.85)!important;
                          text-transform:uppercase;letter-spacing:0.12em;margin-bottom:10px;
                          display:flex;justify-content:space-between">
                <span style="color:rgba(255,255,255,0.85)!important">{lbl["enso_panel_title"]}</span>
                <span style="color:rgba(255,255,255,0.85)!important">ONI</span>
              </div>
              <div style="display:flex;justify-content:space-between;align-items:flex-start">
                <div style="display:flex;align-items:center;gap:8px">
                  <span style="width:10px;height:10px;border-radius:50%;background:{enso_dot};display:inline-block;flex-shrink:0"></span>
                  <span style="font-size:1.2rem;font-weight:800;color:#ffffff!important">{enso_short}</span>
                </div>
                <div style="font-size:1.6rem;font-weight:900;color:#ffffff!important">{enso_oni}</div>
              </div>
              <div style="font-size:0.74rem;color:rgba(255,255,255,0.90)!important;margin-top:12px;line-height:1.55;
                          border-top:1px solid rgba(255,255,255,0.15);padding-top:10px">
                {enso_desc}
              </div>
            </div>
            """, unsafe_allow_html=True)

            n_sim_done = len(plots_with_sim)
            pct_done = int(n_sim_done / n_plots * 100) if n_plots else 0
            _sims_done_str = lbl["sims_done_lbl"].format(n=n_sim_done, total=n_plots)

            st.markdown(f"""
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:14px">
              <div style="background:#fff;border:1px solid #e4e4f0;border-radius:10px;padding:14px 16px;border-top:3px solid #1a5c38">
                <div style="font-size:0.6rem;font-weight:700;color:#6b6b8a;text-transform:uppercase;letter-spacing:0.08em">{lbl["avg_yield_lbl"]}</div>
                <div style="font-size:1.5rem;font-weight:900;color:{"#2e7d32" if avg_ev >= _MT_BASELINE else "#c62828"}">{f"{avg_ev:.1f}" if avg_ev else "—"}</div>
                <div style="font-size:0.65rem;color:#9e9e9e">sc/ha</div>
              </div>
              <div style="background:#fff;border:1px solid #e4e4f0;border-radius:10px;padding:14px 16px;border-top:3px solid #1565c0">
                <div style="font-size:0.6rem;font-weight:700;color:#6b6b8a;text-transform:uppercase;letter-spacing:0.08em">{lbl["total_bags_lbl"]}</div>
                <div style="font-size:1.5rem;font-weight:900;color:#1565c0">{f"{total_sc:,.0f}" if total_sc else "—"}</div>
                <div style="font-size:0.65rem;color:#9e9e9e">sc</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div style="background:#fff;border:1px solid #e4e4f0;border-radius:10px;padding:14px 16px">
              <div style="font-size:0.65rem;color:#3a3a5c;margin-bottom:6px;font-weight:600">{_sims_done_str}</div>
              <div style="background:#e8f5e9;border-radius:6px;height:8px">
                <div style="background:{"#1a5c38" if pct_done == 100 else "#2d8a56"};width:{pct_done}%;height:8px;border-radius:6px;transition:width .3s"></div>
              </div>
              <div style="font-size:0.6rem;color:#9e9e9e;margin-top:4px">{total_area:,.0f} ha total · {total_sc:,.0f} bags projected</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Field detail cards ────────────────────────────────────────────────
        st.markdown(f'<div class="section-hdr">{lbl["fields_title"]}</div>', unsafe_allow_html=True)
        st.caption(lbl["fields_detail_sub"])

        cols_per_row = 2
        rows = [plots[i:i + cols_per_row] for i in range(0, len(plots), cols_per_row)]
        for row in rows:
            cols = st.columns(cols_per_row)
            for col, plot in zip(cols, row):
                with col:
                    icon, color = _soil_health(plot.get("context", {}))
                    sims     = plot.get("simulations", [])
                    last_sim = sims[-1] if sims else None
                    ev_val   = last_sim["ev_simulated"] if last_sim else None
                    ev_str   = lbl["last_ev"].format(ev=f"{ev_val:.1f}") if ev_val else lbl["no_sim"]
                    ctx      = plot.get("context", {})
                    badges   = _soil_badges_html(ctx, lbl)

                    delta_html = ""
                    if ev_val is not None:
                        delta  = ev_val - _MT_BASELINE
                        d_sign = "+" if delta >= 0 else ""
                        delta_html = (
                            f'<span style="font-size:0.68rem;color:#6b6b8a;margin-left:6px">'
                            f'{lbl["vs_ref"].format(sign=d_sign, delta=abs(delta))}</span>'
                        )

                    trend_html = ""
                    if len(sims) >= 2:
                        _trend = _sim_trend(sims)
                        trend_html = (
                            f'<span style="font-size:0.62rem;color:#9e9e9e;margin-left:6px">'
                            f'{lbl[f"trend_{_trend}"]}</span>'
                        )

                    bags_html = ""
                    if ev_val and plot["area_ha"]:
                        bags_html = (
                            f'<div style="font-size:0.65rem;color:#6b6b8a;margin-top:3px">'
                            f'{lbl["bags_field"].format(bags=ev_val * plot["area_ha"])}</div>'
                        )

                    enso_last = last_sim.get("c7_enso", "") if last_sim else ""
                    enso_info_card = _ENSO_MAP.get(enso_last, {})
                    enso_tag  = enso_info_card.get(f"short_{lang}", "")
                    enso_tag_html = (
                        f'<span style="font-size:0.6rem;color:#fff;background:{enso_info_card.get("dot","#9e9e9e")};'
                        f'border-radius:4px;padding:1px 6px;margin-left:6px">{enso_tag}</span>'
                        if enso_tag else ""
                    )

                    # Soil characteristics summary
                    ctx_c1 = ctx.get("c1_regiao", "")
                    ctx_c2 = ctx.get("c2_textura", "")
                    ctx_c3 = ctx.get("c3_ph", "")
                    ctx_c4 = ctx.get("c4_drenagem", "")
                    ctx_c5 = ctx.get("c5_aptidao", "")

                    def _short_val(v: str) -> str:
                        return v.split("(")[0].strip() if "(" in v else v

                    char_rows = []
                    for ctx_key, label_key, val in [
                        ("c1_regiao",   lbl["soil_region"],  ctx_c1),
                        ("c2_textura",  lbl["soil_texture"], ctx_c2),
                        ("c3_ph",       lbl["soil_ph"],      ctx_c3),
                        ("c4_drenagem", lbl["soil_drainage"],ctx_c4),
                        ("c5_aptidao",  lbl["soil_aptitude"],ctx_c5),
                    ]:
                        if val:
                            q   = _C_QUALITY.get(ctx_key, {}).get(val, "neutral")
                            dot = _Q_COLOR.get(q, "#9e9e9e")
                            char_rows.append(
                                f'<div style="display:flex;justify-content:space-between;align-items:center;'
                                f'padding:3px 0;border-bottom:1px solid #f5f5f8">'
                                f'<span style="font-size:0.68rem;color:#6b6b8a">{label_key}</span>'
                                f'<span style="font-size:0.68rem;color:#1a1a2e;font-weight:500;display:flex;align-items:center;gap:4px">'
                                f'<span style="width:6px;height:6px;border-radius:50%;background:{dot};display:inline-block"></span>'
                                f'{_short_val(val)}</span></div>'
                            )
                    char_html = "".join(char_rows)

                    st.markdown(f"""
                    <div style="background:#fff;border:1px solid #e4e4f0;border-radius:14px;
                                padding:0;border-left:4px solid {color};margin-bottom:10px;overflow:hidden">

                      <!-- Header -->
                      <div style="padding:16px 18px 12px 18px">
                        <div style="display:flex;justify-content:space-between;align-items:flex-start">
                          <div style="flex:1;min-width:0">
                            <div style="font-size:1.05rem;font-weight:700;color:#1a1a2e">
                              {icon} {plot['nome']}
                            </div>
                            <div style="font-size:0.75rem;color:#6b6b8a;margin-top:2px">
                              {lbl['area_label'].format(area=f"{plot['area_ha']:,.0f}")}
                              &nbsp;·&nbsp;{lbl['num_sims'].format(n=len(sims))}
                              {enso_tag_html}
                            </div>
                          </div>
                          <div style="text-align:right;flex-shrink:0;margin-left:12px">
                            <div style="font-size:1.1rem;font-weight:800;color:#1a1a2e">
                              {ev_str}{delta_html}
                            </div>
                            {bags_html}
                            {trend_html}
                          </div>
                        </div>
                      </div>

                      <!-- Soil characteristics table -->
                      <div style="background:#fafafa;border-top:1px solid #f0f0f6;padding:10px 18px">
                        <div style="font-size:0.6rem;font-weight:700;color:#9e9e9e;text-transform:uppercase;
                                    letter-spacing:0.1em;margin-bottom:6px">
                          {lbl.get("add_ctx_title", "Field conditions")}
                        </div>
                        {char_html}
                      </div>

                      <!-- Badges footer -->
                      <div style="padding:8px 18px;border-top:1px solid #f0f0f6">
                        {badges}
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Action buttons
                    b1, b2, b3, b4 = st.columns([4, 2, 2, 2])
                    with b1:
                        if st.button(lbl["btn_simulate"], key=f"sim_{plot['id']}", use_container_width=True, type="primary"):
                            _prefill_from_plot(plot)
                            navigate("input")
                    with b2:
                        if st.button(lbl["btn_edit"], key=f"edit_{plot['id']}", use_container_width=True):
                            # Toggle edit panel
                            cur = st.session_state.get(f"_edit_open_{plot['id']}", False)
                            st.session_state[f"_edit_open_{plot['id']}"] = not cur
                            st.rerun()
                    with b3:
                        if sims and st.button(lbl["btn_history"], key=f"hist_{plot['id']}", use_container_width=True):
                            cur = st.session_state.get(f"_hist_open_{plot['id']}", False)
                            st.session_state[f"_hist_open_{plot['id']}"] = not cur
                            st.rerun()
                    with b4:
                        if st.button(lbl["btn_delete"], key=f"del_{plot['id']}", use_container_width=True):
                            st.session_state._plot_delete_id = plot["id"]
                            st.rerun()

                    if st.session_state.get(f"_edit_open_{plot['id']}"):
                        _render_edit_form(plot, user_id, lbl, lang)

                    if st.session_state.get(f"_hist_open_{plot['id']}") and sims:
                        with st.container():
                            st.markdown(
                                f'<div style="font-size:0.72rem;font-weight:700;color:#1a3a2a;'
                                f'margin:4px 0 2px 0">{lbl["hist_title"].format(nome=plot["nome"])}</div>',
                                unsafe_allow_html=True,
                            )
                            _render_sim_history(plot, lbl)

        # ── EV comparison chart (≥2 fields with sim) ─────────────────────────
        if len(plots_with_sim) >= 2:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f'<div class="section-hdr">{lbl["chart_title"]}</div>', unsafe_allow_html=True)

            names  = [p["nome"] for p in plots_with_sim]
            evs    = [p["simulations"][-1]["ev_simulated"] for p in plots_with_sim]
            areas  = [p["area_ha"] for p in plots_with_sim]
            bags   = [e * a for e, a in zip(evs, areas)]
            colors = ["#1a5c38" if e >= _MT_BASELINE else "#c62828" for e in evs]

            fig_cmp = go.Figure()
            fig_cmp.add_trace(go.Bar(
                x=evs, y=names, orientation="h",
                marker_color=colors, marker_line_width=0,
                text=[f"<b>{e:.1f}</b>  ≈{b:,.0f} bags" for e, b in zip(evs, bags)],
                textposition="outside",
                customdata=[[a, b] for a, b in zip(areas, bags)],
                hovertemplate="<b>%{y}</b><br>EV: %{x:.1f} sc/ha<br>Area: %{customdata[0]:,.0f} ha<br>Bags: %{customdata[1]:,.0f}<extra></extra>",
            ))
            fig_cmp.add_vline(
                x=_MT_BASELINE, line_color="#f57c00", line_dash="dot", line_width=1.5,
                annotation_text=lbl["chart_ref"].format(ref=_MT_BASELINE),
                annotation_font_size=9, annotation_font_color="#b35c00",
            )
            fig_cmp.update_layout(
                height=max(200, len(plots_with_sim) * 50),
                xaxis_title=lbl["chart_axis"],
                margin=dict(t=8, l=10, r=120, b=36),
                plot_bgcolor="#fafafa", paper_bgcolor="white",
                font=dict(color="#1a1a2e", size=10),
                xaxis=dict(gridcolor="#f0f0f0", range=[min(evs + [_MT_BASELINE]) * 0.88, max(evs + [_MT_BASELINE]) * 1.16]),
                yaxis=dict(tickfont=dict(size=10)),
                showlegend=False,
            )
            st.plotly_chart(fig_cmp, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Add new field ─────────────────────────────────────────────────────────
    with st.expander(lbl["add_title"], expanded=False):
        _render_add_form(user_id, lbl, lang)

    # ── Save current simulation to a field ────────────────────────────────────
    result    = st.session_state.get("sim_result")
    decisions = st.session_state.get("sim_decisions")
    context   = st.session_state.get("sim_context")

    if result and decisions and context and plots:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander(lbl["save_hdr"]):
            plot_names = {p["id"]: p["nome"] for p in plots}
            sel_id = st.selectbox(
                lbl["save_select"],
                options=list(plot_names.keys()),
                format_func=lambda k: plot_names[k],
                key="save_sim_plot_select",
            )
            if st.button(lbl["save_btn"], type="primary", key="btn_save_sim_plots"):
                risk_profile = st.session_state.get("risk_profile", "balanced")
                ev = result["user_selection"]["ev"]
                add_simulation(
                    plot_id=sel_id,
                    c7_enso=context.get("c7_enso", ""),
                    decisions=dict(decisions),
                    risk_profile=risk_profile,
                    ev_simulated=ev,
                )
                st.success(lbl["save_ok"].format(nome=plot_names[sel_id]))
                st.rerun()
    elif result and not plots:
        st.info(lbl["save_no_plots"])


def _prefill_from_plot(plot: dict) -> None:
    st.session_state.talhao_id      = plot["id"]
    st.session_state.talhao_nome    = plot["nome"]
    st.session_state.talhao_prefill = dict(plot.get("context", {}))
    st.session_state.input_step     = 1
