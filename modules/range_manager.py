"""
modules/range_manager.py — Carga y resolución de rangos de referencia.
Extraído de app.py en Sprint 3-B2.

Nota: get_effective_range permanece en app.py por acoplamiento a
st.session_state, fuente_rangos, extracted_ranges y csv_ranges.
"""
from typing import Any, Dict

import pandas as pd
import streamlit as st


def ranges_from_csv(uploaded_csv) -> Dict[str, Any]:
    try:
        if uploaded_csv is None:
            return {}
        df = pd.read_csv(uploaded_csv)
        df.columns = [c.strip().lower() for c in df.columns]
        out: Dict[str, Any] = {}
        for _, row in df.iterrows():
            name = str(row.get("marcador", "")).strip().lower()
            if not name:
                continue
            try:
                lo = float(row.get("lo", float("nan")))
                hi = float(row.get("hi", float("nan")))
            except Exception:
                continue
            if not (lo < hi):
                continue
            sexo = None
            if "sexo" in df.columns and not pd.isna(row.get("sexo")):
                sexo = str(row.get("sexo")).strip().upper()
            if sexo in ("M", "F"):
                cur = out.get(name, {})
                if not isinstance(cur, dict):
                    cur = {}
                cur[sexo] = (lo, hi)
                out[name] = cur
            else:
                out[name] = (lo, hi)
        return out
    except Exception as e:
        st.warning(f"No pude leer el CSV de rangos: {e}")
        return {}
