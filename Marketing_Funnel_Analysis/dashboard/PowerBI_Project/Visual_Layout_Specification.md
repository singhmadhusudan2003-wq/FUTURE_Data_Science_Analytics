# Power BI Visual Layout Specification
## Marketing Funnel & Conversion Performance Analysis

Report canvas: **1280 × 720** (16:9, "Live Page View" default). All positions
below are given as `(x, y, width, height)` in pixels from the top-left corner,
matching what you'd enter in the Power BI **Format pane → General → Properties
(X, Y, Width, Height)** for pixel-perfect placement. Use `View → Gridlines` +
`Snap to grid` while building.

Apply `Theme.json` first (**View → Themes → Browse for themes**) so every new
visual inherits the dark theme automatically.

---

## PAGE 1 — "Executive Overview"

### Header band (0, 0, 1280, 60)
- Text box: "Marketing Funnel & Conversion Performance Analysis" — Segoe UI Semibold 20pt, `#00E5A0`, at (16, 12, 700, 36)
- Image (logo.png) at (1180, 8, 44, 44)

### Slicer bar (0, 64, 1280, 56)
| Slicer | Field | Position (x, y, w, h) | Style |
|---|---|---|---|
| Date | `dim_Date[Date]` | (16, 64, 280, 56) | Between (range slider) |
| Marketing Channel | `fct_MarketingFunnel[Marketing Channel]` | (304, 64, 240, 56) | Dropdown |
| Campaign | `fct_MarketingFunnel[Campaign]` | (552, 64, 240, 56) | Dropdown |
| Country | `fct_MarketingFunnel[Country]` | (800, 64, 240, 56) | Dropdown |
| (optional) Device | `fct_MarketingFunnel[Device]` | (1048, 64, 216, 56) | Dropdown |

> Tip: Select all 4-5 slicers → right-click → **Sync slicers** (Sync visual)
> so the same filters apply across every report page.

### KPI Cards row (0, 128, 1280, 96)
Use **Card** or **Multi-row card** visuals, 10 cards in a 5×2 grid, each
124 px wide with 8 px gutters:

| # | Measure | Position (x, y, w, h) |
|---|---|---|
| 1 | `Total Impressions (Compact)` | (16, 128, 240, 44) |
| 2 | `Total Clicks` | (264, 128, 240, 44) |
| 3 | `Overall CTR %` | (512, 128, 240, 44) |
| 4 | `Total Leads` | (760, 128, 240, 44) |
| 5 | `Total Qualified Leads` | (1008, 128, 256, 44) |
| 6 | `Total Customers` | (16, 180, 240, 44) |
| 7 | `Total Revenue (Compact)` | (264, 180, 240, 44) |
| 8 | `Total Cost` | (512, 180, 240, 44) |
| 9 | `Overall ROI %` | (760, 180, 240, 44) |
| 10 | `Overall Conversion Rate %` | (1008, 180, 256, 44) |

### Funnel Chart (16, 236, 620, 300)
- Visual: **Funnel**
- Category: `FunnelStages[Stage Name]` (sort by `Stage Order` ascending)
- Values: `FunnelStages[Stage Value]`
- Data labels: On, show value + % of first

### Funnel Drop-off Table (652, 236, 612, 300)
- Visual: **Table** or **Clustered bar chart**
- Rows: `FunnelStages[Stage Name]`
- Values: `FunnelStages[Stage Value]`, conditional-formatted drop-off %
  (compute via a measure comparing to `CALCULATE(..., PREVIOUSSTAGE)` or use
  the `Biggest Drop-off Stage` measure in a card underneath)
- Card underneath (652, 546, 300, 40): `Biggest Drop-off Stage` measure

### Revenue Trend (16, 552, 612, 168)
- Visual: **Line chart**
- Axis: `dim_Date[MonthName]` (sorted by `dim_Date[Date]`)
- Values: `Total Revenue`, `Total Cost` (dual line)

---

## PAGE 2 — "Channel & Campaign Performance"

### Slicer bar — same synced slicers as Page 1 (0, 0, 1280, 56)

### Channel Performance — Bar chart (16, 64, 620, 280)
- Visual: **Clustered column chart**
- Axis: `fct_MarketingFunnel[Marketing Channel]`
- Values: `Total Revenue`
- Sort descending by Revenue
- Data colors: theme palette (auto)

### Channel Performance — Matrix table (652, 64, 612, 280)
- Visual: **Table**
- Columns: Marketing Channel, `Channel CTR %`, `Lead to Qualified Rate %`,
  `Qualified to Customer Rate %`, `Channel ROI %`, `Total Revenue`
- Conditional formatting: color scale on `Channel ROI %` (red → green)

### Campaign Performance — Horizontal bar (16, 356, 612, 280)
- Visual: **Clustered bar chart** (horizontal)
- Axis: `fct_MarketingFunnel[Campaign]`
- Values: `Campaign ROI %`
- Top N filter: Top 10 by `Campaign ROI %`

### Campaign Performance — Scatter / ROI bubble (652, 356, 612, 280)
- Visual: **Scatter chart**
- X axis: `Total Cost`
- Y axis: `Campaign ROI %`
- Size: `Total Revenue`
- Legend: `Campaign`

---

## PAGE 3 — "ROI & Conversion Deep-Dive"

### Slicer bar — synced (0, 0, 1280, 56)

### ROI Analysis — Column chart with reference line (16, 64, 620, 260)
- Visual: **Clustered column chart**
- Axis: `Marketing Channel`
- Values: `Channel ROI %`
- Add a constant reference line at 0% (Format → Analytics → Constant line)

### ROI Status — Donut (652, 64, 300, 260)
- Visual: **Donut chart**
- Legend/Category: `ROI Status` measure bucketed via a calculated column, or
  use `Campaign` with `Campaign ROI %` grouped into bins
- Values: Count of campaigns per ROI Status bucket

### Conversion Funnel Rates — Multi-row card (968, 64, 296, 260)
Six stacked cards, one per stage-to-stage conversion:
`Overall CTR %`, `Click to Visit Rate %`, `Visit to Lead Rate %`,
`Lead to Qualified Rate %`, `Qualified to Customer Rate %`,
`Overall Conversion Rate %`

### Conversion Rate Heatmap (16, 340, 612, 280)
- Visual: **Matrix** with conditional formatting (heatmap style), or
  **Azure Maps / Table** substitute if the Heatmap custom visual isn't
  installed
- Rows: `Marketing Channel`
- Columns: `Device`
- Values: `AVERAGE(fct_MarketingFunnel[Conversion Rate])`
- Format → Conditional formatting → Background color → color scale

### Revenue → Channel → Campaign Treemap (652, 340, 612, 280)
- Visual: **Treemap**
- Group: `Marketing Channel`, then `Campaign`
- Values: `Total Revenue`

---

## PAGE 4 — "Geography & Audience" (optional 4th page)

- **Country-wise Revenue**: Filled map or bar chart, Location = `Country`,
  Values = `Total Revenue`
- **Customer Acquisition by Device**: Donut, Legend = `Device`,
  Values = `Total Customers`
- **Customer Distribution by Age Group**: Column chart, Axis = `Age Group`,
  Values = `Total Customers`
- **Marketing Cost by Channel**: Bar chart, Axis = `Marketing Channel`,
  Values = `Total Cost`

---

## Bookmarks (Home tab → View → Bookmarks pane)

| Bookmark | Captures |
|---|---|
| "Default View" | All slicers cleared, Page 1 active |
| "Top Channels" | Marketing Channel slicer = top 3 by revenue (Referral, Google Ads, Email Marketing) |
| "This Quarter" | Date slicer = current quarter |
| "High ROI Campaigns" | Campaign slicer filtered to ROI > 100% |

Add a bookmark navigator button group on Page 1 (Insert → Buttons →
Bookmark, or the Bookmark Navigator visual) so end users can switch views
with one click.

---

## Page-level formatting checklist

- [ ] Canvas background: `#0E1117` (set via Theme.json, already applied)
- [ ] Card/visual background: `#1E2430`–`#161B26`, 12px corner radius
- [ ] All visuals: title on, 13pt Segoe UI Semibold, `#F5F6FA`
- [ ] Consistent 8–16px gutters between visuals (use Format → Align + Distribute)
- [ ] Data colors follow `Theme.json` `dataColors` palette
- [ ] Tooltips: enabled, default report tooltips
- [ ] Mobile layout: Optimize each page for phone view (View → Mobile Layout)
