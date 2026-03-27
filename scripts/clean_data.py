from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from config.variables import PROCESSED_COLUMN_LOOKUP, PROCESSED_CSV_PATH, RAW_CSV_PATH
from scripts.storage import write_table


PROCESSED_DIR = BASE_DIR / "data" / "processed"


def clean_macro_data(df: pd.DataFrame) -> pd.DataFrame:
    tidy = df.copy()
    tidy["date"] = pd.to_datetime(tidy["date"])
    tidy["value"] = pd.to_numeric(tidy["value"], errors="coerce")
    tidy = tidy.dropna(subset=["date", "series_code", "value"]).sort_values(
        ["series_code", "date"]
    )
    tidy["variable"] = tidy["series_code"].map(PROCESSED_COLUMN_LOOKUP)

    processed = (
        tidy.pivot_table(index="date", columns="variable", values="value", aggfunc="last")
        .sort_index()
        .reset_index()
    )

    expected_columns = [
        "date",
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
    for column in expected_columns:
        if column not in processed.columns:
            processed[column] = pd.NA

    return processed[expected_columns]


def main() -> None:
    if not RAW_CSV_PATH.exists():
        raise SystemExit(
            f"Raw file not found at {RAW_CSV_PATH}. Run `python scripts/download_data.py --sample` first."
        )

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    raw = pd.read_csv(RAW_CSV_PATH)
    processed = clean_macro_data(raw)
    processed.to_csv(PROCESSED_CSV_PATH, index=False)
    write_table(processed.assign(date=processed["date"].astype(str)), "processed_data")
    print(f"Processed data written to {PROCESSED_CSV_PATH}")


if __name__ == "__main__":
    main()
