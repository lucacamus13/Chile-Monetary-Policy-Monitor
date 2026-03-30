from __future__ import annotations

from pathlib import Path
import sys

import argparse
import os

import pandas as pd
import requests
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from config.variables import (
    BCCH_SERIES,
    FRED_SERIES,
    SERIES_CATALOG,
    FULL_HISTORY_START,
    RAW_CSV_PATH,
)
from scripts.storage import (
    upsert_table,
    get_last_date,
    series_exists,
    export_raw_to_csv,
)


BCCH_API_URL = "https://si3.bcentral.cl/SieteRestWS/SieteRestWS.ashx"
FRED_API_URL = "https://api.stlouisfed.org/fred/series/observations"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download macroeconomic data with upsert.")
    parser.add_argument(
        "--mode",
        choices=["full", "update"],
        default="update",
        help="full: download complete history from FULL_HISTORY_START. update: incremental since last date.",
    )
    parser.add_argument(
        "--variable",
        type=str,
        default=None,
        help="Specific series code to download (e.g., cpi_chile). Only applies to --mode full.",
    )
    parser.add_argument(
        "--freq",
        type=str,
        default=None,
        choices=["daily", "monthly", "quarterly"],
        help="Filter series by frequency (only applies to --mode update).",
    )
    return parser.parse_args()


def load_local_env() -> None:
    env_path = BASE_DIR / ".env"
    load_dotenv(dotenv_path=env_path, override=True, encoding="utf-8-sig")


def get_required_env(name: str) -> str:
    load_local_env()
    value = os.getenv(name)
    if not value:
        raise SystemExit(f"{name} is missing. Add it to .env or your environment.")
    return value


def fetch_fred_series(series_code: str, series_id: str, start_date: str) -> pd.DataFrame:
    api_key = get_required_env("FRED_API_KEY")
    response = requests.get(
        FRED_API_URL,
        params={
            "series_id": series_id,
            "api_key": api_key,
            "file_type": "json",
            "sort_order": "asc",
            "observation_start": start_date,
        },
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    observations = payload.get("observations", [])
    frame = pd.DataFrame(observations)
    if frame.empty:
        return pd.DataFrame(columns=["date", "series_code", "value"])

    frame = frame[["date", "value"]].copy()
    frame["date"] = pd.to_datetime(frame["date"])
    frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
    frame = frame.dropna(subset=["date", "value"])
    frame["date"] = frame["date"].dt.strftime("%Y-%m-%d")
    frame["series_code"] = series_code
    return frame[["date", "series_code", "value"]]


def fetch_bcch_series(series_code: str, series_id: str, start_date: str) -> pd.DataFrame:
    user = get_required_env("BCCH_API_USER")
    password = get_required_env("BCCH_API_PASS")
    response = requests.get(
        BCCH_API_URL,
        params={
            "user": user,
            "pass": password,
            "function": "GetSeries",
            "timeseries": series_id,
            "firstdate": start_date,
            "lastdate": pd.Timestamp.today().strftime("%Y-%m-%d"),
        },
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    if payload.get("Codigo") != 0:
        raise RuntimeError(f"BCCH API error for {series_code}: {payload.get('Descripcion')}")

    observations = payload.get("Series", {}).get("Obs", [])
    frame = pd.DataFrame(observations)
    if frame.empty:
        return pd.DataFrame(columns=["date", "series_code", "value"])

    frame = frame[["indexDateString", "value"]].copy()
    frame["date"] = pd.to_datetime(frame["indexDateString"], format="%d-%m-%Y", errors="coerce")
    frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
    frame = frame.dropna(subset=["date", "value"])

    if frame["date"].diff().dt.days.dropna().le(7).any():
        frame = (
            frame.set_index("date")
            .resample("MS")
            .mean(numeric_only=True)
            .reset_index()
        )

    frame["date"] = frame["date"].dt.strftime("%Y-%m-%d")
    frame["series_code"] = series_code
    return frame[["date", "series_code", "value"]]


def download_series(series_config, start_date: str) -> pd.DataFrame:
    source = series_config.source.lower()
    code = series_config.code
    source_id = series_config.source_series_id

    if source == "fred":
        return fetch_fred_series(code, source_id, start_date)
    elif source == "bcch":
        return fetch_bcch_series(code, source_id, start_date)
    else:
        raise ValueError(f"Unknown source: {source}")


def run_full_mode(specific_variable: str | None = None) -> None:
    series_to_download = []

    if specific_variable:
        series_to_download = [s for s in SERIES_CATALOG if s.code == specific_variable]
        if not series_to_download:
            raise SystemExit(f"Variable '{specific_variable}' not found in SERIES_CATALOG")
    else:
        series_to_download = SERIES_CATALOG

    print(f"[FULL MODE] Downloading {len(series_to_download)} series from {FULL_HISTORY_START}...")

    for series in series_to_download:
        print(f"  Downloading {series.code} ({series.source})...")
        try:
            df = download_series(series, FULL_HISTORY_START)
            if not df.empty:
                count = upsert_table(df, "raw_data")
                print(f"    -> {len(df)} rows, upserted {count} records")
            else:
                print(f"    -> No data returned")
        except Exception as e:
            print(f"    -> ERROR: {e}")


def run_update_mode(freq_filter: str | None = None) -> None:
    series_to_download = SERIES_CATALOG

    if freq_filter:
        series_to_download = [s for s in series_to_download if s.frequency == freq_filter]
        print(f"[UPDATE MODE] Filtering by freq='{freq_filter}': {len(series_to_download)} series")
    else:
        print(f"[UPDATE MODE] Processing {len(series_to_download)} series...")

    total_updated = 0

    for series in series_to_download:
        exists = series_exists(series.code)

        if not exists:
            print(f"  {series.code}: Not found in DB. Running FULL download...")
            start_date = FULL_HISTORY_START
        else:
            last_date = get_last_date(series.code)
            print(f"  {series.code}: Last date in DB = {last_date}. Fetching incremental...")
            start_date = last_date if last_date else FULL_HISTORY_START

        try:
            df = download_series(series, start_date)
            if not df.empty:
                count = upsert_table(df, "raw_data")
                print(f"    -> {len(df)} rows, upserted {count} records")
                total_updated += count
            else:
                print(f"    -> No new data")
        except Exception as e:
            print(f"    -> ERROR: {e}")

    print(f"\n[UPDATE MODE] Complete. Total records upserted: {total_updated}")


def main() -> None:
    args = parse_args()

    if args.mode == "full":
        run_full_mode(args.variable)
    else:
        run_update_mode(args.freq)

    export_raw_to_csv()
    print("Done.")


if __name__ == "__main__":
    main()
