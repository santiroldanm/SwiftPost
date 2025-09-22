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

    def crear(self, *, datos_entrada: UsuarioCreate) -> Optional[Usuario]:
        """Crea un nuevo usuario en el sistema.

        Args:
            datos_entrada: Datos del usuario a crear

        Returns:
            Usuario: El usuario creado
            None: Si ocurre un error al crear el usuario
        """
        print("\n[DEBUG] Iniciando creación de usuario...")
        try:
            # Extraer los datos del usuario
            datos_usuario = datos_entrada.model_dump()
            print(f"[DEBUG] Datos de entrada: {datos_usuario}")

            # Verificar campos requeridos
            campos_requeridos = [
                "nombre_usuario",
                "password",
                "primer_nombre",
                "primer_apellido",
                "rol",
            ]
            for campo in campos_requeridos:
                if campo not in datos_usuario or not datos_usuario[campo]:
                    print(f"[ERROR] Campo requerido faltante o vacío: {campo}")
                    return None

            # Hashear la contraseña
            if "password" in datos_usuario and datos_usuario["password"]:
                print("[DEBUG] Hasheando contraseña...")
                try:
                    datos_usuario["password"] = Security.hash_password(
                        datos_usuario["password"]
                    )
                    print("[DEBUG] Contraseña hasheada correctamente")
                except Exception as hash_error:
                    print(f"[ERROR] Error al hashear la contraseña: {str(hash_error)}")
                    return None

            # Crear el objeto de usuario
            print("[DEBUG] Creando objeto Usuario...")
            try:
                db_obj = Usuario(**datos_usuario)
                print(f"[DEBUG] Objeto Usuario creado: {db_obj}")
            except Exception as create_error:
                print(f"[ERROR] Error al crear objeto Usuario: {str(create_error)}")
                return None

            # Guardar en la base de datos
            try:
                print("[DEBUG] Guardando en la base de datos...")
                self.db.add(db_obj)
                self.db.commit()
                self.db.refresh(db_obj)
                print(
                    f"[DEBUG] Usuario guardado exitosamente con ID: {db_obj.id_usuario}"
                )
                return db_obj
            except Exception as db_error:
                self.db.rollback()
                print(f"[ERROR] Error al guardar en la base de datos: {str(db_error)}")
                return None

        except Exception as e:
            self.db.rollback()
            print(f"[ERROR] Error inesperado al crear usuario: {str(e)}")
            import traceback

            traceback.print_exc()
            return None

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

    def eliminar(self, usuario_id: UUID) -> bool:
        """
        Eliminar un usuario

        Args:
            usuario_id: UUID del usuario

        Returns:
            True si se eliminó, False si no existe
        """
        usuario = self.obtener_por_id(usuario_id)
        if usuario:
            self.db.delete(usuario)
            self.db.commit()
            return True
        return False

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

    def desactivar(self, db: Session, *, id: UUID, actualizado_por: UUID) -> Usuario:
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

    def es_empleado(self, usuario: Usuario) -> bool:
        """
        Verifica si un usuario es empleado.

        Args:
            usuario: Instancia del usuario a verificar

        Returns:
            bool: True si el usuario es empleado, False en caso contrario
        """
        if not usuario.rol:
            return False

        rol = self.db.query(Rol).filter(Rol.id_rol == usuario.rol).first()

        if not rol or not rol.nombre_rol:
            return False

        return rol.nombre_rol.lower() == "empleado"

    def es_cliente(self, usuario: Usuario) -> bool:
        """
        Verifica si un usuario es cliente.

        Args:
            usuario: Instancia del usuario a verificar

        Returns:
            bool: True si el usuario es cliente, False en caso contrario
        """
        if not usuario.rol:
            return False

        rol = self.db.query(Rol).filter(Rol.id_rol == usuario.rol).first()

        if not rol or not rol.nombre_rol:
            return False

        return rol.nombre_rol.lower() == "cliente"
