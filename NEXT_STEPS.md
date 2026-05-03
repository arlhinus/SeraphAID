# NEXT_STEPS.md — SeraphAID
_Última actualización: 2026-04-05_

---

## Estado: Sprint 1 completado. Iniciar Sprint 2.

---

## Sprint 2 — Datos expandidos (siguiente)

**Objetivo:** Cobertura real de rangos y explicaciones para todos los ~57 analitos.

### Tareas

- [ ] **Expandir `ranges.py`** con los ~50 marcadores faltantes (o crear `data/ranges_data.py`)
  - Hepáticos: bil_total, bil_directa, bil_indirecta, fosfatasa_alc, got_ast, gpt_alt, prot_totales, albumina, ggt, globulinas, rel_albumina_glob, tp_seg, tp_pct, inr
  - Electrolitos/Renal: sodio, potasio, cloro, urea_bun, vfg_ckd_epi, fosforo, magnesio
  - Inflamación: procalcitonina, pcr, ferritina
  - Hemograma: eritrocitos, hematocrito, vcm, hcm, chcm, plaquetas, vpm, leucocitos, rdw_cv, neutro, linf, mono, eos, baso
  - Coagulación: ttpa
  - Gases: ph, pco2, po2, hco3, exceso_base, sat_o2, tco2, fio2, pres_baro, temp

- [ ] **Expandir `explicaciones.csv`** con los ~50 marcadores faltantes
  - 3 estados por marcador: alto, bajo, limite
  - Lenguaje paciente, disclaimer implícito, fuente URL

- [ ] **Migrar `GENERIC` dict** de app.py → explicaciones.csv
  - Una vez migrado, eliminar el dict del código

- [ ] **Renombrar `CLAUDE.md.txt`** → `CLAUDE.md` (o crear symlink)

- [ ] **Crear tests básicos** en `tests/`
  - `test_classification.py`: classify_with_margin, show_line
  - `test_explanations.py`: normalize_marker, buscar_explicacion
  - `test_ranges.py`: get_range, get_effective_range

---

## Sprint 3 — Modularización (después de Sprint 2)

- [ ] Extraer `modules/exam_interpreter.py`
- [ ] Extraer `modules/file_extractor.py`
- [ ] Extraer `modules/range_manager.py`
- [ ] `app.py` queda como solo UI y orquestación
- [ ] Mejorar UX: resultados alterados primero, sección "¿Qué hacer a continuación?"

---

## Sprint 4 — Conectar LLM (después de Sprint 3)

- [ ] Integrar `modules/ai/registry.get_provider()` en app.py
- [ ] Agregar selector de provider en sidebar (si hay múltiples disponibles)
- [ ] Sección de interpretación IA en resultados (opcional, colapsable)
- [ ] Integrar session_id y user_id (anónimo) con `storage/`

---

## Sprint 5 — Módulo B: Medicamentos

- [ ] Solo comenzar cuando Módulo A esté production-ready
- [ ] Crear `pages/02_medicamentos.py` (Streamlit multi-page)
- [ ] Implementar `modules/medications.py`
- [ ] UI: búsqueda por nombre + explicación estructurada
- [ ] Disclaimers farmacéuticos

---

## Pendientes menores no bloqueantes

- [ ] Agregar `anthropic` a `requirements.txt` (cuando se active ese provider)
- [ ] Considerar `bil_total` como la suma de directa + indirecta (validación de consistencia)
- [ ] Considerar alerta si diferencial leucocitario no suma ~100%
