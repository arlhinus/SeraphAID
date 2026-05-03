# CLAUDE.md — SeraphAID

## Proyecto
SeraphAID es un sistema integral de información al paciente que traduce información clínica compleja en explicaciones comprensibles, accionables y seguras, comenzando por interpretación de exámenes de laboratorio.

**Nunca reemplaza la atención médica profesional. Nunca emite diagnósticos.**

---

## Reglas permanentes
1. No reemplazar criterio médico profesional.
2. No emitir diagnósticos definitivos.
3. No romper funcionalidades existentes sin revisar primero.
4. Priorizar refactor progresivo sobre reescritura total.
5. Documentar decisiones importantes en DECISIONS.md.
6. Mantener compatibilidad con ejecución local en Windows.
7. Favorecer arquitectura modular y mantenible.
8. Todo output de la app debe incluir disclaimer de "no reemplaza evaluación profesional".

---

## Antes de cada sesión, leer en orden:
1. STATUS.md — estado actual del proyecto
2. NEXT_STEPS.md — tareas pendientes
3. DECISIONS.md — decisiones ya tomadas
4. PROJECT_AUDIT.md — diagnóstico técnico completo

---

## Stack actual
- Python 3.x
- Streamlit (UI)
- Pydantic (validación)
- pandas (datos CSV)
- pdfplumber + pytesseract + Pillow (OCR)
- openai (SDK instalado, no conectado aún)
- ElevenLabs TTS (vía requests, módulo separado)

---

## Estructura de archivos clave
```
app.py                     ← UI + orquestación principal (~1200 líneas, monolítico por refactorizar)
ranges.py                  ← Rangos de referencia universales (6 marcadores, expandir)
tts_elevenlabs.py          ← TTS utility
explicaciones.csv          ← Explicaciones por marcador/estado (7 marcadores, expandir)
prompts/interpret_prompt.txt ← Prompt LLM (listo, no conectado)
.env                       ← API keys (ELEVEN_API_KEY, etc.)
```

---

## Bugs conocidos (ver STATUS.md para estado)
- B1: `normalize_marker()` sin `return` — CSV nunca consultado
- B2: API key hardcodeada en línea 1056 de app.py
- B3: Campo `hemoglobina` duplicado en formulario

---

## Módulos futuros previstos
- Módulo A: Exámenes (actual, en refinamiento)
- Módulo B: Medicamentos (próximo)
- Módulo C: Indicaciones/documentos clínicos
- Módulo D: Orientación post-consulta
- Módulo E: Educación personalizada

---

## Prioridad de implementación actual
1. Corregir bugs críticos (Sprint 1)
2. Separar datos del código (Sprint 2)
3. Modularizar lógica (Sprint 3)
4. Conectar LLM (Sprint 4)
5. Módulo B: Medicamentos (Sprint 5)
