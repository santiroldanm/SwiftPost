"""
Módulo base con funcionalidades comunes para los menús.
"""

from typing import Optional, Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from getpass import getpass

# Definir las opciones de menú
MENU_OPCIONES = {
    "sin_sesion": {"1": "Iniciar sesión", "2": "Registrarse", "0": "Salir"},
    "con_sesion": {
        "1": "Ver perfil",
        "2": "Actualizar perfil",
        "0": "Cerrar sesión",
    },
    "cliente": {"3": "Gestionar paquetes", "4": "Ver historial de envíos"},
    "empleado": {"3": "Gestionar envíos", "4": "Clientes", "5": "Reportes"},
    "admin": {"6": "Administrar usuarios", "7": "Configuración del sistema"},
}


def mostrar_encabezado(titulo: str = "") -> None:
    """Muestra un encabezado formateado."""
    print("\n" + "=" * 60)
    if titulo:
        print(f"{titulo:^60}")
        print("=" * 60)


def mostrar_menu_base(usuario_actual: Optional[object] = None) -> str:
    """
    Muestra el menú base y devuelve la opción seleccionada.

    Args:
        usuario_actual: Objeto del usuario actual (opcional)

    Returns:
        str: Opción seleccionada por el usuario
    """
    mostrar_encabezado("SWIFTPOST - SISTEMA DE MENSAJERÍA")

    if usuario_actual:
        # Mostrar información del usuario
        print(f"Usuario: {getattr(usuario_actual, 'nombre_usuario', 'N/A')}")
        try:
            rol = getattr(usuario_actual, "rol", None)
            if rol:
                print(f"Rol: {getattr(rol, 'nombre_rol', 'Sin rol')}")
        except Exception:
            print("Rol: No disponible")
        print("-" * 60)

        # Mostrar opciones según el rol
        opciones = {**MENU_OPCIONES["con_sesion"]}

        rol_nombre = (
            getattr(usuario_actual.rol, "nombre_rol", "").lower()
            if hasattr(usuario_actual, "rol")
            else ""
        )

        if rol_nombre == "administrador":
            opciones.update(MENU_OPCIONES["admin"])
        elif rol_nombre == "empleado":
            opciones.update(MENU_OPCIONES["empleado"])
        elif rol_nombre == "cliente":
            opciones.update(MENU_OPCIONES["cliente"])

    else:
        # Mostrar opciones para usuarios no autenticados
        opciones = MENU_OPCIONES["sin_sesion"]

    # Mostrar las opciones disponibles
    for key, value in sorted(opciones.items()):
        print(f"| {key:>2} | {value}")

    print("=" * 60)
    return input("\nSeleccione una opción: ").strip()


def obtener_input(mensaje: str, requerido: bool = True, password: bool = False) -> str:
    """
    Solicita entrada al usuario con validación básica.

    Args:
        mensaje: Mensaje a mostrar al usuario
        requerido: Si es True, el campo es obligatorio
        password: Si es True, oculta la entrada (para contraseñas)

    Returns:
        str: Valor ingresado por el usuario
    """
    while True:
        try:
            valor = getpass(mensaje) if password else input(mensaje)
            valor = valor.strip()

            if requerido and not valor:
                print("Este campo es obligatorio.")
                continue

            return valor

        except KeyboardInterrupt:
            print("\nOperación cancelada por el usuario.")
            raise
        except Exception as e:
            print(f"Error: {str(e)}")
            if not requerido:
                return ""


def confirmar_accion(mensaje: str = "¿Está seguro? (s/n): ") -> bool:
    """
    Pide confirmación al usuario para una acción.

    Args:
        mensaje: Mensaje de confirmación a mostrar

    Returns:
        bool: True si el usuario confirma, False en caso contrario
    """
    respuesta = input(mensaje).strip().lower()
    return respuesta in ("s", "si", "sí", "y", "yes")
