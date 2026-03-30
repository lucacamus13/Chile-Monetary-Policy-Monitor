from __future__ import annotations

from pathlib import Path
import sys

CURRENT_DIR = Path(__file__).resolve().parents[1]
if str(CURRENT_DIR) not in sys.path:
    sys.path.append(str(CURRENT_DIR))

from ipom_shared import build_context, render_page_header, render_inflacion
import streamlit as st

st.set_page_config(page_title='Inflacion | Monitor IPoM Chile', layout='wide')
ctx = build_context()
render_page_header(ctx, '3. Escenario nacional: inflacion', 'Seguimiento de IPC total, subyacente proxy y brecha respecto de la meta.')
render_inflacion(ctx)
