# 📊 Power BI Dashboard — Build Guide

> **Why is there no `.pbix` file?**
> Power BI Desktop is a Windows application and isn't available in this environment, so a native `.pbix` binary can't be generated here — there is no code path that produces a genuine, openable `.pbix` without the application itself. Instead, this folder includes:
> - `Customer_Retention_Dashboard.html` — a fully working, **interactive** dashboard with real filters (Contract, Internet Service, Payment Method, Senior Citizen, Tenure Group) that recompute every KPI and chart live in your browser, plus dedicated Cohort Analysis, Customer Lifetime Metrics, and Churn/Retention Trend sections.
> - `../images/dashboard_preview.png` — a PNG screenshot of the KPI/filter section, ready to drop into a README or LinkedIn post.
> - This guide — copy-paste DAX measures and a step-by-step layout so you (or anyone with Power BI Desktop, free to install) can rebuild the exact same dashboard as a real `.pbix` in about 15–20 minutes.

---

## 1. Load the Data

1. Open **Power BI Desktop** → **Get Data** → **Text/CSV**.
2. Select `data/Telco_Customer_Churn_Cleaned.csv` (the cleaned + feature-engineered dataset produced by the notebook — includes `TenureGroup`, `ChargeGroup`, `NumAddOnServices`, `ChurnFlag`, `CLV_Estimate`).
3. Click **Load**.
4. In **Power Query Editor**, confirm data types: `tenure` → Whole Number, `MonthlyCharges`/`TotalCharges`/`CLV_Estimate` → Decimal Number, `ChurnFlag` → Whole Number, everything else → Text.
5. Optionally also load `reports/clv_by_contract.csv`, `reports/risk_segments.csv`, `reports/retention_matrix.csv`, and `reports/cohort_quarterly_summary.csv` as separate tables — these are pre-aggregated and make the Cohort/CLV/Trend visuals trivial to build without recreating the derivation logic in DAX.

## 2. Create Core DAX Measures

Add a new table of measures (Modeling → New Measure) using the following:

```DAX
Total Customers = COUNTROWS('Telco_Customer_Churn_Cleaned')

Total Churned = CALCULATE([Total Customers], 'Telco_Customer_Churn_Cleaned'[Churn] = "Yes")

Active Customers = [Total Customers] - [Total Churned]

Churn Rate % = DIVIDE([Total Churned], [Total Customers], 0)

Retention Rate % = 1 - [Churn Rate %]

Avg Monthly Charges = AVERAGE('Telco_Customer_Churn_Cleaned'[MonthlyCharges])

Avg Tenure (Months) = AVERAGE('Telco_Customer_Churn_Cleaned'[tenure])

Avg Total Charges = AVERAGE('Telco_Customer_Churn_Cleaned'[TotalCharges])

Monthly Revenue Lost = CALCULATE(SUM('Telco_Customer_Churn_Cleaned'[MonthlyCharges]), 'Telco_Customer_Churn_Cleaned'[Churn] = "Yes")

Total Monthly Revenue = SUM('Telco_Customer_Churn_Cleaned'[MonthlyCharges])

High Risk Customers =
CALCULATE(
    [Total Customers],
    'Telco_Customer_Churn_Cleaned'[Contract] = "Month-to-month",
    'Telco_Customer_Churn_Cleaned'[tenure] <= 12,
    'Telco_Customer_Churn_Cleaned'[PaymentMethod] = "Electronic check"
)

Avg Customer Lifetime (Churned) =
CALCULATE(AVERAGE('Telco_Customer_Churn_Cleaned'[tenure]), 'Telco_Customer_Churn_Cleaned'[Churn] = "Yes")

Avg CLV = AVERAGE('Telco_Customer_Churn_Cleaned'[CLV_Estimate])
```

## 3. Cohort Analysis Measures

If you loaded `retention_matrix.csv` / `cohort_quarterly_summary.csv` as separate tables, no extra DAX is needed — just drag `Cohort`, `Month 0`...`Month 24` (or `AcquisitionQuarter`, `RetentionRate`) straight into a matrix/heatmap visual (conditional formatting → background color, on the retention % fields) for an instant retention-matrix heatmap.

To derive acquisition month natively in Power Query instead, add a custom column:
```
AcquisitionMonth = Date.AddMonths(#date(2024,1,1), - [tenure])
```
then build a `AcquisitionQuarter` column with `Date.QuarterOfYear` / `Date.Year`, and group by it for cohort sizing and retention %.

## 4. Customer Lifetime Value Measures

If using `clv_by_contract.csv` directly: drag `Contract`, `EstimatedCLV`, `AvgLifetimeMonths`, `ChurnRate` into a clustered column chart. Otherwise, compute inline:

```DAX
CLV by Contract =
AVERAGEX(
    VALUES('Telco_Customer_Churn_Cleaned'[Contract]),
    CALCULATE([Avg Monthly Charges] * [Avg Customer Lifetime (Churned)])
)
```

## 5. Churn Trend / Risk Segment Measures

If using `risk_segments.csv`: drag `RiskTier`, `ActualChurnRate`, `CustomerCount`, `RevenueAtRisk` into a bar chart, sorted by a custom Risk Tier order (Very High → Low).

To build the risk score natively, add a Power Query custom column mirroring the notebook's `risk_score()` function (contract + tenure + payment method + service-gap point system), then bucket into `RiskTier` with a nested `if`/`switch` column.

## 6. Dashboard Layout (multi-page, matches the HTML dashboard)

### Page 1 — Overview (KPIs + core segments)
| Zone | Visual | Fields |
|---|---|---|
| Top strip | 6× **KPI Card** | Total Customers, Churn Rate %, Retention Rate %, Avg Monthly Charges, Monthly Revenue Lost, Avg Tenure |
| Donut | **Donut chart** | Legend = `Churn`, Values = `Total Customers` |
| Contract | **Stacked column** | Axis = `Contract`, Legend = `Churn`, Values = Count (% of axis) |
| Internet | **Clustered column** | Axis = `InternetService`, Values = `Total Customers` |
| Tenure | **Line chart** | Axis = `TenureGroup`, Values = `Churn Rate %` |
| Payment | **Horizontal bar** | Axis = `PaymentMethod`, Values = `Churn Rate %`, sorted descending |
| Right rail | **Slicers** | `Contract`, `InternetService`, `SeniorCitizen`, `PaymentMethod`, `TenureGroup` |

### Page 2 — Cohort Analysis
- **Matrix visual** with conditional-formatting heatmap: rows = `Cohort` (quarter), columns = `Month 0`...`Month 24`, values = retention %.
- **Heatmap-style matrix**: rows = Acquisition Year, columns = Acquisition Month, values = retention %.

### Page 3 — Customer Lifetime Metrics
- **Clustered column**: `Contract` × `EstimatedCLV`.
- **Clustered column**: `Contract` × `AvgLifetimeMonths`.
- **Bar chart**: `RiskTier` × `ActualChurnRate`, with `RevenueAtRisk` as a tooltip/secondary measure.

### Page 4 — Churn Trend & Retention Trend
- **Combo chart**: Axis = Acquisition Month, Columns = Cohort Size, Line = Churn Rate % (most recent 24 months).
- **Line chart**: Axis = exact `tenure` month, Values = rolling Churn Rate %.
- **Area chart**: Axis = months since acquisition (0–72), Values = % retained (pooled survival curve).

## 7. Theme

Apply a custom theme (View → Themes → Browse for themes) using this JSON, which matches the palette used in the HTML dashboard:

```json
{
  "name": "Churn Analysis Dark",
  "dataColors": ["#00D4B4", "#FF5C7A", "#5B8DEF", "#FFB84D", "#8A94A6", "#C7CEDA"],
  "background": "#1B2430",
  "foreground": "#E8ECF1",
  "tableAccent": "#00D4B4"
}
```

## 8. Publish & Export

- **File → Export → PDF** for a shareable static copy.
- **File → Save As** → `Customer_Retention_Dashboard.pbix` and drop it into this folder to complete the project structure exactly as specified.
- Optionally publish to the Power BI Service and embed the live report link in the README.

---
Once rebuilt, you can swap this guide's screenshot reference for your own export of the live `.pbix` for full authenticity.
