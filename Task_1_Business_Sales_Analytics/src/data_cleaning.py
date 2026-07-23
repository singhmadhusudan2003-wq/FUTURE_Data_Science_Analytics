"""
data_cleaning.py
-----------------
Data cleaning and preprocessing utilities for the Business Sales
Performance Analytics project.

Author: Future Interns - Data Science & Analytics Track
"""

from pathlib import Path

import numpy as np
import pandas as pd


def load_raw_data(path: str) -> pd.DataFrame:
    """Load the raw sales CSV file into a DataFrame."""
    df = pd.read_csv(path)
    return df


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle missing values in the sales dataset.

    - Sales: imputed using the median sales value for the same
      Category + Sub-Category group (falls back to global median).
    - Discount: missing values assumed to be 0 (no discount applied).
    - Customer Name: filled with 'Unknown Customer'.
    - Ship Date: rows with a blank/missing Ship Date are dropped, since
      shipping information is required for logistics analysis.
    """
    df = df.copy()

    # Treat empty strings as missing
    df["Ship Date"] = df["Ship Date"].replace("", np.nan)
    df = df.dropna(subset=["Ship Date"])

    # Sales: group-wise median imputation
    df["Sales"] = df.groupby(["Category", "Sub-Category"])["Sales"].transform(
        lambda s: s.fillna(s.median())
    )
    df["Sales"] = df["Sales"].fillna(df["Sales"].median())

    # Discount: assume no discount when missing
    df["Discount"] = df["Discount"].fillna(0)

    # Customer Name: fill placeholder
    df["Customer Name"] = df["Customer Name"].fillna("Unknown Customer")

    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Remove fully duplicated rows (same Order ID + Product ID combo)."""
    before = len(df)
    df = df.drop_duplicates(subset=["Order ID", "Product ID"], keep="first")
    after = len(df)
    print(f"Removed {before - after} duplicate rows.")
    return df.reset_index(drop=True)


def convert_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """Convert columns to their correct data types."""
    df = df.copy()
    df["Order Date"] = pd.to_datetime(df["Order Date"], errors="coerce")
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], errors="coerce")
    df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce")
    df["Profit"] = pd.to_numeric(df["Profit"], errors="coerce")
    df["Discount"] = pd.to_numeric(df["Discount"], errors="coerce")
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce").astype("Int64")

    category_cols = ["Segment", "Country", "State", "City", "Region",
                      "Category", "Sub-Category", "Shipping Mode",
                      "Payment Method", "Sales Representative"]
    for col in category_cols:
        df[col] = df[col].astype("category")

    df = df.dropna(subset=["Order Date", "Ship Date", "Sales"])
    return df


def detect_outliers(df: pd.DataFrame, column: str = "Sales", method: str = "iqr") -> pd.DataFrame:
    """
    Flag outliers using the IQR method and cap them at the upper bound
    (winsorization) rather than dropping the rows, to preserve sample size.
    Returns the DataFrame with an added '<column>_outlier' boolean flag.
    """
    df = df.copy()
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    df[f"{column}_outlier"] = (df[column] < lower_bound) | (df[column] > upper_bound)
    n_outliers = df[f"{column}_outlier"].sum()
    print(f"Detected {n_outliers} outliers in '{column}' (IQR method).")

    # Cap extreme values instead of removing them
    df[column] = np.where(df[column] > upper_bound, upper_bound, df[column])
    df[column] = np.where(df[column] < lower_bound, lower_bound, df[column])

    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create additional analytical features used throughout the analysis."""
    df = df.copy()

    df["Order Year"] = df["Order Date"].dt.year
    df["Order Month"] = df["Order Date"].dt.month
    df["Order Month Name"] = df["Order Date"].dt.strftime("%b")
    df["Order Year-Month"] = df["Order Date"].dt.to_period("M").astype(str)
    df["Order Quarter"] = df["Order Date"].dt.quarter
    df["Order Weekday"] = df["Order Date"].dt.day_name()

    df["Shipping Days"] = (df["Ship Date"] - df["Order Date"]).dt.days

    # Avoid divide-by-zero issues
    df["Profit Margin (%)"] = np.where(
        df["Sales"] != 0, (df["Profit"] / df["Sales"]) * 100, 0
    )

    df["Average Order Value"] = df["Sales"] / df["Quantity"].replace(0, 1)

    df["Is Profitable"] = df["Profit"] > 0

    return df


def clean_pipeline(input_path: str, output_path: str = None) -> pd.DataFrame:
    """Run the full cleaning + feature engineering pipeline end-to-end."""
    df = load_raw_data(input_path)
    print(f"Loaded {len(df)} raw rows.")

    df = handle_missing_values(df)
    df = remove_duplicates(df)
    df = convert_data_types(df)
    df = detect_outliers(df, column="Sales")
    df = engineer_features(df)

    print(f"Final cleaned dataset: {len(df)} rows, {df.shape[1]} columns.")

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"Saved cleaned dataset to {output_path}")

    return df


if __name__ == "__main__":
    clean_pipeline(
        input_path="../data/sales_data.csv",
        output_path="../data/sales_data_cleaned.csv",
    )
