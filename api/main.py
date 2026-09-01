import asyncio
import os
import tempfile
import uuid
import shutil
import psutil
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, File, Form, HTTPException, UploadFile, Depends
from fastapi.middleware.cors import CORSMiddleware

from api.database import (
    actualizar_nota,
    actualizar_titulo_sesion,
    add_message,
    buscar_sesiones,
    clear_history,
    crear_carpeta,
    crear_nota,
    crear_o_actualizar_sesion,
    eliminar_carpeta,
    eliminar_nota,
    eliminar_sesion,
    get_history,
    get_preference,
    guardar_estadistica_tokens,
    init_db,
    listar_carpetas,
    listar_notas,
    obtener_estadisticas_tokens,
    obtener_nota,
    set_preference,
    toggle_pin_sesion,
)
from api.schemas import (
    ActualizarNotaBody,
    AskRequest,
    AskResponse,
    BuscarRequest,
    BuscarResponse,
    CarpetaBody,
    CarpetaResponse,
    ChatRequest,
    ChatResponse,
    CrearNotaBody,
    EstadísticasResponse,
    HistorialResponse,
    HistorialItem,
    NotaResponse,
    UpdateSessionBody,
)
from api.auth import get_current_user_id
from src.config import RETRIEVER_K
from src.embeddings import obtener_modelo
from src.llm import obtener_llm
from src.loader import cargar_pdf
from src.rag import formatear_documentos, obtener_prompt_por_modo
from src.splitter import fragmentar
from src.vector_store import agregar_documentos
from src.vector_store import buscar as buscar_vectorial
from src.vector_store import obtener_retriever

app = FastAPI(title="API RAG ParrotGPT")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TAMANO_MAXIMO_MB = 50
TAMANO_MAXIMO_BYTES = TAMANO_MAXIMO_MB * 1024 * 1024

_ejecutor = ThreadPoolExecutor(max_workers=2)


def _procesar_pdf_sync(ruta: str, sid: str, user_id: str) -> tuple[list, list]:
    docs = cargar_pdf(ruta)
    fragmentos = fragmentar(docs)
    for frag in fragmentos:
        frag.metadata["session_id"] = sid
        frag.metadata["user_id"] = user_id
    agregar_documentos(fragmentos)
    return docs, fragmentos


@app.on_event("startup")
def startup():
    init_db()

@app.get("/api/system-status")
def system_status():
    # 1. Uso de Memoria RAM
    memory_info = psutil.virtual_memory()
    
    # 2. Uso de Disco
    disk_info = shutil.disk_usage("/")
    
    # 3. Datos del Proceso Actual
    process = psutil.Process(os.getpid())
    process_ram_mb = process.memory_info().rss / (1024 * 1024)

    return {
        "ram": {
            "proceso_actual_mb": round(process_ram_mb, 2),
            "ram_total_mb": round(memory_info.total / (1024 * 1024), 2),
            "ram_usada_mb": round(memory_info.used / (1024 * 1024), 2),
            "porcentaje_ram_sistema": memory_info.percent
        },
        "disco": {
            "total_gb": round(disk_info.total / (1024**3), 2),
            "usado_gb": round(disk_info.used / (1024**3), 2),
            "libre_gb": round(disk_info.free / (1024**3), 2)
        }
    }


@app.get("/api/health")
def health():
    llm = obtener_llm()
    embeddings_model = obtener_modelo()
    return {
        "status": "ok",
        "modelo_llm": llm.model_name, # Asumiendo que el objeto LLM tiene un atributo 'model_name'
        "embeddings": embeddings_model.model_name, # Asumiendo que el objeto Embeddings tiene un atributo 'model_name'
    }


@app.post("/api/ask", response_model=AskResponse)
def ask(req: AskRequest, user_id: str = Depends(get_current_user_id)):
    from src.vector_store import cargar_bd
    bd = cargar_bd()
    try:
        hay_docs = bd._collection.count() > 0
    except Exception:
        hay_docs = False

    if not hay_docs:
        return AskResponse(
            respuesta="No hay documentos indexados. Primero debes subir un PDF usando POST /api/upload.",
            fuentes=[],
        )

    filtro = {"$and": [{"session_id": req.session_id}, {"user_id": user_id}]}
    retriever = obtener_retriever(k=RETRIEVER_K, filtro=filtro)
    docs = retriever.invoke(req.pregunta)

    contexto = formatear_documentos(docs)

    if not contexto.strip():
        return AskResponse(
            respuesta="Lo siento, la información solicitada no está disponible en los documentos indexados.",
            fuentes=[],
        )

    history = get_history(req.session_id, limit=10, user_id=user_id)
    historial_texto = "\n".join(f"{m.rol}: {m.contenido}" for m in history)

    prompt = f"""Eres un experto analista de documentos.
Responde basándote ÚNICAMENTE en el Contexto provisto.
Si tenés la información total o general sobre lo que se pregunta, brindala.
Solo decí "No tengo esa información" si el tema no se menciona en lo absoluto en el documento.

Contexto:
{contexto}

Historial reciente:
{historial_texto}

Pregunta: {req.pregunta}
Respuesta:"""

    llm = obtener_llm()
    try:
        respuesta = llm.invoke(prompt)
    except ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="El servicio de IA (Ollama) no está disponible. Verifica que el servidor esté corriendo.",
        )

    add_message(req.session_id, "user", req.pregunta, user_id=user_id)
    add_message(req.session_id, "assistant", respuesta, user_id=user_id)
    crear_o_actualizar_sesion(req.session_id, req.pregunta, user_id=user_id)

    fuentes = [{"contenido": d.page_content, "metadata": d.metadata} for d in docs]
    return AskResponse(respuesta=respuesta, fuentes=fuentes)


@app.post("/api/chat", response_model=ChatResponse)
def chat_mejorado(req: ChatRequest, user_id: str = Depends(get_current_user_id)):
    """
    Endpoint mejorado de chat con soporte para múltiples modos e idiomas.
    
    Modos disponibles:
    - 'rag': Solo usa documentos indexados (modo estricto)
    - 'general': Usa conocimiento general (sin documentos)
    - 'hibrido': Combina documentos + conocimiento general
    
    Idiomas soportados:
    - 'es': Español
    - 'en': Inglés
    - 'fr': Francés
    - 'de': Alemán
    """
    modo = req.modo.lower()
    idioma = req.idioma.lower()[:2]  # Normalizar a 2 letras
    
    if modo not in ["rag", "general", "hibrido"]:
        raise HTTPException(400, "Modo no válido. Use: 'rag', 'general' o 'hibrido'")
    
    if idioma not in ["es", "en", "fr", "de"]:
        raise HTTPException(400, "Idioma no soportado. Use: 'es', 'en', 'fr' o 'de'")

    # ========== VALIDACIÓN DE DOCUMENTOS ==========
    docs_disponibles = False
    contexto = ""
    docs = []
    
    if modo in ["rag", "hibrido"]:
        from src.vector_store import cargar_bd
        try:
            bd = cargar_bd()
            hay_docs = bd._collection.count() > 0
            docs_disponibles = hay_docs
        except Exception:
            docs_disponibles = False

        if modo == "rag" and not docs_disponibles:
            mensajes_error = {
                "es": "❌ No hay documentos indexados. Modo 'rag' requiere documentos. Sube un PDF primero.",
                "en": "❌ No indexed documents. RAG mode requires documents. Upload a PDF first.",
                "fr": "❌ Aucun document indexé. Le mode RAG nécessite des documents. Veuillez d'abord télécharger un PDF.",
                "de": "❌ Keine indizierten Dokumente. RAG-Modus erfordert Dokumente. Bitte laden Sie zuerst eine PDF-Datei hoch.",
            }
            return ChatResponse(
                respuesta=mensajes_error.get(idioma, mensajes_error["es"]),
                modo_usado="rag",
                fuentes=[],
            )

        # ========== RECUPERACIÓN DE CONTEXTO ==========
        if docs_disponibles:
            filtro = {"$and": [{"session_id": req.session_id}, {"user_id": user_id}]}
            retriever = obtener_retriever(k=RETRIEVER_K, filtro=filtro)
            docs = retriever.invoke(req.pregunta)
            contexto = formatear_documentos(docs)

    # ========== OBTENCIÓN DEL PROMPT DINÁMICO ==========
    template_prompt = obtener_prompt_por_modo(modo, idioma)
    
    # ========== CONSTRUCCIÓN DE HISTORIAL ==========
    history = get_history(req.session_id, limit=10, user_id=user_id)
    historial_texto = "\n".join(f"{m.rol}: {m.contenido}" for m in history)

    # ========== CONSTRUCCIÓN DEL PROMPT FINAL ==========
    if modo == "general":
        # Para modo general, no incluir contexto de documentos
        prompt_final = template_prompt.format(
            historial=historial_texto,
            input=req.pregunta,
        )
    else:
        # Para rag e híbrido, incluir contexto
        prompt_final = template_prompt.format(
            context=contexto if contexto else "[No relevant documents found]" if idioma == "en" else "[Ningún documento relevante encontrado]",
            historial=historial_texto,
            input=req.pregunta,
        )

    # ========== GENERACIÓN DE RESPUESTA ==========
    llm = obtener_llm()
    try:
        respuesta = llm.invoke(prompt_final)
    except ConnectionError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Servicio de IA no disponible: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generando respuesta: {str(e)}",
        )

    # ========== OBTENER ESTADÍSTICAS DE TOKENS ==========
    tokens_usados = llm.obtener_ultimo_usage()
    if not tokens_usados["entrada"] and not tokens_usados["salida"]:
        # Fallback si Gemini no retorna tokens (usar conteo aproximado)
        tokens_usados = {
            "entrada": len(req.pregunta.split()),
            "salida": len(respuesta.split()),
        }

    # ========== GUARDAR EN HISTORIAL ==========
    add_message(req.session_id, "user", req.pregunta, user_id=user_id)
    add_message(req.session_id, "assistant", respuesta, user_id=user_id)
    crear_o_actualizar_sesion(req.session_id, req.pregunta, user_id=user_id)

    # ========== GUARDAR ESTADÍSTICAS DE TOKENS ==========
    try:
        guardar_estadistica_tokens(
            user_id=user_id,
            session_id=req.session_id,
            tokens_entrada=tokens_usados.get("entrada", 0),
            tokens_salida=tokens_usados.get("salida", 0),
            modo=modo,
            idioma=idioma,
        )
    except Exception as e:
        print(f"⚠️ Error al guardar estadísticas de tokens: {e}")

    # ========== PREPARAR FUENTES ==========
    fuentes = []
    if req.incluir_fuentes and docs_disponibles and modo in ["rag", "hibrido"]:
        try:
            fuentes = [{"contenido": d.page_content, "metadata": d.metadata} for d in docs]
        except Exception:
            pass

    return ChatResponse(
        respuesta=respuesta,
        modo_usado=modo,
        fuentes=fuentes,
        tokens_usados=tokens_usados,
    )


@app.get("/api/stats", response_model=EstadísticasResponse)
def obtener_stats(user_id: str | None = None):
    """
    Endpoint para obtener estadísticas de tokens consumidos.
    
    Parámetros:
    - user_id (opcional): Si se proporciona, retorna estadísticas solo de ese usuario.
    
    Retorna:
    - total_tokens_entrada: Total de tokens de entrada
    - total_tokens_salida: Total de tokens de salida
    - total_tokens: Total combinado
    - costo_estimado: Costo aproximado en USD (Gemini 2.5 Flash pricing)
    - total_requests: Total de requests realizados
    - requests_por_modo: Desglose por modo (rag, general, hibrido)
    - requests_por_idioma: Desglose por idioma (es, en, fr, de)
    - tokens_promedio_por_request: Promedio de tokens totales
    - tokens_entrada_promedio: Promedio de tokens entrada
    - tokens_salida_promedio: Promedio de tokens salida
    """
    stats = obtener_estadisticas_tokens(user_id=user_id)
    return EstadísticasResponse(**stats)


@app.post("/api/buscar", response_model=BuscarResponse)
def buscar(req: BuscarRequest, user_id: str = Depends(get_current_user_id)):
    docs = buscar_vectorial(req.pregunta, k=req.k, user_id=user_id)
    resultados = [{"contenido": d.page_content, "metadata": d.metadata} for d in docs]
    return BuscarResponse(resultados=resultados)


@app.post("/api/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    pregunta: str = Form(""),
    session_id: str = Form(""),
    user_id: str = Depends(get_current_user_id),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Solo se aceptan archivos PDF (extensión .pdf)")

    sid = session_id or user_id

    content = await file.read()
    if len(content) > TAMANO_MAXIMO_BYTES:
        raise HTTPException(
            413,
            f"Archivo demasiado grande ({len(content) / 1024 / 1024:.1f} MB). "
            f"Máximo: {TAMANO_MAXIMO_MB} MB.",
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
        f.write(content)
        ruta = f.name

    try:
        loop = asyncio.get_event_loop()
        docs, fragmentos = await loop.run_in_executor(
            _ejecutor, _procesar_pdf_sync, ruta, sid, user_id
        )
    except Exception as e:
        try:
            os.remove(ruta)
        except Exception:
            pass
        raise HTTPException(500, f"Error al procesar el PDF: {e}")

    try:
        os.remove(ruta)
    except Exception:
        pass

    preview = fragmentos[0].page_content[:200] if fragmentos else ""
    respuesta = ""

    if pregunta:
        filtro = {"$and": [{"session_id": sid}, {"user_id": user_id}]}
        retriever = obtener_retriever(k=RETRIEVER_K, filtro=filtro)
        docs_resp = retriever.invoke(pregunta)
        contexto = formatear_documentos(docs_resp)

        if not contexto.strip():
            respuesta = "Lo siento, la información solicitada no está disponible en los documentos indexados."
        else:
            prompt = f"""Eres un experto analista de documentos.
Responde basándote ÚNICAMENTE en el Contexto provisto.
Si tenés la información total o general sobre lo que se pregunta, brindala.
Solo decí "No tengo esa información" si el tema no se menciona en lo absoluto en el documento.

Contexto: {contexto}

Pregunta: {pregunta}
Respuesta:"""
            try:
                llm = obtener_llm()
                respuesta = llm.invoke(prompt)
            except ConnectionError:
                raise HTTPException(
                    status_code=503,
                    detail="El servicio de IA (Ollama) no está disponible. Verifica que el servidor esté corriendo.",
                )

        add_message(sid, "user", pregunta, user_id=user_id)
        add_message(sid, "assistant", respuesta, user_id=user_id)
        crear_o_actualizar_sesion(sid, pregunta, user_id=user_id)

    return {
        "respuesta": respuesta,
        "session_id": sid,
        "nombre_archivo": file.filename,
        "paginas": len(docs),
        "fragmentos": len(fragmentos),
        "preview": preview,
    }


@app.get("/api/upload/{session_id}")
def estado_upload(session_id: str, user_id: str = Depends(get_current_user_id)):
    from src.vector_store import cargar_bd
    bd = cargar_bd()
    resultados = bd.get(
        where={"$and": [{"session_id": session_id}, {"user_id": user_id}]}
    )
    disponible = len(resultados.get("ids", [])) > 0
    nombre_archivo = None
    paginas = None
    fragmentos = None
    if disponible:
        metadatas = resultados.get("metadatas", [])
        if metadatas:
            nombre_archivo = metadatas[0].get("source", "documento.pdf")
            fragmentos = len(metadatas)
            paginas_unicas = set()
            for m in metadatas:
                page = m.get("page")
                if page is not None:
                    paginas_unicas.add(page)
            paginas = len(paginas_unicas)
    return {
        "disponible": disponible,
        "nombre_archivo": nombre_archivo,
        "paginas": paginas,
        "fragmentos": fragmentos,
    }


@app.get("/test/api/upload/{session_id}")
def estado_upload_test(session_id: str):
    from src.vector_store import cargar_bd
    bd = cargar_bd()
    resultados = bd.get(where={"session_id": session_id})
    disponible = len(resultados.get("ids", [])) > 0
    nombre_archivo = None
    paginas = None
    fragmentos = None
    if disponible:
        metadatas = resultados.get("metadatas", [])
        if metadatas:
            nombre_archivo = metadatas[0].get("source", "documento.pdf")
            fragmentos = len(metadatas)
            paginas_unicas = set()
            for m in metadatas:
                page = m.get("page")
                if page is not None:
                    paginas_unicas.add(page)
            paginas = len(paginas_unicas)
    return {
        "disponible": disponible,
        "nombre_archivo": nombre_archivo,
        "paginas": paginas,
        "fragmentos": fragmentos,
    }


# --- SESIONES Y HISTORIAL ---

@app.get("/api/sessions")
def listar_sesiones(q: str = "", user_id: str = Depends(get_current_user_id)):
    sesiones = buscar_sesiones(query=q, user_id=user_id)
    return [
        {
            "session_id": s.session_id,
            "titulo": s.titulo,
            "pinned": s.pinned,
            "creado_en": str(s.creado_en),
            "actualizado_en": str(s.actualizado_en),
        }
        for s in sesiones
    ]


@app.delete("/api/sessions/{session_id}", status_code=204)
def borrar_sesion(session_id: str, user_id: str = Depends(get_current_user_id)):
    eliminar_sesion(session_id, user_id=user_id)


@app.patch("/api/sessions/{session_id}")
def editar_sesion(session_id: str, body: UpdateSessionBody, user_id: str = Depends(get_current_user_id)):
    if body.titulo:
        actualizar_titulo_sesion(session_id, body.titulo, user_id=user_id)
    return {"mensaje": "Actualizado"}


@app.patch("/api/sessions/{session_id}/pin")
def pin_sesion(session_id: str, user_id: str = Depends(get_current_user_id)):
    pinned = toggle_pin_sesion(session_id, user_id=user_id)
    return {"pinned": pinned}


@app.get("/api/historial/{session_id}", response_model=HistorialResponse)
def obtener_historial(session_id: str, user_id: str = Depends(get_current_user_id)):
    mensajes = get_history(session_id, user_id=user_id)
    items = [
        HistorialItem(rol=m.rol, contenido=m.contenido, creado_en=str(m.creado_en))
        for m in mensajes
    ]
    return HistorialResponse(session_id=session_id, mensajes=items)


@app.delete("/api/historial/{session_id}")
def eliminar_historial(session_id: str, user_id: str = Depends(get_current_user_id)):
    clear_history(session_id, user_id=user_id)
    return {"mensaje": f"Historial de '{session_id}' eliminado"}


# --- PREFERENCIAS ---

@app.get("/api/theme")
def obtener_tema():
    theme = get_preference("theme")
    return {"theme": theme or "default"}


@app.put("/api/theme")
def guardar_tema(body: dict):
    theme = body.get("theme", "default")
    set_preference("theme", theme)
    return {"theme": theme}


# --- CARPETAS ---

@app.get("/api/carpetas", response_model=list[CarpetaResponse])
def obtener_carpetas(user_id: str = Depends(get_current_user_id)):
    return [
        CarpetaResponse(id=c.id, nombre=c.nombre, creado_en=str(c.creado_en))
        for c in listar_carpetas()
    ]


@app.post("/api/carpetas", response_model=CarpetaResponse)
def nueva_carpeta(body: CarpetaBody, user_id: str = Depends(get_current_user_id)):
    c = crear_carpeta(body.nombre)
    return CarpetaResponse(id=c.id, nombre=c.nombre, creado_en=str(c.creado_en))


@app.delete("/api/carpetas/{carpeta_id}", status_code=204)
def borrar_carpeta(carpeta_id: int, user_id: str = Depends(get_current_user_id)):
    eliminar_carpeta(carpeta_id)


# --- NOTAS ---

@app.get("/api/notas", response_model=list[NotaResponse])
def obtener_notas(carpeta_id: int | None = None, q: str = "", user_id: str = Depends(get_current_user_id)):
    return [
        NotaResponse(
            id=n.id, session_id=n.session_id, carpeta_id=n.carpeta_id,
            titulo=n.titulo, contenido=n.contenido,
            creado_en=str(n.creado_en), actualizado_en=str(n.actualizado_en),
        )
        for n in listar_notas(carpeta_id=carpeta_id, query=q, user_id=user_id)
    ]


@app.post("/api/notas", response_model=NotaResponse)
def nueva_nota(body: CrearNotaBody, user_id: str = Depends(get_current_user_id)):
    n = crear_nota(
        titulo=body.titulo, 
        contenido=body.contenido, 
        session_id=body.session_id, 
        carpeta_id=body.carpeta_id,
        user_id=user_id  # <--- Asocia la nota creada al usuario autenticado
    )
    return NotaResponse(
        id=n.id, session_id=n.session_id, carpeta_id=n.carpeta_id,
        titulo=n.titulo, contenido=n.contenido,
        creado_en=str(n.creado_en), actualizado_en=str(n.actualizado_en),
    )


@app.get("/api/notas/{nota_id}", response_model=NotaResponse)
def obtener_nota_endpoint(nota_id: int, user_id: str = Depends(get_current_user_id)):
    n = obtener_nota(nota_id, user_id=user_id)
    if not n:
        raise HTTPException(404, "Nota no encontrada")
    return NotaResponse(
        id=n.id, session_id=n.session_id, carpeta_id=n.carpeta_id,
        titulo=n.titulo, contenido=n.contenido,
        creado_en=str(n.creado_en), actualizado_en=str(n.actualizado_en),
    )


@app.put("/api/notas/{nota_id}", response_model=NotaResponse)
def editar_nota(nota_id: int, body: ActualizarNotaBody, user_id: str = Depends(get_current_user_id)):
    n = actualizar_nota(nota_id, titulo=body.titulo, contenido=body.contenido, user_id=user_id)
    if not n:
        raise HTTPException(404, "Nota no encontrada")
    return NotaResponse(
        id=n.id, session_id=n.session_id, carpeta_id=n.carpeta_id,
        titulo=n.titulo, contenido=n.contenido,
        creado_en=str(n.creado_en), actualizado_en=str(n.actualizado_en),
    )


@app.delete("/api/notas/{nota_id}", status_code=204)
def borrar_nota(nota_id: int, user_id: str = Depends(get_current_user_id)):
    eliminar_nota(nota_id, user_id=user_id)