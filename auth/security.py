from typing import Optional, Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from database.config import get_db
from cruds.usuario_crud import usuario as usuario_crud
from cruds.rol_crud import rol as rol_crud

# Variable global para cachear los roles
_roles_cache = {}

def get_roles(db: Session) -> Dict[str, str]:
    """
    Obtiene los roles desde la base de datos y los devuelve como un diccionario.
    Los roles se almacenan en caché para mejorar el rendimiento.
    """
    global _roles_cache
    
    # Si ya tenemos los roles en caché, los devolvemos
    if _roles_cache:
        return _roles_cache
    
    # Si no, los obtenemos de la base de datos
    roles_db = rol_crud.obtener_activos(db=db)
    _roles_cache = {rol.nombre_rol.lower(): str(rol.id_rol) for rol in roles_db}
    
    return _roles_cache

def clear_roles_cache():
    """Limpia la caché de roles (útil para pruebas o actualizaciones)"""
    global _roles_cache
    _roles_cache = {}

def get_role_id(db: Session, role_name: str) -> Optional[str]:
    """Obtiene el ID de un rol por su nombre (case-insensitive)"""
    roles = get_roles(db)
    return roles.get(role_name.lower())

def get_role_name(db: Session, role_id: str) -> Optional[str]:
    """Obtiene el nombre de un rol por su ID"""
    roles = get_roles(db)
    for name, id_ in roles.items():
        if id_ == str(role_id):
            return name
    return None

def authenticate_user(db: Session, username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Autentica un usuario con nombre de usuario y contraseña.
    Devuelve un diccionario con los datos del usuario y su rol si la autenticación es exitosa.
    """
    # Limpiar caché de roles para asegurar que tenemos los últimos datos
    clear_roles_cache()
    
    user = usuario_crud.obtener_por_nombre_usuario(db, nombre_usuario=username)
    if not user or user.password != password:  # Comparación directa sin hash
        return None
    
    # Obtener el nombre del rol
    rol = rol_crud.obtener_por_id(db, id_rol=user.id_rol)
    if not rol:
        return None  # Usuario sin rol válido
        
    rol_nombre = rol.nombre_rol.lower()
    
    return {
        'id_usuario': user.id_usuario,
        'nombre_usuario': user.nombre_usuario,
        'rol_id': str(user.id_rol),  # Asegurarse de que sea string
        'rol_nombre': rol_nombre,
        'activo': user.activo
    }

def get_user_role(user_data: Dict[str, Any]) -> str:
    """Obtiene el nombre del rol del usuario a partir de sus datos."""
    return user_data.get('rol_nombre', 'cliente')

def is_admin(user_data: Dict[str, Any], db: Optional[Session] = None) -> bool:
    """Verifica si el usuario es administrador."""
    if not user_data:
        return False
    
    # Si se proporciona una sesión de base de datos, verificar dinámicamente
    if db is not None:
        role_name = get_role_name(db, user_data.get('rol_id', ''))
        return role_name and role_name.lower() == 'admin'
    
    # Si no hay sesión, intentar determinar por el nombre del rol en los datos del usuario
    role_name = user_data.get('rol_nombre', '').lower()
    return role_name == 'admin'

def is_employee(user_data: Dict[str, Any], db: Optional[Session] = None) -> bool:
    """Verifica si el usuario es empleado."""
    if not user_data:
        return False
    
    # Si se proporciona una sesión de base de datos, verificar dinámicamente
    if db is not None:
        role_name = get_role_name(db, user_data.get('rol_id', ''))
        return role_name and role_name.lower() == 'empleado'
    
    # Si no hay sesión, intentar determinar por el nombre del rol en los datos del usuario
    role_name = user_data.get('rol_nombre', '').lower()
    return role_name == 'empleado'

def is_client(user_data: Dict[str, Any], db: Optional[Session] = None) -> bool:
    """Verifica si el usuario es cliente."""
    if not user_data:
        return False
    
    # Si se proporciona una sesión de base de datos, verificar dinámicamente
    if db is not None:
        role_name = get_role_name(db, user_data.get('rol_id', ''))
        # Si no es admin ni empleado, asumimos que es cliente
        if not role_name:
            return False
        return role_name.lower() not in ['admin', 'empleado']
    
    # Si no hay sesión, intentar determinar por el nombre del rol en los datos del usuario
    role_name = user_data.get('rol_nombre', '').lower()
    return role_name not in ['admin', 'empleado'] and bool(role_name)

def get_current_user(db: Session, username: str) -> Optional[Dict[str, Any]]:
    """Obtiene los datos del usuario actual basado en el nombre de usuario."""
    if not username:
        return None
    
    user = usuario_crud.get_by_username(db, username=username)
    if not user:
        return None
    
    # Obtener el nombre del rol
    rol = rol_crud.get(db, id=user.id_rol)
    rol_nombre = rol.nombre_rol.lower() if rol else 'cliente'
    
    return {
        'id_usuario': user.id_usuario,
        'nombre_usuario': user.nombre_usuario,
        'rol_id': user.id_rol,
        'rol_nombre': rol_nombre,
        'activo': user.activo
    }

def get_current_active_user(db: Session, username: str) -> Optional[Dict[str, Any]]:
    """Verifica si el usuario actual está activo y devuelve sus datos."""
    user_data = get_current_user(db, username)
    if user_data and user_data.get('activo', False):
        return user_data
    return None

def require_role(user_data: Dict[str, Any], required_role: str) -> bool:
    """
    Verifica si el usuario tiene el rol requerido.
    Los valores posibles para required_role son: 'admin', 'empleado', 'cliente'
    """
    if not user_data:
        return False
    
    role_checkers = {
        'admin': is_admin,
        'empleado': is_employee,
        'cliente': is_client
    }
    
    checker = role_checkers.get(required_role.lower())
    return checker(user_data) if checker else False
