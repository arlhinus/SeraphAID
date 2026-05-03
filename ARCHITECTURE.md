# ARCHITECTURE.md — SeraphAID

---

## Stack

| Capa | Tecnología | Estado |
|---|---|---|
| UI | Streamlit | ✅ Actual |
| Lógica core | Python 3.x | ✅ Actual |
| Validación | Pydantic v2 | ✅ Actual |
| Datos tabulares | pandas + CSV | ✅ Actual |
| OCR | pdfplumber + pytesseract + Pillow | ✅ Actual |
| IA / LLM | OpenAI o Anthropic SDK | ⏳ Pendiente conexión |
| TTS | ElevenLabs via requests | ✅ Actual |
| Persistencia | Sin persistencia aún | ⏳ SQLite (futuro) |

---

## Estructura de carpetas objetivo

```
SeraphAID/
├── app.py                         ← UI Streamlit (orquestador solo)
├── modules/
│   ├── __init__.py
│   ├── exam_interpreter.py        ← classify_with_margin, show_line, construir_resumen
│   ├── file_extractor.py          ← extract_text_from_upload, parse_values_and_ranges
│   ├── range_manager.py           ← get_range, get_effective_range, ranges_from_csv
│   ├── ai_interpreter.py          ← llamada LLM con prompt (Módulo IA)
│   ├── medications.py             ← Módulo B: medicamentos (stub inicial)
│   └── tts.py                     ← (mover tts_elevenlabs.py aquí o renombrar)
├── data/
│   ├── ranges_data.py             ← UNIVERSAL_RANGES expandido (~50 marcadores)
│   ├── explicaciones.csv          ← Explicaciones expandidas (~50 marcadores x 3 estados)
│   └── markers_config.json        ← Config: aliases, unidades, notas por marcador
├── prompts/
│   └── interpret_prompt.txt       ← Prompt LLM (actual, mantener)
├── tests/
│   ├── test_exam_interpreter.py
│   ├── test_range_manager.py
│   ├── test_file_extractor.py
│   └── test_medications.py
├── .env                           ← API keys (no en git)
├── requirements.txt
├── CLAUDE.md
└── docs/                          ← Archivos de especificación .md
    ├── PROJECT_AUDIT.md
    ├── STATUS.md
    ├── NEXT_STEPS.md
    ├── DECISIONS.md
    └── ...
```

---

## Estructura de carpetas actual (post Sprint 1)

```
SeraphAID/
├── app.py                         ← UI Streamlit (orquestador)
├── ranges.py                      ← Rangos universales (expandir → data/)
├── tts_elevenlabs.py              ← TTS aislado (ENABLE_TTS=False)
├── explicaciones.csv              ← Explicaciones (expandir)
├── prompts/
│   └── interpret_prompt.txt       ← Prompt LLM
├── modules/
│   ├── __init__.py
│   └── ai/
│       ├── __init__.py
│       ├── base.py                ← AIProvider (interfaz abstracta)
│       ├── registry.py            ← get_provider() — carga por AI_PROVIDER env
│       ├── rules_provider.py      ← Siempre disponible, sin API key
│       ├── openai_provider.py     ← Requiere OPENAI_API_KEY
│       └── anthropic_provider.py  ← Requiere ANTHROPIC_API_KEY
├── storage/
│   ├── __init__.py
│   ├── base.py                    ← StorageBackend (interfaz abstracta)
│   └── local_json.py              ← Implementación local (v0.x)
├── data/                          ← (vacío por ahora, listo para rangos_data.py)
├── tests/                         ← (vacío por ahora)
├── .env                           ← API keys reales (no en git)
├── .env.example                   ← Plantilla de configuración
└── requirements.txt
```

---

## Módulos y responsabilidades

### `app.py` (después del refactor)
- Solo: layout Streamlit, formulario, sidebar, llamada a módulos.
- No debe contener lógica de negocio ni datos embebidos.

### `modules/exam_interpreter.py`
- `classify_with_margin(value, ref, margin_pct)` → estado
- `show_line(label, value, ref, margin_pct)` → render Streamlit
- `construir_resumen_detallado(detalles)` → str Markdown
- `normalize_marker(nombre_ui)` → str key (corregido)
- `buscar_explicacion(marcador, estado)` → (texto, url)

### `modules/file_extractor.py`
- `extract_text_from_upload(file)` → str
- `parse_values_and_ranges(text)` → (values_dict, ranges_dict)

### `modules/range_manager.py`
- `get_range(marker, sexo)` → Optional[Tuple[float,float]]
- `get_effective_range(marker, sexo, fuente, ...)` → Optional[Tuple]
- `ranges_from_csv(file)` → dict

### `modules/ai_interpreter.py`
- `interpret_with_llm(context_str, api_key)` → str
- Usa `prompts/interpret_prompt.txt`
- Maneja errores gracefully (retorna None si falla)

### `data/ranges_data.py`
- `UNIVERSAL_RANGES` expandido con los ~50 marcadores
- `SEX_SPECIFIC_RANGES` para los que varían por sexo/edad

---

## Flujo de datos (objetivo)

```
Upload/Form input
     ↓
file_extractor.py → texto raw, valores, rangos del examen
     ↓
PatientInput (Pydantic) — validación
     ↓
range_manager.py → rangos efectivos por marcador
     ↓
exam_interpreter.py → clasificación + explicaciones
     ↓ (opcional)
ai_interpreter.py → enriquecimiento LLM
     ↓
app.py → render Streamlit + TTS
```

---

## Estrategia de refactor (compatibilidad)

1. Cada módulo extraído se prueba independientemente.
2. `app.py` importa los módulos nuevos uno a uno.
3. Se verifica que la app corre igual antes de continuar.
4. No se cambia comportamiento externo hasta que módulo esté estable.

---

## Arquitectura de IA multi-proveedor

```
AI_PROVIDER env var
        ↓
registry.get_provider()
        ├─ "rules"      → RulesProvider      (siempre disponible)
        ├─ "openai"     → OpenAIProvider      (requiere OPENAI_API_KEY)
        ├─ "anthropic"  → AnthropicProvider   (requiere ANTHROPIC_API_KEY)
        └─ [futuro]     → LocalKBProvider     (base de conocimiento local)
                          RAGProvider          (retrieval augmented)
                          HybridProvider       (reglas + LLM)

Todos implementan: AIProvider.interpret(context) → str
Si el provider falla → fallback automático a RulesProvider
```

**Agregar un nuevo provider:** crear archivo en `modules/ai/`, implementar `AIProvider`, registrar en `_PROVIDER_MAP` en `registry.py`. Sin tocar `app.py`.

---

## Arquitectura de storage multi-usuario

```
StorageBackend (interfaz)
        ├─ LocalJSONStorage    ← v0.x actual (archivos JSON por user_id)
        ├─ SQLiteStorage       ← v1.x (SQLite local con autenticación simple)
        └─ CloudStorage        ← v2.x (PostgreSQL / Supabase con auth real)

Cada operación usa: user_id + session_id
user_id en v0.x = UUID anónimo en session_state (sin login real)
user_id en v1.x+ = UUID asociado a credenciales de usuario
```

**Agregar autenticación:** el `user_id` ya existe en la interfaz. Solo se agrega la pantalla de login y se reemplaza `LocalJSONStorage` por `SQLiteStorage`. Sin reescribir la lógica de negocio.

---

## Decisiones de diseño

- **LLM es opcional**: si no hay API key, el sistema funciona solo con reglas. Nunca crash.
- **Provider pattern para IA**: desacoplado de `app.py`. Configurable por variable de entorno.
- **Storage preparado para usuarios**: `user_id` desde el inicio, aunque sea anónimo en v0.x.
- **Streamlit multi-page**: cuando se agregue Módulo B, usar `pages/` de Streamlit.
- **TTS desactivado** (ENABLE_TTS=False) hasta que haya demanda concreta.
