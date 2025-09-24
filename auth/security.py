from typing import Optional, Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from database.config import get_db
from cruds.usuario_crud import usuario as usuario_crud
from cruds.rol_crud import rol as rol_crud

# Variable global para almacenar en caché los roles
_cache_roles = {}

def obtener_roles(db: Session) -> Dict[str, str]:
    """
    Obtiene los roles desde la base de datos y los devuelve como un diccionario.
    Los roles se almacenan en caché para mejorar el rendimiento.
    """
    global _cache_roles
    
    # Si ya tenemos los roles en caché, los devolvemos
    if _cache_roles:
        return _cache_roles
    
    # Si no, los obtenemos de la base de datos
    roles_db = rol_crud.obtener_activos(db=db)
    _cache_roles = {rol.nombre_rol.lower(): str(rol.id_rol) for rol in roles_db}
    
    return _cache_roles

def limpiar_cache_roles():
    """Limpia la caché de roles (útil para pruebas o actualizaciones)"""
    global _cache_roles
    _cache_roles = {}

def obtener_id_rol(db: Session, nombre_rol: str) -> Optional[str]:
    """Obtiene el ID de un rol por su nombre (no distingue mayúsculas/minúsculas)"""
    roles = obtener_roles(db)
    return roles.get(nombre_rol.lower())

def obtener_nombre_rol(db: Session, id_rol: str) -> Optional[str]:
    """Obtiene el nombre de un rol por su ID"""
    roles = obtener_roles(db)
    for nombre, id_ in roles.items():
        if id_ == str(id_rol):
            return nombre
    return None

def autenticar_usuario(db: Session, nombre_usuario: str, contraseña: str) -> Optional[Dict[str, Any]]:
    """
    Autentica un usuario con nombre de usuario y contraseña.
    Devuelve un diccionario con los datos del usuario y su rol si la autenticación es exitosa.
    """
    # Limpiar caché de roles para asegurar que tenemos los últimos datos
    limpiar_cache_roles()
    
    usuario = usuario_crud.obtener_por_nombre_usuario(db, nombre_usuario=nombre_usuario)
    if not usuario or usuario.password != contraseña:  # Comparación directa sin hash
        return None
    
    # Obtener el nombre del rol
    rol = rol_crud.obtener_por_id(db, id_rol=usuario.id_rol)
    if not rol:
        return None  # Usuario sin rol válido
        
    nombre_rol = rol.nombre_rol.lower()
    
    return {
        'id_usuario': usuario.id_usuario,
        'nombre_usuario': usuario.nombre_usuario,
        'rol_id': str(usuario.id_rol),  # Asegurarse de que sea string
        'rol_nombre': nombre_rol,
        'activo': usuario.activo
    }

def obtener_rol_usuario(datos_usuario: Dict[str, Any]) -> str:
    """Obtiene el nombre del rol del usuario a partir de sus datos."""
    return datos_usuario.get('rol_nombre', 'cliente')

def es_administrador(datos_usuario: Dict[str, Any], db: Optional[Session] = None) -> bool:
    """Verifica si el usuario es administrador."""
    if not datos_usuario:
        return False
    
    # Si se proporciona una sesión de base de datos, verificar dinámicamente
    if db is not None:
        nombre_rol = obtener_nombre_rol(db, datos_usuario.get('rol_id', ''))
        return nombre_rol and nombre_rol.lower() in ['admin', 'administrador']
    
    # Si no hay sesión, intentar determinar por el nombre del rol en los datos del usuario
    nombre_rol = datos_usuario.get('rol_nombre', '').lower()
    return nombre_rol in ['admin', 'administrador']

def es_empleado(datos_usuario: Dict[str, Any], db: Optional[Session] = None) -> bool:
    """Verifica si el usuario es empleado."""
    if not datos_usuario:
        return False
    
    # Si se proporciona una sesión de base de datos, verificar dinámicamente
    if db is not None:
        nombre_rol = obtener_nombre_rol(db, datos_usuario.get('rol_id', ''))
        return nombre_rol and nombre_rol.lower() == 'empleado'
    
    # Si no hay sesión, intentar determinar por el nombre del rol en los datos del usuario
    nombre_rol = datos_usuario.get('rol_nombre', '').lower()
    return nombre_rol == 'empleado'

def es_cliente(datos_usuario: Dict[str, Any], db: Optional[Session] = None) -> bool:
    """Verifica si el usuario es cliente."""
    if not datos_usuario:
        return False
    
    # Si se proporciona una sesión de base de datos, verificar dinámicamente
    if db is not None:
        nombre_rol = obtener_nombre_rol(db, datos_usuario.get('rol_id', ''))
        # Si no es admin ni empleado, asumimos que es cliente
        if not nombre_rol:
            return False
        return nombre_rol.lower() not in ['admin', 'empleado']
    
    # Si no hay sesión, intentar determinar por el nombre del rol en los datos del usuario
    nombre_rol = datos_usuario.get('rol_nombre', '').lower()
    return nombre_rol not in ['admin', 'empleado'] and bool(nombre_rol)

def obtener_usuario_actual(db: Session, nombre_usuario: str) -> Optional[Dict[str, Any]]:
    """Obtiene los datos del usuario actual basado en el nombre de usuario."""
    if not nombre_usuario:
        return None
    
    usuario = usuario_crud.obtener_por_nombre_usuario(db, nombre_usuario=nombre_usuario)
    if not usuario:
        return None
    
    # Obtener el nombre del rol
    rol = rol_crud.obtener_por_id(db, id_rol=usuario.id_rol)
    nombre_rol = rol.nombre_rol.lower() if rol else 'cliente'
    
    return {
        'id_usuario': usuario.id_usuario,
        'nombre_usuario': usuario.nombre_usuario,
        'rol_id': usuario.id_rol,
        'rol_nombre': nombre_rol,
        'activo': usuario.activo
    }

def obtener_usuario_activo_actual(db: Session, nombre_usuario: str) -> Optional[Dict[str, Any]]:
    """Verifica si el usuario actual está activo y devuelve sus datos."""
    datos_usuario = obtener_usuario_actual(db, nombre_usuario)
    if datos_usuario and datos_usuario.get('activo', False):
        return datos_usuario
    return None

def requiere_rol(datos_usuario: Dict[str, Any], rol_requerido: str) -> bool:
    """
    Verifica si el usuario tiene el rol requerido.
    Los valores posibles para rol_requerido son: 'admin', 'empleado', 'cliente'
    """
    if not datos_usuario:
        return False
    
    verificadores_rol = {
        'admin': es_administrador,
        'empleado': es_empleado,
        'cliente': es_cliente
    }
    
    verificador = verificadores_rol.get(rol_requerido.lower())
    return verificador(datos_usuario) if verificador else False
