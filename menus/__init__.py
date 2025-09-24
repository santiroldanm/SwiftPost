"""
Paquete que contiene los módulos de menús de la aplicación SwiftPost.
"""

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

from .usuario_menu import (
    mostrar_menu_usuarios,
    listar_usuarios,
    buscar_usuario,
    editar_usuario,
    cambiar_estado_usuario,
    manejar_menu_usuarios
)

from .empleado_menu import (
    mostrar_menu_empleados,
    listar_empleados,
    buscar_empleado,
    registrar_empleado,
    editar_empleado,
    cambiar_estado_empleado,
    manejar_menu_empleados
)

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
    'mostrar_menu_administrador',
    'manejar_opcion_administrador',
    'gestionar_clientes',
    'gestionar_sedes',
    'gestionar_transportes',
    'gestionar_paquetes_admin',
    'mostrar_reportes_admin',
    'configuracion_sistema',
    
    'mostrar_menu_usuarios',
    'listar_usuarios',
    'buscar_usuario',
    'editar_usuario',
    'cambiar_estado_usuario',
    'manejar_menu_usuarios',
    
    'mostrar_menu_empleados',
    'listar_empleados',
    'buscar_empleado',
    'registrar_empleado',
    'editar_empleado',
    'cambiar_estado_empleado',
    'manejar_menu_empleados',
    
    'mostrar_menu_sedes',
    'listar_sedes',
    'buscar_sede_por_ciudad',
    'agregar_sede',
    'editar_sede',
    'cambiar_estado_sede',
    'manejar_menu_sedes'
]
