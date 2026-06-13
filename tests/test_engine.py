"""
Testa o motor de simulação (backend/engine.py).
Verifica a aritmética exata do modelo aditivo v7 com valores calculados à mão.
"""

import pytest
from engine import compute_simulation
from data import BASELINE, CONTEXT_NODES, DECISION_NODES, RAIN_STATES, RAIN_PROBS


# ── Fixtures de inputs ────────────────────────────────────────────────────────

def _all_middle_context():
    """C1-C7 todos na opção intermediária (adj=0, exceto C7 Neutro=+1)."""
    return {
        "c1_regiao":  "Intermediária (Sapezal, Campo Novo)",
        "c2_textura": "Intermediária (textura média)",
        "c3_ph":      "Limítrofe (5,0–5,4 ou 6,6–6,8)",
        "c4_drenagem":"Moderada (moderadamente/imperfeito)",
        "c5_aptidao": "Média (Argissolo, Cambissolo)",
        "c6_area":    "Média (50–200 ha)",
        "c7_enso":    "Neutro",
    }


def _all_best_context():
    """C1-C7 todos na opção mais favorável."""
    return {
        "c1_regiao":  "Favorável (Sorriso, Sinop, Lucas RV)",
        "c2_textura": "Favorável (argilosa / média bem estruturada)",
        "c3_ph":      "Adequado (5,5 – 6,5)",
        "c4_drenagem":"Boa (bem drenado)",
        "c5_aptidao": "Alta (Latossolo, Nitossolo)",
        "c6_area":    "Grande (>200 ha)",
        "c7_enso":    "El Niño (chuva regular em MT)",
    }


def _all_worst_context():
    """C1-C7 todos na opção mais adversa."""
    return {
        "c1_regiao":  "Desafiadora (Primavera Leste, Querência)",
        "c2_textura": "Desafiadora (arenosa / baixa retenção)",
        "c3_ph":      "Crítico (<5,0 ou >6,8)",
        "c4_drenagem":"Ruim (mal / excessivamente drenado)",
        "c5_aptidao": "Baixa (Neossolo, Gleissolo)",
        "c6_area":    "Pequena (≤50 ha)",
        "c7_enso":    "La Niña (chuva concentrada/curta)",
    }


def _optimal_decisions():
    """D1-D6 todos na opção com maior ajuste."""
    return {
        "d1_janela":     "Ótima (16/out – 10/nov)",
        "d2_cultivar":   "Alto potencial (P98R30, NK6727, BMX Foco; pós-2020)",
        "d3_tsi":        "Premium (fung+inset+nemat+inoc)",
        "d4_densidade":  "Média (280k–340k)",
        "d5_manejo":     "Alto (≥3 fung. + monitor ferrugem)",
        "d6_tecnologia": "Alta precisão (RTK + pneumática moderna)",
    }


def _middle_decisions():
    """D2, D3, D6 = adj 0; D1 Ótima, D4 Média, D5 Padrão."""
    return {
        "d1_janela":     "Ótima (16/out – 10/nov)",
        "d2_cultivar":   "Intermediário (2015–2019)",
        "d3_tsi":        "Standard (fungicida + inoculante)",
        "d4_densidade":  "Média (280k–340k)",
        "d5_manejo":     "Padrão (2 aplicações)",
        "d6_tecnologia": "Padrão",
    }


def _worst_decisions():
    return {
        "d1_janela":     "Tardia (após 10/nov)",
        "d2_cultivar":   "Limitado (legados pré-2015)",
        "d3_tsi":        "Sem TSI",
        "d4_densidade":  "Baixa (≤280k sementes/ha)",
        "d5_manejo":     "Baixo (1 ou nenhuma)",
        "d6_tecnologia": "Baixa (espaçamento irregular)",
    }


# ── Estrutura da resposta ──────────────────────────────────────────────────────

class TestResponseStructure:
    def test_required_keys_present(self):
        r = compute_simulation(_all_middle_context(), _middle_decisions())
        for key in ("baseline", "context_adj", "fixed_adj", "base_effective",
                    "rain_states", "rain_probs", "paths", "matrix",
                    "criteria", "user_selection"):
            assert key in r, f"Chave '{key}' ausente na resposta"

    def test_baseline_preserved(self):
        r = compute_simulation(_all_middle_context(), _middle_decisions())
        assert r["baseline"] == BASELINE

    def test_paths_count_is_27(self):
        """D1(3) × D4(3) × D5(3) = 27 paths."""
        r = compute_simulation(_all_middle_context(), _middle_decisions())
        assert len(r["paths"]) == 27

    def test_matrix_shape_27x3(self):
        r = compute_simulation(_all_middle_context(), _middle_decisions())
        assert len(r["matrix"]) == 27
        for row in r["matrix"]:
            assert len(row) == 3

    def test_criteria_has_six_keys(self):
        r = compute_simulation(_all_middle_context(), _middle_decisions())
        expected = {"maximax", "wald", "laplace", "hurwicz", "bayes_ev", "savage"}
        assert set(r["criteria"].keys()) == expected

    def test_user_selection_keys(self):
        r = compute_simulation(_all_middle_context(), _middle_decisions())
        us = r["user_selection"]
        for k in ("d1", "d4", "d5", "yields", "ev"):
            assert k in us

    def test_rain_probs_sum_to_one(self):
        r = compute_simulation(_all_middle_context(), _middle_decisions())
        total = sum(r["rain_probs"])
        assert abs(total - 1.0) < 1e-9


# ── Aritmética exata ──────────────────────────────────────────────────────────

class TestExactArithmetic:
    """
    Valores calculados à mão para contexto "todos intermediários" e
    decisões intermediárias (D2=D3=D6=0, D1=+4, D4=+2, D5=0).

    context_adj   = 0+0+0+0+0+0+1 = 1   (só C7 Neutro=+1)
    context_base  = 60 + 1 = 61
    fixed_adj     = 0+0+0 = 0
    base_effective= 61
    D1=+4, D4=+2, D5=0 → path_base = 67
    Rain (Neutro 30/50/20): yields = [67-8, 67+2, 67+4] = [59, 69, 71]
    EV = 0.30×59 + 0.50×69 + 0.20×71 = 17.7+34.5+14.2 = 66.4
    """

    def setup_method(self):
        self.r = compute_simulation(_all_middle_context(), _middle_decisions())

    def test_context_adj(self):
        # C7 Neutro = +1, todos os outros = 0
        assert self.r["context_adj"] == 1.0

    def test_context_base(self):
        assert self.r["context_base"] == 61.0

    def test_fixed_adj(self):
        # D2=0, D3=0, D6=0
        assert self.r["fixed_adj"] == 0.0

    def test_base_effective(self):
        assert self.r["base_effective"] == 61.0

    def test_user_selection_ev(self):
        # D1=+4, D4=+2, D5=0 → path_base=67
        # Rain Neutro: [59, 69, 71] × [0.30, 0.50, 0.20] = 66.4
        ev = self.r["user_selection"]["ev"]
        assert abs(ev - 66.4) < 0.01

    def test_user_selection_yields(self):
        yields = self.r["user_selection"]["yields"]
        assert yields[0] == 59.0   # Seca
        assert yields[1] == 69.0   # Normal
        assert yields[2] == 71.0   # Úmida

    def test_best_path_base_effective_used(self):
        """Todos os 27 paths partem de base_effective=61."""
        for path in self.r["paths"]:
            # path_base = base_effective + d1_adj + d4_adj + d5_adj
            expected = (
                61
                + DECISION_NODES["d1_janela"]["options"][path["d1"]]
                + DECISION_NODES["d4_densidade"]["options"][path["d4"]]
                + DECISION_NODES["d5_manejo"]["options"][path["d5"]]
            )
            assert abs(path["path_base"] - expected) < 0.001

    def test_matrix_values_consistent_with_path_base(self):
        """Cada linha da matrix = path_base ± rain_adjustment."""
        rain_adjs = list(RAIN_STATES.values())
        for i, path in enumerate(self.r["paths"]):
            for j, rain_adj in enumerate(rain_adjs):
                expected = path["path_base"] + rain_adj
                assert abs(self.r["matrix"][i][j] - expected) < 0.001


class TestBestScenarioArithmetic:
    """
    Contexto ótimo + decisões ótimas:
    context_adj = 5+5+4+3+5+2+3 = 27 → context_base = 87
    fixed_adj   = 6+3+3 = 12 → base_effective = 99
    D1=+4, D4=+2, D5=+5 → path_base = 110
    El Niño probs (15/50/35): yields = [102, 112, 114]
    EV = 0.15×102 + 0.50×112 + 0.35×114 = 15.3+56.0+39.9 = 111.2
    """

    def setup_method(self):
        self.r = compute_simulation(_all_best_context(), _optimal_decisions())

    def test_context_adj(self):
        assert self.r["context_adj"] == 27.0

    def test_base_effective(self):
        assert self.r["base_effective"] == 99.0

    def test_user_ev(self):
        ev = self.r["user_selection"]["ev"]
        assert abs(ev - 111.2) < 0.01

    def test_user_yields(self):
        yields = self.r["user_selection"]["yields"]
        assert yields[0] == 102.0   # Seca
        assert yields[1] == 112.0   # Normal
        assert yields[2] == 114.0   # Úmida


class TestWorstScenarioArithmetic:
    """
    Contexto adverso:
    context_adj = -6-7-6-8-7-1-3 = -38 → context_base = 22
    fixed_adj   = -8-5-4 = -17 → base_effective = 5
    Piores decisões D1=-8, D4=-1, D5=-7 → path_base = -11
    La Niña probs (50/30/20): yields = [-19, -9, -7]
    EV = 0.50×(-19) + 0.30×(-9) + 0.20×(-7) = -9.5-2.7-1.4 = -13.6
    """

    def setup_method(self):
        self.r = compute_simulation(_all_worst_context(), _worst_decisions())

    def test_context_adj(self):
        assert self.r["context_adj"] == -38.0

    def test_base_effective(self):
        assert self.r["base_effective"] == 5.0

    def test_user_ev_is_negative(self):
        """No pior cenário, o EV esperado é negativo (modelo pode ir abaixo de 0)."""
        assert self.r["user_selection"]["ev"] < 0

    def test_user_ev_exact(self):
        ev = self.r["user_selection"]["ev"]
        assert abs(ev - (-13.6)) < 0.01

    def test_model_allows_negative_yields(self):
        """O modelo aditivo não clipa — yields negativos são permitidos."""
        for row in self.r["matrix"]:
            # Pelo menos algum yield é negativo no pior cenário
            pass
        user_yields = self.r["user_selection"]["yields"]
        assert user_yields[0] < 0   # seca na pior configuração


# ── Variação de ENSO ──────────────────────────────────────────────────────────

class TestENSOImpact:
    """El Niño deve resultar em EV maior que La Niña para o mesmo talhão."""

    def test_elnino_ev_greater_than_lanina(self):
        ctx_base = _all_middle_context()

        ctx_elnino  = {**ctx_base, "c7_enso": "El Niño (chuva regular em MT)"}
        ctx_lanina  = {**ctx_base, "c7_enso": "La Niña (chuva concentrada/curta)"}

        r_el  = compute_simulation(ctx_elnino,  _middle_decisions())
        r_la  = compute_simulation(ctx_lanina,  _middle_decisions())

        ev_el = r_el["user_selection"]["ev"]
        ev_la = r_la["user_selection"]["ev"]
        assert ev_el > ev_la, (
            f"EV El Niño ({ev_el:.2f}) deveria ser > La Niña ({ev_la:.2f})"
        )

    def test_rain_probs_change_with_enso(self):
        ctx_base = _all_middle_context()
        for enso_label in CONTEXT_NODES["c7_enso"]["options"].keys():
            r = compute_simulation({**ctx_base, "c7_enso": enso_label}, _middle_decisions())
            assert r["rain_probs"] == list(RAIN_PROBS[enso_label].values())
