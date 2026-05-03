# UX_UI_SPEC.md — SeraphAID

---

## Principios de diseño

1. **Claridad sobre complejidad**: el usuario es paciente, no médico.
2. **Accesibilidad**: texto legible, contraste, audio opcional.
3. **Confianza sin alarmismo**: colores y tono que informan sin generar ansiedad innecesaria.
4. **Progresivo**: mostrar lo simple primero, detalle bajo demanda (expanders).
5. **Seguro por diseño**: disclaimer siempre visible.

---

## Tono visual

- Paleta: blanco/gris claro + acento azul/verde (salud, calma).
- Iconos: emojis clínicos (🧪 examen, 💊 medicamento, 📄 documento).
- Tipografía: la de Streamlit (sans-serif legible).
- Nunca rojo alarmante como color dominante; usarlo solo en semáforo de alertas críticas.

---

## Estructura de navegación (objetivo v1.0)

```
SeraphAID
├── [Tab/Página] 🧪 Exámenes de laboratorio  ← ACTUAL
├── [Tab/Página] 💊 Medicamentos             ← MÓDULO B (próximo)
├── [Tab/Página] 📄 Indicaciones médicas     ← MÓDULO C (futuro)
└── [Tab/Página] ℹ️ Acerca de / Ayuda
```

---

## Pantalla principal — Exámenes

### Header
```
SeraphAID – Intérprete de Exámenes
[Caption/disclaimer visible siempre]
```

### Sección 1: Carga de examen
- File uploader: PDF, JPG, PNG
- Preview de extracción en expander colapsado
- Estado: "Cargando...", "Texto extraído", "No se pudo leer el archivo"

### Sección 2: Formulario de valores
- Campos básicos siempre visibles: edad, sexo + marcadores principales (Hb, glucosa, colesterol, creatinina)
- Secciones adicionales en expanders: Perfil hepático, Electrolitos/Renal, Hemograma, Gases
- Valores precargados si se detectaron del PDF
- Botón prominente: "Interpretar resultados"

### Sección 3: Resultados (post-submit)
- Semáforo por marcador: 🔴 alto/bajo, 🟠 límite, 🟢 normal
- Tabla o lista compacta con todos los marcadores ingresados
- Expandir para ver explicación de cada alterado
- Resumen general en texto simple
- Botón "Escuchar resumen" (TTS, si API key disponible)
- Disclaimer siempre al pie

### Sidebar
- Fuente de rangos (selectbox)
- Margen para "límite" (slider)
- Opciones de carga de CSV de rangos

---

## Estados de carga y error

| Situación | UI |
|---|---|
| Procesando PDF | Spinner + "Extrayendo texto del examen..." |
| Validación fallida (Pydantic) | `st.error()` con mensaje amigable |
| Sin rangos para un marcador | "Sin referencia disponible" (no alarma) |
| Sin API key para TTS | Warning suave, botón deshabilitado |
| Sin API key para LLM | Funciona solo con reglas (sin aviso intrusivo) |
| Error de red (ElevenLabs/OpenAI) | `st.error()` con mensaje descriptivo |

---

## Flujo del usuario (happy path)

```
1. Abre la app
2. Sube PDF o imagen de su examen
3. El sistema extrae y precarga los valores
4. Revisa/ajusta valores en el formulario
5. Clic "Interpretar resultados"
6. Ve semáforo de resultados
7. Lee explicaciones en lenguaje simple
8. (Opcional) Escucha el resumen en audio
9. Anota qué consultar con su médico
```

---

## Mejoras UX para Sprint 3 (propuestas)

- Reorganizar resultados: primero los alterados, luego los normales.
- Agregar sección "¿Qué hacer a continuación?" con checklist simple.
- Resaltar los valores más críticos con jerarquía visual.
- Añadir tooltips explicativos en cada nombre de marcador.
- Progress indicator durante procesamiento de PDF largo.
