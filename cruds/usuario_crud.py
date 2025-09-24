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
    
    def obtener_por_nombre_usuario(self, db: Session, nombre_usuario: str) -> Optional[Usuario]:
        """Obtiene un usuario por nombre de usuario."""
        return db.query(Usuario).filter(Usuario.nombre_usuario == nombre_usuario).first()
    
    def obtener_por_correo(self, db: Session, correo: str) -> Optional[Usuario]:
        """Obtiene un usuario por correo electrónico."""
        return db.query(Usuario).filter(Usuario.nombre_usuario == correo).first()
    
    def obtener_por_rol(self, db: Session, id_rol: UUID, saltar: int = 0, limite: int = 100) -> List[Usuario]:
        """Obtiene usuarios por rol."""
        return (
            db.query(Usuario)
            .filter(Usuario.id_rol == id_rol)
            .offset(saltar)
            .limit(limite)
            .all()
        )
    
    def obtener_activos(self, db: Session, saltar: int = 0, limite: int = 100) -> List[Usuario]:
        """Obtiene usuarios activos."""
        return (
            db.query(Usuario)
            .filter(Usuario.activo == True)  # noqa: E712
            .offset(saltar)
            .limit(limite)
            .all()
        )
    
    def autenticar(self, db: Session, nombre_usuario: str, contrasena: str) -> Optional[Usuario]:
        """Autentica un usuario por nombre de usuario y contraseña."""
        usuario = self.obtener_por_nombre_usuario(db, nombre_usuario=nombre_usuario)
        if not usuario:
            return None
        # La verificación real de contraseña debe hacerse en la capa de seguridad.
        # Aquí asumimos que otra función (authenticate_user) hace la validación.
        return usuario
    
    def crear_usuario(self, db: Session, *, datos_usuario: UsuarioCreate) -> Usuario:
        """Crea un nuevo usuario con campos coherentes (nombre_usuario, password, id_rol)."""
        usuario_db = Usuario(
            nombre_usuario=datos_usuario.nombre_usuario,
            password=datos_usuario.password,
            id_rol=datos_usuario.id_rol,
            activo=True,
            fecha_creacion=datetime.now()
        )
        db.add(usuario_db)
        db.commit()
        db.refresh(usuario_db)
        return usuario_db
    
    def actualizar_usuario(
        self,
        db: Session,
        *,
        usuario_db: Usuario,
        datos_actualizacion: Union[UsuarioUpdate, Dict[str, Any]],
        actualizado_por: UUID
    ) -> Usuario:
        """Actualiza un usuario existente."""
        if isinstance(datos_actualizacion, dict):
            datos_actualizados = datos_actualizacion
        else:
            datos_actualizados = datos_actualizacion.dict(exclude_unset=True)
        
        # No permitir actualización de contraseña directamente
        datos_actualizados.pop("password", None)
        
        # No gestionamos hashing aquí; debe ser responsabilidad de otra capa si se requiere.
        return super().update(db, db_obj=usuario_db, obj_in=datos_actualizados)
    
    def actualizar_contrasena(
        self, db: Session, *, usuario_db: Usuario, nueva_contrasena: str, id_usuario_actualizacion: UUID
    ) -> Usuario:
        """Actualiza la contraseña del usuario."""
        usuario_db.password = nueva_contrasena
        usuario_db.actualizado_por = id_usuario_actualizacion
        db.add(usuario_db)
        db.commit()
        db.refresh(usuario_db)
        return usuario_db
    
    def desactivar_usuario(self, db: Session, *, id_usuario: UUID, id_usuario_actualizacion: UUID) -> Optional[Usuario]:
        """Desactiva un usuario."""
        usuario = self.obtener_por_id(db, id=id_usuario)
        if usuario:
            usuario.activo = False
            usuario.actualizado_por = id_usuario_actualizacion
            usuario.fecha_actualizacion = datetime.utcnow()
            db.add(usuario)
            db.commit()
            db.refresh(usuario)
        return usuario
    
    def esta_activo(self, usuario: Usuario) -> bool:
        """Verifica si el usuario está activo."""
        return usuario.activo
    
    def es_superusuario(self, usuario: Usuario) -> bool:
        """Verifica si el usuario es superusuario."""
        # Aquí deberías implementar la lógica para determinar si es superusuario
        # Por ejemplo, podrías verificar si tiene un rol específico
        return getattr(getattr(usuario, "rol", None), "nombre_rol", "").lower() == "administrador"


usuario = UsuarioCRUD(Usuario)
