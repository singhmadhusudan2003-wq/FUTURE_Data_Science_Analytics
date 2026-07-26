# Power BI Dashboard

A real `.pbix` binary cannot be authored outside Power BI Desktop (see
`PowerBI_Project/Import_Instructions.md` for why). Instead, this folder
contains a **complete, ready-to-assemble Power BI project package** — every
line of M code, every DAX measure, a real importable theme file, and an
exact visual-by-visual layout spec — so building the final `.pbix` is a
~20-minute copy/paste job in Power BI Desktop rather than a design exercise.

```
PowerBI_Project/
├── PowerQuery_M.pq                 # Data load + transform (M) for fct_MarketingFunnel & dim_Date
├── DAX_Measures.dax                # 35+ measures: KPIs, Funnel, Channel, Campaign, ROI, Conversion Rate
├── Theme.json                      # Real Power BI theme (View → Themes → Browse for themes)
├── Visual_Layout_Specification.md  # Exact page/visual layout with pixel positions & field wells
└── Import_Instructions.md          # Step-by-step assembly guide (start here)
```

**Start with `PowerBI_Project/Import_Instructions.md`.**

Covers, exactly as required:
- KPI Cards (10 measures)
- Funnel Chart (native Funnel visual + drop-off table)
- Revenue Trend (line chart + time-intelligence DAX)
- Channel Performance (bar chart + matrix)
- Campaign Performance (bar chart + scatter)
- ROI Analysis (column chart + status donut)
- Conversion Rate Analysis (stage-by-stage cards + heatmap)
- Slicers: Date, Channel, Campaign, Country (synced across pages)
- Professional dark theme and pixel-level layout
