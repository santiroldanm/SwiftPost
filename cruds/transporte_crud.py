from typing import Any, Dict, List, Optional, Union
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from entities.transporte import Transporte, TransporteCreate, TransporteUpdate
from .base_crud import CRUDBase


class TransporteCRUD(CRUDBase[Transporte, TransporteCreate, TransporteUpdate]):
    """Clase para operaciones CRUD de Transporte."""

    def __init__(self, db: Session):
        super().__init__(Transporte, db)
        self.db = db

    def obtener_por_id(self, id_transporte: UUID) -> Optional[Transporte]:
        """
        Obtiene un transporte por su ID.

        Args:
            id_transporte: ID del transporte a buscar

        Returns:
            Optional[Transporte]: El transporte encontrado o None si no existe
        """
        try:
            if not id_transporte:
                return None
            return (
                self.db.query(Transporte)
                .filter(Transporte.id_transporte == id_transporte)
                .first()
            )
        except Exception as e:
            print(f"Error al obtener transporte por ID {id_transporte}: {str(e)}")
            return None

    def obtener_por_placa(self, placa: str) -> Optional[Transporte]:
        """
        Busca un transporte por su placa.
        Args:
            placa: Número de placa del vehículo
        Returns:
            Transporte: El transporte encontrado o None si no existe
        """
        return (
            self.db.query(Transporte).filter(Transporte.placa == placa.upper()).first()
        )

    def obtener_por_estado(
        self, estado: str, skip: int = 0, limit: int = 100
    ) -> List[Transporte]:
        """
        Obtiene una lista de transportes filtrados por estado.
        Args:
            estado: Estado del transporte a filtrar
            skip: Número de registros a omitir (paginación)
            limit: Número máximo de registros a devolver
        Returns:
            List[Transporte]: Lista de transportes que coinciden con el estado
        """
        return (
            self.db.query(Transporte)
            .filter(Transporte.estado == estado)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def obtener_por_tipo(
        self, tipo: str, skip: int = 0, limit: int = 100
    ) -> List[Transporte]:
        """
        Obtiene una lista de transportes filtrados por tipo.
        Args:
            tipo: Tipo de transporte a filtrar
            skip: Número de registros a omitir (paginación)
            limit: Número máximo de registros a devolver
        Returns:
            List[Transporte]: Lista de transportes que coinciden con el tipo
        """
        return (
            self.db.query(Transporte)
            .filter(Transporte.tipo_vehiculo == tipo.capitalize())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def obtener_activos(self, skip: int = 0, limit: int = 100) -> List[Transporte]:
        """
        Obtiene una lista de transportes activos.
        Args:
            skip: Número de registros a omitir (paginación)
            skip: Número de registros a omitir (paginación)
            limit: Número máximo de registros a devolver
        Returns:
            List[Transporte]: Lista de transportes activos
        """
        return (
            self.db.query(Transporte)
            .filter(Transporte.activo == True)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def crear(self, *, obj_in: TransporteCreate, creado_por: UUID) -> Transporte:
        """
        Crea un nuevo registro de transporte.
        Args:
            obj_in: Datos del transporte a crear
            creado_por: ID del usuario que realiza la creación
        Returns:
            Transporte: El transporte recién creado
        """
        db_obj = Transporte(**obj_in.model_dump(), creado_por=creado_por)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def actualizar_estado(
        self, *, db_obj: Transporte, nuevo_estado: str, actualizado_por: UUID
    ) -> Transporte:
        """
        Actualiza el estado de un transporte existente.
        Args:
            db_obj: Instancia del transporte a actualizar
            nuevo_estado: Nuevo estado del transporte
            actualizado_por: ID del usuario que realiza la actualización
        Returns:
            Transporte: El transporte actualizado
        """
        db_obj.estado = nuevo_estado
        db_obj.actualizado_por = actualizado_por
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def actualizar(
        self,
        *,
        db_obj: Transporte,
        obj_in: Union[TransporteUpdate, Dict[str, Any]],
        actualizado_por: UUID,
    ) -> Optional[Transporte]:
        """
        Actualiza los datos de un transporte existente.

        Args:
            db_obj: Instancia del transporte a actualizar
            obj_in: Datos a actualizar
            actualizado_por: ID del usuario que realiza la actualización

        Returns:
            Optional[Transporte]: El transporte actualizado o None si hay error
        """
        try:
            if isinstance(obj_in, dict):
                update_data = obj_in
            else:
                update_data = obj_in.model_dump(exclude_unset=True)

            if "placa" in update_data:
                del update_data["placa"]

            for campo, valor in update_data.items():
                if hasattr(db_obj, campo):
                    setattr(db_obj, campo, valor)

            db_obj.actualizado_por = str(actualizado_por)
            db_obj.fecha_actualizacion = datetime.now()

            self.db.commit()
            self.db.refresh(db_obj)
            return db_obj

        except ValueError as e:
            self.db.rollback()
            print(f" Error de validación: {e}")
            return None
        except Exception as e:
            self.db.rollback()
            print(f" Error al actualizar transporte: {e}")
            import traceback

            traceback.print_exc()
            return None

    def desactivar_transporte(
        self, *, id_transporte: UUID, actualizado_por: UUID
    ) -> bool:
        """
        Desactiva un transporte (soft delete).

        Args:
            id_transporte: ID del transporte a desactivar
            actualizado_por: ID del usuario que realiza la desactivación

        Returns:
            bool: True si se desactivó correctamente, False en caso contrario
        """
        try:
            transporte = self.obtener_por_id(id_transporte)

            if not transporte:
                print(f" Error: Transporte no encontrado con ID: {id_transporte}")
                return False

            if not transporte.activo:
                print(f" Advertencia: El transporte ya está inactivo")
                return False

            transporte.activo = False
            transporte.actualizado_por = str(actualizado_por)
            transporte.fecha_actualizacion = datetime.now()

            self.db.commit()
            return True

        except Exception as e:
            self.db.rollback()
            print(f" Error al desactivar transporte: {e}")
            import traceback

            traceback.print_exc()
            return False
