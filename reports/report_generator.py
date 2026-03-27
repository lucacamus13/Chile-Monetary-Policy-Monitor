from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from config.variables import INDICATORS_CSV_PATH


OUTPUT_FILE = BASE_DIR / "reports" / "latest_report.md"


def build_report(latest: pd.Series) -> str:
    stance = "restrictive" if latest["real_rate"] > 0 else "accommodative"
    inflation_signal = "above target" if latest["inflation_gap"] > 0 else "at or below target"

    return f"""# Chile Monetary Policy Snapshot

## Executive summary

- Chile CPI is {latest['cpi_yoy']:.1f}% YoY, which is {inflation_signal}.
- The policy rate stands at {latest['tpm']:.2f}% and the estimated real rate is {latest['real_rate']:.2f}%.
- The Chile-US policy spread is {latest['rate_spread']:.2f} percentage points.
- IMACEC proxy growth is {latest['gdp_or_imacec']:.1f}% YoY and unemployment is {latest['unemployment']:.1f}%.
- The current monetary stance appears {stance}.
"""


def main() -> None:
    if not INDICATORS_CSV_PATH.exists():
        raise SystemExit(
            f"Indicator file not found at {INDICATORS_CSV_PATH}. Run `python scripts/indicators.py` first."
        )

    indicators = pd.read_csv(INDICATORS_CSV_PATH, parse_dates=["date"]).sort_values("date")
    latest = indicators.iloc[-1]
    OUTPUT_FILE.write_text(build_report(latest), encoding="utf-8")
    print(f"Report written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
