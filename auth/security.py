from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from database.config import get_db
from cruds.usuario_crud import UsuarioCRUD
from cruds.rol_crud import RolCRUD

_cache_roles = {}


def obtener_roles(db: Session) -> Dict[str, str]:
    """
    Obtiene los roles desde la base de datos y los devuelve como un diccionario.
    Los roles se almacenan en caché para mejorar el rendimiento.
    """
    global _cache_roles

    if _cache_roles:
        return _cache_roles

    roles_db = RolCRUD().obtener_activos()
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


def autenticar_usuario(
    db: Session, nombre_usuario: str, contraseña: str
) -> Optional[Dict[str, Any]]:
    """
    Autentica un usuario con nombre de usuario y contraseña.
    Devuelve un diccionario con los datos del usuario y su rol si la autenticación es exitosa.
    """
    limpiar_cache_roles()

    # Crear instancia de UsuarioCRUD
    usuario_crud = UsuarioCRUD(db)
    usuario = usuario_crud.obtener_por_nombre_usuario(db, nombre_usuario=nombre_usuario)

    if not usuario or usuario.password != contraseña:
        return None

    rol = rol_crud.obtener_por_id(db, id_rol=usuario.id_rol)
    if not rol:
        return None

    nombre_rol = rol.nombre_rol.lower()

    return {
        "id_usuario": usuario.id_usuario,
        "nombre_usuario": usuario.nombre_usuario,
        "rol_id": str(usuario.id_rol),
        "rol_nombre": nombre_rol,
        "activo": usuario.activo,
    }


def obtener_rol_usuario(datos_usuario: Dict[str, Any]) -> str:
    """Obtiene el nombre del rol del usuario a partir de sus datos."""
    return datos_usuario.get("rol_nombre", "cliente")


def es_administrador(
    datos_usuario: Dict[str, Any], db: Optional[Session] = None
) -> bool:
    """Verifica si el usuario es administrador."""
    if not datos_usuario:
        return False

    if db is not None:
        nombre_rol = obtener_nombre_rol(db, datos_usuario.get("rol_id", ""))
        return nombre_rol and nombre_rol.lower() in ["admin", "administrador"]

    nombre_rol = datos_usuario.get("rol_nombre", "").lower()
    return nombre_rol in ["admin", "administrador"]


def es_empleado(datos_usuario: Dict[str, Any], db: Optional[Session] = None) -> bool:
    """Verifica si el usuario es empleado."""
    if not datos_usuario:
        return False

    if db is not None:
        nombre_rol = obtener_nombre_rol(db, datos_usuario.get("rol_id", ""))
        return nombre_rol and nombre_rol.lower() == "empleado"

    nombre_rol = datos_usuario.get("rol_nombre", "").lower()
    return nombre_rol == "empleado"


def es_cliente(datos_usuario: Dict[str, Any], db: Optional[Session] = None) -> bool:
    """Verifica si el usuario es cliente."""
    if not datos_usuario:
        return False

    if db is not None:
        nombre_rol = obtener_nombre_rol(db, datos_usuario.get("rol_id", ""))
        if not nombre_rol:
            return False
        return nombre_rol.lower() not in ["admin", "empleado"]

    nombre_rol = datos_usuario.get("rol_nombre", "").lower()
    return nombre_rol not in ["admin", "empleado"] and bool(nombre_rol)


def obtener_usuario_actual(
    db: Session, nombre_usuario: str
) -> Optional[Dict[str, Any]]:
    """Obtiene los datos del usuario actual basado en el nombre de usuario."""
    if not nombre_usuario:
        return None

    usuario = usuario_crud.obtener_por_nombre_usuario(db, nombre_usuario=nombre_usuario)
    if not usuario:
        return None

    rol = rol_crud.obtener_por_id(db, id_rol=usuario.id_rol)
    nombre_rol = rol.nombre_rol.lower() if rol else "cliente"

    return {
        "id_usuario": usuario.id_usuario,
        "nombre_usuario": usuario.nombre_usuario,
        "rol_id": usuario.id_rol,
        "rol_nombre": nombre_rol,
        "activo": usuario.activo,
    }


def obtener_usuario_activo_actual(
    db: Session, nombre_usuario: str
) -> Optional[Dict[str, Any]]:
    """Verifica si el usuario actual está activo y devuelve sus datos."""
    datos_usuario = obtener_usuario_actual(db, nombre_usuario)
    if datos_usuario and datos_usuario.get("activo", False):
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
        "admin": es_administrador,
        "empleado": es_empleado,
        "cliente": es_cliente,
    }

    verificador = verificadores_rol.get(rol_requerido.lower())
    return verificador(datos_usuario) if verificador else False
