from __future__ import annotations

from pathlib import Path
import sys

CURRENT_DIR = Path(__file__).resolve().parents[1]
if str(CURRENT_DIR) not in sys.path:
    sys.path.append(str(CURRENT_DIR))

from ipom_shared import build_context, render_page_header, render_escenario_internacional
import streamlit as st

st.set_page_config(page_title='Escenario internacional | Monitor IPoM Chile', layout='wide')
ctx = build_context()
render_page_header(ctx, '2. Escenario internacional', 'Condiciones externas, commodities y supuestos financieros globales.')
render_escenario_internacional(ctx)
