import sys
import os
from typing import List, Optional
from datetime import datetime

# Agregar el directorio raíz al path para poder importar los modelos
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
        {"nombre_rol": "cliente", "activo": True}
    ]
    
    for rol_data in roles_por_defecto:
        # Verificar si el rol ya existe
        rol_existente = db.query(Rol).filter(
            Rol.nombre_rol == rol_data["nombre_rol"]
        ).first()
        
        if not rol_existente:
            # Crear el rol si no existe
            nuevo_rol = Rol(
                nombre_rol=rol_data["nombre_rol"],
                activo=rol_data["activo"],
                fecha_creacion=datetime.now()
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
    # Crear tablas si no existen
    create_tables()
    
    # Inicializar la sesión de la base de datos
    db = SessionLocal()
    try:
        # Inicializar roles
        init_roles(db)
    except Exception as e:
        print(f"Error durante la inicialización: {e}")
        db.rollback()
        raise
    finally:
        # Cerrar la sesión
        db.close()

if __name__ == "__main__":
    main()
