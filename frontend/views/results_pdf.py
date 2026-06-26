"""PDF generation for the results page."""

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
    pdf.cell(210, 10, "Crop Simulation Report", align="C")

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(180, 230, 160)
    pdf.set_xy(0, 30)
    pdf.cell(210, 8, "Soy . Mato Grosso", align="C")

    pdf.set_text_color(50, 50, 50)
    pdf.set_xy(18, 72)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 7, f"Producer: {user_name}")
    pdf.ln(7)
    pdf.set_x(18)
    pdf.cell(0, 7, f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    pdf.ln(7)
    region = _pdf_safe(display.get("Region", "-"))
    pdf.set_x(18)
    pdf.cell(0, 7, _pdf_safe(f"Region: {region}"))

    # ── Resumo Executivo ──────────────────────────────────────────────────────
    pdf.ln(16)
    pdf.set_x(18)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(13, 43, 24)
    pdf.cell(0, 8, "1. Executive Summary")
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
        "The simulation identified the best management combination for your field.",
        f"Main recommendation: {rec_d1}, {rec_d4.lower()}, {rec_d5.lower()}.",
        f"Expected yield: {optimal_ev:.1f} sc/ha ({delta_str} sc/ha vs. reference of {baseline:.0f} sc/ha).",
    ]
    if mc_opt:
        summary_lines.append(
            f"Confidence interval (90%): {mc_opt['p5']:.0f} to {mc_opt['p95']:.0f} sc/ha."
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
    pdf.cell(0, 8, "2. Field Context")
    pdf.ln(10)

    ctx_rows = [
        ("Region",             display.get("Region", "-")),
        ("Soil Texture",       display.get("Texture", "-")),
        ("Soil pH",            display.get("pH", "-")),
        ("Drainage",           display.get("Drainage", "-")),
        ("Soil Type",          display.get("Soil Type", "-")),
        ("Planted Area",       display.get("Area", "-")),
        ("Climate Forecast",   display.get("Climate Forecast", "-")),
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
    pdf.cell(0, 8, "3. Top 3 Recommendations")
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
        pdf.cell(90, 6, _pdf_safe(f"Expected yield: {ev:.1f} sc/ha ({delta_str2} sc/ha)"))
        pdf.ln(7)
        if mc:
            pdf.set_x(18)
            pdf.cell(0, 6, _pdf_safe(
                f"90% interval: {mc['p5']:.0f} to {mc['p95']:.0f} sc/ha  |  "
                f"Risk below reference: {mc['p_below']:.1%}"
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
    pdf.cell(0, 8, "4. How the Simulator Calculates")
    pdf.ln(12)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(40, 40, 40)
    metodologia = [
        ("Regional reference:",
         f"The model starts from {baseline:.0f} sc/ha, the historical average yield for soy "
         "in Mato Grosso (source: CONAB 2023/24)."),
        ("Field context adjustment:",
         "Region, soil type and texture, pH, drainage, area size, and climate forecast "
         "adjust the reference up or down, reflecting the true potential of your field."),
        ("Management decision evaluation:",
         "Planting window, density, disease management, cultivar, seed treatment, and "
         "planter technology are evaluated across different combinations."),
        ("Climate scenarios:",
         "The simulator considers three rainfall scenarios during the critical period (dry, normal, and wet), "
         "with probabilities based on the El Nino/La Nina forecast provided."),
        ("Risk analysis (Monte Carlo):",
         "1,000 simulations are run with stochastic input variations to estimate the "
         "expected yield interval with 90% confidence."),
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
    pdf.cell(0, 8, "5. Glossary")
    pdf.ln(10)
    glossario = [
        ("sc/ha",             "60 kg bags per hectare - the standard yield unit."),
        ("Planting window",   "Optimal sowing period for the best crop development."),
        ("TSI",               "Industrial Seed Treatment - application of fungicide, insecticide, nematicide, and inoculant before planting."),
        ("ENSO",              "El Nino-Southern Oscillation - climate phenomenon that influences rainfall in the Center-West."),
        ("R3-R6",             "Flowering to grain-filling stages - the most critical period for yield."),
        ("P5 / P95",          "5th and 95th percentiles of the results distribution - bounds of the 90% confidence interval."),
        ("Monte Carlo",       "Simulation method using thousands of scenarios with random variations to estimate the distribution of results."),
        ("Latosol",           "Clay-rich, well-structured soil common in the Cerrado - excellent internal drainage, ideal for soy."),
        ("Asian rust",        "Main fungal disease of soy in MT; requires monitoring and preventive fungicides."),
        ("EV / Bayes",        "Expected value: weighted average across climate scenarios - the main recommendation criterion."),
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
