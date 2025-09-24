"""
Script de migración para agregar coordenadas tridimensionales a la tabla 'sedes'.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from database.config import SessionLocal, engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrar_agregar_coordenadas_sede():
    """
    Agrega las columnas de coordenadas (latitud, longitud, altitud) a la tabla 'sedes'.
    """
    db = SessionLocal()
    try:
        # Verificar si las columnas ya existen
        check_columns_query = text(
            """
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'sedes' 
            AND column_name IN ('latitud', 'longitud', 'altitud')
            AND table_schema = 'public'
        """
        )

        result = db.execute(check_columns_query).fetchall()
        existing_columns = [row[0] for row in result]

        if len(existing_columns) == 3:
            logger.info("Las columnas de coordenadas ya existen en la tabla 'sedes'")
            return True

        logger.info("Agregando columnas de coordenadas a la tabla 'sedes'...")

        # Agregar columnas de coordenadas
        if "latitud" not in existing_columns:
            add_latitud_query = text(
                """
                ALTER TABLE sedes 
                ADD COLUMN latitud FLOAT
            """
            )
            db.execute(add_latitud_query)
            logger.info("Columna 'latitud' agregada")

        if "longitud" not in existing_columns:
            add_longitud_query = text(
                """
                ALTER TABLE sedes 
                ADD COLUMN longitud FLOAT
            """
            )
            db.execute(add_longitud_query)
            logger.info("Columna 'longitud' agregada")

        if "altitud" not in existing_columns:
            add_altitud_query = text(
                """
                ALTER TABLE sedes 
                ADD COLUMN altitud FLOAT
            """
            )
            db.execute(add_altitud_query)
            logger.info("Columna 'altitud' agregada")

        # Agregar comentarios a las columnas
        add_comments_query = text(
            """
            COMMENT ON COLUMN sedes.latitud IS 'Latitud en grados decimales';
            COMMENT ON COLUMN sedes.longitud IS 'Longitud en grados decimales';
            COMMENT ON COLUMN sedes.altitud IS 'Altitud en metros sobre el nivel del mar';
        """
        )
        db.execute(add_comments_query)

        # Agregar algunas coordenadas de ejemplo para sedes existentes
        # (Coordenadas de ejemplo para Medellín, Colombia)
        update_example_coords = text(
            """
            UPDATE sedes 
            SET 
                latitud = 6.2442 + (RANDOM() * 0.1 - 0.05),
                longitud = -75.5812 + (RANDOM() * 0.1 - 0.05),
                altitud = 1495 + (RANDOM() * 100 - 50)
            WHERE latitud IS NULL AND longitud IS NULL
        """
        )
        db.execute(update_example_coords)

        db.commit()
        logger.info("Migración de coordenadas completada exitosamente")

        # Verificar que la migración fue exitosa
        verify_query = text("SELECT COUNT(*) FROM sedes WHERE latitud IS NOT NULL")
        count = db.execute(verify_query).scalar()
        logger.info(f"Sedes con coordenadas asignadas: {count}")

        return True

    except Exception as e:
        logger.error(f"Error durante la migración: {str(e)}")
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    print("Iniciando migracion para agregar coordenadas a tabla 'sedes'...")
    success = migrar_agregar_coordenadas_sede()
    if success:
        print("Migracion de coordenadas completada exitosamente")
    else:
        print("Error durante la migracion de coordenadas")
        sys.exit(1)
