from pydantic import BaseModel


class AskRequest(BaseModel):
    pregunta: str
    session_id: str = "default"


class AskResponse(BaseModel):
    respuesta: str
    fuentes: list[dict]


# ==================== SCHEMAS PARA MODO MEJORADO ====================

class ChatRequest(BaseModel):
    """Request para endpoint /chat mejorado con soporte de modos e idiomas."""
    pregunta: str
    session_id: str = "default"
    modo: str = "rag"  # "rag", "general", "hibrido"
    idioma: str = "es"  # "es", "en", "fr", "de"
    incluir_fuentes: bool = True


class ChatResponse(BaseModel):
    """Response para endpoint /chat mejorado."""
    respuesta: str
    modo_usado: str
    fuentes: list[dict] = []
    tokens_usados: dict = {}  # {"entrada": int, "salida": int}


# ==================== RESTO DE SCHEMAS ====================

class BuscarRequest(BaseModel):
    pregunta: str
    k: int = 3
    user_id: str


class BuscarResponse(BaseModel):
    resultados: list[dict]


class HistorialItem(BaseModel):
    rol: str
    contenido: str
    creado_en: str


class HistorialResponse(BaseModel):
    session_id: str
    mensajes: list[HistorialItem]


class UpdateSessionBody(BaseModel):
    titulo: str | None = None


class CarpetaBody(BaseModel):
    nombre: str


class CarpetaResponse(BaseModel):
    id: int
    nombre: str
    creado_en: str


class CrearNotaBody(BaseModel):
    titulo: str = "Sin título"
    contenido: str = ""
    session_id: str | None = None
    carpeta_id: int = 1


class ActualizarNotaBody(BaseModel):
    titulo: str | None = None
    contenido: str | None = None


# ==================== SCHEMAS PARA ESTADÍSTICAS ====================

class EstadísticasResponse(BaseModel):
    """Response para endpoint /api/stats."""
    total_tokens_entrada: int
    total_tokens_salida: int
    total_tokens: int
    costo_estimado: str
    total_requests: int
    requests_por_modo: dict
    requests_por_idioma: dict
    tokens_promedio_por_request: int
    tokens_entrada_promedio: int
    tokens_salida_promedio: int


class NotaResponse(BaseModel):
    id: int
    session_id: str | None
    carpeta_id: int
    titulo: str
    contenido: str
    creado_en: str
    actualizado_en: str
