from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from src.llm import obtener_llm


PLANTILLA_RAG = """Eres un asistente de IA estrictamente limitado al contexto provisto.
Si la respuesta a la pregunta del usuario no se puede deducir de manera directa y evidente
a partir de los fragmentos de texto proporcionados a continuación, debes responder exactamente:
'Lo siento, la información solicitada no está disponible en los documentos indexados.'
No utilices tu conocimiento general bajo ninguna circunstancia. No inventes datos.

Contexto:
{context}

Historial reciente:
{historial}

Pregunta: {input}
Respuesta:"""


def formatear_documentos(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def crear_cadena_rag(retriever):
    prompt = ChatPromptTemplate.from_template(PLANTILLA_RAG)
    llm = obtener_llm()
    return (
        {"context": retriever | formatear_documentos, "input": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
