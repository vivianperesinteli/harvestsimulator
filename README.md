# Simulador de Safra — Soja Verão, Mato Grosso

**Bayer CropScience × Inteli · Module 6 · Group 2**

Ferramenta web de apoio à decisão agrícola para produtores de soja no Mato Grosso. O produtor informa as condições do talhão e suas decisões de manejo; o simulador calcula a produtividade esperada em cada cenário climático, aplica 6 critérios econômicos de decisão e estima o intervalo de confiança via simulação de Monte Carlo.

---

## Funcionalidades

| Funcionalidade | Descrição |
|---|---|
| Matriz de Payoff | 27 combinações de manejo × 3 cenários climáticos (sc/ha) |
| 6 Critérios de Decisão | Bayes EV, Wald, Laplace, Hurwicz, Maximax, Savage |
| Monte Carlo | 1.000–5.000 iterações, distribuições triangulares configuráveis |
| Análise de Risco | P(yield < threshold), P5/P95, desvio padrão |
| Tornado Chart | Correlação de Spearman por variável estocástica |
| Comparação de Alternativas | Sua seleção vs. path ótimo (Bayes EV) |
| Upgrade Potential | Impacto de trocar cultivar, TSI ou plantadeira |
| Export | PDF (relatório completo) + CSV por recomendação |
| Explainer interativo | 10 passos de metodologia com fórmulas e gráficos |

---

## Pré-requisitos

- Python 3.11+
- pip

---

## Instalação e execução local

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Terminal 1 — backend FastAPI (porta 8000)
uvicorn backend.main:app --port 8000

# 3. Terminal 2 — frontend Streamlit (porta 8501)
streamlit run frontend/app.py
```

Acesse `http://localhost:8501` e faça login com:
- **Usuário:** `demo`
- **Senha:** `demo123`

---

## Variáveis de ambiente (produção)

| Variável | Padrão | Descrição |
|---|---|---|
| `BACKEND_URL` | `http://localhost:8000` | URL do backend FastAPI |
| `ALLOWED_ORIGINS` | `http://localhost:8501` | Origens CORS permitidas (separadas por vírgula) |

---

## Estrutura do projeto

```
simulator/
├── backend/
│   ├── main.py          # FastAPI — endpoints /health, /api/nodes, /api/simulate, /api/monte_carlo
│   ├── engine.py        # Compute simulation: payoff matrix, critérios, upgrade potential
│   ├── monte_carlo.py   # Motor MC: distribuições triangulares + tornado
│   ├── models.py        # Pydantic models para request/response
│   └── data.py          # Constantes: nós, ajustes, probabilidades de chuva
├── frontend/
│   ├── app.py           # Streamlit: autenticação + roteador + sidebar
│   ├── auth.py          # Login/cadastro com PBKDF2-SHA256
│   ├── api.py           # Cliente HTTP para o backend
│   ├── styles.py        # CSS global (identidade visual)
│   ├── navigation.py    # Roteador de páginas via session_state
│   └── views/
│       ├── input.py         # 3 etapas: contexto → decisões → revisão
│       ├── results.py       # Recomendações, matriz, critérios, export PDF/CSV
│       ├── results_helpers.py  # Labels e textos compartilhados
│       ├── results_pdf.py      # Gerador de PDF (fpdf2)
│       ├── dashboard.py     # Gráficos: waterfall, radar, barras, sensibilidade
│       ├── monte_carlo.py   # UI Monte Carlo com histograma e tornado
│       ├── explainer.py     # Explainer interativo — 10 passos
│       └── history.py       # Histórico de simulações da sessão
├── data/
│   └── users.json       # Usuários (gerado automaticamente)
├── tests/
│   └── test_monte_carlo.py
├── requirements.txt
├── runtime.txt
├── .env.example
└── README.md
```

---

## API

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/health` | Status do servidor |
| GET | `/api/nodes` | Opções de todos os nós C1–C7 e D1–D6 |
| POST | `/api/simulate` | Roda a simulação completa (payoff matrix + critérios + MC) |
| POST | `/api/monte_carlo` | Monte Carlo com parâmetros configuráveis |

---

## Modelo

- **Escopo:** Soja Verão · Mato Grosso · Baseline = 60 sc/ha (CONAB 2023/24)
- **Variáveis de contexto (C1–C7):** região, textura, pH, drenagem, aptidão, área, ENSO
- **Variáveis de decisão (D1–D6):** janela de plantio, cultivar, TSI, densidade, manejo de doenças, plantadeira
- **Cenários climáticos:** Seca, Normal, Úmida — probabilidades condicionais ao ENSO
- **Variáveis estocásticas (MC):** D2 Triangular(−8,0,+6), D3 Triangular(−5,0,+3), D6 Triangular(−4,0,+3), Chuva R3–R6 discreta

---

## Como ler os resultados

- **Referência da região:** 60 sc/ha — produtividade média histórica MT
- **Ponto de partida da sua lavoura:** baseline ajustado pelo contexto do campo
- **Produtividade esperada:** média ponderada pelos cenários climáticos (Bayes EV)
- **Intervalo 90%:** entre P5 e P95 das 2.000 simulações de Monte Carlo
- **Risco:** probabilidade de ficar abaixo do threshold configurável (padrão: referência regional)

---

## Licença

Projeto acadêmico — Inteli · Bayer CropScience.  
Dados proprietários da Bayer não estão incluídos neste repositório.
