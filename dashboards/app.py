from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

TARGET_INFLATION = 3.0
PROCESSED_CSV_PATH = BASE_DIR / 'data' / 'processed' / 'processed_data.csv'
INDICATORS_CSV_PATH = BASE_DIR / 'data' / 'processed' / 'indicators.csv'


st.set_page_config(page_title='Chile Monetary Policy Monitor', layout='wide')
st.title('Chile Monetary Policy Monitor')
st.caption('Macro dashboard for tracking inflation, policy stance, activity, and external conditions.')


@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    processed = pd.read_csv(PROCESSED_CSV_PATH, parse_dates=['date'])
    indicators = pd.read_csv(INDICATORS_CSV_PATH, parse_dates=['date'])
    return processed, indicators


if not PROCESSED_CSV_PATH.exists() or not INDICATORS_CSV_PATH.exists():
    st.warning(
        'Processed files are missing. Run `python scripts/download_data.py --source all`, '
        '`python scripts/clean_data.py`, and `python scripts/indicators.py` first.'
    )
    st.stop()

processed, indicators = load_data()
indicators = indicators.sort_values('date').copy()
usable = indicators[indicators['is_usable_month'] == True].copy()
latest_usable = usable.iloc[-1] if not usable.empty else indicators.iloc[-1]
latest_available = indicators.iloc[-1]

st.sidebar.header('Filters')
show_partial = st.sidebar.checkbox('Include partial months', value=False)
base_df = indicators if show_partial else usable

if base_df.empty:
    st.error('No usable months available in the current dataset.')
    st.stop()

min_date = base_df['date'].min().date()
max_date = base_df['date'].max().date()
date_range = st.sidebar.slider(
    'Date range',
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
)
filtered = base_df[
    (base_df['date'].dt.date >= date_range[0])
    & (base_df['date'].dt.date <= date_range[1])
].copy()

market_options = ['usdclp', 'copper', 'oil']
selected_markets = st.sidebar.multiselect(
    'Market variables',
    options=market_options,
    default=market_options,
)

st.info(
    f"Latest usable month: {latest_usable['date'].date()} | "
    f"Latest available month in raw pipeline: {latest_available['date'].date()}"
)

col1, col2, col3, col4 = st.columns(4)
col1.metric('Chile CPI YoY', f"{latest_usable['cpi_yoy']:.2f}%" if pd.notna(latest_usable['cpi_yoy']) else 'N/A')
col2.metric('TPM', f"{latest_usable['tpm']:.2f}%" if pd.notna(latest_usable['tpm']) else 'N/A')
col3.metric('Real Rate', f"{latest_usable['real_rate']:.2f}%" if pd.notna(latest_usable['real_rate']) else 'N/A')
col4.metric('Chile-US Spread', f"{latest_usable['rate_spread']:.2f} pp" if pd.notna(latest_usable['rate_spread']) else 'N/A')

inflation_tab, policy_tab, activity_tab, markets_tab = st.tabs(
    ['Inflation', 'Policy', 'Activity', 'Markets']
)

with inflation_tab:
    inflation_chart = px.line(
        filtered,
        x='date',
        y=['cpi_yoy', 'inflation_3m_avg'],
        labels={'value': 'Percent', 'date': 'Date', 'variable': 'Series'},
        title='Chile Inflation Monitoring',
    )
    inflation_chart.add_hline(y=TARGET_INFLATION, line_dash='dash', line_color='green')
    st.plotly_chart(inflation_chart, use_container_width=True)

with policy_tab:
    policy_chart = px.line(
        filtered,
        x='date',
        y=['tpm', 'fed_funds', 'real_rate', 'rate_spread'],
        labels={'value': 'Percent', 'date': 'Date', 'variable': 'Series'},
        title='Monetary Policy Stance',
    )
    st.plotly_chart(policy_chart, use_container_width=True)

with activity_tab:
    activity_chart = px.line(
        filtered,
        x='date',
        y=['activity_growth', 'activity_3m_avg', 'unemployment'],
        labels={'value': 'Percent', 'date': 'Date', 'variable': 'Series'},
        title='Domestic Activity and Labor Market',
    )
    st.plotly_chart(activity_chart, use_container_width=True)

with markets_tab:
    if not selected_markets:
        st.info('Select at least one market variable from the sidebar.')
    else:
        market_chart = px.line(
            filtered,
            x='date',
            y=selected_markets,
            labels={'value': 'Level', 'date': 'Date', 'variable': 'Series'},
            title='Financial Conditions and External Sector',
        )
        st.plotly_chart(market_chart, use_container_width=True)

st.subheader('Latest analytical table')
st.dataframe(
    filtered.sort_values('date', ascending=False).head(12),
    use_container_width=True,
)
