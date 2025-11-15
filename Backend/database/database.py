import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "swiftpost")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")

    if DB_USER and DB_PASSWORD:
        DATABASE_URL = (
            f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )
    else:
        raise ValueError(
            "Se requiere configurar las variables de entorno para la conexión a la base de datos"
        )

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=300,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    Generador de sesiones de base de datos.

    Uso:
        db = next(get_db())
        try:
            # Usar la sesión
            pass
        finally:
            db.close()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Inicializa la base de datos creando todas las tablas.
    """
    try:
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
        logger.info("Tablas creadas exitosamente")

        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info(f"Conexión a la base de datos exitosa: {result.scalar() == 1}")

    except Exception as e:
        logger.error(f"Error al inicializar la base de datos: {e}")
        raise
