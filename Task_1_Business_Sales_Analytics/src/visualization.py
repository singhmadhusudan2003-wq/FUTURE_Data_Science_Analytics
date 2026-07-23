"""
visualization.py
-----------------
Generates all static, professional-quality charts for the Business Sales
Performance Analytics project using Matplotlib and Seaborn. These images
are used in the Jupyter notebook, the PDF report, and the README.

Interactive versions of the key charts are additionally rendered with
Plotly inside the Jupyter notebook and the HTML dashboard
(see dashboard.py).

Author: Future Interns - Data Science & Analytics Track
"""

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import seaborn as sns

sns.set_theme(style="whitegrid", palette="viridis")
plt.rcParams["figure.dpi"] = 130
plt.rcParams["axes.titlesize"] = 14
plt.rcParams["axes.titleweight"] = "bold"
plt.rcParams["axes.labelsize"] = 11
plt.rcParams["font.family"] = "DejaVu Sans"

PRIMARY = "#2563EB"
SECONDARY = "#F59E0B"
GOOD = "#16A34A"
BAD = "#DC2626"


def _currency_fmt(ax, axis="y"):
    formatter = mticker.FuncFormatter(lambda x, _: f"${x:,.0f}")
    if axis == "y":
        ax.yaxis.set_major_formatter(formatter)
    else:
        ax.xaxis.set_major_formatter(formatter)


def _save(fig, out_dir, name):
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    path = Path(out_dir) / name
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {path}")


def plot_monthly_revenue_trend(df, out_dir):
    monthly = df.groupby("Order Year-Month")["Sales"].sum().reset_index()
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(monthly["Order Year-Month"], monthly["Sales"], color=PRIMARY, linewidth=2, marker="o", markersize=3)
    ax.fill_between(monthly["Order Year-Month"], monthly["Sales"], color=PRIMARY, alpha=0.1)
    ax.set_title("Monthly Revenue Trend")
    ax.set_xlabel("Month"); ax.set_ylabel("Revenue")
    _currency_fmt(ax)
    ax.set_xticks(ax.get_xticks()[::3])
    plt.xticks(rotation=45, ha="right")
    _save(fig, out_dir, "revenue_trend.png")


def plot_monthly_profit_trend(df, out_dir):
    monthly = df.groupby("Order Year-Month")["Profit"].sum().reset_index()
    colors = [GOOD if v >= 0 else BAD for v in monthly["Profit"]]
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.bar(monthly["Order Year-Month"], monthly["Profit"], color=colors)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_title("Monthly Profit Trend")
    ax.set_xlabel("Month"); ax.set_ylabel("Profit")
    _currency_fmt(ax)
    ax.set_xticks(ax.get_xticks()[::3])
    plt.xticks(rotation=45, ha="right")
    _save(fig, out_dir, "profit_trend.png")


def plot_sales_by_category(df, out_dir):
    cat = df.groupby("Category", observed=True)["Sales"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(x=cat.values, y=cat.index, hue=cat.index, palette="Blues_r", ax=ax, legend=False)
    ax.set_title("Sales by Category")
    ax.set_xlabel("Total Sales"); ax.set_ylabel("")
    _currency_fmt(ax, axis="x")
    _save(fig, out_dir, "sales_by_category.png")


def plot_profit_by_category(df, out_dir):
    cat = df.groupby("Category", observed=True)["Profit"].sum().sort_values(ascending=False)
    colors = [GOOD if v >= 0 else BAD for v in cat.values]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(cat.index, cat.values, color=colors)
    ax.invert_yaxis()
    ax.set_title("Profit by Category")
    ax.set_xlabel("Total Profit")
    _currency_fmt(ax, axis="x")
    _save(fig, out_dir, "profit_by_category.png")


def plot_sales_by_region(df, out_dir):
    reg = df.groupby("Region", observed=True)["Sales"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.barplot(x=reg.index, y=reg.values, hue=reg.index, palette="viridis", ax=ax, legend=False)
    ax.set_title("Sales by Region")
    ax.set_xlabel("Region"); ax.set_ylabel("Total Sales")
    _currency_fmt(ax)
    _save(fig, out_dir, "sales_by_region.png")


def plot_profit_by_region(df, out_dir):
    reg = df.groupby("Region", observed=True)["Profit"].sum().sort_values(ascending=False)
    colors = [GOOD if v >= 0 else BAD for v in reg.values]
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(reg.index, reg.values, color=colors)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_title("Profit by Region")
    ax.set_xlabel("Region"); ax.set_ylabel("Total Profit")
    _currency_fmt(ax)
    _save(fig, out_dir, "profit_by_region.png")


def plot_top_products(df, out_dir, n=10):
    top = df.groupby("Product Name")["Sales"].sum().sort_values(ascending=False).head(n)
    fig, ax = plt.subplots(figsize=(9, 6))
    sns.barplot(x=top.values, y=top.index, hue=top.index, palette="mako", ax=ax, legend=False)
    ax.set_title(f"Top {n} Products by Sales")
    ax.set_xlabel("Total Sales"); ax.set_ylabel("")
    _currency_fmt(ax, axis="x")
    _save(fig, out_dir, "top_products.png")


def plot_top_customers(df, out_dir, n=10):
    top = df.groupby("Customer Name")["Sales"].sum().sort_values(ascending=False).head(n)
    fig, ax = plt.subplots(figsize=(9, 6))
    sns.barplot(x=top.values, y=top.index, hue=top.index, palette="crest", ax=ax, legend=False)
    ax.set_title(f"Top {n} Customers by Sales")
    ax.set_xlabel("Total Sales"); ax.set_ylabel("")
    _currency_fmt(ax, axis="x")
    _save(fig, out_dir, "top_customers.png")


def plot_discount_vs_profit(df, out_dir):
    sample = df.sample(min(2000, len(df)), random_state=1)
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.scatterplot(data=sample, x="Discount", y="Profit", hue="Category", alpha=0.6, ax=ax, palette="Set2")
    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax.set_title("Discount vs Profit")
    _currency_fmt(ax)
    _save(fig, out_dir, "discount_vs_profit.png")


def plot_correlation_heatmap(df, out_dir):
    num_cols = ["Sales", "Quantity", "Discount", "Profit", "Profit Margin (%)", "Shipping Days"]
    corr = df[num_cols].corr()
    fig, ax = plt.subplots(figsize=(7, 6))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0, ax=ax, linewidths=0.5)
    ax.set_title("Correlation Heatmap")
    _save(fig, out_dir, "correlation_heatmap.png")


def plot_sales_distribution(df, out_dir):
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.histplot(df["Sales"], bins=50, color=PRIMARY, kde=True, ax=ax)
    ax.set_title("Sales Distribution")
    _currency_fmt(ax, axis="x")
    _save(fig, out_dir, "sales_distribution.png")


def plot_profit_distribution(df, out_dir):
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.histplot(df["Profit"], bins=50, color=SECONDARY, kde=True, ax=ax)
    ax.axvline(0, color="black", linestyle="--", linewidth=1)
    ax.set_title("Profit Distribution")
    _currency_fmt(ax, axis="x")
    _save(fig, out_dir, "profit_distribution.png")


def plot_quantity_analysis(df, out_dir):
    qty = df.groupby("Category", observed=True)["Quantity"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(x=qty.index, y=qty.values, hue=qty.index, palette="flare", ax=ax, legend=False)
    ax.set_title("Total Units Sold by Category")
    ax.set_ylabel("Units Sold")
    _save(fig, out_dir, "quantity_analysis.png")


def plot_state_wise_sales(df, out_dir, n=15):
    state = df.groupby("State", observed=True)["Sales"].sum().sort_values(ascending=False).head(n)
    fig, ax = plt.subplots(figsize=(9, 7))
    sns.barplot(x=state.values, y=state.index, hue=state.index, palette="Blues_r", ax=ax, legend=False)
    ax.set_title(f"Top {n} States by Sales")
    ax.set_xlabel("Total Sales"); ax.set_ylabel("")
    _currency_fmt(ax, axis="x")
    _save(fig, out_dir, "state_wise_sales.png")


def plot_customer_segment_analysis(df, out_dir):
    seg = df.groupby("Segment", observed=True)["Sales"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(7, 7))
    colors = sns.color_palette("Set2", len(seg))
    ax.pie(seg.values, labels=seg.index, autopct="%1.1f%%", startangle=90, colors=colors,
           wedgeprops={"edgecolor": "white", "linewidth": 1.5})
    ax.set_title("Sales Share by Customer Segment")
    _save(fig, out_dir, "customer_segment_analysis.png")


def plot_year_wise_growth(df, out_dir):
    yearly = df.groupby("Order Year")["Sales"].sum().sort_index()
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(yearly.index.astype(str), yearly.values, color=PRIMARY)
    for bar, val in zip(bars, yearly.values):
        ax.text(bar.get_x() + bar.get_width() / 2, val, f"${val:,.0f}",
                ha="center", va="bottom", fontsize=9)
    ax.set_title("Year-wise Revenue Growth")
    ax.set_xlabel("Year"); ax.set_ylabel("Total Sales")
    _currency_fmt(ax)
    _save(fig, out_dir, "year_wise_growth.png")


def generate_all_charts(df: pd.DataFrame, out_dir: str = "../images"):
    """Generate the complete set of charts required for the project."""
    plot_monthly_revenue_trend(df, out_dir)
    plot_monthly_profit_trend(df, out_dir)
    plot_sales_by_category(df, out_dir)
    plot_profit_by_category(df, out_dir)
    plot_sales_by_region(df, out_dir)
    plot_profit_by_region(df, out_dir)
    plot_top_products(df, out_dir)
    plot_top_customers(df, out_dir)
    plot_discount_vs_profit(df, out_dir)
    plot_correlation_heatmap(df, out_dir)
    plot_sales_distribution(df, out_dir)
    plot_profit_distribution(df, out_dir)
    plot_quantity_analysis(df, out_dir)
    plot_state_wise_sales(df, out_dir)
    plot_customer_segment_analysis(df, out_dir)
    plot_year_wise_growth(df, out_dir)
    print("\nAll charts generated successfully.")


if __name__ == "__main__":
    from data_cleaning import clean_pipeline

    data = clean_pipeline("../data/sales_data.csv")
    generate_all_charts(data, out_dir="../images")
