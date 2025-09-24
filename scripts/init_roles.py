import sys
import os
from typing import List, Optional
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from database.config import SessionLocal, engine, create_tables
from entities.rol import Rol


def init_roles(db: Session):
    """
    Inicializa los roles básicos en la base de datos si no existen.
    """
    roles_por_defecto = [
        {"nombre_rol": "administrador", "activo": True},
        {"nombre_rol": "empleado", "activo": True},
        {"nombre_rol": "cliente", "activo": True},
    ]

    for rol_data in roles_por_defecto:
        rol_existente = (
            db.query(Rol).filter(Rol.nombre_rol == rol_data["nombre_rol"]).first()
        )

        if not rol_existente:
            nuevo_rol = Rol(
                nombre_rol=rol_data["nombre_rol"],
                activo=rol_data["activo"],
                fecha_creacion=datetime.now(),
            )
            db.add(nuevo_rol)
            print(f"Rol creado: {rol_data['nombre_rol']}")

    try:
        db.commit()
        print("Inicialización de roles completada con éxito.")
    except Exception as e:
        db.rollback()
        print(f"Error al inicializar roles: {e}")
        raise


def main():
    create_tables()

    db = SessionLocal()
    try:
        init_roles(db)
    except Exception as e:
        print(f"Error durante la inicialización: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
