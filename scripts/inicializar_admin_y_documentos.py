import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from database.database import SessionLocal
from entities.rol import Rol
from entities.usuario import Usuario
from entities.tipo_documento import TipoDocumento


def crear_usuario_administrador(db: Session):
    """Crea el usuario administrador si no existe."""
    rol_admin = db.query(Rol).filter(Rol.nombre_rol == "administrador").first()

    if not rol_admin:
        print("Error: No se encontró el rol de administrador.")
        return None

    usuario_admin = db.query(Usuario).filter(Usuario.nombre_usuario == "admin").first()

    if usuario_admin:
        print("El usuario administrador ya existe.")
        return usuario_admin

    usuario_admin = Usuario(
        id_rol=rol_admin.id_rol,
        nombre_usuario="admin",
        password="admin123",  
        activo=True,
        fecha_creacion=datetime.now(),
    )

    db.add(usuario_admin)
    db.commit()
    db.refresh(usuario_admin)

    print("Usuario administrador creado con éxito.")
    print(f"Usuario: admin")
    print(f"Contraseña: admin123 (¡Cámbiala después del primer inicio de sesión!)")

    return usuario_admin


def crear_tipos_documento_por_defecto(db: Session, id_usuario_creador: str):
    """Crea los tipos de documento por defecto si no existen."""
    documentos_por_defecto = [
        {"nombre": "Cédula de Ciudadanía", "codigo": "CC", "numero": 1, "activo": True},
        {"nombre": "Tarjeta de Identidad", "codigo": "TI", "numero": 2, "activo": True},
        {
            "nombre": "Cédula de Extranjería",
            "codigo": "CE",
            "numero": 3,
            "activo": True,
        },
        {"nombre": "Pasaporte", "codigo": "PA", "numero": 4, "activo": True},
        {"nombre": "NIT", "codigo": "NIT", "numero": 5, "activo": True},
    ]

    contador_creados = 0

    for datos_documento in documentos_por_defecto:
        documento_existente = (
            db.query(TipoDocumento)
            .filter(
                (TipoDocumento.codigo == datos_documento["codigo"])
                | (TipoDocumento.nombre == datos_documento["nombre"])
            )
            .first()
        )

        if not documento_existente:
            nuevo_documento = TipoDocumento(
                **datos_documento,
                creado_por=id_usuario_creador,
                actualizado_por=id_usuario_creador,
                fecha_creacion=datetime.now(),
            )
            db.add(nuevo_documento)
            contador_creados += 1
            print(
                f"Tipo de documento creado: {datos_documento['nombre']} ({datos_documento['codigo']})"
            )

    if contador_creados > 0:
        db.commit()
        print(f"\nSe crearon {contador_creados} tipos de documento por defecto.")
    else:
        print("\nTodos los tipos de documento ya existen en la base de datos.")


def principal():
    """Función principal del script de inicialización."""
    db = SessionLocal()

    try:
        print("\n=== Creando usuario administrador ===")
        usuario_admin = crear_usuario_administrador(db)

        if not usuario_admin:
            print("No se pudo crear el usuario administrador. Saliendo...")
            return

        print("\n=== Creando tipos de documento por defecto ===")
        crear_tipos_documento_por_defecto(db, usuario_admin.id_usuario)

        print("\n¡Inicialización completada con éxito!")

    except Exception as e:
        print(f"\nError durante la inicialización: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    principal()
