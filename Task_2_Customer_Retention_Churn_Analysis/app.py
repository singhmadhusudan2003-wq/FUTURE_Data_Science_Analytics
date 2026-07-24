"""Interactive Customer Retention & Churn Analysis dashboard.

Run locally with: streamlit run app.py
"""
from __future__ import annotations

import io
import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT_DIR = Path(__file__).resolve().parent
DATA_PATH = ROOT_DIR / "data" / "Telco_Customer_Churn_Cleaned.csv"
PRIMARY, SECONDARY, DANGER = "#2563EB", "#14B8A6", "#EF4444"

st.set_page_config(page_title="Customer Retention & Churn Analysis", page_icon="📊", layout="wide", initial_sidebar_state="expanded")


def inject_css() -> None:
    """Apply the dashboard's compact, accessible visual system."""
    st.markdown("""<style>
    .stApp {background:#F8FAFC;color:#0F172A} [data-testid="stSidebar"] {background:linear-gradient(180deg,#0F172A,#1E3A5F)} [data-testid="stSidebar"] * {color:#F8FAFC}
    .hero {padding:1.65rem 2rem;border-radius:18px;color:#fff;background:linear-gradient(120deg,#0B1736 0%,#1D4ED8 56%,#0F9D9A 100%);margin:0 0 1.5rem;box-shadow:0 12px 30px rgba(15,23,42,.2);overflow:hidden}
    .hero-kicker {font-size:.84rem;font-weight:700;letter-spacing:.03em;opacity:.92;margin-bottom:.55rem}.hero h1 {font-size:2.2rem;line-height:1.15;margin:0;font-weight:750;letter-spacing:-.7px}.hero-subtitle {font-size:1.02rem;line-height:1.55;max-width:900px;opacity:.9;margin:.65rem 0 1.05rem}.hero-meta {display:flex;flex-wrap:wrap;gap:.55rem .75rem}.hero-meta span {background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.2);border-radius:999px;padding:.36rem .65rem;font-size:.82rem;font-weight:600}
    @media (max-width: 700px) {.hero {padding:1.3rem 1.15rem;border-radius:15px}.hero h1 {font-size:1.65rem}.hero-subtitle {font-size:.94rem}.hero-meta {gap:.45rem}.hero-meta span {width:100%;border-radius:8px}}
    .kpi-card {background:#fff;border-radius:14px;padding:1rem 1.05rem;border:1px solid #E2E8F0;box-shadow:0 4px 12px rgba(15,23,42,.06);min-height:108px;transition:transform .2s,box-shadow .2s}.kpi-card:hover {transform:translateY(-3px);box-shadow:0 9px 20px rgba(37,99,235,.14)}
    .kpi-label {font-size:.78rem;color:#64748B;font-weight:650;text-transform:uppercase}.kpi-value {font-size:1.55rem;color:#0F172A;font-weight:750;margin-top:.35rem}
    .section-title {font-size:1.35rem;font-weight:750;margin:1.35rem 0 .2rem;color:#0F172A}.section-subtitle {color:#64748B;margin:0 0 .7rem}
    .insight {padding:.7rem .9rem;margin:.38rem 0;background:#fff;border-radius:9px;border-left:4px solid #2563EB;box-shadow:0 2px 7px rgba(15,23,42,.05)}.footer {margin-top:2.25rem;padding:1.35rem 1rem;background:#F1F5F9;border-top:1px solid #CBD5E1;text-align:center;color:#475569;font-size:.82rem;line-height:1.7}.footer p {margin:.08rem 0}.footer strong {color:#1E3A8A}.footer .footer-stack {display:flex;flex-wrap:wrap;justify-content:center;gap:.2rem 1rem}@media (max-width:700px) {.footer {margin-top:1.5rem;padding:1.1rem .75rem;font-size:.76rem}.footer .footer-stack {flex-direction:column;gap:.05rem}}
    </style>""", unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def load_data(path: str) -> pd.DataFrame:
    """Load and normalize the project's cleaned Telco source dataset."""
    data = pd.read_csv(path)
    data.columns = data.columns.str.strip()
    for col in ["tenure", "MonthlyCharges", "TotalCharges", "CLV_Estimate"]:
        if col in data:
            data[col] = pd.to_numeric(data[col], errors="coerce").fillna(0)
    data["Churn"] = data["Churn"].astype(str).str.strip().str.title()
    data["ChurnFlag"] = (data["Churn"] == "Yes").astype(int)
    risk_score = ((data["Contract"] == "Month-to-month").astype(int) * 2 + (data["InternetService"] == "Fiber optic").astype(int) + (data["PaymentMethod"] == "Electronic check").astype(int) + (data["tenure"] <= 12).astype(int))
    data["RiskSegment"] = np.select([risk_score >= 3, risk_score >= 1], ["High Risk", "Medium Risk"], default="Low Risk")
    data["EstimatedCLV"] = data.get("CLV_Estimate", data["MonthlyCharges"] * np.maximum(data["tenure"], 1))
    data["RevenueAtRisk"] = data["MonthlyCharges"] * data["ChurnFlag"]
    data["AcquisitionMonth"] = (pd.Timestamp("2024-01-01") - pd.to_timedelta(data["tenure"] * 30, unit="D")).dt.to_period("M").dt.to_timestamp()
    return data


def format_currency(value: float) -> str:
    return f"${value:,.0f}"


def kpi_card(label: str, value: str, icon: str) -> None:
    st.markdown(f'<div class="kpi-card"><div class="kpi-label">{icon} {label}</div><div class="kpi-value">{value}</div></div>', unsafe_allow_html=True)


def chart_layout(fig: go.Figure, height: int = 350) -> go.Figure:
    fig.update_layout(height=height, margin=dict(l=12, r=12, t=45, b=12), paper_bgcolor="white", plot_bgcolor="white", font=dict(color="#334155"), legend_title_text="")
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#E2E8F0")
    return fig


def churn_rate_table(data: pd.DataFrame, column: str) -> pd.DataFrame:
    """Return customer count, revenue, and churn percentage by category."""
    output = data.groupby(column, dropna=False).agg(Customers=("ChurnFlag", "size"), ChurnRate=("ChurnFlag", "mean"), Revenue=("MonthlyCharges", "sum")).reset_index()
    output["ChurnRate"] *= 100
    return output


def build_cohort_matrix(data: pd.DataFrame) -> pd.DataFrame:
    """Build a tenure-based retention matrix for the snapshot dataset."""
    cohort = pd.crosstab(data["AcquisitionMonth"], data["tenure"]).reindex(columns=range(0, 73), fill_value=0)
    retention = cohort.cumsum(axis=1).iloc[:, ::3]
    retention.columns = [f"Month {month}" for month in retention.columns]
    return retention.div(retention.max(axis=1).replace(0, np.nan), axis=0).mul(100).fillna(0)


def generate_insights(data: pd.DataFrame) -> list[str]:
    """Create at least 15 live, data-backed executive insights."""
    overall_churn = data["ChurnFlag"].mean() * 100
    contract = churn_rate_table(data, "Contract").sort_values("ChurnRate")
    internet = churn_rate_table(data, "InternetService").sort_values("ChurnRate")
    payment = churn_rate_table(data, "PaymentMethod").sort_values("ChurnRate")
    gender = churn_rate_table(data, "gender").sort_values("ChurnRate")
    segment = churn_rate_table(data, "RiskSegment").sort_values("ChurnRate")
    tenure_churn, charge_churn = data.groupby("Churn")["tenure"].mean(), data.groupby("Churn")["MonthlyCharges"].mean()
    clv_contract = data.groupby("Contract")["EstimatedCLV"].mean().sort_values()
    revenue_segment = data.groupby("RiskSegment")["MonthlyCharges"].sum().sort_values()
    loyal = data.loc[data["Churn"] == "No"].groupby("Contract")["tenure"].mean().sort_values()
    senior, partner, dependent = (churn_rate_table(data, col).sort_values("ChurnRate") for col in ["SeniorCitizen", "Partner", "Dependents"])
    return [
        f"Overall churn is {overall_churn:.1f}% across {len(data):,} selected customers.",
        f"{contract.iloc[-1]['Contract']} has the highest contract churn rate ({contract.iloc[-1]['ChurnRate']:.1f}%).",
        f"{contract.iloc[0]['Contract']} has the strongest contract retention ({100-contract.iloc[0]['ChurnRate']:.1f}%).",
        f"{internet.iloc[-1]['InternetService']} customers have the highest churn ({internet.iloc[-1]['ChurnRate']:.1f}%).",
        f"{payment.iloc[-1]['PaymentMethod']} is the highest-churn payment method ({payment.iloc[-1]['ChurnRate']:.1f}%).",
        f"The {segment.iloc[-1]['RiskSegment']} segment is most exposed, with {segment.iloc[-1]['Customers']:,} customers and {segment.iloc[-1]['ChurnRate']:.1f}% churn.",
        f"{revenue_segment.index[-1]} customers contribute the most selected monthly revenue ({format_currency(revenue_segment.iloc[-1])}).",
        f"Churned customers average {tenure_churn.get('Yes', 0):.1f} months of tenure, versus {tenure_churn.get('No', 0):.1f} for retained customers.",
        f"Churned customers pay {format_currency(charge_churn.get('Yes', 0))} on average each month.",
        f"{clv_contract.index[-1]} has the highest average estimated CLV ({format_currency(clv_contract.iloc[-1])}).",
        f"{clv_contract.index[0]} has the lowest average estimated CLV ({format_currency(clv_contract.iloc[0])}).",
        f"Most loyal retained customers are on {loyal.index[-1]} contracts, averaging {loyal.iloc[-1]:.1f} months.",
        f"Senior Citizen = {senior.iloc[-1]['SeniorCitizen']} has {senior.iloc[-1]['ChurnRate']:.1f}% churn.",
        f"Partner = {partner.iloc[-1]['Partner']} has the highest partner-group churn ({partner.iloc[-1]['ChurnRate']:.1f}%).",
        f"Dependents = {dependent.iloc[-1]['Dependents']} has the highest dependent-group churn ({dependent.iloc[-1]['ChurnRate']:.1f}%).",
        f"{gender.iloc[-1]['gender']} customers have the higher gender-group churn rate ({gender.iloc[-1]['ChurnRate']:.1f}%).",
    ]


def create_pdf(kpis: dict[str, str], insights: list[str]) -> bytes:
    """Create a concise PDF report directly from the active dashboard results."""
    buffer = io.BytesIO()
    document = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=36, leftMargin=36)
    styles = getSampleStyleSheet()
    story = [Paragraph("Customer Retention & Churn Analysis", styles["Title"]), Paragraph("Filtered dashboard business report", styles["Heading2"]), Spacer(1, 0.2 * inch)]
    table = Table([["Metric", "Value"]] + [[key, val] for key, val in kpis.items()], colWidths=[3.6 * inch, 2.0 * inch])
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(PRIMARY)), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), .3, colors.HexColor("#CBD5E1")), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]), ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("PADDING", (0, 0), (-1, -1), 7)]))
    story += [table, Spacer(1, .22 * inch), Paragraph("Key Insights", styles["Heading2"])]
    story += [Paragraph(f"• {item}", styles["BodyText"]) for item in insights]
    document.build(story)
    return buffer.getvalue()


def reset_filter_state() -> None:
    """Clear filter widget state before Streamlit redraws the sidebar."""
    for key in list(st.session_state):
        if key.startswith("filter_"):
            del st.session_state[key]


def main() -> None:
    inject_css()
    if not DATA_PATH.exists():
        st.error(f"Dataset not found: {DATA_PATH}")
        st.stop()
    data = load_data(str(DATA_PATH))
    st.sidebar.markdown("# 📊 Churn Navigator")
    st.sidebar.caption("Refine every metric and visual")
    columns = ["gender", "SeniorCitizen", "Partner", "Dependents", "Contract", "PaymentMethod", "InternetService"]
    # Changed: native sidebar widgets rerun Streamlit immediately on every selection.
    # No submit button or filter-specific apply state is required.
    selections = {
        col: st.sidebar.multiselect(
            col.replace("SeniorCitizen", "Senior Citizen").replace("InternetService", "Internet Service"),
            sorted(data[col].dropna().unique().tolist()),
            default=sorted(data[col].dropna().unique().tolist()),
            key=f"filter_{col}",
        )
        for col in columns
    }
    # Retained: callback clears all filter widgets before Streamlit redraws the dashboard.
    st.sidebar.button("↺ Reset filters", use_container_width=True, on_click=reset_filter_state)
    filtered = data.copy()
    for col, values in selections.items():
        filtered = filtered[filtered[col].isin(values)]
    if filtered.empty:
        st.warning("No customers match these filters. Reset or broaden a selection.")
        st.stop()
    # Updated header only: premium, responsive hero for the business analytics dashboard.
    with st.container():
        st.markdown(
            """
            <div class="hero">
                <div class="hero-kicker">🎓 Future Intern – Data Science &amp; Analytics</div>
                <h1>📊 Customer Retention &amp; Churn Analysis Dashboard</h1>
                <p class="hero-subtitle">Interactive analytics dashboard for customer retention, churn prediction insights, customer lifetime value, cohort analysis, and business decision-making.</p>
                <div class="hero-meta">
                    <span>🗂 Dataset: IBM Telco Customer Churn (7,043 Customers)</span>
                    <span>👨‍💻 Developed by: Madhu Sudhan</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    churn_count = int(filtered["ChurnFlag"].sum())
    retention_rate = (1 - filtered["ChurnFlag"].mean()) * 100
    kpis = {"Total Customers": f"{len(filtered):,}", "Churn Customers": f"{churn_count:,}", "Retention Rate": f"{retention_rate:.1f}%", "Churn Rate": f"{100-retention_rate:.1f}%", "Average Monthly Charges": format_currency(filtered["MonthlyCharges"].mean()), "Average Total Charges": format_currency(filtered["TotalCharges"].mean()), "Average Tenure": f"{filtered['tenure'].mean():.1f} months", "Estimated Customer Lifetime Value": format_currency(filtered["EstimatedCLV"].mean()), "Revenue At Risk": format_currency(filtered["RevenueAtRisk"].sum())}
    cards = [("Total Customers", "👥"), ("Churn Customers", "⚠️"), ("Retention Rate", "🛡️"), ("Churn Rate", "📉"), ("Average Monthly Charges", "💳"), ("Average Total Charges", "💰"), ("Average Tenure", "🗓️"), ("Estimated Customer Lifetime Value", "✨"), ("Revenue At Risk", "🚨")]
    for start in range(0, len(cards), 3):
        for container, (label, icon) in zip(st.columns(3), cards[start:start + 3]):
            with container: kpi_card(label, kpis[label], icon)

    st.markdown('<div class="section-title">Churn Drivers & Customer Profile</div>', unsafe_allow_html=True)
    row = st.columns(3)
    with row[0]: st.plotly_chart(chart_layout(px.pie(filtered, names="Churn", color="Churn", title="Churn Distribution", color_discrete_map={"Yes": DANGER, "No": SECONDARY}, hole=.58)), use_container_width=True)
    with row[1]:
        fig = px.bar(churn_rate_table(filtered, "Contract"), x="Contract", y="ChurnRate", color="ChurnRate", title="Contract vs Churn Rate", color_continuous_scale="Reds", text_auto=".1f"); fig.update_yaxes(ticksuffix="%")
        st.plotly_chart(chart_layout(fig), use_container_width=True)
    with row[2]:
        fig = px.bar(filtered.groupby(["InternetService", "Churn"]).size().reset_index(name="Customers"), x="InternetService", y="Customers", color="Churn", barmode="group", title="Internet Service vs Churn", color_discrete_map={"Yes": DANGER, "No": SECONDARY})
        st.plotly_chart(chart_layout(fig), use_container_width=True)
    row = st.columns(2)
    with row[0]:
        fig = px.bar(churn_rate_table(filtered, "PaymentMethod").sort_values("ChurnRate", ascending=False), y="PaymentMethod", x="ChurnRate", orientation="h", title="Payment Method vs Churn Rate", color="ChurnRate", color_continuous_scale="Blues", text_auto=".1f"); fig.update_xaxes(ticksuffix="%")
        st.plotly_chart(chart_layout(fig), use_container_width=True)
    with row[1]:
        tree = filtered.groupby(["RiskSegment", "Contract", "Churn"]).size().reset_index(name="Customers")
        fig = px.treemap(tree, path=["RiskSegment", "Contract", "Churn"], values="Customers", color="RiskSegment", title="Customer Segments", color_discrete_map={"High Risk": DANGER, "Medium Risk": "#F59E0B", "Low Risk": SECONDARY})
        st.plotly_chart(chart_layout(fig), use_container_width=True)

    st.markdown('<div class="section-title">Customer Value & Retention</div>', unsafe_allow_html=True)
    row = st.columns(3)
    with row[0]: st.plotly_chart(chart_layout(px.histogram(filtered, x="tenure", color="Churn", nbins=24, barmode="overlay", title="Tenure Distribution", color_discrete_map={"Yes": DANGER, "No": SECONDARY})), use_container_width=True)
    with row[1]: st.plotly_chart(chart_layout(px.box(filtered, x="Churn", y="MonthlyCharges", color="Churn", title="Monthly Charges vs Churn", color_discrete_map={"Yes": DANGER, "No": SECONDARY})), use_container_width=True)
    with row[2]: st.plotly_chart(chart_layout(px.scatter(filtered, x="MonthlyCharges", y="TotalCharges", color="Churn", size="tenure", size_max=18, title="Monthly Charges vs Total Charges", color_discrete_map={"Yes": DANGER, "No": SECONDARY}, opacity=.7)), use_container_width=True)
    row = st.columns(2)
    with row[0]:
        numeric = filtered[["tenure", "MonthlyCharges", "TotalCharges", "EstimatedCLV", "ChurnFlag"]].corr().round(2)
        st.plotly_chart(chart_layout(px.imshow(numeric, text_auto=True, aspect="auto", color_continuous_scale="RdBu_r", zmin=-1, zmax=1, title="Correlation Matrix")), use_container_width=True)
    with row[1]:
        trend = filtered.groupby("tenure").agg(RetentionRate=("ChurnFlag", lambda x: (1-x.mean())*100)).reset_index()
        fig = px.line(trend, x="tenure", y="RetentionRate", markers=True, title="Retention Trend by Tenure", color_discrete_sequence=[PRIMARY]); fig.update_yaxes(ticksuffix="%")
        st.plotly_chart(chart_layout(fig), use_container_width=True)

    st.markdown('<div class="section-title">Cohort Analysis</div><p class="section-subtitle">Acquisition month is estimated from tenure against the January 2024 snapshot.</p>', unsafe_allow_html=True)
    cohort = build_cohort_matrix(filtered)
    st.plotly_chart(chart_layout(px.imshow(cohort, aspect="auto", color_continuous_scale="Blues", zmin=0, zmax=100, labels={"x": "Customer Age", "y": "Estimated Acquisition Cohort", "color": "Retention %"}, title="Cohort Retention Heatmap"), 430), use_container_width=True)
    with st.expander("View monthly retention table"):
        table = pd.DataFrame({"Month": range(73)}); table["Customers retained"] = [(filtered["tenure"] >= month).sum() for month in range(73)]; table["Retention rate"] = (table["Customers retained"] / len(filtered) * 100).round(1)
        st.dataframe(table, use_container_width=True, hide_index=True)

    st.markdown('<div class="section-title">Customer Lifetime Value & Risk Segmentation</div>', unsafe_allow_html=True)
    stats = st.columns(3); stats[0].metric("Average CLV", format_currency(filtered["EstimatedCLV"].mean())); stats[1].metric("Highest CLV", format_currency(filtered["EstimatedCLV"].max())); stats[2].metric("Lowest CLV", format_currency(filtered["EstimatedCLV"].min()))
    row = st.columns(2)
    with row[0]: st.plotly_chart(chart_layout(px.bar(filtered.groupby("Contract")["EstimatedCLV"].mean().reset_index().sort_values("EstimatedCLV", ascending=False), x="Contract", y="EstimatedCLV", title="Contract-wise CLV", color="EstimatedCLV", color_continuous_scale="Teal")), use_container_width=True)
    with row[1]:
        risk = churn_rate_table(filtered, "RiskSegment")
        fig = px.bar(risk, x="RiskSegment", y="Customers", color="ChurnRate", text="ChurnRate", title="Customer Risk Segmentation", color_continuous_scale="RdYlGn_r"); fig.update_traces(texttemplate="%{text:.1f}% churn", textposition="outside")
        st.plotly_chart(chart_layout(fig), use_container_width=True)
    revenue = filtered.groupby(["RiskSegment", "Churn"])["MonthlyCharges"].sum().reset_index()
    st.plotly_chart(chart_layout(px.bar(revenue, x="RiskSegment", y="MonthlyCharges", color="Churn", barmode="group", title="Revenue Analysis by Risk Segment", color_discrete_map={"Yes": DANGER, "No": SECONDARY})), use_container_width=True)

    insights = generate_insights(filtered)
    st.markdown('<div class="section-title">Executive Insights</div><p class="section-subtitle">Automatically refreshed from the active selection.</p>', unsafe_allow_html=True)
    left, right = st.columns(2)
    for index, insight in enumerate(insights): (left if index % 2 == 0 else right).markdown(f'<div class="insight">💡 {insight}</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Recommended Actions</div>', unsafe_allow_html=True)
    for item in ["Prioritize proactive outreach to high-risk month-to-month customers before their next billing cycle.", "Offer contract-upgrade incentives to high-churn cohorts, with a focus on electronic-check payers.", "Audit fiber-optic customer experience and support journeys where churn is elevated.", "Pair retention offers with tenure milestones, especially during the first 12 months.", "Protect high-CLV customers with service-health alerts and dedicated support paths."]: st.markdown(f"- {item}")
    st.markdown('<div class="section-title">Download Center</div>', unsafe_allow_html=True)
    downloads = st.columns(3)
    downloads[0].download_button("Download filtered dataset (CSV)", filtered.drop(columns=["ChurnFlag"], errors="ignore").to_csv(index=False).encode("utf-8"), "filtered_customer_churn.csv", "text/csv", use_container_width=True)
    downloads[1].download_button("Download business report (PDF)", create_pdf(kpis, insights), "customer_churn_report.pdf", "application/pdf", use_container_width=True)
    downloads[2].download_button("Download KPIs (JSON)", json.dumps(kpis, indent=2).encode("utf-8"), "customer_churn_kpis.json", "application/json", use_container_width=True)
    # Footer: positioned after all dashboard content so it remains at the page bottom.
    st.markdown(
        """
        <footer class="footer">
            <p><strong>© 2026 Madhu Sudhan</strong></p>
            <p>🎓 Future Intern – Data Science &amp; Analytics Internship</p>
            <div class="footer-stack">
                <span>❤️ Built with Python, Streamlit, Plotly, Pandas, NumPy &amp; Scikit-learn</span>
                <span>🗂 IBM Telco Customer Churn Dataset</span>
            </div>
        </footer>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
