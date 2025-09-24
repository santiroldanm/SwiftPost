"""Módulo de autenticación y autorización para SwiftPost."""

from .security import (
    authenticate_user,
    get_current_user,
    get_current_active_user,
    get_user_role,
    is_admin,
    is_employee,
    is_client,
    require_role,
    get_roles,
    get_role_id,
    get_role_name,
    clear_roles_cache
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
