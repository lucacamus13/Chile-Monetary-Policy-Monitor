from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SeriesConfig:
    code: str
    display_name: str
    source: str
    source_series_id: str
    frequency: str
    unit: str
    category: str
    country: str
    processed_column: str
    priority: int
    notes: str = ""


SERIES_CATALOG = [
    SeriesConfig(
        code="cpi_chile",
        display_name="Chile CPI",
        source="BCCH",
        source_series_id="F074.IPC.IND.Z.EP23.C.M",
        frequency="monthly",
        unit="index",
        category="inflation",
        country="Chile",
        processed_column="cpi_chile",
        priority=1,
        notes="Official CPI index from Banco Central de Chile, linked series.",
    ),
    SeriesConfig(
        code="cpi_usa",
        display_name="US CPI",
        source="FRED",
        source_series_id="CPIAUCSL",
        frequency="monthly",
        unit="index",
        category="inflation",
        country="United States",
        processed_column="cpi_usa",
        priority=1,
        notes="Used as external inflation benchmark.",
    ),
    SeriesConfig(
        code="tpm",
        display_name="Chile Monetary Policy Rate",
        source="BCCH",
        source_series_id="F022.TPM.TIN.D001.NO.Z.D",
        frequency="daily",
        unit="percent",
        category="rates",
        country="Chile",
        processed_column="tpm",
        priority=1,
        notes="Main domestic policy stance variable.",
    ),
    SeriesConfig(
        code="fed_funds",
        display_name="Federal Funds Rate",
        source="FRED",
        source_series_id="FEDFUNDS",
        frequency="monthly",
        unit="percent",
        category="rates",
        country="United States",
        processed_column="fed_funds",
        priority=1,
        notes="Main external monetary policy benchmark.",
    ),
    SeriesConfig(
        code="imacec",
        display_name="IMACEC",
        source="BCCH",
        source_series_id="F032.IMC.IND.Z.Z.EP18.Z.Z.0.M",
        frequency="monthly",
        unit="index",
        category="activity",
        country="Chile",
        processed_column="gdp_or_imacec",
        priority=1,
        notes="Monthly activity proxy for Chilean GDP dynamics.",
    ),
    SeriesConfig(
        code="unemployment",
        display_name="Unemployment Rate",
        source="FRED",
        source_series_id="LRUNTTTTCLM156S",
        frequency="monthly",
        unit="percent",
        category="activity",
        country="Chile",
        processed_column="unemployment",
        priority=1,
        notes="Labor market slack indicator.",
    ),
    SeriesConfig(
        code="usdclp",
        display_name="USD/CLP Exchange Rate",
        source="FRED",
        source_series_id="CCUSMA02CLM618N",
        frequency="monthly",
        unit="clp_per_usd",
        category="financial_conditions",
        country="Chile",
        processed_column="usdclp",
        priority=1,
        notes="Tracks exchange-rate pass-through and external pressure.",
    ),
    SeriesConfig(
        code="copper",
        display_name="Copper Price",
        source="FRED",
        source_series_id="PCOPPUSDM",
        frequency="monthly",
        unit="usd_per_metric_ton",
        category="external_sector",
        country="Global",
        processed_column="copper",
        priority=1,
        notes="Key external driver for Chile's terms of trade.",
    ),
    SeriesConfig(
        code="oil",
        display_name="Oil Price",
        source="FRED",
        source_series_id="MCOILWTICO",
        frequency="monthly",
        unit="usd_per_barrel",
        category="external_sector",
        country="Global",
        processed_column="oil",
        priority=1,
        notes="Relevant for imported inflation and global conditions.",
    ),
]


SERIES_LOOKUP = {series.code: series for series in SERIES_CATALOG}
PROCESSED_COLUMN_LOOKUP = {series.code: series.processed_column for series in SERIES_CATALOG}
FRED_SERIES = [series for series in SERIES_CATALOG if series.source == "FRED"]
BCCH_SERIES = [series for series in SERIES_CATALOG if series.source == "BCCH"]
TARGET_INFLATION = 3.0
BASE_DIR = Path(__file__).resolve().parents[1]
DATABASE_PATH = BASE_DIR / "database.db"
RAW_CSV_PATH = BASE_DIR / "data" / "raw" / "macro_data.csv"
PROCESSED_CSV_PATH = BASE_DIR / "data" / "processed" / "processed_data.csv"
INDICATORS_CSV_PATH = BASE_DIR / "data" / "processed" / "indicators.csv"
