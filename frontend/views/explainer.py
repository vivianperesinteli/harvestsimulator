"""Painel Explicativo — Como o simulador chega às recomendações."""

from __future__ import annotations
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from frontend.navigation import go as nav_go

# ── Definição dos passos ──────────────────────────────────────────────────────

_STEPS = [
    (1,  "Ponto de Partida",       "A produtividade média histórica como referência"),
    (2,  "Contexto do Talhão",     "7 fatores do campo ajustam a referência"),
    (3,  "Decisões do Produtor",   "6 decisões — fixas e variáveis"),
    (4,  "27 Caminhos Possíveis",  "Combinações das decisões variáveis"),
    (5,  "Clima e ENSO",           "Cenários climáticos e suas probabilidades"),
    (6,  "Efeitos de Interação",   "Combinações que amplificam ou penalizam o resultado"),
    (7,  "Matriz de Payoff",       "27 caminhos × 3 climas = todos os resultados possíveis"),
    (8,  "Critérios de Decisão",   "6 perspectivas para escolher o melhor caminho"),
    (9,  "Análise de Risco",       "10.000 simulações estimam o intervalo de confiança"),
    (10, "Recomendação Final",     "O modelo aponta a combinação com maior retorno esperado"),
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
            if st.button("← Anterior", use_container_width=True):
                st.session_state.explainer_step -= 1
                st.rerun()
    with c_info:
        st.markdown(
            f'<div style="text-align:center;font-size:0.78rem;color:#6b6b8a;padding-top:8px">'
            f'Passo {current} de {_N}</div>',
            unsafe_allow_html=True,
        )
    with c_next:
        if current < _N:
            if st.button("Próximo →", type="primary", use_container_width=True):
                st.session_state.explainer_step += 1
                st.rerun()
        else:
            if st.button("Reiniciar", use_container_width=True):
                st.session_state.explainer_step = 1
                st.rerun()


def _step_header(num: int, title: str, desc: str) -> None:
    st.markdown(f"""
    <div class="exp-step-header">
        <div class="exp-step-number">Passo {num}</div>
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


# ── Passos ────────────────────────────────────────────────────────────────────

def _render_step_1() -> None:
    _step_header(1, "Ponto de Partida", "A produtividade média histórica do Mato Grosso serve como âncora do modelo")

    c1, c2 = st.columns([1, 2], gap="large")
    with c1:
        st.markdown("""
        <div style="text-align:center;padding:40px 20px;background:#fff;border-radius:12px;border:1px solid #e4e4f0;box-shadow:0 2px 8px rgba(0,0,0,0.06)">
            <div style="font-size:0.7rem;font-weight:700;color:#6b6b8a;text-transform:uppercase;letter-spacing:0.1em">Baseline</div>
            <div style="font-size:5rem;font-weight:900;color:#1a5c38;line-height:1">60</div>
            <div style="font-size:1rem;color:#3a3a5c;font-weight:600">sc/ha</div>
            <div style="font-size:0.72rem;color:#6b6b8a;margin-top:8px">Fonte: CONAB · MT 2023/24</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        _info_card("Por que 60 sc/ha?",
            "A produtividade média do Mato Grosso na safra 2023/24 foi de 60 sacas por hectare, "
            "segundo o levantamento da CONAB. Este número representa o desempenho de um produtor "
            "médio da região — antes de qualquer ajuste pelas condições específicas do talhão.")

        st.markdown("<br>", unsafe_allow_html=True)
        _formula_box(
            "Produtividade = <strong>60</strong> + ajustes do contexto + ajustes das decisões + ajuste climático",
            label="Equação geral do modelo"
        )

        st.markdown("<br>", unsafe_allow_html=True)
        _info_card("Como funciona o ajuste",
            "Cada fator — solo, clima, manejo, cultivar — adiciona ou subtrai sacas por hectare "
            "em relação a essa referência. O produtor que tem condições melhores que a média "
            "recebe ajuste positivo; condições piores, ajuste negativo.",
            color="#1565c0")


def _render_step_2(result: dict | None) -> None:
    _step_header(2, "Contexto do Talhão",
        "7 fatores não controláveis pelo produtor descrevem as condições do campo")

    col_table, col_chart = st.columns([1, 1], gap="large")

    with col_table:
        st.markdown("**Os 7 fatores de contexto e seu impacto (sc/ha):**")
        labels = [
            ("C1", "Região", "Favorável (Sorriso, Sinop...)", "+5", "Desafiadora (Primavera, Querência)", "−6"),
            ("C2", "Textura do Solo", "Argilosa / bem estruturada", "+5", "Arenosa / baixa retenção", "−7"),
            ("C3", "pH do Solo", "Adequado 5,5–6,5", "+4", "Crítico <5,0 ou >6,8", "−6"),
            ("C4", "Drenagem", "Sem encharcamento", "+3", "Com alagamentos frequentes", "−8"),
            ("C5", "Tipo de Solo", "Latossolo / Nitossolo", "+5", "Neossolo / Gleissolo", "−7"),
            ("C6", "Área", "Acima de 200 ha", "+2", "Até 50 ha", "−1"),
            ("C7", "Previsão Climática", "El Niño", "+3", "La Niña", "−3"),
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
        st.markdown("**Amplitude de ajuste por fator:**")
        nomes = ["Região", "Textura", "pH", "Drenagem", "Tipo Solo", "Área", "ENSO"]
        positivos = [5, 5, 4, 3, 5, 2, 3]
        negativos = [-6, -7, -6, -8, -7, -1, -3]

        fig = go.Figure()
        fig.add_bar(x=positivos, y=nomes, orientation="h",
                    marker_color="#2d8a56", name="Ganho máximo",
                    text=[f"+{v}" for v in positivos], textposition="outside")
        fig.add_bar(x=negativos, y=nomes, orientation="h",
                    marker_color="#c62828", name="Penalidade máxima",
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
                <span style="font-size:0.75rem;color:#1a5c38;font-weight:700">RESULTADO NA SUA SIMULAÇÃO</span><br>
                <span style="font-size:1.4rem;font-weight:800;color:{color}">{sign}{ctx_adj:.1f} sc/ha</span>
                <span style="font-size:0.8rem;color:#3a3a5c"> de ajuste pelo contexto</span><br>
                <span style="font-size:0.8rem;color:#1a5c38">Base ajustada: {result['context_base']:.0f} sc/ha</span>
            </div>
            """, unsafe_allow_html=True)


def _render_step_3(result: dict | None) -> None:
    _step_header(3, "Decisões do Produtor",
        "6 decisões de manejo — três deslocam todos os cenários igualmente, três criam os cenários")

    _formula_box(
        "Base efetiva = 60 + contexto + <strong style='color:#b35c00'>D2 (cultivar) + D3 (TSI) + D6 (plantadeira)</strong> "
        "+ <strong style='color:#1a5c38'>D1 (janela) + D4 (densidade) + D5 (manejo doenças)</strong>"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    c_fixed, c_var = st.columns(2, gap="large")

    with c_fixed:
        st.markdown("""
        <div style="background:#fff8e1;border:1px solid #ffe082;border-radius:10px;padding:20px">
            <div style="font-size:0.7rem;font-weight:700;color:#b35c00;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:12px">
                🔒 Decisões Fixas — deslocam todos os 27 cenários igualmente
            </div>
        """, unsafe_allow_html=True)
        for cod, nome, desc, faixa in [
            ("D2", "Cultivar", "Potencial genético da variedade", "−8 a +6 sc/ha"),
            ("D3", "TSI", "Tratamento Industrial de Sementes", "−5 a +3 sc/ha"),
            ("D6", "Plantadeira", "Tecnologia e precisão de plantio", "−4 a +3 sc/ha"),
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
                Ajuste fixo na sua simulação: {result['fixed_adj']:+.1f} sc/ha
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c_var:
        st.markdown("""
        <div style="background:#e8f5e9;border:1px solid #a5d6a7;border-radius:10px;padding:20px">
            <div style="font-size:0.7rem;font-weight:700;color:#1a5c38;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:12px">
                🔀 Decisões Variáveis — cada combinação gera um cenário diferente
            </div>
        """, unsafe_allow_html=True)
        for cod, nome, desc, faixa, opts in [
            ("D1", "Janela de Plantio", "Período de semeadura", "−8 a +4 sc/ha", "3 opções"),
            ("D4", "Densidade", "Sementes por hectare", "−1 a +2 sc/ha", "3 opções"),
            ("D5", "Manejo de Doenças", "Número de fungicidas", "−7 a +5 sc/ha", "3 opções"),
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
            3 × 3 × 3 = 27 combinações avaliadas simultaneamente
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    _info_card("Por que separar fixas das variáveis?",
        "As decisões fixas (D2, D3, D6) deslocam todos os 27 caminhos pelo mesmo valor — "
        "não mudam qual combinação é a melhor, só mudam o nível absoluto de produtividade. "
        "As variáveis (D1, D4, D5) mudam o ranking entre os caminhos porque cada uma interage "
        "diferente com os cenários climáticos.", color="#1565c0")


def _render_step_4(result: dict | None) -> None:
    _step_header(4, "27 Caminhos Possíveis",
        "D1 × D4 × D5 = 3 × 3 × 3 = 27 combinações avaliadas em paralelo")

    c_tree, c_explain = st.columns([3, 2], gap="large")

    with c_tree:
        st.markdown("**Estrutura das combinações:**")
        d1_opts = ["Precoce\n(até 15/out)", "Ótima\n(16/out–10/nov)", "Tardia\n(após 10/nov)"]
        d4_opts = ["Dens. Baixa", "Dens. Média", "Dens. Alta"]
        d5_opts = ["Manejo Intensivo", "Manejo Padrão", "Manejo Reduzido"]

        rows = []
        for i, d1 in enumerate(["Precoce", "Ótima", "Tardia"]):
            for j, d4 in enumerate(["Baixa", "Média", "Alta"]):
                for k, d5 in enumerate(["Intensivo", "Padrão", "Reduzido"]):
                    path_num = i * 9 + j * 3 + k + 1
                    rows.append({"#": path_num, "D1 · Janela": d1, "D4 · Densidade": d4, "D5 · Manejo": d5})

        df = pd.DataFrame(rows).set_index("#")
        highlight_idx = None
        if result:
            ps = result.get("paths", [])
            opt_idx = result.get("criteria", {}).get("bayes_ev", {}).get("path_idx", None)
            highlight_idx = opt_idx + 1 if opt_idx is not None else None

        def _hl(row):
            if highlight_idx and row.name == highlight_idx:
                return ["background-color:#e8f5e9;font-weight:bold"] * len(row)
            return [""] * len(row)

        st.dataframe(df.style.apply(_hl, axis=1), use_container_width=True, height=400)
        if highlight_idx:
            st.caption(f"★ linha {highlight_idx} = melhor caminho da sua simulação")

    with c_explain:
        _info_card("O que são esses 27 caminhos?",
            "Cada linha da tabela representa uma estratégia completa de manejo: "
            "uma janela de plantio específica, uma densidade específica e um nível "
            "de proteção contra doenças específico. O simulador avalia todas ao mesmo tempo.")

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
        <div style="background:#ffffff;border:1.5px solid #c4c4d4;border-radius:10px;padding:16px;box-shadow:0 2px 8px rgba(0,0,0,0.08)">
            <div style="font-size:0.7rem;font-weight:700;color:#4a4a6a;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:10px">Lógica da combinação</div>
        """, unsafe_allow_html=True)
        for n, label, sub in [
            ("3", "opções de janela", "Precoce · Ótima · Tardia"),
            ("×", "", ""),
            ("3", "opções de densidade", "Baixa · Média · Alta"),
            ("×", "", ""),
            ("3", "opções de manejo", "Intensivo · Padrão · Reduzido"),
            ("=", "", ""),
            ("27", "caminhos avaliados", "em paralelo, para cada cenário climático"),
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
    _step_header(5, "Clima e ENSO",
        "Cada um dos 27 caminhos é avaliado em 3 estados climáticos com probabilidades condicionais ao ENSO")

    from backend.data import RAIN_STATES, RAIN_PROBS

    c_prob, c_explain = st.columns([3, 2], gap="large")

    with c_prob:
        st.markdown("**Probabilidades de chuva no período R3–R6 (enchimento de grão):**")
        enso_labels = {
            "El Niño (chuva regular em MT)":    "El Niño",
            "Neutro":                            "Neutro",
            "La Niña (chuva concentrada/curta)": "La Niña",
        }
        rain_labels = {
            "Seca (<150 mm)":      "Seca",
            "Normal (150–250 mm)": "Normal",
            "Úmida (>250 mm)":     "Úmida",
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
            from backend.data import CONTEXT_NODES
            ctx = st.session_state.get("sim_context", {})
            user_enso = enso_labels.get(ctx.get("c7_enso", ""), None)

        def _hl_enso(row):
            if user_enso and row.name == user_enso:
                return ["background-color:#e8f5e9;font-weight:bold"] * len(row)
            return [""] * len(row)

        st.dataframe(df_prob.style.apply(_hl_enso, axis=1), use_container_width=True)
        if user_enso:
            st.caption(f"★ linha destacada = ENSO da sua simulação ({user_enso})")

        st.markdown("<br>", unsafe_allow_html=True)
        fig = go.Figure()
        colors = {"Seca": "#c62828", "Normal": "#f57c00", "Úmida": "#1565c0"}
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
        _info_card("Por que usar ENSO?",
            "El Niño e La Niña alteram significativamente a distribuição de chuvas no Mato Grosso "
            "durante o enchimento de grão (R3–R6). Em anos de La Niña, a probabilidade de seca "
            "sobe para 50% — mudando completamente qual estratégia é mais segura.")

        st.markdown("<br>", unsafe_allow_html=True)
        _info_card("Ajuste de cada estado climático",
            "• Seca (<150 mm): −8 sc/ha\n"
            "• Normal (150–250 mm): +2 sc/ha\n"
            "• Úmida (>250 mm): +4 sc/ha\n\n"
            "Esses valores são aplicados por cima de cada caminho para gerar a matriz final.",
            color="#1565c0")

        st.markdown("<br>", unsafe_allow_html=True)
        _info_card("Resultado",
            "Cada um dos 27 caminhos é avaliado em 3 climas → "
            "matriz de 27 × 3 = 81 resultados possíveis.",
            color="#b35c00")


def _render_step_6() -> None:
    _step_header(6, "Efeitos de Interação",
        "Algumas combinações de variáveis produzem efeitos que vão além da soma das partes")

    st.markdown("""
    <div style="background:#fff3e0;border-left:4px solid #f57c00;padding:12px 16px;border-radius:0 8px 8px 0;margin-bottom:20px;font-size:0.85rem;color:#3a3a5c">
        <strong>O que é uma interação?</strong> O modelo aditivo assume que cada fator contribui de forma independente.
        Mas na prática, cultivar de alto potencial + manejo ruim de doenças é <em>mais</em> prejudicial do que a soma dos dois.
        Os termos de interação capturam esses efeitos.
    </div>
    """, unsafe_allow_html=True)

    inter_data = [
        {
            "titulo": "Interação 1 — Cultivar × Manejo de Doenças (D2 × D5)",
            "cor": "#1a5c38",
            "desc": "Cultivares de alto potencial genético são mais susceptíveis a ferrugem. Com manejo adequado, entregam o potencial. Com manejo ruim, o alto potencial vira passivo.",
            "linhas": [
                ("Alto potencial + Manejo intensivo", "+2,0 sc/ha", "#2e7d32"),
                ("Alto potencial + Manejo reduzido",  "−2,0 sc/ha", "#c62828"),
                ("Intermediário + Manejo intensivo",  "+0,5 sc/ha", "#2e7d32"),
                ("Legado + Manejo intensivo",         "−1,0 sc/ha", "#c62828"),
            ],
        },
        {
            "titulo": "Interação 2 — Drenagem × Chuva (C4 × Clima)",
            "cor": "#1565c0",
            "desc": "Solo com drenagem ruim não penaliza em anos secos — às vezes até ajuda por reter umidade. O problema aparece em anos úmidos, quando o encharcamento causa asfixia radicular.",
            "linhas": [
                ("Drenagem ruim + Ano úmido",     "−4,0 sc/ha", "#c62828"),
                ("Drenagem ruim + Ano normal",    "−1,5 sc/ha", "#f57c00"),
                ("Drenagem ruim + Ano seco",      "+4,0 sc/ha", "#2e7d32"),
                ("Drenagem moderada + Úmido",     "−1,5 sc/ha", "#f57c00"),
                ("Boa drenagem + Úmido",          "+1,0 sc/ha", "#2e7d32"),
            ],
        },
        {
            "titulo": "Interação 3 — Janela de Plantio × ENSO (D1 × C7)",
            "cor": "#b35c00",
            "desc": "Plantio tardio em ano de La Niña é a combinação mais arriscada: o enchimento de grão cai no pico do veranico. Em El Niño, plantar tarde tem menos consequências.",
            "linhas": [
                ("Tardio + La Niña",  "−2,5 sc/ha", "#c62828"),
                ("Tardio + El Niño",  "+1,0 sc/ha", "#2e7d32"),
                ("Ótimo + El Niño",   "+1,0 sc/ha", "#2e7d32"),
                ("Precoce + La Niña", "−1,0 sc/ha", "#f57c00"),
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
    _step_header(7, "Matriz de Payoff",
        "Cada combinação de caminho × clima produz um valor de produtividade esperada")

    if not result:
        st.info("Rode uma simulação para ver a sua matriz de payoff aqui.")
        _formula_box("Payoff[caminho i, clima j] = base_efetiva + D1ᵢ + D4ᵢ + D5ᵢ + chuvaⱼ + interações")
        return

    paths  = result["paths"]
    matrix = result["matrix"]
    states = result["rain_states"]
    ev_vals = result["criteria"]["bayes_ev"]["criterion_values"]
    opt_idx = result["criteria"]["bayes_ev"]["path_idx"]

    _formula_box("Payoff[caminho i, clima j] = base_efetiva + D1ᵢ + D4ᵢ + D5ᵢ + chuvaⱼ + interações")
    st.markdown("<br>", unsafe_allow_html=True)

    d1_s = {"Precoce (até 15/out)": "Precoce", "Ótima (16/out – 10/nov)": "Ótima", "Tardia (após 10/nov)": "Tardia"}
    d4_s = {"Baixa (≤280k sementes/ha)": "Baixa", "Média (280k–340k)": "Média", "Alta (>340k)": "Alta"}
    d5_s = {"Alto (≥3 fung. + monitor ferrugem)": "Intensivo", "Padrão (2 aplicações)": "Padrão", "Baixo (1 ou nenhuma)": "Reduzido"}
    rain_s = [s.split(" ")[0] for s in states]

    rows = []
    for i, path in enumerate(paths):
        row = {
            "#": i + 1,
            "Janela": d1_s.get(path["d1"], path["d1"]),
            "Dens.":  d4_s.get(path["d4"], path["d4"]),
            "Manejo": d5_s.get(path["d5"], path["d5"]),
        }
        for j, rs in enumerate(rain_s):
            row[rs] = matrix[i][j]
        row["Prod. Esp."] = round(ev_vals[i], 1)
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
        .format({rs: "{:.1f}" for rs in rain_s} | {"Prod. Esp.": "{:.1f}"})
        .background_gradient(subset=["Prod. Esp."], cmap="YlGn")
    )
    st.dataframe(styled, use_container_width=True, height=500)
    st.caption(f"★ linha em verde = melhor caminho (Prod. Esp. = {ev_vals[opt_idx]:.1f} sc/ha) · Referência: {baseline} sc/ha")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Melhor resultado possível", f"{max(max(r) for r in matrix):.1f} sc/ha")
    with c2:
        st.metric("Pior resultado possível", f"{min(min(r) for r in matrix):.1f} sc/ha")
    with c3:
        st.metric("Amplitude total", f"{max(max(r) for r in matrix) - min(min(r) for r in matrix):.1f} sc/ha")


def _render_step_8(result: dict | None) -> None:
    _step_header(8, "Critérios de Decisão",
        "6 perspectivas diferentes para escolher o melhor caminho na matriz")

    criterios = [
        ("bayes_ev", "Melhor resultado esperado",
         "Pondera cada resultado pela probabilidade do clima. É o critério principal — maximiza o valor esperado.",
         "#1a5c38", "⭐ Principal"),
        ("wald", "Mais seguro no pior cenário",
         "Escolhe o caminho que garante o maior resultado mesmo no pior clima possível. Perfil conservador.",
         "#1565c0", "🛡️ Conservador"),
        ("maximax", "Máximo potencial produtivo",
         "Escolhe o caminho com o maior resultado possível, ignorando o risco. Perfil otimista.",
         "#b35c00", "🚀 Otimista"),
        ("laplace", "Média entre todos os cenários",
         "Trata todos os climas como igualmente prováveis. Referência sem viés.",
         "#6b6b8a", "⚖️ Neutro"),
        ("hurwicz", "Equilíbrio risco/oportunidade",
         "Pondera 50% melhor caso + 50% pior caso. Compromisso entre otimismo e cautela.",
         "#7b1fa2", "🎯 Equilibrado"),
        ("savage", "Menor arrependimento possível",
         "Minimiza o quanto o produtor perderia por não ter escolhido a estratégia ótima em cada clima.",
         "#c62828", "😌 Sem arrependimento"),
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
                    d1_s = {"Precoce (até 15/out)": "Precoce", "Ótima (16/out – 10/nov)": "Ótima", "Tardia (após 10/nov)": "Tardia"}
                    d5_s = {"Alto (≥3 fung. + monitor ferrugem)": "Intensivo", "Padrão (2 aplicações)": "Padrão", "Baixo (1 ou nenhuma)": "Reduzido"}
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
            st.success("✓ Todos os principais critérios apontam para o mesmo caminho — recomendação robusta.")
        else:
            st.info("ℹ️ Critérios diferentes apontam para caminhos diferentes — o modelo usa Bayes EV como primário.")


def _render_step_9(result: dict | None) -> None:
    _step_header(9, "Análise de Risco",
        "10.000 simulações por caminho estimam o intervalo de confiança da produtividade")

    c_explain, c_result = st.columns([1, 1], gap="large")

    with c_explain:
        _info_card("Como funciona o Monte Carlo",
            "Para cada caminho, o modelo sorteia 10.000 cenários onde D2 (cultivar), "
            "D3 (TSI) e D6 (plantadeira) variam aleatoriamente — porque mesmo com uma "
            "escolha feita, o resultado real pode variar por condições de execução, "
            "qualidade do lote de sementes, resposta do campo etc.")

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("""
        <div style="background:#ffffff;border:1.5px solid #c4c4d4;border-radius:10px;padding:16px;box-shadow:0 2px 8px rgba(0,0,0,0.08)">
            <div style="font-size:0.7rem;font-weight:700;color:#4a4a6a;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:10px">Variáveis estocásticas</div>
        """, unsafe_allow_html=True)
        for var, dist in [
            ("D2 · Cultivar",    "Triangular(−8, 0, +6)"),
            ("D3 · TSI",         "Triangular(−5, 0, +3)"),
            ("D6 · Plantadeira", "Triangular(−4, 0, +3)"),
            ("Chuva R3–R6",      "Discreta por P(chuva|ENSO)"),
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
                st.markdown("**Distribuição simulada — melhor caminho:**")
                import numpy as np
                rng = np.random.default_rng(42)
                sim_yields = rng.normal(mc["mean"], mc["std"], 500)
                fig = go.Figure()
                fig.add_histogram(x=sim_yields, nbinsx=30, marker_color="#2d8a56",
                                  opacity=0.75, name="Simulações")
                fig.add_vline(x=mc["p5"],  line_dash="dot", line_color="#c62828",
                              annotation_text=f"P5: {mc['p5']:.0f}", annotation_position="top left")
                fig.add_vline(x=mc["p95"], line_dash="dot", line_color="#1565c0",
                              annotation_text=f"P95: {mc['p95']:.0f}", annotation_position="top right")
                fig.add_vline(x=mc["mean"], line_dash="solid", line_color="#1a5c38",
                              annotation_text=f"Média: {mc['mean']:.0f}", annotation_position="top right")
                fig.update_layout(height=280, margin=dict(l=20, r=20, t=30, b=30),
                                  plot_bgcolor="white", paper_bgcolor="white", showlegend=False,
                                  xaxis_title="sc/ha", yaxis_title="Frequência",
                                  xaxis=dict(gridcolor="#d8d8e8", tickfont=dict(color="#1a1a2e", size=11),
                                             title_font=dict(color="#1a1a2e")),
                                  yaxis=dict(gridcolor="#d8d8e8", tickfont=dict(color="#1a1a2e", size=11),
                                             title_font=dict(color="#1a1a2e")),
                                  font=dict(color="#1a1a2e", size=11))
                st.plotly_chart(fig, use_container_width=True)

                c_p5, c_mean, c_p95 = st.columns(3)
                with c_p5:
                    st.metric("P5 (pior 5%)", f"{mc['p5']:.0f} sc/ha")
                with c_mean:
                    st.metric("Média", f"{mc['mean']:.0f} sc/ha")
                with c_p95:
                    st.metric("P95 (melhor 5%)", f"{mc['p95']:.0f} sc/ha")

                risk = mc.get("p_below", 0)
                risk_color = "🔴" if risk > 0.25 else "🟡" if risk > 0.10 else "🟢"
                st.markdown(f"""
                <div style="background:#f8f9fa;border-radius:8px;padding:12px 16px;margin-top:8px;font-size:0.84rem">
                    {risk_color} <strong>{risk:.0%} de chance</strong> de ficar abaixo da referência de 60 sc/ha
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Rode uma simulação para ver a distribuição do Monte Carlo aqui.")
            _info_card("O que o resultado mostra",
                "P5 = em 95% das simulações, a produtividade ficou acima desse valor\n"
                "P95 = em 95% das simulações, a produtividade ficou abaixo desse valor\n"
                "A faixa P5–P95 é o intervalo de 90% de confiança.")


def _render_step_10(result: dict | None) -> None:
    _step_header(10, "Recomendação Final",
        "O modelo combina todos os passos anteriores para apontar a estratégia com maior retorno esperado")

    _formula_box(
        "Recomendação = argmax<sub>i</sub> Σⱼ [ Payoff(i,j) + Interações(i,j) ] × P(chuvaⱼ | ENSO)"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("**Pipeline completo — do campo à recomendação:**")

    pipeline = [
        ("60 sc/ha", "Baseline CONAB", "#e8f5e9", "#1a5c38"),
        ("+ Contexto", "C1–C7 · solo, região, clima", "#e3f2fd", "#1565c0"),
        ("+ Decisões fixas", "D2 · D3 · D6", "#fff8e1", "#b35c00"),
        ("× 27 caminhos", "D1 × D4 × D5", "#f3e5f5", "#7b1fa2"),
        ("× 3 climas", "Seca · Normal · Úmida por ENSO", "#e0f2f1", "#00695c"),
        ("+ Interações", "3 termos de amplificação", "#fce4ec", "#c62828"),
        ("→ Matriz 27×3", "81 resultados possíveis", "#fff3e0", "#e65100"),
        ("→ Bayes EV", "Ponderação pelas probabilidades", "#e8f5e9", "#1a5c38"),
        ("→ Monte Carlo", "10.000 sim. · P5/P95", "#e3f2fd", "#1565c0"),
        ("🎯 Recomendação", "Melhor estratégia para o seu talhão", "#1a5c38", "#ffffff"),
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
        st.markdown("**Resultado da sua simulação:**")

        opt_idx  = result["criteria"]["bayes_ev"]["path_idx"]
        opt_path = result["paths"][opt_idx]
        opt_ev   = result["criteria"]["bayes_ev"]["value"]
        baseline = result["baseline"]
        mc       = opt_path.get("mc") or {}

        d1_s = {"Precoce (até 15/out)": "Precoce", "Ótima (16/out – 10/nov)": "Ótima", "Tardia (após 10/nov)": "Tardia"}
        d4_s = {"Baixa (≤280k sementes/ha)": "Baixa", "Média (280k–340k)": "Média", "Alta (>340k)": "Alta"}
        d5_s = {"Alto (≥3 fung. + monitor ferrugem)": "Intensivo", "Padrão (2 aplicações)": "Padrão", "Baixo (1 ou nenhuma)": "Reduzido"}

        delta = opt_ev - baseline
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#0d2b18,#1a5c38);border-radius:12px;
                    padding:28px 32px;color:#fff;margin-top:8px">
            <div style="font-size:0.7rem;font-weight:700;color:#76c442;text-transform:uppercase;
                        letter-spacing:0.12em;margin-bottom:10px">🎯 Recomendação Principal</div>
            <div style="display:flex;gap:40px;flex-wrap:wrap">
                <div>
                    <div style="font-size:0.7rem;color:rgba(255,255,255,0.6)">Janela de Plantio</div>
                    <div style="font-size:1rem;font-weight:700">{d1_s.get(opt_path["d1"], opt_path["d1"])}</div>
                </div>
                <div>
                    <div style="font-size:0.7rem;color:rgba(255,255,255,0.6)">Densidade</div>
                    <div style="font-size:1rem;font-weight:700">{d4_s.get(opt_path["d4"], opt_path["d4"])}</div>
                </div>
                <div>
                    <div style="font-size:0.7rem;color:rgba(255,255,255,0.6)">Manejo de Doenças</div>
                    <div style="font-size:1rem;font-weight:700">{d5_s.get(opt_path["d5"], opt_path["d5"])}</div>
                </div>
                <div>
                    <div style="font-size:0.7rem;color:rgba(255,255,255,0.6)">Prod. Esperada</div>
                    <div style="font-size:1.6rem;font-weight:900;color:#76c442">{opt_ev:.1f} sc/ha</div>
                    <div style="font-size:0.75rem;color:rgba(255,255,255,0.7)">{delta:+.1f} sc/ha vs. referência</div>
                </div>
                {f'<div><div style="font-size:0.7rem;color:rgba(255,255,255,0.6)">Intervalo 90%</div><div style="font-size:0.92rem;font-weight:600">{mc["p5"]:.0f} – {mc["p95"]:.0f} sc/ha</div></div>' if mc else ""}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Ver resultados completos →", type="primary"):
            nav_go("results")
    else:
        st.info("Rode uma simulação para ver a recomendação final aqui.")
        if st.button("Ir para Nova Simulação →", type="primary"):
            nav_go("input")


# ── CSS específico do painel ──────────────────────────────────────────────────

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


# ── Render principal ──────────────────────────────────────────────────────────

def render() -> None:
    st.markdown(_EXPLAINER_CSS, unsafe_allow_html=True)

    result = st.session_state.get("sim_result")

    st.markdown('<div class="page-title">Como o Simulador Calcula</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Entenda cada etapa do modelo — do baseline à recomendação final</div>',
        unsafe_allow_html=True,
    )

    if result:
        st.caption("✓ Usando dados da sua última simulação")
    else:
        st.caption("ℹ️ Rode uma simulação para ver seus dados reais em cada etapa")

    st.markdown("<br>", unsafe_allow_html=True)

    current = _step_key()
    _progress_bar(current)
    st.markdown("---")

    # Roteador de passos
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
