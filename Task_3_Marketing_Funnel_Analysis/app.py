"""Marketing Funnel & Conversion Performance Analysis dashboard."""

import base64
import os
from datetime import datetime

import streamlit as st

from utils.charts import (
    campaign_comparison_chart, channel_performance_chart,
    country_revenue_chart, customer_acquisition_by_device_chart,
    customer_distribution_chart, funnel_chart, funnel_stage_bar_chart,
    heatmap_chart, lead_conversion_by_channel_chart, marketing_cost_chart,
    monthly_trend_chart, revenue_trend_chart, roi_by_campaign_chart,
    treemap_chart,
)
from utils.data_loader import filter_data, load_data
from utils.helpers import (
    build_pdf_report, format_currency, format_number, format_percent,
    to_csv_bytes, to_excel_bytes,
)
from utils.metrics import (
    calculate_kpis, campaign_performance, channel_performance, funnel_summary,
    generate_insights, generate_recommendations,
)

st.set_page_config(
    page_title="Marketing Funnel & Conversion Performance Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")


def load_css() -> None:
    """Inject the dashboard's local presentation stylesheet."""
    css_path = os.path.join(ASSETS_DIR, "style.css")
    if os.path.exists(css_path):
        with open(css_path, encoding="utf-8") as css_file:
            st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)


def logo_data_uri() -> str:
    """Return the local logo as a browser-safe data URI for the header."""
    logo_path = os.path.join(ASSETS_DIR, "logo.png")
    if not os.path.exists(logo_path):
        return ""

    with open(logo_path, "rb") as logo_file:
        encoded_logo = base64.b64encode(logo_file.read()).decode("ascii")
    return f"data:image/png;base64,{encoded_logo}"


load_css()

try:
    df_raw = load_data()
except (FileNotFoundError, ValueError) as error:
    st.error(str(error))
    st.stop()

FILTER_DEFAULTS = {
    "filter_date_range": (df_raw["Date"].min().date(), df_raw["Date"].max().date()),
    "filter_channels": [],
    "filter_campaigns": [],
    "filter_countries": [],
    "filter_devices": [],
}


def reset_filters() -> None:
    """Restore every dashboard filter to its original, unfiltered state."""
    for key, default in FILTER_DEFAULTS.items():
        st.session_state[key] = list(default) if isinstance(default, list) else default


for state_key, default_value in FILTER_DEFAULTS.items():
    if state_key not in st.session_state:
        st.session_state[state_key] = (
            list(default_value) if isinstance(default_value, list) else default_value
        )

# Premium dashboard header
refresh_timestamp = datetime.now().strftime("%d %b %Y · %I:%M %p")
logo_uri = logo_data_uri()
logo_markup = (
    f'<img class="dashboard-logo" src="{logo_uri}" alt="Dashboard logo">'
    if logo_uri
    else '<div class="dashboard-logo dashboard-logo-fallback">📊</div>'
)
st.markdown(
    f"""
    <section class="analytics-header">
        <div class="header-title-group">
            {logo_markup}
            <div class="header-copy">
                <p class="header-eyebrow">EXECUTIVE ANALYTICS DASHBOARD</p>
                <h1>📊 Marketing Funnel &amp; Conversion Performance Analysis</h1>
                <p class="header-subtitle">Marketing Performance, Funnel Analytics &amp; Conversion Intelligence</p>
            </div>
        </div>
        <div class="refresh-status">
            <span class="refresh-dot"></span>
            <div><span>Last refreshed</span><strong>{refresh_timestamp}</strong></div>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)

# Sidebar filters
with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-brand-icon">⌘</div>
            <div><span>CONTROL CENTER</span><strong>Dashboard Filters</strong></div>
        </div>
        <p class="sidebar-intro">Refine the analysis across every visual and export.</p>
        """,
        unsafe_allow_html=True,
    )
    st.button(
        "↻ Reset all filters",
        key="reset_filters_button",
        on_click=reset_filters,
        width="stretch",
        help="Restore the full date range and clear every filter selection.",
    )
    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.markdown('<p class="filter-section-label">TIME PERIOD</p>', unsafe_allow_html=True)

    min_date = df_raw["Date"].min().date()
    max_date = df_raw["Date"].max().date()
    date_range = st.date_input(
        "Date range", min_value=min_date, max_value=max_date, key="filter_date_range"
    )

    st.markdown('<p class="filter-section-label">AUDIENCE &amp; CAMPAIGN</p>', unsafe_allow_html=True)
    channels = st.multiselect(
        "Marketing channel", sorted(df_raw["Marketing Channel"].unique()), key="filter_channels"
    )
    campaigns = st.multiselect(
        "Campaign", sorted(df_raw["Campaign"].unique()), key="filter_campaigns"
    )
    countries = st.multiselect(
        "Country", sorted(df_raw["Country"].unique()), key="filter_countries"
    )
    devices = st.multiselect(
        "Device", sorted(df_raw["Device"].unique()), key="filter_devices"
    )
    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-version">MARKETING FUNNEL ANALYSIS <span>•</span> v1.0</p>', unsafe_allow_html=True)

# Normalize date_range (st.date_input can return a single date while typing).
active_date_range = date_range if isinstance(date_range, tuple) and len(date_range) == 2 else (min_date, max_date)

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

# KPI cards
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
for index, (icon, label, value) in enumerate(kpi_defs):
    with cols[index % 5]:
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-icon">{icon}</div><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div></div>',
            unsafe_allow_html=True,
        )
    if (index + 1) % 5 == 0 and index != len(kpi_defs) - 1:
        cols = st.columns(5)

# Funnel chart
st.markdown('<div class="section-title">Conversion Funnel</div>', unsafe_allow_html=True)
funnel_col1, funnel_col2 = st.columns([1.3, 1])
with funnel_col1:
    st.plotly_chart(funnel_chart(df), width="stretch")
with funnel_col2:
    st.plotly_chart(funnel_stage_bar_chart(df), width="stretch")
with st.expander("View funnel stage data table"):
    st.dataframe(funnel_summary(df), width="stretch", hide_index=True)

# Visualizations
st.markdown('<div class="section-title">Revenue &amp; Trend Analysis</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(revenue_trend_chart(df), width="stretch")
with c2:
    st.plotly_chart(monthly_trend_chart(df), width="stretch")

st.markdown('<div class="section-title">Channel &amp; Campaign Performance</div>', unsafe_allow_html=True)
c3, c4 = st.columns(2)
with c3:
    st.plotly_chart(channel_performance_chart(df), width="stretch")
with c4:
    st.plotly_chart(campaign_comparison_chart(df), width="stretch")
c5, c6 = st.columns(2)
with c5:
    st.plotly_chart(lead_conversion_by_channel_chart(df), width="stretch")
with c6:
    st.plotly_chart(roi_by_campaign_chart(df), width="stretch")

st.markdown('<div class="section-title">Audience &amp; Geography</div>', unsafe_allow_html=True)
c7, c8 = st.columns(2)
with c7:
    st.plotly_chart(customer_acquisition_by_device_chart(df), width="stretch")
with c8:
    st.plotly_chart(country_revenue_chart(df), width="stretch")
c9, c10 = st.columns(2)
with c9:
    st.plotly_chart(marketing_cost_chart(df), width="stretch")
with c10:
    st.plotly_chart(customer_distribution_chart(df), width="stretch")

st.markdown('<div class="section-title">Deep-Dive: Heatmap &amp; Treemap</div>', unsafe_allow_html=True)
c11, c12 = st.columns(2)
with c11:
    st.plotly_chart(heatmap_chart(df), width="stretch")
with c12:
    st.plotly_chart(treemap_chart(df), width="stretch")

# Insights and recommendations
st.markdown('<div class="section-title">💡 Automated Business Insights</div>', unsafe_allow_html=True)
insights = generate_insights(df)
for insight in insights:
    st.markdown(f'<div class="insight-card">{insight}</div>', unsafe_allow_html=True)

st.markdown('<div class="section-title">✅ Recommendations</div>', unsafe_allow_html=True)
recommendations = generate_recommendations(df)
for index, recommendation in enumerate(recommendations, start=1):
    st.markdown(f'<div class="recommendation-card">{index}. {recommendation}</div>', unsafe_allow_html=True)

# Data tables
st.markdown('<div class="section-title">📋 Detailed Data Tables</div>', unsafe_allow_html=True)
tab1, tab2, tab3 = st.tabs(["Channel Performance", "Campaign Performance", "Raw Filtered Data"])
with tab1:
    st.dataframe(channel_performance(df), width="stretch", hide_index=True)
with tab2:
    st.dataframe(campaign_performance(df), width="stretch", hide_index=True)
with tab3:
    st.dataframe(df, width="stretch", hide_index=True)

# Export section
st.markdown('<div class="section-title">📥 Export Data &amp; Report</div>', unsafe_allow_html=True)
exp1, exp2, exp3 = st.columns(3)
with exp1:
    st.download_button("⬇️ Download CSV", to_csv_bytes(df), "marketing_funnel_filtered.csv", "text/csv", width="stretch")
with exp2:
    st.download_button("⬇️ Download Excel", to_excel_bytes(df), "marketing_funnel_filtered.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", width="stretch")
with exp3:
    pdf_bytes = build_pdf_report(kpis, insights, recommendations)
    st.download_button("⬇️ Download PDF Report", pdf_bytes, "Marketing_Funnel_Report.pdf", "application/pdf", width="stretch")

st.markdown(
    """<div class="dashboard-footer">Marketing Funnel &amp; Conversion Performance Analysis Dashboard &middot; Built with Streamlit &amp; Plotly &middot; Data Analytics Internship Project</div>""",
    unsafe_allow_html=True,
)
