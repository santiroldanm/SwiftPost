from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from sqlalchemy.orm import Session

from entities.usuario import Usuario, UsuarioCreate, UsuarioUpdate
from .base_crud import CRUDBase


class UsuarioCRUD(CRUDBase[Usuario, UsuarioCreate, UsuarioUpdate]):
    """CRUD operations for Usuario."""
    
    def get_by_username(self, db: Session, username: str) -> Optional[Usuario]:
        """Get a user by username."""
        return db.query(Usuario).filter(Usuario.username == username).first()
    
    def get_by_email(self, db: Session, correo: str) -> Optional[Usuario]:
        """Get a user by email."""
        return db.query(Usuario).filter(Usuario.correo == correo).first()
    
    def get_by_rol(self, db: Session, id_rol: UUID, skip: int = 0, limit: int = 100) -> List[Usuario]:
        """Get users by role."""
        return (
            db.query(Usuario)
            .filter(Usuario.id_rol == id_rol)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_activos(self, db: Session, skip: int = 0, limit: int = 100) -> List[Usuario]:
        """Get active users."""
        return (
            db.query(Usuario)
            .filter(Usuario.activo == True)  # noqa: E712
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def authenticate(self, db: Session, username: str, password: str) -> Optional[Usuario]:
        """Authenticate a user."""
        user = self.get_by_username(db, username=username)
        if not user:
            return None
        if not user.verificar_contrasena(password):
            return None
        return user
    
    def create(self, db: Session, *, obj_in: UsuarioCreate, creado_por: UUID) -> Usuario:
        """Create a new user."""
        db_obj = Usuario(
            **obj_in.dict(exclude={"contrasena"}),
            contrasena=Usuario.generar_hash_contrasena(obj_in.contrasena),
            creado_por=creado_por
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
        """Update a user."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        if "contrasena" in update_data:
            update_data["contrasena"] = Usuario.generar_hash_contrasena(update_data["contrasena"])
        
        update_data["actualizado_por"] = actualizado_por
        return super().update(db, db_obj=db_obj, obj_in=update_data)
    
    def update_password(
        self, db: Session, *, db_obj: Usuario, nueva_contrasena: str, actualizado_por: UUID
    ) -> Usuario:
        """Update user password."""
        db_obj.contrasena = Usuario.generar_hash_contrasena(nueva_contrasena)
        db_obj.actualizado_por = actualizado_por
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def deactivate(self, db: Session, *, id: UUID, actualizado_por: UUID) -> Usuario:
        """Deactivate a user."""
        usuario = self.get(db, id)
        if usuario:
            usuario.activo = False
            usuario.actualizado_por = actualizado_por
            db.add(usuario)
            db.commit()
            db.refresh(usuario)
        return usuario
    
    def is_active(self, usuario: Usuario) -> bool:
        """Check if user is active."""
        return usuario.activo
    
    def is_superuser(self, usuario: Usuario) -> bool:
        """Check if user is superuser."""
        # Assuming there's a way to check if the user has admin role
        # You might need to adjust this based on your role/permission system
        return usuario.rol.nombre.lower() == "admin" if hasattr(usuario, "rol") and usuario.rol else False


usuario = UsuarioCRUD(Usuario)
