# 🩺 SeraphAID

**Sistema integral de información al paciente que traduce información clínica compleja en explicaciones comprensibles, accionables y seguras.**

Actualmente enfocado en la **interpretación de exámenes de laboratorio**, con una arquitectura modular diseñada para expandirse a medicamentos, documentos clínicos, orientación post-consulta y educación personalizada.

> ⚠️ **Este sistema nunca reemplaza la atención médica profesional. Nunca emite diagnósticos.**  
> Todo output generado por la aplicación incluye un recordatorio explícito de que no sustituye la evaluación de un profesional de la salud.

---

## 🧭 Filosofía y reglas permanentes

1. **No reemplazar criterio médico profesional**.
2. **No emitir diagnósticos definitivos**.
3. **No romper funcionalidades existentes** sin revisar primero.
4. **Priorizar refactor progresivo** sobre reescritura total.
5. **Documentar decisiones importantes** en `DECISIONS.md`.
6. **Mantener compatibilidad con ejecución local en Windows**.
7. **Favorecer arquitectura modular y mantenible**.
8. **Todo output de la app debe incluir disclaimer** de "no reemplaza evaluación profesional".

---

## 🧱 Stack actual

| Componente       | Tecnología                           |
|------------------|--------------------------------------|
| Lenguaje         | Python 3.x                           |
| UI               | [Streamlit](https://streamlit.io/)   |
| Validación       | Pydantic                             |
| Datos tabulares  | pandas                               |
| OCR / PDF        | pdfplumber, pytesseract, Pillow      |
| Voz (TTS)        | ElevenLabs (vía `requests`)          |
| IA conversacional| OpenAI (SDK instalado, aún no conectado) |

---

## 📁 Estructura de archivos clave
