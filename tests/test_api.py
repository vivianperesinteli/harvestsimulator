"""
Testa os endpoints FastAPI (backend/main.py) via TestClient.
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# ── Payloads de referência ────────────────────────────────────────────────────

_VALID_CONTEXT = {
    "c1_regiao":  "Intermediária (Sapezal, Campo Novo)",
    "c2_textura": "Intermediária (textura média)",
    "c3_ph":      "Limítrofe (5,0–5,4 ou 6,6–6,8)",
    "c4_drenagem":"Moderada (moderadamente/imperfeito)",
    "c5_aptidao": "Média (Argissolo, Cambissolo)",
    "c6_area":    "Média (50–200 ha)",
    "c7_enso":    "Neutro",
}

_VALID_DECISIONS = {
    "d1_janela":     "Ótima (16/out – 10/nov)",
    "d2_cultivar":   "Intermediário (2015–2019)",
    "d3_tsi":        "Standard (fungicida + inoculante)",
    "d4_densidade":  "Média (280k–340k)",
    "d5_manejo":     "Padrão (2 aplicações)",
    "d6_tecnologia": "Padrão",
}

_VALID_MC_PARAMS = {
    "d2": {"min": -8.0, "mode": 0.0, "max": 6.0},
    "d3": {"min": -5.0, "mode": 0.0, "max": 3.0},
    "d6": {"min": -4.0, "mode": 0.0, "max": 3.0},
}


# ── GET /health ───────────────────────────────────────────────────────────────

class TestHealth:
    def test_status_200(self):
        r = client.get("/health")
        assert r.status_code == 200

    def test_body_has_status_ok(self):
        r = client.get("/health")
        assert r.json()["status"] == "ok"

    def test_body_has_version(self):
        r = client.get("/health")
        assert "version" in r.json()


# ── GET /api/nodes ─────────────────────────────────────────────────────────────

class TestNodes:
    def test_status_200(self):
        r = client.get("/api/nodes")
        assert r.status_code == 200

    def test_has_context_and_decisions(self):
        r = client.get("/api/nodes")
        body = r.json()
        assert "context" in body
        assert "decisions" in body

    def test_context_has_seven_nodes(self):
        r = client.get("/api/nodes")
        assert len(r.json()["context"]) == 7

    def test_decisions_has_six_nodes(self):
        r = client.get("/api/nodes")
        assert len(r.json()["decisions"]) == 6

    def test_each_node_has_label_and_options(self):
        r = client.get("/api/nodes")
        body = r.json()
        for section in ("context", "decisions"):
            for key, node in body[section].items():
                assert "label"   in node, f"{key}: sem 'label'"
                assert "options" in node, f"{key}: sem 'options'"
                assert isinstance(node["options"], list)
                assert len(node["options"]) == 3

    def test_c7_enso_options_include_enso_keywords(self):
        r = client.get("/api/nodes")
        options = r.json()["context"]["c7_enso"]["options"]
        text = " ".join(options)
        assert "Ni" in text   # El Niño / La Niña
        assert "Neutro" in text


# ── POST /api/simulate ────────────────────────────────────────────────────────

class TestSimulate:
    def test_valid_payload_returns_200(self):
        r = client.post("/api/simulate", json={
            "context":   _VALID_CONTEXT,
            "decisions": _VALID_DECISIONS,
        })
        assert r.status_code == 200

    def test_response_has_required_fields(self):
        r = client.post("/api/simulate", json={
            "context":   _VALID_CONTEXT,
            "decisions": _VALID_DECISIONS,
        })
        body = r.json()
        for f in ("baseline", "base_effective", "paths", "matrix",
                  "criteria", "user_selection", "rain_states", "rain_probs"):
            assert f in body, f"Campo '{f}' ausente"

    def test_baseline_is_60(self):
        r = client.post("/api/simulate", json={
            "context":   _VALID_CONTEXT,
            "decisions": _VALID_DECISIONS,
        })
        assert r.json()["baseline"] == 60.0

    def test_27_paths_returned(self):
        r = client.post("/api/simulate", json={
            "context":   _VALID_CONTEXT,
            "decisions": _VALID_DECISIONS,
        })
        assert len(r.json()["paths"]) == 27

    def test_missing_context_key_returns_422(self):
        bad_ctx = {k: v for k, v in _VALID_CONTEXT.items() if k != "c1_regiao"}
        r = client.post("/api/simulate", json={
            "context":   bad_ctx,
            "decisions": _VALID_DECISIONS,
        })
        assert r.status_code == 422

    def test_missing_decision_key_returns_422(self):
        bad_dec = {k: v for k, v in _VALID_DECISIONS.items() if k != "d1_janela"}
        r = client.post("/api/simulate", json={
            "context":   _VALID_CONTEXT,
            "decisions": bad_dec,
        })
        assert r.status_code == 422

    def test_invalid_context_value_returns_422(self):
        bad_ctx = {**_VALID_CONTEXT, "c1_regiao": "OPÇÃO_INEXISTENTE"}
        r = client.post("/api/simulate", json={
            "context":   bad_ctx,
            "decisions": _VALID_DECISIONS,
        })
        assert r.status_code == 422

    def test_invalid_decision_value_returns_422(self):
        bad_dec = {**_VALID_DECISIONS, "d5_manejo": "OPÇÃO_INEXISTENTE"}
        r = client.post("/api/simulate", json={
            "context":   _VALID_CONTEXT,
            "decisions": bad_dec,
        })
        assert r.status_code == 422

    def test_empty_body_returns_422(self):
        r = client.post("/api/simulate", json={})
        assert r.status_code == 422

    def test_criteria_keys_present(self):
        r = client.post("/api/simulate", json={
            "context":   _VALID_CONTEXT,
            "decisions": _VALID_DECISIONS,
        })
        criteria = r.json()["criteria"]
        for key in ("maximax", "wald", "laplace", "hurwicz", "bayes_ev", "savage"):
            assert key in criteria

    def test_user_selection_ev_is_numeric(self):
        r = client.post("/api/simulate", json={
            "context":   _VALID_CONTEXT,
            "decisions": _VALID_DECISIONS,
        })
        ev = r.json()["user_selection"]["ev"]
        assert isinstance(ev, float)

    @pytest.mark.parametrize("enso,expected_higher", [
        ("El Niño (chuva regular em MT)",    True),
        ("La Niña (chuva concentrada/curta)", False),
    ])
    def test_enso_impacts_ev(self, enso, expected_higher):
        """Cenários ENSO devem gerar EVs diferentes para o mesmo talhão."""
        ctx_neutro = {**_VALID_CONTEXT, "c7_enso": "Neutro"}
        ctx_enso   = {**_VALID_CONTEXT, "c7_enso": enso}

        r_neutro = client.post("/api/simulate", json={"context": ctx_neutro, "decisions": _VALID_DECISIONS})
        r_enso   = client.post("/api/simulate", json={"context": ctx_enso,   "decisions": _VALID_DECISIONS})

        ev_neutro = r_neutro.json()["user_selection"]["ev"]
        ev_enso   = r_enso.json()["user_selection"]["ev"]

        if expected_higher:
            assert ev_enso > ev_neutro
        else:
            assert ev_enso < ev_neutro

    def test_best_decisions_beat_worst(self):
        """Decisões ótimas devem resultar em EV maior que decisões ruins."""
        best = {
            "d1_janela":     "Ótima (16/out – 10/nov)",
            "d2_cultivar":   "Alto potencial (P98R30, NK6727, BMX Foco; pós-2020)",
            "d3_tsi":        "Premium (fung+inset+nemat+inoc)",
            "d4_densidade":  "Média (280k–340k)",
            "d5_manejo":     "Alto (≥3 fung. + monitor ferrugem)",
            "d6_tecnologia": "Alta precisão (RTK + pneumática moderna)",
        }
        worst = {
            "d1_janela":     "Tardia (após 10/nov)",
            "d2_cultivar":   "Limitado (legados pré-2015)",
            "d3_tsi":        "Sem TSI",
            "d4_densidade":  "Baixa (≤280k sementes/ha)",
            "d5_manejo":     "Baixo (1 ou nenhuma)",
            "d6_tecnologia": "Baixa (espaçamento irregular)",
        }
        r_best  = client.post("/api/simulate", json={"context": _VALID_CONTEXT, "decisions": best})
        r_worst = client.post("/api/simulate", json={"context": _VALID_CONTEXT, "decisions": worst})
        assert r_best.json()["user_selection"]["ev"] > r_worst.json()["user_selection"]["ev"]


# ── POST /api/monte_carlo ─────────────────────────────────────────────────────

class TestMonteCarlo:
    def _payload(self, n_iter=500):
        return {
            "context":   _VALID_CONTEXT,
            "decisions": _VALID_DECISIONS,
            "params":    _VALID_MC_PARAMS,
            "n_iter":    n_iter,
            "threshold": 60.0,
        }

    def test_valid_payload_returns_200(self):
        r = client.post("/api/monte_carlo", json=self._payload())
        assert r.status_code == 200

    def test_response_keys(self):
        r = client.post("/api/monte_carlo", json=self._payload())
        for k in ("yields", "mean", "std", "p5", "p95", "p_below", "tornado"):
            assert k in r.json()

    def test_yields_count(self):
        r = client.post("/api/monte_carlo", json=self._payload(n_iter=200))
        assert len(r.json()["yields"]) == 200

    def test_p_below_between_0_and_1(self):
        r = client.post("/api/monte_carlo", json=self._payload())
        p = r.json()["p_below"]
        assert 0.0 <= p <= 1.0

    def test_missing_params_returns_422(self):
        payload = {k: v for k, v in self._payload().items() if k != "params"}
        r = client.post("/api/monte_carlo", json=payload)
        assert r.status_code == 422
