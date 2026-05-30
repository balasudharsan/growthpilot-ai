import os
from pathlib import Path

from fpdf import FPDF

from utils.config import project_path
from utils.logger import get_logger


def sanitise_for_pdf(text: str) -> str:
    if not isinstance(text, str):
        text = str(text)
    replacements = {
        '₹': 'Rs.',
        '₨': 'Rs.',
        '\u20b9': 'Rs.',
        '\u2013': '-',
        '\u2014': '-',
        '\u2018': "'",
        '\u2019': "'",
        '\u201c': '"',
        '\u201d': '"',
        '\u2022': '-',
        '\u2026': '...',
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text


logger = get_logger(__name__)


def _write_list(pdf: FPDF, title: str, items: list[str]) -> None:
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, sanitise_for_pdf(title), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    for item in items:
        pdf.multi_cell(0, 6, sanitise_for_pdf(f"- {item}"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)


def generate_pdf(report: dict) -> str:
    try:
        reports_dir = project_path(os.getenv("REPORTS_DIR", "static/reports"))
        reports_dir.mkdir(parents=True, exist_ok=True)
        file_path = reports_dir / f"{report['report_id']}.pdf"

        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, sanitise_for_pdf("GrowthPilot AI Strategy Report"), new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(
            0,
            7,
            sanitise_for_pdf(f"Business: {report['business']['business_name']}"),
            new_x="LMARGIN",
            new_y="NEXT",
        )
        pdf.multi_cell(
            0,
            7,
            sanitise_for_pdf(f"Tier: {report['classification']['tier']}"),
            new_x="LMARGIN",
            new_y="NEXT",
        )
        pdf.ln(4)

        _write_list(pdf, "Executive Summary", [report["executive_summary"]])
        for swot_key, items in report["swot"].items():
            _write_list(pdf, swot_key.title(), items)
        _write_list(pdf, "Pricing Recommendations", report["pricing_recommendations"])
        _write_list(pdf, "Marketing Plan", report["marketing_plan"])
        _write_list(pdf, "30-Day Action Plan", report["thirty_day_action_plan"])
        if report["risks"]:
            _write_list(pdf, "Risks", report["risks"])

        pdf.output(file_path)
        return str(file_path)
    except Exception:
        logger.exception("PDF generation failed")
        raise
