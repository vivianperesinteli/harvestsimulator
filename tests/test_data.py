"""
Testa as constantes e a estrutura dos nós definidos em backend/data.py.
Garante que nenhuma alteração acidental quebre o modelo.
"""

import pytest
from data import BASELINE, CONTEXT_NODES, DECISION_NODES, RAIN_STATES, RAIN_PROBS


class TestBaseline:
    def test_baseline_value(self):
        """Baseline deve ser exatamente 60 sc/ha (CONAB MT 2023/24)."""
        assert BASELINE == 60.0

    def test_baseline_is_float(self):
        assert isinstance(BASELINE, float)


class TestContextNodes:
    def test_seven_context_nodes(self):
        """Devem existir exatamente 7 nós de contexto C1–C7."""
        assert len(CONTEXT_NODES) == 7

    def test_required_keys_present(self):
        expected = {"c1_regiao", "c2_textura", "c3_ph", "c4_drenagem",
                    "c5_aptidao", "c6_area", "c7_enso"}
        assert set(CONTEXT_NODES.keys()) == expected

    def test_each_node_has_three_options(self):
        for key, node in CONTEXT_NODES.items():
            assert len(node["options"]) == 3, (
                f"Nó {key} deveria ter 3 opções, tem {len(node['options'])}"
            )

    def test_each_node_has_label(self):
        for key, node in CONTEXT_NODES.items():
            assert "label" in node, f"Nó {key} sem campo 'label'"
            assert node["label"]

    def test_adjustments_are_numeric(self):
        for key, node in CONTEXT_NODES.items():
            for opt, adj in node["options"].items():
                assert isinstance(adj, (int, float)), (
                    f"{key} → '{opt}': ajuste deve ser número, é {type(adj)}"
                )

    def test_c7_enso_has_positive_neutral_negative(self):
        """El Niño > Neutro > La Niña em ajuste."""
        opts = CONTEXT_NODES["c7_enso"]["options"]
        vals = list(opts.values())
        assert max(vals) > 0, "El Niño deve ter ajuste positivo"
        assert min(vals) < 0, "La Niña deve ter ajuste negativo"

    @pytest.mark.parametrize("key,expected_order", [
        ("c1_regiao",  [5, 0, -6]),
        ("c3_ph",      [4, 0, -6]),
        ("c4_drenagem",[3, 0, -8]),
        ("c5_aptidao", [5, 0, -7]),
    ])
    def test_adjustment_ordering(self, key, expected_order):
        """Primeiro=favorável, segundo=neutro, terceiro=adverso."""
        vals = list(CONTEXT_NODES[key]["options"].values())
        assert vals == expected_order, (
            f"{key}: esperado {expected_order}, obtido {vals}"
        )


class TestDecisionNodes:
    def test_six_decision_nodes(self):
        """Devem existir exatamente 6 nós de decisão D1–D6."""
        assert len(DECISION_NODES) == 6

    def test_required_keys_present(self):
        expected = {"d1_janela", "d2_cultivar", "d3_tsi",
                    "d4_densidade", "d5_manejo", "d6_tecnologia"}
        assert set(DECISION_NODES.keys()) == expected

    def test_each_node_has_three_options(self):
        for key, node in DECISION_NODES.items():
            assert len(node["options"]) == 3

    def test_matrix_nodes_have_nonzero_best(self):
        """D1, D4, D5 (os nós da Payoff Matrix) devem ter ajuste ótimo > 0."""
        for key in ("d1_janela", "d4_densidade", "d5_manejo"):
            max_adj = max(DECISION_NODES[key]["options"].values())
            assert max_adj > 0, f"{key}: melhor ajuste deveria ser > 0"

    @pytest.mark.parametrize("key,expected_best_adj", [
        ("d1_janela",    4),
        ("d2_cultivar",  6),
        ("d3_tsi",       3),
        ("d4_densidade", 2),
        ("d5_manejo",    5),
        ("d6_tecnologia",3),
    ])
    def test_best_adjustment_value(self, key, expected_best_adj):
        best = max(DECISION_NODES[key]["options"].values())
        assert best == expected_best_adj


class TestRainStates:
    def test_three_rain_states(self):
        assert len(RAIN_STATES) == 3

    def test_state_names(self):
        names = list(RAIN_STATES.keys())
        assert "Seca" in names[0]
        assert "Normal" in names[1]
        assert any("mida" in n for n in names)   # Úmida

    def test_rain_adjustments_ordered(self):
        """Seca < Normal < Úmida em ajuste."""
        adjs = list(RAIN_STATES.values())
        assert adjs[0] < adjs[1] < adjs[2]

    def test_seca_negative(self):
        seca_adj = list(RAIN_STATES.values())[0]
        assert seca_adj < 0

    def test_umida_positive(self):
        umida_adj = list(RAIN_STATES.values())[2]
        assert umida_adj > 0


class TestRainProbs:
    def test_three_enso_scenarios(self):
        assert len(RAIN_PROBS) == 3

    def test_enso_keys_match_c7_options(self):
        c7_opts = set(CONTEXT_NODES["c7_enso"]["options"].keys())
        rain_keys = set(RAIN_PROBS.keys())
        assert c7_opts == rain_keys, (
            f"Chaves RAIN_PROBS não batem com opções c7_enso.\n"
            f"c7_enso: {c7_opts}\nRAIN_PROBS: {rain_keys}"
        )

    @pytest.mark.parametrize("enso_key", list(RAIN_PROBS.keys()))
    def test_probs_sum_to_one(self, enso_key):
        total = sum(RAIN_PROBS[enso_key].values())
        assert abs(total - 1.0) < 1e-9, (
            f"{enso_key}: probabilidades somam {total}, esperado 1.0"
        )

    @pytest.mark.parametrize("enso_key", list(RAIN_PROBS.keys()))
    def test_all_probs_positive(self, enso_key):
        for state, p in RAIN_PROBS[enso_key].items():
            assert p > 0, f"{enso_key} → {state}: prob deve ser > 0"

    def test_elnino_has_lower_seca_prob_than_lanina(self):
        """El Niño tem menos seca que La Niña no MT."""
        elnino_seca = RAIN_PROBS[
            next(k for k in RAIN_PROBS if "Ni" in k and "El" in k)
        ]
        lanina_seca = RAIN_PROBS[
            next(k for k in RAIN_PROBS if "Ni" in k and "La" in k)
        ]
        seca_key = next(k for k in RAIN_STATES if "Seca" in k)
        assert elnino_seca[seca_key] < lanina_seca[seca_key]
