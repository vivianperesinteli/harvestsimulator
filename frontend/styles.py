"""Visual identity — Simulador de Safra."""

import streamlit as st

_CSS = """
<style>
/* ── Variáveis de cor ── */
:root {
  /* Cores do simulador */
  --green-900: #0d2b18;
  --green-700: #1a5c38;
  --green-500: #2d8a56;
  --green-300: #76c442;
  --green-100: #e8f5e9;
  --green-50:  #f1f8f3;
  --amber-500: #f4a024;
  --amber-dark: #b35c00;
  --amber-100: #fff8e1;
  --gray-900:  #1a1a2e;
  --gray-700:  #3a3a5c;
  --gray-500:  #6b6b8a;
  --gray-200:  #e4e4f0;
  --gray-100:  #fafaf8;
  --white:     #ffffff;
  --red-500:   #c62828;
  --red-100:   #fdecea;
  --blue-600:  #1565c0;
  --blue-100:  #e3f2fd;
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.08);
  --shadow-md: 0 4px 12px rgba(0,0,0,0.10);
  --shadow-lg: 0 8px 24px rgba(0,0,0,0.12);
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 16px;

  /* Sobrescreve variáveis de tema do Streamlit (impede modo escuro) */
  --text-color:                  #1a1a2e !important;
  --background-color:            #f4ecde !important;
  --secondary-background-color:  #e8e0d2 !important;
  --primary-color:               #1a5c38 !important;
}

/* ── Fundo creme com gradiente — body fixed ── */
html {
  background: #f4ecde !important;
}
body {
  background:
    /* Mancha verde no canto superior direito */
    radial-gradient(ellipse 70% 50% at 102% -2%,   rgba(45,138,86,0.28)  0%, transparent 55%),
    /* Mancha verde-escuro no canto inferior esquerdo */
    radial-gradient(ellipse 65% 55% at -2%  102%,  rgba(13,43,24,0.22)   0%, transparent 52%),
    /* Toque de verde-lima no canto inferior direito */
    radial-gradient(ellipse 50% 45% at 105% 105%,  rgba(118,196,66,0.14) 0%, transparent 55%),
    /* Brilho suave no canto superior esquerdo */
    radial-gradient(ellipse 40% 38% at -3%  -3%,   rgba(45,138,86,0.10)  0%, transparent 60%),
    /* Faixa central levemente mais escura — cria profundidade */
    radial-gradient(ellipse 80% 40% at 50%  55%,   rgba(210,185,155,0.18) 0%, transparent 70%),
    /* Linha diagonal de luz — textura */
    linear-gradient(
      118deg,
      #fdf8f0 0%,
      #f9f2e6 14%,
      #f4ecde 28%,
      #f7f0e8 42%,
      #efe8da 56%,
      #f3ece3 70%,
      #ece4d8 84%,
      #e8e0d2 100%
    ) !important;
  background-attachment: fixed !important;
  min-height: 100vh !important;
  color: #1a1a2e !important;
}

/* Todos os containers do Streamlit — transparentes para deixar body aparecer */
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMain"] > div,
.main,
[data-testid="stVerticalBlock"],
[data-testid="stVerticalBlockBorderWrapper"],
[data-testid="stHorizontalBlock"],
[data-testid="element-container"],
[data-testid="stColumn"],
[data-testid="column"] {
  background: transparent !important;
  color: #1a1a2e !important;
}
.stApp {
  min-height: 100vh !important;
}
.main .block-container {
  background: transparent !important;
  padding-top: 2rem !important;
  padding-left: 2.5rem !important;
  padding-right: 2.5rem !important;
  max-width: none !important;
}

/* ── Texto escuro universal — cobre todos os elementos nativos do Streamlit ── */
.stApp *:not([class*="sidebar"]):not(.landing-hero-col):not(.landing-hero):not(.landing-main-title):not(.landing-badge):not(.landing-main-desc):not(.landing-benefit-text):not(.landing-tag):not(.landing-desc):not(.nav-active):not(.nav-section-label):not(.sidebar-brand):not(.sidebar-brand-sub):not(.sidebar-user-name):not(.sidebar-user-role):not(.scope-label):not(.scope-value):not(.scope-dot):not([data-testid="stSidebar"] *) {
  color: #1a1a2e;
}

/* Seletores específicos com !important para garantir override do tema escuro */
[data-testid="stMain"] p,
[data-testid="stMain"] li,
[data-testid="stMain"] h1,
[data-testid="stMain"] h2,
[data-testid="stMain"] h3,
[data-testid="stMain"] h4,
[data-testid="stMain"] span,
[data-testid="stMain"] strong,
[data-testid="stMain"] em,
[data-testid="stMain"] label,
[data-testid="stMain"] small {
  color: #1a1a2e !important;
}

/* Markdown containers */
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stMarkdownContainer"] strong,
[data-testid="stMarkdownContainer"] em,
[data-testid="stMarkdownContainer"] span {
  color: #1a1a2e !important;
}

/* Labels de widgets */
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] span,
[data-testid="stWidgetLabel"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stRadio"] label,
div[data-testid="stTextInput"] label,
div[data-testid="stPasswordInput"] label,
div[data-testid="stNumberInput"] label,
div[data-testid="stDateInput"] label,
div[data-testid="stMultiSelect"] label,
div[data-testid="stCheckbox"] label,
div[data-testid="stSlider"] label {
  color: #1a1a2e !important;
}

/* Valores digitados nos campos de texto */
input[type="text"],
input[type="password"],
input[type="email"],
input[type="number"],
textarea {
  color: #1a1a2e !important;
  background-color: #ffffff !important;
}
input::placeholder, textarea::placeholder {
  color: #9090aa !important;
}

/* ── Olhinho de senha — botão dentro do input ── */
[data-baseweb="base-input"] button {
  background-color: transparent !important;
  border: none !important;
  outline: none !important;
  box-shadow: none !important;
}
/* Remove a linha preta/separador que o BaseUI coloca entre o input e o olhinho */
/* Cobre diretos e aninhados — emotion pode colocar o border em qualquer div */
[data-baseweb="base-input"] div,
[data-baseweb="base-input"] > div,
[data-baseweb="base-input"] > div > div,
[data-baseweb="base-input"] > div:last-child {
  border: none !important;
  border-left: none !important;
  border-right: none !important;
  box-shadow: none !important;
  background: transparent !important;
}
[data-baseweb="base-input"] button svg,
[data-baseweb="base-input"] button svg path,
[data-baseweb="base-input"] button svg g {
  fill: #6b6b8a !important;
  stroke: none !important;
}
[data-baseweb="base-input"] button:hover svg,
[data-baseweb="base-input"] button:hover svg path {
  fill: #1a1a2e !important;
}

/* ── Esconde o texto "Press Enter" do Streamlit (InputInstructions) ── */
[data-testid="InputInstructions"] {
  display: none !important;
}

/* ── Código inline <code> — fundo claro, texto escuro ── */
code {
  background-color: rgba(26, 92, 56, 0.1) !important;
  color: #1a5c38 !important;
  padding: 1px 5px !important;
  border-radius: 4px !important;
  font-size: 0.85em !important;
}
/* Garante que code dentro de caixa clara também fica claro */
[data-testid="stMarkdownContainer"] code,
.stMarkdown code {
  background-color: rgba(26, 92, 56, 0.1) !important;
  color: #1a5c38 !important;
}

/* Tabs (abas: Entrar / Criar conta) */
[data-testid="stTabs"] button,
[data-testid="stTabs"] button p,
[data-testid="stTabs"] button span,
[data-baseweb="tab"],
[data-baseweb="tab"] span,
button[role="tab"],
button[role="tab"] p {
  color: #1a1a2e !important;
}
[data-testid="stTabs"] button[aria-selected="true"],
[data-testid="stTabs"] button[aria-selected="true"] p {
  color: #1a5c38 !important;
  font-weight: 700 !important;
}

/* Expanders */
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span,
[data-testid="stExpander"] p {
  color: #1a1a2e !important;
}

/* Alertas nativos (st.info / st.success / st.error) */
[data-testid="stAlert"] p,
[data-testid="stAlert"] span,
[data-testid="stAlert"] li {
  color: #1a1a2e !important;
}

/* Caption */
[data-testid="stCaptionContainer"] p,
.stCaption p {
  color: #3a3a5c !important;
}

/* ── Selectbox / multiselect — container (dentro do stMain) ── */
div[data-baseweb="select"] > div,
div[data-baseweb="select"] > div > div {
  background-color: #ffffff !important;
  color: #1a1a2e !important;
}
[data-baseweb="select"] span,
[data-baseweb="select"] [data-value] {
  color: #1a1a2e !important;
}

/* ── Dropdown aberto — renderizado como portal FORA do stMain ── */
/* Cobre qualquer listbox/popover independente de onde está no DOM  */
[data-baseweb="popover"] {
  background-color: #ffffff !important;
}
[data-baseweb="popover"] * {
  color: #1a1a2e !important;
}
[data-baseweb="menu"] {
  background-color: #ffffff !important;
}
[data-baseweb="menu"] *,
[data-baseweb="menu"] li,
[data-baseweb="menu"] ul {
  background-color: #ffffff !important;
  color: #1a1a2e !important;
}
[data-baseweb="option"] {
  background-color: #ffffff !important;
  color: #1a1a2e !important;
}
[data-baseweb="option"] * {
  background-color: transparent !important;
  color: #1a1a2e !important;
}
[data-baseweb="option"]:hover {
  background-color: #e8f5e9 !important;
}
[data-baseweb="option"]:hover * {
  color: #1a5c38 !important;
}
[data-baseweb="option"][aria-selected="true"] {
  background-color: #e8f5e9 !important;
  color: #1a5c38 !important;
}
/* Fallback por role — garante cobertura em versões diferentes do Streamlit */
[role="listbox"] {
  background-color: #ffffff !important;
}
[role="listbox"] * {
  color: #1a1a2e !important;
}
[role="option"] {
  background-color: #ffffff !important;
  color: #1a1a2e !important;
}
[role="option"]:hover {
  background-color: #e8f5e9 !important;
  color: #1a5c38 !important;
}
/* Dropdown do multiselect / selectbox via testid */
[data-testid="stSelectboxVirtualDropdown"],
[data-testid="stSelectboxVirtualDropdown"] * {
  background-color: #ffffff !important;
  color: #1a1a2e !important;
}

/* ── Radio buttons ── */
div[data-testid="stRadio"] label,
div[data-testid="stRadio"] [data-testid="stMarkdownContainer"] p,
div[data-testid="stRadio"] span {
  color: #1a1a2e !important;
}

/* ── Multiselect — tags ── */
div[data-testid="stMultiSelect"] [data-baseweb="tag"],
div[data-testid="stMultiSelect"] [data-baseweb="tag"] span {
  background-color: #e8f5e9 !important;
  color: #1a5c38 !important;
}

/* ── Calendário (date picker) ── */
/* ESTRATÉGIA: o calendário abre num portal direto em body — sem herdar
   estilos do #root. Usamos :has() para pegar o wrapper anônimo do portal
   e html body para especificidade (0,1,0,2) nas regras internas.       */

/* 1. Portal anônimo: qualquer div direto do body que contenha o calendário */
body > div:has([data-baseweb="calendar"]),
body > div:has([data-baseweb="calendar"]) > * {
  background: #ffffff !important;
  background-color: #ffffff !important;
}

/* 2. Popover + wrapper */
html body [data-baseweb="popover"],
html body [data-baseweb="popover"] > div,
html body [data-baseweb="popover"] > div > div {
  background: #ffffff !important;
  background-color: #ffffff !important;
  border: 1px solid #b8dfc6 !important;
  border-radius: 12px !important;
  box-shadow: 0 8px 32px rgba(13,43,24,0.14), 0 2px 8px rgba(0,0,0,0.07) !important;
}

/* 3. Calendário raiz — branco */
html body [data-baseweb="calendar"] {
  background: #ffffff !important;
  background-color: #ffffff !important;
  border-radius: 10px !important;
  overflow: hidden !important;
}

/* 4. Reset geral: texto verde-escuro, sem cor de fundo nos wrappers de layout */
html body [data-baseweb="calendar"] * {
  color: #1a3a2a !important;
  border-color: #c8e6d4 !important;
}

/* 5. GRID e CÉLULAS — background BRANCO (não transparente!).
      Células vazias sem conteúdo herdariam fundo escuro se fossem transparent.
      Qualquer div com role de grid/row/cell recebe branco explícito.          */
html body [data-baseweb="calendar"] [role="grid"],
html body [data-baseweb="calendar"] [role="row"],
html body [data-baseweb="calendar"] [role="gridcell"],
html body [data-baseweb="calendar"] [role="columnheader"],
html body [data-baseweb="calendar"] table,
html body [data-baseweb="calendar"] tbody,
html body [data-baseweb="calendar"] thead,
html body [data-baseweb="calendar"] tr,
html body [data-baseweb="calendar"] td,
html body [data-baseweb="calendar"] th {
  background: #ffffff !important;
  background-color: #ffffff !important;
  color: #1a3a2a !important;
}

/* 6. Conteúdo DENTRO das células — transparente (o branco da célula aparece) */
html body [data-baseweb="calendar"] [role="gridcell"] > *,
html body [data-baseweb="calendar"] [role="row"] > div:not([role="gridcell"]) {
  background: transparent !important;
  background-color: transparent !important;
}

/* 6. Botões de navegar mês */
html body [data-baseweb="calendar"] button {
  color: #1a5c38 !important;
  border: none !important;
  border-radius: 6px !important;
  font-weight: 600 !important;
  background: transparent !important;
}
html body [data-baseweb="calendar"] button:hover {
  background: #e8f5e9 !important;
  background-color: #e8f5e9 !important;
  color: #0d2b18 !important;
}

/* 7. Cabeçalho dias da semana */
html body [data-baseweb="calendar"] [role="columnheader"],
html body [data-baseweb="calendar"] [role="columnheader"] * {
  color: #2d8a56 !important;
  font-weight: 700 !important;
  font-size: 0.72rem !important;
  letter-spacing: 0.04em !important;
  background: transparent !important;
}

/* 8. Dias desabilitados / outros meses */
html body [data-baseweb="calendar"] button[disabled],
html body [data-baseweb="calendar"] [aria-disabled="true"] button {
  color: rgba(45,138,86,0.32) !important;
  font-weight: 400 !important;
  background: transparent !important;
}

/* 9. Dia normal */
html body [data-baseweb="calendar"] [role="gridcell"] button {
  color: #1a3a2a !important;
  border-radius: 50% !important;
  font-weight: 500 !important;
  background: transparent !important;
}
html body [data-baseweb="calendar"] [role="gridcell"] button:hover {
  background: #e8f5e9 !important;
  background-color: #e8f5e9 !important;
  color: #0d2b18 !important;
}

/* 10. Dia selecionado */
html body [data-baseweb="calendar"] [aria-selected="true"] button,
html body [data-baseweb="calendar"] [data-selected="true"] button {
  background: #1a5c38 !important;
  background-color: #1a5c38 !important;
  color: #ffffff !important;
  border-radius: 50% !important;
  font-weight: 700 !important;
  box-shadow: 0 2px 8px rgba(13,43,24,0.3) !important;
}
html body [data-baseweb="calendar"] [aria-selected="true"] *,
html body [data-baseweb="calendar"] [data-selected="true"] * {
  color: #ffffff !important;
  background: transparent !important;
}

/* 11. Range entre datas */
html body [data-baseweb="calendar"] [data-range-highlight="true"] {
  background: #e8f5e9 !important;
  background-color: #e8f5e9 !important;
}
html body [data-baseweb="calendar"] [data-range-highlight="true"] button {
  background: transparent !important;
  color: #1a3a2a !important;
}

/* 12. Select mês/ano */
html body [data-baseweb="calendar"] select {
  background: #ffffff !important;
  color: #1a5c38 !important;
  font-weight: 700 !important;
  border: 1px solid #c8e6d4 !important;
  border-radius: 6px !important;
}

/* Input de data — campo de texto */
[data-testid="stDateInput"] input {
  background: #ffffff !important;
  background-color: #ffffff !important;
  color: #1a1a2e !important;
}
[data-testid="stDateInput"] [data-baseweb="base-input"] {
  background: #ffffff !important;
  background-color: #ffffff !important;
}

/* ── Number input — botões +/− ── */
div[data-testid="stNumberInput"] [data-testid="stNumberInputStepUp"],
div[data-testid="stNumberInput"] [data-testid="stNumberInputStepDown"],
div[data-testid="stNumberInput"] button {
  background-color: #f0f2f6 !important;
  color: #1a1a2e !important;
  border: 1px solid #d0d0e0 !important;
}
div[data-testid="stNumberInput"] button:hover {
  background-color: #e8f5e9 !important;
  color: #1a5c38 !important;
}
div[data-testid="stNumberInput"] button svg,
div[data-testid="stNumberInput"] button svg path {
  fill: #1a1a2e !important;
  stroke: #1a1a2e !important;
}
div[data-testid="stNumberInput"] input {
  background-color: #ffffff !important;
  color: #1a1a2e !important;
}
div[data-testid="stNumberInput"] [data-baseweb="base-input"] {
  background-color: #ffffff !important;
}

/* ── Checkbox ── */
[data-testid="stCheckbox"] label {
  color: #1a1a2e !important;
}
[data-testid="stCheckbox"] span,
[data-testid="stCheckbox"] p {
  color: #1a1a2e !important;
}
[data-baseweb="checkbox"] [data-baseweb="icon"] {
  background-color: #1a5c38 !important;
  border-color: #1a5c38 !important;
}
/* Checkbox box não-selecionado */
[data-baseweb="checkbox"] > div:first-child {
  background-color: #ffffff !important;
  border-color: #b0b0c0 !important;
}

/* ── Select slider ── */
[data-testid="stSlider"] div[data-testid="stTickBar"] span {
  color: #3a3a5c !important;
}
[data-testid="stSlider"] [role="slider"] {
  background-color: #1a5c38 !important;
}
[data-testid="stSlider"] [data-testid="stMarkdownContainer"] p {
  color: #1a1a2e !important;
}

/* ── Plotly SVG — força texto escuro nos eixos e legendas ── */
.js-plotly-plot .ytick text,
.js-plotly-plot .xtick text,
.js-plotly-plot .legendtext,
.js-plotly-plot .gtitle,
.js-plotly-plot .annotation-text {
  fill: #1a1a2e !important;
}
.js-plotly-plot .gridlayer .ygrid,
.js-plotly-plot .gridlayer .xgrid {
  stroke: #d0d0e0 !important;
}

/* ── Inputs genéricos (baseweb) ── */
div[data-baseweb="base-input"] {
  background-color: #ffffff !important;
}
div[data-baseweb="base-input"] input {
  background-color: #ffffff !important;
  color: #1a1a2e !important;
}

/* ── Multiselect tokens ── */
[data-baseweb="tag"] {
  background-color: #e8f5e9 !important;
  color: #1a5c38 !important;
}
[data-baseweb="tag"] span {
  color: #1a5c38 !important;
}
[data-baseweb="tag"] [data-baseweb="icon"] {
  color: #1a5c38 !important;
  fill: #1a5c38 !important;
}

/* ── Reset / Base — esconde todos os elementos nativos do Streamlit ── */
#MainMenu,
header,
footer,
[data-testid="stHeader"],
[data-testid="stDecoration"],
[data-testid="stDeployButton"],
[data-testid="stStatusWidget"],
[data-testid="stToolbar"],
.stDeployButton {
  display: none !important;
  height: 0 !important;
  min-height: 0 !important;
  overflow: hidden !important;
}
/* Remove padding-top que o Streamlit reserva pro header */
[data-testid="stAppViewContainer"] > section:first-child {
  padding-top: 0 !important;
}
[data-testid="stMain"] {
  padding-top: 0 !important;
  background: transparent !important;
}

/* ── Sidebar — força alinhamento à esquerda em todos os textos ── */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
  text-align: left !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
  background:
    repeating-linear-gradient(
      -58deg,
      transparent 0px, transparent 38px,
      rgba(118,196,66,0.018) 38px, rgba(118,196,66,0.018) 39px
    ),
    radial-gradient(ellipse 80% 50% at 50% 80%, rgba(29,92,56,0.35) 0%, transparent 70%),
    linear-gradient(180deg, #0d2b18 0%, #091a0f 100%) !important;
  border-right: 1px solid rgba(255,255,255,0.05);
}
section[data-testid="stSidebar"] > div:first-child {
  background: transparent !important;
  padding-top: 0 !important;
}
/* Remove padding interno do Streamlit que empurra o conteúdo da sidebar pra baixo */
section[data-testid="stSidebar"] [data-testid="stSidebarContent"],
section[data-testid="stSidebar"] > div > div:first-child,
section[data-testid="stSidebar"] > div > div {
  padding-top: 0 !important;
  margin-top: 0 !important;
}
/* Remove gap do bloco vertical da sidebar e puxa o logo para o topo */
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"],
section[data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] {
  gap: 0 !important;
  padding-top: 0 !important;
  margin-top: 0 !important;
}
/* O primeiro element-container da sidebar (que contém o logo) sobe ao topo */
section[data-testid="stSidebar"] [data-testid="element-container"]:first-of-type {
  margin-top: 0 !important;
  padding-top: 0 !important;
}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] small,
section[data-testid="stSidebar"] label {
  color: rgba(255,255,255,0.65) !important;
}
section[data-testid="stSidebar"] hr {
  border-color: rgba(255,255,255,0.08) !important;
  margin: 12px 0 !important;
}
section[data-testid="stSidebar"] .stButton > button {
  background: transparent !important;
  border: none !important;
  color: rgba(255,255,255,0.65) !important;
  text-align: left !important;
  width: 100% !important;
  padding: 8px 10px 8px 18px !important;
  font-size: 0.86rem !important;
  font-weight: 400 !important;
  border-radius: var(--radius-sm) !important;
  transition: all 0.15s ease !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
  background: rgba(118,196,66,0.1) !important;
  color: rgba(255,255,255,0.95) !important;
}

/* ── Nav items — botão ativo na sidebar ── */
section[data-testid="stSidebar"] button[data-testid="baseButton-primary"] {
  background: linear-gradient(90deg, rgba(118,196,66,0.22) 0%, rgba(118,196,66,0.05) 100%) !important;
  border-left: 3px solid #76c442 !important;
  border-top: none !important;
  border-right: none !important;
  border-bottom: none !important;
  color: #ffffff !important;
  border-radius: 0 6px 6px 0 !important;
  font-weight: 600 !important;
  font-size: 0.86rem !important;
  text-shadow: 0 0 16px rgba(118,196,66,0.25) !important;
  box-shadow: none !important;
  text-align: left !important;
  padding: 10px 10px 10px 15px !important;
  margin-bottom: 2px !important;
}
section[data-testid="stSidebar"] button[data-testid="baseButton-primary"]:hover {
  background: linear-gradient(90deg, rgba(118,196,66,0.30) 0%, rgba(118,196,66,0.10) 100%) !important;
}
/* Botão inativo — estilo padrão sidebar */
section[data-testid="stSidebar"] button[data-testid="baseButton-secondary"] {
  background: transparent !important;
  border: none !important;
  color: rgba(255,255,255,0.75) !important;
  font-size: 0.86rem !important;
  text-align: left !important;
  padding: 10px 10px 10px 18px !important;
  box-shadow: none !important;
  border-radius: 0 6px 6px 0 !important;
  margin-bottom: 2px !important;
}
section[data-testid="stSidebar"] button[data-testid="baseButton-secondary"]:hover {
  background: rgba(255,255,255,0.06) !important;
  color: #ffffff !important;
}
/* Botão desabilitado (ex: Dashboard sem resultado) */
section[data-testid="stSidebar"] button[data-testid="baseButton-secondary"]:disabled,
section[data-testid="stSidebar"] button[disabled] {
  color: rgba(255,255,255,0.25) !important;
  background: transparent !important;
  cursor: default !important;
}
.nav-section-label {
  font-size: 0.65rem;
  font-weight: 700;
  color: rgba(255,255,255,0.55) !important;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  padding: 6px 10px 6px 18px;
  margin-top: 16px;
  display: block;
}

/* ── Sidebar logo ── */
.sidebar-logo-area {
  padding: 20px 18px 24px 18px;
  border-bottom: 1px solid rgba(255,255,255,0.09);
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 14px;
}
.sidebar-logo-circle {
  width: 44px; height: 44px;
  background: linear-gradient(145deg, #1a5c38 0%, #0d2b18 100%);
  border-radius: 13px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 4px 16px rgba(118,196,66,0.28), 0 2px 6px rgba(0,0,0,0.28);
  position: relative;
  overflow: hidden;
}
.sidebar-logo-circle::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(145deg, rgba(118,196,66,0.14) 0%, transparent 60%);
  pointer-events: none;
}
.sidebar-brand {
  color: #ffffff !important;
  font-size: 1.0rem;
  font-weight: 700;
  display: block;
  line-height: 1.15;
  letter-spacing: -0.01em;
}
.sidebar-brand-sub {
  color: rgba(255,255,255,0.60) !important;
  font-size: 0.70rem;
  display: block;
  margin-top: 2px;
}
.sidebar-user {
  padding: 12px 16px;
  border-top: 1px solid rgba(255,255,255,0.07);
  margin-top: 8px;
}
.sidebar-user-name {
  color: rgba(255,255,255,0.8) !important;
  font-size: 0.8rem;
  font-weight: 500;
}
.sidebar-user-role {
  color: rgba(255,255,255,0.62) !important;
  font-size: 0.68rem;
}
.sidebar-scope {
  padding: 10px 16px 16px 18px;
  border-top: 1px solid rgba(255,255,255,0.07);
  margin-top: 4px;
}
.scope-label { color: rgba(255,255,255,0.58) !important; font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.08em; }
.scope-value { color: rgba(255,255,255,0.85) !important; font-size: 0.78rem; font-weight: 500; display: flex; align-items: center; gap: 6px; margin-top: 2px; }
.scope-dot { width: 7px; height: 7px; background: var(--green-300); border-radius: 50%; display: inline-block; }

/* ── Page titles ── */
.page-title {
  font-size: 1.65rem;
  font-weight: 800;
  background: linear-gradient(135deg, #0d2b18 0%, #1a5c38 60%, #2d8a56 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  color: transparent !important;
  margin-bottom: 2px;
  letter-spacing: -0.025em;
  line-height: 1.2;
  display: inline-block;
}
.page-subtitle {
  font-size: 0.83rem;
  color: var(--gray-500);
  margin-top: 0;
  margin-bottom: 6px;
  letter-spacing: 0.01em;
}

/* ── Section headers ── */
.section-hdr {
  font-size: 0.68rem;
  font-weight: 700;
  color: var(--green-700);
  text-transform: uppercase;
  letter-spacing: 0.13em;
  padding: 2px 0 2px 12px;
  border-left: 3px solid var(--green-300);
  margin: 34px 0 16px 0;
  line-height: 1.5;
}

/* ── Metric cards ── */
.metric-card {
  background: var(--white);
  border: 1px solid var(--gray-200);
  border-top: 3px solid var(--green-300);
  border-radius: 0 0 var(--radius-md) var(--radius-md);
  padding: 16px 18px;
  box-shadow: 0 2px 10px rgba(13,43,24,0.07), 0 1px 3px rgba(0,0,0,0.04);
}
.mc-label { font-size: 0.7rem; color: var(--gray-700); margin-bottom: 2px; text-transform: uppercase; letter-spacing: 0.06em; font-weight: 600; }
.mc-value { font-size: 1.7rem; font-weight: 800; color: var(--gray-900); line-height: 1.1; }
.mc-sub   { font-size: 0.72rem; color: var(--gray-700); margin-top: 2px; }
.mc-caption { font-size: 0.7rem; color: var(--gray-700); margin-top: 6px; font-style: italic; line-height: 1.3; }

/* ── Buttons ── */
div[data-testid="stButton"] > button[kind="primary"],
div[data-testid="stFormSubmitButton"] > button[kind="primary"],
div[data-testid="stFormSubmitButton"] > button {
  background: linear-gradient(135deg, #1a5c38 0%, #2d8a56 100%) !important;
  color: #ffffff !important;
  border: none !important;
  border-radius: 8px !important;
  font-size: 0.88rem !important;
  font-weight: 700 !important;
  padding: 10px 24px !important;
  transition: all 0.2s ease !important;
  box-shadow: 0 4px 16px rgba(13,43,24,0.3), 0 1px 4px rgba(0,0,0,0.08) !important;
  letter-spacing: 0.01em !important;
}
div[data-testid="stButton"] > button[kind="primary"] p,
div[data-testid="stButton"] > button[kind="primary"] span,
div[data-testid="stFormSubmitButton"] > button p,
div[data-testid="stFormSubmitButton"] > button span {
  color: #ffffff !important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover,
div[data-testid="stFormSubmitButton"] > button:hover {
  transform: translateY(-1px) !important;
  box-shadow: 0 6px 24px rgba(13,43,24,0.42), 0 2px 8px rgba(0,0,0,0.1) !important;
  background: linear-gradient(135deg, #1a5c38 0%, #38a76a 100%) !important;
}
/* Botões secundários, default e form_submit — fundo branco, texto escuro */
div[data-testid="stButton"] > button[kind="secondary"],
div[data-testid="stButton"] > button:not([kind="primary"]),
div[data-testid="stFormSubmitButton"] > button:not([kind="primary"]) {
  background: #ffffff !important;
  background-color: #ffffff !important;
  color: #1a1a2e !important;
  border: 1px solid #d0d0e0 !important;
  border-radius: var(--radius-sm) !important;
  font-size: 0.88rem !important;
  font-weight: 500 !important;
  transition: all 0.15s ease !important;
}
div[data-testid="stButton"] > button[kind="secondary"]:hover,
div[data-testid="stButton"] > button:not([kind="primary"]):hover,
div[data-testid="stFormSubmitButton"] > button:not([kind="primary"]):hover {
  background: #f1f8f3 !important;
  background-color: #f1f8f3 !important;
  border-color: var(--green-700) !important;
  color: var(--green-700) !important;
}
/* Download buttons */
div[data-testid="stDownloadButton"] > button {
  background: #ffffff !important;
  background-color: #ffffff !important;
  color: #1a1a2e !important;
  border: 1px solid #d0d0e0 !important;
  border-radius: var(--radius-sm) !important;
  font-size: 0.88rem !important;
}
div[data-testid="stDownloadButton"] > button:hover {
  background: #f1f8f3 !important;
  background-color: #f1f8f3 !important;
  border-color: var(--green-700) !important;
  color: var(--green-700) !important;
}
/* Garante que texto dentro dos botões secundários fica escuro */
div[data-testid="stButton"] > button:not([kind="primary"]) p,
div[data-testid="stButton"] > button:not([kind="primary"]) span,
div[data-testid="stDownloadButton"] > button p,
div[data-testid="stDownloadButton"] > button span {
  color: #1a1a2e !important;
}

/* ── Sidebar buttons — transparente, sem borda, texto claro ── */
/* Cobre class .stButton, data-testid=stButton e BaseButton do Streamlit 1.58 */
section[data-testid="stSidebar"] div[data-testid="stButton"],
section[data-testid="stSidebar"] div[data-testid="stButton"] > div,
section[data-testid="stSidebar"] .stButton,
section[data-testid="stSidebar"] .stButton > div {
  background: transparent !important;
  background-color: transparent !important;
  box-shadow: none !important;
  border: none !important;
}
section[data-testid="stSidebar"] div[data-testid="stButton"] > button,
section[data-testid="stSidebar"] div[data-testid="stButton"] > button:not([kind="primary"]),
section[data-testid="stSidebar"] .stButton > button,
section[data-testid="stSidebar"] .stButton > button:not([kind="primary"]),
section[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"],
section[data-testid="stSidebar"] button[kind="secondary"] {
  background: transparent !important;
  background-color: transparent !important;
  color: rgba(255,255,255,0.65) !important;
  border: none !important;
  box-shadow: none !important;
  outline: none !important;
  text-align: left !important;
  width: 100% !important;
  padding: 8px 10px 8px 18px !important;
  font-size: 0.86rem !important;
  font-weight: 400 !important;
  border-radius: var(--radius-sm) !important;
}
section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover,
section[data-testid="stSidebar"] div[data-testid="stButton"] > button:not([kind="primary"]):hover,
section[data-testid="stSidebar"] .stButton > button:hover,
section[data-testid="stSidebar"] .stButton > button:not([kind="primary"]):hover,
section[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"]:hover,
section[data-testid="stSidebar"] button[kind="secondary"]:hover {
  background: rgba(118,196,66,0.1) !important;
  background-color: rgba(118,196,66,0.1) !important;
  color: rgba(255,255,255,0.95) !important;
  border: none !important;
}
section[data-testid="stSidebar"] div[data-testid="stButton"] > button p,
section[data-testid="stSidebar"] div[data-testid="stButton"] > button span,
section[data-testid="stSidebar"] .stButton > button p,
section[data-testid="stSidebar"] .stButton > button span,
section[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] p,
section[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"] span {
  color: inherit !important;
  text-align: left !important;
}
/* Força alinhamento esquerda em tudo na sidebar — botões e containers */
section[data-testid="stSidebar"] button {
  justify-content: flex-start !important;
  text-align: left !important;
  display: flex !important;
  align-items: center !important;
}
section[data-testid="stSidebar"] button * {
  justify-content: flex-start !important;
  text-align: left !important;
  flex: 1 !important;
}
/* Containers de botão e markdown na sidebar */
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] * {
  text-align: left !important;
}
section[data-testid="stSidebar"] [data-testid^="stButton"],
section[data-testid="stSidebar"] [data-testid^="stBaseButton"] {
  text-align: left !important;
  justify-content: flex-start !important;
}
section[data-testid="stSidebar"] [data-testid^="stBaseButton"] * {
  text-align: left !important;
  justify-content: flex-start !important;
}

/* ── Metric widget — texto escuro, fundo transparente ── */
[data-testid="stMetric"] {
  background: transparent !important;
}
[data-testid="stMetricLabel"] p,
[data-testid="stMetricLabel"] span,
[data-testid="stMetricLabel"] label,
[data-testid="stMetricLabel"] div {
  color: #6b6b8a !important;
  font-size: 0.78rem !important;
}
[data-testid="stMetricValue"] span,
[data-testid="stMetricValue"] div {
  color: #1a1a2e !important;
}
[data-testid="stMetricDelta"] p,
[data-testid="stMetricDelta"] span {
  font-size: 0.78rem !important;
}

/* ── Expanders — fundo branco ── */
[data-testid="stExpander"] details {
  background-color: #ffffff !important;
  border: 1px solid #e4e4f0 !important;
  border-radius: 8px !important;
}
[data-testid="stExpander"] details summary {
  background-color: #fafaf8 !important;
  border-radius: 8px !important;
  padding: 10px 16px !important;
  color: #1a1a2e !important;
}
[data-testid="stExpander"] details summary p,
[data-testid="stExpander"] details summary span {
  color: #1a1a2e !important;
  font-weight: 600 !important;
}

/* ── Alert / info boxes — fundo claro ── */
div[data-baseweb="notification"] {
  background-color: #e3f2fd !important;
}
[data-testid="stAlert"] {
  background-color: #e3f2fd !important;
}
/* success */
[data-testid="stAlert"][data-type="success"],
div.stSuccess > div[data-baseweb="notification"] {
  background-color: #e8f5e9 !important;
}
/* error/warning */
[data-testid="stAlert"][data-type="error"],
div.stError > div[data-baseweb="notification"] {
  background-color: #fdecea !important;
}
[data-testid="stAlert"][data-type="warning"],
div.stWarning > div[data-baseweb="notification"] {
  background-color: #fff8e1 !important;
}
[data-testid="stAlert"] p,
[data-testid="stAlert"] span,
[data-testid="stAlert"] li,
div[data-baseweb="notification"] p,
div[data-baseweb="notification"] span {
  color: #1a1a2e !important;
}

/* ── Gráficos Plotly — container branco ── */
[data-testid="stPlotlyChart"] {
  background: #ffffff !important;
  border-radius: 8px !important;
}
.js-plotly-plot, .plotly, .plot-container {
  background: #ffffff !important;
}

/* ── Dataframe / tabela ── */
[data-testid="stDataFrame"],
[data-testid="stDataFrame"] > div {
  background: #ffffff !important;
  border-radius: 8px !important;
}
/* AG Grid cells */
.ag-theme-streamlit,
.ag-root-wrapper,
.ag-root,
.ag-body-viewport,
.ag-center-cols-container {
  background-color: #ffffff !important;
  color: #1a1a2e !important;
}
.ag-header, .ag-header-row, .ag-header-cell {
  background-color: #f0f2f6 !important;
  color: #1a1a2e !important;
}
.ag-cell, .ag-cell-value {
  color: #1a1a2e !important;
}
.ag-row-odd {
  background-color: #fafaf8 !important;
}
.ag-row-even {
  background-color: #ffffff !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] p,
[data-testid="stSpinner"] span {
  color: #1a1a2e !important;
}

/* ── Divider ── */
[data-testid="stDivider"] hr,
.stDivider hr {
  border-color: #e4e4f0 !important;
}

/* ── Recommendation cards ── */
.rec-card-v2 {
  background: var(--white);
  border: 1px solid var(--gray-200);
  border-radius: var(--radius-lg);
  padding: 24px 28px;
  margin-bottom: 20px;
  box-shadow: var(--shadow-sm);
  transition: box-shadow 0.2s ease, transform 0.15s ease;
}
.rec-card-v2:hover { box-shadow: var(--shadow-md); transform: translateY(-1px); }
.rec-card-v2.rank-1 {
  border: 1.5px solid rgba(45,138,86,0.4);
  border-top: 5px solid var(--green-500);
  background: linear-gradient(180deg, rgba(118,196,66,0.04) 0%, #ffffff 60px);
  box-shadow: 0 6px 32px rgba(13,43,24,0.12), 0 1px 4px rgba(0,0,0,0.05);
}
.rec-card-v2.rank-1:hover { box-shadow: 0 10px 40px rgba(13,43,24,0.18); }
.rec-card-v2.rank-2 {
  border-left: 4px solid var(--amber-500);
  opacity: 0.95;
}
.rec-card-v2.rank-3 {
  border-left: 4px solid var(--gray-300);
  opacity: 0.88;
}

.rec-rank-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--green-700);
  color: #ffffff;
  padding: 4px 14px;
  border-radius: 20px;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 12px;
}
.rec-rank-badge.rank-1 {
  background: linear-gradient(135deg, #1a5c38 0%, #2d8a56 100%);
  padding: 5px 16px;
  font-size: 0.78rem;
}
/* amber claro → texto escuro para garantir contraste 4.5:1+ */
.rec-rank-badge.rank-2 { background: var(--amber-dark); color: #ffffff; }
.rec-rank-badge.rank-3 { background: #4e4e6a; color: #ffffff; }

.rec-summary-text {
  font-size: 0.9rem;
  color: var(--gray-700);
  line-height: 1.65;
  margin: 12px 0 18px 0;
  padding: 14px 18px;
  background: var(--green-50);
  border-radius: var(--radius-sm);
  border-left: 3px solid var(--green-300);
}
.rec-card-v2.rank-1 .rec-summary-text {
  font-size: 0.92rem;
  background: linear-gradient(90deg, rgba(118,196,66,0.08) 0%, rgba(118,196,66,0.03) 100%);
  border-left: 4px solid var(--green-500);
}

.rec-yield-big {
  font-size: 3.2rem;
  font-weight: 900;
  color: var(--gray-900);
  line-height: 1;
  letter-spacing: -0.03em;
}
.rec-card-v2.rank-1 .rec-yield-big { font-size: 3.6rem; color: #1a5c38; }
.rec-yield-unit { font-size: 0.82rem; color: var(--gray-700); font-weight: 500; }
.rec-yield-range { font-size: 0.78rem; color: var(--gray-700); margin-top: 4px; }
.rec-yield-interval {
  font-size: 0.78rem;
  color: var(--green-700);
  font-weight: 600;
  margin-top: 3px;
}
.rec-risk-label {
  font-size: 0.75rem;
  color: var(--gray-700);
  margin-top: 6px;
}

.rec-criteria-row { display: flex; flex-wrap: wrap; gap: 6px; margin: 10px 0; }
.crit-tag {
  display: inline-block;
  background: var(--green-100);
  color: var(--green-700);
  border: 1px solid rgba(45,138,86,0.3);
  padding: 3px 10px;
  border-radius: 20px;
  font-size: 0.72rem;
  font-weight: 600;
}
.crit-tag.secondary { background: var(--amber-100); color: #7a3500; border-color: rgba(179,92,0,0.3); }

.rec-decisions-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-top: 14px;
  padding-top: 14px;
  border-top: 1px solid var(--gray-200);
}
.dec-item { }
.dec-label { font-size: 0.67rem; color: var(--gray-700); text-transform: uppercase; letter-spacing: 0.07em; font-weight: 600; }
.dec-value { font-size: 0.84rem; font-weight: 600; color: var(--gray-900); margin-top: 2px; }

/* ── Action bar (export/PDF) ── */
.rec-action-bar {
  display: flex;
  gap: 8px;
  margin-top: 16px;
  padding-top: 14px;
  border-top: 1px solid var(--gray-200);
  flex-wrap: wrap;
}

/* ── Scenario sidebar (resultados) ── */
.scenario-sidebar {
  background: var(--white);
  border: 1px solid var(--gray-200);
  border-top: 3px solid var(--green-300);
  border-radius: 0 0 var(--radius-md) var(--radius-md);
  padding: 16px 18px;
  box-shadow: 0 2px 10px rgba(13,43,24,0.07);
  position: sticky;
  top: 1rem;
}
.scenario-sidebar-title {
  font-size: 0.67rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--gray-700);
  padding-bottom: 10px;
  border-bottom: 1px solid var(--gray-200);
  margin-bottom: 10px;
}
.scenario-row {
  display: flex;
  justify-content: space-between;
  padding: 5px 0;
  border-bottom: 1px solid var(--gray-200);
  font-size: 0.76rem;
}
.scenario-row:last-child { border-bottom: none; }
.scenario-key { color: var(--gray-700); font-weight: 500; }
.scenario-val { color: var(--gray-900); font-weight: 600; text-align: right; max-width: 55%; word-break: break-word; }

/* ── Why-not section ── */
.why-not-card {
  background: var(--gray-100);
  border: 1px solid var(--gray-200);
  border-radius: var(--radius-md);
  padding: 16px 20px;
  margin-top: 8px;
}
.why-not-title { font-size: 0.82rem; font-weight: 700; color: var(--gray-900); margin-bottom: 10px; }
.why-not-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
  border-bottom: 1px solid var(--gray-200);
  font-size: 0.8rem;
}
.why-not-path { color: var(--gray-900); font-weight: 500; }
.why-not-gap { color: var(--red-500); font-weight: 600; }

/* ── Step indicator (input flow) ── */
.step-indicator {
  display: flex;
  align-items: center;
  gap: 0;
  margin-bottom: 28px;
}
.step-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.78rem;
  color: var(--gray-500);
}
.step-item.active { color: var(--green-700); font-weight: 600; }
.step-item.done { color: var(--green-500); }
.step-circle {
  width: 28px; height: 28px;
  border-radius: 50%;
  border: 2px solid var(--gray-200);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--gray-500);
  background: var(--white);
  flex-shrink: 0;
}
.step-circle.active {
  border-color: var(--green-700);
  color: var(--green-700);
  background: linear-gradient(135deg, var(--green-100) 0%, #d4eedd 100%);
  box-shadow: 0 0 0 3px rgba(26,92,56,0.1);
}
.step-circle.done {
  border-color: var(--green-700);
  background: linear-gradient(135deg, var(--green-700) 0%, var(--green-500) 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(13,43,24,0.22);
}
.step-line { flex: 1; height: 2px; background: var(--gray-200); min-width: 32px; }
.step-line.done { background: linear-gradient(90deg, var(--green-700), var(--green-300)); }

/* ── Input form ── */
.form-section {
  background: var(--white);
  border: 1px solid var(--gray-200);
  border-left: 4px solid var(--green-300);
  border-radius: 0 var(--radius-lg) var(--radius-lg) 0;
  padding: 24px 28px;
  margin-bottom: 20px;
  box-shadow: 0 2px 10px rgba(13,43,24,0.06);
}
.form-section-title {
  font-size: 1rem;
  font-weight: 700;
  color: var(--gray-900);
  margin-bottom: 4px;
}
.form-section-desc {
  font-size: 0.8rem;
  color: var(--gray-700);
  margin-bottom: 18px;
  line-height: 1.5;
}
.input-help {
  background: var(--green-50);
  border-left: 3px solid var(--green-500);
  padding: 8px 12px;
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  font-size: 0.75rem;
  color: var(--green-700);
  margin: 6px 0 12px 0;
  line-height: 1.4;
}

/* ── Review card ── */
.review-card {
  background: var(--white);
  border: 1px solid var(--gray-200);
  border-left: 4px solid var(--green-100);
  border-radius: 0 var(--radius-md) var(--radius-md) 0;
  padding: 14px 18px;
  margin-bottom: 8px;
  box-shadow: 0 1px 4px rgba(13,43,24,0.05);
}
.review-row { display: flex; justify-content: space-between; padding: 5px 0; border-bottom: 1px solid var(--gray-200); font-size: 0.82rem; }
.review-row:last-child { border-bottom: none; }
.review-key { color: var(--gray-700); font-weight: 500; }
.review-val { color: var(--gray-900); font-weight: 600; text-align: right; max-width: 60%; }
.review-section-label { font-size: 0.67rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; color: var(--gray-700); padding: 8px 0 4px 0; }

/* ── Auth / Landing ── */
.auth-page {
  min-height: 100vh;
  background: var(--gray-100);
}
.auth-card {
  background: var(--white);
  border-radius: var(--radius-lg);
  padding: 36px 40px;
  box-shadow: var(--shadow-lg);
}
.auth-title { font-size: 1.35rem; font-weight: 800; color: var(--gray-900); }
.auth-subtitle { font-size: 0.8rem; color: var(--gray-500); margin-top: 4px; }
.auth-error {
  background: var(--red-100);
  border-left: 3px solid var(--red-500);
  padding: 8px 12px;
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  font-size: 0.8rem;
  color: var(--red-500);
  margin: 10px 0;
}
.auth-success {
  background: var(--green-100);
  border-left: 3px solid var(--green-500);
  padding: 8px 12px;
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  font-size: 0.8rem;
  color: var(--green-700);
  margin: 10px 0;
}
.landing-hero-col {
  background: linear-gradient(150deg, var(--green-900) 0%, #1a4a2a 100%);
  border-radius: var(--radius-lg);
  padding: 48px 40px;
  height: 100%;
  min-height: 520px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}
/* Auth page hero — sem background próprio (o fundo da página já é verde escuro) */
.auth-hero * { color: inherit; }
.landing-badge {
  display: inline-block;
  background: rgba(118,196,66,0.2);
  color: #76c442 !important;
  border: 1px solid rgba(118,196,66,0.35);
  padding: 4px 14px;
  border-radius: 20px;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 18px;
}
.landing-main-title {
  font-size: 2.2rem;
  font-weight: 900;
  color: #ffffff !important;
  line-height: 1.15;
  letter-spacing: -0.02em;
  margin-bottom: 16px;
}
.landing-main-desc {
  font-size: 0.95rem;
  color: rgba(255,255,255,0.88) !important;
  line-height: 1.65;
  margin-bottom: 28px;
  max-width: 400px;
}
.landing-benefit {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 14px;
}
.landing-benefit-icon {
  width: 28px; height: 28px;
  background: rgba(118,196,66,0.2);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.82rem;
  flex-shrink: 0;
}
.landing-benefit-text {
  font-size: 0.85rem;
  color: rgba(255,255,255,0.90) !important;
  line-height: 1.5;
}

/* Garante texto branco em todo conteúdo dentro dos heroes */
.landing-hero, .landing-hero-col {
  color: #ffffff !important;
}
.landing-hero .landing-tag,
.landing-hero-col .landing-badge {
  color: #76c442 !important;
}
/* strong/b dentro dos heroes — vence o selector universal !important */
.landing-hero strong,
.landing-hero b,
.landing-hero-col strong,
.landing-hero-col b,
.landing-benefit-text strong,
.landing-benefit-text b {
  color: #ffffff !important;
}
/* Texto de benefício (parágrafo após o strong) */
.landing-benefit-text {
  color: rgba(255,255,255,0.90) !important;
}
.landing-benefit-text * {
  color: inherit !important;
}

/* ── Landing page interna (home) ── */
.landing-hero {
  background:
    repeating-linear-gradient(
      -58deg,
      transparent 0px, transparent 38px,
      rgba(118,196,66,0.022) 38px, rgba(118,196,66,0.022) 39px
    ),
    radial-gradient(ellipse 65% 80% at 80% 30%, rgba(29,92,56,0.38) 0%, transparent 65%),
    linear-gradient(135deg, #0d2b18 0%, #1a3a2a 100%);
  border-radius: var(--radius-lg);
  padding: 60px 48px;
  color: #ffffff !important;
  margin-bottom: 32px;
}
.landing-tag {
  display: inline-block;
  background: rgba(118,196,66,0.2);
  color: #76c442 !important;
  border: 1px solid rgba(118,196,66,0.3);
  padding: 4px 14px;
  border-radius: 20px;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 16px;
}
.landing-title { font-size: 2.6rem; font-weight: 900; color: #ffffff !important; line-height: 1.1; letter-spacing: -0.03em; margin: 0 0 14px 0; }
.landing-desc { font-size: 1rem; color: rgba(255,255,255,0.90) !important; line-height: 1.6; max-width: 480px; margin-bottom: 28px; }

.how-card {
  background: var(--white);
  border: 1px solid var(--gray-200);
  border-top: 3px solid var(--green-300);
  border-radius: 0 0 var(--radius-md) var(--radius-md);
  padding: 24px 20px;
  text-align: center;
  box-shadow: 0 2px 10px rgba(13,43,24,0.07), 0 1px 3px rgba(0,0,0,0.04);
  height: 100%;
  transition: box-shadow 0.2s ease, transform 0.18s ease;
}
.how-card:hover {
  box-shadow: 0 6px 24px rgba(13,43,24,0.12), 0 2px 6px rgba(0,0,0,0.06);
  transform: translateY(-2px);
}
.how-number {
  width: 40px; height: 40px;
  background: linear-gradient(135deg, var(--green-700) 0%, var(--green-500) 100%);
  color: #ffffff;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 1rem;
  margin-bottom: 14px;
  box-shadow: 0 4px 12px rgba(13,43,24,0.25);
}
.how-title { font-size: 0.88rem; font-weight: 700; color: var(--gray-900); margin-bottom: 6px; }
.how-desc { font-size: 0.8rem; color: var(--gray-700); line-height: 1.5; }

/* ── History ── */
.hist-card {
  background: var(--white);
  border: 1px solid var(--gray-200);
  border-left: 4px solid var(--green-100);
  border-radius: 0 var(--radius-md) var(--radius-md) 0;
  padding: 14px 18px;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 4px rgba(13,43,24,0.06);
  cursor: pointer;
  transition: box-shadow 0.18s ease, border-color 0.18s ease, transform 0.15s ease;
}
.hist-card:hover {
  box-shadow: 0 4px 16px rgba(13,43,24,0.1);
  border-left-color: var(--green-300);
  transform: translateX(2px);
}
.hist-number {
  width: 36px; height: 36px;
  background: linear-gradient(135deg, var(--green-700) 0%, var(--green-500) 100%);
  color: #ffffff;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 0.9rem;
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(13,43,24,0.2);
}
.hist-main { flex: 1; }
.hist-title { font-size: 0.88rem; font-weight: 600; color: var(--gray-900); }
.hist-sub { font-size: 0.74rem; color: var(--gray-700); margin-top: 2px; }
.hist-ev { text-align: right; }
.hist-ev-val { font-size: 1.1rem; font-weight: 800; color: var(--green-700); }
.hist-ev-unit { font-size: 0.7rem; color: var(--gray-700); }

/* ── Prob validation ── */
.prob-error { background: var(--red-100); border-left: 3px solid var(--red-500); padding: 8px 12px; border-radius: 0 var(--radius-sm) var(--radius-sm) 0; font-size: 0.82rem; color: #8b0000; margin: 8px 0; }
.prob-ok    { background: var(--green-100); border-left: 3px solid var(--green-500); padding: 8px 12px; border-radius: 0 var(--radius-sm) var(--radius-sm) 0; font-size: 0.82rem; color: var(--green-700); margin: 8px 0; }

/* ── Ajuste entre card HTML e expander/botões abaixo dele ── */
[data-testid="stMarkdownContainer"] + [data-testid="stExpander"],
[data-testid="stMarkdownContainer"] + div[data-testid="stHorizontalBlock"] {
  margin-top: 4px !important;
}

/* ── Sidebar collapse/expand button — always visible and styled ── */
[data-testid="collapsedControl"] {
  display: flex !important;
  visibility: visible !important;
  opacity: 1 !important;
  position: fixed !important;
  top: 50% !important;
  left: 0 !important;
  transform: translateY(-50%) !important;
  z-index: 99999 !important;
  background: linear-gradient(180deg, #1a5c38 0%, #0d2b18 100%) !important;
  border-radius: 0 10px 10px 0 !important;
  box-shadow: 3px 0 14px rgba(0,0,0,0.30) !important;
  padding: 12px 5px !important;
  min-height: 52px !important;
  min-width: 24px !important;
  align-items: center !important;
  justify-content: center !important;
  cursor: pointer !important;
}
[data-testid="collapsedControl"]:hover {
  background: linear-gradient(180deg, #2d8a56 0%, #1a5c38 100%) !important;
  box-shadow: 4px 0 18px rgba(0,0,0,0.40) !important;
}
[data-testid="collapsedControl"] button {
  background: transparent !important;
  border: none !important;
  color: rgba(255,255,255,0.92) !important;
  padding: 0 !important;
}
[data-testid="collapsedControl"] svg,
[data-testid="collapsedControl"] button svg {
  fill: rgba(255,255,255,0.92) !important;
  color: rgba(255,255,255,0.92) !important;
}
/* Sidebar open — collapse button (the arrow to close it) */
[data-testid="stSidebarCollapseButton"] button {
  background: transparent !important;
  border: none !important;
  color: rgba(255,255,255,0.55) !important;
}
[data-testid="stSidebarCollapseButton"] button:hover {
  color: rgba(255,255,255,0.95) !important;
  background: rgba(255,255,255,0.08) !important;
}
[data-testid="stSidebarCollapseButton"] svg {
  fill: rgba(255,255,255,0.55) !important;
}
[data-testid="stSidebarCollapseButton"] button:hover svg {
  fill: rgba(255,255,255,0.95) !important;
}

/* ── Language toggle — esconde os botões nativos, mantém clicáveis via JS ── */
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] {
  display: none !important;
}

/* ── Responsive ── */
@media (max-width: 768px) {
  .rec-decisions-grid { grid-template-columns: repeat(2, 1fr); }
  .landing-main-title { font-size: 1.6rem; }
  .landing-title { font-size: 1.8rem; }
}
</style>
"""


_CAL_JS = """
<script>
(function() {
  var W = '#ffffff', T = 'transparent', GRN = '#1a5c38', TXT = '#1a3a2a', RNG = '#e8f5e9';
  var _fixing = false;

  function fix(el, bg, color) {
    el.style.setProperty('background', bg, 'important');
    el.style.setProperty('background-color', bg, 'important');
    if (color) el.style.setProperty('color', color, 'important');
  }

  function fixCalendar() {
    if (_fixing) return;
    _fixing = true;
    try {
      var doc = window.parent.document;
      doc.querySelectorAll('body > div').forEach(function(portal) {
        var cal = portal.querySelector('[data-baseweb="calendar"]');
        if (!cal) return;
        fix(portal, W);
        // grid cells — branco
        portal.querySelectorAll('[role="grid"],[role="row"],[role="gridcell"],[role="columnheader"]')
          .forEach(function(el) { fix(el, W, TXT); });
        // conteúdo dentro de gridcell — transparente
        portal.querySelectorAll('[role="gridcell"] > *').forEach(function(el) {
          fix(el, T);
        });
        // dias normais
        portal.querySelectorAll('[role="gridcell"] button').forEach(function(btn) {
          var cell = btn.closest('[role="gridcell"]');
          var sel  = cell && (cell.getAttribute('aria-selected') === 'true' || btn.getAttribute('aria-selected') === 'true');
          var rng  = cell && cell.getAttribute('data-range-highlight') === 'true';
          if (sel) {
            fix(btn, GRN, W);
          } else if (rng) {
            fix(cell, RNG); fix(btn, T, TXT);
          } else {
            fix(btn, T, TXT);
          }
        });
      });
    } finally {
      _fixing = false;
    }
  }

  // Injeta regras de alta prioridade no head do documento pai
  var doc = window.parent.document;
  if (!doc.getElementById('simcal-js-override')) {
    var s = doc.createElement('style');
    s.id = 'simcal-js-override';
    s.textContent =
      'body>div:has([data-baseweb="calendar"]){background:#fff!important}' +
      'body>div:has([data-baseweb="calendar"]) [role="grid"],' +
      'body>div:has([data-baseweb="calendar"]) [role="row"],' +
      'body>div:has([data-baseweb="calendar"]) [role="gridcell"],' +
      'body>div:has([data-baseweb="calendar"]) [role="columnheader"]' +
      '{background:#fff!important;background-color:#fff!important;color:#1a3a2a!important}' +
      'body>div:has([data-baseweb="calendar"]) [role="gridcell"]>*' +
      '{background:transparent!important;background-color:transparent!important}' +
      'body>div:has([data-baseweb="calendar"]) [aria-selected="true"] button' +
      '{background:#1a5c38!important;color:#fff!important;border-radius:50%!important}' +
      'body>div:has([data-baseweb="calendar"]) [data-range-highlight="true"]' +
      '{background:#e8f5e9!important}' +
      'body>div:has([data-baseweb="calendar"]) button[disabled]{color:rgba(45,138,86,0.32)!important}';
    doc.head.appendChild(s);
  }

  // Observa quando o calendário abre (novo filho direto do body)
  new MutationObserver(function(muts) {
    muts.forEach(function(m) {
      if (m.addedNodes.length) fixCalendar();
    });
  }).observe(window.parent.document.body, { childList: true });

  fixCalendar();
})();
</script>
"""


def inject_styles() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)
