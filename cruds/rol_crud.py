from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from uuid import UUID, uuid4
from sqlalchemy.orm import Session, Query
from sqlalchemy import or_, and_
from sqlalchemy.exc import SQLAlchemyError
import logging
from entities.rol import Rol, RolCreate, RolUpdate, RolBase
from .base_crud import CRUDBase

logger = logging.getLogger(__name__)


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
            return self.db.query(self.model).filter(self.model.id_rol == id_rol).first()
        except (ValueError, AttributeError) as e:
            logger.error(f"ID de rol inválido: {id_rol}")
            return None

    def obtener_todos(
        self, skip: int = 0, limit: int = 100, solo_activos: bool = True
    ) -> List[Rol]:
        """
        Obtiene todos los roles con paginación.
        Args:
            skip: Número de registros a omitir
            limit: Número máximo de registros a devolver
            solo_activos: Si es True, devuelve solo roles activos
        Returns:
            Lista de roles
        """
        query = self.db.query(self.model)
        if solo_activos:
            query = query.filter(self.model.activo == True)
        return query.offset(skip).limit(limit).all()

    def crear(
        self,
        obj_in: Union[RolCreate, Dict[str, Any]],
        creado_por: UUID = None,
    ) -> Optional[Rol]:
        """
        Crea un nuevo rol.
        Args:
            obj_in: Datos del rol a crear (puede ser un diccionario o un objeto RolCreate)
            creado_por: ID del usuario que crea el rol (opcional)
        Returns:
            El rol creado o None si hubo un error
        Raises:
            ValueError: Si ya existe un rol con el mismo nombre o los datos son inválidos
        """
        try:
            if not isinstance(obj_in, dict):
                obj_in = obj_in.dict(exclude_unset=True)
            nombre = str(obj_in.get("nombre_rol", "")).strip().lower()
            if not nombre:
                raise ValueError("El nombre del rol es requerido")
            if self.obtener_por_nombre(nombre):
                raise ValueError(f"Ya existe un rol con el nombre: {nombre}")
            db_obj = self.model(
                id_rol=uuid4(),
                nombre_rol=nombre,
                descripcion=obj_in.get("descripcion", "").strip(),
                activo=bool(obj_in.get("activo", True)),
                fecha_creacion=datetime.utcnow(),
                creado_por=creado_por,
            )
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            logger.info(f"Rol creado exitosamente: {db_obj.id_rol}")
            return db_obj
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error al crear el rol: {str(e)}", exc_info=True)
            raise ValueError("Error al crear el rol en la base de datos")
        except Exception as e:
            db.rollback()
            logger.error(f"Error inesperado al crear rol: {str(e)}", exc_info=True)
            raise

    def actualizar(self, *, db_obj: Rol, obj_in: RolUpdate) -> Rol:
        """
        Actualiza un rol existente.
        Args:
            db_obj: Rol existente a actualizar
            obj_in: Datos para actualizar el rol
        Returns:
            El rol actualizado
        Raises:
            ValueError: Si ya existe otro rol con el mismo nombre
        """
        update_data = obj_in.dict(exclude_unset=True)
        if "nombre_rol" in update_data and update_data["nombre_rol"]:
            nuevo_nombre = update_data["nombre_rol"].lower()
            if nuevo_nombre != db_obj.nombre_rol.lower() and self.obtener_por_nombre(
                nuevo_nombre
            ):
                raise ValueError(f"Ya existe un rol con el nombre: {nuevo_nombre}")
            update_data["nombre_rol"] = nuevo_nombre
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db_obj.fecha_actualizacion = datetime.utcnow()
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def eliminar(self, db: Session, id_rol: str) -> bool:
        """
        Elimina un rol por su ID.
        Args:
            db: Sesión de base de datos
            id_rol: ID del rol a eliminar
        Returns:
            True si se eliminó correctamente, False si no se encontró el rol
        Raises:
            ValueError: Si el rol está asignado a usuarios o es un rol de sistema
        """
        rol = self.obtener_por_id(id_rol)
        if not rol:
            return False
        roles_sistema = ["administrador", "empleado", "cliente"]
        if rol.nombre_rol.lower() in roles_sistema:
            raise ValueError("No se puede eliminar un rol de sistema")
        if hasattr(rol, "usuarios") and rol.usuarios and len(rol.usuarios) > 0:
            raise ValueError("No se puede eliminar un rol que está asignado a usuarios")
        db.delete(rol)
        db.commit()
        return True

    def obtener_activos(self, skip: int = 0, limit: int = 100) -> List[Rol]:
        """
        Obtiene una lista de roles activos.
        Args:
            skip: Número de registros a omitir (paginación)
            limit: Número máximo de registros a devolver
        Returns:
            Lista de roles activos
        """
        return (
            self.db.query(self.model)
            .filter(self.model.activo == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def obtener_por_permiso(
        self, permiso: str, skip: int = 0, limit: int = 100
    ) -> tuple[List[Rol], int]:
        """
        Obtiene roles que tienen un permiso específico.
        Args:
            permiso: Permiso a buscar
            skip: Número de registros a omitir (para paginación)
            limit: Número máximo de registros a devolver
        Returns:
            Tupla con (lista de roles con el permiso, total de registros)
        """
        if not permiso:
            return [], 0
        consulta = self.db.query(self.model).filter(self.model.activo == True)
        if hasattr(self.model, "permisos"):
            consulta = consulta.filter(self.model.permisos.any(permiso))
        total = consulta.count()
        resultados = consulta.offset(skip).limit(limit).all()
        return resultados, total
