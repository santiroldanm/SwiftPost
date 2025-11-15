"""
Paquete de configuración de la base de datos.

Este paquete contiene toda la configuración necesaria para la conexión
y operación con la base de datos PostgreSQL en Neon.
"""

from .config import DATABASE_URL, engine, Base, SessionLocal, get_db, create_tables

__all__ = ["DATABASE_URL", "engine", "Base", "SessionLocal", "get_db", "create_tables"]
