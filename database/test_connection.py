"""
Script para probar la conexión a PostgreSQL (Neon)
"""

import sys
from datetime import datetime

from database.config import DATABASE_URL, engine
from sqlalchemy import text


def test_connection():
    """Probar la conexión a la base de datos"""
    print("=== PRUEBA DE CONEXION A POSTGRESQL (NEON) ===\n")
    print(f"URL de conexion: {DATABASE_URL}")
    print()

    try:
        # Intentar conectar
        with engine.connect() as connection:
            print("[OK] Conexion exitosa a PostgreSQL!")

            # Probar una consulta simple
            result = connection.execute(text("SELECT version() as version"))
            version = result.fetchone()
            print(f"[OK] Version de PostgreSQL: {version[0]}")

            # Verificar si la base de datos existe
            result = connection.execute(
                text(
                    "SELECT datname FROM pg_database WHERE datname = current_database()"
                )
            )
            db_exists = result.fetchone()

            if db_exists:
                print(f"[OK] Conectado a la base de datos: {db_exists[0]}")
            else:
                print("[WARNING] No se pudo verificar la base de datos actual")

            # Listar tablas disponibles
            print("\nTablas disponibles:")
            result = connection.execute(
                text(
                    "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
                )
            )
            tables = result.fetchall()
            if tables:
                for table in tables:
                    print(f"  - {table[0]}")
            else:
                print("  (No hay tablas creadas aun)")

    except Exception as e:
        print(f"[ERROR] Error de conexion: {e}")
        print("\nPosibles soluciones:")
        print("1. Verificar que la URL de conexion sea correcta")
        print("2. Verificar que la base de datos este activa en Neon")
        print("3. Verificar que las credenciales sean correctas")
        print("4. Verificar la conexion a internet")
        return False

    return True


def test_tables():
    """Probar la creacion de tablas"""
    print("\n=== PROBANDO CREACION DE TABLAS ===\n")

    try:
        from database.config import create_tables

        create_tables()
        print("[OK] Tablas creadas exitosamente")

    except Exception as e:
        print(f"[ERROR] Error creando las tablas: {e}")
        return False

    return True


def create_admin_user():
    """Crear usuario administrador por defecto"""
    print("\n=== CREANDO USUARIO ADMINISTRADOR ===\n")

    try:
        from database.config import SessionLocal
        from entities.usuario import Usuario
        from entities.rol import Rol
        from passlib.context import CryptContext
        import uuid

        db = SessionLocal()

        # Verificar si ya existe un admin
        admin_rol = db.query(Rol).filter(Rol.nombre_rol == "administrador").first()

        if not admin_rol:
            # Crear rol de administrador si no existe
            admin_rol = Rol(
                nombre_rol="administrador",
                activo=True,
                fecha_creacion=datetime.now(),
                fecha_actualizacion=datetime.now(),
            )
            db.add(admin_rol)
            db.commit()
            db.refresh(admin_rol)
            print("[OK] Rol de administrador creado exitosamente")

        # Verificar si ya existe un usuario admin
        admin_exists = db.query(Usuario).filter(Usuario.rol == admin_rol.id_rol).first()

        if admin_exists:
            print(
                f"[OK] Usuario administrador ya existe: {admin_exists.nombre_usuario}"
            )
            db.close()
            return True

        # Hashear la contraseña
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed_password = pwd_context.hash("admin123")

        # Crear usuario admin
        admin_user = Usuario(
            rol=admin_rol.id_rol,
            primer_nombre="Admin",
            segundo_nombre=None,
            primer_apellido="Sistema",
            segundo_apellido=None,
            nombre_usuario="admin",
            password=hashed_password,
            activo=True,
            fecha_creacion=datetime.now(),
            fecha_actualizacion=datetime.now(),
        )

        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        print("[OK] Usuario administrador creado exitosamente")
        print(f"     ID: {admin_user.id_usuario}")
        print(f"     Usuario: {admin_user.nombre_usuario}")
        print(f"     Nombre: {admin_user.primer_nombre} {admin_user.primer_apellido}")

        db.close()
        return True

    except Exception as e:
        print(f"[ERROR] Error creando usuario administrador: {e}")
        print(f"[DEBUG] Tipo de error: {type(e).__name__}")
        print(f"[DEBUG] Modulo del error: {type(e).__module__}")
        print(f"[DEBUG] Traceback completo:")
        import traceback

        traceback.print_exc()

        # Debug adicional para errores de importación
        if "UUID" in str(e) or "SchemaItem" in str(e):
            print(f"[DEBUG] Error relacionado con UUID detectado")
            print(f"[DEBUG] Verificando imports en entidades...")

            import os

            entities_dir = os.path.join(os.path.dirname(__file__), "..", "entities")
            for file in os.listdir(entities_dir):
                if file.endswith(".py") and file != "__init__.py":
                    print(f"[DEBUG] Archivo: {file}")
                    try:
                        with open(
                            os.path.join(entities_dir, file), "r", encoding="utf-8"
                        ) as f:
                            content = f.read()
                            if "from uuid import" in content:
                                print(f"[DEBUG]   - Usa 'from uuid import' (PROBLEMA)")
                            if "Column(UUID" in content:
                                print(f"[DEBUG]   - Usa 'Column(UUID' (PROBLEMA)")
                            if "PG_UUID" in content:
                                print(f"[DEBUG]   - Usa 'PG_UUID' (CORRECTO)")
                    except Exception as file_err:
                        print(f"[DEBUG]   - Error leyendo archivo: {file_err}")
        return False


if __name__ == "__main__":
    print("Iniciando prueba de conexion...\n")

    # Probar conexion
    if test_connection():
        print("\n" + "=" * 50)
        # Probar creacion de tablas
        if test_tables():
            print("\n" + "=" * 50)
            # Crear usuario administrador
            create_admin_user()

        print("\n[SUCCESS] Configuracion completada!")
        print("Ahora puedes ejecutar:")
        print("  python main.py")
        print("  python ejemplo_basico.py")
    else:
        print("\n[ERROR] No se pudo establecer la conexion")
        sys.exit(1)
