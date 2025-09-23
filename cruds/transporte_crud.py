from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from sqlalchemy.orm import Session

from entities.transporte import Transporte, TransporteCreate, TransporteUpdate
from .base_crud import CRUDBase


class TransporteCRUD(CRUDBase[Transporte, TransporteCreate, TransporteUpdate]):
    """Operaciones CRUD para Transporte."""
    
    def get_multi(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[Transporte]:
        """
        Obtiene múltiples transportes con paginación.

        Args:
            db: Sesión de base de datos
            skip: Número de registros a omitir (para paginación)
            limit: Número máximo de registros a devolver

        Returns:
            Lista de transportes
        """
        return db.query(self.modelo).offset(skip).limit(limit).all()
    
    def get_by_placa(self, db: Session, placa: str) -> Optional[Transporte]:
        """Obtiene un transporte por placa."""
        return db.query(Transporte).filter(Transporte.placa == placa).first()
    
    def get_by_estado(
        self, db: Session, estado: str, skip: int = 0, limit: int = 100
    ) -> List[Transporte]:
        """Obtiene transportes por estado."""
        return (
            db.query(Transporte)
            .filter(Transporte.estado == estado)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_tipo(
        self, db: Session, tipo: str, skip: int = 0, limit: int = 100
    ) -> List[Transporte]:
        """Obtiene transportes por tipo."""
        return (
            db.query(Transporte)
            .filter(Transporte.tipo == tipo)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_activos(self, db: Session, skip: int = 0, limit: int = 100) -> List[Transporte]:
        """Obtiene transportes activos."""
        return (
            db.query(Transporte)
            .filter(Transporte.activo == True)  # noqa: E712
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def create(self, db: Session, *, obj_in: TransporteCreate, creado_por: UUID) -> Transporte:
        """Crea un nuevo transporte."""
        db_obj = Transporte(
            **obj_in.dict(),
            creado_por=creado_por
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update_estado(
        self,
        db: Session,
        *,
        db_obj: Transporte,
        nuevo_estado: str,
        actualizado_por: UUID
    ) -> Transporte:
        """Actualiza el estado de un transporte."""
        db_obj.estado = nuevo_estado
        db_obj.actualizado_por = actualizado_por
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(
        self,
        db: Session,
        *,
        db_obj: Transporte,
        obj_in: Union[TransporteUpdate, Dict[str, Any]],
        actualizado_por: UUID
    ) -> Transporte:
        """Actualiza un transporte."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        update_data["actualizado_por"] = actualizado_por
        return super().update(db, db_obj=db_obj, obj_in=update_data)
    
    def deactivate(self, db: Session, *, id: UUID, actualizado_por: UUID) -> Transporte:
        """Desactiva un transporte."""
        transporte = self.get(db, id)
        if transporte:
            transporte.activo = False
            transporte.actualizado_por = actualizado_por
            db.add(transporte)
            db.commit()
            db.refresh(transporte)
        return transporte


transporte = TransporteCRUD(Transporte)
