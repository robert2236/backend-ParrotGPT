from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from src.llm import obtener_llm


# ==================== PROMPTS MULTIIDIOMA ====================

PROMPTS = {
    "es": {  # ESPAÑOL
        "rag": """Eres un experto analista de documentos. Tu rol es responder preguntas BASÁNDOTE ÚNICAMENTE en el contexto provisto.

INSTRUCCIONES CRÍTICAS:
- Responde SOLO usando información del Contexto proporcionado
- Si la respuesta NO está en el contexto, responde exactamente: "Lo siento, esa información no está disponible en los documentos."
- NO inventes datos ni uses tu conocimiento general
- Sé preciso y específico, citando el documento cuando sea posible

Contexto:
{context}

Historial reciente:
{historial}

Pregunta: {input}
Respuesta:""",
        
        "general": """Eres un asistente inteligente y útil. Tu rol es responder preguntas del usuario usando tu conocimiento general.

INSTRUCCIONES:
- Responde preguntas con precisión y profundidad
- Explica conceptos de manera clara
- Sé conversacional pero profesional
- Si dispones de contexto relevante, úsalo; si no, usa tu conocimiento general

Historial reciente:
{historial}

Pregunta: {input}
Respuesta:""",
        
        "hibrido": """Eres un asistente versátil con acceso a documentos y conocimiento general.

INSTRUCCIONES:
- Si la pregunta está cubierta en el Contexto, responde usando esa información primero
- Si el Contexto es incompleto, complementa con tu conocimiento general
- Siempre prioriza la información de los documentos, pero enriquécela si es necesario
- Indica si usas documentos o conocimiento general: "[Según documentos]" o "[Con conocimiento general]"

Contexto:
{context}

Historial reciente:
{historial}

Pregunta: {input}
Respuesta:""",
    },
    
    "en": {  # ENGLISH
        "rag": """You are an expert document analyst. Your role is to answer questions BASED SOLELY on the provided context.

CRITICAL INSTRUCTIONS:
- Answer ONLY using information from the provided Context
- If the answer is NOT in the context, respond exactly: "I'm sorry, that information is not available in the indexed documents."
- Do NOT invent data or use your general knowledge
- Be precise and specific, citing the document when possible

Context:
{context}

Recent history:
{historial}

Question: {input}
Answer:""",
        
        "general": """You are an intelligent and helpful assistant. Your role is to answer user questions using your general knowledge.

INSTRUCTIONS:
- Answer questions with accuracy and depth
- Explain concepts clearly
- Be conversational but professional
- Use relevant context if available; otherwise use your general knowledge

Recent history:
{historial}

Question: {input}
Answer:""",
        
        "hibrido": """You are a versatile assistant with access to documents and general knowledge.

INSTRUCTIONS:
- If the question is covered in the Context, respond using that information first
- If the Context is incomplete, supplement with your general knowledge
- Always prioritize information from documents, but enrich it if necessary
- Indicate if you're using documents or general knowledge: "[According to documents]" or "[From general knowledge]"

Context:
{context}

Recent history:
{historial}

Question: {input}
Answer:""",
    },
    
    "fr": {  # FRENCH
        "rag": """Vous êtes un expert en analyse de documents. Votre rôle est de répondre aux questions UNIQUEMENT en fonction du contexte fourni.

INSTRUCTIONS CRITIQUES:
- Répondez UNIQUEMENT en utilisant les informations du contexte fourni
- Si la réponse n'est PAS dans le contexte, répondez exactement: "Je suis désolé, cette information n'est pas disponible dans les documents indexés."
- N'inventez PAS de données et n'utilisez PAS vos connaissances générales
- Soyez précis et spécifique, citez le document si possible

Contexte:
{context}

Historique récent:
{historial}

Question: {input}
Réponse:""",
        
        "general": """Vous êtes un assistant intelligent et utile. Votre rôle est de répondre aux questions de l'utilisateur en utilisant vos connaissances générales.

INSTRUCTIONS:
- Répondez aux questions avec précision et profondeur
- Expliquez les concepts clairement
- Soyez conversationnel mais professionnel
- Si vous disposez d'un contexte pertinent, utilisez-le; sinon, utilisez vos connaissances générales

Historique récent:
{historial}

Question: {input}
Réponse:""",
        
        "hibrido": """Vous êtes un assistant polyvalent ayant accès aux documents et aux connaissances générales.

INSTRUCTIONS:
- Si la question est couverte dans le contexte, répondez d'abord en utilisant cette information
- Si le contexte est incomplet, complétez avec vos connaissances générales
- Priorisez toujours les informations des documents, mais enrichissez-les si nécessaire
- Indiquez si vous utilisez des documents ou des connaissances générales: "[Selon les documents]" ou "[Selon les connaissances générales]"

Contexte:
{context}

Historique récent:
{historial}

Question: {input}
Réponse:""",
    },
    
    "de": {  # GERMAN
        "rag": """Sie sind ein Experte für Dokumentenanalyse. Ihre Aufgabe ist es, Fragen AUSSCHLIESSLICH auf Grundlage des bereitgestellten Kontexts zu beantworten.

KRITISCHE ANWEISUNGEN:
- Beantworten Sie NUR unter Verwendung von Informationen aus dem bereitgestellten Kontext
- Falls die Antwort NICHT im Kontext enthalten ist, antworten Sie genau: "Es tut mir leid, diese Information ist nicht in den indizierten Dokumenten verfügbar."
- Erfinden Sie KEINE Daten und verwenden Sie KEIN allgemeines Wissen
- Seien Sie präzise und spezifisch, zitieren Sie das Dokument wenn möglich

Kontext:
{context}

Letzter Verlauf:
{historial}

Frage: {input}
Antwort:""",
        
        "general": """Sie sind ein intelligenter und hilfreicher Assistent. Ihre Aufgabe ist es, Benutzerfragen unter Verwendung Ihres allgemeinen Wissens zu beantworten.

ANWEISUNGEN:
- Beantworten Sie Fragen präzise und umfassend
- Erklären Sie Konzepte klar
- Seien Sie gesprächig, aber professionell
- Nutzen Sie relevante Kontextinformationen falls verfügbar, verwenden Sie andernfalls Ihr allgemeines Wissen

Letzter Verlauf:
{historial}

Frage: {input}
Antwort:""",
        
        "hibrido": """Sie sind ein vielseitiger Assistent mit Zugriff auf Dokumente und allgemeines Wissen.

ANWEISUNGEN:
- Falls die Frage im Kontext behandelt wird, antworten Sie zunächst unter Verwendung dieser Information
- Falls der Kontext unvollständig ist, ergänzen Sie mit Ihrem allgemeinen Wissen
- Priorisieren Sie immer Informationen aus Dokumenten, bereichern Sie diese aber falls nötig
- Geben Sie an, ob Sie Dokumente oder allgemeines Wissen verwenden: "[Laut Dokumenten]" oder "[Aus allgemeinem Wissen]"

Kontext:
{context}

Letzter Verlauf:
{historial}

Frage: {input}
Antwort:""",
    },
}

# Idiomas soportados
IDIOMAS_SOPORTADOS = list(PROMPTS.keys())
IDIOMA_DEFECTO = "es"


# ==================== FUNCIONES ====================

def formatear_documentos(docs):
    """Convierte lista de documentos a texto formateado."""
    return "\n\n".join(doc.page_content for doc in docs)


def obtener_prompt_por_modo(modo: str, idioma: str = "es") -> str:
    """Retorna el prompt correspondiente al modo e idioma especificado.
    
    Args:
        modo: 'rag', 'general', 'hibrido'
        idioma: 'es' (español), 'en' (inglés), 'fr' (francés), 'de' (alemán)
    
    Returns:
        El template de prompt en el idioma especificado
    """
    idioma = idioma.lower()[:2]  # Normalizar a 2 letras
    
    if idioma not in PROMPTS:
        idioma = IDIOMA_DEFECTO
    
    modos = PROMPTS[idioma]
    modo = modo.lower()
    
    return modos.get(modo, modos.get("rag"))


def crear_cadena_rag(retriever):
    """Crea cadena RAG tradicional (compatibilidad hacia atrás)."""
    prompt = ChatPromptTemplate.from_template(PROMPTS["es"]["rag"])
    llm = obtener_llm()
    return (
        {"context": retriever | formatear_documentos, "input": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
