"""
Testa os mapeamentos do frontend (frontend/views/input.py).
Garante que cada label exibido ao usuário produz um valor aceito pelo backend.
"""

import pytest
from datetime import date

from frontend.views.input import (
    _C1_OPTIONS, _C2_OPTIONS, _C3_OPTIONS, _C4_OPTIONS,
    _C5_OPTIONS, _C6_OPTIONS, _C7_OPTIONS,
    _D2_OPTIONS, _D6_OPTIONS,
    _map_janela, _map_tsi, _map_densidade, _map_manejo,
)
from data import CONTEXT_NODES, DECISION_NODES


# ── Todos os mapeamentos produzem valores válidos para a API ──────────────────

class TestContextMappingsValid:
    """Cada opção de display deve mapear para uma chave válida na API."""

    @pytest.mark.parametrize("display_val,api_val", list(_C1_OPTIONS.items()))
    def test_c1_options(self, display_val, api_val):
        assert api_val in CONTEXT_NODES["c1_regiao"]["options"], (
            f"C1 '{api_val}' não encontrado"
        )

    @pytest.mark.parametrize("display_val,api_val", list(_C2_OPTIONS.items()))
    def test_c2_options(self, display_val, api_val):
        assert api_val in CONTEXT_NODES["c2_textura"]["options"]

    @pytest.mark.parametrize("display_val,api_val", list(_C3_OPTIONS.items()))
    def test_c3_options(self, display_val, api_val):
        assert api_val in CONTEXT_NODES["c3_ph"]["options"]

    @pytest.mark.parametrize("display_val,api_val", list(_C4_OPTIONS.items()))
    def test_c4_options(self, display_val, api_val):
        assert api_val in CONTEXT_NODES["c4_drenagem"]["options"]

    @pytest.mark.parametrize("display_val,api_val", list(_C5_OPTIONS.items()))
    def test_c5_options(self, display_val, api_val):
        assert api_val in CONTEXT_NODES["c5_aptidao"]["options"]

    @pytest.mark.parametrize("display_val,api_val", list(_C6_OPTIONS.items()))
    def test_c6_options(self, display_val, api_val):
        assert api_val in CONTEXT_NODES["c6_area"]["options"]

    @pytest.mark.parametrize("display_val,api_val", list(_C7_OPTIONS.items()))
    def test_c7_options(self, display_val, api_val):
        assert api_val in CONTEXT_NODES["c7_enso"]["options"]

    def test_all_context_nodes_covered(self):
        """Cada nó de contexto deve ter pelo menos um mapeamento."""
        maps_by_node = {
            "c1_regiao":  _C1_OPTIONS,
            "c2_textura": _C2_OPTIONS,
            "c3_ph":      _C3_OPTIONS,
            "c4_drenagem":_C4_OPTIONS,
            "c5_aptidao": _C5_OPTIONS,
            "c6_area":    _C6_OPTIONS,
            "c7_enso":    _C7_OPTIONS,
        }
        for node_key, mapping in maps_by_node.items():
            assert len(mapping) == 3, f"{node_key}: esperado 3 opções, tem {len(mapping)}"


class TestDecisionMappingsValid:
    @pytest.mark.parametrize("display_val,api_val", list(_D2_OPTIONS.items()))
    def test_d2_options(self, display_val, api_val):
        assert api_val in DECISION_NODES["d2_cultivar"]["options"]

    @pytest.mark.parametrize("display_val,api_val", list(_D6_OPTIONS.items()))
    def test_d6_options(self, display_val, api_val):
        assert api_val in DECISION_NODES["d6_tecnologia"]["options"]

    def test_d2_covers_all_api_options(self):
        """Todos os cultivares da API devem ter um display correspondente."""
        api_vals = set(DECISION_NODES["d2_cultivar"]["options"].keys())
        mapped   = set(_D2_OPTIONS.values())
        assert api_vals == mapped, (
            f"D2 não cobre: {api_vals - mapped}"
        )

    def test_d6_covers_all_api_options(self):
        api_vals = set(DECISION_NODES["d6_tecnologia"]["options"].keys())
        mapped   = set(_D6_OPTIONS.values())
        assert api_vals == mapped


# ── _map_janela ───────────────────────────────────────────────────────────────

class TestMapJanela:
    @pytest.mark.parametrize("d,expected", [
        (date(2024,  9,  1), "Precoce (até 15/out)"),
        (date(2024, 10, 14), "Precoce (até 15/out)"),
        (date(2024, 10, 15), "Precoce (até 15/out)"),
        (date(2024, 10, 16), "Ótima (16/out – 10/nov)"),
        (date(2024, 10, 20), "Ótima (16/out – 10/nov)"),
        (date(2024, 11, 10), "Ótima (16/out – 10/nov)"),
        (date(2024, 11, 11), "Tardia (após 10/nov)"),
        (date(2024, 12, 15), "Tardia (após 10/nov)"),
    ])
    def test_date_to_janela(self, d, expected):
        assert _map_janela(d) == expected

    def test_result_is_valid_api_option(self):
        api_opts = set(DECISION_NODES["d1_janela"]["options"].keys())
        for d in (date(2024, 10, 1), date(2024, 10, 20), date(2024, 12, 1)):
            assert _map_janela(d) in api_opts

    def test_boundary_oct15(self):
        assert _map_janela(date(2024, 10, 15)) == "Precoce (até 15/out)"
        assert _map_janela(date(2024, 10, 16)) == "Ótima (16/out – 10/nov)"

    def test_boundary_nov10(self):
        assert _map_janela(date(2024, 11, 10)) == "Ótima (16/out – 10/nov)"
        assert _map_janela(date(2024, 11, 11)) == "Tardia (após 10/nov)"


# ── _map_tsi ──────────────────────────────────────────────────────────────────

class TestMapTSI:
    def test_all_four_components_gives_premium(self):
        r = _map_tsi(["Fungicida", "Inoculante", "Inseticida", "Nematicida"])
        assert r == "Premium (fung+inset+nemat+inoc)"

    def test_inset_plus_nemat_plus_one_gives_premium(self):
        r = _map_tsi(["Inseticida", "Nematicida", "Fungicida"])
        assert r == "Premium (fung+inset+nemat+inoc)"

    def test_fungicida_inoculante_only_gives_standard(self):
        r = _map_tsi(["Fungicida", "Inoculante"])
        assert r == "Standard (fungicida + inoculante)"

    def test_only_fungicida_gives_standard(self):
        r = _map_tsi(["Fungicida"])
        assert r == "Standard (fungicida + inoculante)"

    def test_only_inoculante_gives_standard(self):
        r = _map_tsi(["Inoculante"])
        assert r == "Standard (fungicida + inoculante)"

    def test_empty_gives_sem_tsi(self):
        r = _map_tsi([])
        assert r == "Sem TSI"

    def test_all_results_are_valid_api_options(self):
        api_opts = set(DECISION_NODES["d3_tsi"]["options"].keys())
        combos = [
            [],
            ["Fungicida"],
            ["Inoculante"],
            ["Fungicida", "Inoculante"],
            ["Fungicida", "Inoculante", "Inseticida"],
            ["Fungicida", "Inoculante", "Inseticida", "Nematicida"],
        ]
        for combo in combos:
            r = _map_tsi(combo)
            assert r in api_opts, f"_map_tsi({combo!r}) = {r!r} não é opção válida"

    def test_inset_nemat_without_fungicida_gives_premium(self):
        """Inseticida + Nematicida, mesmo sem fungicida, cobre o critério premium."""
        r = _map_tsi(["Inseticida", "Nematicida", "Inoculante"])
        assert r == "Premium (fung+inset+nemat+inoc)"


# ── _map_densidade ────────────────────────────────────────────────────────────

class TestMapDensidade:
    @pytest.mark.parametrize("seeds,expected", [
        (150_000, "Baixa (≤280k sementes/ha)"),
        (280_000, "Baixa (≤280k sementes/ha)"),
        (280_001, "Média (280k–340k)"),
        (310_000, "Média (280k–340k)"),
        (340_000, "Média (280k–340k)"),
        (340_001, "Alta (>340k)"),
        (500_000, "Alta (>340k)"),
    ])
    def test_density_mapping(self, seeds, expected):
        assert _map_densidade(seeds) == expected

    def test_boundary_280k(self):
        assert _map_densidade(280_000) == "Baixa (≤280k sementes/ha)"
        assert _map_densidade(280_001) == "Média (280k–340k)"

    def test_boundary_340k(self):
        assert _map_densidade(340_000) == "Média (280k–340k)"
        assert _map_densidade(340_001) == "Alta (>340k)"

    def test_all_results_are_valid_api_options(self):
        api_opts = set(DECISION_NODES["d4_densidade"]["options"].keys())
        for seeds in (200_000, 310_000, 400_000):
            r = _map_densidade(seeds)
            assert r in api_opts


# ── _map_manejo ───────────────────────────────────────────────────────────────

class TestMapManejo:
    @pytest.mark.parametrize("n_apps,monitoring,expected", [
        (3, True,  "Alto (≥3 fung. + monitor ferrugem)"),
        (4, True,  "Alto (≥3 fung. + monitor ferrugem)"),
        (3, False, "Padrão (2 aplicações)"),   # sem monitoramento → padrão
        (2, True,  "Padrão (2 aplicações)"),   # menos de 3 apps → padrão
        (2, False, "Padrão (2 aplicações)"),
        (1, False, "Baixo (1 ou nenhuma)"),
        (0, False, "Baixo (1 ou nenhuma)"),
        (1, True,  "Baixo (1 ou nenhuma)"),    # 1 app, mesmo com monitor → baixo
    ])
    def test_manejo_mapping(self, n_apps, monitoring, expected):
        assert _map_manejo(n_apps, monitoring) == expected

    def test_all_results_are_valid_api_options(self):
        api_opts = set(DECISION_NODES["d5_manejo"]["options"].keys())
        for n, m in [(0,False), (2,False), (3,True)]:
            r = _map_manejo(n, m)
            assert r in api_opts
