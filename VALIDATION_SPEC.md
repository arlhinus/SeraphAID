# VALIDATION_SPEC.md — SeraphAID

---

## Validaciones de entrada (Pydantic — ya implementadas)

| Campo | Regla | Mensaje de error |
|---|---|---|
| `edad` | int, 18 ≤ edad ≤ 120 | "Edad fuera de rango válido" |
| `sexo` | pattern "^(M\|F)$" o None | "Sexo debe ser M o F" |
| Marcadores | Optional[float], sin restricción adicional | — |

---

## Validaciones de consistencia (a implementar)

### Bilirrubina
- `bil_total` ≈ `bil_directa` + `bil_indirecta` (tolerancia ±10%)
- Si discrepancia > 20%: warning "Las fracciones de bilirrubina no suman el total. Revise los valores."

### Diferencial leucocitario
- neutro + linf + mono + eos + baso ≈ 100% (tolerancia ±5%)
- Si suma < 90% o > 110%: warning "La fórmula diferencial no suma ~100%. Revise los porcentajes."

### Hemoglobina vs Hematocrito
- Hb × 3 ≈ Hto (regla de los tres)
- Si discrepancia > 15%: info "Hemoglobina y hematocrito tienen discrepancia inusual."

### Gases en sangre
- Si pH < 7.35 y HCO3 < 22: consistente con acidosis metabólica
- Si pH > 7.45 y HCO3 > 26: consistente con alcalosis metabólica
- No validar automáticamente; solo informar si hay datos suficientes

---

## Manejo de datos incompletos

| Situación | Comportamiento |
|---|---|
| Marcador sin valor (None) | Mostrar "sin valor ingresado", no computar estado |
| Marcador sin rango de referencia | Mostrar "sin referencia disponible", no computar estado |
| Valor = 0.0 en campo numérico | Tratar como valor ingresado (Streamlit devuelve 0 si el usuario no toca el campo) → **decisión pendiente**: distinguir 0 ingresado de campo vacío |
| Texto del PDF vacío | Warning amigable, continuar con entrada manual |
| CSV de rangos con formato incorrecto | Warning, ignorar esa fila |

---

## Criterios para bloquear o advertir

### Bloqueo (error — detener procesamiento)
- Edad fuera de rango [18-120]
- Sexo inválido

### Advertencia (warning — continuar)
- Diferencial leucocitario no suma ~100%
- Discrepancia bilirrubina total vs fracciones
- No se pudo leer texto del PDF
- No se encontró ningún valor en el texto extraído

### Información (info — mostrar pero no alarmar)
- Marcadores sin rango de referencia (frecuente en analitos menos comunes)
- TTS sin API key configurada
- LLM sin API key configurada

---

## Validaciones de rangos

- Si `lo >= hi` en un rango: ignorar ese rango (no clasificar)
- Si `value < 0` y el marcador no puede ser negativo (ej: hemoglobina): warning
- Si `value` es extremadamente atípico (ej: glucosa=10000): no bloquear, pero considerar flag futuro

---

## Tests de validación a crear

```python
# tests/test_validation.py
test_patient_input_valid_adult()
test_patient_input_invalid_age()
test_patient_input_invalid_sex()
test_classify_normal()
test_classify_alto()
test_classify_bajo()
test_classify_limite_boundary()
test_classify_no_range()
test_ranges_from_csv_valid()
test_ranges_from_csv_invalid_format()
test_bilirubin_consistency_warning()
test_differential_sum_warning()
```
