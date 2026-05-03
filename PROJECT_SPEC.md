# PROJECT_SPEC.md — SeraphAID

---

## Propósito del producto
SeraphAID es un sistema de información al paciente que traduce información clínica compleja —exámenes de laboratorio, medicamentos, indicaciones médicas— en lenguaje comprensible, accionable y seguro.

**No es:** un sistema diagnóstico, un reemplazo de atención médica, ni una herramienta clínica para profesionales.

---

## Usuario objetivo
- **Principal:** Paciente adulto (18+) con educación básica/media que recibe resultados de laboratorio o indicaciones médicas y quiere entenderlas.
- **Secundario:** Cuidador de paciente (familiar, enfermero/a domiciliaria).
- **Contexto de uso:** Local en Windows; sesión individual; sin necesidad de cuenta ni login.

---

## Casos de uso prioritarios (MVP)

### CU-01: Interpretar examen de laboratorio
El usuario sube un PDF/imagen de su examen O ingresa los valores manualmente. El sistema muestra qué valores están fuera de rango, qué significa cada alteración en lenguaje simple, y sugiere acciones de seguimiento seguras.

### CU-02: Escuchar el resumen del examen (accesibilidad)
El sistema genera audio con el resumen de resultados alterados, útil para personas con dificultad de lectura.

### CU-03: Consultar información de un medicamento [futuro]
El usuario ingresa el nombre de un medicamento. El sistema explica para qué sirve, cómo tomarlo, qué efectos adversos esperar, y cuándo consultar al médico.

### CU-04: Traducir indicaciones médicas [futuro]
El usuario pega o sube un texto de indicaciones médicas. El sistema lo traduce a lenguaje simple con "qué significa / qué debo hacer / cuándo consultar".

---

## Alcance actual (v0.x — MVP funcional)
- Módulo A: Interpretación de exámenes (funcional, en refinamiento)
- ~50 analitos con clasificación por rangos
- Soporte PDF, imagen (OCR), entrada manual
- Opciones de rango: universal, manual, CSV, desde examen
- Texto explicativo con disclaimer
- TTS (ElevenLabs, opcional)

## Alcance siguiente (v1.0 — MVP mejorado)
- Bugs corregidos
- Módulo A modularizado y limpio
- LLM conectado como interpretación enriquecida (opcional)
- Módulo B: Medicamentos (básico)
- UI reorganizada con tabs

## Alcance futuro (v2.0+)
- Módulo C: Indicaciones/documentos clínicos
- Módulo D: Orientación post-consulta
- Historial de sesiones (SQLite local)
- Módulo E: Educación personalizada

---

## Restricciones de seguridad
1. Nunca usar lenguaje diagnóstico definitivo ("tienes diabetes", "es cáncer").
2. Siempre incluir disclaimer visible.
3. Recomendar siempre consultar profesional de salud.
4. No almacenar datos sensibles sin consentimiento explícito.
5. No compartir datos con terceros salvo las APIs estrictamente necesarias (OpenAI/Claude para interpretación, ElevenLabs para TTS).

---

## Criterios de éxito del MVP
- La app corre sin errores en Windows local.
- Los bugs críticos están corregidos.
- Un usuario sin conocimientos médicos puede interpretar su examen en < 3 minutos.
- El resultado incluye siempre disclaimer claro.
- Al menos los 20 analitos más comunes tienen rango y explicación cubiertos.
