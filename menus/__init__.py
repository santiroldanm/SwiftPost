"""
Paquete que contiene los módulos de menús de la aplicación SwiftPost.
"""

# Exportar las funciones principales del menú de administrador
from .admin_menu import (
    mostrar_menu_administrador,
    manejar_opcion_administrador,
    gestionar_clientes,
    gestionar_sedes,
    gestionar_transportes,
    gestionar_paquetes_admin,
    mostrar_reportes_admin,
    configuracion_sistema
)

# Exportar las funciones del menú de usuarios
from .usuario_menu import (
    mostrar_menu_usuarios,
    listar_usuarios,
    buscar_usuario,
    editar_usuario,
    cambiar_estado_usuario,
    manejar_menu_usuarios
)

# Exportar las funciones del menú de empleados
from .empleado_menu import (
    mostrar_menu_empleados,
    listar_empleados,
    buscar_empleado,
    registrar_empleado,
    editar_empleado,
    cambiar_estado_empleado,
    manejar_menu_empleados
)

# Exportar las funciones del menú de sedes
from .sede_menu import (
    mostrar_menu_sedes,
    listar_sedes,
    buscar_sede_por_ciudad,
    agregar_sede,
    editar_sede,
    cambiar_estado_sede,
    manejar_menu_sedes
)

__all__ = [
    # Menú de administrador
    'mostrar_menu_administrador',
    'manejar_opcion_administrador',
    'gestionar_clientes',
    'gestionar_sedes',
    'gestionar_transportes',
    'gestionar_paquetes_admin',
    'mostrar_reportes_admin',
    'configuracion_sistema',
    
    # Menú de usuarios
    'mostrar_menu_usuarios',
    'listar_usuarios',
    'buscar_usuario',
    'editar_usuario',
    'cambiar_estado_usuario',
    'manejar_menu_usuarios',
    
    # Menú de empleados
    'mostrar_menu_empleados',
    'listar_empleados',
    'buscar_empleado',
    'registrar_empleado',
    'editar_empleado',
    'cambiar_estado_empleado',
    'manejar_menu_empleados',
    
    # Menú de sedes
    'mostrar_menu_sedes',
    'listar_sedes',
    'buscar_sede_por_ciudad',
    'agregar_sede',
    'editar_sede',
    'cambiar_estado_sede',
    'manejar_menu_sedes'
]
