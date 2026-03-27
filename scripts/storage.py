from __future__ import annotations

import sqlite3
from pathlib import Path
import sys

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from config.variables import DATABASE_PATH


def write_table(df: pd.DataFrame, table_name: str, database_path: Path = DATABASE_PATH) -> None:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database_path) as connection:
        df.to_sql(table_name, connection, if_exists="replace", index=False)


def read_table(table_name: str, database_path: Path = DATABASE_PATH) -> pd.DataFrame:
    with sqlite3.connect(database_path) as connection:
        return pd.read_sql_query(f"SELECT * FROM {table_name}", connection)
