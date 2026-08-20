import asyncio
import os
import tempfile
import uuid
import shutil
import psutil
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
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
    init_db,
    listar_carpetas,
    listar_notas,
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
    CrearNotaBody,
    HistorialResponse,
    HistorialItem,
    NotaResponse,
    UpdateSessionBody,
)
from src.config import RETRIEVER_K
from src.embeddings import obtener_modelo
from src.llm import obtener_llm
from src.loader import cargar_pdf
from src.rag import formatear_documentos
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


def _procesar_pdf_sync(ruta: str, sid: str) -> tuple[list, list]:
    docs = cargar_pdf(ruta)
    fragmentos = fragmentar(docs)
    for frag in fragmentos:
        frag.metadata["session_id"] = sid
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
    return {
        "status": "ok",
        "modelo_llm": "llama3.2",
        "embeddings": "paraphrase-multilingual-MiniLM-L12-v2",
    }


@app.post("/api/ask", response_model=AskResponse)
def ask(req: AskRequest):
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

    retriever = obtener_retriever(k=RETRIEVER_K, filtro={"session_id": req.session_id})
    docs = retriever.invoke(req.pregunta)

    contexto = formatear_documentos(docs)

    if not contexto.strip():
        return AskResponse(
            respuesta="Lo siento, la información solicitada no está disponible en los documentos indexados.",
            fuentes=[],
        )

    history = get_history(req.session_id, limit=10)
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

    add_message(req.session_id, "user", req.pregunta)
    add_message(req.session_id, "assistant", respuesta)
    crear_o_actualizar_sesion(req.session_id, req.pregunta)

    fuentes = [{"contenido": d.page_content, "metadata": d.metadata} for d in docs]
    return AskResponse(respuesta=respuesta, fuentes=fuentes)


@app.post("/api/buscar", response_model=BuscarResponse)
def buscar(req: BuscarRequest):
    docs = buscar_vectorial(req.pregunta, k=req.k)
    resultados = [{"contenido": d.page_content, "metadata": d.metadata} for d in docs]
    return BuscarResponse(resultados=resultados)


@app.post("/api/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    pregunta: str = Form(""),
    session_id: str = Form(""),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Solo se aceptan archivos PDF (extensión .pdf)")

    sid = session_id or str(uuid.uuid4())

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
            _ejecutor, _procesar_pdf_sync, ruta, sid
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
        retriever = obtener_retriever(k=RETRIEVER_K, filtro={"session_id": sid})
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

        add_message(sid, "user", pregunta)
        add_message(sid, "assistant", respuesta)
        crear_o_actualizar_sesion(sid, pregunta)

    return {
        "respuesta": respuesta,
        "session_id": sid,
        "nombre_archivo": file.filename,
        "paginas": len(docs),
        "fragmentos": len(fragmentos),
        "preview": preview,
    }


@app.get("/api/upload/{session_id}")
def estado_upload(session_id: str):
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


@app.get("/api/sessions")
def listar_sesiones(q: str = ""):
    sesiones = buscar_sesiones(query=q)
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
def borrar_sesion(session_id: str):
    eliminar_sesion(session_id)


@app.patch("/api/sessions/{session_id}")
def editar_sesion(session_id: str, body: UpdateSessionBody):
    if body.titulo:
        actualizar_titulo_sesion(session_id, body.titulo)
    return {"mensaje": "Actualizado"}


@app.patch("/api/sessions/{session_id}/pin")
def pin_sesion(session_id: str):
    pinned = toggle_pin_sesion(session_id)
    return {"pinned": pinned}


@app.get("/api/historial/{session_id}", response_model=HistorialResponse)
def obtener_historial(session_id: str):
    mensajes = get_history(session_id)
    items = [
        HistorialItem(rol=m.rol, contenido=m.contenido, creado_en=str(m.creado_en))
        for m in mensajes
    ]
    return HistorialResponse(session_id=session_id, mensajes=items)


@app.delete("/api/historial/{session_id}")
def eliminar_historial(session_id: str):
    clear_history(session_id)
    return {"mensaje": f"Historial de '{session_id}' eliminado"}


@app.get("/api/theme")
def obtener_tema():
    theme = get_preference("theme")
    return {"theme": theme or "default"}


@app.put("/api/theme")
def guardar_tema(body: dict):
    theme = body.get("theme", "default")
    set_preference("theme", theme)
    return {"theme": theme}


@app.get("/api/carpetas", response_model=list[CarpetaResponse])
def obtener_carpetas():
    return [
        CarpetaResponse(id=c.id, nombre=c.nombre, creado_en=str(c.creado_en))
        for c in listar_carpetas()
    ]


@app.post("/api/carpetas", response_model=CarpetaResponse)
def nueva_carpeta(body: CarpetaBody):
    c = crear_carpeta(body.nombre)
    return CarpetaResponse(id=c.id, nombre=c.nombre, creado_en=str(c.creado_en))


@app.delete("/api/carpetas/{carpeta_id}", status_code=204)
def borrar_carpeta(carpeta_id: int):
    eliminar_carpeta(carpeta_id)


@app.get("/api/notas", response_model=list[NotaResponse])
def obtener_notas(carpeta_id: int | None = None, q: str = ""):
    return [
        NotaResponse(
            id=n.id, session_id=n.session_id, carpeta_id=n.carpeta_id,
            titulo=n.titulo, contenido=n.contenido,
            creado_en=str(n.creado_en), actualizado_en=str(n.actualizado_en),
        )
        for n in listar_notas(carpeta_id=carpeta_id, query=q)
    ]


@app.post("/api/notas", response_model=NotaResponse)
def nueva_nota(body: CrearNotaBody):
    n = crear_nota(titulo=body.titulo, contenido=body.contenido, session_id=body.session_id, carpeta_id=body.carpeta_id)
    return NotaResponse(
        id=n.id, session_id=n.session_id, carpeta_id=n.carpeta_id,
        titulo=n.titulo, contenido=n.contenido,
        creado_en=str(n.creado_en), actualizado_en=str(n.actualizado_en),
    )


@app.get("/api/notas/{nota_id}", response_model=NotaResponse)
def obtener_nota_endpoint(nota_id: int):
    n = obtener_nota(nota_id)
    if not n:
        raise HTTPException(404, "Nota no encontrada")
    return NotaResponse(
        id=n.id, session_id=n.session_id, carpeta_id=n.carpeta_id,
        titulo=n.titulo, contenido=n.contenido,
        creado_en=str(n.creado_en), actualizado_en=str(n.actualizado_en),
    )


@app.put("/api/notas/{nota_id}", response_model=NotaResponse)
def editar_nota(nota_id: int, body: ActualizarNotaBody):
    n = actualizar_nota(nota_id, titulo=body.titulo, contenido=body.contenido)
    if not n:
        raise HTTPException(404, "Nota no encontrada")
    return NotaResponse(
        id=n.id, session_id=n.session_id, carpeta_id=n.carpeta_id,
        titulo=n.titulo, contenido=n.contenido,
        creado_en=str(n.creado_en), actualizado_en=str(n.actualizado_en),
    )


@app.delete("/api/notas/{nota_id}", status_code=204)
def borrar_nota(nota_id: int):
    eliminar_nota(nota_id)
