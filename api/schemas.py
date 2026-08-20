from pydantic import BaseModel


class AskRequest(BaseModel):
    pregunta: str
    session_id: str = "default"


class AskResponse(BaseModel):
    respuesta: str
    fuentes: list[dict]


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


class NotaResponse(BaseModel):
    id: int
    session_id: str | None
    carpeta_id: int
    titulo: str
    contenido: str
    creado_en: str
    actualizado_en: str
