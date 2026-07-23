"""
dashboard.py
------------
Builds a self-contained, interactive HTML dashboard for the Business
Sales Performance Analytics project using Plotly.js (loaded from CDN
in the browser at view-time, so no local Plotly Python dependency is
required to *generate* the file).

The dashboard includes:
  - KPI summary cards
  - Region / Category / Segment filters
  - Interactive revenue & profit trend charts
  - Category, region, and top-product breakdowns
  - A simple top navigation bar between dashboard sections

Run:
    python dashboard.py
Output:
    ../dashboard/interactive_dashboard.html

Author: Future Interns - Data Science & Analytics Track
"""

import json
from pathlib import Path

import pandas as pd

from data_cleaning import clean_pipeline
from analysis import calculate_kpis


def _row_level_records(df: pd.DataFrame) -> list:
    """Build a lightweight row-level dataset (only the fields the dashboard
    needs) so filters can be applied client-side in the browser."""
    cols = ["Order Year-Month", "Order Year", "Region", "Category",
            "Sub-Category", "Segment", "Sales", "Profit", "Quantity",
            "Product Name", "State"]
    small = df[cols].copy()
    small["Order Year-Month"] = small["Order Year-Month"].astype(str)
    return small.to_dict(orient="records")


def build_dashboard(df: pd.DataFrame, output_path: str):
    kpis = calculate_kpis(df)
    records = _row_level_records(df)

    regions = sorted(df["Region"].dropna().unique().tolist())
    categories = sorted(df["Category"].dropna().unique().tolist())
    segments = sorted(df["Segment"].dropna().unique().tolist())

    data_json = json.dumps(records)
    kpis_json = json.dumps(kpis, default=str)
    regions_json = json.dumps(regions)
    categories_json = json.dumps(categories)
    segments_json = json.dumps(segments)

    html = HTML_TEMPLATE.format(
        data_json=data_json,
        kpis_json=kpis_json,
        regions_json=regions_json,
        categories_json=categories_json,
        segments_json=segments_json,
    )

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Dashboard written to {output_path}")


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Future Interns | Business Sales Performance Dashboard</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
  :root {{
    --primary: #2563EB;
    --secondary: #F59E0B;
    --bg: #0F172A;
    --panel: #1E293B;
    --text: #E2E8F0;
    --muted: #94A3B8;
    --good: #22C55E;
    --bad: #EF4444;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; font-family: 'Segoe UI', Roboto, Arial, sans-serif;
    background: var(--bg); color: var(--text);
  }}
  header {{
    background: linear-gradient(135deg, #1D4ED8, #7C3AED);
    padding: 22px 32px; display: flex; align-items: center; justify-content: space-between;
    flex-wrap: wrap; gap: 12px;
  }}
  header h1 {{ margin: 0; font-size: 22px; }}
  header p {{ margin: 4px 0 0; color: #E0E7FF; font-size: 13px; }}
  nav {{
    display: flex; gap: 6px; background: var(--panel); padding: 10px 32px;
    border-bottom: 1px solid #334155; flex-wrap: wrap;
  }}
  nav button {{
    background: transparent; border: 1px solid #334155; color: var(--text);
    padding: 8px 16px; border-radius: 20px; cursor: pointer; font-size: 13px;
  }}
  nav button.active {{ background: var(--primary); border-color: var(--primary); }}
  .filters {{
    display: flex; gap: 16px; padding: 16px 32px; background: var(--panel);
    flex-wrap: wrap; align-items: center; border-bottom: 1px solid #334155;
  }}
  .filters label {{ font-size: 12px; color: var(--muted); display: block; margin-bottom: 4px; }}
  .filters select {{
    background: #0F172A; color: var(--text); border: 1px solid #334155;
    padding: 8px 10px; border-radius: 8px; min-width: 160px;
  }}
  .filters button.reset {{
    background: var(--secondary); border: none; color: #1E293B; font-weight: 600;
    padding: 9px 16px; border-radius: 8px; cursor: pointer; align-self: flex-end;
  }}
  main {{ padding: 24px 32px 48px; }}
  .kpi-grid {{
    display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
    gap: 16px; margin-bottom: 28px;
  }}
  .kpi-card {{
    background: var(--panel); border: 1px solid #334155; border-radius: 14px;
    padding: 18px; position: relative; overflow: hidden;
  }}
  .kpi-card::before {{
    content: ""; position: absolute; top: 0; left: 0; height: 4px; width: 100%;
    background: var(--primary);
  }}
  .kpi-card h3 {{ margin: 0; font-size: 12px; color: var(--muted); text-transform: uppercase; letter-spacing: .04em; }}
  .kpi-card .value {{ font-size: 24px; font-weight: 700; margin-top: 8px; }}
  .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }}
  .grid-3 {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-bottom: 20px; }}
  @media (max-width: 900px) {{ .grid-2, .grid-3 {{ grid-template-columns: 1fr; }} }}
  .card {{
    background: var(--panel); border: 1px solid #334155; border-radius: 14px; padding: 14px;
  }}
  .card h2 {{ font-size: 14px; margin: 4px 8px 0; color: var(--text); }}
  .section {{ display: none; }}
  .section.active {{ display: block; }}
  footer {{ text-align: center; color: var(--muted); font-size: 12px; padding: 24px; }}
</style>
</head>
<body>

<header>
  <div>
    <h1>Business Sales Performance Dashboard</h1>
    <p>Future Interns &middot; Data Science &amp; Analytics Track &middot; FUTURE_DS_01</p>
  </div>
  <div style="font-size:12px;color:#E0E7FF;">Generated automatically from sales_data_cleaned.csv</div>
</header>

<nav>
  <button class="nav-btn active" data-target="overview">Overview</button>
  <button class="nav-btn" data-target="regional">Regional &amp; Category</button>
  <button class="nav-btn" data-target="products">Products &amp; Segments</button>
</nav>

<div class="filters">
  <div>
    <label>Region</label>
    <select id="regionFilter"><option value="">All Regions</option></select>
  </div>
  <div>
    <label>Category</label>
    <select id="categoryFilter"><option value="">All Categories</option></select>
  </div>
  <div>
    <label>Segment</label>
    <select id="segmentFilter"><option value="">All Segments</option></select>
  </div>
  <button class="reset" onclick="resetFilters()">Reset Filters</button>
</div>

<main>
  <div id="kpiGrid" class="kpi-grid"></div>

  <div id="overview" class="section active">
    <div class="grid-2">
      <div class="card"><h2>Monthly Revenue Trend</h2><div id="chartRevenueTrend"></div></div>
      <div class="card"><h2>Monthly Profit Trend</h2><div id="chartProfitTrend"></div></div>
    </div>
    <div class="grid-2">
      <div class="card"><h2>Year-wise Revenue Growth</h2><div id="chartYearGrowth"></div></div>
      <div class="card"><h2>Sales Distribution</h2><div id="chartSalesDist"></div></div>
    </div>
  </div>

  <div id="regional" class="section">
    <div class="grid-2">
      <div class="card"><h2>Sales by Region</h2><div id="chartRegionSales"></div></div>
      <div class="card"><h2>Sales by Category</h2><div id="chartCategorySales"></div></div>
    </div>
    <div class="grid-2">
      <div class="card"><h2>Profit by Region</h2><div id="chartRegionProfit"></div></div>
      <div class="card"><h2>Top 15 States by Sales</h2><div id="chartStateSales"></div></div>
    </div>
  </div>

  <div id="products" class="section">
    <div class="grid-2">
      <div class="card"><h2>Top 10 Products by Sales</h2><div id="chartTopProducts"></div></div>
      <div class="card"><h2>Sales Share by Segment</h2><div id="chartSegmentShare"></div></div>
    </div>
    <div class="grid-2">
      <div class="card"><h2>Sub-Category Performance</h2><div id="chartSubCategory"></div></div>
      <div class="card"><h2>Quantity Sold by Category</h2><div id="chartQuantity"></div></div>
    </div>
  </div>
</main>

<footer>Future Interns &middot; Data Science &amp; Analytics Internship &middot; Business Sales Performance Analytics (FUTURE_DS_01)</footer>

<script>
const RAW_DATA = {data_json};
const BASE_KPIS = {kpis_json};
const REGIONS = {regions_json};
const CATEGORIES = {categories_json};
const SEGMENTS = {segments_json};

const plotlyLayoutBase = {{
  paper_bgcolor: "#1E293B", plot_bgcolor: "#1E293B",
  font: {{ color: "#E2E8F0", size: 11 }},
  margin: {{ t: 10, l: 50, r: 20, b: 60 }},
}};

function populateSelect(id, options) {{
  const sel = document.getElementById(id);
  options.forEach(o => {{
    const opt = document.createElement("option");
    opt.value = o; opt.textContent = o;
    sel.appendChild(opt);
  }});
}}
populateSelect("regionFilter", REGIONS);
populateSelect("categoryFilter", CATEGORIES);
populateSelect("segmentFilter", SEGMENTS);

function currentFilters() {{
  return {{
    region: document.getElementById("regionFilter").value,
    category: document.getElementById("categoryFilter").value,
    segment: document.getElementById("segmentFilter").value,
  }};
}}

function filteredData() {{
  const f = currentFilters();
  return RAW_DATA.filter(r =>
    (!f.region || r.Region === f.region) &&
    (!f.category || r.Category === f.category) &&
    (!f.segment || r.Segment === f.segment)
  );
}}

function sumBy(rows, keyField, valField) {{
  const map = {{}};
  rows.forEach(r => {{
    const k = r[keyField];
    map[k] = (map[k] || 0) + (r[valField] || 0);
  }});
  return map;
}}

function sortedEntries(map, desc = true) {{
  return Object.entries(map).sort((a, b) => desc ? b[1] - a[1] : a[1] - b[1]);
}}

function renderKpis(rows) {{
  const totalSales = rows.reduce((s, r) => s + r.Sales, 0);
  const totalProfit = rows.reduce((s, r) => s + r.Profit, 0);
  const orders = rows.length;
  const aov = orders ? totalSales / orders : 0;
  const margin = totalSales ? (totalProfit / totalSales) * 100 : 0;

  const cards = [
    ["Total Revenue", "$" + totalSales.toLocaleString(undefined, {{maximumFractionDigits: 0}})],
    ["Total Profit", "$" + totalProfit.toLocaleString(undefined, {{maximumFractionDigits: 0}})],
    ["Total Orders", orders.toLocaleString()],
    ["Avg Order Value", "$" + aov.toLocaleString(undefined, {{maximumFractionDigits: 0}})],
    ["Profit Margin", margin.toFixed(1) + "%"],
    ["Best Region", BASE_KPIS["Best Region"]],
  ];

  const grid = document.getElementById("kpiGrid");
  grid.innerHTML = "";
  cards.forEach(([label, value]) => {{
    const div = document.createElement("div");
    div.className = "kpi-card";
    div.innerHTML = `<h3>${{label}}</h3><div class="value">${{value}}</div>`;
    grid.appendChild(div);
  }});
}}

function renderCharts() {{
  const rows = filteredData();
  renderKpis(rows);

  // Monthly revenue & profit trend
  const monthMap = {{}};
  rows.forEach(r => {{
    const k = r["Order Year-Month"];
    if (!monthMap[k]) monthMap[k] = {{ sales: 0, profit: 0 }};
    monthMap[k].sales += r.Sales;
    monthMap[k].profit += r.Profit;
  }});
  const months = Object.keys(monthMap).sort();
  Plotly.newPlot("chartRevenueTrend", [{{
    x: months, y: months.map(m => monthMap[m].sales),
    type: "scatter", mode: "lines+markers", line: {{ color: "#2563EB", width: 2 }},
    fill: "tozeroy", fillcolor: "rgba(37,99,235,0.15)"
  }}], {{...plotlyLayoutBase}}, {{displayModeBar: false, responsive: true}});

  Plotly.newPlot("chartProfitTrend", [{{
    x: months, y: months.map(m => monthMap[m].profit),
    type: "bar", marker: {{ color: months.map(m => monthMap[m].profit >= 0 ? "#22C55E" : "#EF4444") }}
  }}], {{...plotlyLayoutBase}}, {{displayModeBar: false, responsive: true}});

  // Year growth
  const yearMap = sumBy(rows, "Order Year", "Sales");
  const years = Object.keys(yearMap).sort();
  Plotly.newPlot("chartYearGrowth", [{{
    x: years, y: years.map(y => yearMap[y]), type: "bar", marker: {{ color: "#7C3AED" }}
  }}], {{...plotlyLayoutBase}}, {{displayModeBar: false, responsive: true}});

  // Sales distribution (histogram)
  Plotly.newPlot("chartSalesDist", [{{
    x: rows.map(r => r.Sales), type: "histogram", marker: {{ color: "#F59E0B" }}, nbinsx: 40
  }}], {{...plotlyLayoutBase}}, {{displayModeBar: false, responsive: true}});

  // Region sales / profit
  const regionSales = sortedEntries(sumBy(rows, "Region", "Sales"));
  Plotly.newPlot("chartRegionSales", [{{
    x: regionSales.map(e => e[0]), y: regionSales.map(e => e[1]), type: "bar", marker: {{ color: "#2563EB" }}
  }}], {{...plotlyLayoutBase}}, {{displayModeBar: false, responsive: true}});

  const regionProfit = sortedEntries(sumBy(rows, "Region", "Profit"));
  Plotly.newPlot("chartRegionProfit", [{{
    x: regionProfit.map(e => e[0]), y: regionProfit.map(e => e[1]), type: "bar",
    marker: {{ color: regionProfit.map(e => e[1] >= 0 ? "#22C55E" : "#EF4444") }}
  }}], {{...plotlyLayoutBase}}, {{displayModeBar: false, responsive: true}});

  // Category sales
  const catSales = sortedEntries(sumBy(rows, "Category", "Sales"));
  Plotly.newPlot("chartCategorySales", [{{
    y: catSales.map(e => e[0]), x: catSales.map(e => e[1]), type: "bar", orientation: "h",
    marker: {{ color: "#0EA5E9" }}
  }}], {{...plotlyLayoutBase, margin: {{t:10,l:120,r:20,b:40}}}}, {{displayModeBar: false, responsive: true}});

  // Top states
  const stateSales = sortedEntries(sumBy(rows, "State", "Sales")).slice(0, 15);
  Plotly.newPlot("chartStateSales", [{{
    y: stateSales.map(e => e[0]), x: stateSales.map(e => e[1]), type: "bar", orientation: "h",
    marker: {{ color: "#38BDF8" }}
  }}], {{...plotlyLayoutBase, margin: {{t:10,l:140,r:20,b:40}}}}, {{displayModeBar: false, responsive: true}});

  // Top products
  const prodSales = sortedEntries(sumBy(rows, "Product Name", "Sales")).slice(0, 10);
  Plotly.newPlot("chartTopProducts", [{{
    y: prodSales.map(e => e[0]), x: prodSales.map(e => e[1]), type: "bar", orientation: "h",
    marker: {{ color: "#A78BFA" }}
  }}], {{...plotlyLayoutBase, margin: {{t:10,l:180,r:20,b:40}}}}, {{displayModeBar: false, responsive: true}});

  // Segment share
  const segSales = sumBy(rows, "Segment", "Sales");
  Plotly.newPlot("chartSegmentShare", [{{
    labels: Object.keys(segSales), values: Object.values(segSales), type: "pie", hole: 0.45,
    marker: {{ colors: ["#2563EB", "#F59E0B", "#22C55E"] }}
  }}], {{...plotlyLayoutBase}}, {{displayModeBar: false, responsive: true}});

  // Sub-category performance
  const subCatSales = sortedEntries(sumBy(rows, "Sub-Category", "Sales")).slice(0, 12);
  Plotly.newPlot("chartSubCategory", [{{
    y: subCatSales.map(e => e[0]), x: subCatSales.map(e => e[1]), type: "bar", orientation: "h",
    marker: {{ color: "#F472B6" }}
  }}], {{...plotlyLayoutBase, margin: {{t:10,l:140,r:20,b:40}}}}, {{displayModeBar: false, responsive: true}});

  // Quantity by category
  const qty = sortedEntries(sumBy(rows, "Category", "Quantity"));
  Plotly.newPlot("chartQuantity", [{{
    x: qty.map(e => e[0]), y: qty.map(e => e[1]), type: "bar", marker: {{ color: "#FB923C" }}
  }}], {{...plotlyLayoutBase}}, {{displayModeBar: false, responsive: true}});
}}

function resetFilters() {{
  document.getElementById("regionFilter").value = "";
  document.getElementById("categoryFilter").value = "";
  document.getElementById("segmentFilter").value = "";
  renderCharts();
}}

document.getElementById("regionFilter").addEventListener("change", renderCharts);
document.getElementById("categoryFilter").addEventListener("change", renderCharts);
document.getElementById("segmentFilter").addEventListener("change", renderCharts);

document.querySelectorAll(".nav-btn").forEach(btn => {{
  btn.addEventListener("click", () => {{
    document.querySelectorAll(".nav-btn").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".section").forEach(s => s.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(btn.dataset.target).classList.add("active");
    window.dispatchEvent(new Event("resize"));
  }});
}});

renderCharts();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    data = clean_pipeline("../data/sales_data.csv")
    build_dashboard(data, "../dashboard/interactive_dashboard.html")
