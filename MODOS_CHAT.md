# 🤖 Sistema de Modos de Chat - ParrotGPT

## Resumen
El backend ahora soporta **3 modos de conversación** en español para adaptarse a diferentes necesidades:

```
📌 RAG (Retrieval-Augmented Generation)
📌 GENERAL (Conocimiento General) 
📌 HÍBRIDO (Combinado)
```

---

## 📡 Endpoint Principal

```
POST /api/chat
```

### Estructura del Request

```json
{
  "pregunta": "¿Cuál es el reglamento del laboratorio?",
  "session_id": "mi_sesion_123",
  "modo": "rag",
  "incluir_fuentes": true
}
```

### Parámetros

| Parámetro | Tipo | Obligatorio | Descripción | Default |
|-----------|------|------------|-------------|---------|
| `pregunta` | string | ✅ | La pregunta del usuario | - |
| `session_id` | string | ❌ | ID de la conversación | "default" |
| `modo` | string | ❌ | Modo: "rag", "general", "hibrido" | "rag" |
| `incluir_fuentes` | boolean | ❌ | Retornar documentos de referencia | true |

---

## 🎯 Modos de Funcionamiento

### 1️⃣ **RAG** (Modo Estricto)
Responde ÚNICAMENTE usando documentos indexados.

**Casos de uso:**
- ✅ Preguntas sobre reglamentos/manuales
- ✅ Consultas sobre documentos específicos
- ✅ Información confidencial/sensible
- ❌ Explicaciones generales

**Ejemplo:**
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "pregunta": "¿Cuáles son los requisitos de seguridad?",
    "modo": "rag",
    "session_id": "sesion_lab"
  }'
```

**Respuesta:**
```json
{
  "respuesta": "Según el documento de seguridad, los requisitos son...",
  "modo_usado": "rag",
  "fuentes": [
    {
      "contenido": "Los requisitos de seguridad incluyen...",
      "metadata": {"source": "reglamento.pdf", "page": 2}
    }
  ],
  "tokens_usados": {"entrada": 8, "salida": 45}
}
```

---

### 2️⃣ **GENERAL** (Modo Libre)
Usa conocimiento general del LLM sin documentos.

**Casos de uso:**
- ✅ Explicaciones conceptuales
- ✅ Brainstorming y lluvia de ideas
- ✅ Preguntas no relacionadas con documentos
- ✅ Estilo ChatGPT tradicional

**Ejemplo:**
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "pregunta": "¿Cómo funciona la microscopía electrónica?",
    "modo": "general",
    "session_id": "sesion_lab"
  }'
```

**Respuesta:**
```json
{
  "respuesta": "La microscopía electrónica es una técnica que utiliza...",
  "modo_usado": "general",
  "fuentes": [],
  "tokens_usados": {"entrada": 9, "salida": 120}
}
```

---

### 3️⃣ **HÍBRIDO** (Mejor de Ambos)
Responde primero con documentos, complementa con conocimiento general.

**Casos de uso:**
- ✅ Profundizar en temas específicos
- ✅ Corregir/complementar información de documentos
- ✅ Balancear especificidad con amplitud
- ✅ Máxima versatilidad

**Ejemplo:**
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "pregunta": "Explica cómo usar el microscopio del laboratorio",
    "modo": "hibrido",
    "session_id": "sesion_lab",
    "incluir_fuentes": true
  }'
```

**Respuesta:**
```json
{
  "respuesta": "[Según documentos] El microscopio requiere: 1) Calibración inicial... [Con conocimiento general] Adicionalmente, es importante saber que...",
  "modo_usado": "hibrido",
  "fuentes": [
    {
      "contenido": "Instrucciones de calibración: ...",
      "metadata": {"source": "manual_equipo.pdf", "page": 5}
    }
  ],
  "tokens_usados": {"entrada": 11, "salida": 200}
}
```

---

## 🔄 Comparación de Modos

| Aspecto | RAG | General | Híbrido |
|---------|-----|---------|---------|
| **Usa documentos** | ✅ | ❌ | ✅ |
| **Usa conocimiento general** | ❌ | ✅ | ✅ |
| **Requiere archivos** | ✅ | ❌ | ❌ |
| **Mejor para precisión** | ✅✅✅ | ⚠️ | ✅✅ |
| **Mejor para flexibilidad** | ❌ | ✅✅✅ | ✅✅ |
| **Mejor para ChatGPT-like** | ❌ | ✅✅✅ | ✅✅ |

---

## 🚀 Ejemplos Prácticos

### Uso desde Python
```python
import requests

BASE_URL = "http://localhost:8000"
HEADERS = {"Authorization": "Bearer tu_token"}

# Usar modo RAG (solo documentos)
response = requests.post(
    f"{BASE_URL}/api/chat",
    headers=HEADERS,
    json={
        "pregunta": "¿Cuál es el protocolo de seguridad?",
        "modo": "rag",
        "session_id": "lab_sesion_1"
    }
)
print(response.json())

# Usar modo General (conocimiento general)
response = requests.post(
    f"{BASE_URL}/api/chat",
    headers=HEADERS,
    json={
        "pregunta": "¿Cómo instalo un software?",
        "modo": "general",
        "session_id": "lab_sesion_1"
    }
)
print(response.json())

# Usar modo Híbrido (lo mejor de ambos)
response = requests.post(
    f"{BASE_URL}/api/chat",
    headers=HEADERS,
    json={
        "pregunta": "Explica cómo usar el equipo XYZ",
        "modo": "hibrido",
        "session_id": "lab_sesion_1"
    }
)
print(response.json())
```

### Uso desde JavaScript/Frontend
```javascript
async function chat(pregunta, modo = "rag") {
  const response = await fetch("http://localhost:8000/api/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify({
      pregunta: pregunta,
      modo: modo,
      session_id: "sesion_actual",
      incluir_fuentes: true
    })
  });
  
  const data = await response.json();
  console.log(`Respuesta (${data.modo_usado}):`, data.respuesta);
  console.log("Fuentes:", data.fuentes);
}

// Llamadas
chat("¿Reglas del laboratorio?", "rag");
chat("¿Cómo funciona la ciencia?", "general");
chat("Cómo usar el microscopio", "hibrido");
```

---

## ⚙️ Configuración

### Variables de Entorno
```bash
# Modelo LLM a usar
LLM_MODELO=gemini-2.5-flash

# API Key (si usas Gemini)
GEMINI_API_KEY=sk-...

# Embeddings
EMBEDDINGS_MODELO=paraphrase-multilingual-MiniLM-L12-v2

# Recuperación
RETRIEVER_K=4
CHUNK_SIZE=800
CHUNK_OVERLAP=150
```

### Rutas de Base de Datos
```
data/
├── pdf/              # PDFs subidos
└── vectorial/        # Base de datos vectorial (Chroma)
    └── chroma.sqlite3
```

---

## 🔍 Troubleshooting

### "Modo no válido"
```
Error: Modo no válido. Use: 'rag', 'general' o 'hibrido'
```
**Solución:** Verifica que el campo `modo` tenga valor exacto: `"rag"`, `"general"` o `"hibrido"`

### "No hay documentos indexados"
```
Error: No hay documentos indexados. Modo 'rag' requiere documentos.
```
**Solución:** Sube un PDF primero usando POST `/api/upload`

### Respuesta vacía en modo RAG
Significa que los documentos no contienen información sobre la pregunta.
**Alternativa:** Cambia a modo `"hibrido"` para obtener respuesta del LLM.

---

## 📊 Monitoreo

### Ver historial de sesión
```bash
GET /api/historial/{session_id}
```

### Buscar en documentos
```bash
POST /api/buscar
{
  "pregunta": "seguridad",
  "k": 5,
  "user_id": "usuario_123"
}
```

---

## 🎓 Recomendaciones

| Situación | Modo Recomendado |
|-----------|-----------------|
| Preguntas sobre un documento específico | **RAG** |
| Aprender conceptos generales | **GENERAL** |
| Combinar teoría + práctica del documento | **HÍBRIDO** |
| Máxima confiabilidad/precisión | **RAG** |
| Máxima flexibilidad/conversación | **GENERAL** |
| Equilibrio perfecto | **HÍBRIDO** |

---

## 📝 Notas Importantes

- ✅ Los modos están completamente en **español**
- ✅ Cada respuesta incluye `modo_usado` para verificación
- ✅ Las fuentes se retornan solo si están disponibles
- ✅ Historial se guarda automáticamente
- ✅ Compatible con el endpoint anterior `/api/ask`

---

**Versión:** 1.0 | **Actualizado:** 2026-09-01
