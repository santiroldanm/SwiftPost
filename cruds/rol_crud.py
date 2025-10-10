from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from uuid import UUID, uuid4
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from entities.rol import Rol
from schemas.rol_schema import RolCreate, RolUpdate
from .base_crud import CRUDBase


class RolCRUD(CRUDBase[Rol, RolCreate, RolUpdate]):
    """
    Operaciones CRUD para la entidad Rol.
    Proporciona métodos para crear, leer, actualizar y eliminar roles,
    así como operaciones específicas para buscar roles por nombre.
    """

    def __init__(self, db: Session):
        super().__init__(Rol, db)
        self.db = db
        self.model = Rol

    def obtener_rol_por_nombre(
        self,
        nombre: str,
        exacto: bool = True,
        case_sensitive: bool = False,
    ) -> Optional[Rol]:
        """
        Obtiene un rol por su nombre.
        Args:
            db: Sesión de base de datos
            nombre: Nombre del rol a buscar
            exacto: Si es True, busca coincidencia exacta. Si es False, busca coincidencias parciales
            case_sensitive: Si es True, la búsqueda distingue entre mayúsculas y minúsculas
        Returns:
            El rol encontrado o None si no existe
        Raises:
            ValueError: Si el nombre está vacío
        """
        if not nombre or not isinstance(nombre, str):
            logger.warning("Se intentó buscar un rol con un nombre inválido")
            return None
        query = self.db.query(self.model)
        if exacto:
            if case_sensitive:
                query = query.filter(self.model.nombre_rol == nombre)
            else:
                query = query.filter(self.model.nombre_rol.ilike(nombre))
        else:
            if case_sensitive:
                query = query.filter(self.model.nombre_rol.contains(nombre))
            else:
                query = query.filter(self.model.nombre_rol.ilike(f"%{nombre}%"))
        return query.first()

    def obtener_por_id(self, id_rol: Union[str, UUID]) -> Optional[Rol]:
        """
        Obtiene un rol por su ID.
        Args:
            id_rol: ID del rol a buscar (como string o UUID)
        Returns:
            El rol encontrado o None si no existe
        """
        try:
            if isinstance(id_rol, UUID):
                id_rol = str(id_rol)
            return self.db.query(Rol).filter(Rol.id_rol == id_rol).first()
        except Exception as e:
            print(f"Error al obtener rol por ID: {e}")
            return None

    def obtener_roles(self, skip: int = 0, limit: int = 100) -> List[Rol]:
        """
        Obtiene todos los roles con paginación.
        Args:
            skip: Número de registros a omitir
            limit: Número máximo de registros a devolver
        Returns:
            Lista de roles
        """
        try:
            return self.db.query(Rol).offset(skip).limit(limit).all()
        except Exception as e:
            print(f"Error al obtener roles: {e}")
            return []

    def crear_rol(
        self,
        datos_entrada: Union[RolCreate, Dict[str, Any]],
        usuario_id: Union[str, UUID],
    ) -> Optional[Rol]:
        """
        Crea un nuevo rol.
        Args:
            datos_entrada: Datos del rol a crear
            usuario_id: ID del usuario que crea el rol
        Returns:
            El rol creado o None si hubo un error
        """
        try:
            if not isinstance(datos_entrada, dict):
                datos_entrada = (
                    datos_entrada.model_dump()
                    if hasattr(datos_entrada, "model_dump")
                    else datos_entrada.dict()
                )

            nombre = str(datos_entrada.get("nombre_rol", "")).strip()
            if not nombre:
                raise ValueError("El nombre del rol es requerido")

            if self.obtener_rol_por_nombre(nombre):
                raise ValueError(f"Ya existe un rol con el nombre: {nombre}")

            db_obj = Rol(
                id_rol=str(uuid4()),
                nombre_rol=nombre,
                activo=True,
                fecha_creacion=datetime.now(),
            )
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            return db_obj
        except Exception as e:
            self.db.rollback()
            print(f"Error al crear rol: {e}")
            raise

    def actualizar_rol(
        self,
        rol_db: Rol,
        datos_actualizacion: Dict[str, Any],
        actualizado_por: Union[str, UUID],
    ) -> Rol:
        """
        Actualiza un rol existente.
        Args:
            rol_db: Rol existente a actualizar
            datos_actualizacion: Datos para actualizar
            actualizado_por: ID del usuario que actualiza
        Returns:
            El rol actualizado
        """
        try:
            if (
                "nombre_rol" in datos_actualizacion
                and datos_actualizacion["nombre_rol"]
            ):
                nuevo_nombre = datos_actualizacion["nombre_rol"]
                if nuevo_nombre.lower() != rol_db.nombre_rol.lower():
                    if self.obtener_rol_por_nombre(nuevo_nombre):
                        raise ValueError(
                            f"Ya existe un rol con el nombre: {nuevo_nombre}"
                        )

            for campo, valor in datos_actualizacion.items():
                if hasattr(rol_db, campo):
                    setattr(rol_db, campo, valor)

            rol_db.fecha_actualizacion = datetime.now()
            self.db.add(rol_db)
            self.db.commit()
            self.db.refresh(rol_db)
            return rol_db
        except Exception as e:
            self.db.rollback()
            print(f"Error al actualizar rol: {e}")
            raise

    def eliminar_rol(self, id_rol: Union[str, UUID]) -> bool:
        """
        Elimina un rol por su ID (soft delete).
        Args:
            id_rol: ID del rol a eliminar
        Returns:
            True si se eliminó correctamente, False si no se encontró el rol
        """
        try:
            rol = self.obtener_por_id(id_rol)
            if not rol:
                return False

            roles_sistema = ["administrador", "empleado", "cliente"]
            if rol.nombre_rol.lower() in roles_sistema:
                raise ValueError("No se puede eliminar un rol de sistema")

            rol.activo = False
            rol.fecha_actualizacion = datetime.now()
            self.db.add(rol)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"Error al eliminar rol: {e}")
            return False

    def obtener_activos(self, skip: int = 0, limit: int = 100) -> List[Rol]:
        """
        Obtiene una lista de roles activos.
        Args:
            skip: Número de registros a omitir
            limit: Número máximo de registros a devolver
        Returns:
            Lista de roles activos
        """
        try:
            return (
                self.db.query(Rol)
                .filter(Rol.activo == True)
                .offset(skip)
                .limit(limit)
                .all()
            )
        except Exception as e:
            print(f"Error al obtener roles activos: {e}")
            return []
