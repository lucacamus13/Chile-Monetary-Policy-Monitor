# Chile Monetary Policy Monitor

Portfolio project focused on economic analysis, data engineering, and dashboard design for monetary policy monitoring in Chile.

## Why this project matters

This repository is designed to resemble the workflow used by:

- Central banks
- Investment banks
- Economic research teams
- Asset managers
- Consulting firms

The project consolidates macroeconomic data, transforms it into decision-ready indicators, and exposes it through an interactive dashboard. The goal is to show recruiters that the developer can move from raw economic data to an analytical product with business value.

## Core questions answered

- Is inflation converging to target?
- Is the Chilean policy rate restrictive or accommodative?
- How much does the Fed influence local policy conditions?
- Is domestic activity weakening or overheating?
- Are external variables tightening financial conditions?

## Project structure

```text
project/
├── config/
│   └── variables.py
├── dashboards/
│   └── app.py
├── data/
│   ├── processed/
│   ├── raw/
│   └── sample/
├── notebooks/
├── reports/
│   └── report_generator.py
├── scripts/
│   ├── clean_data.py
│   ├── download_data.py
│   └── indicators.py
├── docs/
│   ├── dashboard-spec.md
│   ├── data-dictionary.md
│   └── project-brief.md
├── .env.example
└── requirements.txt
```

## Data sources

Target production sources:

- FRED
- World Bank
- Central Bank of Chile

For local development and portfolio demonstration, the repository also includes sample data that allows the pipeline and dashboard to run without external credentials.

## Key variables

- Chile CPI
- US CPI
- Chile monetary policy rate
- Federal funds rate
- IMACEC proxy
- Unemployment rate
- USD/CLP
- Copper price
- Oil price

## Derived indicators

- Inflation YoY
- Inflation MoM
- Real policy rate
- Chile-US policy spread
- Activity growth
- FX depreciation
- Rolling averages

## Quick start

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the pipeline with sample data:

```bash
python scripts/download_data.py --sample
python scripts/clean_data.py
python scripts/indicators.py
```

4. Launch the dashboard:

```bash
streamlit run dashboards/app.py
```

## Recruiter-facing value

This project demonstrates:

- Economic intuition and macro monitoring logic
- Data ingestion and transformation workflows
- Config-driven Python development
- Dashboard design for decision-making
- Communication of technical outputs to non-technical stakeholders

## Next upgrades

- Connect live FRED and Central Bank APIs
- Add automated report generation
- Store outputs in SQLite or DuckDB
- Publish a Power BI version using the processed tables
