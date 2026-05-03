"""
modules/exam_interpreter.py — Clasificación, explicaciones y resumen de exámenes.
Extraído de app.py en Sprint 3-B2.
"""
import logging
import re
from typing import Optional, Tuple

import pandas as pd
import streamlit as st

from modules.file_extractor import safe_text_normalize

DEFAULT_MARGIN_PCT = 5.0


@st.cache_data
def cargar_explicaciones_csv(path: str = "explicaciones.csv") -> pd.DataFrame:
    try:
        df = pd.read_csv(path)
        df.columns = [c.strip().lower() for c in df.columns]
        if "marcador" in df.columns:
            df["marcador"] = df["marcador"].astype(str).str.lower().str.strip()
        if "estado" in df.columns:
            df["estado"] = df["estado"].astype(str).str.lower().str.strip()
        return df
    except Exception:
        return pd.DataFrame(columns=["marcador", "estado", "explicacion", "fuente_url"])


EXPL = cargar_explicaciones_csv()


def normalize_marker(nombre_ui: str) -> str:
    """Normaliza etiqueta de UI a clave de CSV."""
    n = safe_text_normalize((nombre_ui or "").strip().lower())
    n = re.sub(r"[^a-z0-9]", "", n)
    mapping = {
        "colesteroltotal": "col_total",
        "coltotal": "col_total",
        "colesterol": "col_total",
        "hdl": "hdl",
        "hdlcolesterol": "hdl",
        "hdlcolesterolhdl": "hdl",
        "ldl": "ldl",
        "ldlcolesterol": "ldl",
        "ldlcolesterolldl": "ldl",
        "trigliceridos": "trigliceridos",
        "glucosa": "glucosa",
        "glucosenaayunas": "glucosa",
        "hemoglobina": "hemoglobina",
        "creatinina": "creatinina",
        "bilirrubinatotal": "bil_total",
        "bilirrubinadirecta": "bil_directa",
        "bilirrubinaindirecta": "bil_indirecta",
        "fosfatasaalcalina": "fosfatasa_alc",
        "got": "got_ast",
        "ast": "got_ast",
        "gotast": "got_ast",
        "gpt": "gpt_alt",
        "alt": "gpt_alt",
        "gptalt": "gpt_alt",
        "proteinastotales": "prot_totales",
        "albumina": "albumina",
        "ggt": "ggt",
        "globulinas": "globulinas",
        "relacionalbglob": "rel_albumina_glob",
        "tpsegundos": "tp_seg",
        "tp": "tp_seg",
        "tpporcentaje": "tp_pct",
        "inr": "inr",
        "sodio": "sodio",
        "potasio": "potasio",
        "cloro": "cloro",
        "ureabun": "urea_bun",
        "vfgckdepi": "vfg_ckd_epi",
        "vfg": "vfg_ckd_epi",
        "fosforo": "fosforo",
        "magnesio": "magnesio",
        "procalcitonina": "procalcitonina",
        "pcr": "pcr",
        "eritrocitos": "eritrocitos",
        "hematocrito": "hematocrito",
        "vcm": "vcm",
        "hcm": "hcm",
        "chcm": "chcm",
        "plaquetas": "plaquetas",
        "vpm": "vpm",
        "leucocitos": "leucocitos",
        "rdwcv": "rdw_cv",
        "neutrofilos": "neutro",
        "linfocitos": "linf",
        "monocitos": "mono",
        "eosinofilos": "eos",
        "basofilos": "baso",
        "ttpa": "ttpa",
        "ferritina": "ferritina",
        "ph": "ph",
        "pco2": "pco2",
        "po2": "po2",
        "hco3": "hco3",
        "excesobase": "exceso_base",
        "saturaciono2": "sat_o2",
        "tco2": "tco2",
        "fio2": "fio2",
        "presionbarometrica": "pres_baro",
        "temperatura": "temp",
        # Nuevos marcadores Sprint 6
        "tsh": "tsh",
        "t4libre": "t4_libre",
        "t3libre": "t3_libre",
        "vhs": "vhs",
        "acidourico": "acido_urico",
        "vitaminad": "vitamina_d",
        "vitaminab12": "vitamina_b12",
        "nitrogenoureicobun": "urea_bun",
    }
    return mapping.get(n, n)


def buscar_explicacion(marcador_ui: str, estado: str) -> Tuple[Optional[str], Optional[str]]:
    mk = normalize_marker(marcador_ui)
    if EXPL is None or EXPL.empty:
        return None, None
    row = EXPL[(EXPL["marcador"] == mk) & (EXPL["estado"] == (estado or "").lower())]
    if not row.empty:
        return row.iloc[0].get("explicacion"), row.iloc[0].get("fuente_url", "")
    return None, None


def classify_with_margin(value: float, ref: Optional[Tuple[float, float]], margin_pct: float) -> Optional[str]:
    if ref is None or value is None:
        return None
    lo, hi = ref
    if lo >= hi:
        return None
    margin = (hi - lo) * (margin_pct / 100.0)
    if value < lo:
        return "limite" if value >= lo - margin else "bajo"
    if value > hi:
        return "limite" if value <= hi + margin else "alto"
    if (value - lo) <= margin or (hi - value) <= margin:
        return "limite"
    return "normal"


def show_line(label: str, value: Optional[float], ref: Optional[Tuple[float, float]],
              margin_pct: float = DEFAULT_MARGIN_PCT) -> Optional[str]:
    if value is None:
        st.write(f"• {label}: sin valor ingresado.")
        return None
    if ref is None:
        st.write(f"• {label}: {value} — sin referencia para cálculo.")
        return None
    status = classify_with_margin(value, ref, margin_pct)
    lo, hi = ref
    color = {"alto": "🔴", "bajo": "🔴", "limite": "🟠", "normal": "🟢"}.get(status, "⚪")
    st.write(f"{color} **{label}**: {value} → **{(status or 'desconocido').upper()}** (ref: {lo}–{hi})")
    return status


def construir_resumen_detallado(detalles: list) -> str:
    bullets = []
    for mk_ui, stt in detalles:
        if not stt:
            continue
        exp, url = buscar_explicacion(mk_ui, stt)
        if not exp:
            logging.warning(f"Sin explicación en CSV para '{mk_ui}' estado '{stt}'.")
        if exp:
            if url and isinstance(url, str) and url.startswith("http"):
                bullets.append(f"- **{mk_ui} ({stt})**: {exp} [Fuente]({url})")
            else:
                bullets.append(f"- **{mk_ui} ({stt})**: {exp}")
    if bullets:
        return "\n".join(bullets) + "\n\nEste resultado es orientativo y no reemplaza la evaluación profesional."
    if detalles:
        return "Se detectan parámetros fuera del rango de referencia. Consulte con su médico."
    return ("Tus valores ingresados están dentro de rangos de referencia. "
            "Este resultado es con fines de orientación y no reemplaza la evaluación profesional.")
