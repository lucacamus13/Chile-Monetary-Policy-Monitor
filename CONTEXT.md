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
- Semantic model built from `processed_data` and `indicators`

---

## 5. Data Storage

The project uses a hybrid storage approach:

### Primary Storage

- SQLite database (`database.db`)

### Secondary Storage

- CSV files (for Power BI integration)

### Database Design

#### Table: raw_data

- date
- variable
- value

#### Table: processed_data

- date
- cpi_chile
- cpi_usa
- tpm
- fed_funds
- usdclp
- copper
- oil
- gdp_or_imacec
- unemployment

#### Table: indicators

- date
- cpi_yoy
- cpi_mom
- real_rate
- rate_spread
- usdclp_change
- copper_change
- oil_change
- inflation_gap
- activity_growth

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

---

## 9. Data Pipeline

The pipeline consists of:

1. `download_data.py`
   - Fetch data from APIs
   - Store raw data in CSV and SQLite

2. `clean_data.py`
   - Clean and merge datasets
   - Handle missing values
   - Store `processed_data` in CSV and SQLite

3. `indicators.py`
   - Compute analytical indicators
   - Store `indicators` in CSV and SQLite

4. Outputs available in:
   - SQLite database
   - CSV files

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
- Support table: `processed_data`
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

## 13. Design Principles

The project must:

- Solve a real economic problem
- Be interpretable by non-technical users
- Follow real analyst workflows
- Prioritize clarity over unnecessary complexity
- Be reproducible and extendable

---

## 14. End Goal

The final product should demonstrate the ability to:

- Work with real-world macroeconomic data
- Build a modular data pipeline
- Compute policy-relevant indicators
- Design technical and business-facing dashboards
- Communicate insights clearly to stakeholders

This should be portfolio-ready and comparable to junior analyst work in banking, consulting, or economic research.
