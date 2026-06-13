"""Geração de PDF para a página de resultados."""

from __future__ import annotations
from datetime import datetime

from frontend.views.results_helpers import (
    _pdf_safe, _shorten,
    _D1_SHORT, _D4_SHORT, _D5_SHORT,
    _janela_guidance, _densidade_guidance, _manejo_guidance,
)


def _build_pdf(
    result: dict, display: dict, user_name: str,
    paths: list, ev_vals: list, states: list, probs: list,
    matrix: list, criteria: dict, baseline: float,
) -> bytes:
    from fpdf import FPDF

    optimal_idx  = criteria["bayes_ev"]["path_idx"]
    optimal_path = paths[optimal_idx]
    optimal_ev   = ev_vals[optimal_idx]

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=18)

    # ── Capa ─────────────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.set_fill_color(13, 43, 24)
    pdf.rect(0, 0, 210, 60, "F")

    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(0, 16)
    pdf.cell(210, 10, "Relatório de Simulação de Safra", align="C")

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(180, 230, 160)
    pdf.set_xy(0, 30)
    pdf.cell(210, 8, "Soja Verão · Mato Grosso", align="C")

    pdf.set_text_color(50, 50, 50)
    pdf.set_xy(18, 72)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 7, f"Produtor: {user_name}")
    pdf.ln(7)
    pdf.set_x(18)
    pdf.cell(0, 7, f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    pdf.ln(7)
    region = _pdf_safe(display.get("Região", "-"))
    pdf.set_x(18)
    pdf.cell(0, 7, _pdf_safe(f"Região: {region}"))

    # ── Resumo Executivo ──────────────────────────────────────────────────────
    pdf.ln(16)
    pdf.set_x(18)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(13, 43, 24)
    pdf.cell(0, 8, "1. Resumo Executivo")
    pdf.ln(10)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(40, 40, 40)
    rec_d1 = _D1_SHORT.get(optimal_path["d1"], optimal_path["d1"])
    rec_d4 = _D4_SHORT.get(optimal_path["d4"], optimal_path["d4"])
    rec_d5 = _D5_SHORT.get(optimal_path["d5"], optimal_path["d5"])
    delta     = optimal_ev - baseline
    delta_str = f"+{delta:.1f}" if delta >= 0 else f"{delta:.1f}"
    mc_opt    = optimal_path.get("mc") or {}

    summary_lines = [
        "A simulação identificou a melhor combinação de manejo para o seu talhão.",
        f"Recomendação principal: {rec_d1}, {rec_d4.lower()}, {rec_d5.lower()}.",
        f"Produtividade esperada: {optimal_ev:.1f} sc/ha ({delta_str} sc/ha vs. referência de {baseline:.0f} sc/ha).",
    ]
    if mc_opt:
        summary_lines.append(
            f"Intervalo de confiança (90%): {mc_opt['p5']:.0f} a {mc_opt['p95']:.0f} sc/ha."
        )
    for line in summary_lines:
        pdf.set_x(18)
        pdf.multi_cell(174, 6, _pdf_safe(line))
        pdf.ln(1)

    # ── Contexto da Lavoura ───────────────────────────────────────────────────
    pdf.ln(8)
    pdf.set_x(18)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(13, 43, 24)
    pdf.cell(0, 8, "2. Contexto da Lavoura")
    pdf.ln(10)

    ctx_rows = [
        ("Regiao",             display.get("Região", "-")),
        ("Textura do Solo",    display.get("Textura", "-")),
        ("pH do Solo",         display.get("pH", "-")),
        ("Drenagem",           display.get("Drenagem", "-")),
        ("Tipo de Solo",       display.get("Tipo de Solo", "-")),
        ("Area Plantada",      display.get("Área", "-")),
        ("Previsao Climatica", display.get("Previsão Climática", "-")),
    ]
    pdf.set_font("Helvetica", "", 9)
    for k, v in ctx_rows:
        pdf.set_x(18)
        pdf.set_fill_color(245, 248, 245)
        pdf.cell(70, 6, _pdf_safe(k), border=0)
        pdf.cell(104, 6, _pdf_safe(str(v)), border=0)
        pdf.ln(7)

    # ── Top 3 Recomendações ───────────────────────────────────────────────────
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(13, 43, 24)
    pdf.set_xy(18, 18)
    pdf.cell(0, 8, "3. Top 3 Recomendações")
    pdf.ln(12)

    ranked = sorted(enumerate(paths), key=lambda x: ev_vals[x[0]], reverse=True)[:3]
    for rank_num, (pidx, path) in enumerate(ranked, 1):
        ev    = ev_vals[pidx]
        mc    = path.get("mc") or {}
        delta = ev - baseline

        pdf.set_x(18)
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(29, 92, 56)
        pdf.cell(0, 7, _pdf_safe(f"#{rank_num} - {_shorten(path)}"))
        pdf.ln(8)

        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(40, 40, 40)
        pdf.set_x(18)
        delta_str2 = f"+{delta:.1f}" if delta >= 0 else f"{delta:.1f}"
        pdf.cell(90, 6, _pdf_safe(f"Produtividade esperada: {ev:.1f} sc/ha ({delta_str2} sc/ha)"))
        pdf.ln(7)
        if mc:
            pdf.set_x(18)
            pdf.cell(0, 6, _pdf_safe(
                f"Intervalo 90%: {mc['p5']:.0f} a {mc['p95']:.0f} sc/ha  |  "
                f"Risco abaixo da referencia: {mc['p_below']:.1%}"
            ))
            pdf.ln(7)

        pdf.set_x(18)
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(80, 80, 80)
        for guidance in [_janela_guidance(path["d1"]), _densidade_guidance(path["d4"]), _manejo_guidance(path["d5"])]:
            if guidance:
                pdf.set_x(22)
                pdf.multi_cell(166, 5, _pdf_safe(f"* {guidance}"))
                pdf.ln(1)
        pdf.ln(6)
        pdf.set_draw_color(220, 220, 220)
        pdf.set_x(18)
        pdf.line(18, pdf.get_y(), 192, pdf.get_y())
        pdf.ln(6)

    # ── Metodologia simplificada ──────────────────────────────────────────────
    pdf.add_page()
    pdf.set_xy(18, 18)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(13, 43, 24)
    pdf.cell(0, 8, "4. Como o Simulador Calcula")
    pdf.ln(12)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(40, 40, 40)
    metodologia = [
        ("Referência regional:",
         f"O modelo parte de {baseline:.0f} sc/ha, produtividade média histórica para soja "
         "no Mato Grosso (fonte CONAB 2023/24)."),
        ("Ajuste pelo contexto do campo:",
         "Região, tipo e textura do solo, pH, drenagem, tamanho da área e previsão climática "
         "ajustam a referência para cima ou para baixo, refletindo o potencial real do seu talhão."),
        ("Avaliação das decisões de manejo:",
         "Janela de plantio, densidade, manejo de doenças, cultivar, tratamento de sementes e "
         "tecnologia da plantadeira são avaliados em diferentes combinações."),
        ("Cenários climáticos:",
         "O simulador considera três cenários de chuva no período crítico (seca, normal e úmida), "
         "com probabilidades baseadas na previsão de El Niño/La Niña informada."),
        ("Análise de risco (Monte Carlo):",
         "São rodadas 1.000 simulações com variações estocásticas nos insumos para estimar o "
         "intervalo de produtividade esperada com 90% de confiança."),
    ]
    for titulo, descricao in metodologia:
        pdf.set_x(18)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(0, 6, _pdf_safe(titulo))
        pdf.ln(6)
        pdf.set_x(22)
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(166, 5, _pdf_safe(descricao))
        pdf.ln(4)

    # ── Glossário ─────────────────────────────────────────────────────────────
    pdf.ln(4)
    pdf.set_x(18)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(13, 43, 24)
    pdf.cell(0, 8, "5. Glossário")
    pdf.ln(10)
    glossario = [
        ("sc/ha",             "Sacas de 60 kg por hectare - unidade de produtividade."),
        ("Janela de plantio", "Periodo ideal de semeadura para o desenvolvimento otimo da cultura."),
        ("TSI",               "Tratamento de Sementes Industrial - aplicacao de fungicida, inseticida, nematicida e inoculante antes do plantio."),
        ("ENSO",              "El Nino-Oscilacao Sul - fenomeno climatico que influencia as chuvas no Centro-Oeste."),
        ("R3-R6",             "Fases de floracao ao enchimento de grao - periodo mais critico para a produtividade."),
        ("P5 / P95",          "Percentis 5 e 95 da distribuicao de resultados - limites do intervalo de 90% de confianca."),
        ("Monte Carlo",       "Metodo de simulacao com milhares de cenarios e variacoes aleatorias para estimar a distribuicao de resultados."),
        ("Latossolo",         "Solo argiloso e bem estruturado, comum no Cerrado - excelente drenagem interna, ideal para soja."),
        ("Ferrugem asiatica", "Principal doenca fungica da soja no MT; exige monitoramento e fungicidas preventivos."),
        ("EV / Bayes",        "Valor esperado: media ponderada pelos cenarios climaticos - criterio principal de recomendacao."),
    ]
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(40, 40, 40)
    for termo, definicao in glossario:
        pdf.set_x(18)
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(46, 5, f"{termo}:")
        pdf.set_font("Helvetica", "", 9)
        pdf.multi_cell(140, 5, definicao)
        pdf.ln(2)

    return bytes(pdf.output())
