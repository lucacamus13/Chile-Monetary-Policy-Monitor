from __future__ import annotations

from pathlib import Path
import sys
from typing import Any

import numpy as np
import pandas as pd
import streamlit as st

if not hasattr(np, 'unicode_'):
    np.unicode_ = np.str_

import plotly.express as px

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

TARGET_INFLATION = 3.0
INDICATORS_CSV_PATH = BASE_DIR / 'data' / 'processed' / 'indicators.csv'
OIL_DAILY_CSV_PATH = BASE_DIR / 'data' / 'processed' / 'oil_daily.csv'
IPOM_OPTIONS = ['Marzo 2026', 'Diciembre 2025', 'Septiembre 2025']
PAGE_OPTIONS = [
    'Resumen ejecutivo',
    'Escenario internacional',
    'Inflacion',
    'Actividad y demanda',
    'Politica monetaria',
    'Riesgos',
]
DISPLAY_NAMES = {
    'cpi_yoy': 'IPC total YoY',
    'inflation_3m_avg': 'Inflacion promedio 3m',
    'cpi_mom': 'IPC total MoM',
    'tpm': 'TPM',
    'fed_funds': 'Fed Funds',
    'real_rate': 'Tasa real',
    'rate_spread': 'Spread Chile-EE.UU.',
    'activity_growth': 'Actividad YoY',
    'activity_3m_avg': 'Actividad promedio 3m',
    'unemployment': 'Desempleo',
    'usdclp': 'USD/CLP',
    'usdclp_change': 'USD/CLP MoM',
    'copper': 'Cobre',
    'copper_change': 'Cobre MoM',
    'oil': 'Petroleo',
    'oil_change': 'Petroleo MoM',
    'gdp_or_imacec': 'PIB o Imacec',
    'latam_fx_index': 'Indice LATAM',
    'usdclp_index': 'USD/CLP',
    'usa_dollar_reindex': 'Indice DXY',
    'euro_usd_index': 'EUR/USD',
}


@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    indicators = pd.read_csv(INDICATORS_CSV_PATH, parse_dates=['date'])
    if OIL_DAILY_CSV_PATH.exists():
        oil_daily = pd.read_csv(OIL_DAILY_CSV_PATH, parse_dates=['date'])
    else:
        oil_daily = pd.DataFrame(columns=['date', 'oil_daily'])
    return indicators.sort_values('date').copy(), oil_daily.sort_values('date').copy()


def available_series(df: pd.DataFrame, columns: list[str]) -> list[str]:
    return [column for column in columns if column in df.columns and df[column].notna().any()]


def latest_non_null(df: pd.DataFrame, column: str):
    if column not in df.columns:
        return None
    series = df[['date', column]].dropna(subset=[column])
    if series.empty:
        return None
    return series.iloc[-1]


def previous_non_null(df: pd.DataFrame, column: str):
    if column not in df.columns:
        return None
    series = df[['date', column]].dropna(subset=[column])
    if len(series) < 2:
        return None
    return series.iloc[-2]


def format_value(value, suffix: str = '', decimals: int = 2) -> str:
    if value is None or pd.isna(value):
        return 'N/A'
    return f'{value:.{decimals}f}{suffix}'


def format_delta(current, previous, suffix: str = '', decimals: int = 2) -> str | None:
    if current is None or previous is None or pd.isna(current) or pd.isna(previous):
        return None
    delta = current - previous
    return f'{delta:+.{decimals}f}{suffix}'


def build_line_chart(df: pd.DataFrame, y_columns: list[str], title: str, value_label: str = 'Valor'):
    series = available_series(df, y_columns)
    if not series:
        st.info(f'No hay series disponibles para {title.lower()}.')
        return

    fig = px.line(
        df,
        x='date',
        y=series,
        labels={'date': 'Fecha', 'value': value_label, 'variable': 'Serie'},
        title=title,
    )
    fig.for_each_trace(lambda trace: trace.update(name=DISPLAY_NAMES.get(trace.name, trace.name)))
    fig.update_layout(legend_title_text='Serie', hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)


def ensure_data_available() -> None:
    if INDICATORS_CSV_PATH.exists():
        return
    st.warning(
        'Indicators file is missing. Run `python scripts/download_data.py --sample` '
        'and `python scripts/indicators.py` first.'
    )
    st.stop()


def build_context() -> dict[str, Any]:
    ensure_data_available()
    indicators, oil_daily = load_data()
    usable = indicators[indicators['is_usable_month'] == True].copy() if 'is_usable_month' in indicators.columns else indicators.copy()
    latest_available = indicators.iloc[-1]

    st.sidebar.header('Configuracion IPoM')
    selected_ipom = st.sidebar.selectbox('IPoM activo', IPOM_OPTIONS, index=0, key='selected_ipom')
    show_partial = st.sidebar.checkbox('Incluir meses parciales', value=False, key='show_partial')
    show_inflation_compare = st.sidebar.checkbox('Comparar IPoM anterior vs actual: inflacion', value=True, key='show_inflation_compare')
    show_activity_compare = st.sidebar.checkbox('Comparar IPoM anterior vs actual: PIB', value=True, key='show_activity_compare')

    base_df = indicators if show_partial else usable
    if base_df.empty:
        st.error('No hay meses utilizables disponibles con la configuracion actual.')
        st.stop()

    latest_usable = base_df.iloc[-1]
    min_date = base_df['date'].min().date()
    max_date = base_df['date'].max().date()
    date_range = st.sidebar.slider(
        'Rango de fechas',
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date),
        key='date_range',
    )
    filtered = base_df[
        (base_df['date'].dt.date >= date_range[0])
        & (base_df['date'].dt.date <= date_range[1])
    ].copy()

    if filtered.empty:
        st.error('No hay datos en el rango seleccionado.')
        st.stop()

    market_options = [column for column in ['usdclp', 'copper', 'oil'] if column in filtered.columns]
    selected_markets = st.sidebar.multiselect(
        'Variables de mercado',
        market_options,
        default=market_options,
        key='selected_markets',
    )

    st.sidebar.markdown('---')
    st.sidebar.caption(f'Datos utilizables hasta: {latest_usable["date"].date()}')
    st.sidebar.caption(f'Ultimo pull visible en pipeline: {latest_available["date"].date()}')

    headline_gap = latest_usable['inflation_gap'] if 'inflation_gap' in latest_usable.index else None
    real_rate = latest_usable['real_rate'] if 'real_rate' in latest_usable.index else None

    if pd.notna(real_rate) and real_rate > 1.0:
        stance_label = 'Restrictiva'
    elif pd.notna(real_rate) and real_rate >= 0:
        stance_label = 'En normalizacion'
    else:
        stance_label = 'Incertidumbre mayor al habitual'

    return {
        'indicators': indicators,
        'oil_daily': oil_daily,
        'base_df': base_df,
        'filtered': filtered,
        'latest_usable': latest_usable,
        'latest_available': latest_available,
        'selected_ipom': selected_ipom,
        'selected_markets': selected_markets,
        'show_inflation_compare': show_inflation_compare,
        'show_activity_compare': show_activity_compare,
        'headline_gap': headline_gap,
        'real_rate': real_rate,
        'stance_label': stance_label,
    }


def render_page_header(ctx: dict[str, Any], title: str, caption: str) -> None:
    st.title(title)
    st.caption(caption)
    st.info(
        f'IPoM activo: {ctx["selected_ipom"]} | '
        f'Datos utilizables hasta {ctx["latest_usable"]["date"].date()} | '
        f'Ultimo mes visible del pipeline: {ctx["latest_available"]["date"].date()}'
    )


def render_metric(ctx: dict[str, Any], column: str, label: str, suffix: str = '', decimals: int = 2):
    latest = latest_non_null(ctx['base_df'], column)
    previous = previous_non_null(ctx['base_df'], column)
    value = latest[column] if latest is not None else None
    prior = previous[column] if previous is not None else None
    st.metric(label, format_value(value, suffix=suffix, decimals=decimals), format_delta(value, prior, suffix=suffix, decimals=decimals))


def render_resumen_ejecutivo(ctx: dict[str, Any]) -> None:
    latest_usable = ctx['latest_usable']
    oil_daily = ctx['oil_daily']
    headline_gap = ctx['headline_gap']
    stance_label = ctx['stance_label']

    latest_oil_row = oil_daily.iloc[-1] if not oil_daily.empty else None
    prev_oil_row = oil_daily.iloc[-2] if len(oil_daily) > 1 else None
    oil_value = latest_oil_row['oil_daily'] if latest_oil_row is not None else None
    oil_prev_value = prev_oil_row['oil_daily'] if prev_oil_row is not None else None

    summary_lines = [
        f'La inflacion anual se ubica en {format_value(latest_usable.get("cpi_yoy"), suffix="%")}, con una brecha de {format_value(headline_gap, suffix=" pp")}.',
        f'La TPM se encuentra en {format_value(latest_usable.get("tpm"), suffix="%")}, mientras la tasa real ex ante luce {stance_label.lower()}.',
        f'La actividad muestra una variacion anual de {format_value(latest_usable.get("activity_growth"), suffix="%")}, con desempleo en {format_value(latest_usable.get("unemployment"), suffix="%")}.' ,
        f'En el frente externo, el cobre se ubica en {format_value(latest_usable.get("copper"), decimals=0)} y el petroleo en {format_value(oil_value)}.'
    ]

    st.markdown(f'**Stance general: {stance_label}**')
    st.write(' '.join(summary_lines))

    metric_cols = st.columns(5)
    with metric_cols[0]:
        render_metric(ctx, 'tpm', 'TPM actual', suffix='%')
    with metric_cols[1]:
        render_metric(ctx, 'cpi_yoy', 'IPC total', suffix='%')
    with metric_cols[2]:
        render_metric(ctx, 'inflation_3m_avg', 'IPC subyacente proxy', suffix='%')
    with metric_cols[3]:
        render_metric(ctx, 'gdp_or_imacec', 'PIB / Imacec', decimals=2)
    with metric_cols[4]:
        st.metric('Petroleo', format_value(oil_value), format_delta(oil_value, oil_prev_value))


def render_escenario_internacional(ctx: dict[str, Any]) -> None:
    latest_usable = ctx['latest_usable']
    st.subheader('Supuestos internacionales disponibles')
    intl_table = pd.DataFrame([
        {'Indicador': 'Petroleo WTI', 'Ultimo dato': format_value(latest_usable.get('oil')), 'Cambio mensual': format_value(latest_usable.get('oil_change'), suffix='%')},
        {'Indicador': 'Cobre', 'Ultimo dato': format_value(latest_usable.get('copper'), decimals=0), 'Cambio mensual': format_value(latest_usable.get('copper_change'), suffix='%')},
        {'Indicador': 'Fed Funds', 'Ultimo dato': format_value(latest_usable.get('fed_funds'), suffix='%'), 'Cambio mensual': 'Carga manual pendiente'},
        {'Indicador': 'USD/CLP', 'Ultimo dato': format_value(latest_usable.get('usdclp'), decimals=0), 'Cambio mensual': format_value(latest_usable.get('usdclp_change'), suffix='%')},
    ])
    st.dataframe(intl_table, use_container_width=True, hide_index=True)

    col1, col2 = st.columns(2)
    with col1:
        build_line_chart(ctx['oil_daily'], ['oil_daily'], 'Trayectoria del precio del petroleo (diario)', value_label='USD por barril')
    with col2:
        build_line_chart(ctx['filtered'], ['copper'], 'Trayectoria del precio del cobre', value_label='Precio')

    build_line_chart(ctx['filtered'], ['fed_funds'], 'Fed Funds: historial disponible', value_label='Porcentaje')

    fx_series = available_series(ctx['filtered'], ['latam_fx_index', 'usdclp_index', 'usa_dollar_reindex', 'euro_usd_index'])
    if fx_series:
        fx_filtered = ctx['filtered'][
            (ctx['filtered']['date'] >= '2025-03-01') & 
            (ctx['filtered']['date'] <= '2026-03-31')
        ]
        
        color_map = {
            'usdclp_index': 'red',
            'usa_dollar_reindex': 'blue',
            'euro_usd_index': 'green',
            'latam_fx_index': 'lightblue',
        }
        
        label_map = {
            'usdclp_index': 'Chile',
            'usa_dollar_reindex': 'EE.UU.',
            'euro_usd_index': 'Eurozona',
            'latam_fx_index': 'América Latina',
        }
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.line(
                fx_filtered,
                x='date',
                y=fx_series,
                labels={'date': 'Fecha', 'value': 'Indice', 'variable': 'Serie'},
                title='<b>a) Monedas</b><br><sup>(índice 01.ene.25 = 100)</sup>',
                color_discrete_map=color_map,
            )
            
            for trace in fig.data:
                trace.name = label_map.get(trace.name, trace.name)
            
            fig.add_shape(type="line", x0="2026-02-01", x1="2026-02-01", y0=0, y1=1, yref="paper", line=dict(color="gray", width=1.5, dash="dash"))
            fig.update_layout(legend_title_text='Serie', hovermode='x unified', yaxis_showgrid=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.info("Gráfico 2 (placeholder)")
    else:
        st.info('Series de tipo de cambio no disponibles.')

    st.caption('Pendiente para una siguiente iteracion: mercado vs FOMC, Brent, socios comerciales y riesgo geopolitico estructurado.')


def render_inflacion(ctx: dict[str, Any]) -> None:
    filtered = ctx['filtered']
    latest_usable = ctx['latest_usable']

    inflation_series = ['cpi_yoy', 'inflation_3m_avg']
    inflation_available = available_series(filtered, inflation_series)
    if inflation_available:
        inflation_chart = px.line(
            filtered,
            x='date',
            y=inflation_available,
            labels={'date': 'Fecha', 'value': 'Porcentaje', 'variable': 'Serie'},
            title='IPC total vs IPC subyacente proxy',
        )
        inflation_chart.for_each_trace(lambda trace: trace.update(name=DISPLAY_NAMES.get(trace.name, trace.name)))
        inflation_chart.add_hline(y=TARGET_INFLATION, line_dash='dash', line_color='green')
        inflation_chart.add_hrect(y0=2, y1=4, line_width=0, fillcolor='green', opacity=0.08)
        st.plotly_chart(inflation_chart, use_container_width=True)
    else:
        st.info('No hay series suficientes para construir el grafico principal de inflacion.')

    left_col, right_col = st.columns(2)
    with left_col:
        build_line_chart(filtered, ['cpi_mom'], 'Variacion mensual del IPC', value_label='Porcentaje')
    with right_col:
        build_line_chart(filtered, ['inflation_gap'], 'Brecha de inflacion respecto de la meta', value_label='Puntos porcentuales')

    if ctx['show_inflation_compare']:
        st.dataframe(
            pd.DataFrame([
                {'Escenario': 'IPoM vigente', 'IPC total YoY': format_value(latest_usable.get('cpi_yoy'), suffix='%'), 'IPC subyacente proxy': format_value(latest_usable.get('inflation_3m_avg'), suffix='%')},
                {'Escenario': 'IPoM anterior', 'IPC total YoY': 'Carga manual pendiente', 'IPC subyacente proxy': 'Carga manual pendiente'},
            ]),
            use_container_width=True,
            hide_index=True,
        )
    st.caption('Pendiente para una siguiente iteracion: expectativas EEE/EOF y contribuciones del IPC desde tablas BCCh.')


def render_actividad(ctx: dict[str, Any]) -> None:
    latest_usable = ctx['latest_usable']
    build_line_chart(ctx['filtered'], ['gdp_or_imacec'], 'PIB / Imacec: trayectoria disponible', value_label='Indice')

    col1, col2 = st.columns(2)
    with col1:
        build_line_chart(ctx['filtered'], ['activity_growth', 'activity_3m_avg'], 'Actividad mensual', value_label='Porcentaje')
    with col2:
        build_line_chart(ctx['filtered'], ['unemployment'], 'Mercado laboral: desempleo', value_label='Porcentaje')

    if ctx['show_activity_compare']:
        st.dataframe(
            pd.DataFrame([
                {'Escenario': 'IPoM vigente', 'PIB / Imacec': format_value(latest_usable.get('gdp_or_imacec'), decimals=2), 'Actividad YoY': format_value(latest_usable.get('activity_growth'), suffix='%')},
                {'Escenario': 'IPoM anterior', 'PIB / Imacec': 'Carga manual pendiente', 'Actividad YoY': 'Carga manual pendiente'},
            ]),
            use_container_width=True,
            hide_index=True,
        )

    activity_projection_table = pd.DataFrame([
        {'Variable': 'PIB', 'Estado actual': format_value(latest_usable.get('gdp_or_imacec'), decimals=2), 'Nota': 'Rango IPoM pendiente de carga manual'},
        {'Variable': 'Consumo privado', 'Estado actual': 'No disponible aun', 'Nota': 'Requiere nueva serie'},
        {'Variable': 'FBCF', 'Estado actual': 'No disponible aun', 'Nota': 'Requiere nueva serie'},
        {'Variable': 'Cuenta corriente', 'Estado actual': 'No disponible aun', 'Nota': 'Requiere nueva serie'},
    ])
    st.dataframe(activity_projection_table, use_container_width=True, hide_index=True)


def render_politica_monetaria(ctx: dict[str, Any]) -> None:
    latest_usable = ctx['latest_usable']
    real_rate = ctx['real_rate']

    build_line_chart(ctx['filtered'], ['tpm', 'fed_funds'], 'TPM vs Fed Funds', value_label='Porcentaje')

    col1, col2 = st.columns([2, 1])
    with col1:
        build_line_chart(ctx['filtered'], ['real_rate', 'rate_spread'], 'Tasa real y diferencial de tasas', value_label='Porcentaje')
    with col2:
        st.subheader('Semaforo de tasa real')
        if pd.isna(real_rate):
            st.info('Sin dato suficiente para clasificar la tasa real.')
        elif real_rate > 0:
            st.success(f'Tasa real positiva: {format_value(real_rate, suffix="%")}')
        else:
            st.warning(f'Tasa real negativa: {format_value(real_rate, suffix="%")}')

    policy_table = pd.DataFrame([
        {'Indicador': 'TPM', 'Nivel': format_value(latest_usable.get('tpm'), suffix='%')},
        {'Indicador': 'Fed Funds', 'Nivel': format_value(latest_usable.get('fed_funds'), suffix='%')},
        {'Indicador': 'Spread Chile-EE.UU.', 'Nivel': format_value(latest_usable.get('rate_spread'), suffix=' pp')},
        {'Indicador': 'USD/CLP', 'Nivel': format_value(latest_usable.get('usdclp'), decimals=0)},
    ])
    st.dataframe(policy_table, use_container_width=True, hide_index=True)
    st.caption('Pendiente para una siguiente iteracion: corredor de TPM, puntos EEE/EOF, curva forward y tipo de cambio real proyectado.')


def render_riesgos(ctx: dict[str, Any]) -> None:
    risk_cols = st.columns(3)
    with risk_cols[0]:
        st.error(f'Inflacion al alza: brecha actual {format_value(ctx["headline_gap"], suffix=" pp")}')
    with risk_cols[1]:
        activity_value = ctx['latest_usable'].get('activity_growth')
        if pd.notna(activity_value) and activity_value < 0:
            st.warning(f'Actividad a la baja: crecimiento anual {format_value(activity_value, suffix="%")}')
        else:
            st.info(f'Actividad sin senal contractiva severa: {format_value(activity_value, suffix="%")}')
    with risk_cols[2]:
        st.info('Factor local/fiscal: pendiente de integracion con variables domesticas y escenario IPoM manual.')

    build_line_chart(ctx['filtered'], ['activity_growth'], 'Brecha de actividad proxy', value_label='Porcentaje')
    st.caption('Pendiente para una siguiente iteracion: brecha de actividad oficial IPoM y riesgo geopolitico (`GEOPOLRISK`).')
