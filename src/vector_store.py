from langchain_chroma import Chroma

from src.config import RUTA_BD_VECTORIAL, RETRIEVER_K
from src.loader import cargar_pdf
from src.splitter import fragmentar
from src.embeddings import obtener_modelo


def indexar(ruta_pdf: str) -> Chroma:
    modelo = obtener_modelo()
    docs = cargar_pdf(ruta_pdf)
    fragmentos = fragmentar(docs)
    bd = Chroma.from_documents(
        documents=fragmentos,
        embedding=modelo,
        persist_directory=RUTA_BD_VECTORIAL,
    )
    return bd


def agregar_documentos(fragmentos: list) -> Chroma:
    modelo = obtener_modelo()
    bd = Chroma(
        persist_directory=RUTA_BD_VECTORIAL,
        embedding_function=modelo,
    )
    bd.add_documents(fragmentos)
    return bd


def cargar_bd() -> Chroma:
    modelo = obtener_modelo()
    return Chroma(
        persist_directory=RUTA_BD_VECTORIAL,
        embedding_function=modelo,
    )


def obtener_retriever(k: int = RETRIEVER_K, filtro: dict | None = None):
    bd = cargar_bd()
    kwargs = {"k": k}
    if filtro:
        kwargs["filter"] = filtro
    return bd.as_retriever(search_kwargs=kwargs)


def buscar(pregunta: str, k: int = 1):
    bd = cargar_bd()
    return bd.similarity_search(pregunta, k=k)
