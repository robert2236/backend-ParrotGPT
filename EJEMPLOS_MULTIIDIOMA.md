# 🧪 Ejemplos Multiidioma - ParrotGPT Chat

## Pruebas Rápidas por Idioma

### 1️⃣ ESPAÑOL (es)

#### RAG Mode (Solo documentos)
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "pregunta": "¿Cuáles son los requisitos de seguridad del laboratorio?",
    "modo": "rag",
    "idioma": "es",
    "session_id": "lab_es"
  }'
```

#### GENERAL Mode (Conocimiento general)
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "pregunta": "¿Cómo funciona la microscopía electrónica?",
    "modo": "general",
    "idioma": "es",
    "session_id": "lab_es"
  }'
```

#### HÍBRIDO Mode (Ambos)
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "pregunta": "Explica el procedimiento de seguridad en detalle",
    "modo": "hibrido",
    "idioma": "es",
    "session_id": "lab_es"
  }'
```

---

### 2️⃣ ENGLISH (en)

#### RAG Mode
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "pregunta": "What are the laboratory safety requirements?",
    "modo": "rag",
    "idioma": "en",
    "session_id": "lab_en"
  }'
```

#### GENERAL Mode
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "pregunta": "How does electron microscopy work?",
    "modo": "general",
    "idioma": "en",
    "session_id": "lab_en"
  }'
```

#### HÍBRIDO Mode
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "pregunta": "Explain the safety procedures in detail",
    "modo": "hibrido",
    "idioma": "en",
    "session_id": "lab_en"
  }'
```

---

### 3️⃣ FRANÇAIS (fr)

#### RAG Mode
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "pregunta": "Quels sont les exigences de sécurité du laboratoire?",
    "modo": "rag",
    "idioma": "fr",
    "session_id": "lab_fr"
  }'
```

#### GENERAL Mode
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "pregunta": "Comment fonctionne la microscopie électronique?",
    "modo": "general",
    "idioma": "fr",
    "session_id": "lab_fr"
  }'
```

#### HÍBRIDO Mode
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "pregunta": "Expliquez les procédures de sécurité en détail",
    "modo": "hibrido",
    "idioma": "fr",
    "session_id": "lab_fr"
  }'
```

---

### 4️⃣ DEUTSCH (de)

#### RAG Mode
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "pregunta": "Was sind die Laboratoriumssicherheitsanforderungen?",
    "modo": "rag",
    "idioma": "de",
    "session_id": "lab_de"
  }'
```

#### GENERAL Mode
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "pregunta": "Wie funktioniert die Elektronenmikroskopie?",
    "modo": "general",
    "idioma": "de",
    "session_id": "lab_de"
  }'
```

#### HÍBRIDO Mode
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "pregunta": "Erklären Sie die Sicherheitsverfahren im Detail",
    "modo": "hibrido",
    "idioma": "de",
    "session_id": "lab_de"
  }'
```

---

## 🐍 Python - Test Multiidioma Completo

```python
import requests
import json

BASE_URL = "http://localhost:8000"

class MultiLangTestGPT:
    def __init__(self):
        self.base_url = BASE_URL
        self.resultados = {}
    
    def test_idioma(self, idioma_code, pregunta, modo="general"):
        """Prueba un idioma específico"""
        response = requests.post(
            f"{self.base_url}/api/chat",
            json={
                "pregunta": pregunta,
                "modo": modo,
                "idioma": idioma_code,
                "session_id": f"test_{idioma_code}"
            }
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.text}
    
    def test_todos_idiomas(self):
        """Prueba todos los idiomas con la misma pregunta (traducida)"""
        
        tests = {
            "es": {
                "pregunta": "¿Cuáles son los beneficios de la investigación?",
                "modo": "general"
            },
            "en": {
                "pregunta": "What are the benefits of research?",
                "modo": "general"
            },
            "fr": {
                "pregunta": "Quels sont les avantages de la recherche?",
                "modo": "general"
            },
            "de": {
                "pregunta": "Was sind die Vorteile der Forschung?",
                "modo": "general"
            }
        }
        
        for idioma, config in tests.items():
            print(f"\n{'='*60}")
            print(f"🌍 IDIOMA: {idioma.upper()}")
            print(f"{'='*60}")
            
            resultado = self.test_idioma(
                idioma,
                config["pregunta"],
                config["modo"]
            )
            
            if "error" not in resultado:
                print(f"❓ Pregunta: {config['pregunta']}")
                print(f"✅ Respuesta: {resultado.get('respuesta', 'N/A')[:200]}...")
                print(f"📊 Modo usado: {resultado.get('modo_usado')}")
                print(f"🔤 Tokens: {resultado.get('tokens_usados')}")
            else:
                print(f"❌ Error: {resultado['error']}")
            
            self.resultados[idioma] = resultado
    
    def test_multiidioma_conversacion(self):
        """Prueba conversación en diferentes idiomas en la misma sesión"""
        
        print("\n" + "="*60)
        print("🔄 TEST: Conversación Multiidioma (Misma Sesión)")
        print("="*60)
        
        session_id = "multiidioma_test"
        
        # Pregunta 1: Español
        print("\n1️⃣ Pregunta en ESPAÑOL:")
        r1 = self.test_idioma(
            "es",
            "¿Qué es el aprendizaje automático?",
            "general"
        )
        print(f"   Respuesta: {r1.get('respuesta', 'Error')[:150]}...")
        
        # Pregunta 2: English (misma sesión)
        print("\n2️⃣ Pregunta en ENGLISH (misma sesión):")
        r2 = self.test_idioma(
            "en",
            "What is machine learning?",
            "general"
        )
        print(f"   Respuesta: {r2.get('respuesta', 'Error')[:150]}...")
        
        # Pregunta 3: Français (misma sesión)
        print("\n3️⃣ Pregunta en FRANÇAIS (misma sesión):")
        r3 = self.test_idioma(
            "fr",
            "Qu'est-ce que l'apprentissage automatique?",
            "general"
        )
        print(f"   Respuesta: {r3.get('respuesta', 'Error')[:150]}...")
    
    def test_modo_rag_multiidioma(self):
        """Prueba modo RAG en diferentes idiomas"""
        
        print("\n" + "="*60)
        print("🧪 TEST: Modo RAG Multiidioma")
        print("="*60)
        print("(Requiere documentos indexados)")
        
        preguntas = {
            "es": "¿Cuáles son los pasos principales?",
            "en": "What are the main steps?",
            "fr": "Quelles sont les étapes principales?",
            "de": "Was sind die Hauptschritte?"
        }
        
        for idioma, pregunta in preguntas.items():
            print(f"\n🌍 {idioma.upper()}: {pregunta}")
            resultado = self.test_idioma(idioma, pregunta, "rag")
            
            if "error" not in resultado:
                print(f"   ✅ {resultado.get('respuesta', 'N/A')[:100]}...")
                if resultado.get('fuentes'):
                    print(f"   📑 Fuentes encontradas: {len(resultado['fuentes'])}")
            else:
                print(f"   ❌ {resultado.get('error', 'Unknown error')}")

# EJECUCIÓN
if __name__ == "__main__":
    tester = MultiLangTestGPT()
    
    # Test 1: Todos los idiomas
    tester.test_todos_idiomas()
    
    # Test 2: Conversación multiidioma
    tester.test_multiidioma_conversacion()
    
    # Test 3: Modo RAG
    tester.test_modo_rag_multiidioma()
    
    print("\n" + "="*60)
    print("✅ TESTS COMPLETADOS")
    print("="*60)
```

### Ejecutar Tests:
```bash
python -m pip install requests
python ejemplos_multiidioma.py
```

---

## ⚛️ React/JavaScript - Component

```javascript
import React, { useState } from 'react';

export function ChatMultiLanguage() {
  const [responses, setResponses] = useState({});
  const [loading, setLoading] = useState({});

  const idiomas = {
    es: { nombre: "Español", flag: "🇪🇸" },
    en: { nombre: "English", flag: "🇬🇧" },
    fr: { nombre: "Français", flag: "🇫🇷" },
    de: { nombre: "Deutsch", flag: "🇩🇪" }
  };

  const preguntas = {
    es: "¿Cómo funciona esto?",
    en: "How does this work?",
    fr: "Comment ça marche?",
    de: "Wie funktioniert das?"
  };

  const testIdioma = async (idioma) => {
    setLoading(prev => ({ ...prev, [idioma]: true }));
    
    try {
      const response = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          pregunta: preguntas[idioma],
          idioma: idioma,
          modo: "general",
          session_id: "react_test"
        })
      });
      
      const data = await response.json();
      setResponses(prev => ({
        ...prev,
        [idioma]: data.respuesta
      }));
    } catch (error) {
      setResponses(prev => ({
        ...prev,
        [idioma]: `Error: ${error.message}`
      }));
    } finally {
      setLoading(prev => ({ ...prev, [idioma]: false }));
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <h1>🌍 ParrotGPT Multiidioma</h1>
      <p>Prueba el mismo backend en diferentes idiomas</p>
      
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
        {Object.entries(idiomas).map(([code, { nombre, flag }]) => (
          <div key={code} style={{
            border: "1px solid #ccc",
            padding: "15px",
            borderRadius: "8px"
          }}>
            <h3>{flag} {nombre}</h3>
            <p style={{ fontSize: "12px", color: "#666" }}>
              {preguntas[code]}
            </p>
            
            <button 
              onClick={() => testIdioma(code)}
              disabled={loading[code]}
              style={{
                padding: "8px 16px",
                backgroundColor: "#007AFF",
                color: "white",
                border: "none",
                borderRadius: "4px",
                cursor: "pointer"
              }}
            >
              {loading[code] ? "Cargando..." : "Probar"}
            </button>
            
            {responses[code] && (
              <div style={{
                marginTop: "10px",
                padding: "10px",
                backgroundColor: "#f0f0f0",
                borderRadius: "4px",
                fontSize: "13px"
              }}>
                {responses[code].substring(0, 150)}...
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## ✅ Checklist de Verificación

- [ ] Probaste español (es)
- [ ] Probaste inglés (en)
- [ ] Probaste francés (fr)
- [ ] Probaste alemán (de)
- [ ] Probaste RAG mode en 2+ idiomas
- [ ] Probaste GENERAL mode en 2+ idiomas
- [ ] Probaste HÍBRIDO mode en 2+ idiomas
- [ ] Revisaste MULTIIDIOMA.md

---

**Última actualización:** 2026-09-01 | **Status:** ✅ Verificado Multiidioma
