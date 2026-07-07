from functools import lru_cache
from langchain_huggingface import HuggingFaceEmbeddings

from src.config import EMBEDDINGS_MODELO


@lru_cache(maxsize=1)
def obtener_modelo(nombre: str = EMBEDDINGS_MODELO):
    return HuggingFaceEmbeddings(model_name=nombre)
