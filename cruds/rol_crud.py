from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import UUID

from sqlalchemy.orm import Session

from entities.rol import Rol, RolCreate, RolUpdate
from .base_crud import CRUDBase


class RolCRUD(CRUDBase[Rol, RolCreate, RolUpdate]):
    """Operaciones CRUD para la entidad Rol con validaciones."""

    def __init__(self):
        super().__init__(Rol)
        # Configuraciones específicas para Rol
        self.longitud_minima_nombre = 3
        self.longitud_maxima_nombre = 50
        self.roles_sistema = ["administrador", "coordinador", "mensajero", "cliente"]

    def _validar_datos_rol(self, datos: Dict[str, Any]) -> bool:
        """Valida los datos básicos de un rol."""
        # Validar nombre
        nombre = datos.get("nombre", "").strip().lower()
        if not nombre or not (
            self.longitud_minima_nombre <= len(nombre) <= self.longitud_maxima_nombre
        ):
            return False

        # Validar descripción si está presente
        if "descripcion" in datos and len(datos["descripcion"]) > 500:
            return False

        # Validar permisos si están presentes
        if "permisos" in datos and not isinstance(datos["permisos"], list):
            return False

        return True

    def obtener_por_nombre(self, db: Session, nombre: str) -> Optional[Rol]:
        """
        Obtiene un rol por su nombre (case insensitive).

        Args:
            db: Sesión de base de datos
            nombre: Nombre del rol a buscar

        Returns:
            El rol encontrado o None si no existe
        """
        nombre = nombre.strip().lower()
        if not nombre:
            return None

        # Búsqueda case-insensitive por nombre_rol, priorizando roles activos
        consulta = db.query(Rol).filter(Rol.nombre_rol.ilike(f"%{nombre}%"))
        consulta = consulta.filter(Rol.activo == True)
        return consulta.first()

    def obtener_activos(
        self, db: Session, saltar: int = 0, limite: int = 100
    ) -> Tuple[List[Rol], int]:
        """
        Obtiene roles activos con paginación.

        Args:
            db: Sesión de base de datos
            saltar: Número de registros a omitir (para paginación)
            limite: Número máximo de registros a devolver

        Returns:
            Tupla con (lista de roles activos, total de registros)
        """
        consulta = db.query(Rol).filter(Rol.activo == True)
        total = consulta.count()
        resultados = consulta.offset(saltar).limit(limite).all()
        return resultados, total

    def obtener_por_permiso(
        self, db: Session, permiso: str, saltar: int = 0, limite: int = 100
    ) -> Tuple[List[Rol], int]:
        """
        Obtiene roles que tienen un permiso específico.

        Args:
            db: Sesión de base de datos
            permiso: Permiso a buscar
            saltar: Número de registros a omitir (para paginación)
            limite: Número máximo de registros a devolver

        Returns:
            Tupla con (lista de roles con el permiso, total de registros)
        """
        if not permiso:
            return [], 0

        consulta = db.query(Rol).filter(
            Rol.activo == True, Rol.permisos.any(permiso)  # type: ignore
        )
        total = consulta.count()
        resultados = consulta.offset(saltar).limit(limite).all()
        return resultados, total

    def crear(
        self, db: Session, *, datos_entrada: RolCreate, creado_por: UUID
    ) -> Optional[Rol]:
        """
        Crea un nuevo rol con validación de datos.

        Args:
            db: Sesión de base de datos
            datos_entrada: Datos para crear el rol
            creado_por: ID del usuario que crea el registro

        Returns:
            El rol creado o None si hay un error
        """
        datos = datos_entrada.dict()

        # Validar datos
        if not self._validar_datos_rol(datos):
            return None

        # Convertir nombre a minúsculas
        datos["nombre"] = datos["nombre"].strip().lower()

        # Verificar duplicados
        if self.obtener_por_nombre(db, datos["nombre"]):
            return None

        # Crear el rol
        try:
            rol = Rol(
                **datos,
                creado_por=creado_por,
                fecha_creacion=datetime.utcnow(),
                activo=True
            )
            db.add(rol)
            db.commit()
            db.refresh(rol)
            return rol
        except Exception:
            db.rollback()
            return None

    def actualizar(
        self,
        db: Session,
        *,
        objeto_db: Rol,
        datos_entrada: Union[RolUpdate, Dict[str, Any]],
        actualizado_por: UUID
    ) -> Optional[Rol]:
        """
        Actualiza un rol existente con validación de datos.

        Args:
            db: Sesión de base de datos
            objeto_db: Objeto de rol a actualizar
            datos_entrada: Datos para actualizar
            actualizado_por: ID del usuario que actualiza el registro

        Returns:
            El rol actualizado o None si hay un error
        """
        if isinstance(datos_entrada, dict):
            datos_actualizados = datos_entrada
        else:
            datos_actualizados = datos_entrada.dict(exclude_unset=True)

        # No permitir modificar el nombre si es un rol de sistema
        if objeto_db.nombre in self.roles_sistema and "nombre" in datos_actualizados:
            del datos_actualizados["nombre"]

        # Validar datos actualizados
        datos_completos = objeto_db.__dict__.copy()
        datos_completos.update(datos_actualizados)

        if not self._validar_datos_rol(datos_completos):
            return None

        # Verificar duplicado de nombre
        if "nombre" in datos_actualizados:
            datos_actualizados["nombre"] = datos_actualizados["nombre"].strip().lower()
            if datos_actualizados[
                "nombre"
            ] != objeto_db.nombre and self.obtener_por_nombre(
                db, datos_actualizados["nombre"]
            ):
                return None

        # Actualizar el rol
        try:
            for campo, valor in datos_actualizados.items():
                if hasattr(objeto_db, campo):
                    setattr(objeto_db, campo, valor)

            objeto_db.actualizado_por = actualizado_por
            objeto_db.fecha_actualizacion = datetime.utcnow()

            db.add(objeto_db)
            db.commit()
            db.refresh(objeto_db)
            return objeto_db
        except Exception:
            db.rollback()
            return None

    def desactivar(self, db: Session, *, id: UUID, actualizado_por: UUID) -> bool:
        """
        Desactiva un rol por su ID.

        Args:
            db: Sesión de base de datos
            id: ID del rol a desactivar
            actualizado_por: ID del usuario que realiza la desactivación

        Returns:
            True si se desactivó correctamente, False en caso contrario
        """
        try:
            rol = self.obtener_por_id(db, id)
            if not rol or not rol.activo or rol.nombre in self.roles_sistema:
                return False

            rol.activo = False
            rol.actualizado_por = actualizado_por
            rol.fecha_actualizacion = datetime.utcnow()

            db.add(rol)
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False


# Instancia única para importar
rol = RolCRUD()
