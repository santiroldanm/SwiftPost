import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

# Obtener la URL de conexión desde las variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL")

# Si no hay DATABASE_URL, construir desde variables individuales
if not DATABASE_URL:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "swiftpost")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    
    if DB_USER and DB_PASSWORD:
        DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    else:
        raise ValueError(
            "Se requiere configurar las variables de entorno para la conexión a la base de datos"
        )

# Configurar el motor de SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Mostrar consultas SQL en la consola (útil para desarrollo)
    pool_pre_ping=True,  # Verificar la conexión antes de usarla
    pool_recycle=300,  # Reciclar conexiones cada 5 minutos
)

# Crear la fábrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
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
        # Importar todos los modelos para que sean registrados con SQLAlchemy
        from entities import usuario, rol, cliente, empleado, sede, tipo_documento, paquete, detalle_entrega, transporte
        
        # Crear todas las tablas
        Base.metadata.create_all(bind=engine)
        logger.info("Tablas creadas exitosamente")
        
        # Verificar la conexión
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info(f"Conexión a la base de datos exitosa: {result.scalar() == 1}")
            
    except Exception as e:
        logger.error(f"Error al inicializar la base de datos: {e}")
        raise