"""
charts.py
---------
All Plotly chart-building functions for the Streamlit dashboard.
Each function accepts a (filtered) dataframe and returns a
plotly.graph_objects.Figure ready to be rendered with st.plotly_chart.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.metrics import FUNNEL_STAGES, funnel_summary, channel_performance, campaign_performance

# Shared dark-theme template
TEMPLATE = "plotly_dark"
COLOR_SEQUENCE = px.colors.qualitative.Vivid


def funnel_chart(df: pd.DataFrame) -> go.Figure:
    summary = funnel_summary(df)
    fig = go.Figure(go.Funnel(
        y=summary["Stage"],
        x=summary["Count"],
        textinfo="value+percent initial+percent previous",
        marker={"color": COLOR_SEQUENCE[: len(summary)]},
    ))
    fig.update_layout(title="Marketing Funnel: Impressions → Customers", template=TEMPLATE)
    return fig


def revenue_trend_chart(df: pd.DataFrame) -> go.Figure:
    trend = df.groupby(df["Date"].dt.to_period("D"))["Revenue"].sum().reset_index()
    trend["Date"] = trend["Date"].astype(str)
    fig = px.line(
        trend, x="Date", y="Revenue", title="Revenue Trend Over Time",
        template=TEMPLATE, markers=False,
    )
    fig.update_traces(line_color="#00E5A0")
    return fig


def monthly_trend_chart(df: pd.DataFrame) -> go.Figure:
    monthly = df.groupby("Month").agg(
        Revenue=("Revenue", "sum"), Cost=("Cost", "sum"), Customers=("Customers", "sum")
    ).reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(x=monthly["Month"], y=monthly["Revenue"], name="Revenue", marker_color="#00E5A0"))
    fig.add_trace(go.Bar(x=monthly["Month"], y=monthly["Cost"], name="Cost", marker_color="#FF5C5C"))
    fig.add_trace(go.Scatter(
        x=monthly["Month"], y=monthly["Customers"], name="Customers",
        yaxis="y2", mode="lines+markers", line=dict(color="#FFD166", width=3),
    ))
    fig.update_layout(
        title="Monthly Revenue, Cost & Customer Trend", template=TEMPLATE, barmode="group",
        yaxis=dict(title="Revenue / Cost"),
        yaxis2=dict(title="Customers", overlaying="y", side="right"),
    )
    return fig


def channel_performance_chart(df: pd.DataFrame) -> go.Figure:
    ch = channel_performance(df)
    fig = px.bar(
        ch, x="Marketing Channel", y="Revenue", color="Marketing Channel",
        title="Channel Performance by Revenue", template=TEMPLATE,
        color_discrete_sequence=COLOR_SEQUENCE,
    )
    fig.update_layout(showlegend=False)
    return fig


def campaign_comparison_chart(df: pd.DataFrame) -> go.Figure:
    camp = campaign_performance(df).head(10)
    fig = px.bar(
        camp, x="ROI (%)", y="Campaign", orientation="h",
        title="Top 10 Campaigns by ROI", template=TEMPLATE,
        color="ROI (%)", color_continuous_scale="Tealgrn",
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    return fig


def lead_conversion_by_channel_chart(df: pd.DataFrame) -> go.Figure:
    ch = channel_performance(df)
    fig = px.bar(
        ch, x="Marketing Channel", y="Customer Conversion (%)", color="Marketing Channel",
        title="Lead-to-Customer Conversion by Channel", template=TEMPLATE,
        color_discrete_sequence=COLOR_SEQUENCE,
    )
    fig.update_layout(showlegend=False)
    return fig


def customer_acquisition_by_device_chart(df: pd.DataFrame) -> go.Figure:
    device_df = df.groupby("Device")["Customers"].sum().reset_index()
    fig = px.pie(
        device_df, names="Device", values="Customers", hole=0.45,
        title="Customer Acquisition by Device", template=TEMPLATE,
        color_discrete_sequence=COLOR_SEQUENCE,
    )
    return fig


def country_revenue_chart(df: pd.DataFrame) -> go.Figure:
    country_df = df.groupby("Country")["Revenue"].sum().reset_index().sort_values("Revenue", ascending=False)
    fig = px.bar(
        country_df, x="Country", y="Revenue", title="Country-wise Revenue",
        template=TEMPLATE, color="Revenue", color_continuous_scale="Blues",
    )
    return fig


def roi_by_campaign_chart(df: pd.DataFrame) -> go.Figure:
    camp = campaign_performance(df)
    fig = px.scatter(
        camp, x="Cost", y="ROI (%)", size="Revenue", color="Campaign",
        title="ROI vs Cost by Campaign (bubble size = Revenue)", template=TEMPLATE,
        color_discrete_sequence=COLOR_SEQUENCE,
    )
    fig.update_layout(showlegend=False)
    return fig


def marketing_cost_chart(df: pd.DataFrame) -> go.Figure:
    ch = channel_performance(df).sort_values("Cost", ascending=False)
    fig = px.bar(
        ch, x="Marketing Channel", y="Cost", title="Marketing Cost by Channel",
        template=TEMPLATE, color="Cost", color_continuous_scale="OrRd",
    )
    return fig


def customer_distribution_chart(df: pd.DataFrame) -> go.Figure:
    dist = df.groupby("Age Group")["Customers"].sum().reset_index()
    fig = px.bar(
        dist, x="Age Group", y="Customers", title="Customer Distribution by Age Group",
        template=TEMPLATE, color="Customers", color_continuous_scale="Purples",
    )
    return fig


def heatmap_chart(df: pd.DataFrame) -> go.Figure:
    pivot = df.pivot_table(
        index="Marketing Channel", columns="Device", values="Conversion Rate", aggfunc="mean"
    ).fillna(0)
    fig = px.imshow(
        pivot, text_auto=".2f", aspect="auto", template=TEMPLATE,
        title="Conversion Rate Heatmap: Channel × Device", color_continuous_scale="Viridis",
    )
    return fig


def treemap_chart(df: pd.DataFrame) -> go.Figure:
    treemap_df = df.groupby(["Marketing Channel", "Campaign"])["Revenue"].sum().reset_index()
    fig = px.treemap(
        treemap_df, path=["Marketing Channel", "Campaign"], values="Revenue",
        title="Revenue Treemap: Channel → Campaign", template=TEMPLATE,
        color="Revenue", color_continuous_scale="Tealgrn",
    )
    return fig


def funnel_stage_bar_chart(df: pd.DataFrame) -> go.Figure:
    """Bar version of the funnel for a compact drop-off view."""
    summary = funnel_summary(df)
    fig = px.bar(
        summary, x="Stage", y="Count", text="Drop-off (%)", template=TEMPLATE,
        title="Funnel Stage Volumes & Drop-off", color="Stage",
        color_discrete_sequence=COLOR_SEQUENCE,
    )
    fig.update_traces(texttemplate="Drop: %{text}%", textposition="outside")
    fig.update_layout(showlegend=False)
    return fig
