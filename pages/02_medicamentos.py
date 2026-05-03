"""
pages/02_medicamentos.py — Módulo B: Medicamentos.
Sprint 8-FE: topbar unificado, sidebar eliminado, controles inline.
"""
import pandas as pd
import streamlit as st
from modules.medications import (
    cargar_medicamentos, buscar_medicamento, filtrar_por_grupo,
    construir_contexto_med, DISCLAIMER,
)
from modules.ai.registry import get_provider, list_available_providers
from modules.ui_components import render_topbar, COLOR

st.set_page_config(
    page_title="SeraphAID · Medicamentos",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="collapsed",
)
render_topbar("medicamentos")

# ── Carga de datos ─────────────────────────────────────────────────────────────
df_meds = cargar_medicamentos()

if df_meds.empty:
    st.error("No se pudo cargar la base de medicamentos. Verifique que exista data/medicamentos.csv.")
    st.stop()

# ── Controles inline: filtro por grupo + IA ───────────────────────────────────
_fc1, _fc2, _fc3 = st.columns([2, 2, 5])
with _fc1:
    grupos_disponibles = ["Todos"] + sorted(df_meds["grupo"].dropna().unique().tolist())
    grupo_sel = st.selectbox("Grupo farmacológico", options=grupos_disponibles)
with _fc2:
    _ai_labels = {
        "rules":     "Solo datos locales (sin IA)",
        "openai":    "OpenAI (GPT-4o)",
        "anthropic": "Anthropic (Claude)",
    }
    _ai_available = list_available_providers()
    if len(_ai_available) > 1:
        st.selectbox(
            "🤖 Proveedor IA",
            options=_ai_available,
            format_func=lambda p: _ai_labels.get(p, p),
            key="_ai_provider_name",
        )
    else:
        if "_ai_provider_name" not in st.session_state:
            st.session_state["_ai_provider_name"] = "rules"
        st.caption("IA no disponible · configura una API key en .env")

# ── Búsqueda ───────────────────────────────────────────────────────────────────
query = st.text_input(
    "Buscar medicamento",
    placeholder="Ej: paracetamol, omeprazol, metformina, atorvastatina...",
    help="Puede buscar por nombre comercial o nombre genérico.",
)

df_filtrado = filtrar_por_grupo(grupo_sel, df_meds)

# ── Resolución de resultados ───────────────────────────────────────────────────
resultados: pd.DataFrame = pd.DataFrame()

if not query and grupo_sel == "Todos":
    st.info(f"Ingrese el nombre de un medicamento o seleccione un grupo. Base de datos: **{len(df_meds)} medicamentos**.")
    st.divider()
    st.caption(DISCLAIMER)
    st.stop()

if not query and grupo_sel != "Todos":
    st.info(f"**{len(df_filtrado)} medicamentos** en el grupo: **{grupo_sel}**")
    med_sel = st.selectbox(
        "Seleccionar medicamento:",
        options=df_filtrado["nombre"].tolist(),
        index=None,
        placeholder="Haga clic para elegir un medicamento...",
    )
    if med_sel is None:
        st.divider()
        st.caption(DISCLAIMER)
        st.stop()
    resultados = df_filtrado[df_filtrado["nombre"] == med_sel].reset_index(drop=True)
else:
    resultados = buscar_medicamento(query, df_filtrado)
    if resultados.empty:
        st.warning(
            f"No se encontró **{query}** en la base de datos"
            + (f" para el grupo **{grupo_sel}**" if grupo_sel != "Todos" else "")
            + ". Consulte a su médico o farmacéutico."
        )
        st.divider()
        st.caption(DISCLAIMER)
        st.stop()

# ── Fichas de resultados ──────────────────────────────────────────────────────
_RIESGO_ICON  = {"bajo": "🟢", "moderado": "🟠", "alto": "🔴"}
_RIESGO_LABEL = {
    "bajo":     "Riesgo bajo",
    "moderado": "Riesgo moderado",
    "alto":     "Riesgo alto — requiere supervisión médica estricta",
}
_CONFIANZA_LABEL = {
    "revision_inicial": "Revisión inicial (orientativa)",
    "revisado":         "Revisado",
    "verificado":       "Verificado con fuente externa",
}

for _, row in resultados.iterrows():
    nivel = str(row.get("nivel_riesgo", "")).lower()
    icono = _RIESGO_ICON.get(nivel, "⚪")
    label_riesgo = _RIESGO_LABEL.get(nivel, nivel)

    with st.container(border=True):
        col_titulo, col_riesgo = st.columns([3, 1])
        with col_titulo:
            st.subheader(f"💊 {row['nombre']}")
            if row.get("nombre_generico") and row["nombre_generico"] != row["nombre"]:
                st.caption(f"Nombre genérico: {row['nombre_generico']}")
            if row.get("grupo"):
                st.caption(f"Grupo: {row['grupo']}")
        with col_riesgo:
            st.markdown(f"**{icono} {label_riesgo}**")

        st.markdown("**¿Para qué sirve?**")
        st.write(row.get("para_que_sirve", "—"))

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("**Precauciones generales**")
            st.write(row.get("precauciones", "—"))
        with col_b:
            st.markdown("**Efectos frecuentes**")
            st.write(row.get("efectos_frecuentes", "—"))

        st.markdown("**🚨 ¿Cuándo consultar a su médico?**")
        st.warning(row.get("cuando_consultar", "Ante cualquier síntoma inusual, consulte a su médico."))

        # ── Interpretación IA opcional ──────────────────────────────────────
        _ai_name = st.session_state.get("_ai_provider_name", "rules")
        if _ai_name != "rules":
            with st.expander("🤖 Explicación adicional (IA)", expanded=False):
                with st.spinner("Consultando IA..."):
                    try:
                        _ctx = construir_contexto_med(row)
                        _ai_result = get_provider(_ai_name).interpret(_ctx)
                        st.markdown(_ai_result)
                        st.caption("⚠️ Esta interpretación es orientativa y no reemplaza la evaluación profesional.")
                    except Exception as _e:
                        st.warning(f"La interpretación IA no está disponible en este momento: {_e}")

        # ── Trazabilidad / Fuente ───────────────────────────────────────────
        _fuente   = str(row.get("fuente_base", "") or "curada_local_v1")
        _url      = str(row.get("url_fuente", "") or "")
        _fecha    = str(row.get("fecha_revision", "") or "—")
        _conf_raw = str(row.get("nivel_confianza", "") or "")
        _conf     = _CONFIANZA_LABEL.get(_conf_raw, _conf_raw or "—")
        _pais     = str(row.get("pais_contexto", "") or "—")

        with st.expander("📋 Fuente de información", expanded=False):
            st.caption(f"**Fuente base:** {_fuente}")
            st.caption(f"**Última revisión:** {_fecha}  |  **Contexto:** {_pais}")
            st.caption(f"**Nivel de confianza:** {_conf}")
            if _url.startswith("http"):
                st.link_button("Ver fuente externa", _url)
            else:
                st.caption("_Sin URL de fuente registrada para este medicamento._")

st.divider()
st.caption(DISCLAIMER)
