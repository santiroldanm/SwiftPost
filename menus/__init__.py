"""
Módulo que contiene los menús de la aplicación SwiftPost.
"""

from .base import mostrar_encabezado, mostrar_menu_base
from .cliente import menu_cliente
from .empleado import menu_empleado
from .admin import menu_admin
from .inicio import menu_inicio

__all__ = [
    "mostrar_encabezado",
    "mostrar_menu_base",
    "menu_inicio",
    "menu_cliente",
    "menu_empleado",
    "menu_admin",
]
