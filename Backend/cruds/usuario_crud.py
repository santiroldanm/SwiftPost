from typing import Any, Dict, List, Optional, Union
from uuid import UUID
from sqlalchemy.orm import Session
from entities.cliente import Cliente
from entities.empleado import Empleado
from entities.rol import Rol
from entities.usuario import Usuario, UsuarioCreate, UsuarioUpdate
from .base_crud import CRUDBase
from datetime import datetime


class UsuarioCRUD(CRUDBase[Usuario, UsuarioCreate, UsuarioUpdate]):
    """Operaciones CRUD para Usuario."""

    def __init__(self, db: Session):
        super().__init__(Usuario, db)
        self.db = db

    def obtener_usuarios(self, skip: int = 0, limit: int = 100) -> List[Usuario]:
        """
        Obtener lista de usuarios con paginación

        Args:
            skip: Número de registros a omitir
            limit: Límite de registros a retornar

        Returns:
            Lista de usuarios
        """
        return self.db.query(Usuario).offset(skip).limit(limit).all()

    def obtener_por_id(self, id: Union[UUID, str]) -> Optional[Usuario]:
        """Obtiene un usuario por su ID."""
        try:
            if not id:
                return None
            """ Convertir a string para la consulta """
            id_str = str(id) if isinstance(id, UUID) else id
            return self.db.query(Usuario).filter(Usuario.id_usuario == id_str).first()
        except Exception as e:
            print(f"Error al obtener usuario por ID {id}: {str(e)}")
            return None

    def obtener_por_nombre_usuario(self, nombre_usuario: str) -> Optional[Usuario]:
        """Obtiene un usuario por nombre de usuario."""
        return (
            self.db.query(Usuario)
            .filter(Usuario.nombre_usuario == nombre_usuario)
            .first()
        )

    def obtener_por_correo(self, correo: str) -> Optional[Usuario]:
        """Obtiene un usuario por correo electrónico."""
        return self.db.query(Usuario).filter(Usuario.nombre_usuario == correo).first()

    def obtener_por_rol(
        self, id_rol: UUID, saltar: int = 0, limite: int = 100
    ) -> List[Usuario]:
        """Obtiene usuarios por rol."""
        return (
            self.db.query(Usuario)
            .filter(Usuario.id_rol == id_rol)
            .offset(saltar)
            .limit(limite)
            .all()
        )

    def obtener_usuarios_admin(self) -> List[Usuario]:
        """
        Obtener todos los usuarios administradores

        Returns:
            Lista de usuarios administradores
        """
        return (
            self.db.query(Usuario)
            .join(Rol)
            .filter((Rol.nombre_rol == "admin") | (Rol.nombre_rol == "administrador"))
            .all()
        )

    def obtener_activos(self, saltar: int = 0, limite: int = 100) -> List[Usuario]:
        """Obtiene usuarios activos."""
        return (
            self.db.query(Usuario)
            .filter(Usuario.activo == True)
            .offset(saltar)
            .limit(limite)
            .all()
        )

    def autenticar(self, nombre_usuario: str, contraseña: str) -> Optional[Usuario]:
        """Autentica un usuario por nombre de usuario y contraseña."""
        nombre_usuario = nombre_usuario.strip() if nombre_usuario else ""
        contraseña = contraseña.strip() if contraseña else ""
        
        if not nombre_usuario or not contraseña:
            return None
        
        usuario = self.obtener_por_nombre_usuario(nombre_usuario=nombre_usuario)
        if not usuario:
            print(f"Usuario no encontrado: {nombre_usuario}")
            return None
        
        if usuario.password.strip() != contraseña:
            print(f"Contraseña incorrecta para usuario: {nombre_usuario}")
            return None
        
        if not usuario.activo:
            print(f"Usuario inactivo: {nombre_usuario}")
            return None
        
        return usuario

    def crear_usuario(
        self,
        *,
        nombre_usuario: str,
        password: str,
        id_rol: str,
    ) -> Usuario:
        """Crea un nuevo usuario con campos individuales."""
        usuario_db = Usuario(
            nombre_usuario=nombre_usuario,
            password=password,
            id_rol=id_rol,
            activo=True,
            fecha_creacion=datetime.now(),
        )
        self.db.add(usuario_db)
        self.db.commit()
        self.db.refresh(usuario_db)
        return usuario_db

    def actualizar_usuario(
        self,
        *,
        usuario_db: Usuario,
        datos_actualizacion: Union[UsuarioUpdate, Dict[str, Any]],
        actualizado_por: UUID,
    ) -> Usuario:
        """Actualiza un usuario existente."""
        try:
            if not isinstance(datos_actualizacion, dict):
                datos_actualizacion = datos_actualizacion.dict(exclude_unset=True)

            for campo, valor in datos_actualizacion.items():
                if campo != "password" and hasattr(usuario_db, campo):
                    setattr(usuario_db, campo, valor)

            usuario_db.fecha_actualizacion = datetime.now()
            usuario_db.actualizado_por = actualizado_por

            self.db.commit()
            self.db.refresh(usuario_db)
            return usuario_db

        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Error al actualizar usuario: {str(e)}")

    def eliminar_usuario(self, usuario_id: UUID) -> bool:
        """
        Marca un usuario como eliminado (soft delete).
        """
        try:
            usuario = self.obtener_por_id(usuario_id)
            if not usuario:
                return False

            usuario.activo = False
            usuario.fecha_actualizacion = datetime.now()
            usuario.actualizado_por = usuario_id
            self.db.commit()
            self.db.refresh(usuario)
            return True

        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Error al eliminar usuario: {str(e)}")

    def actualizar_contrasena(
        self,
        *,
        usuario_db: Usuario,
        nueva_contrasena: str,
        id_usuario_actualizacion: UUID,
    ) -> Usuario:
        """Actualiza la contraseña del usuario."""
        usuario_db.password = nueva_contrasena
        usuario_db.actualizado_por = id_usuario_actualizacion
        self.db.add(usuario_db)
        self.db.commit()
        self.db.refresh(usuario_db)
        return usuario_db

    def desactivar_usuario(
        self, *, id_usuario: UUID, id_usuario_actualizacion: UUID
    ) -> Optional[Usuario]:
        """Desactiva un usuario."""
        usuario = self.obtener_por_id(id=id_usuario)
        if usuario:
            usuario.activo = False
            usuario.actualizado_por = id_usuario_actualizacion
            usuario.fecha_actualizacion = datetime.utcnow()
            self.db.add(usuario)
            self.db.commit()
            self.db.refresh(usuario)
        return usuario

    def esta_activo(self, usuario: Usuario) -> bool:
        """Verifica si el usuario está activo."""
        return usuario.activo

    def es_admin(self, usuario_id: UUID) -> bool:
        """Verifica si el usuario es administrador."""
        usuario = self.obtener_por_id(id=usuario_id)
        return (
            getattr(getattr(usuario, "rol", None), "nombre_rol", "").lower() == "admin"
            or getattr(getattr(usuario, "rol", None), "nombre_rol", "").lower()
            == "administrador"
        )


usuario = UsuarioCRUD(Usuario)
