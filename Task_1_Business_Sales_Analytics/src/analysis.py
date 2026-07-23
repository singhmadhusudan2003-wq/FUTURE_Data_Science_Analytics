"""
analysis.py
-----------
Business KPI calculations and analytical summaries for the
Business Sales Performance Analytics project.

Author: Future Interns - Data Science & Analytics Track
"""

import pandas as pd


def calculate_kpis(df: pd.DataFrame) -> dict:
    """Calculate the core business KPIs used across the report and dashboard."""
    total_revenue = df["Sales"].sum()
    total_profit = df["Profit"].sum()
    total_orders = df["Order ID"].nunique()
    avg_order_value = df["Sales"].sum() / total_orders if total_orders else 0
    profit_margin = (total_profit / total_revenue * 100) if total_revenue else 0

    region_sales = df.groupby("Region", observed=True)["Sales"].sum().sort_values(ascending=False)
    category_sales = df.groupby("Category", observed=True)["Sales"].sum().sort_values(ascending=False)
    category_profit = df.groupby("Category", observed=True)["Profit"].sum().sort_values(ascending=False)
    product_sales = df.groupby("Product Name")["Sales"].sum().sort_values(ascending=False)
    customer_sales = df.groupby("Customer Name")["Sales"].sum().sort_values(ascending=False)
    month_sales = df.groupby("Order Year-Month")["Sales"].sum().sort_values(ascending=False)
    month_profit = df.groupby("Order Year-Month")["Profit"].sum().sort_values(ascending=False)

    year_sales = df.groupby("Order Year")["Sales"].sum().sort_index()
    growth_pct = 0.0
    if len(year_sales) >= 2:
        first, last = year_sales.iloc[0], year_sales.iloc[-1]
        if first != 0:
            growth_pct = ((last - first) / first) * 100

    kpis = {
        "Total Revenue": round(total_revenue, 2),
        "Total Profit": round(total_profit, 2),
        "Total Orders": int(total_orders),
        "Average Order Value": round(avg_order_value, 2),
        "Profit Margin (%)": round(profit_margin, 2),
        "Best Region": region_sales.index[0],
        "Best Region Sales": round(region_sales.iloc[0], 2),
        "Worst Region": region_sales.index[-1],
        "Worst Region Sales": round(region_sales.iloc[-1], 2),
        "Best Category": category_sales.index[0],
        "Best Category Sales": round(category_sales.iloc[0], 2),
        "Worst Category": category_sales.index[-1],
        "Worst Category Sales": round(category_sales.iloc[-1], 2),
        "Most Profitable Category": category_profit.index[0],
        "Best Product": product_sales.index[0],
        "Best Product Sales": round(product_sales.iloc[0], 2),
        "Top Customer": customer_sales.index[0],
        "Top Customer Sales": round(customer_sales.iloc[0], 2),
        "Highest Sales Month": month_sales.index[0],
        "Highest Sales Month Value": round(month_sales.iloc[0], 2),
        "Highest Profit Month": month_profit.index[0],
        "Highest Profit Month Value": round(month_profit.iloc[0], 2),
        "Revenue Growth (%) (First to Last Year)": round(growth_pct, 2),
    }
    return kpis


def region_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Region", observed=True)
        .agg(Total_Sales=("Sales", "sum"), Total_Profit=("Profit", "sum"),
             Orders=("Order ID", "nunique"), Avg_Discount=("Discount", "mean"))
        .sort_values("Total_Sales", ascending=False)
        .round(2)
    )


def category_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["Category", "Sub-Category"], observed=True)
        .agg(Total_Sales=("Sales", "sum"), Total_Profit=("Profit", "sum"),
             Orders=("Order ID", "nunique"))
        .sort_values("Total_Sales", ascending=False)
        .round(2)
    )


def top_products(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    return (
        df.groupby("Product Name")
        .agg(Total_Sales=("Sales", "sum"), Total_Profit=("Profit", "sum"),
             Units_Sold=("Quantity", "sum"))
        .sort_values("Total_Sales", ascending=False)
        .head(n)
        .round(2)
    )


def top_customers(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    return (
        df.groupby("Customer Name")
        .agg(Total_Sales=("Sales", "sum"), Orders=("Order ID", "nunique"))
        .sort_values("Total_Sales", ascending=False)
        .head(n)
        .round(2)
    )


def monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Order Year-Month")
        .agg(Total_Sales=("Sales", "sum"), Total_Profit=("Profit", "sum"), Orders=("Order ID", "nunique"))
        .reset_index()
        .sort_values("Order Year-Month")
        .round(2)
    )


def yearly_growth(df: pd.DataFrame) -> pd.DataFrame:
    yearly = df.groupby("Order Year").agg(Total_Sales=("Sales", "sum")).sort_index()
    yearly["Growth (%)"] = yearly["Total_Sales"].pct_change() * 100
    return yearly.round(2)


def segment_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Segment", observed=True)
        .agg(Total_Sales=("Sales", "sum"), Total_Profit=("Profit", "sum"),
             Orders=("Order ID", "nunique"))
        .sort_values("Total_Sales", ascending=False)
        .round(2)
    )


def state_summary(df: pd.DataFrame, n: int = 15) -> pd.DataFrame:
    return (
        df.groupby("State", observed=True)
        .agg(Total_Sales=("Sales", "sum"), Total_Profit=("Profit", "sum"))
        .sort_values("Total_Sales", ascending=False)
        .head(n)
        .round(2)
    )
