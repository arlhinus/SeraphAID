"""
modules/file_extractor.py — Extracción de texto y valores desde archivos de examen.
Sprint 6: matching línea-a-línea, corrección HDL/BUN, nuevos marcadores (TSH, VHS, etc.).

Errores clínicos corregidos:
- HDL: ya no captura "Índice Col/HDL" ni "Razón Col/HDL" como valor de HDL.
- Urea/BUN: alias específicos ("nitrogeno ureico", "bun") en lugar del genérico "urea"
  que puede confundirse con "Uremia" (reportada en mmol/L por algunos laboratorios).
- bil_total: agregado (estaba ausente en versión anterior).
- Aliases ordenados por especificidad: los más específicos van primero.
"""
import io
import re
import logging
import unicodedata
from typing import Dict, Tuple

import pdfplumber
import pytesseract
import streamlit as st
from PIL import Image

logger = logging.getLogger(__name__)


def safe_text_normalize(s: str) -> str:
    if s is None:
        return ""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return s


def extract_text_from_upload(file) -> str:
    """Extrae texto del PDF o imagen usando pdfplumber / Tesseract."""
    if file is None:
        return ""
    try:
        content = file.read()
        if not content:
            return ""
        if getattr(file, "type", "") == "application/pdf" or file.name.lower().endswith(".pdf"):
            text = ""
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                for page in pdf.pages:
                    text += (page.extract_text() or "") + "\n"
            return safe_text_normalize(text)
        else:
            image = Image.open(io.BytesIO(content)).convert("RGB")
            try:
                text = pytesseract.image_to_string(image, lang="spa")
            except Exception:
                text = pytesseract.image_to_string(image)
            return safe_text_normalize(text)
    except Exception as e:
        st.warning(f"No pude extraer texto del archivo: {e}")
        return ""


# ── Detección de contexto de índice/razón ────────────────────────────────────
# Si una línea contiene estas palabras, NO es el valor directo del analito.
_RATIO_KEYWORDS = {"relaci", "indice", "indic", "razon", "ratio", "/hdl", "/ldl", "col/h", "total/h"}

def _is_ratio_line(line: str) -> bool:
    low = line.lower()
    return any(kw in low for kw in _RATIO_KEYWORDS)


# ── Aliases por marcador ──────────────────────────────────────────────────────
# Orden de prioridad: más específicos primero.
# Para HDL/LDL: se verifica que la línea no sea un índice/razón antes de capturar.
# Para urea_bun: se usa "nitrogeno ureico" / "bun" y NO "urea" solo (evita "uremia" mmol/L).
_ALIASES: Dict[str, list] = {
    # Glucosa
    "glucosa":          ["glucosa en ayunas", "glucosa ayunas", "glucosa", "glucose"],
    # Lípidos — HDL y LDL con protección anti-ratio
    "col_total":        ["colesterol total", "cholesterol total", "colesterol"],
    "hdl":              ["colesterol hdl", "hdl colesterol", "c-hdl", "hdl-c", "hdl"],
    "ldl":              ["colesterol ldl", "ldl colesterol", "c-ldl", "ldl-c", "ldl"],
    "trigliceridos":    ["trigliceridos", "trigliceridos", "triglycerides"],
    # Hemoglobina / hemograma
    "hemoglobina":      ["hemoglobina", "hemoglobin", "hgb"],
    "eritrocitos":      ["eritrocitos", "globulos rojos", "red blood cells", "rbc"],
    "hematocrito":      ["hematocrito", "hematocrit", "hct"],
    "vcm":              ["volumen corpuscular medio", "vcm", "mean corpuscular volume", "mcv"],
    "hcm":              ["hemoglobina corpuscular media", "hcm", "mean corpuscular hemoglobin", "mch"],
    "chcm":             ["concentracion de hemoglobina corpuscular media", "chcm", "mchc"],
    "rdw_cv":           ["rdw-cv", "rdw cv", "rdw", "red cell distribution width"],
    "leucocitos":       ["leucocitos", "globulos blancos", "white blood cells", "wbc"],
    "plaquetas":        ["plaquetas", "platelets", "plt"],
    "vpm":              ["volumen plaquetario medio", "vpm", "mean platelet volume", "mpv"],
    # Diferencial
    "neutro":           ["neutrofilos", "neutrofilos", "neutrophils"],
    "linf":             ["linfocitos", "lymphocytes"],
    "mono":             ["monocitos", "monocytes"],
    "eos":              ["eosinofilos", "eosinofilos", "eosinophils"],
    "baso":             ["basofilos", "basofilos", "basophils"],
    # Renal — urea_bun con aliases específicos (NO "urea" genérico)
    "creatinina":       ["creatinina", "creatinine", "creat"],
    "urea_bun":         ["nitrogeno ureico", "nitrogen ureico", "n. ureico", "n ureico",
                         "blood urea nitrogen", "bun", "urea nitrogeno"],
    "vfg_ckd_epi":      ["tasa de filtracion glomerular", "velocidad de filtracion glomerular",
                         "vfg", "tfg", "ckd-epi", "glomerular filtration rate", "gfr"],
    # Hepático — bil_total antes de bil_directa/indirecta
    "bil_total":        ["bilirrubina total", "bilirubin total", "total bilirubin", "bt"],
    "bil_directa":      ["bilirrubina directa", "bilirrubina conjugada", "direct bilirubin", "bd"],
    "bil_indirecta":    ["bilirrubina indirecta", "bilirrubina no conjugada", "indirect bilirubin", "bi"],
    "fosfatasa_alc":    ["fosfatasa alcalina", "alkaline phosphatase", "alp"],
    "got_ast":          ["got (ast)", "got-ast", "aspartato aminotransferasa", "aspartate aminotransferase", "got", "ast"],
    "gpt_alt":          ["gpt (alt)", "gpt-alt", "alanina aminotransferasa", "alanine aminotransferase", "gpt", "alt"],
    "ggt":              ["gamma-glutamil transferasa", "gamma glutamil transferasa", "gamma gt",
                         "gamma-glutamyl transferase", "ggt"],
    "prot_totales":     ["proteinas totales", "proteinas totales", "total protein", "prot totales"],
    "albumina":         ["albumina", "albumina", "albumin"],
    "globulinas":       ["globulinas", "globulins"],
    "rel_albumina_glob":["relacion albumina/globulina", "relacion alb/glob", "albumin/globulin ratio", "a/g"],
    # Coagulación
    "tp_seg":           ["tiempo de protrombina (segundos)", "tiempo de protrombina", "tp (s)", "prothrombin time"],
    "tp_pct":           ["actividad de protrombina", "tp (%)", "tp porcentaje", "prothrombin activity"],
    "inr":              ["inr", "razon internacional normalizada", "international normalized ratio"],
    "ttpa":             ["tiempo de tromboplastina parcial activada", "ttpa", "tpta",
                         "aptt", "activated partial thromboplastin time"],
    # Electrolitos
    "sodio":            ["sodio", "sodium"],
    "potasio":          ["potasio", "potassium"],
    "cloro":            ["cloro", "cloruro", "chloride"],
    "fosforo":          ["fosforo", "fosforo", "phosphorus", "phosphate"],
    "magnesio":         ["magnesio", "magnesium"],
    # Inflamación
    "pcr":              ["proteina c reactiva ultrasensible", "proteina c reactiva",
                         "proteina c reactiva", "c-reactive protein", "pcr us", "crp", "pcr"],
    "procalcitonina":   ["procalcitonina", "procalcitonin", "pct"],
    "ferritina":        ["ferritina", "ferritin"],
    "vhs":              ["velocidad de sedimentacion globular", "velocidad eritrosedimentacion",
                         "vhs", "vsg", "eritrosedimentacion", "erythrocyte sedimentation rate", "esr"],
    # Tiroides
    "tsh":              ["tirotropina ultrasensible", "tsh ultrasensible", "tsh", "thyroid stimulating hormone"],
    "t4_libre":         ["tiroxina libre", "t4 libre", "t4l", "ft4", "free t4", "free thyroxine"],
    "t3_libre":         ["triyodotironina libre", "t3 libre", "t3l", "ft3"],
    # Vitaminas y minerales
    "vitamina_d":       ["25-hidroxi vitamina d", "25 oh vitamina d", "25-oh-d",
                         "vitamina d 25-oh", "vitamina d", "25-hydroxyvitamin d"],
    "vitamina_b12":     ["vitamina b12", "cobalamina", "vitamin b12", "b12"],
    "acido_urico":      ["acido urico", "acido urico", "uric acid", "urato"],
    # Gases (orden: alias más específico primero para evitar confusión de "ph" con "phosphate")
    "ph":               ["ph arterial", "ph venoso", "ph"],
    "pco2":             ["presion parcial de co2", "pco2", "partial pressure co2"],
    "po2":              ["presion parcial de o2", "po2", "partial pressure o2"],
    "hco3":             ["bicarbonato", "hco3", "bicarbonate"],
    "exceso_base":      ["exceso de base", "exceso base", "base excess"],
    "sat_o2":           ["saturacion de oxigeno", "saturacion o2", "saturacion o2",
                         "spo2", "oxygen saturation"],
    "tco2":             ["co2 total", "tco2", "total co2"],
    "fio2":             ["fraccion inspirada de oxigeno", "fio2", "fraction of inspired oxygen"],
    "pres_baro":        ["presion barometrica", "barometric pressure"],
    "temp":             ["temperatura corporal", "temperatura", "temperature"],
}

# Marcadores que requieren verificación anti-ratio antes de capturar
_CHECK_RATIO_CONTEXT = {"hdl", "ldl"}


def parse_values_and_ranges(text: str) -> Tuple[Dict[str, float], Dict[str, Tuple[float, float]]]:
    """
    Parsea texto de examen laboratorial.

    Devuelve:
      values: {marcador_canónico: valor_float}
      ranges: {marcador_canónico: (lo, hi)} — rangos del propio laboratorio

    Reglas:
    - Matching línea-a-línea para mayor precisión de contexto.
    - HDL/LDL: se rechazan líneas con indicadores de índice/razón.
    - Urea/BUN: usa aliases específicos, no "urea" genérico.
    - Aliases ordenados por especificidad (más específico primero).
    - Soporta coma decimal (3,5 → 3.5).
    """
    values: Dict[str, float] = {}
    ranges: Dict[str, Tuple[float, float]] = {}

    if not text:
        return values, ranges

    lines = [safe_text_normalize(line).lower() for line in text.split("\n") if line.strip()]

    for key, alias_list in _ALIASES.items():
        for alias in alias_list:
            alias_low = alias.lower()
            for line in lines:
                if alias_low not in line:
                    continue
                # Rechazar líneas de índice/razón para marcadores sensibles
                if key in _CHECK_RATIO_CONTEXT and _is_ratio_line(line):
                    logger.debug("HDL/LDL ratio context skipped: %s", line[:80])
                    continue
                # Capturar valor numérico (si no tenemos aún)
                if key not in values:
                    m = re.search(
                        rf"{re.escape(alias_low)}\s*[:\-]?\s*([0-9]+[,.]?[0-9]*)",
                        line
                    )
                    if m:
                        try:
                            values[key] = float(m.group(1).replace(",", "."))
                        except ValueError:
                            pass
                # Capturar rango de referencia (si no tenemos aún)
                if key not in ranges:
                    m_rng = re.search(
                        rf"{re.escape(alias_low)}.*?([0-9]+[,.]?[0-9]*)\s*[-–]\s*([0-9]+[,.]?[0-9]*)",
                        line
                    )
                    if m_rng:
                        try:
                            lo = float(m_rng.group(1).replace(",", "."))
                            hi = float(m_rng.group(2).replace(",", "."))
                            if lo < hi:
                                ranges[key] = (lo, hi)
                        except ValueError:
                            pass
            # Una vez encontrado valor Y rango con este alias, pasar al siguiente key
            if key in values and key in ranges:
                break

    return values, ranges
