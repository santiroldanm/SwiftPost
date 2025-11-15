"""Módulo de autenticación y autorización para SwiftPost."""

from .security import (
    autenticar_usuario as authenticate_user,
    obtener_usuario_actual as get_current_user,
    obtener_usuario_activo_actual as get_current_active_user,
    obtener_rol_usuario as get_user_role,
    es_administrador as is_admin,
    es_empleado as is_employee,
    es_cliente as is_client,
    requiere_rol as require_role,
    obtener_roles as get_roles,
    obtener_id_rol as get_role_id,
    obtener_nombre_rol as get_role_name,
    limpiar_cache_roles as clear_roles_cache
)

__all__ = [
    'authenticate_user',
    'get_current_user',
    'get_current_active_user',
    'get_user_role',
    'is_admin',
    'is_employee',
    'is_client',
    'require_role',
    'get_roles',
    'get_role_id',
    'get_role_name',
    'clear_roles_cache'
]
