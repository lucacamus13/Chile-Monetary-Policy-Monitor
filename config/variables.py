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
        display_name="Tipo de cambio Chile",
        source="BCCH",
        source_series_id="F073.TCO.PRE.Z.D",
        frequency="monthly",
        unit="clp_per_usd",
        category="financial_conditions",
        country="Chile",
        processed_column="usdclp",
        priority=1,
        notes="Tipo de cambio peso chileno por dolar estadounidense.",
    ),
    SeriesConfig(
        code="usa_dollar_index",
        display_name="Tipo de cambio multilateral EEUU",
        source="FRED",
        source_series_id="DTWEXBGS",
        frequency="monthly",
        unit="index",
        category="financial_conditions",
        country="United States",
        processed_column="usa_dollar_index",
        priority=2,
        notes="Indice dolar multilateral (DXY) frente a principales monedas.",
    ),
    SeriesConfig(
        code="euro_usd",
        display_name="Tipo de cambio Eurozona",
        source="BCCH",
        source_series_id="F072.EUR.USD.N.O.D",
        frequency="monthly",
        unit="eur_per_usd",
        category="financial_conditions",
        country="Eurozone",
        processed_column="euro_usd",
        priority=2,
        notes="Euro por dolar estadounidense.",
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
        source_series_id="DCOILWTICO",
        frequency="monthly",
        unit="usd_per_barrel",
        category="external_sector",
        country="Global",
        processed_column="oil",
        priority=1,
        notes="Relevant for imported inflation and global conditions.",
    ),
    SeriesConfig(
        code="bra_usd",
        display_name="Brazil/USD Exchange Rate",
        source="BCCH",
        source_series_id="F072.BRL.USD.N.O.D",
        frequency="monthly",
        unit="brl_per_usd",
        category="financial_conditions",
        country="Brazil",
        processed_column="bra_usd",
        priority=2,
        notes="Brazilian real per USD - LATAM comparator.",
    ),
    SeriesConfig(
        code="mex_usd",
        display_name="Mexico/USD Exchange Rate",
        source="BCCH",
        source_series_id="F072.MXN.USD.N.O.D",
        frequency="monthly",
        unit="mxn_per_usd",
        category="financial_conditions",
        country="Mexico",
        processed_column="mex_usd",
        priority=2,
        notes="Mexican peso per USD - LATAM comparator.",
    ),
    SeriesConfig(
        code="per_usd",
        display_name="Peru/USD Exchange Rate",
        source="BCCH",
        source_series_id="F072.PEN.USD.N.O.D",
        frequency="monthly",
        unit="pen_per_usd",
        category="financial_conditions",
        country="Peru",
        processed_column="per_usd",
        priority=2,
        notes="Peruvian sol per USD - LATAM comparator.",
    ),
    SeriesConfig(
        code="col_usd",
        display_name="Colombia/USD Exchange Rate",
        source="BCCH",
        source_series_id="F072.COP.USD.N.O.D",
        frequency="monthly",
        unit="cop_per_usd",
        category="financial_conditions",
        country="Colombia",
        processed_column="col_usd",
        priority=2,
        notes="Colombian peso per USD - LATAM comparator.",
    ),
]


SERIES_LOOKUP = {series.code: series for series in SERIES_CATALOG}
PROCESSED_COLUMN_LOOKUP = {series.code: series.processed_column for series in SERIES_CATALOG}

LATAM_FX_CODES = ["usdclp", "bra_usd", "mex_usd", "per_usd", "col_usd", "euro_usd"]
LATAM_BASE_DATE = "2025-01-01"
FRED_SERIES = [series for series in SERIES_CATALOG if series.source == "FRED"]
BCCH_SERIES = [series for series in SERIES_CATALOG if series.source == "BCCH"]
TARGET_INFLATION = 3.0
FULL_HISTORY_START = "2015-01-01"
BASE_DIR = Path(__file__).resolve().parents[1]
DATABASE_PATH = BASE_DIR / "database.db"
RAW_CSV_PATH = BASE_DIR / "data" / "raw" / "macro_data.csv"
INDICATORS_CSV_PATH = BASE_DIR / "data" / "processed" / "indicators.csv"
