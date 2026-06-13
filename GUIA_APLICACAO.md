# Guia da Aplicação — Decision Tree Simulator v7

## Visão Geral

Aplicação web de **apoio à decisão agrícola** para produtores de soja no Mato Grosso. O usuário informa as características do campo e as decisões que pretende tomar. O sistema calcula qual combinação maximiza a produtividade esperada, aplica 6 critérios econômicos de decisão, e permite análise de risco via simulação Monte Carlo — tudo quantificado em **sc/ha**.

- **Escopo:** Soja Verão · Mato Grosso · Baseline = 60 sc/ha  
- **Modelo:** Decision Tree v7 (Baseline-Adjusted) — aditivo, 13 nós  
- **Unidade:** sc/ha exclusivamente — nenhuma referência monetária  

---

## Como Rodar

Dentro da pasta `Sprint 3/simulator/`, abrir dois terminais:

```powershell
# Terminal 1 — backend
uvicorn backend.main:app --reload --port 8000

# Terminal 2 — frontend
streamlit run frontend/app.py
```

O Streamlit abre automaticamente em `http://localhost:8501`.  
Login de acesso rápido: usuário `demo` / senha `demo123`.

---

## Arquitetura

```
Usuário (navegador :8501)
        │
        │  HTTP POST (requests — server-side, não visível no DevTools)
        ▼
frontend/app.py              ← Streamlit — autenticação + roteador
  ├── auth.py                ← login / cadastro / logout
  ├── styles.py              ← CSS global (visual identity)
  ├── navigation.py          ← go(page) via session_state
  ├── api.py                 ← chamadas HTTP ao backend
  └── views/
      ├── input.py           ← 3 etapas: contexto → decisões → revisão
      ├── results.py         ← cards de recomendação + matriz + critérios + árvore
      ├── dashboard.py       ← waterfall + radar + sensibilidade
      ├── monte_carlo.py     ← distribuições triangulares + tornado
      └── history.py         ← histórico de simulações da sessão
        │
        │  JSON via HTTP :8000
        ▼
backend/main.py              ← FastAPI
  ├── GET  /health
  ├── GET  /api/nodes
  ├── POST /api/simulate
  └── POST /api/monte_carlo
        │
        ▼
backend/engine.py            ← compute_simulation(context, decisions)
backend/monte_carlo.py       ← run_monte_carlo(context, decisions, params)
backend/data.py              ← constantes: nós, ajustes, probs de chuva
backend/models.py            ← schemas Pydantic
```

**Princípio central:** o frontend envia os inputs brutos exatamente como o usuário selecionou. O backend faz **toda** a computação. O frontend só exibe.

> As chamadas HTTP são feitas em Python (server-side). Por isso não aparecem na aba Network do DevTools do navegador — isso é normal e esperado no Streamlit.

---

## Autenticação

O sistema exige login antes de acessar qualquer funcionalidade.

### Como funciona

- Ao abrir `http://localhost:8501`, o usuário vê a tela de login/cadastro.
- Credenciais são armazenadas em `data/users.json` com senha hasheada via **SHA-256**.
- Nenhuma dependência externa de autenticação — implementado com `hashlib` (Python built-in).
- O estado de autenticação vive em `st.session_state.auth`.

### Criar conta

Na aba **Criar conta**, preencher nome completo, e-mail, usuário e senha (mínimo 6 caracteres). O sistema valida duplicidade de usuário e e-mail.

### Acesso demo

Usuário `demo` / senha `demo123` — criado automaticamente na primeira inicialização.

### Logout

Botão **Sair** no rodapé da sidebar. Limpa toda a sessão.

---

## Modelo Matemático

```
Yield (sc/ha) = Baseline + Σ Ajustes_contexto(C1–C7) + Σ Ajustes_decisão(D1–D6) + Ajuste_chuva
```

O modelo é **aditivo** — cada nó contribui com um ajuste fixo em sc/ha sobre o baseline de 60.

### Nós de Contexto (C1–C7) — não controláveis

Características observadas do campo e da safra. O produtor informa; não pode alterar diretamente.

| Nó | Label | Opções exibidas ao usuário | Ajuste (sc/ha) |
|---|---|---|---|
| C1 | Região MT | Sorriso / Sinop / Lucas RV | +5 |
| | | Sapezal / Campo Novo do Parecis | 0 |
| | | Primavera do Leste / Querência | −6 |
| C2 | Textura do Solo | Argilosa (>35% argila) | +5 |
| | | Média (20–35% argila) | 0 |
| | | Arenosa (<20% argila) | −7 |
| C3 | pH do Solo | pH 5,5–6,5 (ideal) | +4 |
| | | pH 5,0–5,4 ou 6,6–6,8 (corrigível) | 0 |
| | | pH <5,0 ou >6,8 (crítico) | −6 |
| C4 | Drenagem | Bem drenado | +3 |
| | | Drenagem moderada | 0 |
| | | Mal drenado / alagamentos | −8 |
| C5 | Aptidão Estrutural | Latossolo / Nitossolo | +5 |
| | | Argissolo / Cambissolo | 0 |
| | | Neossolo / Gleissolo | −7 |
| C6 | Área Plantada | Acima de 200 ha | +2 |
| | | 50 a 200 ha | 0 |
| | | Até 50 ha | −1 |
| C7 | Forecast ENSO | El Niño (chuvas regulares MT) | +3 |
| | | Condições neutras | +1 |
| | | La Niña (veranicos prolongados) | −3 |

**C7 tem papel duplo:** além do ajuste aditivo, define as probabilidades condicionais de chuva no período R3–R6.

### Nós de Decisão (D1–D6) — controláveis

O que o produtor decide fazer. O frontend converte inputs amigáveis para os valores internos do modelo.

| Nó | Input no frontend | Opções internas | Ajuste (sc/ha) |
|---|---|---|---|
| D1 | Date picker (data de plantio) | Ótima (16/out–10/nov) | +4 |
| | Mapeado pela data selecionada | Precoce (até 15/out) | −3 |
| | | Tardia (após 10/nov) | −8 |
| D2 | Select de cultivares | Alto potencial (P98R30, NK6727, BMX Foco; pós-2020) | +6 |
| | | Intermediário (2015–2019) | 0 |
| | | Limitado (legados pré-2015) | −8 |
| D3 | Multi-select de componentes TSI | Premium (fung+inset+nemat+inoc) | +3 |
| | Mapeado pelos itens marcados | Standard (fungicida + inoculante) | 0 |
| | | Sem TSI | −5 |
| D4 | Número de sementes/ha | Média (280k–340k) | +2 |
| | Mapeado pelo valor numérico | Baixa (≤280k) | −1 |
| | | Alta (>340k) | −1 |
| D5 | Slider de aplicações + checkbox de monitoramento | Alto (≥3 fung. + monitor) | +5 |
| | Mapeado pela combinação | Padrão (2 aplicações) | 0 |
| | | Baixo (1 ou nenhuma) | −7 |
| D6 | Select por capacidade de equipamento | Alta precisão (RTK + pneumática, <2 cm) | +3 |
| | | Precisão padrão (2–5 cm) | 0 |
| | | Baixa precisão (>5 cm) | −4 |

**D1, D4 e D5** são os nós expandidos na Payoff Matrix (3×3×3 = 27 combinações).  
**D2, D3 e D6** entram como valor fixo na `base_effective` — afetam todos os 27 paths igualmente.

### Nó Chance — Chuva R3–R6 (revelado ex-post)

Estado da natureza não controlável pelo produtor. Ajuste aditivo em sc/ha:

| Estado | Chuva | Ajuste |
|---|---|---|
| Seca | < 150 mm | −8 |
| Normal | 150–250 mm | +2 |
| Úmida | > 250 mm | +4 |

Probabilidades **condicionais ao ENSO** (C7):

| ENSO | P(Seca) | P(Normal) | P(Úmida) |
|---|---|---|---|
| El Niño | 15% | 50% | 35% |
| Neutro | 30% | 50% | 20% |
| La Niña | 50% | 30% | 20% |

---

## Como a Simulação é Calculada

Ao confirmar a revisão, o frontend envia um POST para `/api/simulate`:

```json
{
  "context":   { "c1_regiao": "Favorável (Sorriso, Sinop, Lucas RV)", ..., "c7_enso": "Neutro" },
  "decisions": { "d1_janela": "Ótima (16/out – 10/nov)", ..., "d6_tecnologia": "Padrão" }
}
```

O backend executa `compute_simulation(context, decisions)` em `backend/engine.py` em 5 passos:

**Passo 1 — Base de contexto**
```
context_adj  = Σ ajustes(C1…C7)
context_base = 60 + context_adj
```

**Passo 2 — Base efetiva**
```
fixed_adj      = adj(D2) + adj(D3) + adj(D6)
base_effective = context_base + fixed_adj
```

**Passo 3 — Payoff Matrix 27 × 3**

Para cada combinação D1×D4×D5 e cada estado de chuva:
```
yield = base_effective + adj(D1) + adj(D4) + adj(D5) + adj(chuva)
```

**Passo 4 — 6 Critérios de Decisão**

| Critério | Lógica |
|---|---|
| **Maximax** | `max(row)` por path; escolhe o maior. Perfil otimista. |
| **Wald / Maximin** | `min(row)` por path; escolhe o maior mínimo. Perfil conservador. |
| **Laplace** | Média simples dos 3 estados (equiprováveis). |
| **Hurwicz (α=0,5)** | `0,5 × max + 0,5 × min`. Equilíbrio otimismo/pessimismo. |
| **Bayes / EV** | `Σ yield × P(chuva\|ENSO)`. **Critério principal.** |
| **Savage / Minimax Regret** | Minimiza o maior arrependimento entre os estados. |

**Passo 5 — Retorno**

A resposta inclui: baseline, ajustes intermediários, base efetiva, matriz 27×3, 27 paths com labels, todos os critérios com valores e índice do path recomendado, e o EV da seleção específica do usuário.

---

## Fluxo de Uso — Passo a Passo

### 1. Login / Cadastro

O usuário acessa `http://localhost:8501` e faz login ou cria uma conta. Após autenticação, é redirecionado para a **Home**.

### 2. Home

Exibe:
- Saudação personalizada com o nome do usuário logado
- Hero com descrição do produto em linguagem do produtor
- "Como funciona" em 4 passos visuais
- Resumo do modelo (baseline, fórmula, critérios)
- Atalho para as últimas 3 simulações da sessão (se houver)
- Botão **Iniciar nova simulação**

### 3. Simulação — Etapa 1: Contexto do Campo

7 perguntas sobre características não controláveis do talhão:

- **Região:** seleciona por cidades reais (ex: "Sorriso, Sinop, Lucas do Rio Verde")
- **Textura:** por descrição técnica (ex: "Argilosa — mais de 35% argila")
- **pH:** por faixa de valor
- **Drenagem:** por comportamento observado
- **Aptidão estrutural:** por ordem pedológica (ex: "Latossolo ou Nitossolo")
- **Área:** por faixa em hectares
- **Forecast ENSO:** previsão INPE/CPTEC para a safra

Cada pergunta tem uma nota explicativa (em verde) sobre por que aquela informação importa.

### 4. Simulação — Etapa 2: Decisões do Produtor

6 inputs para as decisões agronômicas:

- **D1 — Date picker:** seleciona a data planejada de início do plantio (set/2024–dez/2024). O sistema classifica automaticamente como Precoce / Ótima / Tardia com feedback visual colorido.
- **D2 — Select de cultivares:** lista cultivares específicos por geração (P98R30, NK6727, BMX Foco, etc.)
- **D3 — Multi-select TSI:** marca os componentes aplicados (Fungicida, Inoculante, Inseticida, Nematicida). O sistema mapeia automaticamente para Premium / Standard / Sem TSI.
- **D4 — Número de sementes/ha:** input numérico de 150.000 a 500.000 com feedback da faixa resultante.
- **D5 — Slider + checkbox:** número de aplicações de fungicida (0–4) + monitoramento ativo de ferrugem. Mapeado para Alto / Padrão / Baixo.
- **D6 — Select por equipamento:** capacidade da plantadeira descrita por variação de espaçamento.

### 5. Simulação — Etapa 3: Revisão

Tela de confirmação antes de simular, mostrando:
- Coluna esquerda: resumo do contexto em linguagem legível
- Coluna direita: resumo das decisões com os mapeamentos calculados (ex: "28/out/2024 → Ótima")
- Botões para voltar e editar qualquer etapa, ou **Confirmar e Simular**

### 6. Resultados

Quatro abas:

#### Aba Recomendações
- **Top 3 cards ranqueados por EV (Bayes)**, cada um mostrando:
  - EV esperado em sc/ha (destaque grande) + delta vs baseline
  - Yield por cenário (Seca / Normal / Úmida) com código de cor
  - Badges dos critérios de decisão que recomendam este path
  - Grid com todas as 6 decisões (D1–D6)
- Cada card tem um **expandível** com:
  - Por que esta combinação é recomendada (texto gerado pelo modelo)
  - Como implementar: orientações práticas de janela, densidade e manejo
- **Seção "Por que as outras não foram escolhidas"**: tabela com as 5 combinações de menor EV e gap em relação à recomendação principal
- Mensagem comparando a seleção do usuário com a recomendação ótima
- Botão de **export CSV** da Payoff Matrix completa

#### Aba Payoff Matrix
- Tabela com 27 linhas (paths D1×D4×D5), colunas Seca / Normal / Úmida / EV / Maximax / Wald
- Verde = melhor EV; Azul = seleção do usuário
- Heatmap de yield por path × estado de chuva

#### Aba Critérios
- Tabela resumindo qual path cada critério recomenda e com qual valor
- Gráfico de barras horizontal com EV de todos os 27 paths

#### Aba Árvore de Decisão
- **Sunburst interativo** (Plotly): hierarquia D1 → D4 → D5, cor proporcional ao EV médio
- Tabela de terminais com yield por estado e EV

### 7. Dashboard

Visualizações analíticas da simulação ativa:

- **Waterfall:** decomposição do yield — Baseline → C1-C7 → D2/D3/D6 → D1/D4/D5 → Chuva → EV Final
- **Radar:** contexto C1–C7 normalizado para [0,1] — perfil visual do talhão
- **Barras de cenário:** yield do usuário vs path ótimo nos 3 estados de chuva
- **Sensibilidade:** todos os 13 nós ordenados por ajuste absoluto

### 8. Monte Carlo

Simulação de risco com distribuições de incerteza sobre D2, D3 e D6:

**Configuração:**
- Número de iterações: 1.000–5.000 (slider)
- Threshold de risco: define P(yield < threshold)
- Parâmetros triangulares editáveis para cada variável estocástica (mínimo, moda, máximo)

**O modelo sorteia por iteração:**
1. D2 (Cultivar) via triangular(−8, 0, +6)
2. D3 (TSI) via triangular(−5, 0, +3)
3. D6 (Tecnologia) via triangular(−4, 0, +3)
4. Estado de chuva via rng.choice ponderado pelas probs condicionais ao ENSO

**Saídas:**
- 5 cards estatísticos: Média, Desvio, P5, P95, P(yield < threshold)
- Histograma com área de risco destacada + linhas de P5 / P95 / média / threshold
- **Tornado chart** (Pearson): correlação de cada variável estocástica com o yield final — identifica as principais fontes de incerteza
- Comparação lado a lado: sua seleção vs path ótimo (Bayes)
- Export CSV com todas as iterações

**Endpoint:** `POST /api/monte_carlo`

```json
{
  "context":   { ... },
  "decisions": { ... },
  "params": {
    "d2": { "min": -8.0, "mode": 0.0, "max": 6.0 },
    "d3": { "min": -5.0, "mode": 0.0, "max": 3.0 },
    "d6": { "min": -4.0, "mode": 0.0, "max": 3.0 }
  },
  "n_iter": 2000,
  "threshold": 60.0
}
```

### 9. Histórico

Registra automaticamente todas as simulações realizadas na sessão:

- **Sumário:** total de simulações, melhor EV, EV médio, simulação destaque
- **Cards por simulação:** EV best e EV do usuário, expandível com inputs e tabela de critérios
- Botão **Restaurar simulação**: carrega os resultados de volta na aba Resultados
- **Gráfico comparativo:** EV best vs EV usuário em todas as simulações
- **Tabela comparativa de inputs:** side-by-side entre simulações
- Export CSV do histórico completo

> O histórico é mantido em `st.session_state` — persiste durante a sessão, mas é resetado ao fechar o browser ou fazer logout.

---

## Estrutura de Arquivos

```
simulator/
├── backend/
│   ├── data.py          ← constantes: nós, ajustes, probabilidades do modelo v7
│   ├── engine.py        ← compute_simulation() — toda a lógica de cálculo
│   ├── monte_carlo.py   ← run_monte_carlo() — distribuições triangulares + tornado
│   ├── models.py        ← schemas Pydantic (Request/Response de simulate e monte_carlo)
│   └── main.py          ← FastAPI: /health, /api/nodes, /api/simulate, /api/monte_carlo
├── frontend/
│   ├── app.py           ← entry point: auth gate, sidebar, roteador de páginas
│   ├── auth.py          ← login / cadastro / logout / hashing SHA-256
│   ├── api.py           ← simulate(), monte_carlo(), get_nodes() — HTTP ao backend
│   ├── navigation.py    ← go(page) via st.session_state + st.rerun()
│   ├── styles.py        ← CSS global: paleta verde Bayer + âmbar, cards, sidebar
│   └── views/
│       ├── input.py     ← 3 etapas: contexto (C1–C7) → decisões (D1–D6) → revisão
│       ├── results.py   ← recomendações, payoff matrix, critérios, árvore sunburst
│       ├── dashboard.py ← waterfall, radar, barras de cenário, sensibilidade
│       ├── monte_carlo.py ← config, histograma, tornado, comparação, export
│       └── history.py   ← histórico de sessão, comparativo, restauração
├── data/
│   └── users.json       ← usuários cadastrados (criado automaticamente)
├── tests/
│   ├── conftest.py      ← configura sys.path para todos os testes
│   ├── test_data.py     ← constantes e estrutura dos nós
│   ├── test_engine.py   ← aritmética exata do modelo aditivo
│   ├── test_criteria.py ← cada critério de decisão isolado
│   ├── test_monte_carlo.py ← distribuição triangular + saídas estatísticas
│   ├── test_api.py      ← endpoints FastAPI (happy path + erros 422)
│   ├── test_mappings.py ← mapeamentos do frontend (date picker, TSI, densidade)
│   └── test_auth.py     ← login, cadastro, hashing, session_state
└── requirements.txt
```

---

## Testes Automatizados

A suite de testes cobre backend e frontend com 230 casos:

```powershell
# Rodar todos os testes
python -m pytest tests/ -v

# Rodar um arquivo específico
python -m pytest tests/test_engine.py -v

# Ver apenas falhas
python -m pytest tests/ --tb=short -q
```

| Arquivo | Casos | Cobre |
|---|---|---|
| `test_data.py` | 28 | Baseline=60, estrutura dos nós, RAIN_PROBS somam 1.0 |
| `test_engine.py` | 20 | Aritmética exata para 3 cenários calculados à mão |
| `test_criteria.py` | 22 | Maximax, Wald, Laplace, Hurwicz, Bayes EV, Savage |
| `test_monte_carlo.py` | 17 | Estrutura, estatísticas, distribuição triangular, tornado |
| `test_api.py` | 29 | Todos os endpoints — happy path e erros 422 |
| `test_mappings.py` | 59 | Todos os displays do frontend → opções válidas da API |
| `test_auth.py` | 27 | SHA-256, register, login, session_state |

---

## API Reference

### GET /health
```json
{ "status": "ok", "version": "2.0.0" }
```

### GET /api/nodes
Retorna todas as opções disponíveis para cada nó (útil para referência ou integração).
```json
{
  "context":   { "c1_regiao": { "label": "C1 · Região MT", "options": [...] }, ... },
  "decisions": { "d1_janela": { "label": "D1 · Janela de Plantio", "options": [...] }, ... }
}
```

### POST /api/simulate
**Request:**
```json
{
  "context":   { "c1_regiao": "Favorável (Sorriso, Sinop, Lucas RV)", ..., "c7_enso": "Neutro" },
  "decisions": { "d1_janela": "Ótima (16/out – 10/nov)", ..., "d6_tecnologia": "Padrão" }
}
```
**Response:** baseline, context_adj, fixed_adj, base_effective, rain_states, rain_probs, paths (27), matrix (27×3), criteria (6 critérios), user_selection (EV + yields).

**Erros:** 422 se alguma chave estiver ausente ou o valor não for uma opção válida.

### POST /api/monte_carlo
**Request:** context + decisions + params (triangulares para d2/d3/d6) + n_iter + threshold.  
**Response:** yields (lista), mean, std, p5, p95, p_below, tornado (correlações de Pearson).

---

## Fontes dos Dados

| Item | Fonte |
|---|---|
| Baseline 60 sc/ha | CONAB Boletim Grãos Jan/2024 — MT 2023/24 |
| C1 Região | CONAB ranking municípios MT 2023/24 + dataset Bayer por city |
| C2 Textura | EMBRAPA SiBCS + dataset soil_texture |
| C3 pH | EMBRAPA Soja — Acidez e Calagem |
| C4 Drenagem | EMBRAPA SiBCS + dataset soil_drainage_class |
| C5 Aptidão estrutural | EMBRAPA SiBCS (soil_order) |
| C6 Área plantada | Dataset Bayer planted_area_ha |
| C7 ENSO | INPE/CPTEC histórico MT + INMET série histórica |
| D1 Janela de plantio | EMBRAPA ZARC Soja MT + dataset planting_date |
| D2 Cultivar | Bayer Cultivar Trial MT 2022/23 |
| D3 TSI | EMBRAPA Circ. Téc. 90 + Bayer Acceleron |
| D4 Densidade | Dataset Bayer P25/P50/P75 |
| D5 Manejo de doenças | EMBRAPA Soja — Ferrugem Asiática |
| D6 Tecnologia de plantio | Bayer Climate FieldView + dataset planting_maker |
| Chuva R3–R6 | INMET Sorriso/Sinop 2010–2024 + dataset rainfall_sum_R3_R6 |
| Probs Chuva\|ENSO | INMET × INPE histórico ENSO MT 1991–2023 |
| Parâmetros triangulares (MC) | Excel Decision Tree v7 — aba Monte Carlo |
