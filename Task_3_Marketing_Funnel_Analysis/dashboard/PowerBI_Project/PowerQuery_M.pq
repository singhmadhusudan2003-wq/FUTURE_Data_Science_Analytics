// ============================================================================
// Power Query M Script — Marketing Funnel & Conversion Performance Analysis
// ============================================================================
// HOW TO USE:
//   Power BI Desktop → Home → Transform Data → Home → New Source → Blank Query
//   → Advanced Editor → paste the query below → Done → Close & Apply.
//   Repeat for each of the 3 queries in this file (fct_MarketingFunnel,
//   dim_Date, and the two "Fix Data Types" steps are already embedded).
//
//   Alternatively: Get Data → Text/CSV → point to data/marketing_funnel.csv,
//   then replace the auto-generated steps with the ones below (paste into
//   the Advanced Editor) to get identical typed columns and derived fields.
// ============================================================================


// ----------------------------------------------------------------------------
// QUERY 1: fct_MarketingFunnel  (main fact table)
// ----------------------------------------------------------------------------
let
    Source = Csv.Document(
        File.Contents("C:\Path\To\Marketing_Funnel_Analysis\data\marketing_funnel.csv"),
        [Delimiter=",", Columns=19, Encoding=65001, QuoteStyle=QuoteStyle.Csv]
    ),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),

    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers", {
        {"Date", type date},
        {"Campaign", type text},
        {"Marketing Channel", type text},
        {"Impressions", Int64.Type},
        {"Clicks", Int64.Type},
        {"CTR", type number},
        {"Landing Page Visits", Int64.Type},
        {"Leads", Int64.Type},
        {"Qualified Leads", Int64.Type},
        {"Customers", Int64.Type},
        {"Conversion Rate", type number},
        {"Revenue", type number},
        {"Cost", type number},
        {"ROI", type number},
        {"Country", type text},
        {"Device", type text},
        {"Age Group", type text},
        {"Gender", type text},
        {"Campaign Type", type text}
    }),

    // --- Derived / helper columns used by DAX measures & slicers ---
    #"Added Profit" = Table.AddColumn(#"Changed Type", "Profit", each [Revenue] - [Cost], type number),

    #"Added Click_to_Visit_Rate" = Table.AddColumn(#"Added Profit", "Click to Visit Rate",
        each if [Clicks] = 0 then 0 else [Landing Page Visits] / [Clicks], type number),

    #"Added Visit_to_Lead_Rate" = Table.AddColumn(#"Added Click_to_Visit_Rate", "Visit to Lead Rate",
        each if [Landing Page Visits] = 0 then 0 else [Leads] / [Landing Page Visits], type number),

    #"Added Lead_to_Qualified_Rate" = Table.AddColumn(#"Added Visit_to_Lead_Rate", "Lead to Qualified Rate",
        each if [Leads] = 0 then 0 else [Qualified Leads] / [Leads], type number),

    #"Added Qualified_to_Customer_Rate" = Table.AddColumn(#"Added Lead_to_Qualified_Rate", "Qualified to Customer Rate",
        each if [Qualified Leads] = 0 then 0 else [Customers] / [Qualified Leads], type number),

    #"Added Cost_per_Lead" = Table.AddColumn(#"Added Qualified_to_Customer_Rate", "Cost per Lead",
        each if [Leads] = 0 then 0 else [Cost] / [Leads], type number),

    #"Added Avg_Order_Value" = Table.AddColumn(#"Added Cost_per_Lead", "Avg Order Value",
        each if [Customers] = 0 then 0 else [Revenue] / [Customers], type number),

    #"Added Year" = Table.AddColumn(#"Added Avg_Order_Value", "Year", each Date.Year([Date]), Int64.Type),
    #"Added Month" = Table.AddColumn(#"Added Year", "Month", each Date.Month([Date]), Int64.Type),
    #"Added MonthName" = Table.AddColumn(#"Added Month", "MonthName", each Date.ToText([Date], "MMM yyyy"), type text),
    #"Added Quarter" = Table.AddColumn(#"Added MonthName", "Quarter", each "Q" & Number.ToText(Date.QuarterOfYear([Date])) & " " & Number.ToText(Date.Year([Date])), type text),
    #"Added Weekday" = Table.AddColumn(#"Added Quarter", "Weekday", each Date.DayOfWeekName([Date]), type text),

    #"Reordered Columns" = Table.ReorderColumns(#"Added Weekday", {
        "Date", "Year", "Month", "MonthName", "Quarter", "Weekday",
        "Campaign", "Campaign Type", "Marketing Channel",
        "Impressions", "Clicks", "CTR", "Landing Page Visits",
        "Leads", "Qualified Leads", "Customers",
        "Conversion Rate", "Revenue", "Cost", "Profit", "ROI",
        "Click to Visit Rate", "Visit to Lead Rate", "Lead to Qualified Rate",
        "Qualified to Customer Rate", "Cost per Lead", "Avg Order Value",
        "Country", "Device", "Age Group", "Gender"
    })
in
    #"Reordered Columns"


// ----------------------------------------------------------------------------
// QUERY 2: dim_Date  (standalone date dimension table — mark as "Date table"
// in Power BI: Table tools → Mark as Date Table → column "Date")
// ----------------------------------------------------------------------------
let
    StartDate = #date(2024, 1, 1),
    EndDate = #date(2025, 12, 31),
    DayCount = Duration.Days(EndDate - StartDate) + 1,
    DateList = List.Dates(StartDate, DayCount, #duration(1, 0, 0, 0)),
    #"Converted to Table" = Table.FromList(DateList, Splitter.SplitByNothing(), {"Date"}),
    #"Changed Type" = Table.TransformColumnTypes(#"Converted to Table", {{"Date", type date}}),
    #"Added Year" = Table.AddColumn(#"Changed Type", "Year", each Date.Year([Date]), Int64.Type),
    #"Added Quarter" = Table.AddColumn(#"Added Year", "Quarter", each "Q" & Number.ToText(Date.QuarterOfYear([Date])) & " " & Number.ToText(Date.Year([Date])), type text),
    #"Added Month" = Table.AddColumn(#"Added Quarter", "Month", each Date.Month([Date]), Int64.Type),
    #"Added MonthName" = Table.AddColumn(#"Added Month", "MonthName", each Date.ToText([Date], "MMM yyyy"), type text),
    #"Added MonthNameShort" = Table.AddColumn(#"Added MonthName", "MonthShort", each Date.ToText([Date], "MMM"), type text),
    #"Added Weekday" = Table.AddColumn(#"Added MonthNameShort", "Weekday", each Date.DayOfWeekName([Date]), type text),
    #"Added WeekdayNum" = Table.AddColumn(#"Added Weekday", "WeekdayNum", each Date.DayOfWeek([Date], Day.Monday) + 1, Int64.Type),
    #"Added IsWeekend" = Table.AddColumn(#"Added WeekdayNum", "IsWeekend", each Date.DayOfWeek([Date], Day.Monday) >= 5, type logical)
in
    #"Added IsWeekend"


// ----------------------------------------------------------------------------
// After loading both queries:
//   1. Go to Model view.
//   2. Create a relationship: dim_Date[Date]  (1)  →  (*)  fct_MarketingFunnel[Date]
//      Cardinality: One-to-Many, Cross filter direction: Single.
//   3. Right-click dim_Date → "Mark as date table" → choose the Date column.
//   4. Hide fct_MarketingFunnel[Date] from Report View if you want all date
//      slicing to route through dim_Date (optional but recommended).
// ----------------------------------------------------------------------------
