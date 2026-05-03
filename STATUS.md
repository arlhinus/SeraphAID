# STATUS.md — SeraphAID
_Última actualización: 2026-04-05_

---

## Estado general: SPRINT 5-C COMPLETADO (Módulo B — listo para pruebas)

### Etapa 1 — Auditoría ✅
### Etapa 2 — Arquitectura y especificación ✅
### Etapa 3 — Sprint 1 (saneamiento) ✅

---

## Cambios aplicados en Sprint 1

| # | Cambio | Archivo |
|---|---|---|
| ✅ B1 | `normalize_marker()` corregida con `return` | app.py:589 |
| ✅ B2 | API key hardcodeada eliminada | app.py:1061 |
| ✅ B3 | Hemoglobina duplicada eliminada del expander | app.py:353 |
| ✅ | `ENABLE_TTS = False` — TTS aislado bajo flag | app.py:25 |
| ✅ | `import logging` movido al nivel global | app.py:5 |
| ✅ | `import logging` inline eliminado de función | app.py:~954 |
| ✅ | `.gitignore` actualizado | .gitignore |
| ✅ | `requirements.txt` limpiado (sin duplicados, agregado python-dotenv) | requirements.txt |
| ✅ | `.env.example` creado | .env.example |
| ✅ | Arquitectura multi-proveedor IA creada | modules/ai/ |
| ✅ | Capa de storage preparada para usuarios | storage/ |

---

## Bugs críticos confirmados

| # | Bug | Estado |
|---|---|---|
| B1 | `normalize_marker()` sin `return` | ✅ Corregido |
| B2 | API key hardcodeada | ✅ Corregido |
| B3 | Hemoglobina duplicada | ✅ Corregido |

---

## Sprint 3-B2 — Modularización ✅

| Módulo creado | Funciones |
|---|---|
| `modules/file_extractor.py` | `safe_text_normalize`, `extract_text_from_upload`, `parse_values_and_ranges` |
| `modules/range_manager.py` | `ranges_from_csv` |
| `modules/exam_interpreter.py` | `classify_with_margin`, `show_line`, `cargar_explicaciones_csv`, `normalize_marker`, `buscar_explicacion`, `construir_resumen_detallado` |
| `tests/test_modules.py` | 5 tests, todos pasando |

`app.py`: 868 → 506 líneas. Funciona como orquestador UI.

---

## Sprint 3-A — CSV completo ✅

| Cambio | Detalle |
|---|---|
| ✅ `explicaciones.csv` | 23 → 56 marcadores, 168 filas, 3 estados c/u |
| ✅ Inconsistencias key normalizadas | sat_o2, pres_baro, temp, neutro, linf, mono, eos, baso → claves correctas según normalize_marker() |

## Sprint 4-A — Session ID + Storage ✅

| Cambio | Detalle |
|---|---|
| ✅ `uuid` + `datetime` imports | app.py |
| ✅ `LocalJSONStorage` import | app.py |
| ✅ `session_id` anónimo en `st.session_state` | app.py:35 |
| ✅ `_storage = LocalJSONStorage()` instanciado | app.py:37 |
| ✅ `_storage.save_session()` tras `render_results()` | app.py:501 |
| ✅ `DEFAULT_MARGIN_PCT` duplicado eliminado | app.py (importado de exam_interpreter) |

Sesión guardada en `.seraphaid_data/anonymous/{session_id}.json` con: timestamp, edad, sexo, data completa.

---

## Deuda técnica pendiente

- `openai`/LLM no conectado en app.py
- `CLAUDE.md.txt` → renombrar a `CLAUDE.md`

## Sprint 4-B — AI provider opcional en UI ✅

| Cambio | Detalle |
|---|---|
| ✅ Import `get_provider`, `list_available_providers` | app.py |
| ✅ Selector de proveedor en sidebar | app.py (~119) — usa `key="_ai_provider_name"` en session_state |
| ✅ Sección IA colapsable en resultados | app.py — solo aparece si proveedor ≠ "rules" |
| ✅ Fallback silencioso a reglas | sin API key → selector muestra "Solo reglas", expander no aparece |

## Sprint 5-A — Módulo B: Medicamentos base ✅

| Archivo | Detalle |
|---|---|
| ✅ `data/medicamentos.csv` | 20 medicamentos comunes. Columnas: nombre, nombre_generico, grupo, para_que_sirve, precauciones, efectos_frecuentes |
| ✅ `modules/medications.py` | `cargar_medicamentos()`, `buscar_medicamento()`, `DISCLAIMER`. Sin dependencia de pdfplumber. |
| ✅ `pages/02_medicamentos.py` | Búsqueda libre, ficha por medicamento, disclaimer prominente |

Módulo A intacto. Tests pasando (5/5).

## Sprint 5-B — Módulo B expandido ✅

| Cambio | Detalle |
|---|---|
| ✅ `data/medicamentos.csv` | 20 → 78 medicamentos. Nuevas columnas: `cuando_consultar`, `nivel_riesgo` (bajo/moderado/alto) |
| ✅ `modules/medications.py` | `filtrar_por_grupo()`, `construir_contexto_med()`, nuevas columnas en schema |
| ✅ `pages/02_medicamentos.py` | Badge de riesgo (🟢🟠🔴), sección "¿Cuándo consultar?", filtro por grupo en sidebar, tabla de grupo sin query |
| ✅ Placeholder IA | Listo en comentario (mismo patrón Módulo A, Sprint 5-C lo activa) |

Distribución de riesgo: 14 bajo / 49 moderado / 15 alto. Tests 5/5 pasando.

## Sprint 5-C — Módulo B: AI provider conectado ✅

| Cambio | Detalle |
|---|---|
| ✅ `pages/02_medicamentos.py` | Import `get_provider`/`list_available_providers`, selector IA en sidebar, expander IA activado |
| ✅ Patrón idéntico al Módulo A | Mismo key `_ai_provider_name`, mismo try/except, mismo caption disclaimer |
| ✅ Contexto IA | `construir_contexto_med(row)` → 7 campos estructurados → `provider.interpret()` |

Sin API key: selector muestra "Solo datos locales", expander IA no aparece. Tests 5/5 pasando.

## Sprint 6 — Hardening clínico + UX ✅

### Fase A — Correcciones clínicas del parser ✅
| Corrección | Detalle |
|---|---|
| ✅ HDL anti-ratio | `_is_ratio_line()` + `_CHECK_RATIO_CONTEXT` — evita capturar "Índice Col/HDL" como valor HDL |
| ✅ Urea/BUN alias específicos | Aliases `nitrogeno ureico`, `bun` — elimina riesgo de confusión con "uremia" (mmol/L) |
| ✅ bil_total agregado | Ausente en versión anterior — aliases: bilirrubina total, bt |
| ✅ Matching línea-a-línea | `parse_values_and_ranges` ahora itera por línea para contexto preciso |
| ✅ Regex de rango corregido | `.*?` en lugar de `[^0-9\n]{0,80}` — soporta valor antes del rango en la misma línea |

### Fase B — Sidebar simplificado ✅
| Cambio | Detalle |
|---|---|
| ✅ Eliminar "Configuración clínica" | Sin selector de fuente de rangos ni slider de margen en sidebar |
| ✅ `get_effective_range` simplificado | 2 pasos: rangos extraídos del lab → rangos internos |
| ✅ Provenance info | `st.info()` muestra cuántos parámetros usan rangos del laboratorio |

### Fase C — Diseño clínico oscuro ✅
| Cambio | Detalle |
|---|---|
| ✅ CSS dark theme | Fondo `#0d1117`, sidebar `#161b22`, botones `#1f6feb` |
| ✅ "Alterados primero" | Clasificación silenciosa → alterados visibles, normales en expander |
| ✅ Métricas resumen | `st.metric()` para "Fuera de rango", "En límite", "Normales" |

### Fase E — Nuevos marcadores ✅
| Marcador | Alias | Rango |
|---|---|---|
| `tsh` | tirotropina ultrasensible, tsh ultrasensible | (0.4, 4.0) mIU/L |
| `t4_libre` | tiroxina libre, t4 libre, t4l, ft4 | (0.8, 1.8) ng/dL |
| `t3_libre` | triyodotironina libre, t3 libre, ft3 | (2.3, 4.2) pg/mL |
| `vhs` | velocidad de sedimentacion globular, esr | M:(0–15) F:(0–20) mm/h |
| `acido_urico` | acido urico, uric acid | M:(3.4–7.0) F:(2.4–6.0) mg/dL |
| `vitamina_d` | 25-hidroxi vitamina d, vitamina d | (30–100) ng/mL |
| `vitamina_b12` | vitamina b12, cobalamina | (200–900) pg/mL |

`app.py`: formulario expandido con sección "Tiroides y vitaminas (opcionales)".
`modules/exam_interpreter.py`: mappings nuevos en `normalize_marker()`.
`explicaciones.csv`: 168 → 189 filas (6 marcadores × 3 estados).

### Fase F — Trazabilidad medicamentos ✅
| Cambio | Detalle |
|---|---|
| ✅ `data/medicamentos.csv` | +5 columnas: `fuente_base`, `url_fuente`, `fecha_revision`, `nivel_confianza`, `pais_contexto` |
| ✅ `modules/medications.py` | `_EMPTY_COLS` actualizado con nuevas columnas |

### Fase G — Tests clínicos ✅
| Test | Detalle |
|---|---|
| ✅ `test_hdl_not_confused_with_ratio` | HDL captura 52.0, no 3.4 desde línea de índice |
| ✅ `test_urea_bun_alias_not_bare_urea` | urea_bun via "nitrogeno ureico", no confunde con uremia |
| ✅ `test_bil_total_parsed` | bil_total parseado correctamente |
| ✅ `test_new_markers_ranges` | TSH, VHS, ácido úrico, vitamina D, B12 con rangos correctos |
| ✅ `test_normalize_marker_new` | Labels UI → claves CSV para todos los nuevos marcadores |
| ✅ `test_altered_first_ordering` | classify_with_margin separa alterados/normales correctamente |

**Tests: 11/11 pasando.**

## Próximo sprint recomendado: Sprint 7 — Pruebas con pacientes reales + ajuste UX
