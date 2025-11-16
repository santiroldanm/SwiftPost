"""
Configuración de la base de datos PostgreSQL con Neon
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "neondb")
    DB_USERNAME = os.getenv("DB_USERNAME", "")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")

    if DB_USERNAME and DB_PASSWORD:
        DATABASE_URL = (
            f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )
    else:
        raise ValueError(
            "Se requiere DATABASE_URL o las credenciales individuales de la base de datos"
        )


def get_engine():
    """Create and configure the SQLAlchemy engine with UUID support"""
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_recycle=300,
    )

    try:
        with engine.connect() as conn:
            conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
            conn.commit()
    except Exception:
        pass

    return engine


engine = get_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

__all__ = ["DATABASE_URL", "engine", "Base", "SessionLocal", "get_db", "create_tables"]


def get_db():
    """
    Generador de sesiones de base de datos
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Crear todas las tablas definidas en los modelos
    """
    from entities import (
        usuario,
        rol,
        cliente,
        empleado,
        sede,
        tipo_documento,
        paquete,
        detalle_entrega,
        transporte,
    )

    Base.metadata.create_all(bind=engine)
