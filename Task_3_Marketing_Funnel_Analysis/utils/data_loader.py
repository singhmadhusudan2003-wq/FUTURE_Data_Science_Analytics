"""
data_loader.py
---------------
Handles loading, validation, cleaning, and caching of the marketing
funnel dataset used across the Streamlit dashboard.
"""

from __future__ import annotations

import os
import pandas as pd
import streamlit as st

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "marketing_funnel.csv")

REQUIRED_COLUMNS = [
    "Date", "Campaign", "Marketing Channel", "Impressions", "Clicks", "CTR",
    "Landing Page Visits", "Leads", "Qualified Leads", "Customers",
    "Conversion Rate", "Revenue", "Cost", "ROI", "Country", "Device",
    "Age Group", "Gender", "Campaign Type",
]

NUMERIC_COLUMNS = [
    "Impressions", "Clicks", "CTR", "Landing Page Visits", "Leads",
    "Qualified Leads", "Customers", "Conversion Rate", "Revenue", "Cost", "ROI",
]


@st.cache_data(show_spinner="Loading marketing funnel dataset...")
def load_data(path: str = DATA_PATH) -> pd.DataFrame:
    """
    Load the marketing funnel dataset from CSV, validate its schema,
    coerce data types, and perform light cleaning.

    Parameters
    ----------
    path : str
        Path to the CSV file.

    Returns
    -------
    pd.DataFrame
        Cleaned dataframe ready for analysis.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Dataset not found at '{path}'. Ensure 'marketing_funnel.csv' "
            "exists inside the /data folder."
        )

    df = pd.read_csv(path)

    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {missing}")

    # Type coercion
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    for col in NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop rows with an unparseable date (should not normally occur)
    df = df.dropna(subset=["Date"]).copy()

    # Fill any stray numeric NaNs with 0 (defensive, dataset is generated clean)
    df[NUMERIC_COLUMNS] = df[NUMERIC_COLUMNS].fillna(0)

    # Derive helper columns used throughout the dashboard
    df["Month"] = df["Date"].dt.to_period("M").astype(str)
    df["Weekday"] = df["Date"].dt.day_name()
    df["Year"] = df["Date"].dt.year

    return df


def filter_data(
    df: pd.DataFrame,
    date_range: tuple | None = None,
    channels: list | None = None,
    campaigns: list | None = None,
    countries: list | None = None,
    devices: list | None = None,
) -> pd.DataFrame:
    """
    Apply sidebar filter selections to the dataframe.

    Any filter left as None or empty is skipped (treated as "All").
    """
    filtered = df.copy()

    if date_range and len(date_range) == 2:
        start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        filtered = filtered[(filtered["Date"] >= start) & (filtered["Date"] <= end)]

    if channels:
        filtered = filtered[filtered["Marketing Channel"].isin(channels)]

    if campaigns:
        filtered = filtered[filtered["Campaign"].isin(campaigns)]

    if countries:
        filtered = filtered[filtered["Country"].isin(countries)]

    if devices:
        filtered = filtered[filtered["Device"].isin(devices)]

    return filtered
