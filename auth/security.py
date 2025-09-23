from typing import Optional
from sqlalchemy.orm import Session
from database.config import get_db
from cruds.usuario_crud import usuario as usuario_crud

def authenticate_user(db: Session, username: str, password: str):
    """Autentica un usuario con nombre de usuario y contraseña (sin encriptación)."""
    user = usuario_crud.get_by_username(db, username=username)
    if not user or user.password != password:  # Comparación directa sin hash
        return None
    return user

def get_current_user(db: Session, username: str):
    """Obtiene el usuario actual basado en el nombre de usuario."""
    if not username:
        return None
    return usuario_crud.get_by_username(db, username=username)

def get_current_active_user(db: Session, username: str):
    """Verifica si el usuario actual está activo."""
    user = get_current_user(db, username)
    if user and not user.activo:
        return None
    return user
