# DECISIONS.md — SeraphAID
_Registro de decisiones arquitectónicas y de producto_

---

## D-001 · Mantener Streamlit como framework UI
**Fecha:** 2026-04-05
**Decisión:** Continuar con Streamlit para el MVP y las próximas fases.
**Razón:** La base de código existente funciona. Streamlit es óptimo para herramientas de información de datos en Python local. El overhead de migrar a FastAPI+React no está justificado en este punto.
**Revisable cuando:** La app necesite multi-usuario, autenticación real, o UX compleja (ej. flujos multi-paso con animaciones).

---

## D-002 · Refactor modular progresivo, no reescritura total
**Fecha:** 2026-04-05
**Decisión:** Extraer lógica a módulos gradualmente, manteniendo `app.py` funcional en todo momento.
**Razón:** La app actual corre. Una reescritura total rompe el trabajo existente y no agrega valor inmediato.
**Plan:** Cada sprint extrae un módulo. `app.py` pasa de ser todo-en-uno a ser orquestador.

---

## D-003 · El disclaimer de "no reemplaza atención médica" es no negociable
**Fecha:** 2026-04-05
**Decisión:** Todo output del sistema debe incluir disclaimer explícito. El sistema nunca usará lenguaje diagnóstico definitivo.
**Razón:** Requisito de seguridad y ético fundamental. Ver SAFETY_GUARDRAILS.md.

---

## D-004 · LLM como capa opcional, no reemplaza las reglas
**Fecha:** 2026-04-05
**Decisión:** La interpretación por reglas (rangos + GENERIC) se mantiene siempre disponible. El LLM es una capa adicional enriquecedora.
**Razón:** Permite funcionar sin API key, reduce dependencia de terceros, mantiene predictibilidad.

---

## D-005 · GENERIC dict se moverá a explicaciones.csv
**Fecha:** 2026-04-05
**Decisión:** Migrar las ~300 líneas del dict GENERIC en app.py al archivo explicaciones.csv (ampliado).
**Razón:** Datos en código son difíciles de mantener. CSV es editable sin tocar código.
**Pendiente:** Confirmar con usuario (pregunta 2 de NEXT_STEPS Bloque 2).

---

## D-006 · Bug normalize_marker() identificado
**Fecha:** 2026-04-05
**Decisión:** Corregir agregando `return mapping.get(n, n)` al final de la función.
**Impacto actual:** El CSV de explicaciones.csv nunca es consultado. Todos los lookups caen al GENERIC dict. La app funciona pero no usa el archivo CSV.

---

## D-007 · API key hardcodeada en línea 1056 de app.py
**Fecha:** 2026-04-05
**Decisión:** Eliminar esa línea inmediatamente. La línea 1057 (`os.getenv("ELEVEN_API_KEY")`) es la correcta.
**Riesgo:** Si el repositorio se hace público con esa línea, la key real quedaría expuesta. El `.gitignore` está vacío.

---

## D-008 · Corrección de bugs críticos B1, B2, B3 (aprobado por usuario)
**Fecha:** 2026-04-05
**Decisión:** Corregir los 3 bugs críticos sin cambiar comportamiento visible.
- **B1**: `normalize_marker()` → agregar `return mapping.get(n, n)` al final. Efecto: el CSV de explicaciones ya funciona.
- **B2**: Eliminar `os.getenv("sk_f8eebb...")` (línea 1056). La línea siguiente es la correcta.
- **B3**: Eliminar la segunda definición de `hemoglobina` dentro del expander de hemograma (línea ~353). Se conserva solo la del formulario principal.

---

## D-009 · Arquitectura de IA multi-proveedor desacoplada
**Fecha:** 2026-04-05
**Decisión:** Diseñar la capa de IA como un sistema de providers intercambiables.
- Interfaz base abstracta: `AIProvider` con método `interpret(context: str) -> str`.
- Implementaciones iniciales: `OpenAIProvider`, `AnthropicProvider`, `RulesOnlyProvider`.
- El proveedor activo se configura vía `.env` (`AI_PROVIDER=openai|anthropic|rules`).
- El sistema funciona sin ninguna API key (modo `rules`).
- Preparado para futura incorporación de: bases de conocimiento locales, servicios externos, RAG.
**Razón:** Evitar vendor lock-in. La prioridad es no limitar escalabilidad ni uso por pacientes reales.

---

## D-010 · ElevenLabs TTS removido de prioridad y roadmap activo
**Fecha:** 2026-04-05
**Decisión:** El código TTS existente queda aislado bajo flag `ENABLE_TTS = False` en app.py. No se desarrolla más en esta fase.
**Razón:** No es parte del MVP orientado a pacientes reales. El esfuerzo se concentra en calidad de interpretación y módulo de medicamentos.
**Revisable cuando:** Haya demanda concreta de accesibilidad por voz.

---

## D-011 · Preparación para historial por usuario y autenticación futura
**Fecha:** 2026-04-05
**Decisión:** La arquitectura debe soportar usuarios y sesiones sin rehacer todo.
- Introducir concepto de `session_id` y `user_id` desde ahora (aunque user_id sea anónimo en v0.x).
- Abstraer el storage en una capa `storage/` con implementación inicial `LocalJSONStorage`.
- La interfaz de storage permitirá reemplazar con SQLite, PostgreSQL, o cloud en v2.0.
- La UI no requiere login en v0.x; se prepara el esquema, no la pantalla.
**Razón:** Diseñar hacia atrás es costoso. El modelo de datos debe contemplar usuarios desde el inicio.

---

## D-014 · Modularización de app.py (Sprint 3-B2)
**Fecha:** 2026-04-05
**Decisión:** Extraídas 10 funciones de app.py a 3 módulos. `get_effective_range` permanece en app.py por acoplamiento directo a `st.session_state`, `fuente_rangos`, `extracted_ranges` y `csv_ranges` — extraerla requeriría pasar esas dependencias como parámetros, lo que es un refactor más amplio que escapa al alcance de este sprint.
**app.py:** 868 → 506 líneas.

---

## D-013 · Dict GENERIC eliminado de app.py (Sprint 3-B1)
**Fecha:** 2026-04-05
**Decisión:** Eliminadas ~325 líneas del dict GENERIC y su lógica de fallback en `construir_resumen_detallado`. `explicaciones.csv` cubre los 56 marcadores con 3 estados cada uno.
**Riesgo residual:** Si un marcador no está en CSV (ej: se agrega uno nuevo sin actualizar el CSV), el sistema registra warning en log y omite la explicación — comportamiento correcto y visible.

---

## D-019 · Módulo B comparte el selector de proveedor IA con Módulo A
**Fecha:** 2026-04-05
**Decisión:** El sidebar de `pages/02_medicamentos.py` tiene su propio widget de selector IA usando el mismo `key="_ai_provider_name"`. Streamlit comparte `session_state` entre páginas, por lo que el proveedor seleccionado en una página persiste en la otra.
**Razón:** Consistencia UX sin lógica centralizada extra. El selector en cada página es autónomo pero comparte estado.

---

## D-018 · nivel_riesgo como orientación al paciente, no como clasificación clínica formal
**Fecha:** 2026-04-05
**Decisión:** El campo `nivel_riesgo` (bajo/moderado/alto) en medicamentos es una señal orientativa para el paciente sobre el nivel de supervisión médica recomendada, no una clasificación farmacológica oficial.
**Criterio usado:** bajo = OTC/suplementos, moderado = mayoría de fármacos de prescripción, alto = anticoagulantes, antiepilépticos, opiáceos, hipoglucemiantes de alto riesgo, corticoides sistémicos, psicofármacos con riesgo de dependencia.
**No usar para:** triaje clínico, alertas automáticas de interacciones, ni decisiones de prescripción.

---

## D-016 · Módulo B: datos en CSV desde el inicio, no en código
**Fecha:** 2026-04-05
**Decisión:** `data/medicamentos.csv` como fuente de datos del Módulo B desde Sprint 5-A.
**Razón:** Lección aprendida del dict GENERIC en Módulo A — datos en código son difíciles de mantener. El CSV es editable sin tocar código y extensible.
**Estructura inicial:** 20 medicamentos, 6 columnas. Fácil de ampliar agregando filas.

---

## D-017 · medications.py sin dependencia de file_extractor
**Fecha:** 2026-04-05
**Decisión:** `modules/medications.py` implementa su propia normalización de texto (`_norm()`) en lugar de importar `safe_text_normalize` de `file_extractor`.
**Razón:** `file_extractor` importa `pdfplumber` a nivel de módulo. El Módulo B no necesita PDF. Importarlo crearía una dependencia innecesaria.

---

## D-015 · IA como capa opcional en UI (Sprint 4-B)
**Fecha:** 2026-04-05
**Decisión:** La interpretación IA se integra como expander colapsable en resultados. El selector de provider vive en sidebar. La lógica de reglas (`construir_resumen_detallado`) siempre corre primero e independientemente.
**Comportamiento sin API key:** `list_available_providers()` retorna solo `["rules"]` → selectbox muestra solo "Solo reglas (sin IA)" → expander IA no aparece → app funciona igual que antes.
**Comportamiento con API key:** proveedor disponible aparece en selectbox → si el usuario lo selecciona, el expander IA aparece tras los resultados con `get_provider(name).interpret(consejo)`.

---

## D-027 · Topbar unificado + sidebar eliminado (Sprint 8-FE)
**Fecha:** 2026-04-05
**Decisión:** Crear `modules/ui_components.py` con `render_topbar(active_page)` y `COLOR` dict. Ambas páginas (`app.py`, `pages/02_medicamentos.py`) llaman a `render_topbar()` justo después de `set_page_config`. Sidebar oculto via CSS + `initial_sidebar_state="collapsed"`. Layout cambiado de `"centered"` a `"wide"` con `max-width:920px` en CSS para control total del ancho. El selector de grupo y de IA se movieron del sidebar al área principal (inline).
**Paleta aplicada:** fondo `#0F172A`, card `#1E293B`, borde `#334155`, accent `#2563EB`/`#3B82F6`, texto `#F8FAFC`/`#CBD5E1`.
**Resultado:** navegación horizontal visible en ambas páginas; página activa resaltada con badge azul; sin columna izquierda.

---

## D-026 · Panel clínico de paciente: fases 0–8 (Sprint 7-FE)
**Fecha:** 2026-04-05
**Decisión:** Agregar a render_results() un panel de estado global (verde/amarillo/rojo), métricas hero, barra proporcional de colores, bloque "Lo más relevante" (top 5), contexto clínico relacionado por marcador (diccionario `_RELATED`), y microcopy no alarmista. Navegación superior con `st.page_link`.
**Regla de estado global:** 🔴 si n_fuera ≥ 2 · 🟡 si n_fuera == 1 o n_limite > 0 · 🟢 si todo normal.
**Paleta:** fondo #0B0F14 · azul #2563EB · verde #10B981 · amarillo #F59E0B · rojo #EF4444.
**Sin cambios:** lógica clínica, parsing, módulos, tests. Solo presentación.

---

## D-024 · Fuente base del Módulo B: curada_local_v1
**Fecha:** 2026-04-05
**Decisión:** La fuente base de todos los medicamentos en `data/medicamentos.csv` es `curada_local_v1`. Esto indica que el contenido fue redactado localmente en lenguaje paciente para el contexto latinoamericano, con revisión inicial por el equipo SeraphAID. No proviene de una base externa automatizada.
**Nivel de confianza inicial:** `revision_inicial` — orientativo, no validado clínicamente de forma independiente.
**Contexto:** `LAT` (Latinoamérica). Los alias y nombres reflejan el uso chileno/latinoamericano.
**Qué falta para trazabilidad completa:** URL de fuente externa por medicamento (vademécum oficial, MINSAL, FDA, EMA o equivalente). Actualmente `url_fuente` está vacío para todos los medicamentos.
**Revisable cuando:** Se incorpore un proceso de revisión farmacéutica formal o se integre un vademécum externo.

---

## D-025 · Navegación por grupo farmacológico: selectbox → ficha directa
**Fecha:** 2026-04-05
**Decisión:** Cuando el usuario filtra por grupo sin escribir una búsqueda, se muestra un `st.selectbox()` con los nombres del grupo. Al seleccionar uno, se renderiza directamente la ficha completa del medicamento (mismo componente que la búsqueda por nombre).
**Razón:** La tabla anterior (`st.dataframe`) no permitía abrir la ficha del medicamento sin escribir el nombre manualmente. El selectbox elimina esa fricción para el paciente.
**Alternativas descartadas:** Botón "Ver ficha" por fila (más complejo en Streamlit sin callbacks); tarjetas con `st.button` (requiere `session_state` por botón).

---

## D-020 · Sidebar de Módulo A: "Configuración clínica" eliminada
**Fecha:** 2026-04-05
**Decisión:** Eliminar selector de fuente de rangos y slider de margen del sidebar. `get_effective_range` usa 2 pasos automáticos: (1) rangos extraídos del laboratorio, (2) rangos internos. Margen fijo en `DEFAULT_MARGIN_PCT`.
**Razón:** La configuración clínica confundía a pacientes. El comportamiento correcto (priorizar rangos del laboratorio) debe ser automático, no manual.
**Impacto:** UI más simple. Provenance mostrado como `st.info()` cuando hay rangos del laboratorio disponibles.

---

## D-021 · Rangos del laboratorio siempre toman prioridad
**Fecha:** 2026-04-05
**Decisión:** Cuando el PDF del examen incluye rangos de referencia, estos se usan siempre en lugar de los rangos internos de SeraphAID.
**Razón:** El laboratorio específico conoce sus reactivos, equipos y población. Sus rangos son más precisos que los universales.

---

## D-022 · UI "Alterados primero" con expander para normales
**Fecha:** 2026-04-05
**Decisión:** En `render_results()`: clasificar todos los marcadores silenciosamente primero, renderizar los alterados/límite siempre visibles, poner los normales en expander colapsado.
**Razón:** Paciente debe ver inmediatamente qué está fuera de rango sin scrollear. Los normales son confirmación secundaria.

---

## D-023 · Fase F: trazabilidad en medicamentos.csv
**Fecha:** 2026-04-05
**Decisión:** Agregar columnas `fuente_base`, `url_fuente`, `fecha_revision`, `nivel_confianza`, `pais_contexto` a `data/medicamentos.csv`. Valores iniciales: `curada_local_v1`, `""`, `2026-04-05`, `revision_inicial`, `LAT`.
**Razón:** Trazabilidad de datos es requisito de calidad para información médica orientativa. Permite auditoría futura y actualización incremental.

---

## D-012 · Módulo de Exámenes debe ser producción-ready antes de agregar Módulo B
**Fecha:** 2026-04-05
**Decisión:** No comenzar Módulo B (Medicamentos) hasta que Módulo A (Exámenes) sea sólido, bien estructurado y usable por pacientes reales.
**Criterios de "listo":**
- Bugs corregidos.
- Datos completos (rangos + explicaciones para los ~50 marcadores).
- Código modularizado.
- Tests básicos pasando.
- UX revisada (resultados organizados, disclaimers claros).
- LLM opcional conectado.
