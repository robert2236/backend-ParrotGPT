import os
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

# --- LLM CONFIGURACIÓN CON GEMINI ---
PROVEEDOR_LLM = "gemini"
# Modelo gratuito recomendado de alta velocidad y 1M de ventana de contexto:
LLM_MODELO = os.getenv("LLM_MODELO", "gemini-2.5-flash")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# --- EMBEDDINGS Y RAG ---
EMBEDDINGS_MODELO = "paraphrase-multilingual-MiniLM-L12-v2"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150
RETRIEVER_K = 4

RUTA_PDF = RAIZ / "data" / "pdf"
RUTA_BD_VECTORIAL = str(RAIZ / "data" / "vectorial")


#version with local model config
""" from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

LLM_MODELO = "llama3.2"
EMBEDDINGS_MODELO = "paraphrase-multilingual-MiniLM-L12-v2"

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150

RETRIEVER_K = 4

RUTA_PDF = RAIZ / "data" / "pdf"
RUTA_BD_VECTORIAL = str(RAIZ / "data" / "vectorial")
 """