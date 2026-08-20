import os
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from src.config import RAIZ

RUTA_SQLITE = RAIZ / "data" / "historial.db"


RUTA_SQLITE.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(f"sqlite:///{RUTA_SQLITE}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Mensaje(Base):
    __tablename__ = "mensajes"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    rol = Column(String)
    contenido = Column(Text)
    creado_en = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Sesion(Base):
    __tablename__ = "sesiones"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    titulo = Column(String, default="Nueva conversación")
    pinned = Column(Boolean, default=False)
    creado_en = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    actualizado_en = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class Preferencia(Base):
    __tablename__ = "preferencias"

    clave = Column(String, primary_key=True)
    valor = Column(String, default="")


class Carpeta(Base):
    __tablename__ = "carpetas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, default="General")
    creado_en = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    notas = relationship("Nota", back_populates="carpeta", cascade="all, delete-orphan")


class Nota(Base):
    __tablename__ = "notas"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, nullable=True, index=True)
    carpeta_id = Column(Integer, ForeignKey("carpetas.id"), default=1)
    titulo = Column(String, default="Sin título")
    contenido = Column(Text, default="")
    creado_en = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    actualizado_en = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    carpeta = relationship("Carpeta", back_populates="notas")


def init_db():
    Base.metadata.create_all(bind=engine)
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE sesiones ADD COLUMN pinned BOOLEAN DEFAULT 0"))
            conn.commit()
    except Exception:
        pass
    db = SessionLocal()
    try:
        existe = db.query(Carpeta).filter(Carpeta.nombre == "General").first()
        if not existe:
            db.add(Carpeta(nombre="General"))
            db.commit()
    finally:
        db.close()


def add_message(session_id: str, rol: str, contenido: str):
    db = SessionLocal()
    msg = Mensaje(session_id=session_id, rol=rol, contenido=contenido)
    db.add(msg)
    db.commit()
    db.close()


def get_history(session_id: str, limit: int = 20):
    db = SessionLocal()
    msgs = (
        db.query(Mensaje)
        .filter(Mensaje.session_id == session_id)
        .order_by(Mensaje.creado_en.asc())
        .limit(limit)
        .all()
    )
    db.close()
    return msgs


def clear_history(session_id: str):
    db = SessionLocal()
    db.query(Mensaje).filter(Mensaje.session_id == session_id).delete()
    db.query(Sesion).filter(Sesion.session_id == session_id).delete()
    db.commit()
    db.close()


def crear_o_actualizar_sesion(session_id: str, titulo: str):
    db = SessionLocal()
    sesion = db.query(Sesion).filter(Sesion.session_id == session_id).first()
    now = datetime.now(timezone.utc)
    if sesion:
        sesion.actualizado_en = now
    else:
        sesion = Sesion(session_id=session_id, titulo=titulo[:100])
        db.add(sesion)
    db.commit()
    db.close()


def eliminar_sesion(session_id: str):
    db = SessionLocal()
    db.query(Mensaje).filter(Mensaje.session_id == session_id).delete()
    db.query(Sesion).filter(Sesion.session_id == session_id).delete()
    db.commit()
    db.close()


def actualizar_titulo_sesion(session_id: str, titulo: str):
    db = SessionLocal()
    sesion = db.query(Sesion).filter(Sesion.session_id == session_id).first()
    if sesion:
        sesion.titulo = titulo[:100]
        db.commit()
    db.close()


def toggle_pin_sesion(session_id: str) -> bool:
    db = SessionLocal()
    sesion = db.query(Sesion).filter(Sesion.session_id == session_id).first()
    if not sesion:
        db.close()
        return False
    sesion.pinned = not sesion.pinned
    db.commit()
    db.close()
    return sesion.pinned


def buscar_sesiones(query: str = "", limite: int = 50):
    db = SessionLocal()
    q = db.query(Sesion).order_by(Sesion.actualizado_en.desc())
    if query:
        q = q.filter(Sesion.titulo.ilike(f"%{query}%"))
    resultados = q.limit(limite).all()
    db.close()
    return resultados


def get_preference(clave: str) -> str | None:
    db = SessionLocal()
    pref = db.query(Preferencia).filter(Preferencia.clave == clave).first()
    db.close()
    return pref.valor if pref else None


def set_preference(clave: str, valor: str):
    db = SessionLocal()
    pref = db.query(Preferencia).filter(Preferencia.clave == clave).first()
    if pref:
        pref.valor = valor
    else:
        db.add(Preferencia(clave=clave, valor=valor))
    db.commit()
    db.close()


def listar_carpetas():
    db = SessionLocal()
    resultado = db.query(Carpeta).order_by(Carpeta.nombre).all()
    db.close()
    return resultado


def crear_carpeta(nombre: str):
    db = SessionLocal()
    carpeta = Carpeta(nombre=nombre)
    db.add(carpeta)
    db.commit()
    db.refresh(carpeta)
    db.close()
    return carpeta


def eliminar_carpeta(id: int):
    db = SessionLocal()
    carpeta = db.query(Carpeta).filter(Carpeta.id == id).first()
    if carpeta:
        db.delete(carpeta)
        db.commit()
    db.close()


def listar_notas(carpeta_id: int | None = None, query: str = ""):
    db = SessionLocal()
    q = db.query(Nota).order_by(Nota.actualizado_en.desc())
    if carpeta_id:
        q = q.filter(Nota.carpeta_id == carpeta_id)
    if query:
        like = f"%{query}%"
        q = q.filter(Nota.titulo.ilike(like) | Nota.contenido.ilike(like))
    resultado = q.all()
    db.close()
    return resultado


def crear_nota(titulo: str, contenido: str, session_id: str | None = None, carpeta_id: int = 1):
    db = SessionLocal()
    nota = Nota(titulo=titulo, contenido=contenido, session_id=session_id, carpeta_id=carpeta_id)
    db.add(nota)
    db.commit()
    db.refresh(nota)
    db.close()
    return nota


def obtener_nota(id: int):
    db = SessionLocal()
    nota = db.query(Nota).filter(Nota.id == id).first()
    db.close()
    return nota


def actualizar_nota(id: int, titulo: str | None = None, contenido: str | None = None):
    db = SessionLocal()
    nota = db.query(Nota).filter(Nota.id == id).first()
    if nota:
        if titulo is not None:
            nota.titulo = titulo
        if contenido is not None:
            nota.contenido = contenido
        db.commit()
        db.refresh(nota)
    db.close()
    return nota


def eliminar_nota(id: int):
    db = SessionLocal()
    nota = db.query(Nota).filter(Nota.id == id).first()
    if nota:
        db.delete(nota)
        db.commit()
    db.close()