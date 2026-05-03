
---

## 🔍 Bugs conocidos (monitoreados en `STATUS.md`)

| ID  | Descripción                                                                 |
|-----|-----------------------------------------------------------------------------|
| B1  | `normalize_marker()` sin `return` → el CSV de explicaciones nunca es consultado |
| B2  | API key hardcodeada en línea 1056 de `app.py` (riesgo de seguridad)         |
| B3  | Campo `hemoglobina` duplicado en el formulario de entrada                   |

---

## 🗺️ Módulos previstos

| Módulo | Nombre                          | Estado               |
|--------|---------------------------------|----------------------|
| A      | Exámenes de laboratorio         | ✅ En refinamiento   |
| B      | Medicamentos                    | 🔜 Próximo           |
| C      | Indicaciones / documentos clínicos | 📅 Planeado       |
| D      | Orientación post-consulta       | 📅 Planeado          |
| E      | Educación personalizada         | 📅 Planeado          |

---

## 🎯 Prioridad de implementación

1. **Corregir bugs críticos** (Sprint 1)  
2. **Separar datos del código** (Sprint 2)  
3. **Modularizar lógica** (Sprint 3)  
4. **Conectar LLM** (Sprint 4)  
5. **Módulo B: Medicamentos** (Sprint 5)

---

## 🧪 Ejecución local

```bash
# Clonar repositorio
git clone https://github.com/arlhinus/SeraphAID.git
cd SeraphAID

# Crear y activar entorno virtual
python -m venv venv
source venv/bin/activate   # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar claves API
cp .env.example .env
# Editar .env y añadir tus claves (ELEVEN_API_KEY, etc.)

# Ejecutar
streamlit run app.py
