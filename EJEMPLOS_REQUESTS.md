# 🧪 Ejemplos de Requests - ParrotGPT Chat Modes

## Archivo para pruebas con curl o Postman

### 1️⃣ MODO RAG (Solo Documentos)

#### Pregunta Simple
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "pregunta": "¿Cuáles son los requisitos de seguridad del laboratorio?",
    "session_id": "lab_session_001",
    "modo": "rag",
    "incluir_fuentes": true
  }'
```

#### Con Historial (misma sesión)
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "pregunta": "¿Cuáles son los EPP necesarios?",
    "session_id": "lab_session_001",
    "modo": "rag",
    "incluir_fuentes": true
  }'
```

---

### 2️⃣ MODO GENERAL (Conocimiento General - ChatGPT Style)

#### Pregunta Conceptual
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "pregunta": "¿Cómo funciona la fotosíntesis?",
    "session_id": "general_session_001",
    "modo": "general",
    "incluir_fuentes": false
  }'
```

#### Pregunta Educativa
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "pregunta": "Explica la diferencia entre mitosis y meiosis",
    "session_id": "general_session_001",
    "modo": "general"
  }'
```

#### Brainstorming
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "pregunta": "Dame 5 ideas para mejorar la seguridad en laboratorios",
    "session_id": "ideas_session",
    "modo": "general"
  }'
```

---

### 3️⃣ MODO HÍBRIDO (Documentos + Conocimiento General)

#### Complementar Información
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "pregunta": "Explica cómo usar el microscopio mencionado en el manual",
    "session_id": "hybrid_session_001",
    "modo": "hibrido",
    "incluir_fuentes": true
  }'
```

#### Análisis Profundo
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "pregunta": "¿Qué ventajas tiene el procedimiento del documento en comparación con otros métodos?",
    "session_id": "hybrid_session_001",
    "modo": "hibrido",
    "incluir_fuentes": true
  }'
```

#### Resolución de Problemas
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "pregunta": "El equipo no funciona según las instrucciones. ¿Qué podría estar mal?",
    "session_id": "troubleshoot_session",
    "modo": "hibrido",
    "incluir_fuentes": true
  }'
```

---

## 🔍 Tests de Edge Cases

### Pregunta sin Documentos (Modo RAG)
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "pregunta": "¿Cuál es tu nombre?",
    "session_id": "empty_docs",
    "modo": "rag"
  }'
# Esperado: Error indicando que no hay documentos
```

### Sesión Nueva vs Existente
```bash
# Primera pregunta - nueva sesión
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "pregunta": "¿Cuál es el tema?",
    "session_id": "nueva_sesion_123",
    "modo": "general"
  }'

# Segunda pregunta - misma sesión (debe recordar contexto)
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "pregunta": "¿Cuál es el título completo?",
    "session_id": "nueva_sesion_123",
    "modo": "general"
  }'
```

### Modo Inválido
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "pregunta": "¿Hola?",
    "modo": "invalido"
  }'
# Esperado: Error 400 "Modo no válido"
```

---

## 📤 Python Script de Pruebas

```python
import requests
import json

BASE_URL = "http://localhost:8000"

def test_chat(pregunta, modo, session_id="default"):
    """Función auxiliar para probar la API"""
    response = requests.post(
        f"{BASE_URL}/api/chat",
        json={
            "pregunta": pregunta,
            "session_id": session_id,
            "modo": modo,
            "incluir_fuentes": True
        }
    )
    
    print(f"\n{'='*60}")
    print(f"🎯 Modo: {modo.upper()}")
    print(f"❓ Pregunta: {pregunta}")
    print(f"{'='*60}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Respuesta ({data.get('modo_usado')}):")
        print(f"   {data.get('respuesta')}")
        print(f"\n📊 Tokens: {data.get('tokens_usados')}")
        
        if data.get('fuentes'):
            print(f"\n📑 Fuentes ({len(data.get('fuentes'))} documento(s)):")
            for i, fuente in enumerate(data.get('fuentes'), 1):
                print(f"   {i}. {fuente.get('metadata', {}).get('source', 'desconocido')}")
    else:
        print(f"❌ Error {response.status_code}: {response.text}")

# PRUEBAS
if __name__ == "__main__":
    # Test RAG
    test_chat(
        "¿Cuáles son las normas de seguridad?",
        "rag",
        "test_rag"
    )
    
    # Test General
    test_chat(
        "¿Cómo funciona un microscopio?",
        "general",
        "test_general"
    )
    
    # Test Híbrido
    test_chat(
        "Explica el equipo con más detalle",
        "hibrido",
        "test_hibrido"
    )
    
    # Test continuidad de sesión
    test_chat(
        "¿Cuál es el tema?",
        "general",
        "sesion_continua"
    )
    test_chat(
        "¿Y cuáles son los pasos?",
        "general",
        "sesion_continua"  # Misma sesión
    )
```

---

## 📊 Respuesta Esperada (Ejemplo)

```json
{
  "respuesta": "Según el documento de seguridad del laboratorio, los requisitos principales son: 1) Uso obligatorio de bata de laboratorio...",
  "modo_usado": "rag",
  "fuentes": [
    {
      "contenido": "Los requisitos de seguridad incluyen el uso de equipos de protección personal (EPP) adecuados para cada tarea específica.",
      "metadata": {
        "source": "reglamento_seguridad.pdf",
        "page": 2,
        "session_id": "lab_session_001",
        "user_id": "usuario_123"
      }
    }
  ],
  "tokens_usados": {
    "entrada": 8,
    "salida": 45
  }
}
```

---

## 🔌 Integración con Frontend

### React Example
```javascript
async function sendChat(pregunta, modo = "rag") {
  try {
    const response = await fetch("http://localhost:8000/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        pregunta,
        modo,
        session_id: sessionStorage.getItem("session_id") || "new_session",
        incluir_fuentes: true
      })
    });

    if (!response.ok) {
      throw new Error(`Error: ${response.statusText}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error:", error);
    return null;
  }
}

// Uso
const resultado = await sendChat("¿Cuál es el reglamento?", "rag");
console.log(resultado.respuesta);
console.log(`Modo usado: ${resultado.modo_usado}`);
```

---

## ⏱️ Tiempos Esperados

| Modo | Tiempo Típico | Factores |
|------|---------------|----------|
| RAG | 1-3 seg | Tamaño BD, velocidad red |
| GENERAL | 2-5 seg | Complejidad pregunta, modelo |
| HÍBRIDO | 2-6 seg | Búsqueda + generación |

---

## 🛠️ Debugging

### Ver respuesta completa
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"pregunta": "test", "modo": "general"}' | jq .
```

### Ver solo la respuesta
```bash
curl -s -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"pregunta": "test", "modo": "general"}' | jq '.respuesta'
```

### Ver fuentes
```bash
curl -s -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"pregunta": "test", "modo": "rag"}' | jq '.fuentes'
```

---

**Última actualización:** 2026-09-01
