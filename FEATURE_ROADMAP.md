# FEATURE_ROADMAP.md — SeraphAID

---

## Versión actual: v0.5 (MVP funcional con deuda técnica)

**Estado:** Funcional. Corre localmente. Cubre interpretación de exámenes con ~50 analitos.
**Pendiente:** 3 bugs críticos, monolítico, LLM no conectado.

---

## v0.6 — Saneamiento (Sprint 1) ✅ COMPLETADO

**Objetivo:** App estable, limpia, sin bugs críticos.

- [x] Corregir bug `normalize_marker()` (sin `return`)
- [x] Eliminar API key hardcodeada
- [x] Resolver hemoglobina duplicada en formulario
- [x] Limpiar `requirements.txt` (duplicados, agregar python-dotenv)
- [x] Actualizar `.gitignore`
- [x] Mover `import logging` a nivel global
- [x] TTS aislado bajo `ENABLE_TTS = False`
- [x] Arquitectura multi-proveedor IA (`modules/ai/`)
- [x] Capa de storage preparada para usuarios (`storage/`)
- [x] `.env.example` creado

**Resultado:** App funciona correctamente. CSV de explicaciones ya funciona. Arquitectura preparada para LLM y usuarios.

---

## v0.7 — Datos expandidos (Sprint 2)

**Objetivo:** Cobertura completa de rangos y explicaciones.

- [ ] Expandir `ranges.py` con los ~50 marcadores restantes
- [ ] Expandir `explicaciones.csv` con los ~43 marcadores faltantes
- [ ] Migrar `GENERIC` dict de app.py → CSV (o archivo de datos separado)
- [ ] Escribir tests para clasificación y explicaciones

**Resultado esperado:** Todo analito soportado tiene rango y explicación. Sin datos hardcodeados en app.py.

---

## v0.8 — Modularización (Sprint 3)

**Objetivo:** `app.py` como orquestador limpio.

- [ ] Crear `modules/` con submódulos
- [ ] Extraer `exam_interpreter.py`, `file_extractor.py`, `range_manager.py`
- [ ] Mover `tts_elevenlabs.py` → `modules/tts.py`
- [ ] Crear `tests/` con suite básica
- [ ] UI: reorganizar resultados (alterados primero, normales después)
- [ ] UI: agregar sección "¿Qué hacer a continuación?"

**Resultado esperado:** Código mantenible, testeable, extensible.

---

## v1.0 — LLM conectado + UI mejorada (Sprint 4)

**Objetivo:** Primera versión presentable.

- [ ] Implementar `modules/ai_interpreter.py`
- [ ] Conectar `prompts/interpret_prompt.txt` con OpenAI o Claude
- [ ] LLM como capa adicional opcional (requiere API key)
- [ ] UI con tabs: Exámenes / Medicamentos (stub) / Acerca de
- [ ] Mejoras visuales (colores, layout de resultados)
- [ ] Disclaimer más prominente

**Resultado esperado:** App con IA real, profesionalmente presentable.

---

## v1.1 — Módulo B: Medicamentos (Sprint 5)

**Objetivo:** Segunda funcionalidad principal.

- [ ] Crear `modules/medications.py`
- [ ] UI: tab "Medicamentos" funcional
- [ ] Búsqueda por nombre de medicamento
- [ ] Explicación: para qué sirve, cómo tomar, efectos adversos esperables, señales de alarma
- [ ] Basado en LLM + datos estructurados básicos
- [ ] Disclaimer farmacéutico

**Resultado esperado:** Módulo B funcional para medicamentos comunes.

---

## v1.2 — Módulo C: Indicaciones médicas (Sprint 6)

- [ ] Entrada de texto libre (pegar indicaciones/receta)
- [ ] Traducción a lenguaje simple: qué significa / qué hacer / cuándo consultar
- [ ] Resumen de prioridades

---

## v2.0 — Historial y educación (futuro)

- [ ] Persistencia local (SQLite)
- [ ] Historial de exámenes comparativo
- [ ] Módulo D: Orientación post-consulta (checklist, alarmas, seguimiento)
- [ ] Módulo E: Educación personalizada por condición
- [ ] Exportar PDF del resumen

---

## Features descartadas (por ahora)

- **Multi-usuario / login**: no necesario para uso personal local.
- **Deploy cloud**: fuera de alcance hasta que haya revisión de seguridad y privacidad.
- **Integración con laboratorio**: requeriría acuerdos y estándares (HL7/FHIR).
