from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from config.variables import INDICATORS_CSV_PATH, RAW_CSV_PATH, TARGET_INFLATION, PROCESSED_COLUMN_LOOKUP, LATAM_FX_CODES, LATAM_BASE_DATE
from scripts.storage import write_table


COMPLETENESS_COLUMNS = [
    "cpi_chile",
    "cpi_usa",
    "tpm",
    "fed_funds",
    "usdclp",
    "copper",
    "oil",
    "gdp_or_imacec",
    "unemployment",
    "bra_usd",
    "mex_usd",
    "per_usd",
    "col_usd",
    "usa_dollar_index",
    "euro_usd",
]


DAILY_SERIES = ["oil", "tpm", "copper", "usa_dollar_index"]


def pivot_raw_data(df: pd.DataFrame) -> pd.DataFrame:
    tidy = df.copy()
    tidy["date"] = pd.to_datetime(tidy["date"])
    tidy["value"] = pd.to_numeric(tidy["value"], errors="coerce")
    tidy = tidy.dropna(subset=["date", "series_code", "value"])
    tidy["column_name"] = tidy["series_code"].map(PROCESSED_COLUMN_LOOKUP)
    
    daily_data = tidy[tidy["column_name"].isin(DAILY_SERIES)].copy()
    monthly_data = tidy[~tidy["column_name"].isin(DAILY_SERIES)].copy()
    
    if not daily_data.empty:
        daily_data["month"] = daily_data["date"].dt.to_period("M").dt.to_timestamp()
        daily_monthly = (
            daily_data.pivot_table(
                index="month", columns="column_name", values="value", aggfunc="mean"
            )
            .reset_index()
            .rename(columns={"month": "date"})
        )
    else:
        daily_monthly = pd.DataFrame()
    
    if not monthly_data.empty:
        monthly_pivot = (
            monthly_data.pivot_table(
                index="date", columns="column_name", values="value", aggfunc="last"
            )
            .reset_index()
        )
    else:
        monthly_pivot = pd.DataFrame()
    
    if not daily_monthly.empty and not monthly_pivot.empty:
        wide = pd.merge(daily_monthly, monthly_pivot, on="date", how="outer")
    elif not daily_monthly.empty:
        wide = daily_monthly
    else:
        wide = monthly_pivot
    
    wide = wide.sort_values("date").reset_index(drop=True)
    
    for col in COMPLETENESS_COLUMNS:
        if col not in wide.columns:
            wide[col] = pd.NA
    
    return wide


def build_indicator_table(df: pd.DataFrame) -> pd.DataFrame:
    indicators = df.sort_values("date").copy()

    indicators["cpi_yoy"] = indicators["cpi_chile"].pct_change(12, fill_method=None) * 100
    indicators["cpi_mom"] = indicators["cpi_chile"].pct_change(1, fill_method=None) * 100
    indicators["real_rate"] = indicators["tpm"] - indicators["cpi_yoy"]
    indicators["rate_spread"] = indicators["tpm"] - indicators["fed_funds"]
    indicators["usdclp_change"] = indicators["usdclp"].pct_change(fill_method=None) * 100
    indicators["copper_change"] = indicators["copper"].pct_change(fill_method=None) * 100
    indicators["oil_change"] = indicators["oil"].pct_change(fill_method=None) * 100
    indicators["inflation_gap"] = indicators["cpi_yoy"] - TARGET_INFLATION
    indicators["activity_growth"] = indicators["gdp_or_imacec"].pct_change(12, fill_method=None) * 100
    indicators["inflation_3m_avg"] = indicators["cpi_yoy"].rolling(3).mean()
    indicators["activity_3m_avg"] = indicators["activity_growth"].rolling(3).mean()
    indicators["usdclp_volatility_3m"] = indicators["usdclp"].pct_change(fill_method=None).rolling(3).std() * 100

    indicators["data_completeness_count"] = indicators[COMPLETENESS_COLUMNS].notna().sum(axis=1)
    indicators["data_completeness_ratio"] = indicators["data_completeness_count"] / len(COMPLETENESS_COLUMNS)
    indicators["is_complete_month"] = indicators["data_completeness_count"] == len(COMPLETENESS_COLUMNS)
    indicators["is_usable_month"] = indicators["data_completeness_count"] >= 7

    base_columns = [
        "date",
        "cpi_yoy",
        "cpi_mom",
        "real_rate",
        "rate_spread",
        "usdclp_change",
        "copper_change",
        "oil_change",
        "inflation_gap",
        "activity_growth",
        "inflation_3m_avg",
        "activity_3m_avg",
        "usdclp_volatility_3m",
        "data_completeness_count",
        "data_completeness_ratio",
        "is_complete_month",
        "is_usable_month",
        "tpm",
        "fed_funds",
        "usdclp",
        "copper",
        "oil",
        "gdp_or_imacec",
        "unemployment",
        "cpi_chile",
        "cpi_usa",
        "usa_dollar_index",
        "euro_usd",
    ]

    latam_original_cols = [c for c in LATAM_INDEX_CODES if c in indicators.columns]
    
    indicator_columns = base_columns + latam_original_cols

    indicators = indicators.replace([np.inf, -np.inf], np.nan)
    return indicators[indicator_columns]


LATAM_INDEX_CODES = ["bra_usd", "mex_usd", "per_usd", "col_usd"]

REINDEX_CODES = ["usdclp", "usa_dollar_index", "euro_usd"]


def build_latam_fx_index(indicators_df: pd.DataFrame) -> pd.DataFrame:
    base_date = pd.Timestamp(LATAM_BASE_DATE)
    result = indicators_df.copy()

    for code in LATAM_INDEX_CODES:
        if code in result.columns:
            base_value_series = result[result["date"] <= base_date][code].dropna()
            if not base_value_series.empty:
                base_value = base_value_series.iloc[-1]
                result[f"{code}_index"] = (result[code] / base_value) * 100

    index_cols = [f"{c}_index" for c in LATAM_INDEX_CODES if f"{c}_index" in result.columns]
    if index_cols:
        result["latam_fx_index"] = result[index_cols].mean(axis=1)

    for code in REINDEX_CODES:
        if code in result.columns:
            base_value_series = result[result["date"] <= base_date][code].dropna()
            if not base_value_series.empty:
                base_value = base_value_series.iloc[-1]
                if code == "usa_dollar_index":
                    result["usa_dollar_reindex"] = (base_value / result[code]) * 100
                else:
                    result[f"{code}_index"] = (result[code] / base_value) * 100

    return result


DAILY_DATA_PATH = BASE_DIR / "data" / "processed" / "oil_daily.csv"


def main() -> None:
    if not RAW_CSV_PATH.exists():
        raise SystemExit(
            f"Raw data not found at {RAW_CSV_PATH}. Run `python scripts/download_data.py` first."
        )

    raw = pd.read_csv(RAW_CSV_PATH)
    wide = pivot_raw_data(raw)
    indicators = build_indicator_table(wide)
    indicators = build_latam_fx_index(indicators)
    
    oil_daily_df = raw[raw["series_code"] == "oil"][["date", "value"]].copy()
    oil_daily_df = oil_daily_df.rename(columns={"value": "oil_daily"})
    oil_daily_df.to_csv(DAILY_DATA_PATH, index=False)
    
    latam_cols = []
    for code in LATAM_INDEX_CODES:
        if code in indicators.columns:
            latam_cols.append(code)
        if f"{code}_index" in indicators.columns:
            latam_cols.append(f"{code}_index")
    if "latam_fx_index" in indicators.columns:
        latam_cols.append("latam_fx_index")
    
    reindex_cols = []
    for code in REINDEX_CODES:
        if code == "usa_dollar_index" and "usa_dollar_reindex" in indicators.columns:
            reindex_cols.append("usa_dollar_reindex")
        elif f"{code}_index" in indicators.columns:
            reindex_cols.append(f"{code}_index")
    
    all_cols = latam_cols + reindex_cols
    base_columns = [
        "date",
        "cpi_yoy",
        "cpi_mom",
        "real_rate",
        "rate_spread",
        "usdclp_change",
        "copper_change",
        "oil_change",
        "inflation_gap",
        "activity_growth",
        "inflation_3m_avg",
        "activity_3m_avg",
        "usdclp_volatility_3m",
        "data_completeness_count",
        "data_completeness_ratio",
        "is_complete_month",
        "is_usable_month",
        "tpm",
        "fed_funds",
        "usdclp",
        "copper",
        "oil",
        "gdp_or_imacec",
        "unemployment",
        "cpi_chile",
        "cpi_usa",
        "usa_dollar_index",
        "euro_usd",
    ]
    
    indicator_columns = base_columns + all_cols
    
    indicators["date"] = indicators["date"].astype(str)
    indicators = indicators[indicator_columns]
    
    indicators.to_csv(INDICATORS_CSV_PATH, index=False)
    write_table(indicators, "indicators")
    print(f"Indicators written to {INDICATORS_CSV_PATH}")
    print(f"Oil daily data written to {DAILY_DATA_PATH}")


if __name__ == "__main__":
    main()
