# GENERATION_ORCHESTRATION.md — SeraphAID

---

## Flujo de procesamiento completo

### Fase 1: Input del usuario

```
A) Upload de archivo
   └─ extract_text_from_upload(file)
       ├─ PDF: pdfplumber → texto plano
       └─ Imagen: pytesseract (lang=spa) → texto plano
       → safe_text_normalize(text)  [quita acentos compuestos]

B) Parsing del texto extraído
   └─ parse_values_and_ranges(text)
       ├─ Busca ~50 marcadores via aliases + regex
       ├─ Extrae valores numéricos
       └─ Extrae rangos de referencia impresos (si existen)
       → (values_dict, ranges_dict)

C) Precarga del formulario
   └─ session_state.setdefault(f"val_{key}", value)
       → Campos precargados en UI
```

### Fase 2: Validación de entrada

```
Submit del formulario
└─ PatientInput(**form_values)
    ├─ edad: int [18-120]
    ├─ sexo: Optional["M"|"F"]
    └─ ~50 campos Optional[float]

    Si ValidationError → st.error() con mensaje amigable
    Si OK → continuar
```

### Fase 3: Resolución de rangos

```
Para cada marcador:
└─ get_effective_range(marker, sexo)
    ├─ Fuente "examen" → extracted_ranges.get(marker)
    ├─ Fuente "manual" → session_state.custom_ranges.get(marker)
    ├─ Fuente "csv"    → csv_ranges.get(marker) [con lógica sexo]
    └─ Fuente "universal" → ranges.get_range(marker, sexo)
    → Optional[Tuple[float, float]]
```

### Fase 4: Clasificación

```
Para cada marcador con valor y rango:
└─ classify_with_margin(value, ref, margin_pct)
    ├─ value < lo - margin → "bajo"
    ├─ value < lo         → "limite"
    ├─ value > hi + margin → "alto"
    ├─ value > hi         → "limite"
    ├─ cerca del borde     → "limite"
    └─ interior           → "normal"
    → estado: str | None
```

### Fase 5: Generación de explicaciones

```
Para cada marcador con estado != "normal":
└─ buscar_explicacion(marcador_ui, estado)
    ├─ normalize_marker(marcador_ui) → key
    └─ EXPL[(EXPL.marcador == key) & (EXPL.estado == estado)]
       ├─ Hit → (texto_csv, url)
       └─ Miss → GENERIC.get(key, {}).get(estado)
              └─ Miss → warning en log, None

└─ construir_resumen_detallado(detalles)
    ├─ Para cada (marcador, estado) alterado:
    │   → bullet: "- **Marcador (alto)**: explicación [Fuente]"
    ├─ Footer: disclaimer
    └─ Si nada alterado → mensaje "valores en rango"
```

### Fase 6: Generación LLM (opcional — pendiente implementación)

```
Si api_key disponible y usuario lo solicita:
└─ ai_interpreter.interpret_with_llm(context_str)
    ├─ Construir context_str: valores + estados + refs
    ├─ Cargar prompts/interpret_prompt.txt
    ├─ Llamar OpenAI/Claude API
    └─ Parsear y limpiar respuesta
    → texto_ia: str

Mostrar como sección adicional, no reemplazo
```

### Fase 7: Output

```
render_results(data, margin_pct):
├─ Lista de líneas: show_line() por marcador
├─ Sección "Explicación breve": construir_resumen_detallado()
├─ [Opcional] Sección IA: texto_ia
└─ [Opcional] TTS: tts_to_file(texto) → st.audio()
```

---

## Decisiones de orquestación

- **LLM es aditivo**: las reglas siempre corren primero. El LLM enriquece, no reemplaza.
- **Fallback en cascada**: CSV → GENERIC → "sin explicación disponible". Nunca crash silencioso.
- **Sin estado entre sesiones** (hasta v2): cada carga es independiente.
- **Persistencia intra-sesión**: `session_state["last_data"]` permite re-render sin re-submit al interactuar con checkboxes.

---

## Context string para LLM (formato)

```
Marcador: Glucosa | Valor: 125 mg/dL | Referencia: 70–99 | Estado: ALTO
Marcador: LDL | Valor: 145 mg/dL | Referencia: 0–129 | Estado: ALTO
Marcador: HDL | Valor: 52 mg/dL | Referencia: 40–60 | Estado: NORMAL
...
Paciente: Mujer, 45 años
```

El prompt en `interpret_prompt.txt` ya está correctamente formulado para recibir este contexto vía `{context}`.
