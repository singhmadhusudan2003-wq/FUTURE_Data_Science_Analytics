# Step-by-Step Import Guide
## Building `Marketing_Funnel.pbix` from this Power BI Project package

### Why there's no `.pbix` file in this ZIP

A `.pbix` is not a plain document format like `.docx` or `.xlsx` — the data
model portion is serialized with Power BI's proprietary in-memory analytics
engine (the same VertiPaq/xVelocity engine used by Analysis Services), which
only Power BI Desktop itself can write. There is no supported SDK, library,
or command-line tool that can author that binary outside of the Desktop
application, so it genuinely cannot be produced by this environment. What
**can** be produced — and is included here — is everything that goes *into*
building the `.pbix`, pre-written so assembly takes about 10–15 minutes of
copy/paste in Power BI Desktop rather than hours of manual work:

```
dashboard/
├── README.md                          ← Quick overview (this folder)
└── PowerBI_Project/
    ├── PowerQuery_M.pq                ← Full Power Query (M) scripts
    ├── DAX_Measures.dax               ← Every DAX measure needed (30+)
    ├── Theme.json                     ← Real, importable Power BI theme
    ├── Visual_Layout_Specification.md ← Exact page/visual layout, pixel positions
    └── Import_Instructions.md         ← This file
```

---

### Step 1 — Get the data into Power BI Desktop

1. Open **Power BI Desktop** (free download from powerbi.microsoft.com).
2. **Home → Get Data → Blank Query**.
3. **Home → Advanced Editor**, delete the placeholder text, and paste in the
   **first query** (`fct_MarketingFunnel`) from `PowerQuery_M.pq`.
   - Update the file path inside `File.Contents("C:\Path\To\...")` to point
     to your local copy of `data/marketing_funnel.csv`.
4. Click **Done**, then rename the query (right panel) to `fct_MarketingFunnel`.
5. Repeat steps 2–4 for the **second query** (`dim_Date`) in the same file,
   naming it `dim_Date`.
6. **Home → Close & Apply**.

### Step 2 — Build the data model

1. Switch to **Model view** (left rail).
2. Drag `dim_Date[Date]` onto `fct_MarketingFunnel[Date]` to create a
   relationship (Cardinality: One-to-Many, direction: Single).
3. Right-click `dim_Date` → **Mark as date table** → select `Date` column.
4. (Optional) Hide `fct_MarketingFunnel[Date]` in Report view so users only
   filter by `dim_Date`.

### Step 3 — Add the FunnelStages helper table

1. **Modeling → New table**.
2. Paste the `FunnelStages = UNION(...)` calculated table formula found at
   the bottom of `DAX_Measures.dax`.
3. This table powers the native Funnel visual and the `Biggest Drop-off
   Stage` measure.

### Step 4 — Add every DAX measure

1. Select `fct_MarketingFunnel` in the Fields pane.
2. **Table tools → New measure**.
3. Open `DAX_Measures.dax` and paste each measure block one at a time
   (the text before `=` on the first line is the measure name — use that
   exact name when Power BI prompts, or paste the whole block directly into
   the formula bar, which Power BI accepts as `Name = Expression`).
4. There are ~35 measures across 8 sections: Core KPIs, Funnel, Time
   Intelligence, Channel, Campaign, ROI, Conversion Rate, and Formatting
   helpers. Add all of them — later visuals reference many of them.
5. Organize into a display folder: select all new measures → **Modeling →
   Display folder** → type `_Measures`.

### Step 5 — Apply the theme

1. **View → Themes → Browse for themes**.
2. Select `Theme.json` from this folder.
3. All new visuals will now inherit the dark theme (backgrounds, data
   colors, fonts) automatically.

### Step 6 — Build the report pages

Follow `Visual_Layout_Specification.md` exactly — it lists every visual,
its exact field wells (category/values/legend), and its pixel position for
four pages:
1. Executive Overview (KPI cards, Funnel, Drop-off, Revenue Trend)
2. Channel & Campaign Performance
3. ROI & Conversion Deep-Dive
4. Geography & Audience (optional)

Use **Format pane → General → Properties** to type in the exact X/Y/Width/
Height for each visual for a pixel-perfect layout, or eyeball it against the
grid — either works.

### Step 7 — Add slicers

Add four slicers per the layout spec: **Date** (`dim_Date[Date]`),
**Marketing Channel**, **Campaign**, **Country** — all from
`fct_MarketingFunnel`. Select all slicers → right-click → **Sync slicers**
to apply them across every page.

### Step 8 — Add bookmarks (optional but included in spec)

Create the 4 bookmarks listed in `Visual_Layout_Specification.md`
(**View → Bookmarks → Add**) and, optionally, a Bookmark Navigator button
group on page 1.

### Step 9 — Save

**File → Save As** → `Marketing_Funnel.pbix` → save into this `dashboard/`
folder, replacing this instructions-based package with the finished file for
your submission.

---

### Estimated time to complete

| Step | Time |
|---|---|
| Load data + build model | 3 min |
| Add all DAX measures (paste job) | 5 min |
| Apply theme | 1 min |
| Build 3–4 report pages from the spec | 8–12 min |
| Slicers + bookmarks | 3 min |
| **Total** | **~20–25 min** |

Every measure, every M query, and every visual's field wells are fully
specified — no guesswork or blank-canvas design decisions are required.
