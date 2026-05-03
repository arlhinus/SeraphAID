"""
modules/medications.py — Módulo B: búsqueda y explicación de medicamentos.
Sprint 5-B: dataset expandido (78 medicamentos), nuevo campo cuando_consultar,
nivel_riesgo, filtro por grupo, y contexto para futura integración IA.
Sprint 6-F: columnas de trazabilidad (fuente_base, url_fuente, fecha_revision,
nivel_confianza, pais_contexto).
"""
import unicodedata
import logging
import pandas as pd
import streamlit as st

logger = logging.getLogger(__name__)

MEDS_PATH = "data/medicamentos.csv"

DISCLAIMER = (
    "⚠️ Esta información es orientativa y educativa. "
    "No reemplaza la indicación ni el consejo de su médico o farmacéutico. "
    "Consulte siempre con un profesional de la salud antes de iniciar, modificar o suspender un medicamento."
)

_EMPTY_COLS = [
    "nombre", "nombre_generico", "grupo", "para_que_sirve",
    "precauciones", "efectos_frecuentes", "cuando_consultar", "nivel_riesgo",
    "fuente_base", "url_fuente", "fecha_revision", "nivel_confianza", "pais_contexto",
]


def _norm(s: str) -> str:
    """Normaliza texto: minúsculas, sin tildes ni caracteres especiales."""
    return unicodedata.normalize("NFD", s or "").encode("ascii", "ignore").decode("ascii").lower().strip()


@st.cache_data
def cargar_medicamentos(path: str = MEDS_PATH) -> pd.DataFrame:
    try:
        df = pd.read_csv(path)
        df.columns = [c.strip().lower() for c in df.columns]
        for col in ("nombre", "nombre_generico", "grupo", "nivel_riesgo"):
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
        # Normalizar nivel_riesgo a minúsculas
        if "nivel_riesgo" in df.columns:
            df["nivel_riesgo"] = df["nivel_riesgo"].str.lower()
        return df
    except Exception as e:
        logger.warning(f"No se pudo cargar {path}: {e}")
        return pd.DataFrame(columns=_EMPTY_COLS)


def buscar_medicamento(query: str, df: pd.DataFrame) -> pd.DataFrame:
    """Retorna filas cuyo nombre o nombre genérico contiene la búsqueda."""
    if not query or df.empty:
        return pd.DataFrame()
    q = _norm(query)
    mask = (
        df["nombre"].apply(lambda x: q in _norm(x)) |
        df["nombre_generico"].apply(lambda x: q in _norm(x))
    )
    return df[mask].reset_index(drop=True)


def filtrar_por_grupo(grupo: str, df: pd.DataFrame) -> pd.DataFrame:
    """Filtra el DataFrame por grupo farmacológico. 'Todos' devuelve el df completo."""
    if not grupo or grupo == "Todos" or df.empty:
        return df
    return df[df["grupo"] == grupo].reset_index(drop=True)


def construir_contexto_med(row: pd.Series) -> str:
    """
    Construye un string estructurado para futura integración con AI provider.
    Mismo patrón que construir_resumen_detallado en exam_interpreter.
    """
    return (
        f"Medicamento: {row.get('nombre', '')}\n"
        f"Grupo: {row.get('grupo', '')}\n"
        f"Para qué sirve: {row.get('para_que_sirve', '')}\n"
        f"Precauciones: {row.get('precauciones', '')}\n"
        f"Efectos frecuentes: {row.get('efectos_frecuentes', '')}\n"
        f"Cuándo consultar: {row.get('cuando_consultar', '')}\n"
        f"Nivel de riesgo: {row.get('nivel_riesgo', '')}\n"
    )
