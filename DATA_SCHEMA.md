# DATA_SCHEMA.md — SeraphAID

---

## Estructuras de datos internas

### ExamResult (por marcador)
```python
{
    "marker_key": str,           # ej: "glucosa"
    "label_ui": str,             # ej: "Glucosa en ayunas"
    "value": float | None,
    "unit": str,                 # ej: "mg/dL"
    "ref_lo": float | None,
    "ref_hi": float | None,
    "ref_source": str,           # "universal" | "manual" | "csv" | "exam"
    "status": str | None,        # "alto" | "bajo" | "limite" | "normal" | None
    "explanation": str | None,
    "source_url": str | None,
}
```

### PatientInput (Pydantic actual — mantener)
```python
PatientInput:
    edad: int (18–120)
    sexo: Optional["M" | "F"]
    # ~50 marcadores como Optional[float]
```

### RangeEntry (en ranges_data.py)
```python
{
    "marker": str,
    "lo": float,
    "hi": float,
    "sexo": "M" | "F" | None,       # None = aplica a todos
    "age_min": int | None,
    "age_max": int | None,
    "unit": str,
    "notes": str | None,
}
```

### ExplanationEntry (en explicaciones.csv)
```
marcador,estado,explicacion,fuente_url
glucosa,alto,"...",https://...
```
Columnas:
- `marcador`: key normalizada (minúsculas, sin tildes)
- `estado`: "alto" | "bajo" | "limite"
- `explicacion`: texto en español, lenguaje paciente, max ~200 chars
- `fuente_url`: URL de referencia (MedlinePlus, etc.)

### SessionResult (para persistencia futura)
```python
{
    "session_id": str,       # uuid
    "timestamp": str,        # ISO datetime
    "patient_age": int,
    "patient_sex": str | None,
    "results": list[ExamResult],
    "summary": str,
    "ai_interpretation": str | None,
}
```

### MedicationQuery (Módulo B — futuro)
```python
{
    "drug_name": str,
    "query_type": "info" | "interactions" | "side_effects",
    "response": str,
    "disclaimer": str,
    "timestamp": str,
}
```

### ClinicalDocument (Módulo C — futuro)
```python
{
    "original_text": str,
    "doc_type": "indicaciones" | "epicrisis" | "receta" | "otro",
    "translated_sections": {
        "que_significa": str,
        "que_debo_hacer": str,
        "cuando_consultar": str,
    },
    "disclaimer": str,
}
```

---

## Marcadores soportados actualmente (PatientInput)

### Básicos (siempre visibles)
hemoglobina, glucosa, col_total, hdl, ldl, trigliceridos, creatinina

### Perfil hepático
bil_total, bil_directa, bil_indirecta, fosfatasa_alc, got_ast, gpt_alt, prot_totales, albumina, ggt, globulinas, rel_albumina_glob, tp_seg, tp_pct, inr

### Electrolitos / Renal
sodio, potasio, cloro, urea_bun, vfg_ckd_epi, fosforo, magnesio

### Inflamación
procalcitonina, pcr, ferritina

### Hemograma
eritrocitos, hematocrito, vcm, hcm, chcm, plaquetas, vpm, leucocitos, rdw_cv, neutro, linf, mono, eos, baso

### Coagulación
ttpa

### Gases en sangre
ph, pco2, po2, hco3, exceso_base, sat_o2, tco2, fio2, pres_baro, temp

---

## Cobertura actual de datos

| Grupo | Marcadores | Rango en ranges.py | Expl. en CSV |
|---|---|---|---|
| Básicos | 7 | 6/7 | 7/7 |
| Hepático | 14 | 0/14 | 0/14 |
| Electrolitos | 7 | 0/7 | 0/7 |
| Inflamación | 3 | 0/3 | 0/3 |
| Hemograma | 15 | 0/15 | 0/15 |
| Coagulación | 1 | 0/1 | 0/1 |
| Gases | 10 | 0/10 | 0/10 |
| **Total** | **57** | **6/57** | **7/57** |

**Nota:** Los marcadores sin rango en ranges.py se muestran como "sin referencia". Los sin CSV usan el dict GENERIC embebido en app.py.
