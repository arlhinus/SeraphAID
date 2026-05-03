# SAFETY_GUARDRAILS.md — SeraphAID

---

## Principio fundamental

**SeraphAID es una herramienta de información y educación al paciente. No es un sistema diagnóstico, no reemplaza la atención médica profesional, y no debe ser usado para tomar decisiones clínicas sin supervisión médica.**

---

## Límites del sistema

### Lo que SeraphAID HACE
- Explica qué significa un valor de laboratorio en lenguaje simple.
- Informa si un valor está fuera del rango de referencia estándar.
- Sugiere acciones de seguimiento genéricas ("consulte a su médico", "repita el examen").
- Explica para qué sirve un medicamento (información general).
- Traduce indicaciones médicas a lenguaje comprensible.

### Lo que SeraphAID NO HACE
- Diagnostica enfermedades.
- Prescribe medicamentos o dosis.
- Recomienda suspender o modificar tratamientos.
- Interpreta resultados en contexto clínico individual.
- Reemplaza la consulta médica.
- Garantiza la exactitud de los rangos de referencia para un laboratorio específico.

---

## Disclaimers requeridos

### Disclaimer principal (siempre visible en la app)
```
Este resultado es orientativo y no reemplaza la evaluación médica profesional.
Consulte siempre a su médico o profesional de salud ante dudas o síntomas.
```

### Disclaimer en resultados con valores alterados
```
Los valores fuera de rango no implican necesariamente enfermedad.
La interpretación correcta requiere contexto clínico individual.
```

### Disclaimer en módulo de medicamentos (futuro)
```
Esta información es general y no constituye asesoría farmacéutica.
Las dosis y contraindicaciones deben ser determinadas por su médico o farmacéutico.
```

---

## Lenguaje prohibido

| ❌ NO usar | ✅ Usar en cambio |
|---|---|
| "Tienes diabetes" | "Este valor puede sugerir alteraciones del metabolismo de la glucosa" |
| "Es cáncer" | "Requiere evaluación médica" |
| "Debes tomar X medicamento" | "Su médico podría considerar opciones de tratamiento" |
| "Suspende tu medicación" | "Consulte con su médico antes de modificar su tratamiento" |
| "Esto es grave" | "Este resultado merece consulta médica pronto" |
| "No es nada" | "El valor está dentro del rango de referencia" |
| "Estás bien" | "Los valores ingresados están dentro de los rangos de referencia" |

---

## Lenguaje seguro para estados

| Estado | Formulación segura |
|---|---|
| alto | "puede sugerir", "se asocia a", "merece evaluación" |
| bajo | "puede indicar", "se observa en", "requiere correlación" |
| límite | "cercano al límite", "considere repetir", "evalúe factores de riesgo" |
| normal | "dentro del rango de referencia", "dentro de valores habituales" |

---

## Validación del prompt LLM

El prompt en `prompts/interpret_prompt.txt` ya incluye las instrucciones correctas:
- "No emitas diagnósticos definitivos"
- "No provoques alarma"
- "Usa lenguaje orientativo"

**Toda modificación del prompt debe mantener estas restricciones.**

---

## Contenido permitido y no permitido para módulo de medicamentos (futuro)

### Permitido
- Mecanismo de acción en lenguaje simple.
- Indicaciones aprobadas (información pública).
- Efectos adversos frecuentes y esperables.
- Señales de alarma que requieren consulta urgente.
- Interacciones importantes de conocimiento público.

### NO permitido
- Recomendación de dosis específicas.
- Indicación de "tomar este medicamento para X".
- Afirmar que un medicamento es seguro sin matices.
- Comparar medicamentos para recomendar uno.

---

## Revisión periódica

Los disclaimers, el lenguaje de las explicaciones y los límites del sistema deben revisarse:
- Antes de cada nueva funcionalidad.
- Antes de cualquier despliegue público (actualmente: solo local).
- Si se detecta que el sistema está siendo usado para tomar decisiones clínicas sin supervisión.
