"""
helpers.py
----------
Formatting utilities and export helpers (CSV, Excel, PDF) used by app.py.
"""

from __future__ import annotations

import io
from datetime import datetime

import pandas as pd


def format_number(value: float, prefix: str = "", suffix: str = "") -> str:
    """Format large numbers with K / M suffixes for compact KPI cards."""
    try:
        value = float(value)
    except (TypeError, ValueError):
        return str(value)

    if abs(value) >= 1_000_000:
        formatted = f"{value / 1_000_000:.2f}M"
    elif abs(value) >= 1_000:
        formatted = f"{value / 1_000:.2f}K"
    else:
        formatted = f"{value:,.2f}" if isinstance(value, float) and not value.is_integer() else f"{value:,.0f}"

    return f"{prefix}{formatted}{suffix}"


def format_currency(value: float) -> str:
    return format_number(value, prefix="₹")


def format_percent(value: float) -> str:
    try:
        return f"{float(value):.2f}%"
    except (TypeError, ValueError):
        return str(value)


def to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Convert a dataframe to CSV bytes for st.download_button."""
    return df.to_csv(index=False).encode("utf-8")


def to_excel_bytes(df: pd.DataFrame, sheet_name: str = "Marketing Funnel Data") -> bytes:
    """Convert a dataframe to an in-memory Excel (.xlsx) file."""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    buffer.seek(0)
    return buffer.getvalue()


def build_pdf_report(kpis: dict, insights: list[str], recommendations: list[str]) -> bytes:
    """
    Build a simple, professional PDF summary report using ReportLab.
    Returns the PDF as bytes, suitable for st.download_button.
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    )

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2 * cm, bottomMargin=2 * cm,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleStyle", parent=styles["Title"], textColor=colors.HexColor("#0B3D91"),
    )
    heading_style = ParagraphStyle(
        "HeadingStyle", parent=styles["Heading2"], textColor=colors.HexColor("#0B3D91"),
        spaceBefore=14, spaceAfter=6,
    )
    body_style = styles["BodyText"]

    story = []
    story.append(Paragraph("Marketing Funnel & Conversion Performance Report", title_style))
    story.append(Paragraph(f"Generated on {datetime.now().strftime('%d %B %Y, %H:%M')}", body_style))
    story.append(Spacer(1, 0.6 * cm))

    story.append(Paragraph("Key Performance Indicators", heading_style))
    kpi_table_data = [["Metric", "Value"]] + [
        [k.replace("_", " ").title(), f"{v:,.2f}" if isinstance(v, (int, float)) else str(v)]
        for k, v in kpis.items()
    ]
    kpi_table = Table(kpi_table_data, colWidths=[8 * cm, 8 * cm])
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0B3D91")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 0.8 * cm))

    story.append(Paragraph("Business Insights", heading_style))
    for insight in insights:
        clean = insight.replace("**", "")
        story.append(Paragraph(f"• {clean}", body_style))
        story.append(Spacer(1, 0.15 * cm))

    story.append(PageBreak())
    story.append(Paragraph("Recommendations", heading_style))
    for i, rec in enumerate(recommendations, start=1):
        story.append(Paragraph(f"{i}. {rec}", body_style))
        story.append(Spacer(1, 0.15 * cm))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
