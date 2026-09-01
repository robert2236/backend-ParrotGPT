# 🚀 Quick Start - ParrotGPT Modos

## ⚡ Inicio Rápido (5 minutos)

### 1️⃣ Verificar que todo esté correcto

```bash
# Chequear sintaxis Python
python -m py_compile src/rag.py api/schemas.py api/main.py
echo "✅ Sintaxis correcta"
```

### 2️⃣ Iniciar el servidor

```bash
# Si usas Uvicorn
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# O con Python directamente
python api/main.py
```

### 3️⃣ Probar los 3 Modos

#### **Modo RAG** (Solo documentos)
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "pregunta": "¿Cuál es el tema principal?",
    "modo": "rag",
    "session_id": "test_1"
  }'
```

#### **Modo GENERAL** (Como ChatGPT)
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "pregunta": "¿Cuál es el tema principal?",
    "modo": "general",
    "session_id": "test_1"
  }'
```

#### **Modo HÍBRIDO** (Documentos + Conocimiento)
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "pregunta": "¿Cuál es el tema principal?",
    "modo": "hibrido",
    "session_id": "test_1"
  }'
```

---

## 📱 Respuesta Esperada

```json
{
  "respuesta": "La respuesta va aquí...",
  "modo_usado": "rag",
  "fuentes": [
    {
      "contenido": "Fragmento del documento...",
      "metadata": {
        "source": "archivo.pdf",
        "page": 1
      }
    }
  ],
  "tokens_usados": {
    "entrada": 5,
    "salida": 42
  }
}
```

---

## 🎯 Diferencias Clave

| Modo | Resultado |
|------|-----------|
| **rag** | Solo usa documentos, rechaza si no hay documentos |
| **general** | Puro LLM, ignorando documentos (estilo ChatGPT) |
| **hibrido** | Intenta documentos primero, complementa con LLM |

---

## 🔄 Mantener Compatibilidad

El endpoint antiguo `/api/ask` **sigue funcionando exactamente igual**:

```bash
curl -X POST "http://localhost:8000/api/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "pregunta": "¿Pregunta?",
    "session_id": "default"
  }'
```

---

## 📖 Documentación Completa

Para más detalles, revisa:
- 📚 [MODOS_CHAT.md](./MODOS_CHAT.md) - Guía detallada
- 🧪 [EJEMPLOS_REQUESTS.md](./EJEMPLOS_REQUESTS.md) - Ejemplos prácticos
- ✅ [CAMBIOS_IMPLEMENTADOS.md](./CAMBIOS_IMPLEMENTADOS.md) - Qué cambió

---

## 🐛 Troubleshooting Rápido

### Error: "Modo no válido"
→ Usa exactamente: `"modo": "rag"` o `"general"` o `"hibrido"`

### Error: "No hay documentos"
→ Sube un PDF primero con `/api/upload`

### Respuesta vacía (RAG)
→ Los documentos no tienen la información. Intenta con modo `hibrido`

---

## ✅ Checklist

- [ ] Servidor iniciado en puerto 8000
- [ ] Probaste los 3 modos
- [ ] Revisaste la documentación
- [ ] Los archivos no tienen errores

---

**¡Listo! Tu backend ahora es tipo ChatGPT con 3 modos en español** 🎉
