import streamlit as st
import tempfile
import os
from langchain_chroma import Chroma
from langchain_ollama import OllamaLLM

from src.config import LLM_MODELO, RUTA_BD_VECTORIAL, RETRIEVER_K
from src.embeddings import obtener_modelo
from src.loader import cargar_pdf
from src.splitter import fragmentar

st.set_page_config(page_title="ParrotGPT", page_icon="", layout="centered")

TAMANO_MAXIMO_MB = 50
TAMANO_MAXIMO_BYTES = TAMANO_MAXIMO_MB * 1024 * 1024


@st.cache_resource
def iniciar_asistente():
    modelo_emb = obtener_modelo()
    bd = Chroma(persist_directory=RUTA_BD_VECTORIAL, embedding_function=modelo_emb)
    buscador = bd.as_retriever(search_kwargs={"k": RETRIEVER_K})
    llm = OllamaLLM(model=LLM_MODELO)
    return buscador, llm


def procesar_pdf(archivo):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
        f.write(archivo.read())
        ruta = f.name

    progreso = st.progress(0, text="Extrayendo texto del PDF...")
    documentos = cargar_pdf(ruta)
    progreso.progress(30, text="Fragmentando documento...")
    fragmentos = fragmentar(documentos)
    progreso.progress(50, text=f"Generando embeddings ({len(fragmentos)} fragmentos)...")
    modelo_emb = obtener_modelo()
    bd = Chroma.from_documents(fragmentos, modelo_emb)
    progreso.progress(100, text="¡PDF listo!")
    os.remove(ruta)
    return bd.as_retriever(search_kwargs={"k": RETRIEVER_K})


tab1, tab2 = st.tabs([" Asistente del Laboratorio", " Lector Universal"])

with tab1:
    st.title("Asistente del Laboratorio")
    st.markdown("Conozco el reglamento del laboratorio a la perfección.")

    buscador, llm = iniciar_asistente()

    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []

    for msg in st.session_state.mensajes:
        with st.chat_message(msg["rol"]):
            st.markdown(msg["contenido"])

    pregunta = st.chat_input("Escribe tu pregunta sobre el laboratorio...")
    if pregunta:
        with st.chat_message("user"):
            st.markdown(pregunta)
        st.session_state.mensajes.append({"rol": "user", "contenido": pregunta})

        historial = "\n".join(
            f"{m['rol']}: {m['contenido']}"
            for m in st.session_state.mensajes[-4:]
        )
        docs = buscador.invoke(pregunta)
        contexto = "\n\n".join(d.page_content for d in docs)

        plantilla = f"""Eres el Asistente Oficial del Laboratorio de IA de la Universidad.
Responde amablemente basándote ÚNICAMENTE en este Contexto:
{contexto}

Si la respuesta no está en el Contexto, di: "Lo siento, no tengo esa información".

Historial reciente:
{historial}

Pregunta: {pregunta}
Respuesta:"""

        with st.chat_message("assistant"):
            with st.spinner("Pensando..."):
                respuesta = llm.invoke(plantilla)
                st.markdown(respuesta)
        st.session_state.mensajes.append({"rol": "assistant", "contenido": respuesta})

with tab2:
    st.title("Lector Universal")
    st.markdown("Subí un PDF y hacele preguntas.")

    archivo = st.file_uploader("Seleccioná un PDF", type="pdf")

    if archivo is None:
        st.info("Subí un PDF para comenzar.")
        st.session_state.mensajes_pdf = []
        st.session_state.pop("pdf_retriever", None)
        st.session_state.pop("pdf_nombre", None)
    else:
        if archivo.size and archivo.size > TAMANO_MAXIMO_BYTES:
            st.error(
                f"El archivo es demasiado grande "
                f"({archivo.size / 1024 / 1024:.1f} MB). "
                f"Máximo: {TAMANO_MAXIMO_MB} MB."
            )
            st.stop()

        if "pdf_nombre" not in st.session_state or st.session_state.pdf_nombre != archivo.name:
            buscador_pdf = procesar_pdf(archivo)
            st.session_state.pdf_retriever = buscador_pdf
            st.session_state.pdf_nombre = archivo.name
        else:
            buscador_pdf = st.session_state.pdf_retriever

        llm_pdf = OllamaLLM(model=LLM_MODELO)
        st.success(f"Documento '{archivo.name}' listo.")

        if "mensajes_pdf" not in st.session_state:
            st.session_state.mensajes_pdf = []

        for msg in st.session_state.mensajes_pdf:
            with st.chat_message(msg["rol"]):
                st.markdown(msg["contenido"])

        pregunta = st.chat_input("Preguntá sobre el documento...")
        if pregunta:
            st.session_state.mensajes_pdf.append({"rol": "user", "contenido": pregunta})
            with st.chat_message("user"):
                st.markdown(pregunta)

            historial = "\n".join(
                f"{m['rol']}: {m['contenido']}"
                for m in st.session_state.mensajes_pdf[-4:]
            )
            docs = buscador_pdf.invoke(pregunta)
            contexto = "\n\n".join(d.page_content for d in docs)

            plantilla = f"""Eres un experto analista de documentos.
Responde basándote ÚNICAMENTE en el Contexto provisto.
Solo decí "No tengo esa información" si el tema no se menciona en el documento.

Contexto: {contexto}
Historial: {historial}
Pregunta: {pregunta}
Respuesta:"""

            with st.chat_message("assistant"):
                with st.spinner("Analizando..."):
                    respuesta = llm_pdf.invoke(plantilla)
                    st.markdown(respuesta)
            st.session_state.mensajes_pdf.append({"rol": "assistant", "contenido": respuesta})
