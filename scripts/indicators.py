from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from config.variables import INDICATORS_CSV_PATH, PROCESSED_CSV_PATH, TARGET_INFLATION
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
]


def build_indicator_table(df: pd.DataFrame) -> pd.DataFrame:
    indicators = df.sort_values("date").copy()
    indicators["date"] = pd.to_datetime(indicators["date"])

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

    indicator_columns = [
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
    ]

    indicators = indicators.replace([np.inf, -np.inf], np.nan)
    return indicators[indicator_columns]


def main() -> None:
    if not PROCESSED_CSV_PATH.exists():
        raise SystemExit(
            f"Processed input not found at {PROCESSED_CSV_PATH}. Run `python scripts/clean_data.py` first."
        )

    processed = pd.read_csv(PROCESSED_CSV_PATH, parse_dates=["date"])
    indicators = build_indicator_table(processed)
    indicators.to_csv(INDICATORS_CSV_PATH, index=False)
    write_table(indicators.assign(date=indicators["date"].astype(str)), "indicators")
    print(f"Indicators written to {INDICATORS_CSV_PATH}")


if __name__ == "__main__":
    main()
