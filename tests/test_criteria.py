"""
Testa cada critério de decisão isoladamente (backend/engine.py: _compute_criteria).
"""

import pytest
from engine import _compute_criteria


# ── Matriz de controle para testes ────────────────────────────────────────────
#
# 3 alternativas, 3 estados de natureza.
#
# Linha 0: [10, 20, 30]   → max=30, min=10, avg=20
# Linha 1: [25, 25, 25]   → max=25, min=25, avg=25
# Linha 2: [15, 15, 50]   → max=50, min=15, avg=26.7
#
# Probabilidades uniformes: [1/3, 1/3, 1/3]

_MATRIX = [
    [10.0, 20.0, 30.0],
    [25.0, 25.0, 25.0],
    [15.0, 15.0, 50.0],
]
_PROBS_UNIFORM = [1/3, 1/3, 1/3]
_PROBS_SKEWED  = [0.60, 0.30, 0.10]  # alto peso no pior estado


class TestMaximax:
    """Maximax: para cada linha, toma o máximo; escolhe a linha com maior máximo."""

    def test_maximax_chooses_row_with_highest_max(self):
        # max por linha: [30, 25, 50] → idx 2
        result = _compute_criteria(_MATRIX, _PROBS_UNIFORM)
        assert result["maximax"]["path_idx"] == 2

    def test_maximax_value(self):
        result = _compute_criteria(_MATRIX, _PROBS_UNIFORM)
        assert result["maximax"]["value"] == 50.0

    def test_maximax_criterion_values_correct(self):
        result = _compute_criteria(_MATRIX, _PROBS_UNIFORM)
        assert result["maximax"]["criterion_values"] == [30.0, 25.0, 50.0]

    def test_maximax_matrix_one_path(self):
        """Com uma só linha, a resposta é a própria linha."""
        r = _compute_criteria([[5.0, 10.0, 3.0]], [0.4, 0.4, 0.2])
        assert r["maximax"]["path_idx"] == 0
        assert r["maximax"]["value"]    == 10.0


class TestWald:
    """Wald (Maximin): para cada linha, toma o mínimo; escolhe a maior."""

    def test_wald_chooses_row_with_highest_min(self):
        # min por linha: [10, 25, 15] → idx 1 (min=25 é o maior)
        result = _compute_criteria(_MATRIX, _PROBS_UNIFORM)
        assert result["wald"]["path_idx"] == 1

    def test_wald_value(self):
        result = _compute_criteria(_MATRIX, _PROBS_UNIFORM)
        assert result["wald"]["value"] == 25.0

    def test_wald_criterion_values(self):
        result = _compute_criteria(_MATRIX, _PROBS_UNIFORM)
        assert result["wald"]["criterion_values"] == [10.0, 25.0, 15.0]

    def test_wald_prefers_safe_path(self):
        """Wald prefere estabilidade a alto potencial com alto risco."""
        matrix = [
            [100.0, 100.0, 100.0],   # estável
            [0.0,   50.0,  200.0],   # alto potencial, alto risco
        ]
        r = _compute_criteria(matrix, [0.4, 0.4, 0.2])
        assert r["wald"]["path_idx"] == 0  # linha estável é mais segura


class TestLaplace:
    """Laplace: média simples dos estados (equiprováveis)."""

    def test_laplace_uses_equal_weights(self):
        # médias: [20, 25, 26.67] → idx 2
        result = _compute_criteria(_MATRIX, _PROBS_UNIFORM)
        assert result["laplace"]["path_idx"] == 2

    def test_laplace_value(self):
        result = _compute_criteria(_MATRIX, _PROBS_UNIFORM)
        expected = (15 + 15 + 50) / 3
        assert abs(result["laplace"]["value"] - expected) < 0.01

    def test_laplace_ignores_input_probs(self):
        """Laplace deve usar probabilidades iguais, independente das passadas."""
        r1 = _compute_criteria(_MATRIX, _PROBS_UNIFORM)
        r2 = _compute_criteria(_MATRIX, _PROBS_SKEWED)
        assert r1["laplace"]["path_idx"] == r2["laplace"]["path_idx"]
        assert abs(r1["laplace"]["value"] - r2["laplace"]["value"]) < 0.001


class TestHurwicz:
    """Hurwicz α=0,5: 0,5 × max + 0,5 × min."""

    def test_hurwicz_formula(self):
        # linha 0: 0.5×30 + 0.5×10 = 20
        # linha 1: 0.5×25 + 0.5×25 = 25
        # linha 2: 0.5×50 + 0.5×15 = 32.5  → idx 2
        result = _compute_criteria(_MATRIX, _PROBS_UNIFORM)
        assert result["hurwicz"]["path_idx"] == 2
        assert abs(result["hurwicz"]["value"] - 32.5) < 0.01

    def test_hurwicz_criterion_values(self):
        result = _compute_criteria(_MATRIX, _PROBS_UNIFORM)
        vals = result["hurwicz"]["criterion_values"]
        assert abs(vals[0] - 20.0)  < 0.01
        assert abs(vals[1] - 25.0)  < 0.01
        assert abs(vals[2] - 32.5)  < 0.01

    def test_hurwicz_between_maximax_and_wald(self):
        """Valor Hurwicz deve ser entre o pior (Wald) e o melhor (Maximax)."""
        result = _compute_criteria(_MATRIX, _PROBS_UNIFORM)
        wald_v     = result["wald"]["value"]
        maximax_v  = result["maximax"]["value"]
        hurwicz_v  = result["hurwicz"]["value"]
        assert wald_v <= hurwicz_v <= maximax_v


class TestBayesEV:
    """Bayes EV: esperança ponderada pelas probabilidades de entrada."""

    def test_bayes_uses_input_probs(self):
        """Com probs skewed (p_seca=0.60), linha estável deve ganhar do arriscado."""
        matrix = [
            [0.0,   50.0,  200.0],   # alto risco
            [100.0, 100.0, 100.0],   # estável
        ]
        r = _compute_criteria(matrix, [0.60, 0.30, 0.10])
        # EV linha 0: 0.6×0 + 0.3×50 + 0.1×200 = 0+15+20 = 35
        # EV linha 1: 0.6×100 + 0.3×100 + 0.1×100 = 100
        assert r["bayes_ev"]["path_idx"] == 1
        assert abs(r["bayes_ev"]["value"] - 100.0) < 0.01

    def test_bayes_changes_with_probs(self):
        """Mesmo payoff, probabilidades diferentes → recomendações diferentes."""
        matrix = [
            [0.0,  100.0],
            [40.0,  40.0],
        ]
        # Prob uniforme: EV[0]=50, EV[1]=40 → escolhe 0
        r1 = _compute_criteria(matrix, [0.5, 0.5])
        assert r1["bayes_ev"]["path_idx"] == 0

        # Prob pesada em estado 0: EV[0]=0×0.9+100×0.1=10, EV[1]=40 → escolhe 1
        r2 = _compute_criteria(matrix, [0.9, 0.1])
        assert r2["bayes_ev"]["path_idx"] == 1

    def test_bayes_criterion_values_are_weighted_averages(self):
        matrix = [[10.0, 20.0, 30.0]]
        probs  = [0.2, 0.5, 0.3]
        r = _compute_criteria(matrix, probs)
        expected = 0.2*10 + 0.5*20 + 0.3*30  # = 2 + 10 + 9 = 21
        assert abs(r["bayes_ev"]["criterion_values"][0] - expected) < 0.001


class TestSavage:
    """Savage (Minimax Regret): minimiza o máximo arrependimento."""

    def test_savage_computation(self):
        """
        Matriz:
        [10, 20, 30]
        [25, 25, 25]
        [15, 15, 50]

        Máximos por coluna: [25, 25, 50]
        Regrets:
          linha 0: [15, 5, 20] → max = 20
          linha 1: [0,  0, 25] → max = 25
          linha 2: [10, 10, 0] → max = 10
        → Minimax regret: linha 2 (regret=10)
        """
        result = _compute_criteria(_MATRIX, _PROBS_UNIFORM)
        assert result["savage"]["path_idx"] == 2
        assert result["savage"]["value"] == 10.0

    def test_savage_criterion_values(self):
        result = _compute_criteria(_MATRIX, _PROBS_UNIFORM)
        vals = result["savage"]["criterion_values"]
        assert vals[0] == 20.0
        assert vals[1] == 25.0
        assert vals[2] == 10.0

    def test_dominant_path_has_zero_regret(self):
        """Se um path domina todos os outros em todos os estados, regret=0."""
        matrix = [
            [100.0, 100.0, 100.0],
            [ 50.0,  50.0,  50.0],
        ]
        r = _compute_criteria(matrix, [0.5, 0.3, 0.2])
        assert r["savage"]["value"] == 0.0
        assert r["savage"]["path_idx"] == 0


class TestCriteriaConsistency:
    """Testes de consistência entre critérios."""

    def test_path_indices_in_valid_range(self):
        result = _compute_criteria(_MATRIX, _PROBS_UNIFORM)
        n = len(_MATRIX)
        for key in ("maximax", "wald", "laplace", "hurwicz", "bayes_ev", "savage"):
            idx = result[key]["path_idx"]
            assert 0 <= idx < n, f"{key}: path_idx={idx} fora do range [0, {n})"

    def test_criterion_values_length_matches_matrix(self):
        result = _compute_criteria(_MATRIX, _PROBS_UNIFORM)
        for key in ("maximax", "wald", "laplace", "hurwicz", "bayes_ev", "savage"):
            vals = result[key]["criterion_values"]
            assert len(vals) == len(_MATRIX), (
                f"{key}: {len(vals)} valores, esperado {len(_MATRIX)}"
            )

    def test_unanimous_best_path(self):
        """Quando um path domina todos os outros, todos os critérios devem apontá-lo."""
        dominant = [100.0, 100.0, 100.0]
        matrix   = [dominant, [50.0, 50.0, 50.0], [40.0, 60.0, 30.0]]
        result   = _compute_criteria(matrix, [0.4, 0.4, 0.2])
        for key in ("maximax", "wald", "laplace", "hurwicz", "bayes_ev"):
            assert result[key]["path_idx"] == 0, (
                f"{key} não apontou para o path dominante"
            )
