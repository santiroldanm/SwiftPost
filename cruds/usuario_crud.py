from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from sqlalchemy.orm import Session

# Importar dependientes primero para registrar clases en el registry de SQLAlchemy
from entities.cliente import Cliente  # noqa: F401
from entities.empleado import Empleado  # noqa: F401
from entities.usuario import Usuario, UsuarioCreate, UsuarioUpdate
from .base_crud import CRUDBase
from datetime import datetime


class UsuarioCRUD(CRUDBase[Usuario, UsuarioCreate, UsuarioUpdate]):
    """Operaciones CRUD para Usuario."""
    
    def get_by_username(self, db: Session, username: str) -> Optional[Usuario]:
        """Obtiene un usuario por nombre de usuario."""
        return db.query(Usuario).filter(Usuario.nombre_usuario == username).first()
    
    def get_by_email(self, db: Session, correo: str) -> Optional[Usuario]:
        """Compat: no existe correo en Usuario; buscamos por nombre_usuario."""
        return db.query(Usuario).filter(Usuario.nombre_usuario == correo).first()
    
    def get_by_rol(self, db: Session, id_rol: UUID, skip: int = 0, limit: int = 100) -> List[Usuario]:
        """Obtiene usuarios por rol."""
        return (
            db.query(Usuario)
            .filter(Usuario.id_rol == id_rol)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_activos(self, db: Session, skip: int = 0, limit: int = 100) -> List[Usuario]:
        """Obtiene usuarios activos."""
        return (
            db.query(Usuario)
            .filter(Usuario.activo == True)  # noqa: E712
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def authenticate(self, db: Session, username: str, password: str) -> Optional[Usuario]:
        """Autentica un usuario."""
        user = self.get_by_username(db, username=username)
        if not user:
            return None
        # La verificación real de contraseña debe hacerse en la capa de seguridad.
        # Aquí asumimos que otra función (authenticate_user) hace la validación.
        return user
    
    def create(self, db: Session, *, obj_in: UsuarioCreate) -> Usuario:
        """Crea un nuevo usuario con campos coherentes (nombre_usuario, password, id_rol)."""
        db_obj = Usuario(
            nombre_usuario=obj_in.nombre_usuario,
            password=obj_in.password,
            id_rol=obj_in.id_rol,
            activo=True,
            fecha_creacion=datetime.now()
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(
        self,
        db: Session,
        *,
        db_obj: Usuario,
        obj_in: Union[UsuarioUpdate, Dict[str, Any]],
        actualizado_por: UUID
    ) -> Usuario:
        """Actualiza un usuario."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        # No gestionamos hashing aquí; debe ser responsabilidad de otra capa si se requiere.
        return super().update(db, db_obj=db_obj, obj_in=update_data)
    
    def update_password(
        self, db: Session, *, db_obj: Usuario, nueva_contrasena: str, actualizado_por: UUID
    ) -> Usuario:
        """Actualiza la contraseña del usuario."""
        db_obj.password = nueva_contrasena
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def deactivate(self, db: Session, *, id: UUID, actualizado_por: UUID) -> Usuario:
        """Desactiva un usuario."""
        usuario = self.get(db, id)
        if usuario:
            usuario.activo = False
            usuario.actualizado_por = actualizado_por
            db.add(usuario)
            db.commit()
            db.refresh(usuario)
        return usuario
    
    def is_active(self, usuario: Usuario) -> bool:
        """Verifica si el usuario está activo."""
        return usuario.activo
    
    def is_superuser(self, usuario: Usuario) -> bool:
        """Verifica si el usuario es superusuario."""
        # Ajustado al campo correcto nombre_rol
        return (
            getattr(getattr(usuario, "rol", None), "nombre_rol", "").lower() == "administrador"
        )


usuario = UsuarioCRUD(Usuario)
