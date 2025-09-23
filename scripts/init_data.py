import sys
import os
from datetime import datetime
from uuid import uuid4

# Agregar el directorio raíz al path para poder importar los modelos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from database.config import SessionLocal, engine, create_tables
from entities.sede import Sede
from entities.tipo_documento import TipoDocumento


def init_sedes(db: Session, admin_id: str):
    """
    Inicializa las sedes básicas en la base de datos si no existen.
    """
    sedes_por_defecto = [
        {
            "ciudad": "Bogotá",
            "direccion": "Carrera 10 # 20-30",
            "telefono": 1234567,
        },
        {
            "ciudad": "Medellín",
            "direccion": "Calle 50 # 40-30",
            "telefono": 2345678,
        },
        {
            "ciudad": "Cali",
            "direccion": "Avenida 6N # 15-45",
            "telefono": 3456789,
        },
    ]

    for sede_data in sedes_por_defecto:
        # Verificar si la sede ya existe por ciudad
        sede_existente = (
            db.query(Sede).filter(Sede.ciudad == sede_data["ciudad"]).first()
        )

        if not sede_existente:
            # Crear la sede si no existe
            nueva_sede = Sede(
                id_sede=uuid4(),
                ciudad=sede_data["ciudad"],
                direccion=sede_data["direccion"],
                telefono=sede_data["telefono"],
                activo=True,
                fecha_creacion=datetime.now(),
                creado_por=admin_id,
                actualizado_por=admin_id,
            )
            db.add(nueva_sede)
            print(f"Sede creada: {sede_data['ciudad']}")

    try:
        db.commit()
        print("Inicialización de sedes completada con éxito.")
    except Exception as e:
        db.rollback()
        print(f"Error al inicializar sedes: {e}")
        raise


def init_tipos_documento(db: Session, admin_id: str):
    """
    Inicializa los tipos de documento básicos en la base de datos si no existen.
    """
    tipos_documento_por_defecto = [
        {"nombre": "Cédula de Ciudadanía", "codigo": "CC", "numero": 1},
        {"nombre": "Tarjeta de Identidad", "codigo": "TI", "numero": 2},
        {"nombre": "Cédula de Extranjería", "codigo": "CE", "numero": 3},
        {"nombre": "NIT", "codigo": "NIT", "numero": 4},
        {"nombre": "Pasaporte", "codigo": "PAS", "numero": 5},
    ]

    for tipo_doc_data in tipos_documento_por_defecto:
        # Verificar si el tipo de documento ya existe por código
        tipo_doc_existente = (
            db.query(TipoDocumento)
            .filter(TipoDocumento.codigo == tipo_doc_data["codigo"])
            .first()
        )

        if not tipo_doc_existente:
            # Crear el tipo de documento si no existe
            nuevo_tipo_doc = TipoDocumento(
                id_tipo_documento=uuid4(),
                nombre=tipo_doc_data["nombre"],
                codigo=tipo_doc_data["codigo"],
                numero=tipo_doc_data["numero"],
                activo=True,
                fecha_creacion=datetime.now(),
                creado_por=admin_id,
                actualizado_por=admin_id,
            )
            db.add(nuevo_tipo_doc)
            print(
                f"Tipo de documento creado: {tipo_doc_data['nombre']} ({tipo_doc_data['codigo']})"
            )

    try:
        db.commit()
        print("Inicialización de tipos de documento completada con éxito.")
    except Exception as e:
        db.rollback()
        print(f"Error al inicializar tipos de documento: {e}")
        raise


def main():
    # Crear tablas si no existen
    create_tables()

    admin_id = "5883b41c-d178-4f34-a08a-00a8fb03ede7"

    # Inicializar la sesión de la base de datos
    db = SessionLocal()
    try:
        # Inicializar sedes
        init_sedes(db, admin_id)

        # Inicializar tipos de documento
        init_tipos_documento(db, admin_id)

    except Exception as e:
        print(f"Error durante la inicialización: {e}")
        db.rollback()
        raise
    finally:
        # Cerrar la sesión
        db.close()


if __name__ == "__main__":
    main()
