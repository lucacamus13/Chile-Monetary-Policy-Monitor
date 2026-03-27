# Power BI Data Model

## Objective

Build a business-facing semantic model that transforms the macro pipeline outputs into an executive dashboard for monetary policy monitoring.

## Recommended model type

Use a star-schema-inspired model with one main fact table and a date dimension.

## Tables to import

### 1. `indicators`

Source:
- `data/processed/indicators.csv`

Role:
- Main fact table for Power BI
- Contains KPI-ready analytical outputs

Key fields:
- `date`
- `cpi_yoy`
- `cpi_mom`
- `real_rate`
- `rate_spread`
- `usdclp_change`
- `copper_change`
- `oil_change`
- `inflation_gap`
- `activity_growth`
- `inflation_3m_avg`
- `activity_3m_avg`
- `usdclp_volatility_3m`
- `tpm`
- `fed_funds`
- `usdclp`
- `copper`
- `oil`
- `gdp_or_imacec`
- `unemployment`
- `cpi_chile`
- `cpi_usa`

### 2. `processed_data`

Source:
- `data/processed/processed_data.csv`

Role:
- Secondary fact/support table
- Useful for validation, drill-through, and raw level charting

### 3. `dim_date`

Source:
- Create inside Power BI with DAX or Power Query

Recommended columns:
- `Date`
- `Year`
- `Month Number`
- `Month Name`
- `Quarter`
- `YearMonth`
- `Semester`

## Relationships

Primary relationship:
- `dim_date[Date]` 1-to-many `indicators[date]`

Optional relationship:
- `dim_date[Date]` 1-to-many `processed_data[date]`

Guidelines:
- Keep single-direction filtering from `dim_date` to facts
- Mark `dim_date` as the official date table
- Use `indicators` as the default table for visuals

## Why this model works

This design is simple, robust, and recruiter-friendly because it shows:
- Good semantic modeling discipline
- Separation between calendar logic and facts
- Clean KPI consumption for executive dashboards
- A scalable base for adding more countries or variables later

## Suggested DAX measures

### Core KPI measures

```DAX
Chile CPI YoY = MAX(indicators[cpi_yoy])
TPM = MAX(indicators[tpm])
Fed Funds = MAX(indicators[fed_funds])
Real Rate = MAX(indicators[real_rate])
Rate Spread = MAX(indicators[rate_spread])
USDCLP = MAX(indicators[usdclp])
Copper Price = MAX(indicators[copper])
Oil Price = MAX(indicators[oil])
IMACEC Growth = MAX(indicators[gdp_or_imacec])
Unemployment Rate = MAX(indicators[unemployment])
Inflation Gap = MAX(indicators[inflation_gap])
```

### Latest value logic

```DAX
Latest Date = MAX(indicators[date])
```

```DAX
Chile CPI YoY (Latest) =
CALCULATE(
    [Chile CPI YoY],
    FILTER(ALL(indicators[date]), indicators[date] = [Latest Date])
)
```

Use the same pattern for:
- `TPM (Latest)`
- `Real Rate (Latest)`
- `Rate Spread (Latest)`
- `USDCLP (Latest)`

### Trend measures

```DAX
Chile CPI YoY Avg 12M =
AVERAGEX(
    DATESINPERIOD(dim_date[Date], MAX(dim_date[Date]), -12, MONTH),
    [Chile CPI YoY]
)
```

```DAX
Real Rate Avg 6M =
AVERAGEX(
    DATESINPERIOD(dim_date[Date], MAX(dim_date[Date]), -6, MONTH),
    [Real Rate]
)
```

## Recommended report pages

### 1. Overview

Visuals:
- KPI cards: CPI, TPM, Real Rate, Rate Spread, USDCLP
- Small inflation trend line
- Small policy stance trend line
- Executive text box with macro summary

### 2. Inflation

Visuals:
- Line chart: `cpi_yoy`, `cpi_usa`, `inflation_3m_avg`
- Card: `Inflation Gap`
- Target reference line at 3%

### 3. Monetary Policy

Visuals:
- Line chart: `tpm`, `fed_funds`
- Card: `Real Rate`
- Card: `Rate Spread`
- Conditional label: restrictive vs accommodative

### 4. Markets

Visuals:
- Line chart: `usdclp`
- Line chart: `copper`
- Line chart: `oil`
- Cards: monthly changes and volatility

### 5. Economic Activity

Visuals:
- Line chart: `gdp_or_imacec`
- Line chart: `unemployment`
- Card: `activity_growth`
- Optional traffic-light interpretation

## Power BI implementation notes

- Format rates as percentages with one or two decimals
- Format `usdclp` as decimal number
- Use consistent colors by theme:
  - Inflation: red/orange
  - Policy: blue
  - Activity: teal
  - Markets: copper/gray
- Prefer monthly date granularity
- Add a slicer for date range on all pages
- Add tooltips explaining each macro indicator in plain language

## Portfolio positioning

This model helps present the project as more than a dashboard. It shows:
- Data modeling ability
- KPI design for business users
- Translation of macroeconomic analysis into executive reporting
- Familiarity with the workflow expected in research, banking, and consulting teams
