from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

LLM_MODELO = "llama3.2"
EMBEDDINGS_MODELO = "paraphrase-multilingual-MiniLM-L12-v2"

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150

RETRIEVER_K = 4

RUTA_PDF = RAIZ / "data" / "pdf"
RUTA_BD_VECTORIAL = str(RAIZ / "data" / "vectorial")
