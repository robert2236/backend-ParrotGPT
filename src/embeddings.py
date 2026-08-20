import os
from functools import lru_cache
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_ollama import OllamaEmbeddings

# Cambia a True en tu .env local si quieres usar Ollama
USE_LOCAL = os.getenv("USE_LOCAL_LLM", "false").lower() == "true"

@lru_cache(maxsize=1)
def obtener_modelo():
    if USE_LOCAL:
        # Usa Ollama cuando estás en tu PC
        return OllamaEmbeddings(model="nomic-embed-text")
    else:
        # Usa Gemini cuando estás en Render o producción
        return GoogleGenerativeAIEmbeddings(
            model="text-embedding-004", # Sin el prefijo "models/"
            google_api_key=os.getenv("GEMINI_API_KEY")
        )