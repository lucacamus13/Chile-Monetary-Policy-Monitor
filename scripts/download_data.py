from __future__ import annotations

from pathlib import Path
import sys

import argparse
import os
import shutil

import pandas as pd
import requests
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from config.variables import BCCH_SERIES, FRED_SERIES, RAW_CSV_PATH
from scripts.storage import write_table


BCCH_API_URL = "https://si3.bcentral.cl/SieteRestWS/SieteRestWS.ashx"
FRED_API_URL = "https://api.stlouisfed.org/fred/series/observations"
RAW_DIR = BASE_DIR / "data" / "raw"
SAMPLE_FILE = BASE_DIR / "data" / "sample" / "sample_macro_data.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download or stage macroeconomic data.")
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Copy bundled sample data into the raw directory.",
    )
    parser.add_argument(
        "--source",
        choices=["sample", "fred", "bcch", "all"],
        default="all",
        help="Data source to use for the download step.",
    )
    return parser.parse_args()


def load_local_env() -> None:
    env_path = BASE_DIR / ".env"
    load_dotenv(dotenv_path=env_path, override=True, encoding="utf-8-sig")


def stage_sample_data() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SAMPLE_FILE, RAW_CSV_PATH)
    raw_df = pd.read_csv(RAW_CSV_PATH).rename(columns={"series_code": "variable"})[
        ["date", "variable", "value"]
    ]
    write_table(raw_df, "raw_data")
    print(f"Sample data copied to {RAW_CSV_PATH}")


def get_required_env(name: str) -> str:
    load_local_env()
    value = os.getenv(name)
    if not value:
        raise SystemExit(f"{name} is missing. Add it to .env or your environment before running this source.")
    return value


def fetch_fred_series(series_code: str, series_id: str) -> pd.DataFrame:
    api_key = get_required_env("FRED_API_KEY")
    response = requests.get(
        FRED_API_URL,
        params={
            "series_id": series_id,
            "api_key": api_key,
            "file_type": "json",
            "sort_order": "asc",
            "observation_start": "2015-01-01",
        },
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    observations = payload.get("observations", [])
    frame = pd.DataFrame(observations)
    if frame.empty:
        return pd.DataFrame(columns=["date", "variable", "value"])

    frame = frame[["date", "value"]].copy()
    frame["date"] = pd.to_datetime(frame["date"])
    frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
    frame = frame.dropna(subset=["date", "value"])
    frame["date"] = frame["date"].dt.strftime("%Y-%m-%d")
    frame["variable"] = series_code
    return frame[["date", "variable", "value"]]


def fetch_bcch_series(series_code: str, series_id: str) -> pd.DataFrame:
    user = get_required_env("BCCH_API_USER")
    password = get_required_env("BCCH_API_PASS")
    response = requests.get(
        BCCH_API_URL,
        params={
            "user": user,
            "pass": password,
            "function": "GetSeries",
            "timeseries": series_id,
            "firstdate": "2015-01-01",
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
        return pd.DataFrame(columns=["date", "variable", "value"])

    frame = frame[["indexDateString", "value"]].copy()
    frame["date"] = pd.to_datetime(frame["indexDateString"], format="%d-%m-%Y", errors="coerce")
    frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
    frame = frame.dropna(subset=["date", "value"])

    # Daily BCCH series are normalized to monthly averages for downstream consistency.
    if frame["date"].diff().dt.days.dropna().le(7).any():
        frame = (
            frame.set_index("date")
            .resample("MS")
            .mean(numeric_only=True)
            .reset_index()
        )

    frame["date"] = frame["date"].dt.strftime("%Y-%m-%d")
    frame["variable"] = series_code
    return frame[["date", "variable", "value"]]


def build_raw_dataset(source: str) -> pd.DataFrame:
    frames = []

    if source in {"fred", "all"}:
        for series in FRED_SERIES:
            frames.append(fetch_fred_series(series.code, series.source_series_id))

    if source in {"bcch", "all"}:
        for series in BCCH_SERIES:
            frames.append(fetch_bcch_series(series.code, series.source_series_id))

    if not frames:
        return pd.DataFrame(columns=["date", "variable", "value"])

    raw_df = pd.concat(frames, ignore_index=True)
    raw_df = raw_df.sort_values(["variable", "date"]).reset_index(drop=True)
    return raw_df


def persist_raw_data(raw_df: pd.DataFrame) -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    raw_df.rename(columns={"variable": "series_code"}).to_csv(RAW_CSV_PATH, index=False)
    write_table(raw_df, "raw_data")
    print(f"Raw data written to {RAW_CSV_PATH}")


def main() -> None:
    args = parse_args()

    if args.sample or args.source == "sample":
        stage_sample_data()
        return

    raw_df = build_raw_dataset(args.source)
    persist_raw_data(raw_df)


if __name__ == "__main__":
    main()
