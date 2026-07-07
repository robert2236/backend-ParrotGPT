from src.vector_store import obtener_retriever
from src.rag import crear_cadena_rag, formatear_documentos
from src.llm import obtener_llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


def main():
    retriever = obtener_retriever(k=2)
    llm = obtener_llm()

    prompt = ChatPromptTemplate.from_template(
        "Contexto:\n{context}\n\nPregunta:\n{input}\n\nRespuesta:"
    )
    cadena = (
        {"context": retriever | formatear_documentos, "input": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    print("Chat RAG (escribe 'salir' para terminar)")
    while True:
        pregunta = input("\nTu: ")
        if pregunta.lower().strip() == "salir":
            break
        respuesta = cadena.invoke(pregunta)
        print(f"Asistente: {respuesta}")


if __name__ == "__main__":
    main()
