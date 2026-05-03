# PROJECT_AUDIT.md — SeraphAID
_Generado: 2026-04-05_

---

## 1. Mapa del proyecto (archivos reales)

```
SeraphAID/
├── app.py                  ← Aplicación principal (Streamlit) — ~1195 líneas
├── ranges.py               ← Rangos universales de referencia (6 marcadores + Hb)
├── tts_elevenlabs.py       ← Utilitario TTS via ElevenLabs API
├── explicaciones.csv       ← Explicaciones por marcador/estado (7 marcadores)
├── prompts/
│   └── interpret_prompt.txt ← Prompt para LLM (¡NO conectado a la UI!)
├── requirements.txt        ← Dependencias (con duplicado de pandas)
├── .env                    ← Variables de entorno (ELEVEN_API_KEY, etc.)
├── CLAUDE.md.txt           ← Instrucciones de Claude (extensión incorrecta, debe ser CLAUDE.md)
├── .gitignore              ← Vacío (1 línea vacía)
└── .vscode/settings.json   ← Solo CodeGPT config
```

---

## 2. Módulos detectados (dentro de app.py)

| Módulo lógico | Ubicación | Estado |
|---|---|---|
| Config de página | líneas 17-27 | ✅ funcional |
| Modelo Pydantic `PatientInput` | líneas 31-98 | ✅ funcional (50+ campos) |
| Sidebar configuración clínica | líneas 100-129 | ✅ funcional |
| Carga de examen PDF/imagen | líneas 131-166 | ✅ funcional |
| Parser de valores y rangos desde texto | líneas 168-274 | ✅ funcional (regex, ~50 marcadores) |
| Formulario manual | líneas 290-388 | ✅ funcional pero monolítico |
| Cargador CSV rangos | líneas 391-425 | ✅ funcional |
| Selección de rango efectivo | líneas 428-446 | ✅ funcional |
| Clasificación con margen | líneas 449-469 | ✅ funcional |
| Render de línea individual | líneas 472-483 | ✅ funcional |
| Cargador CSV explicaciones | líneas 486-499 | ✅ funcional |
| `normalize_marker()` | líneas 501-588 | ⚠️ **BUG: sin `return`** |
| `buscar_explicacion()` | líneas 589-601 | ⚠️ depende del bug anterior |
| `GENERIC` dict (explicaciones fallback) | líneas 603-927 | ✅ datos ok, pero embebidos en app.py |
| `construir_resumen_detallado()` | líneas 928-963 | ✅ funcional |
| `render_results()` | líneas 967-1029 | ✅ funcional pero masivo |
| TTS (ElevenLabs) | líneas 1053-1117 | ✅ funcional |
| Persistencia de sesión | líneas 1182-1195 | ✅ funcional |
| **OpenAI / LLM** | — | ❌ **NO conectado** (prompt existe, import en requirements, pero sin llamada) |

---

## 3. Flujo actual de la aplicación

```
Usuario abre app
       ↓
[Opcional] Sube PDF/imagen → extract_text_from_upload() → parse_values_and_ranges()
       ↓                         (pdfplumber / pytesseract)       (regex)
Precarga de campos desde texto extraído
       ↓
Formulario manual (edad, sexo, ~50 analitos agrupados en expanders)
       ↓
"Interpretar" (submit)
       ↓
PatientInput (Pydantic) — validación básica
       ↓
render_results():
  Para cada analito:
    → get_effective_range(marcador, sexo)    ← ranges.py + custom/CSV/examen
    → classify_with_margin(valor, rango, %)
    → show_line() → colores 🔴🟠🟢
       ↓
construir_resumen_detallado()
  → buscar_explicacion() → explicaciones.csv
  → fallback → GENERIC dict
       ↓
Mostrar texto explicativo en Markdown
       ↓
[Opcional] TTS → ElevenLabs → st.audio()
```

---

## 4. Fortalezas

- **Base funcional real**: la app corre y produce resultados coherentes.
- **Cobertura amplia de analitos**: ~50 marcadores con aliases para parsing.
- **Arquitectura segura por diseño**: disclaimers y lenguaje no diagnóstico.
- **Flexibilidad de rangos**: 4 fuentes (universal, manual, CSV, examen).
- **TTS integrado**: valor diferencial para accesibilidad.
- **Pydantic validation**: previene entradas malformadas.
- **Prompt LLM bien escrito**: base sólida para conectar AI real.
- **`@st.cache_data`** en carga de CSV: optimización correcta.

---

## 5. Debilidades y deuda técnica

### Críticos
1. **`normalize_marker()` sin `return`** (línea ~588): la función construye el mapping dict pero nunca retorna. `buscar_explicacion()` siempre falla silenciosamente → el CSV de explicaciones nunca se usa.
2. **API key hardcodeada** (línea 1056): `os.getenv("sk_f8eebb37b4750def8fd2428addb2341054aa6ea7e124228c")` — la key real está usada como nombre de variable de entorno. Bug de seguridad (aunque la línea 1057 la sobreescribe correctamente).
3. **OpenAI no conectado**: `openai` en requirements, prompt en prompts/, pero sin implementación. El usuario puede creer que hay IA cuando no la hay.

### Importantes
4. **`app.py` monolítico**: ~1200 líneas con UI, lógica, datos y presentación mezclados.
5. **`GENERIC` embebido en app.py**: ~300 líneas de datos de explicaciones en código, difícil de mantener.
6. **`ranges.py` subpoblado**: solo 6 marcadores; ~44 marcadores no tienen rango programático (se interpretan como "sin referencia").
7. **`explicaciones.csv` subpoblado**: solo 7 marcadores de los ~50 disponibles.
8. **`.gitignore` vacío**: `.venv`, `.env` y `__pycache__` no están ignorados.
9. **`CLAUDE.md.txt`**: extensión incorrecta, no es leído por Claude Code.
10. **`requirements.txt`**: `pandas` duplicado.
11. **Hemoglobina duplicada**: definida dos veces en el formulario (líneas 297 y 353) con diferente clave `key`. En Streamlit esto no falla pero el valor que llega puede ser ambiguo.

### Menores
12. Comentario `# ...existing code...` en líneas 30, 291: artefactos de edición.
13. `import logging` dentro de función (línea 949): debe ser import global.
14. Sin manejo de historial ni persistencia entre sesiones.
15. Sin tests automáticos.
16. `.gitinore` (typo en filename) y `.gitignore` coexisten.

---

## 6. Riesgos

| Riesgo | Impacto | Probabilidad |
|---|---|---|
| Bug `normalize_marker` pasa desapercibido | Alto (CSV nunca usado) | Confirmado |
| API key en código fuente llega a repositorio | Alto (seguridad) | Medio |
| OpenAI no conectado confunde expectativas | Medio | Alto |
| Hemoglobina duplicada produce valor incorrecto | Medio | Medio |
| `ranges.py` incompleto → muchos analitos sin clasificar | Alto (UX) | Confirmado |

---

## 7. Propuesta de refactor (sin reescritura total)

### Paso 1 — Correcciones críticas (1-2h)
- Corregir `normalize_marker()` (agregar `return mapping.get(n, n)`).
- Remover línea 1056 con API key hardcodeada.
- Corregir hemoglobina duplicada.
- Renombrar `CLAUDE.md.txt` → `CLAUDE.md`.
- Limpiar `requirements.txt`.
- Actualizar `.gitignore`.

### Paso 2 — Separación de datos (2-4h)
- Mover `GENERIC` dict → `data/explicaciones_genericas.py` o extender `explicaciones.csv`.
- Expandir `ranges.py` → `data/ranges_data.py` con los ~50 marcadores.

### Paso 3 — Modularización de lógica (4-8h)
- Extraer `modules/exam_interpreter.py`: classify, show_line, construir_resumen.
- Extraer `modules/file_extractor.py`: extract_text, parse_values_and_ranges.
- Extraer `modules/range_manager.py`: get_range, get_effective_range.
- Mantener `app.py` como solo UI/orquestación.

### Paso 4 — Conectar LLM (2-4h)
- Implementar llamada a OpenAI/Claude usando `prompts/interpret_prompt.txt`.
- Hacer la generación IA opcional (fallback a reglas si sin API key).

### Paso 5 — Preparar extensión (4-8h)
- Añadir stub `modules/medications.py`.
- Añadir página/tab "Medicamentos" deshabilitada pero visible.

---

## 8. Componentes que CONSERVAR como base

| Componente | Razón |
|---|---|
| `PatientInput` Pydantic model | Bien estructurado, validación robusta |
| `classify_with_margin()` | Lógica correcta y configurable |
| `extract_text_from_upload()` | Funciona para PDF e imagen |
| `parse_values_and_ranges()` | Aliases exhaustivos, regex funcional |
| `prompts/interpret_prompt.txt` | Bien escrito, listo para LLM |
| `tts_elevenlabs.py` | Limpio, separado, funcional |
| Sidebar de configuración clínica | UX razonable |
| `get_effective_range()` con 4 fuentes | Arquitectura flexible |
