# app.py — SeraphAID · Intérprete de exámenes de laboratorio
# Sprint 6: sidebar simplificado, rangos del lab prioritarios, alterados primero,
#           nuevos marcadores (TSH, VHS, ácido úrico, vitamina D, B12), diseño clínico.
import os
import re
import uuid
import logging
from datetime import datetime, timezone
import pandas as pd
import streamlit as st
from storage.local_json import LocalJSONStorage
from modules.file_extractor import extract_text_from_upload, parse_values_and_ranges
from modules.range_manager import ranges_from_csv
from modules.exam_interpreter import (
    classify_with_margin, show_line, construir_resumen_detallado,
    DEFAULT_MARGIN_PCT, normalize_marker, buscar_explicacion,
)
from modules.ai.registry import get_provider, list_available_providers
from modules.ui_components import render_topbar, COLOR
from pydantic import BaseModel, Field
from typing import Optional, Tuple, Dict
from ranges import get_range
from dotenv import load_dotenv

load_dotenv()

# ── Configuración de página ───────────────────────────────────────────────────
st.set_page_config(
    page_title="SeraphAID · Exámenes",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)
render_topbar("examenes")

# ── Estado de sesión ──────────────────────────────────────────────────────────
ENABLE_TTS = False
if "custom_ranges" not in st.session_state:
    st.session_state.custom_ranges = {}
if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())
_storage = LocalJSONStorage()

# ── Modelo de datos ───────────────────────────────────────────────────────────
class PatientInput(BaseModel):
    edad: int = Field(ge=18, le=120)
    sexo: Optional[str] = Field(default=None, pattern="^(M|F)$")
    # Core
    hemoglobina:     Optional[float] = None
    glucosa:         Optional[float] = None
    col_total:       Optional[float] = None
    hdl:             Optional[float] = None
    ldl:             Optional[float] = None
    trigliceridos:   Optional[float] = None
    creatinina:      Optional[float] = None
    # Hepático
    bil_total:       Optional[float] = None
    bil_directa:     Optional[float] = None
    bil_indirecta:   Optional[float] = None
    fosfatasa_alc:   Optional[float] = None
    got_ast:         Optional[float] = None
    gpt_alt:         Optional[float] = None
    prot_totales:    Optional[float] = None
    albumina:        Optional[float] = None
    ggt:             Optional[float] = None
    globulinas:      Optional[float] = None
    rel_albumina_glob: Optional[float] = None
    tp_seg:          Optional[float] = None
    tp_pct:          Optional[float] = None
    inr:             Optional[float] = None
    # Electrolitos / renal
    sodio:           Optional[float] = None
    potasio:         Optional[float] = None
    cloro:           Optional[float] = None
    urea_bun:        Optional[float] = None
    vfg_ckd_epi:     Optional[float] = None
    fosforo:         Optional[float] = None
    magnesio:        Optional[float] = None
    # Inflamación
    procalcitonina:  Optional[float] = None
    pcr:             Optional[float] = None
    ferritina:       Optional[float] = None
    vhs:             Optional[float] = None   # nuevo
    # Hemograma
    eritrocitos:     Optional[float] = None
    hematocrito:     Optional[float] = None
    vcm:             Optional[float] = None
    hcm:             Optional[float] = None
    chcm:            Optional[float] = None
    plaquetas:       Optional[float] = None
    vpm:             Optional[float] = None
    leucocitos:      Optional[float] = None
    rdw_cv:          Optional[float] = None
    neutro:          Optional[float] = None
    linf:            Optional[float] = None
    mono:            Optional[float] = None
    eos:             Optional[float] = None
    baso:            Optional[float] = None
    # Coagulación
    ttpa:            Optional[float] = None
    # Tiroides (nuevos)
    tsh:             Optional[float] = None
    t4_libre:        Optional[float] = None
    # Vitaminas / minerales (nuevos)
    vitamina_d:      Optional[float] = None
    vitamina_b12:    Optional[float] = None
    acido_urico:     Optional[float] = None
    # Gases
    ph:              Optional[float] = None
    pco2:            Optional[float] = None
    po2:             Optional[float] = None
    hco3:            Optional[float] = None
    exceso_base:     Optional[float] = None
    sat_o2:          Optional[float] = None
    tco2:            Optional[float] = None
    fio2:            Optional[float] = None
    pres_baro:       Optional[float] = None
    temp:            Optional[float] = None

# ── Selector IA inline ────────────────────────────────────────────────────────
_ai_labels = {
    "rules":     "Solo análisis local (sin IA)",
    "openai":    "OpenAI (GPT-4o)",
    "anthropic": "Anthropic (Claude)",
}
_ai_providers = list_available_providers()
if len(_ai_providers) > 1:
    with st.expander("⚙️ Opciones de interpretación", expanded=False):
        st.selectbox(
            "🤖 Proveedor de interpretación IA",
            options=_ai_providers,
            format_func=lambda p: _ai_labels.get(p, p),
            key="_ai_provider_name",
        )
else:
    if "_ai_provider_name" not in st.session_state:
        st.session_state["_ai_provider_name"] = "rules"

# ── Carga de examen ───────────────────────────────────────────────────────────
st.subheader("📄 Cargar examen")
uploaded = st.file_uploader(
    "Sube tu examen en PDF o imagen (JPG/PNG)",
    type=["pdf", "jpg", "jpeg", "png"],
    help="El sistema intentará leer los valores y rangos directamente de tu examen.",
)

extracted_values: Dict[str, float] = {}
extracted_ranges: Dict[str, Tuple[float, float]] = {}
_using_lab_ranges = False

if uploaded is not None:
    raw_text = extract_text_from_upload(uploaded)
    extracted_values, extracted_ranges = parse_values_and_ranges(raw_text)
    _using_lab_ranges = bool(extracted_ranges)
    with st.expander("🔎 Ver datos extraídos del documento"):
        st.write("**Valores detectados:**", extracted_values or "— ninguno")
        st.write("**Rangos del laboratorio:**", extracted_ranges or "— ninguno")
    if extracted_values:
        st.success(f"Se detectaron {len(extracted_values)} valor(es) en el documento. Los campos se han precargado abajo.")

for k, v in extracted_values.items():
    st.session_state.setdefault(f"val_{k}", v)

# ── Rango efectivo (siempre rangos del lab primero) ───────────────────────────
def get_effective_range(marker: str, sexo: Optional[str]) -> Optional[Tuple[float, float]]:
    """
    Prioridad:
    1) Rangos extraídos del examen del laboratorio (siempre preferidos).
    2) Rangos internos de SeraphAID (ranges.py).
    La configuración manual de rangos queda eliminada del UI (ver D-020).
    """
    key = (marker or "").lower()
    if extracted_ranges.get(key):
        return extracted_ranges[key]
    try:
        return get_range(key, sexo)
    except Exception:
        return None

# ── Formulario de ingreso manual ──────────────────────────────────────────────
st.subheader("🔢 Ingresar valores")
st.caption("Completa solo los campos disponibles en tu examen. Los campos vacíos (en 0) se ignorarán.")

def _v(key: str, default: float = 0.0) -> float:
    return float(st.session_state.get(f"val_{key}", default))

with st.form("form"):
    col1, col2 = st.columns(2)
    with col1:
        edad = st.number_input("Edad (años)", min_value=18, max_value=120, value=int(st.session_state.get("val_edad", 40)))
        sexo = st.selectbox("Sexo biológico", options=["", "M", "F"])
        hemoglobina   = st.number_input("Hemoglobina (g/dL)",          value=_v("hemoglobina", 14.0), step=0.1)
        glucosa       = st.number_input("Glucosa en ayunas (mg/dL)",    value=_v("glucosa", 95.0),     step=1.0)
    with col2:
        col_total     = st.number_input("Colesterol total (mg/dL)",     value=_v("col_total", 180.0),  step=1.0)
        hdl           = st.number_input("Colesterol HDL (mg/dL)",       value=_v("hdl", 50.0),         step=1.0)
        ldl           = st.number_input("Colesterol LDL (mg/dL)",       value=_v("ldl", 110.0),        step=1.0)
        trigliceridos = st.number_input("Triglicéridos (mg/dL)",        value=_v("trigliceridos", 140.0), step=1.0)
    creatinina    = st.number_input("Creatinina (mg/dL)",               value=_v("creatinina", 0.9),   step=0.01)

    with st.expander("Tiroides y vitaminas (opcionales)", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            tsh         = st.number_input("TSH (mIU/L)",             value=_v("tsh", 0.0),         step=0.01, key="tsh_input")
            t4_libre    = st.number_input("T4 libre (ng/dL)",        value=_v("t4_libre", 0.0),    step=0.01, key="t4_libre_input")
        with col2:
            vitamina_d  = st.number_input("Vitamina D 25-OH (ng/mL)",value=_v("vitamina_d", 0.0),  step=0.1,  key="vitamina_d_input")
            vitamina_b12= st.number_input("Vitamina B12 (pg/mL)",    value=_v("vitamina_b12", 0.0),step=1.0,  key="vitamina_b12_input")
        with col3:
            acido_urico = st.number_input("Ácido úrico (mg/dL)",     value=_v("acido_urico", 0.0), step=0.1,  key="acido_urico_input")
            vhs         = st.number_input("VHS (mm/h)",              value=_v("vhs", 0.0),          step=1.0,  key="vhs_input")

    with st.expander("Perfil hepático (opcionales)", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            bil_total     = st.number_input("Bilirrubina total (mg/dL)",    value=_v("bil_total", 0.8),     step=0.01)
            bil_directa   = st.number_input("Bilirrubina directa (mg/dL)",  value=_v("bil_directa", 0.2),   step=0.01)
            bil_indirecta = st.number_input("Bilirrubina indirecta (mg/dL)",value=_v("bil_indirecta", 0.6), step=0.01)
            fosfatasa_alc = st.number_input("Fosfatasa alcalina (U/L)",     value=_v("fosfatasa_alc", 80.0),step=1.0)
            got_ast       = st.number_input("GOT / AST (U/L)",              value=_v("got_ast", 25.0),      step=1.0)
        with col2:
            gpt_alt         = st.number_input("GPT / ALT (U/L)",            value=_v("gpt_alt", 30.0),      step=1.0)
            prot_totales    = st.number_input("Proteínas totales (g/dL)",   value=_v("prot_totales", 7.0),  step=0.1)
            albumina        = st.number_input("Albúmina (g/dL)",            value=_v("albumina", 4.2),      step=0.1)
            ggt             = st.number_input("GGT (U/L)",                  value=_v("ggt", 35.0),          step=1.0)
            globulinas      = st.number_input("Globulinas (g/dL)",          value=_v("globulinas", 3.0),    step=0.1)
            rel_albumina_glob=st.number_input("Relación Alb/Glob",         value=_v("rel_albumina_glob", 1.3),step=0.01)
            tp_seg          = st.number_input("TP (segundos)",              value=_v("tp_seg", 12.0),       step=0.1)
            tp_pct          = st.number_input("TP (%)",                     value=_v("tp_pct", 100.0),      step=0.1)
            inr             = st.number_input("INR",                        value=_v("inr", 1.0),           step=0.01)

    with st.expander("Electrolitos / Función renal", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            sodio   = st.number_input("Sodio (mEq/L)",      value=_v("sodio", 140.0),    step=0.1, key="sodio_input")
            potasio = st.number_input("Potasio (mEq/L)",    value=_v("potasio", 4.2),    step=0.1, key="potasio_input")
            cloro   = st.number_input("Cloro (mEq/L)",      value=_v("cloro", 102.0),    step=0.1, key="cloro_input")
        with col2:
            urea_bun    = st.number_input("Nitrógeno ureico / BUN (mg/dL)", value=_v("urea_bun", 30.0),    step=0.1, key="urea_bun_input")
            vfg_ckd_epi = st.number_input("VFG (mL/min/1.73m²)",           value=_v("vfg_ckd_epi", 90.0), step=0.1, key="vfg_input")
        with col3:
            fosforo = st.number_input("Fósforo (mg/dL)",    value=_v("fosforo", 3.5),    step=0.1, key="fosforo_input")
            magnesio= st.number_input("Magnesio (mg/dL)",   value=_v("magnesio", 1.9),   step=0.1, key="magnesio_input")

    with st.expander("Inflamación, Hemograma, Coagulación y Gases (opcionales)", expanded=False):
        st.markdown("**Inflamación**")
        col1, col2 = st.columns(2)
        with col1:
            procalcitonina = st.number_input("Procalcitonina (ng/mL)", value=_v("procalcitonina", 0.05), step=0.01, key="procalcitonina_input")
            pcr            = st.number_input("PCR (mg/L)",              value=_v("pcr", 2.0),            step=0.1,  key="pcr_input")
            ferritina      = st.number_input("Ferritina (ng/mL)",       value=_v("ferritina", 100.0),    step=1.0,  key="ferritina_input")
        st.markdown("**Hemograma**")
        col1, col2, col3 = st.columns(3)
        with col1:
            eritrocitos = st.number_input("Eritrocitos (10^6/µL)", value=_v("eritrocitos", 4.5),  step=0.01, key="eritrocitos_input")
            hematocrito = st.number_input("Hematocrito (%)",       value=_v("hematocrito", 42.0), step=0.1,  key="hematocrito_input")
        with col2:
            vcm  = st.number_input("VCM (fL)",  value=_v("vcm", 90.0),  step=0.1, key="vcm_input")
            hcm  = st.number_input("HCM (pg)",  value=_v("hcm", 30.0),  step=0.1, key="hcm_input")
            chcm = st.number_input("CHCM (g/dL)",value=_v("chcm", 33.0),step=0.1, key="chcm_input")
        with col3:
            plaquetas = st.number_input("Plaquetas (10^3/µL)", value=_v("plaquetas", 250.0),step=1.0,  key="plaquetas_input")
            vpm       = st.number_input("VPM (fL)",            value=_v("vpm", 10.0),       step=0.1,  key="vpm_input")
            leucocitos= st.number_input("Leucocitos (10^3/µL)",value=_v("leucocitos", 6.5), step=0.1,  key="leucocitos_input")
        rdw_cv = st.number_input("RDW-CV (%)", value=_v("rdw_cv", 13.5), step=0.1, key="rdw_cv_input")
        st.markdown("**Fórmula diferencial (%)**")
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1: neutro = st.number_input("Neutrófilos %",  value=_v("neutro", 60.0), step=0.1, key="neutro_input")
        with col2: linf   = st.number_input("Linfocitos %",   value=_v("linf", 30.0),   step=0.1, key="linf_input")
        with col3: mono   = st.number_input("Monocitos %",    value=_v("mono", 5.0),    step=0.1, key="mono_input")
        with col4: eos    = st.number_input("Eosinófilos %",  value=_v("eos", 3.0),     step=0.1, key="eos_input")
        with col5: baso   = st.number_input("Basófilos %",    value=_v("baso", 1.0),    step=0.1, key="baso_input")
        st.markdown("**Coagulación**")
        ttpa = st.number_input("TTPA (segundos)", value=_v("ttpa", 30.0), step=0.1, key="ttpa_input")
        st.markdown("**Gases en sangre**")
        col1, col2, col3 = st.columns(3)
        with col1:
            ph   = st.number_input("pH",           value=_v("ph", 7.4),   step=0.01, key="ph_input")
            pco2 = st.number_input("pCO₂ (mmHg)",  value=_v("pco2", 40.0),step=0.1,  key="pco2_input")
            po2  = st.number_input("pO₂ (mmHg)",   value=_v("po2", 95.0), step=0.1,  key="po2_input")
        with col2:
            hco3        = st.number_input("HCO₃⁻ (mmol/L)",    value=_v("hco3", 24.0),       step=0.1, key="hco3_input")
            exceso_base = st.number_input("Exceso de base",     value=_v("exceso_base", 0.0), step=0.1, key="exceso_base_input")
            sat_o2      = st.number_input("Saturación O₂ (%)", value=_v("sat_o2", 97.0),     step=0.1, key="sat_o2_input")
        with col3:
            tco2     = st.number_input("TCO₂ (mmol/L)",      value=_v("tco2", 25.0),    step=0.1, key="tco2_input")
            fio2     = st.number_input("FIO₂ (%)",           value=_v("fio2", 21.0),    step=0.1, key="fio2_input")
            pres_baro= st.number_input("Presión barom. (mmHg)",value=_v("pres_baro", 760.0),step=0.1, key="pres_baro_input")
            temp     = st.number_input("Temperatura (°C)",   value=_v("temp", 36.6),    step=0.1, key="temp_input")

    submitted = st.form_submit_button("🔍 Interpretar resultados", use_container_width=True)

# ── Contexto clínico relacionado por marcador (Fase 7) ───────────────────────
_RELATED: dict = {
    "Hemoglobina":              ["Hematocrito", "VCM", "Ferritina"],
    "Glucosa":                  ["Triglicéridos", "TSH"],
    "Colesterol total":         ["HDL", "LDL", "Triglicéridos"],
    "HDL":                      ["Colesterol total", "LDL", "Triglicéridos"],
    "LDL":                      ["Colesterol total", "HDL", "Triglicéridos"],
    "Triglicéridos":            ["Colesterol total", "HDL", "Glucosa"],
    "Creatinina":               ["Nitrógeno ureico / BUN", "VFG (CKD-EPI)"],
    "Nitrógeno ureico / BUN":   ["Creatinina", "VFG (CKD-EPI)"],
    "VFG (CKD-EPI)":            ["Creatinina", "Nitrógeno ureico / BUN"],
    "GOT (AST)":                ["GPT (ALT)", "Bilirrubina total", "GGT"],
    "GPT (ALT)":                ["GOT (AST)", "Bilirrubina total", "GGT"],
    "Bilirrubina total":        ["GOT (AST)", "GPT (ALT)", "Fosfatasa alcalina"],
    "GGT":                      ["GOT (AST)", "GPT (ALT)", "Fosfatasa alcalina"],
    "Fosfatasa alcalina":       ["GOT (AST)", "GPT (ALT)", "Bilirrubina total"],
    "Leucocitos":               ["Neutrófilos (%)", "Linfocitos (%)", "PCR", "Procalcitonina"],
    "PCR":                      ["Leucocitos", "Procalcitonina", "VHS"],
    "Procalcitonina":           ["Leucocitos", "PCR"],
    "VHS":                      ["PCR", "Leucocitos"],
    "Ferritina":                ["Hemoglobina", "VCM", "Eritrocitos"],
    "TSH":                      ["T4 libre"],
    "T4 libre":                 ["TSH"],
    "INR":                      ["TP (s)", "TTPA"],
    "TP (s)":                   ["INR", "TTPA"],
    "TTPA":                     ["INR", "TP (s)"],
    "pH":                       ["pCO₂", "HCO₃⁻", "Exceso base"],
    "pCO₂":                     ["pH", "HCO₃⁻", "Exceso base"],
    "HCO₃⁻":                    ["pH", "pCO₂", "Exceso base"],
    "Plaquetas":                ["Leucocitos", "Hematocrito"],
    "Sodio":                    ["Potasio", "Cloro"],
    "Potasio":                  ["Sodio", "Cloro"],
    "Ácido úrico":              ["Creatinina"],
    "Albúmina":                 ["Proteínas totales", "Globulinas"],
    "Hematocrito":              ["Hemoglobina", "Eritrocitos", "VCM"],
}


# ── render_results: Panel global + Hero + Barra + Contexto + Microcopy ───────
def render_results(data: PatientInput, margin_pct: float):
    MARKERS = [
        ("Hemoglobina",            data.hemoglobina,      get_effective_range("hemoglobina",    data.sexo)),
        ("Glucosa",                data.glucosa,           get_effective_range("glucosa",        data.sexo)),
        ("Colesterol total",       data.col_total,         get_effective_range("col_total",      data.sexo)),
        ("HDL",                    data.hdl,               get_effective_range("hdl",            data.sexo)),
        ("LDL",                    data.ldl,               get_effective_range("ldl",            data.sexo)),
        ("Triglicéridos",          data.trigliceridos,     get_effective_range("trigliceridos",  data.sexo)),
        ("Creatinina",             data.creatinina,        get_effective_range("creatinina",     data.sexo)),
        ("TSH",                    data.tsh,               get_effective_range("tsh",            data.sexo)),
        ("T4 libre",               data.t4_libre,          get_effective_range("t4_libre",       data.sexo)),
        ("Vitamina D",             data.vitamina_d,        get_effective_range("vitamina_d",     data.sexo)),
        ("Vitamina B12",           data.vitamina_b12,      get_effective_range("vitamina_b12",   data.sexo)),
        ("Ácido úrico",            data.acido_urico,       get_effective_range("acido_urico",    data.sexo)),
        ("VHS",                    data.vhs,               get_effective_range("vhs",            data.sexo)),
        ("Bilirrubina total",      data.bil_total,         get_effective_range("bil_total",      data.sexo)),
        ("Bilirrubina directa",    data.bil_directa,       get_effective_range("bil_directa",    data.sexo)),
        ("Bilirrubina indirecta",  data.bil_indirecta,     get_effective_range("bil_indirecta",  data.sexo)),
        ("Fosfatasa alcalina",     data.fosfatasa_alc,     get_effective_range("fosfatasa_alc",  data.sexo)),
        ("GOT (AST)",              data.got_ast,           get_effective_range("got_ast",        data.sexo)),
        ("GPT (ALT)",              data.gpt_alt,           get_effective_range("gpt_alt",        data.sexo)),
        ("Proteínas totales",      data.prot_totales,      get_effective_range("prot_totales",   data.sexo)),
        ("Albúmina",               data.albumina,          get_effective_range("albumina",       data.sexo)),
        ("GGT",                    data.ggt,               get_effective_range("ggt",            data.sexo)),
        ("Globulinas",             data.globulinas,        get_effective_range("globulinas",     data.sexo)),
        ("Relación Alb/Glob",      data.rel_albumina_glob, get_effective_range("rel_albumina_glob", data.sexo)),
        ("TP (s)",                 data.tp_seg,            get_effective_range("tp_seg",         data.sexo)),
        ("TP (%)",                 data.tp_pct,            get_effective_range("tp_pct",         data.sexo)),
        ("INR",                    data.inr,               get_effective_range("inr",            data.sexo)),
        ("Sodio",                  data.sodio,             get_effective_range("sodio",          data.sexo)),
        ("Potasio",                data.potasio,           get_effective_range("potasio",        data.sexo)),
        ("Cloro",                  data.cloro,             get_effective_range("cloro",          data.sexo)),
        ("Nitrógeno ureico / BUN", data.urea_bun,          get_effective_range("urea_bun",       data.sexo)),
        ("VFG (CKD-EPI)",          data.vfg_ckd_epi,       get_effective_range("vfg_ckd_epi",    data.sexo)),
        ("Fósforo",                data.fosforo,           get_effective_range("fosforo",        data.sexo)),
        ("Magnesio",               data.magnesio,          get_effective_range("magnesio",       data.sexo)),
        ("Procalcitonina",         data.procalcitonina,    get_effective_range("procalcitonina", data.sexo)),
        ("PCR",                    data.pcr,               get_effective_range("pcr",            data.sexo)),
        ("Ferritina",              data.ferritina,         get_effective_range("ferritina",      data.sexo)),
        ("Eritrocitos",            data.eritrocitos,       get_effective_range("eritrocitos",    data.sexo)),
        ("Hematocrito",            data.hematocrito,       get_effective_range("hematocrito",    data.sexo)),
        ("VCM",                    data.vcm,               get_effective_range("vcm",            data.sexo)),
        ("HCM",                    data.hcm,               get_effective_range("hcm",            data.sexo)),
        ("CHCM",                   data.chcm,              get_effective_range("chcm",           data.sexo)),
        ("Plaquetas",              data.plaquetas,         get_effective_range("plaquetas",      data.sexo)),
        ("VPM",                    data.vpm,               get_effective_range("vpm",            data.sexo)),
        ("Leucocitos",             data.leucocitos,        get_effective_range("leucocitos",     data.sexo)),
        ("RDW-CV",                 data.rdw_cv,            get_effective_range("rdw_cv",         data.sexo)),
        ("Neutrófilos (%)",        data.neutro,            get_effective_range("neutro",         data.sexo)),
        ("Linfocitos (%)",         data.linf,              get_effective_range("linf",           data.sexo)),
        ("Monocitos (%)",          data.mono,              get_effective_range("mono",           data.sexo)),
        ("Eosinófilos (%)",        data.eos,               get_effective_range("eos",            data.sexo)),
        ("Basófilos (%)",          data.baso,              get_effective_range("baso",           data.sexo)),
        ("TTPA",                   data.ttpa,              get_effective_range("ttpa",           data.sexo)),
        ("pH",                     data.ph,                get_effective_range("ph",             data.sexo)),
        ("pCO₂",                   data.pco2,              get_effective_range("pco2",           data.sexo)),
        ("pO₂",                    data.po2,               get_effective_range("po2",            data.sexo)),
        ("HCO₃⁻",                  data.hco3,              get_effective_range("hco3",           data.sexo)),
        ("Exceso base",            data.exceso_base,       get_effective_range("exceso_base",    data.sexo)),
        ("Saturación O₂",          data.sat_o2,            get_effective_range("sat_o2",         data.sexo)),
        ("TCO₂",                   data.tco2,              get_effective_range("tco2",           data.sexo)),
        ("FIO₂",                   data.fio2,              get_effective_range("fio2",           data.sexo)),
        ("Presión barométrica",    data.pres_baro,         get_effective_range("pres_baro",      data.sexo)),
        ("Temperatura (°C)",       data.temp,              get_effective_range("temp",           data.sexo)),
    ]

    # ── Clasificación silenciosa ───────────────────────────────────────────────
    classified = []
    for label, value, ref in MARKERS:
        status = None if (value is None or value == 0.0) else classify_with_margin(value, ref, margin_pct)
        classified.append((label, value, ref, status))

    altered  = [(l, v, r, s) for l, v, r, s in classified if s in ("alto", "bajo", "limite")]
    normals  = [(l, v, r, s) for l, v, r, s in classified if s == "normal"]

    n_fuera  = sum(1 for _, _, _, s in altered if s in ("alto", "bajo"))
    n_limite = sum(1 for _, _, _, s in altered if s == "limite")
    n_normal = len(normals)
    n_total  = n_fuera + n_limite + n_normal

    # ── Provenance ────────────────────────────────────────────────────────────
    if _using_lab_ranges:
        st.info(
            f"Se usaron los rangos de tu laboratorio para {len(extracted_ranges)} parámetro(s). "
            "Para los demás se aplicaron rangos internos de SeraphAID."
        )

    # ── Fase 0: Panel global de estado ────────────────────────────────────────
    if n_fuera >= 2:
        _icon, _titulo, _color = "🔴", "Requiere evaluación médica", "#EF4444"
        _sub = "Se detectan varios valores fuera de rango. Es recomendable revisarlos con un profesional de salud."
    elif n_fuera == 1 or n_limite > 0:
        _icon, _titulo, _color = "🟡", "Requiere seguimiento", "#F59E0B"
        _sub = "Hay valores que conviene revisar con tu médico. No es necesariamente grave, pero merece atención."
    else:
        _icon, _titulo, _color = "🟢", "Estable", "#10B981"
        _sub = "Todos tus resultados se encuentran dentro de los rangos esperados."

    st.markdown(f"""
<div style="background:{COLOR['card']};border:2px solid {_color};border-radius:12px;
            padding:1.1rem 1.5rem;margin-bottom:1.2rem;">
  <span style="font-size:2rem;vertical-align:middle;">{_icon}</span>
  <span style="font-size:1.35rem;font-weight:700;color:{_color};margin-left:.5rem;
               vertical-align:middle;">{_titulo}</span>
  <p style="color:{COLOR['muted']};margin:.5rem 0 0;font-size:.9rem;">{_sub}</p>
</div>""", unsafe_allow_html=True)

    # ── Fase 1: Hero de métricas ───────────────────────────────────────────────
    if n_total > 0:
        _c1, _c2, _c3 = st.columns(3)
        _c1.metric("🔴 Fuera de rango", n_fuera)
        _c2.metric("🟡 En límite",      n_limite)
        _c3.metric("🟢 Normales",       n_normal)

        if n_fuera == 0 and n_limite == 0:
            _msg = "Todos tus resultados están dentro de los rangos esperados."
        elif n_fuera == 0:
            _msg = "La mayoría de tus resultados están dentro de rango. Hay algunos valores que conviene revisar."
        else:
            _msg = "Se detectan valores fuera de rango. Conviene revisarlos con un profesional de salud."
        st.caption(_msg)

    # ── Fase 2: Barra proporcional de colores ─────────────────────────────────
    if n_total > 0:
        _pf = max(n_fuera  * 100 // n_total, 1 if n_fuera  else 0)
        _pl = max(n_limite * 100 // n_total, 1 if n_limite else 0)
        _pn = 100 - _pf - _pl
        _seg_f = f'<div style="flex:{_pf};background:#EF4444;min-width:{_pf}%;"></div>' if n_fuera  else ""
        _seg_l = f'<div style="flex:{_pl};background:#F59E0B;min-width:{_pl}%;"></div>' if n_limite else ""
        _seg_n = f'<div style="flex:{_pn};background:#10B981;min-width:{_pn}%;"></div>' if n_normal else ""
        st.markdown(f"""
<div style="margin:.8rem 0 1.4rem;">
  <div style="display:flex;height:14px;border-radius:7px;overflow:hidden;gap:2px;">
    {_seg_f}{_seg_l}{_seg_n}
  </div>
  <div style="display:flex;gap:1.4rem;margin-top:.4rem;font-size:.78rem;color:{COLOR['muted']};">
    <span>🔴 {n_fuera} fuera de rango</span>
    <span>🟡 {n_limite} en límite</span>
    <span>🟢 {n_normal} normal{"es" if n_normal!=1 else ""}</span>
  </div>
</div>""", unsafe_allow_html=True)

    # ── Fase 3: Lo más relevante (top 5 alterados) ────────────────────────────
    _top = [t for t in altered if t[3] in ("alto", "bajo")][:5]
    _top += [t for t in altered if t[3] == "limite"][:max(0, 5 - len(_top))]
    _top = _top[:5]

    if _top:
        st.markdown("#### 📌 Lo más relevante de tus resultados")
        for _lbl, _val, _ref, _st in _top:
            _bc = "#EF4444" if _st in ("alto", "bajo") else "#F59E0B"
            _ic = "🔴" if _st in ("alto", "bajo") else "🟡"
            _dir = "↑ alto" if _st == "alto" else ("↓ bajo" if _st == "bajo" else "en límite")
            _lo, _hi = (_ref[0], _ref[1]) if _ref else ("—", "—")
            st.markdown(f"""
<div style="background:{COLOR['bg2']};border-left:3px solid {_bc};border-radius:0 8px 8px 0;
            padding:.55rem .9rem;margin:.25rem 0;">
  <strong style="color:{COLOR['text']};">{_ic} {_lbl}</strong>
  <span style="color:{COLOR['muted']};margin-left:.8rem;font-size:.88rem;">{_val} · {_dir} · ref: {_lo}–{_hi}</span>
</div>""", unsafe_allow_html=True)
        st.markdown("")

    st.divider()

    # ── Parámetros alterados + contexto clínico (Fase 7) ──────────────────────
    if altered:
        st.markdown("#### 🔍 Parámetros que requieren atención")
        for _lbl, _val, _ref, _st in altered:
            show_line(_lbl, _val, _ref, margin_pct)
            _rel = _RELATED.get(_lbl, [])
            if _rel:
                st.caption(f"💡 Conviene evaluar junto con: {', '.join(_rel)}")

    # ── Ver todos los normales ─────────────────────────────────────────────────
    if normals:
        with st.expander(f"✅ Ver todos los resultados normales ({n_normal})", expanded=False):
            for _lbl, _val, _ref, _st in normals:
                show_line(_lbl, _val, _ref, margin_pct)

    # ── Explicaciones de alterados ─────────────────────────────────────────────
    detalles = [(label, status) for label, _, _, status in altered]
    if detalles or not altered:
        st.markdown("#### 📋 Qué significa cada resultado")
        consejo = construir_resumen_detallado(detalles)
        st.markdown(consejo)

    # ── Microcopy clínico (Fase 4) ─────────────────────────────────────────────
    if altered:
        st.markdown(f"""
<div style="background:{COLOR['bg2']};border:1px solid {COLOR['border']};border-radius:8px;
            padding:.75rem 1rem;margin-top:1rem;">
  <span style="color:{COLOR['muted']};font-size:.85rem;">
    💬 Estos valores son orientativos. No es necesariamente grave tener un valor fuera de rango —
    el contexto clínico es lo que importa. Si tienes síntomas o dudas, consulta con un profesional de salud.
  </span>
</div>""", unsafe_allow_html=True)

    # ── Interpretación IA opcional ────────────────────────────────────────────
    _ai_name = st.session_state.get("_ai_provider_name", "rules")
    if _ai_name != "rules" and detalles:
        with st.expander("🤖 Interpretación adicional (IA)", expanded=False):
            with st.spinner("Consultando IA..."):
                try:
                    _ai_result = get_provider(_ai_name).interpret(consejo)
                    st.markdown(_ai_result)
                    st.caption("⚠️ Esta interpretación es orientativa y no reemplaza la evaluación profesional.")
                except Exception as _e:
                    st.warning(f"La interpretación IA no está disponible en este momento: {_e}")

    # TTS desactivado — ver DECISIONS.md D-010
    if ENABLE_TTS:
        pass  # código TTS preservado pero inactivo

# ── Submit handler ────────────────────────────────────────────────────────────
def _f(v) -> Optional[float]:
    """Convierte a float; retorna None si es 0 (campo no ingresado)."""
    try:
        result = float(v)
        return result if result != 0.0 else None
    except (TypeError, ValueError):
        return None

if submitted:
    try:
        data = PatientInput(
            edad=int(edad), sexo=sexo or None,
            hemoglobina=_f(hemoglobina),
            glucosa=_f(glucosa),
            col_total=_f(col_total),
            hdl=_f(hdl),
            ldl=_f(ldl),
            trigliceridos=_f(trigliceridos),
            creatinina=_f(creatinina),
            bil_total=_f(bil_total)         if 'bil_total'      in locals() else None,
            bil_directa=_f(bil_directa)     if 'bil_directa'    in locals() else None,
            bil_indirecta=_f(bil_indirecta) if 'bil_indirecta'  in locals() else None,
            fosfatasa_alc=_f(fosfatasa_alc) if 'fosfatasa_alc'  in locals() else None,
            got_ast=_f(got_ast)             if 'got_ast'        in locals() else None,
            gpt_alt=_f(gpt_alt)             if 'gpt_alt'        in locals() else None,
            prot_totales=_f(prot_totales)   if 'prot_totales'   in locals() else None,
            albumina=_f(albumina)           if 'albumina'       in locals() else None,
            ggt=_f(ggt)                     if 'ggt'            in locals() else None,
            globulinas=_f(globulinas)       if 'globulinas'     in locals() else None,
            rel_albumina_glob=_f(rel_albumina_glob) if 'rel_albumina_glob' in locals() else None,
            tp_seg=_f(tp_seg)               if 'tp_seg'         in locals() else None,
            tp_pct=_f(tp_pct)               if 'tp_pct'         in locals() else None,
            inr=_f(inr)                     if 'inr'            in locals() else None,
            sodio=_f(sodio)                 if 'sodio'          in locals() else None,
            potasio=_f(potasio)             if 'potasio'        in locals() else None,
            cloro=_f(cloro)                 if 'cloro'          in locals() else None,
            urea_bun=_f(urea_bun)           if 'urea_bun'       in locals() else None,
            vfg_ckd_epi=_f(vfg_ckd_epi)    if 'vfg_ckd_epi'   in locals() else None,
            fosforo=_f(fosforo)             if 'fosforo'        in locals() else None,
            magnesio=_f(magnesio)           if 'magnesio'       in locals() else None,
            procalcitonina=_f(procalcitonina) if 'procalcitonina' in locals() else None,
            pcr=_f(pcr)                     if 'pcr'            in locals() else None,
            ferritina=_f(ferritina)         if 'ferritina'      in locals() else None,
            vhs=_f(vhs)                     if 'vhs'            in locals() else None,
            eritrocitos=_f(eritrocitos)     if 'eritrocitos'    in locals() else None,
            hematocrito=_f(hematocrito)     if 'hematocrito'    in locals() else None,
            vcm=_f(vcm)                     if 'vcm'            in locals() else None,
            hcm=_f(hcm)                     if 'hcm'            in locals() else None,
            chcm=_f(chcm)                   if 'chcm'           in locals() else None,
            plaquetas=_f(plaquetas)         if 'plaquetas'      in locals() else None,
            vpm=_f(vpm)                     if 'vpm'            in locals() else None,
            leucocitos=_f(leucocitos)       if 'leucocitos'     in locals() else None,
            rdw_cv=_f(rdw_cv)               if 'rdw_cv'         in locals() else None,
            neutro=_f(neutro)               if 'neutro'         in locals() else None,
            linf=_f(linf)                   if 'linf'           in locals() else None,
            mono=_f(mono)                   if 'mono'           in locals() else None,
            eos=_f(eos)                     if 'eos'            in locals() else None,
            baso=_f(baso)                   if 'baso'           in locals() else None,
            ttpa=_f(ttpa)                   if 'ttpa'           in locals() else None,
            tsh=_f(tsh)                     if 'tsh'            in locals() else None,
            t4_libre=_f(t4_libre)           if 't4_libre'       in locals() else None,
            vitamina_d=_f(vitamina_d)       if 'vitamina_d'     in locals() else None,
            vitamina_b12=_f(vitamina_b12)   if 'vitamina_b12'   in locals() else None,
            acido_urico=_f(acido_urico)     if 'acido_urico'    in locals() else None,
            ph=_f(ph)                       if 'ph'             in locals() else None,
            pco2=_f(pco2)                   if 'pco2'           in locals() else None,
            po2=_f(po2)                     if 'po2'            in locals() else None,
            hco3=_f(hco3)                   if 'hco3'           in locals() else None,
            exceso_base=_f(exceso_base)     if 'exceso_base'    in locals() else None,
            sat_o2=_f(sat_o2)               if 'sat_o2'         in locals() else None,
            tco2=_f(tco2)                   if 'tco2'           in locals() else None,
            fio2=_f(fio2)                   if 'fio2'           in locals() else None,
            pres_baro=_f(pres_baro)         if 'pres_baro'      in locals() else None,
            temp=_f(temp)                   if 'temp'           in locals() else None,
        )
        st.session_state["last_data"] = data.dict()
        st.session_state["show_results"] = True
        render_results(data, DEFAULT_MARGIN_PCT)
        try:
            _storage.save_session("anonymous", st.session_state["session_id"], {
                "session_id": st.session_state["session_id"],
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "patient_age": data.edad,
                "patient_sex": data.sexo,
                "data": data.dict(),
            })
        except Exception:
            pass
    except Exception as e:
        st.error(f"Error al procesar los datos: {e}")

elif st.session_state.get("show_results"):
    try:
        last = st.session_state.get("last_data")
        if last:
            data = PatientInput(**last)
            render_results(data, DEFAULT_MARGIN_PCT)
    except Exception as e:
        st.error(f"Error al cargar resultados previos: {e}")
