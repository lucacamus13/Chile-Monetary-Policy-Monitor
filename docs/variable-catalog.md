# Variable Catalog

## Core download list

| code | display_name | source | source_series_id | frequency | unit | category | processed_column | priority |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| cpi_chile | Chile CPI | BCCH | F074.IPC.IND.Z.EP23.C.M | monthly | index | inflation | cpi_chile | 1 |
| cpi_usa | US CPI | FRED | CPIAUCSL | monthly | index | inflation | cpi_usa | 1 |
| tpm | Chile Monetary Policy Rate | BCCH | F022.TPM.TIN.D001.NO.Z.D | daily | percent | rates | tpm | 1 |
| fed_funds | Federal Funds Rate | FRED | FEDFUNDS | monthly | percent | rates | fed_funds | 1 |
| imacec | IMACEC | BCCH | F032.IMC.IND.Z.Z.EP18.Z.Z.0.M | monthly | index | activity | gdp_or_imacec | 1 |
| unemployment | Unemployment Rate | FRED | LRUNTTTTCLM156S | monthly | percent | activity | unemployment | 1 |
| usdclp | USD/CLP Exchange Rate | FRED | CCUSMA02CLM618N | monthly | clp_per_usd | financial_conditions | usdclp | 1 |
| copper | Copper Price | FRED | PCOPPUSDM | monthly | usd_per_metric_ton | external_sector | copper | 1 |
| oil | Oil Price | FRED | MCOILWTICO | monthly | usd_per_barrel | external_sector | oil | 1 |

## Notes

- `priority = 1` means the variable is part of the minimum viable macro monitor.
- FRED is already connected in the downloader.
- BCCH uses the official web service documented at `SieteRestWS.ashx` and requires `BCCH_API_USER` and `BCCH_API_PASS`.
- `processed_column` is the canonical field name used in `processed_data.csv`, `indicators.csv`, and `database.db`.
