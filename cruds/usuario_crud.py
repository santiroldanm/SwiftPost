from typing import Any, Dict, List, Optional, Union, Type
from uuid import UUID
from auth.security import Security
from sqlalchemy.orm import Session
from entities.usuario import Usuario, UsuarioCreate, UsuarioUpdate
from .base_crud import CRUDBase
from entities.rol import Rol


class UsuarioCRUD(CRUDBase[Usuario, UsuarioCreate, UsuarioUpdate]):
    """Operaciones CRUD para la entidad Usuario."""

    def __init__(self, db: Session):
        super().__init__(Usuario)
        self.db = db

    def obtener_por_nombre_usuario(self, nombre_usuario: str) -> Optional[Usuario]:
        """Obtiene un usuario por su nombre de usuario."""
        return (
            self.db.query(Usuario)
            .filter(Usuario.nombre_usuario == nombre_usuario)
            .first()
        )

    def obtener_por_correo(self, correo: str) -> Optional[Usuario]:
        """Obtiene un usuario por su correo electrónico."""
        return self.db.query(Usuario).filter(Usuario.correo == correo).first()

    def obtener_por_rol(
        self, id_rol: UUID, desde: int = 0, limite: int = 100
    ) -> List[Usuario]:
        """Obtiene usuarios por rol con paginación."""
        return (
            self.db.query(Usuario)
            .filter(Usuario.id_rol == id_rol)
            .offset(desde)
            .limit(limite)
            .all()
        )

    def obtener_activos(self, desde: int = 0, limite: int = 100) -> List[Usuario]:
        """Obtiene usuarios activos con paginación."""
        return (
            self.db.query(Usuario)
            .filter(Usuario.activo == True)  # noqa: E712
            .offset(desde)
            .limit(limite)
            .all()
        )

    def obtener_por_id(self, id_usuario: UUID) -> Optional[Usuario]:
        return self.db.query(Usuario).filter(Usuario.id_usuario == id_usuario).first()

    def autenticar(self, nombre_usuario: str, contrasena: str) -> Optional[Usuario]:
        """
        Autentica un usuario con su nombre de usuario y contraseña.

        Args:
            nombre_usuario: Nombre de usuario
            contrasena: Contraseña en texto plano

        Returns:
            Usuario: Si las credenciales son válidas
            None: Si la autenticación falla
        """
        # Cargar el usuario con la relación de rol
        usuario = (
            self.db.query(Usuario)
            .filter(Usuario.nombre_usuario == nombre_usuario)
            .first()
        )

        if not usuario:
            return None

        if not Security.verificar_contrasena(contrasena, usuario.password):
            return None

        # Forzar la carga del rol si no está cargado
        if not hasattr(usuario, "_rol_cargado") or not usuario._rol_cargado:
            self.db.refresh(usuario)

        return usuario

    def crear(self, *, datos_entrada: UsuarioCreate, creado_por: UUID) -> Usuario:
        """Crea un nuevo usuario en el sistema."""
        # Extraer los datos del usuario
        datos_usuario = datos_entrada.model_dump()

        # Crear el objeto de usuario con la contraseña en texto plano
        db_obj = Usuario(**datos_usuario, creado_por=creado_por)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def actualizar(
        self,
        *,
        db_obj: Usuario,
        datos_actualizacion: Union[UsuarioUpdate, Dict[str, Any]],
        actualizado_por: UUID,
    ) -> Usuario:
        """Actualiza la información de un usuario existente."""
        if isinstance(datos_actualizacion, dict):
            datos_actualizados = datos_actualizacion
        else:
            datos_actualizados = datos_actualizacion.dict(exclude_unset=True)

        if "contrasena" in datos_actualizados:
            datos_actualizados["contrasena"] = Usuario.generar_hash_contrasena(
                datos_actualizados["contrasena"]
            )

        datos_actualizados["actualizado_por"] = actualizado_por
        return super().actualizar(
            objeto_db=db_obj, datos_actualizacion=datos_actualizados
        )

    def actualizar_contrasena(
        self, *, db_obj: Usuario, nueva_contrasena: str, actualizado_por: UUID
    ) -> Usuario:
        """Actualiza la contraseña de un usuario."""
        db_obj.contrasena = Usuario.generar_hash_contrasena(nueva_contrasena)
        db_obj.actualizado_por = actualizado_por
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def desactivar(self, *, id: UUID, actualizado_por: UUID) -> Usuario:
        """Desactiva un usuario en el sistema."""
        usuario = self.obtener_por_id(id)
        if usuario:
            usuario.activo = False
            usuario.actualizado_por = actualizado_por
            self.db.add(usuario)
            self.db.commit()
            self.db.refresh(usuario)
        return usuario

    def esta_activo(self, usuario: Usuario) -> bool:
        """Verifica si un usuario está activo."""
        return usuario.activo

    def es_admin(self, usuario: Usuario) -> bool:
        """
        Verifica si un usuario es administrador.

        Args:
            usuario: Instancia del usuario a verificar

        Returns:
            bool: True si el usuario es administrador, False en caso contrario
        """
        if not usuario.rol:
            return False

        rol = self.db.query(Rol).filter(Rol.id_rol == usuario.rol).first()

        if not rol or not rol.nombre_rol:
            return False

        return rol.nombre_rol.lower() == "administrador"
