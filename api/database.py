import os
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, create_engine, inspect, text
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from src.config import RAIZ

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Render entrega URLs con 'postgres://' o 'postgresql://'.
    # Forzamos el uso de 'postgresql+psycopg2://' para SQLAlchemy.
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
    elif DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1)
        
    engine = create_engine(DATABASE_URL)
else:
    # Fallback local usando SQLite
    RUTA_SQLITE = RAIZ / "data" / "historial.db"
    RUTA_SQLITE.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{RUTA_SQLITE}", connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Mensaje(Base):
    __tablename__ = "mensajes"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    user_id = Column(String, index=True, nullable=True)  # ID de Clerk
    rol = Column(String)
    contenido = Column(Text)
    creado_en = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Sesion(Base):
    __tablename__ = "sesiones"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    user_id = Column(String, index=True, nullable=True)  # ID de Clerk
    titulo = Column(String, default="Nueva conversación")
    pinned = Column(Boolean, default=False)
    creado_en = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    actualizado_en = Column(
        DateTime(timezone=True),
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
    creado_en = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    notas = relationship("Nota", back_populates="carpeta", cascade="all, delete-orphan")


class Nota(Base):
    __tablename__ = "notas"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=True)  # ID de Clerk
    session_id = Column(String, nullable=True, index=True)
    carpeta_id = Column(Integer, ForeignKey("carpetas.id"), default=1)
    titulo = Column(String, default="Sin título")
    contenido = Column(Text, default="")
    creado_en = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    actualizado_en = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    carpeta = relationship("Carpeta", back_populates="notas")


def init_db():
    Base.metadata.create_all(bind=engine)

    # Migra tablas existentes sin abortar las columnas siguientes si una ya existe.
    columnas_requeridas = {
        "sesiones": {"pinned": "BOOLEAN DEFAULT FALSE", "user_id": "VARCHAR"},
        "mensajes": {"user_id": "VARCHAR"},
        "notas": {"user_id": "VARCHAR"},
    }
    inspector = inspect(engine)
    for tabla, columnas in columnas_requeridas.items():
        existentes = {columna["name"] for columna in inspector.get_columns(tabla)}
        for columna, tipo in columnas.items():
            if columna not in existentes:
                with engine.begin() as conn:
                    conn.execute(text(f"ALTER TABLE {tabla} ADD COLUMN {columna} {tipo}"))

    db = SessionLocal()
    try:
        existe = db.query(Carpeta).filter(Carpeta.nombre == "General").first()
        if not existe:
            db.add(Carpeta(nombre="General"))
            db.commit()
    finally:
        db.close()


def add_message(session_id: str, rol: str, contenido: str, user_id: str | None = None):
    db = SessionLocal()
    msg = Mensaje(session_id=session_id, rol=rol, contenido=contenido, user_id=user_id)
    db.add(msg)
    db.commit()
    db.close()


def get_history(session_id: str, limit: int = 20, user_id: str | None = None):
    db = SessionLocal()
    q = db.query(Mensaje).filter(Mensaje.session_id == session_id)
    if user_id:
        q = q.filter(Mensaje.user_id == user_id)
    msgs = q.order_by(Mensaje.creado_en.asc()).limit(limit).all()
    db.close()
    return msgs


def clear_history(session_id: str, user_id: str | None = None):
    db = SessionLocal()
    q_msg = db.query(Mensaje).filter(Mensaje.session_id == session_id)
    q_ses = db.query(Sesion).filter(Sesion.session_id == session_id)
    if user_id:
        q_msg = q_msg.filter(Mensaje.user_id == user_id)
        q_ses = q_ses.filter(Sesion.user_id == user_id)
    q_msg.delete(synchronize_session=False)
    q_ses.delete(synchronize_session=False)
    db.commit()
    db.close()


def crear_o_actualizar_sesion(session_id: str, titulo: str, user_id: str | None = None):
    db = SessionLocal()
    q = db.query(Sesion).filter(Sesion.session_id == session_id)
    if user_id:
        q = q.filter(Sesion.user_id == user_id)
    sesion = q.first()
    now = datetime.now(timezone.utc)
    if sesion:
        sesion.actualizado_en = now
    else:
        sesion = Sesion(session_id=session_id, titulo=titulo[:100], user_id=user_id)
        db.add(sesion)
    db.commit()
    db.close()


def eliminar_sesion(session_id: str, user_id: str | None = None):
    db = SessionLocal()
    q_msg = db.query(Mensaje).filter(Mensaje.session_id == session_id)
    q_ses = db.query(Sesion).filter(Sesion.session_id == session_id)
    if user_id:
        q_msg = q_msg.filter(Mensaje.user_id == user_id)
        q_ses = q_ses.filter(Sesion.user_id == user_id)
    q_msg.delete(synchronize_session=False)
    q_ses.delete(synchronize_session=False)
    db.commit()
    db.close()


def actualizar_titulo_sesion(session_id: str, titulo: str, user_id: str | None = None):
    db = SessionLocal()
    q = db.query(Sesion).filter(Sesion.session_id == session_id)
    if user_id:
        q = q.filter(Sesion.user_id == user_id)
    sesion = q.first()
    if sesion:
        sesion.titulo = titulo[:100]
        db.commit()
    db.close()


def toggle_pin_sesion(session_id: str, user_id: str | None = None) -> bool:
    db = SessionLocal()
    q = db.query(Sesion).filter(Sesion.session_id == session_id)
    if user_id:
        q = q.filter(Sesion.user_id == user_id)
    sesion = q.first()
    if not sesion:
        db.close()
        return False
    sesion.pinned = not sesion.pinned
    db.commit()
    db.close()
    return sesion.pinned


def buscar_sesiones(query: str = "", limite: int = 50, user_id: str | None = None):
    db = SessionLocal()
    q = db.query(Sesion)
    if user_id:
        q = q.filter(Sesion.user_id == user_id)
    q = q.order_by(Sesion.actualizado_en.desc())
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


def listar_notas(carpeta_id: int | None = None, query: str = "", user_id: str | None = None):
    db = SessionLocal()
    q = db.query(Nota)
    if user_id:
        q = q.filter(Nota.user_id == user_id)
    q = q.order_by(Nota.actualizado_en.desc())
    if carpeta_id:
        q = q.filter(Nota.carpeta_id == carpeta_id)
    if query:
        like = f"%{query}%"
        q = q.filter(Nota.titulo.ilike(like) | Nota.contenido.ilike(like))
    resultado = q.all()
    db.close()
    return resultado


def crear_nota(titulo: str, contenido: str, session_id: str | None = None, carpeta_id: int = 1, user_id: str | None = None):
    db = SessionLocal()
    nota = Nota(
        titulo=titulo,
        contenido=contenido,
        session_id=session_id,
        carpeta_id=carpeta_id,
        user_id=user_id
    )
    db.add(nota)
    db.commit()
    db.refresh(nota)
    db.close()
    return nota


def obtener_nota(id: int, user_id: str | None = None):
    db = SessionLocal()
    q = db.query(Nota).filter(Nota.id == id)
    if user_id:
        q = q.filter(Nota.user_id == user_id)
    nota = q.first()
    db.close()
    return nota


def actualizar_nota(id: int, titulo: str | None = None, contenido: str | None = None, user_id: str | None = None):
    db = SessionLocal()
    q = db.query(Nota).filter(Nota.id == id)
    if user_id:
        q = q.filter(Nota.user_id == user_id)
    nota = q.first()
    if nota:
        if titulo is not None:
            nota.titulo = titulo
        if contenido is not None:
            nota.contenido = contenido
        db.commit()
        db.refresh(nota)
    db.close()
    return nota


def eliminar_nota(id: int, user_id: str | None = None):
    db = SessionLocal()
    q = db.query(Nota).filter(Nota.id == id)
    if user_id:
        q = q.filter(Nota.user_id == user_id)
    nota = q.first()
    if nota:
        db.delete(nota)
        db.commit()
    db.close()