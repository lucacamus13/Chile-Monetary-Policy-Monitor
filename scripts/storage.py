from __future__ import annotations

import sqlite3
from pathlib import Path
import sys

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from config.variables import DATABASE_PATH


def init_raw_data_table(database_path: Path = DATABASE_PATH) -> None:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS raw_data (
                date TEXT NOT NULL,
                series_code TEXT NOT NULL,
                value REAL,
                updated_at TEXT DEFAULT (datetime('now')),
                PRIMARY KEY (date, series_code)
            )
        """)
        conn.commit()


def write_table(df: pd.DataFrame, table_name: str, database_path: Path = DATABASE_PATH) -> None:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    init_raw_data_table(database_path)
    
    df = df.copy()
    if "updated_at" not in df.columns:
        from datetime import datetime
        df["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with sqlite3.connect(database_path) as connection:
        df.to_sql(table_name, connection, if_exists="replace", index=False)


def upsert_table(df: pd.DataFrame, table_name: str, database_path: Path = DATABASE_PATH) -> int:
    if df.empty:
        return 0
    
    database_path.parent.mkdir(parents=True, exist_ok=True)
    init_raw_data_table(database_path)
    
    df = df.copy()
    from datetime import datetime
    df["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    key_columns = ["date", "series_code"]
    columns = list(df.columns)
    non_key_cols = [c for c in columns if c not in key_columns]
    
    placeholders = ", ".join(["?"] * len(columns))
    columns_sql = ", ".join(columns)
    
    update_set = ", ".join([f"{c}=excluded.{c}" for c in non_key_cols])
    
    sql = f"""
        INSERT INTO {table_name} ({columns_sql})
        VALUES ({placeholders})
        ON CONFLICT ({', '.join(key_columns)}) DO UPDATE SET {update_set}
    """
    
    with sqlite3.connect(database_path) as conn:
        cursor = conn.cursor()
        data = [tuple(row) for row in df.values]
        cursor.executemany(sql, data)
        conn.commit()
        return cursor.rowcount


def read_table(table_name: str, database_path: Path = DATABASE_PATH) -> pd.DataFrame:
    with sqlite3.connect(database_path) as connection:
        return pd.read_sql_query(f"SELECT * FROM {table_name}", connection)


def get_last_date(series_code: str, database_path: Path = DATABASE_PATH) -> str | None:
    with sqlite3.connect(database_path) as conn:
        cursor = conn.execute(
            "SELECT MAX(date) FROM raw_data WHERE series_code = ?",
            (series_code,)
        )
        result = cursor.fetchone()[0]
        return result


def series_exists(series_code: str, database_path: Path = DATABASE_PATH) -> bool:
    with sqlite3.connect(database_path) as conn:
        cursor = conn.execute(
            "SELECT 1 FROM raw_data WHERE series_code = ? LIMIT 1",
            (series_code,)
        )
        return cursor.fetchone() is not None


def export_raw_to_csv(database_path: Path = DATABASE_PATH, csv_path: Path = None) -> None:
    from config.variables import RAW_CSV_PATH
    if csv_path is None:
        csv_path = RAW_CSV_PATH
    
    df = read_table("raw_data", database_path)
    df = df.drop(columns=["updated_at"], errors="ignore")
    df = df.sort_values(["series_code", "date"]).reset_index(drop=True)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_path, index=False)
    print(f"CSV exported to {csv_path}")
