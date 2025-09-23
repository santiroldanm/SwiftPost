"""
Módulo para el menú de inicio de sesión y registro de usuarios.
"""

from typing import Optional, Tuple
from sqlalchemy.orm import Session
from getpass import getpass
from entities.usuario import UsuarioCreate
from .base import mostrar_encabezado, obtener_input
from cruds.usuario_crud import usuario as usuario_crud
from cruds.rol_crud import rol as rol_crud
from entities.usuario import Usuario
from auth.security import authenticate_user


def autenticar_usuario(db: Session) -> Tuple[Optional[Usuario], bool]:
    """
    Maneja el proceso de autenticación de usuarios.

    Args:
        db: Sesión de base de datos

    Returns:
        Tuple[Optional[Usuario], bool]: (usuario_autenticado, salir)
    """
    mostrar_encabezado("INICIO DE SESIÓN")

    try:
        usuario = obtener_input("Nombre de usuario: ")
        contrasena = getpass("Contraseña: ")

        # Autenticar al usuario
        usuario_autenticado = authenticate_user(db, usuario, contrasena)

        if not usuario_autenticado:
            input(
                "\n¡Error! Usuario o contraseña incorrectos. Presione Enter para continuar..."
            )
            return None, False

        if not usuario_autenticado.activo:
            input(
                "\n¡Error! Este usuario está inactivo. Contacte al administrador. Presione Enter para continuar..."
            )
            return None, False

        input(
            f"\n¡Bienvenido, {usuario_autenticado.nombre_usuario}! Presione Enter para continuar..."
        )
        return usuario_autenticado, False

    except KeyboardInterrupt:
        return None, True
    except Exception as e:
        input(f"\nError inesperado: {str(e)}. Presione Enter para continuar...")
        return None, False


def registrar_nuevo_usuario(db: Session) -> bool:
    """
    Maneja el registro de nuevos usuarios.

    Args:
        db: Sesión de base de datos

    Returns:
        bool: True si el registro fue exitoso, False en caso contrario
    """
    mostrar_encabezado("REGISTRO DE NUEVO USUARIO")

    try:
        # Obtener datos del usuario
        nombre_usuario = obtener_input("Nombre de usuario: ")

        # Verificar si el usuario ya existe
        if usuario_crud.get_by_username(db, nombre_usuario):
            input(
                "\n¡Error! Este nombre de usuario ya está en uso. Presione Enter para continuar..."
            )
            return False

        # Obtener contraseña
        while True:
            contrasena = getpass("Contraseña (mínimo 8 caracteres): ")
            if len(contrasena) < 8:
                print("La contraseña debe tener al menos 8 caracteres.")
                continue

            confirmacion = getpass("Confirme la contraseña: ")
            if contrasena != confirmacion:
                print("Las contraseñas no coinciden. Intente de nuevo.")
                continue
            break

        # Seleccionar rol
        print("\nSeleccione el tipo de usuario:")
        roles = rol_crud.obtener_todos(db)
        for i, rol in enumerate(roles, 1):
            print(f"{i}. {rol.nombre_rol}")

        while True:
            try:
                opcion = int(input("\nOpción: ")) - 1
                if 0 <= opcion < len(roles):
                    rol_id = roles[opcion].id_rol
                    break
                print("Opción inválida. Intente de nuevo.")
            except (ValueError, IndexError):
                print("Por favor ingrese un número válido.")

        # Crear el objeto UsuarioCreate
        usuario_data = UsuarioCreate(
            nombre_usuario=nombre_usuario,
            password=contrasena,
            id_rol=str(rol_id),
            activo=True,
        )

        # Crear el usuario
        usuario_nuevo = usuario_crud.create(db=db, obj_in=usuario_data)

        db.commit()
        input(
            f"\n¡Usuario {usuario_nuevo.nombre_usuario} registrado exitosamente! Presione Enter para continuar..."
        )
        return True

    except KeyboardInterrupt:
        return False
    except Exception as e:
        db.rollback()
        input(
            f"\nError al registrar el usuario: {str(e)}. Presione Enter para continuar..."
        )
        return False


def menu_inicio(db: Session) -> Tuple[Optional[Usuario], bool]:
    """
    Muestra el menú de inicio (login/registro).

    Args:
        db: Sesión de base de datos

    Returns:
        Tuple[Optional[Usuario], bool]: (usuario_autenticado, salir)
    """
    while True:
        mostrar_encabezado("BIENVENIDO A SWIFTPOST")
        print("1. Iniciar sesión")
        print("2. Registrarse")
        print("0. Salir")
        print("=" * 60)

        opcion = input("\nSeleccione una opción: ").strip()

        if opcion == "1":
            usuario, salir = autenticar_usuario(db)
            if usuario or salir:
                return usuario, salir
        elif opcion == "2":
            registrar_nuevo_usuario(db)
        elif opcion == "0":
            return None, True
        else:
            input("\nOpción inválida. Presione Enter para continuar...")
