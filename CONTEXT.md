# Project Context — Chile Monetary Policy Monitor

## 1. Overview

This project builds a data-driven monitoring system for Chilean monetary policy.

It replicates workflows used in:
- Central banks
- Investment banks
- Economic research teams
- Consulting firms
- Asset management firms

The system integrates data engineering, economic analysis, and business intelligence.

---

## 2. Problem Statement

Monetary policy analysis requires tracking multiple macroeconomic variables:

- Inflation
- Interest rates
- Economic activity
- Exchange rates
- External conditions

Analysts in banks and research teams must continuously answer:

- Is inflation converging to target?
- Is monetary policy restrictive or accommodative?
- How does the Federal Reserve influence Chile?
- Is economic activity weakening?
- Are external conditions tightening financial conditions?

This information is typically fragmented across multiple sources.

---

## 3. Objective

Build an end-to-end system that:

1. Downloads macroeconomic data from reliable sources
2. Cleans and structures the data
3. Computes key monetary policy indicators
4. Stores data in a structured database
5. Provides interactive dashboards
6. Enables business-level visualization

The project must simulate real workflows in financial institutions.

---

## 4. System Architecture

The system is divided into three layers:

### 4.1 Backend (Python)

Responsible for:
- Data ingestion (APIs)
- Data cleaning
- Feature engineering (indicators)
- Data storage

### 4.2 Frontend (Streamlit)

- Interactive dashboard for technical users
- Exploration and analysis
- Portfolio demonstration

### 4.3 Business Intelligence Layer (Power BI)

- Executive dashboards
- KPI monitoring
- Business-oriented visualization
- Semantic model built from `indicators`

---

## 5. Data Storage

The project uses a hybrid storage approach:

### Primary Storage

- SQLite database (`database.db`) — source of truth

### Secondary Storage

- CSV files (for Power BI integration) — regenerated from SQLite on each pipeline run

### Database Design

#### Table: raw_data

| Column | Type | Description |
|--------|------|-------------|
| date | TEXT | Date of observation (YYYY-MM-DD) |
| series_code | TEXT | Series identifier (e.g., cpi_chile, oil, latam_fx_index) |
| value | REAL | Numeric value |
| updated_at | TEXT | Timestamp of last update |

Primary Key: (date, series_code)

The table uses **upsert** logic — new records are inserted, existing records are updated.

#### Table: indicators

| Column | Type | Description |
|--------|------|-------------|
| date | TEXT | Date (YYYY-MM-DD) |
| cpi_yoy | REAL | CPI year-over-year (%) |
| cpi_mom | REAL | CPI month-over-month (%) |
| real_rate | REAL | Real interest rate (TPM - CPI YoY) |
| rate_spread | REAL | Chile-USA rate spread (pp) |
| usdclp_change | REAL | USD/CLP monthly change (%) |
| copper_change | REAL | Copper monthly change (%) |
| oil_change | REAL | Oil monthly change (%) |
| inflation_gap | REAL | Inflation - target (3%) |
| activity_growth | REAL | Activity YoY growth (%) |
| latam_fx_index | REAL | LATAM FX index (base 100 = Jan 2025) |
| ... | ... | Other raw and derived variables |

The `indicators` table is the main analytical output and the main Power BI fact table.

---

## 6. Data Sources

Use real-world public sources:

- FRED (Federal Reserve Economic Data)
- World Bank
- Central Bank of Chile

---

## 7. Key Variables

### Inflation

- CPI Chile
- CPI USA

### Interest Rates

- Chile Monetary Policy Rate (TPM)
- Federal Funds Rate

### Economic Activity

- GDP (or proxy such as IMACEC)
- Unemployment rate

### Financial Conditions

- USD/CLP exchange rate
- Brazil/USD (BRL)
- Mexico/USD (MXN)
- Peru/USD (PEN)
- Colombia/USD (COP)
- LATAM FX Index (average of BRL, MXN, PEN, COP, base 100 = Jan 2025)

### External Sector

- Copper price
- Oil price

---

## 8. Derived Indicators

The system must compute:

- Year-over-year inflation
- Month-over-month inflation
- Real interest rate (TPM - inflation)
- Interest rate spread (Chile - USA)
- Growth rates (GDP, copper, FX)
- Rolling averages (optional)
- Volatility measures (optional)
- LATAM FX Index (base 100 = Jan 2025, average of BRL, MXN, PEN, COP reindexed)
- Individual country FX indices (Brazil, Mexico, Peru, Colombia)

---

## 9. Data Pipeline

The pipeline consists of:

1. `download_data.py`
   - Fetch data from APIs (FRED, BCCh)
   - Store raw data in SQLite with **upsert** logic
   - Regenerate CSV from SQLite after each run

2. `indicators.py`
   - Pivot raw data to wide format
   - Compute analytical indicators
   - Store `indicators` in CSV and SQLite

### Download Modes

`download_data.py` supports two modes:

| Mode | Command | Description |
|------|---------|-------------|
| Full | `--mode full` | Downloads complete history from FULL_HISTORY_START (2015-01-01). Use for new series or reprocess. |
| Update | `--mode update` (default) | Incremental download since last date in DB. Auto-detects if series doesn't exist and runs full download. |

Additional options:
- `--variable [code]`: Download specific series (only with `--mode full`)
- `--freq [daily|monthly|quarterly]`: Filter by frequency (only with `--mode update`)

### Examples

```bash
# First time: download complete history for all series
py scripts/download_data.py --mode full

# Add new series: download complete history for one series
py scripts/download_data.py --mode full --variable cpi_chile

# Monthly update: download only new data since last run
py scripts/download_data.py --mode update

# Update only monthly series
py scripts/download_data.py --mode update --freq monthly
```

### Upsert Logic

The system uses **upsert** (INSERT OR UPDATE) to prevent data loss:

- Never overwrites existing data from other series
- If record exists (date, series_code) → updates value and updated_at
- If record doesn't exist → inserts new record
- Only overwrites data for the specific (date, series_code) being updated

Outputs available in:
- SQLite database (`database.db`)
- CSV files (regenerated from SQLite)

---

## 10. Expected Outputs

### 10.1 Streamlit Dashboard

Includes:

- Inflation panel
- Monetary policy panel (TPM, Fed, real rate)
- Economic activity panel
- Financial markets panel
- External conditions panel

Must include interactivity:
- Date filters
- Variable selection

### 10.2 Power BI Dashboard

Designed for business users.

Pages:

1. Overview (KPIs)
2. Inflation
3. Monetary Policy
4. Markets
5. Economic Activity

Power BI model:
- Main fact table: `indicators`
- Dimension table: `dim_date`

### 10.3 Analytical Insights (Optional but Recommended)

Generate simple interpretations such as:

"Real interest rates are currently positive, indicating a restrictive stance."

---

## 11. Repository Structure

```text
chilean monetary policy monitor/
├── config/
│   └── variables.py
├── dashboards/
│   └── app.py
├── data/
│   ├── raw/
│   ├── processed/
│   └── sample/
├── docs/
│   └── powerbi-model.md
├── notebooks/
├── reports/
│   ├── report_generator.py
│   └── latest_report.md
├── scripts/
│   ├── download_data.py
│   ├── clean_data.py
│   ├── indicators.py
│   └── storage.py
├── .env.example
├── CONTEXT.md
├── README.md
├── database.db
└── requirements.txt
```

---

## 12. Power BI Modeling Principles

The BI layer should:

- Use `indicators` as the primary fact table
- Use a dedicated `dim_date` table for time intelligence
- Keep relationships simple and one-directional
- Prioritize business clarity over unnecessary complexity
- Support KPI cards, trend lines, and executive summaries

---

## 13. FX Index Methodology

### LATAM FX Index

The LATAM FX Index replicates the methodology from the IPoM (Informe de Política Monetaria):

1. Each currency series is reindexed to base 100 = January 2025
2. The index is calculated as: `(current_value / base_value) * 100`
3. Values > 100 indicate depreciation vs USD since January 2025
4. Values < 100 indicate appreciation vs USD since January 2025
5. The LATAM FX Index is the simple average of: Brazil (BRL), Mexico (MXN), Peru (PEN), Colombia (COP)

### USD Dollar Index

The USA Dollar Index (`usa_dollar_reindex`) is inverted from FRED DTWEXBGS to match IPoM methodology:
- IPoM uses: Higher index = USD depreciation
- FRED DTWEXBGS: Higher index = USD appreciation
- Solution: Inverted the series (`base_value / current_value * 100`) to align with IPoM

### Reindexed Series in indicators.csv

| Column | Description | Base |
|--------|-------------|------|
| `latam_fx_index` | Average of LATAM currencies | 100 = Jan 2025 |
| `bra_usd_index` | Brazil FX Index | 100 = Jan 2025 |
| `mex_usd_index` | Mexico FX Index | 100 = Jan 2025 |
| `per_usd_index` | Peru FX Index | 100 = Jan 2025 |
| `col_usd_index` | Colombia FX Index | 100 = Jan 2025 |
| `usdclp_index` | Chile FX Index | 100 = Jan 2025 |
| `usa_dollar_reindex` | USA FX Index (inverted) | 100 = Jan 2025 |
| `euro_usd_index` | Eurozone FX Index | 100 = Jan 2025 |

---

## 15. Design Principles

The project must:

- Solve a real economic problem
- Be interpretable by non-technical users
- Follow real analyst workflows
- Prioritize clarity over unnecessary complexity
- Be reproducible and extendable

---

## 16. End Goal

The final product should demonstrate the ability to:

- Work with real-world macroeconomic data
- Build a modular data pipeline
- Compute policy-relevant indicators
- Design technical and business-facing dashboards
- Communicate insights clearly to stakeholders

This should be portfolio-ready and comparable to junior analyst work in banking, consulting, or economic research.
