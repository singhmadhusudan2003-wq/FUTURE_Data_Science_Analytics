"""
generate_report.py
-------------------
Builds the client-ready PDF report (reports/Business_Sales_Report.pdf)
for the Business Sales Performance Analytics project using ReportLab.

Author: Future Interns - Data Science & Analytics Track
"""

import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image, ListFlowable, ListItem, PageBreak, Paragraph, SimpleDocTemplate,
    Spacer, Table, TableStyle,
)

from data_cleaning import clean_pipeline
from analysis import calculate_kpis, region_summary, category_summary, top_products, segment_summary

PRIMARY = colors.HexColor("#2563EB")
DARK = colors.HexColor("#1E293B")
MUTED = colors.HexColor("#64748B")
LIGHT_BG = colors.HexColor("#F1F5F9")

IMG_DIR = Path("../images")


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="CoverTitle", fontSize=28, leading=34, alignment=TA_CENTER,
                               textColor=DARK, fontName="Helvetica-Bold", spaceAfter=10))
    styles.add(ParagraphStyle(name="CoverSubtitle", fontSize=14, leading=18, alignment=TA_CENTER,
                               textColor=PRIMARY, fontName="Helvetica-Bold", spaceAfter=6))
    styles.add(ParagraphStyle(name="CoverMeta", fontSize=10.5, leading=15, alignment=TA_CENTER,
                               textColor=MUTED, fontName="Helvetica"))
    styles.add(ParagraphStyle(name="H1", fontSize=17, leading=21, spaceBefore=16, spaceAfter=10,
                               textColor=DARK, fontName="Helvetica-Bold"))
    styles.add(ParagraphStyle(name="H2", fontSize=12.5, leading=16, spaceBefore=10, spaceAfter=6,
                               textColor=PRIMARY, fontName="Helvetica-Bold"))
    styles.add(ParagraphStyle(name="BodyText2", fontSize=10, leading=14.5, spaceAfter=8,
                               textColor=colors.HexColor("#1F2937"), alignment=TA_LEFT))
    styles.add(ParagraphStyle(name="Caption", fontSize=8.5, leading=11, textColor=MUTED,
                               alignment=TA_CENTER, spaceAfter=14))
    styles.add(ParagraphStyle(name="KPILabel", fontSize=8.5, textColor=MUTED, fontName="Helvetica"))
    styles.add(ParagraphStyle(name="KPIValue", fontSize=13, textColor=DARK, fontName="Helvetica-Bold"))
    return styles


def kpi_table(kpis, styles):
    def cell(label, value):
        return [Paragraph(label, styles["KPILabel"]), Paragraph(str(value), styles["KPIValue"])]

    data = [
        cell("Total Revenue", f"${kpis['Total Revenue']:,.0f}") + cell("Total Profit", f"${kpis['Total Profit']:,.0f}"),
        cell("Total Orders", f"{kpis['Total Orders']:,}") + cell("Avg Order Value", f"${kpis['Average Order Value']:,.0f}"),
        cell("Profit Margin", f"{kpis['Profit Margin (%)']}%") + cell("Best Region", kpis["Best Region"]),
        cell("Best Category", kpis["Best Category"]) + cell("Top Product", kpis["Best Product"]),
    ]
    t = Table(data, colWidths=[1.6 * inch, 1.9 * inch, 1.6 * inch, 1.9 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BG),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.white),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
    ]))
    return t


def df_to_table(df, styles, col_widths=None, first_col_label="Group"):
    df2 = df.reset_index()
    header = [str(c) for c in df2.columns]
    data = [header] + df2.astype(str).values.tolist()
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
    ]))
    return t


def chart_image(name, width=6.4 * inch):
    path = IMG_DIR / name
    img = Image(str(path), width=width, height=width * 0.56)
    return img


def build_report(df, output_path="../reports/Business_Sales_Report.pdf"):
    styles = build_styles()
    kpis = calculate_kpis(df)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                             topMargin=0.65 * inch, bottomMargin=0.65 * inch,
                             leftMargin=0.7 * inch, rightMargin=0.7 * inch,
                             title="Business Sales Performance Report")
    story = []

    # ---------- COVER PAGE ----------
    story.append(Spacer(1, 1.6 * inch))
    story.append(Paragraph("Business Sales Performance Analytics", styles["CoverTitle"]))
    story.append(Paragraph("Client-Ready Analysis Report", styles["CoverSubtitle"]))
    story.append(Spacer(1, 0.4 * inch))
    story.append(Paragraph("Prepared for: Future Interns — Data Science &amp; Analytics Internship", styles["CoverMeta"]))
    story.append(Paragraph("Project Code: FUTURE_DS_01", styles["CoverMeta"]))
    story.append(Paragraph("Dataset Period: 2022 – 2025 &nbsp;|&nbsp; Records Analyzed: "
                            f"{len(df):,}", styles["CoverMeta"]))
    story.append(Spacer(1, 1.8 * inch))
    story.append(Paragraph("Prepared using Python, Pandas, Matplotlib, Seaborn &amp; Plotly",
                            styles["CoverMeta"]))
    story.append(PageBreak())

    # ---------- EXECUTIVE SUMMARY ----------
    story.append(Paragraph("Executive Summary", styles["H1"]))
    story.append(Paragraph(
        f"This report analyzes {len(df):,} cleaned sales transactions to evaluate overall business "
        f"performance, uncover revenue and profit drivers, and translate the findings into actionable "
        f"recommendations. Over the analyzed period, the business generated <b>${kpis['Total Revenue']:,.0f}</b> "
        f"in total revenue and <b>${kpis['Total Profit']:,.0f}</b> in profit, representing an overall profit "
        f"margin of <b>{kpis['Profit Margin (%)']}%</b>. The <b>{kpis['Best Region']}</b> region and the "
        f"<b>{kpis['Best Category']}</b> category are the strongest performers, while the "
        f"<b>{kpis['Worst Region']}</b> region and <b>{kpis['Worst Category']}</b> category present the "
        f"clearest opportunities for improvement.", styles["BodyText2"]))
    story.append(Spacer(1, 8))
    story.append(kpi_table(kpis, styles))
    story.append(Spacer(1, 14))

    # ---------- BUSINESS OBJECTIVE ----------
    story.append(Paragraph("Business Objective", styles["H1"]))
    story.append(Paragraph(
        "Analyze business sales data to identify revenue trends, top-selling products, high-value "
        "categories, and regional performance, and deliver a client-ready dashboard and report with clear "
        "insights and actionable recommendations for improving revenue growth and profit margin.",
        styles["BodyText2"]))

    # ---------- DATASET OVERVIEW ----------
    story.append(Paragraph("Dataset Overview", styles["H1"]))
    story.append(Paragraph(
        "The dataset simulates a multi-year retail/B2B sales operation across the United States, covering "
        "Order ID, Order Date, Ship Date, Customer, Segment, Region/State/City, Product/Category/Sub-Category, "
        "Sales, Quantity, Discount, Profit, Shipping Mode, Payment Method, and Sales Representative fields. "
        f"After cleaning, the working dataset contains <b>{len(df):,}</b> transaction-level rows spanning "
        f"<b>{df['Order Year'].min()}–{df['Order Year'].max()}</b>.", styles["BodyText2"]))

    # ---------- DATA CLEANING ----------
    story.append(Paragraph("Data Cleaning &amp; Methodology", styles["H1"]))
    story.append(ListFlowable([
        ListItem(Paragraph("<b>Missing values:</b> Sales imputed using Category/Sub-Category median; "
                            "Discount defaulted to 0; missing Customer Name labeled 'Unknown Customer'; "
                            "rows with missing Ship Date removed.", styles["BodyText2"])),
        ListItem(Paragraph("<b>Duplicates:</b> Duplicate Order ID + Product ID combinations were identified "
                            "and removed to prevent double-counting revenue.", styles["BodyText2"])),
        ListItem(Paragraph("<b>Data types:</b> Dates converted to datetime, monetary fields to numeric, and "
                            "categorical fields (Region, Category, Segment, etc.) converted to category type "
                            "for memory efficiency and consistent grouping.", styles["BodyText2"])),
        ListItem(Paragraph("<b>Outlier treatment:</b> The IQR method was used to flag and cap (winsorize) "
                            "extreme Sales values, preserving sample size while limiting the influence of "
                            "data-entry-scale anomalies.", styles["BodyText2"])),
        ListItem(Paragraph("<b>Feature engineering:</b> Order Year/Month/Quarter, Shipping Days, Profit "
                            "Margin (%), and Average Order Value were derived to support trend and "
                            "profitability analysis.", styles["BodyText2"])),
    ], bulletType="bullet"))

    story.append(PageBreak())

    # ---------- KPI DETAIL ----------
    story.append(Paragraph("Key Performance Indicators", styles["H1"]))
    kpi_rows = [
        ["KPI", "Value"],
        ["Total Revenue", f"${kpis['Total Revenue']:,.0f}"],
        ["Total Profit", f"${kpis['Total Profit']:,.0f}"],
        ["Total Orders", f"{kpis['Total Orders']:,}"],
        ["Average Order Value", f"${kpis['Average Order Value']:,.0f}"],
        ["Profit Margin", f"{kpis['Profit Margin (%)']}%"],
        ["Best Region", f"{kpis['Best Region']} (${kpis['Best Region Sales']:,.0f})"],
        ["Worst Region", f"{kpis['Worst Region']} (${kpis['Worst Region Sales']:,.0f})"],
        ["Best Category", f"{kpis['Best Category']} (${kpis['Best Category Sales']:,.0f})"],
        ["Worst Category", f"{kpis['Worst Category']} (${kpis['Worst Category Sales']:,.0f})"],
        ["Most Profitable Category", kpis["Most Profitable Category"]],
        ["Best Product", f"{kpis['Best Product']} (${kpis['Best Product Sales']:,.0f})"],
        ["Top Customer", f"{kpis['Top Customer']} (${kpis['Top Customer Sales']:,.0f})"],
        ["Highest Sales Month", f"{kpis['Highest Sales Month']} (${kpis['Highest Sales Month Value']:,.0f})"],
        ["Highest Profit Month", f"{kpis['Highest Profit Month']} (${kpis['Highest Profit Month Value']:,.0f})"],
        ["Revenue Growth (first→last year)", f"{kpis['Revenue Growth (%) (First to Last Year)']}%"],
    ]
    t = Table(kpi_rows, colWidths=[2.8 * inch, 3.6 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(PageBreak())

    # ---------- CHARTS & INSIGHTS ----------
    story.append(Paragraph("Visual Analysis &amp; Insights", styles["H1"]))

    chart_sections = [
        ("revenue_trend.png", "Monthly Revenue Trend",
         "Revenue fluctuates month to month with recurring peaks, reflecting seasonal buying patterns."),
        ("profit_trend.png", "Monthly Profit Trend",
         "Profit tracks revenue closely but dips in months with heavy discounting, confirming discount "
         "policy as a key margin lever."),
        ("sales_by_category.png", "Sales by Category",
         "Technology leads total revenue by a wide margin, followed by Furniture and Office Supplies."),
        ("profit_by_category.png", "Profit by Category",
         "Technology is also the strongest profit contributor; Office Supplies contributes the least in "
         "absolute terms due to low unit prices."),
        ("sales_by_region.png", "Sales by Region",
         "The East region generates the highest revenue; the South region trails all other regions."),
        ("profit_by_region.png", "Profit by Region",
         "Regional profit ranking mirrors the sales ranking, reinforcing the South as a growth priority."),
        ("top_products.png", "Top 10 Products by Sales",
         "A small number of high-ticket Technology products drive a disproportionate share of revenue."),
        ("top_customers.png", "Top 10 Customers by Sales",
         "Top customers are spread across multiple segments, indicating healthy revenue diversification."),
        ("discount_vs_profit.png", "Discount vs Profit",
         "Profit deteriorates sharply beyond ~20% discount, with many high-discount orders becoming "
         "loss-making."),
        ("correlation_heatmap.png", "Correlation Heatmap",
         "Discount is negatively correlated with Profit and Profit Margin; Shipping Days shows negligible "
         "correlation with financial outcomes."),
        ("sales_distribution.png", "Sales Distribution",
         "Sales values are right-skewed, with a long tail of high-value Technology transactions."),
        ("profit_distribution.png", "Profit Distribution",
         "Profit is centered near a modest positive value with a visible left tail of loss-making orders."),
        ("quantity_analysis.png", "Quantity Analysis by Category",
         "Office Supplies moves the highest unit volume despite generating the least revenue."),
        ("state_wise_sales.png", "Top 15 States by Sales",
         "Sales concentrate in a handful of large states, highlighting both established markets and "
         "white-space opportunities."),
        ("customer_segment_analysis.png", "Customer Segment Analysis",
         "The Consumer segment contributes the largest revenue share, followed by Corporate and Home Office."),
        ("year_wise_growth.png", "Year-wise Growth",
         "Year-over-year growth is uneven, with at least one year showing a revenue decline that merits "
         "root-cause investigation."),
    ]

    for i, (fname, title, insight) in enumerate(chart_sections):
        story.append(Paragraph(title, styles["H2"]))
        story.append(chart_image(fname))
        story.append(Paragraph(f"<b>Insight:</b> {insight}", styles["Caption"]))
        if i % 2 == 1:
            story.append(PageBreak())

    story.append(PageBreak())

    # ---------- SUMMARY TABLES ----------
    story.append(Paragraph("Regional Performance Summary", styles["H1"]))
    story.append(df_to_table(region_summary(df), styles, col_widths=[1.3*inch, 1.5*inch, 1.5*inch, 1*inch, 1.1*inch]))
    story.append(Spacer(1, 14))

    story.append(Paragraph("Customer Segment Summary", styles["H1"]))
    story.append(df_to_table(segment_summary(df), styles, col_widths=[1.6*inch, 1.8*inch, 1.8*inch, 1.2*inch]))
    story.append(PageBreak())

    story.append(Paragraph("Top 10 Products", styles["H1"]))
    story.append(df_to_table(top_products(df, n=10), styles,
                              col_widths=[2.6*inch, 1.4*inch, 1.4*inch, 1*inch]))
    story.append(PageBreak())

    # ---------- INSIGHTS ----------
    story.append(Paragraph("Consolidated Business Insights", styles["H1"]))
    insights = [
        "Technology drives the business, led by a small number of high-ticket products.",
        "Discounting above ~20% erodes profitability and is the largest controllable margin lever.",
        "The South region consistently underperforms the East, West, and Central regions.",
        "Revenue is right-skewed — a small number of large orders drive a disproportionate share of total sales.",
        "Office Supplies is a high-volume, low-value category, likely serving a retention/relationship role.",
        "The Consumer segment leads in volume; Corporate leads in average order value.",
        "Shipping speed shows negligible correlation with profit, so logistics is not the current constraint.",
        "Year-over-year growth is uneven, with at least one year showing a decline that needs investigation.",
        "Revenue is not dangerously concentrated in a single top customer.",
        "Sales are geographically concentrated in a handful of large states, leaving mid-tier states as white space.",
    ]
    story.append(ListFlowable(
        [ListItem(Paragraph(t, styles["BodyText2"])) for t in insights], bulletType="1"
    ))

    story.append(PageBreak())

    # ---------- RECOMMENDATIONS ----------
    story.append(Paragraph("Actionable Recommendations", styles["H1"]))
    recs = [
        "Cap discounts at 20% for Technology and Furniture orders unless manager-approved.",
        "Introduce margin-protected discount tiers (0–10% self-serve, 10–20% approval, 20%+ escalation).",
        "Launch a regional growth campaign in the South, mirroring East-region tactics.",
        "Prioritize inventory and marketing spend on top-selling Technology products; consider bundling.",
        "Reposition Office Supplies as a loyalty/retention category to drive repeat purchase frequency.",
        "Build a dedicated Corporate account-management motion given its higher average order value.",
        "Investigate the year with declining revenue to isolate pricing, mix, or market causes.",
        "Expand marketing investment in mid-tier states showing moderate but growing sales.",
        "Set up automated monthly profit-trend monitoring to catch loss-trending months early.",
        "Review pricing on the lowest-margin sub-categories identified in the category summary.",
        "Codify and share top sales representatives' playbooks across the team.",
        "Introduce a loyalty program for high-value Consumer-segment customers.",
        "Bundle slow-moving sub-categories with top sellers to increase sell-through without heavy discounting.",
        "Test faster shipping options in lower-sales regions to rule out logistics as a hidden barrier.",
        "Establish a quarterly business review (QBR) cadence using this report's KPIs to track initiative impact.",
    ]
    story.append(ListFlowable(
        [ListItem(Paragraph(t, styles["BodyText2"])) for t in recs], bulletType="1"
    ))

    story.append(PageBreak())

    # ---------- CONCLUSION ----------
    story.append(Paragraph("Conclusion", styles["H1"]))
    story.append(Paragraph(
        "The business maintains a fundamentally healthy revenue base anchored by the Technology category, "
        "with the single largest controllable opportunity being tighter discount discipline. Regional "
        "performance also shows a clear and addressable gap, with the South region trailing the rest of the "
        "business. Acting on the recommendations in this report — particularly discount governance and "
        "regional investment — offers a realistic, low-risk path to improving both revenue growth and profit "
        "margin without requiring new product lines.", styles["BodyText2"]))

    story.append(Paragraph("Future Improvements", styles["H1"]))
    story.append(ListFlowable([
        ListItem(Paragraph("Incorporate marketing spend and customer acquisition cost data to compute true ROI "
                            "by channel and region.", styles["BodyText2"])),
        ListItem(Paragraph("Build a cohort-based customer lifetime value (CLV) model to prioritize retention "
                            "investment.", styles["BodyText2"])),
        ListItem(Paragraph("Add a forecasting layer (e.g., Prophet or ARIMA) to project next-quarter revenue "
                            "and proactively flag risk months.", styles["BodyText2"])),
        ListItem(Paragraph("Automate this report and the interactive dashboard to refresh on a scheduled basis "
                            "as new transaction data arrives.", styles["BodyText2"])),
    ], bulletType="bullet"))

    story.append(Spacer(1, 20))
    story.append(Paragraph("Future Interns — Data Science &amp; Analytics Internship | FUTURE_DS_01",
                            styles["Caption"]))

    doc.build(story)
    print(f"Report saved to {output_path}")


if __name__ == "__main__":
    data = clean_pipeline("../data/sales_data.csv")
    build_report(data, "../reports/Business_Sales_Report.pdf")
