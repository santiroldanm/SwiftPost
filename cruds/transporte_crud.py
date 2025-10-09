from typing import Any, Dict, List, Optional, Union
from uuid import UUID
from sqlalchemy.orm import Session
from entities.transporte import Transporte, TransporteCreate, TransporteUpdate
from .base_crud import CRUDBase


class TransporteCRUD(CRUDBase[Transporte, TransporteCreate, TransporteUpdate]):
    """Clase para operaciones CRUD de Transporte."""

    def __init__(self, db: Session):
        self.db = db
        super().__init__(Transporte)

    def obtener_por_placa(self, placa: str) -> Optional[Transporte]:
        """
        Busca un transporte por su placa.
        Args:
            placa: Número de placa del vehículo
        Returns:
            Transporte: El transporte encontrado o None si no existe
        """
        return self.db.query(Transporte).filter(Transporte.placa == placa).first()

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
            .filter(Transporte.tipo == tipo)
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
        actualizado_por: UUID
    ) -> Transporte:
        """
        Actualiza los datos de un transporte existente.
        Args:
            db_obj: Instancia del transporte a actualizar
            obj_in: Datos a actualizar (puede ser un diccionario o instancia de TransporteUpdate)
            actualizado_por: ID del usuario que realiza la actualización
        Returns:
            Transporte: El transporte actualizado
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        update_data["actualizado_por"] = actualizado_por
        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def desactivar_transporte(
        self, db: Session, *, id: UUID, actualizado_por: UUID
    ) -> Transporte:
        """
        Desactiva un transporte estableciendo su estado activo como falso.
        Args:
            db: Sesión de base de datos
            id: ID del transporte a desactivar
            actualizado_por: ID del usuario que realiza la desactivación
        Returns:
            Transporte: El transporte desactivado
        """
        transporte = self.get(db, id)
        if transporte:
            transporte.activo = False
            transporte.actualizado_por = actualizado_por
            db.add(transporte)
            db.commit()
            db.refresh(transporte)
        return transporte


transporte = TransporteCRUD(Transporte)
