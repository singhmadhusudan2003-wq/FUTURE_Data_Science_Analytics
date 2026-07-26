"""
app.py
------
Marketing Funnel & Conversion Performance Analysis Dashboard.

A production-style Streamlit application for analyzing a marketing
funnel dataset: funnel conversion, channel/campaign performance,
revenue & ROI, and automatically generated business insights and
recommendations.

Run with:
    streamlit run app.py
"""

import os
import base64

import streamlit as st

from utils.data_loader import load_data, filter_data
from utils.metrics import (
    calculate_kpis, funnel_summary, generate_insights, generate_recommendations,
    channel_performance, campaign_performance,
)
from utils.charts import (
    funnel_chart, revenue_trend_chart, monthly_trend_chart, channel_performance_chart,
    campaign_comparison_chart, lead_conversion_by_channel_chart,
    customer_acquisition_by_device_chart, country_revenue_chart, roi_by_campaign_chart,
    marketing_cost_chart, customer_distribution_chart, heatmap_chart, treemap_chart,
    funnel_stage_bar_chart,
)
from utils.helpers import (
    format_number, format_currency, format_percent, to_csv_bytes, to_excel_bytes,
    build_pdf_report,
)

# ----------------------------------------------------------------------
# Page configuration
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Marketing Funnel & Conversion Performance Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")


def load_css():
    css_path = os.path.join(ASSETS_DIR, "style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


load_css()

# ----------------------------------------------------------------------
# Header
# ----------------------------------------------------------------------
st.title("📊 Marketing Funnel & Conversion Performance Analysis")
st.caption(
    "End-to-end analysis of funnel conversion, channel performance, revenue, "
    "and ROI — with automated business insights and recommendations."
)

# ----------------------------------------------------------------------
# Load data
# ----------------------------------------------------------------------
try:
    df_raw = load_data()
except (FileNotFoundError, ValueError) as e:
    st.error(str(e))
    st.stop()

# ----------------------------------------------------------------------
# Sidebar filters
# ----------------------------------------------------------------------
with st.sidebar:
    st.header("🔎 Filters")

    min_date, max_date = df_raw["Date"].min().date(), df_raw["Date"].max().date()
    date_range = st.date_input(
        "Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date,
    )

    channels = st.multiselect(
        "Marketing Channel", options=sorted(df_raw["Marketing Channel"].unique())
    )
    campaigns = st.multiselect(
        "Campaign", options=sorted(df_raw["Campaign"].unique())
    )
    countries = st.multiselect(
        "Country", options=sorted(df_raw["Country"].unique())
    )
    devices = st.multiselect(
        "Device", options=sorted(df_raw["Device"].unique())
    )

    st.markdown("---")
    if st.button("🔄 Reset Filters"):
        st.rerun()

    st.markdown("---")
    st.caption("Marketing Funnel Analysis · v1.0")

# Normalize date_range (st.date_input can return a single date while typing)
if isinstance(date_range, tuple) and len(date_range) == 2:
    active_date_range = date_range
else:
    active_date_range = (min_date, max_date)

df = filter_data(
    df_raw,
    date_range=active_date_range,
    channels=channels,
    campaigns=campaigns,
    countries=countries,
    devices=devices,
)

if df.empty:
    st.warning("No data matches the selected filters. Please adjust your filter selection.")
    st.stop()

# ----------------------------------------------------------------------
# KPI Cards
# ----------------------------------------------------------------------
kpis = calculate_kpis(df)

st.markdown('<div class="section-title">Key Performance Indicators</div>', unsafe_allow_html=True)

kpi_defs = [
    ("📣", "Total Impressions", format_number(kpis["total_impressions"])),
    ("🖱️", "Total Clicks", format_number(kpis["total_clicks"])),
    ("🎯", "CTR", format_percent(kpis["ctr"])),
    ("🧲", "Total Leads", format_number(kpis["total_leads"])),
    ("✅", "Qualified Leads", format_number(kpis["qualified_leads"])),
    ("🛒", "Customers", format_number(kpis["customers"])),
    ("💰", "Revenue", format_currency(kpis["revenue"])),
    ("💸", "Marketing Cost", format_currency(kpis["cost"])),
    ("📈", "ROI", format_percent(kpis["roi"])),
    ("🔁", "Overall Conversion Rate", format_percent(kpis["overall_conversion_rate"])),
]

cols = st.columns(5)
for i, (icon, label, value) in enumerate(kpi_defs):
    with cols[i % 5]:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-icon">{icon}</div>
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    if (i + 1) % 5 == 0 and i != len(kpi_defs) - 1:
        cols = st.columns(5)

# ----------------------------------------------------------------------
# Funnel Chart
# ----------------------------------------------------------------------
st.markdown('<div class="section-title">Conversion Funnel</div>', unsafe_allow_html=True)
funnel_col1, funnel_col2 = st.columns([1.3, 1])
with funnel_col1:
    st.plotly_chart(funnel_chart(df), width='stretch')
with funnel_col2:
    st.plotly_chart(funnel_stage_bar_chart(df), width='stretch')

with st.expander("View funnel stage data table"):
    st.dataframe(funnel_summary(df), width='stretch', hide_index=True)

# ----------------------------------------------------------------------
# Visualizations
# ----------------------------------------------------------------------
st.markdown('<div class="section-title">Revenue & Trend Analysis</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(revenue_trend_chart(df), width='stretch')
with c2:
    st.plotly_chart(monthly_trend_chart(df), width='stretch')

st.markdown('<div class="section-title">Channel & Campaign Performance</div>', unsafe_allow_html=True)
c3, c4 = st.columns(2)
with c3:
    st.plotly_chart(channel_performance_chart(df), width='stretch')
with c4:
    st.plotly_chart(campaign_comparison_chart(df), width='stretch')

c5, c6 = st.columns(2)
with c5:
    st.plotly_chart(lead_conversion_by_channel_chart(df), width='stretch')
with c6:
    st.plotly_chart(roi_by_campaign_chart(df), width='stretch')

st.markdown('<div class="section-title">Audience & Geography</div>', unsafe_allow_html=True)
c7, c8 = st.columns(2)
with c7:
    st.plotly_chart(customer_acquisition_by_device_chart(df), width='stretch')
with c8:
    st.plotly_chart(country_revenue_chart(df), width='stretch')

c9, c10 = st.columns(2)
with c9:
    st.plotly_chart(marketing_cost_chart(df), width='stretch')
with c10:
    st.plotly_chart(customer_distribution_chart(df), width='stretch')

st.markdown('<div class="section-title">Deep-Dive: Heatmap & Treemap</div>', unsafe_allow_html=True)
c11, c12 = st.columns(2)
with c11:
    st.plotly_chart(heatmap_chart(df), width='stretch')
with c12:
    st.plotly_chart(treemap_chart(df), width='stretch')

# ----------------------------------------------------------------------
# Insights & Recommendations
# ----------------------------------------------------------------------
st.markdown('<div class="section-title">💡 Automated Business Insights</div>', unsafe_allow_html=True)
insights = generate_insights(df)
for insight in insights:
    st.markdown(f'<div class="insight-card">{insight}</div>', unsafe_allow_html=True)

st.markdown('<div class="section-title">✅ Recommendations</div>', unsafe_allow_html=True)
recommendations = generate_recommendations(df)
for i, rec in enumerate(recommendations, start=1):
    st.markdown(f'<div class="recommendation-card">{i}. {rec}</div>', unsafe_allow_html=True)

# ----------------------------------------------------------------------
# Data tables
# ----------------------------------------------------------------------
st.markdown('<div class="section-title">📋 Detailed Data Tables</div>', unsafe_allow_html=True)
tab1, tab2, tab3 = st.tabs(["Channel Performance", "Campaign Performance", "Raw Filtered Data"])
with tab1:
    st.dataframe(channel_performance(df), width='stretch', hide_index=True)
with tab2:
    st.dataframe(campaign_performance(df), width='stretch', hide_index=True)
with tab3:
    st.dataframe(df, width='stretch', hide_index=True)

# ----------------------------------------------------------------------
# Export section
# ----------------------------------------------------------------------
st.markdown('<div class="section-title">📥 Export Data & Report</div>', unsafe_allow_html=True)
exp1, exp2, exp3 = st.columns(3)

with exp1:
    st.download_button(
        label="⬇️ Download CSV",
        data=to_csv_bytes(df),
        file_name="marketing_funnel_filtered.csv",
        mime="text/csv",
        width='stretch',
    )

with exp2:
    st.download_button(
        label="⬇️ Download Excel",
        data=to_excel_bytes(df),
        file_name="marketing_funnel_filtered.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        width='stretch',
    )

with exp3:
    pdf_bytes = build_pdf_report(kpis, insights, recommendations)
    st.download_button(
        label="⬇️ Download PDF Report",
        data=pdf_bytes,
        file_name="Marketing_Funnel_Report.pdf",
        mime="application/pdf",
        width='stretch',
    )

# ----------------------------------------------------------------------
# Footer
# ----------------------------------------------------------------------
st.markdown(
    """
    <div class="dashboard-footer">
        Marketing Funnel & Conversion Performance Analysis Dashboard &middot;
        Built with Streamlit &amp; Plotly &middot; Data Analytics Internship Project
    </div>
    """,
    unsafe_allow_html=True,
)
