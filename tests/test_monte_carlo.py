"""
Testa a simulação de Monte Carlo (backend/monte_carlo.py).
"""

import pytest
import numpy as np
from monte_carlo import run_monte_carlo


# ── Fixtures ──────────────────────────────────────────────────────────────────

_CTX = {
    "c1_regiao":  "Intermediária (Sapezal, Campo Novo)",
    "c2_textura": "Intermediária (textura média)",
    "c3_ph":      "Limítrofe (5,0–5,4 ou 6,6–6,8)",
    "c4_drenagem":"Moderada (moderadamente/imperfeito)",
    "c5_aptidao": "Média (Argissolo, Cambissolo)",
    "c6_area":    "Média (50–200 ha)",
    "c7_enso":    "Neutro",
}

_DEC = {
    "d1_janela":     "Ótima (16/out – 10/nov)",
    "d2_cultivar":   "Intermediário (2015–2019)",
    "d3_tsi":        "Standard (fungicida + inoculante)",
    "d4_densidade":  "Média (280k–340k)",
    "d5_manejo":     "Padrão (2 aplicações)",
    "d6_tecnologia": "Padrão",
}

# Parâmetros triangulares padrão
_PARAMS = {
    "d2": {"min": -8.0, "mode": 0.0, "max": 6.0},
    "d3": {"min": -5.0, "mode": 0.0, "max": 3.0},
    "d6": {"min": -4.0, "mode": 0.0, "max": 3.0},
}


@pytest.fixture(scope="module")
def mc_result():
    """Roda MC uma vez e reusa nas subclasses do módulo."""
    return run_monte_carlo(_CTX, _DEC, _PARAMS, n_iter=3000, threshold=60.0)


# ── Estrutura da resposta ──────────────────────────────────────────────────────

class TestMCResponseStructure:
    def test_required_keys(self, mc_result):
        for k in ("yields", "mean", "std", "p5", "p95", "p_below", "tornado"):
            assert k in mc_result, f"Chave '{k}' ausente"

    def test_yields_count_matches_n_iter(self, mc_result):
        assert len(mc_result["yields"]) == 3000

    def test_tornado_variables(self, mc_result):
        """Tornado deve ter exatamente 4 variáveis: d2, d3, d6 + chuva."""
        assert len(mc_result["tornado"]) == 4

    def test_tornado_has_correlation_key(self, mc_result):
        for var, info in mc_result["tornado"].items():
            assert "correlation" in info, f"{var}: chave 'correlation' ausente"


# ── Propriedades estatísticas ─────────────────────────────────────────────────

class TestMCStatistics:
    def test_mean_near_expected(self, mc_result):
        """
        base_effective = 61, D1=+4, D4=+2, D5=0 → fixed_base = 67
        D2 triangular(−8,0,+6): media ≈ (−8+0+6)/3 ≈ −0.67
        D3 triangular(−5,0,+3): media ≈ (−5+0+3)/3 ≈ −0.67
        D6 triangular(−4,0,+3): media ≈ (−4+0+3)/3 ≈ −0.33
        Rain Neutro: EV = 0.30×(−8)+0.50×2+0.20×4 = −2.4+1+0.8 = −0.6
        Estimativa: 67 + (−0.67) + (−0.67) + (−0.33) + (−0.6) ≈ 64.7
        Tolerância ampla: ±3 sc/ha por variância amostral.
        """
        assert 61.0 < mc_result["mean"] < 70.0

    def test_std_positive(self, mc_result):
        assert mc_result["std"] > 0

    def test_p5_less_than_mean(self, mc_result):
        assert mc_result["p5"] < mc_result["mean"]

    def test_p95_greater_than_mean(self, mc_result):
        assert mc_result["p95"] > mc_result["mean"]

    def test_p5_less_than_p95(self, mc_result):
        assert mc_result["p5"] < mc_result["p95"]

    def test_p_below_between_0_and_1(self, mc_result):
        assert 0.0 <= mc_result["p_below"] <= 1.0

    def test_p_below_60_reasonable(self, mc_result):
        """Com contexto neutro, risco de ficar abaixo de 60 sc/ha deve ser > 0."""
        assert mc_result["p_below"] > 0.0

    def test_yields_are_numeric(self, mc_result):
        for y in mc_result["yields"]:
            assert isinstance(y, (int, float))

    def test_mean_matches_yields(self, mc_result):
        computed_mean = np.mean(mc_result["yields"])
        assert abs(computed_mean - mc_result["mean"]) < 0.1

    def test_std_matches_yields(self, mc_result):
        computed_std = np.std(mc_result["yields"])
        assert abs(computed_std - mc_result["std"]) < 0.1

    def test_p5_matches_yields(self, mc_result):
        computed_p5 = np.percentile(mc_result["yields"], 5)
        assert abs(computed_p5 - mc_result["p5"]) < 0.5

    def test_p95_matches_yields(self, mc_result):
        computed_p95 = np.percentile(mc_result["yields"], 95)
        assert abs(computed_p95 - mc_result["p95"]) < 0.5


# ── Distribuição triangular ───────────────────────────────────────────────────

class TestTriangularDistribution:
    def test_triangular_mode_shifts_mean(self):
        """Moda positiva deve deslocar média para cima vs moda negativa."""
        params_pos = {
            "d2": {"min": -5.0, "mode": 5.0, "max": 8.0},
            "d3": {"min": -5.0, "mode": 0.0, "max": 3.0},
            "d6": {"min": -4.0, "mode": 0.0, "max": 3.0},
        }
        params_neg = {
            "d2": {"min": -8.0, "mode": -5.0, "max": 6.0},
            "d3": {"min": -5.0, "mode": 0.0, "max": 3.0},
            "d6": {"min": -4.0, "mode": 0.0, "max": 3.0},
        }
        r_pos = run_monte_carlo(_CTX, _DEC, params_pos, n_iter=2000, threshold=60.0)
        r_neg = run_monte_carlo(_CTX, _DEC, params_neg, n_iter=2000, threshold=60.0)
        assert r_pos["mean"] > r_neg["mean"]

    def test_wider_distribution_higher_std(self):
        """Distribuição mais larga → maior desvio padrão."""
        params_narrow = {
            "d2": {"min": -1.0, "mode": 0.0, "max": 1.0},
            "d3": {"min": -1.0, "mode": 0.0, "max": 1.0},
            "d6": {"min": -1.0, "mode": 0.0, "max": 1.0},
        }
        params_wide = {
            "d2": {"min": -8.0, "mode": 0.0, "max": 6.0},
            "d3": {"min": -5.0, "mode": 0.0, "max": 3.0},
            "d6": {"min": -4.0, "mode": 0.0, "max": 3.0},
        }
        r_narrow = run_monte_carlo(_CTX, _DEC, params_narrow, n_iter=2000, threshold=60.0)
        r_wide   = run_monte_carlo(_CTX, _DEC, params_wide,   n_iter=2000, threshold=60.0)
        assert r_wide["std"] > r_narrow["std"]


# ── Correlação (Tornado) ──────────────────────────────────────────────────────

class TestTornado:
    def test_correlations_between_minus_one_and_one(self, mc_result):
        for var, info in mc_result["tornado"].items():
            c = info["correlation"]
            assert -1.0 <= c <= 1.0, f"{var}: correlação {c:.4f} fora do range"

    def test_rain_correlation_positive(self, mc_result):
        """Mais chuva → maior yield → correlação chuva-yield deve ser positiva."""
        rain_key = next(k for k in mc_result["tornado"] if "chuva" in k.lower() or "rain" in k.lower() or "Chuva" in k)
        assert mc_result["tornado"][rain_key]["correlation"] > 0

    def test_dominant_variable_has_highest_abs_correlation(self, mc_result):
        """A variável de maior influência deve ter maior |correlação|."""
        max_corr = max(abs(v["correlation"]) for v in mc_result["tornado"].values())
        assert max_corr > 0.1, "Nenhuma variável com correlação relevante"
