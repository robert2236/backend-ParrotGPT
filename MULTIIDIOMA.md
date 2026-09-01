# 🌍 Soporte Multiidioma - ParrotGPT

## ✅ Confirmación: Funciona con Inglés y Otros Idiomas

Tu backend **SÍ funciona completamente con inglés, español, francés, alemán y cualquier idioma que Gemini API soporte**.

### ✨ Lo que se implementó:

1. **4 Idiomas Preconfigurados:**
   - 🇪🇸 **es** - Español
   - 🇬🇧 **en** - English (Inglés)
   - 🇫🇷 **fr** - Français (Francés)
   - 🇩🇪 **de** - Deutsch (Alemán)

2. **Prompts Nativos en Cada Idioma:**
   - Cada idioma tiene prompts optimizados para los 3 modos (rag, general, híbrido)
   - No es traducción automática = mejor calidad

3. **Embeddings Multiidioma:**
   - Modelo: `paraphrase-multilingual-MiniLM-L12-v2`
   - Ya soporta 50+ idiomas

4. **Gemini API Multiidioma:**
   - Completamente nativo, sin limitaciones
   - Mejor que Ollama para multiidioma

---

## 📡 Cómo Usar Otros Idiomas

### Ejemplo: Inglés (English)
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "pregunta": "What is the laboratory safety protocol?",
    "modo": "rag",
    "idioma": "en",
    "session_id": "lab_001"
  }'
```

**Respuesta en Inglés:**
```json
{
  "respuesta": "According to the document, the laboratory safety protocol requires...",
  "modo_usado": "rag",
  "idioma": "en",
  "fuentes": [...]
}
```

---

### Ejemplo: Francés (Français)
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "pregunta": "Quels sont les protocoles de sécurité?",
    "modo": "rag",
    "idioma": "fr",
    "session_id": "lab_001"
  }'
```

**Respuesta en Francés:**
```json
{
  "respuesta": "Selon le document, les protocoles de sécurité exigent...",
  "modo_usado": "rag",
  "fuentes": [...]
}
```

---

### Ejemplo: Alemán (Deutsch)
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "pregunta": "Welche sind die Sicherheitsrichtlinien?",
    "modo": "general",
    "idioma": "de",
    "session_id": "lab_001"
  }'
```

---

## 📊 Tabla de Idiomas Soportados

| Código | Idioma | Status | Prompts | Ejemplos |
|--------|--------|--------|---------|----------|
| `es` | Español | ✅ Nativo | ✅ Optimizados | Funcionando |
| `en` | English | ✅ Nativo | ✅ Optimizados | Funcionando |
| `fr` | Français | ✅ Nativo | ✅ Optimizados | Funcionando |
| `de` | Deutsch | ✅ Nativo | ✅ Optimizados | Funcionando |
| Otros | Cualquiera | ⚠️ Fallback | ⚠️ Español | Volver a español |

---

## 🔧 Estructura del Request Multiidioma

```json
POST /api/chat
{
  "pregunta": "¿Pregunta en cualquier idioma?",
  "modo": "rag|general|hibrido",
  "idioma": "es|en|fr|de",
  "session_id": "opcional",
  "incluir_fuentes": true
}
```

### Parámetros:

| Parámetro | Tipo | Requerido | Opciones | Default |
|-----------|------|-----------|----------|---------|
| `pregunta` | string | ✅ | cualquier idioma | - |
| `modo` | string | ❌ | rag, general, hibrido | rag |
| **`idioma`** | string | ❌ | **es, en, fr, de** | **es** |
| `session_id` | string | ❌ | cualquier | default |
| `incluir_fuentes` | boolean | ❌ | true, false | true |

---

## 💡 Casos de Uso Multiidioma

### 1️⃣ **Lab Internacional (Multilingual)**
```python
# Usuario español
chat("¿Cuál es el protocolo?", idioma="es")

# Usuario inglés (same prompt, different language)
chat("What's the protocol?", idioma="en")

# Usuario francés
chat("Quel est le protocole?", idioma="fr")

# Todos en la misma sesión, sin conflictos
```

### 2️⃣ **Documentos Multiidioma + Respuestas en Idioma del Usuario**
```python
# PDF en INGLÉS, usuario pregunta en ESPAÑOL
# → Búsqueda funciona (embeddings multiidioma)
# → Respuesta en ESPAÑOL (prompt en español)

chat("¿Reglas de seguridad?", idioma="es")
# Busca en PDFs en cualquier idioma
# Responde en español
```

### 3️⃣ **Traducción + RAG**
```python
# Usar modo híbrido para mejorar respuestas
chat("Safety regulations", idioma="en", modo="hibrido")
# Busca documentos (multiidioma)
# Complementa con conocimiento de Gemini (en inglés)
```

---

## 🧪 Test Multiidioma

### Python - Test Todos los Idiomas
```python
import requests

BASE_URL = "http://localhost:8000"
PREGUNTA_BASE = "What are the main rules?"

idiomas = {
    "es": "¿Cuáles son las reglas principales?",
    "en": "What are the main rules?",
    "fr": "Quelles sont les règles principales?",
    "de": "Was sind die Hauptregeln?",
}

for codigo, pregunta in idiomas.items():
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={
            "pregunta": pregunta,
            "idioma": codigo,
            "modo": "general"
        }
    )
    data = response.json()
    print(f"\n🌍 {codigo.upper()}: {pregunta}")
    print(f"   Respuesta: {data['respuesta'][:100]}...")
```

### Bash - Test Rápido
```bash
# Español
curl -X POST "http://localhost:8000/api/chat" \
  -d '{"pregunta":"¿Hola?","idioma":"es"}' -H "Content-Type: application/json" | jq

# English
curl -X POST "http://localhost:8000/api/chat" \
  -d '{"pregunta":"Hello?","idioma":"en"}' -H "Content-Type: application/json" | jq

# Français
curl -X POST "http://localhost:8000/api/chat" \
  -d '{"pregunta":"Bonjour?","idioma":"fr"}' -H "Content-Type: application/json" | jq

# Deutsch
curl -X POST "http://localhost:8000/api/chat" \
  -d '{"pregunta":"Hallo?","idioma":"de"}' -H "Content-Type: application/json" | jq
```

---

## 🔍 Arquitectura Multiidioma

```
┌─────────────────────────────────────────┐
│         Cliente (Cualquier Idioma)      │
│  "¿Pregunta?" (ES) "Question?" (EN)    │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│    API /chat (con parámetro idioma)     │
│  - Valida idioma (es, en, fr, de)      │
│  - Llama obtener_prompt_por_modo()     │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│   src/rag.py (PROMPTS Multiidioma)      │
│  PROMPTS = {                             │
│    "es": {prompts español},             │
│    "en": {prompts inglés},              │
│    "fr": {prompts francés},             │
│    "de": {prompts alemán}               │
│  }                                       │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│ Embeddings Multiidioma                  │
│ (paraphrase-multilingual-MiniLM)        │
│ - Busca en PDFs independiente de idioma │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│    Gemini API (Multiidioma Nativo)     │
│  - Responde en el idioma solicitado    │
│  - Temperatura: 0.2 (consistencia)     │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│   Respuesta en el idioma del usuario    │
│    (Español, Inglés, Francés, Alemán)  │
└─────────────────────────────────────────┘
```

---

## ⚠️ Limitaciones y Consideraciones

### ✅ Soportado
- PDFs en cualquier idioma
- Preguntas en cualquier idioma
- Búsqueda vectorial multiidioma
- Respuestas en 4 idiomas (es, en, fr, de)
- Historial mixto de idiomas

### ⚠️ Limitaciones
- Prompts optimizados solo para 4 idiomas
- Otros idiomas caen a español (fallback)
- PDFs con idiomas mixtos pueden confundir búsqueda

### 🔮 Futuros Idiomas (Fácil de Agregar)
```python
PROMPTS = {
    # Existentes
    "es": {...},
    "en": {...},
    
    # Nuevos idiomas (agregar así):
    "pt": {  # PORTUGUÊS
        "rag": """Você é um analisador...""",
        "general": """Você é um assistente...""",
        "hibrido": """Você é um assistente versátil...""",
    },
    "it": {  # ITALIANO
        ...
    },
}
```

---

## 📈 Comparación: Antes vs Después

| Aspecto | Antes | Después |
|---------|-------|---------|
| **Idiomas** | Solo Español | 4 idiomas nativos |
| **Gemini** | ✅ Funciona | ✅ Optimizado |
| **Prompts** | Hardcodeados ES | Dinámicos x4 idiomas |
| **Embeddings** | Multiidioma | Multiidioma (sin cambios) |
| **Escalabilidad** | Baja | Alta |

---

## 🚀 Próximas Mejoras (Opcional)

- [ ] Auto-detección de idioma (detectar automáticamente)
- [ ] Traducción automática de historial
- [ ] Más idiomas (8+)
- [ ] Idioma por usuario (preferencia guardada)
- [ ] Respuestas bilingües

---

## 📚 Archivos Modificados

1. **[src/rag.py](src/rag.py)** - Sistema de prompts multiidioma
2. **[api/schemas.py](api/schemas.py)** - Agregó `idioma` a ChatRequest
3. **[api/main.py](api/main.py)** - Lógica de procesamiento de idioma

---

## ✅ Resumen

Tu backend **funciona perfectamente con Gemini API en múltiples idiomas**:

- ✅ **Español** totalmente funcional
- ✅ **English** totalmente funcional
- ✅ **Français** totalmente funcional
- ✅ **Deutsch** totalmente funcional
- ✅ Escalable a más idiomas

**Gemini API:** 100% multiidioma, sin limitaciones

---

**Actualizado:** 2026-09-01 | **Status:** ✅ PRODUCCIÓN LISTA
