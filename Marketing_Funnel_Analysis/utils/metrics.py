"""
metrics.py
----------
KPI calculations, funnel-stage aggregation, and automated business
insight / recommendation generation for the marketing funnel dashboard.
"""

from __future__ import annotations

import pandas as pd


FUNNEL_STAGES = [
    "Impressions", "Clicks", "Landing Page Visits", "Leads",
    "Qualified Leads", "Customers",
]


def calculate_kpis(df: pd.DataFrame) -> dict:
    """
    Compute headline KPIs for the currently filtered dataframe.

    Returns
    -------
    dict
        Dictionary of KPI name -> value.
    """
    if df.empty:
        return {k: 0 for k in [
            "total_impressions", "total_clicks", "ctr", "total_leads",
            "qualified_leads", "customers", "revenue", "cost", "roi",
            "overall_conversion_rate", "cost_per_lead", "avg_order_value",
        ]}

    total_impressions = df["Impressions"].sum()
    total_clicks = df["Clicks"].sum()
    total_leads = df["Leads"].sum()
    qualified_leads = df["Qualified Leads"].sum()
    customers = df["Customers"].sum()
    revenue = df["Revenue"].sum()
    cost = df["Cost"].sum()

    ctr = (total_clicks / total_impressions * 100) if total_impressions else 0
    roi = ((revenue - cost) / cost * 100) if cost else 0
    overall_conversion_rate = (customers / total_impressions * 100) if total_impressions else 0
    cost_per_lead = (cost / total_leads) if total_leads else 0
    avg_order_value = (revenue / customers) if customers else 0

    return {
        "total_impressions": total_impressions,
        "total_clicks": total_clicks,
        "ctr": round(ctr, 2),
        "total_leads": total_leads,
        "qualified_leads": qualified_leads,
        "customers": customers,
        "revenue": revenue,
        "cost": cost,
        "roi": round(roi, 2),
        "overall_conversion_rate": round(overall_conversion_rate, 3),
        "cost_per_lead": round(cost_per_lead, 2),
        "avg_order_value": round(avg_order_value, 2),
    }


def funnel_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate funnel stage totals and stage-over-stage conversion %,
    used to render the funnel chart and drop-off analysis.
    """
    totals = [df[stage].sum() for stage in FUNNEL_STAGES]
    summary = pd.DataFrame({"Stage": FUNNEL_STAGES, "Count": totals})

    summary["Conversion vs Previous (%)"] = (
        summary["Count"].pct_change().fillna(0) * 100 + 100
    ).round(2)
    summary.loc[0, "Conversion vs Previous (%)"] = 100.0

    summary["Conversion vs Top (%)"] = (
        summary["Count"] / summary["Count"].iloc[0] * 100
    ).round(2)

    summary["Drop-off (%)"] = (100 - summary["Conversion vs Previous (%)"]).round(2)
    summary.loc[0, "Drop-off (%)"] = 0.0

    return summary


def channel_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate KPIs grouped by Marketing Channel."""
    grouped = df.groupby("Marketing Channel").agg(
        Impressions=("Impressions", "sum"),
        Clicks=("Clicks", "sum"),
        Leads=("Leads", "sum"),
        Qualified_Leads=("Qualified Leads", "sum"),
        Customers=("Customers", "sum"),
        Revenue=("Revenue", "sum"),
        Cost=("Cost", "sum"),
    ).reset_index()

    grouped["CTR (%)"] = (grouped["Clicks"] / grouped["Impressions"] * 100).round(2)
    grouped["Lead Conversion (%)"] = (
        grouped["Leads"] / grouped["Clicks"] * 100
    ).round(2)
    grouped["Customer Conversion (%)"] = (
        grouped["Customers"] / grouped["Leads"].replace(0, pd.NA) * 100
    ).fillna(0).round(2)
    grouped["ROI (%)"] = (
        (grouped["Revenue"] - grouped["Cost"]) / grouped["Cost"].replace(0, pd.NA) * 100
    ).fillna(0).round(2)

    return grouped.sort_values("Revenue", ascending=False)


def campaign_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate KPIs grouped by Campaign."""
    grouped = df.groupby("Campaign").agg(
        Impressions=("Impressions", "sum"),
        Clicks=("Clicks", "sum"),
        Leads=("Leads", "sum"),
        Customers=("Customers", "sum"),
        Revenue=("Revenue", "sum"),
        Cost=("Cost", "sum"),
    ).reset_index()

    grouped["ROI (%)"] = (
        (grouped["Revenue"] - grouped["Cost"]) / grouped["Cost"].replace(0, pd.NA) * 100
    ).fillna(0).round(2)
    grouped["Conversion Rate (%)"] = (
        grouped["Customers"] / grouped["Impressions"] * 100
    ).round(3)

    return grouped.sort_values("Revenue", ascending=False)


def generate_insights(df: pd.DataFrame) -> list[str]:
    """
    Derive plain-English business insights from the filtered dataset.
    Returns a list of insight strings.
    """
    if df.empty:
        return ["No data available for the selected filters."]

    insights = []

    ch_perf = channel_performance(df)
    if not ch_perf.empty:
        best_channel = ch_perf.sort_values("Customer Conversion (%)", ascending=False).iloc[0]
        worst_channel = ch_perf.sort_values("Customer Conversion (%)", ascending=True).iloc[0]
        best_roi_channel = ch_perf.sort_values("ROI (%)", ascending=False).iloc[0]

        insights.append(
            f"**Highest converting channel:** {best_channel['Marketing Channel']} "
            f"with a {best_channel['Customer Conversion (%)']:.2f}% lead-to-customer rate."
        )
        insights.append(
            f"**Lowest performing channel:** {worst_channel['Marketing Channel']} "
            f"converts only {worst_channel['Customer Conversion (%)']:.2f}% of leads into customers."
        )
        insights.append(
            f"**Highest ROI channel:** {best_roi_channel['Marketing Channel']} delivers "
            f"{best_roi_channel['ROI (%)']:.1f}% return on ad spend."
        )

    funnel = funnel_summary(df)
    if not funnel.empty:
        max_dropoff_row = funnel.iloc[1:].sort_values("Drop-off (%)", ascending=False).iloc[0]
        insights.append(
            f"**Largest funnel drop-off:** {max_dropoff_row['Drop-off (%)']:.1f}% of users are "
            f"lost at the **{max_dropoff_row['Stage']}** stage — the biggest leak in the funnel."
        )

    camp_perf = campaign_performance(df)
    if not camp_perf.empty:
        best_campaign = camp_perf.sort_values("ROI (%)", ascending=False).iloc[0]
        worst_campaign = camp_perf.sort_values("ROI (%)", ascending=True).iloc[0]
        insights.append(
            f"**Highest ROI campaign:** '{best_campaign['Campaign']}' with "
            f"{best_campaign['ROI (%)']:.1f}% ROI."
        )
        insights.append(
            f"**Worst performing campaign:** '{worst_campaign['Campaign']}' with "
            f"{worst_campaign['ROI (%)']:.1f}% ROI — review targeting and creative."
        )

    if "Country" in df.columns:
        country_rev = df.groupby("Country")["Revenue"].sum().sort_values(ascending=False)
        if not country_rev.empty:
            insights.append(
                f"**Best performing country:** {country_rev.index[0]} generated "
                f"₹{country_rev.iloc[0]:,.0f} in revenue, the highest of all regions."
            )

    if "Device" in df.columns:
        device_profit = df.groupby("Device").apply(
            lambda g: g["Revenue"].sum() - g["Cost"].sum(), include_groups=False
        ).sort_values(ascending=False)
        if not device_profit.empty:
            insights.append(
                f"**Most profitable device:** {device_profit.index[0]} users generated the highest "
                f"net profit (₹{device_profit.iloc[0]:,.0f})."
            )

    total_revenue = df["Revenue"].sum()
    if total_revenue > 0 and not ch_perf.empty:
        top_contributor = ch_perf.sort_values("Revenue", ascending=False).iloc[0]
        share = top_contributor["Revenue"] / total_revenue * 100
        insights.append(
            f"**Revenue concentration:** {top_contributor['Marketing Channel']} alone contributes "
            f"{share:.1f}% of total revenue — a signal of channel dependency risk."
        )

    return insights


def generate_recommendations(df: pd.DataFrame) -> list[str]:
    """
    Generate actionable, data-informed recommendations based on the
    filtered dataset's funnel and channel performance.
    """
    if df.empty:
        return ["No data available to generate recommendations."]

    recs = []
    funnel = funnel_summary(df)
    ch_perf = channel_performance(df)

    # Drop-off driven recommendation
    if not funnel.empty:
        worst_stage = funnel.iloc[1:].sort_values("Drop-off (%)", ascending=False).iloc[0]
        stage_name = worst_stage["Stage"]
        if stage_name == "Clicks":
            recs.append("Improve ad creative and targeting to lift click-through rate.")
        elif stage_name == "Landing Page Visits":
            recs.append("Reduce landing page load time and fix broken redirects to curb click-to-visit loss.")
        elif stage_name == "Leads":
            recs.append("Improve landing page UX and simplify lead capture forms to convert more visitors.")
        elif stage_name == "Qualified Leads":
            recs.append("Refine lead scoring criteria and sales qualification process to qualify more leads.")
        elif stage_name == "Customers":
            recs.append("Strengthen sales follow-up cadence and offer incentives to close qualified leads faster.")

    if not ch_perf.empty:
        low_roi = ch_perf.sort_values("ROI (%)", ascending=True).iloc[0]
        high_roi = ch_perf.sort_values("ROI (%)", ascending=False).iloc[0]
        recs.append(f"Reduce or renegotiate ad spend on {low_roi['Marketing Channel']} — it shows the lowest ROI.")
        recs.append(f"Increase budget allocation to {high_roi['Marketing Channel']} to scale high-ROI performance.")

        low_ctr = ch_perf.sort_values("CTR (%)", ascending=True).iloc[0]
        recs.append(f"Optimize ad copy and creatives for {low_ctr['Marketing Channel']} to lift its low CTR.")

    recs.extend([
        "Set up retargeting campaigns for users who abandoned the funnel after visiting the landing page.",
        "Run A/B tests on landing page layouts, headlines, and CTAs to reduce visitor-to-lead drop-off.",
        "Reduce cost-per-lead by shifting spend toward organic and referral channels where feasible.",
        "Personalize offers by device and age group based on observed conversion skews.",
        "Implement lead-nurturing email sequences to move more qualified leads to paying customers.",
        "Introduce loyalty or referral incentives to increase repeat purchase and customer lifetime value.",
    ])

    # De-duplicate while preserving order, cap at 10
    seen = set()
    unique_recs = []
    for r in recs:
        if r not in seen:
            unique_recs.append(r)
            seen.add(r)
    return unique_recs[:10]
