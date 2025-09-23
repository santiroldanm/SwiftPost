from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from sqlalchemy.orm import Session

from entities.sede import Sede, SedeCreate, SedeUpdate
from .base_crud import CRUDBase


class SedeCRUD(CRUDBase[Sede, SedeCreate, SedeUpdate]):
    """Operaciones CRUD para Sede."""
    
    def get_multi(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[Sede]:
        """
        Obtiene múltiples sedes con paginación.

        Args:
            db: Sesión de base de datos
            skip: Número de registros a omitir (para paginación)
            limit: Número máximo de registros a devolver

        Returns:
            Lista de sedes
        """
        return db.query(self.modelo).offset(skip).limit(limit).all()
    
    def get_by_nombre(self, db: Session, nombre: str) -> Optional[Sede]:
        """Obtiene una sede por nombre."""
        return db.query(Sede).filter(Sede.nombre == nombre).first()
    
    def get_by_ciudad(self, db: Session, ciudad: str, skip: int = 0, limit: int = 100) -> List[Sede]:
        """Obtiene sedes por ciudad."""
        return (
            db.query(Sede)
            .filter(Sede.ciudad == ciudad)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_activas(self, db: Session, skip: int = 0, limit: int = 100) -> List[Sede]:
        """Obtiene sedes activas."""
        return (
            db.query(Sede)
            .filter(Sede.activo == True)  # noqa: E712
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def create(self, db: Session, *, obj_in: SedeCreate, creado_por: UUID) -> Sede:
        """Crea una nueva sede."""
        db_obj = Sede(
            **obj_in.dict(),
            creado_por=creado_por
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(
        self,
        db: Session,
        *,
        db_obj: Sede,
        obj_in: Union[SedeUpdate, Dict[str, Any]],
        actualizado_por: UUID
    ) -> Sede:
        """Actualiza una sede."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        update_data["actualizado_por"] = actualizado_por
        return super().update(db, db_obj=db_obj, obj_in=update_data)
    
    def deactivate(self, db: Session, *, id: UUID, actualizado_por: UUID) -> Sede:
        """Desactiva una sede."""
        sede = self.get(db, id)
        if sede:
            sede.activa = False
            sede.actualizado_por = actualizado_por
            db.add(sede)
            db.commit()
            db.refresh(sede)
        return sede


sede = SedeCRUD(Sede)
