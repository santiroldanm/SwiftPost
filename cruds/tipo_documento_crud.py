from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from sqlalchemy.orm import Session

from entities.tipo_documento import TipoDocumento, TipoDocumentoCreate, TipoDocumentoUpdate
from .base_crud import CRUDBase


class TipoDocumentoCRUD(CRUDBase[TipoDocumento, TipoDocumentoCreate, TipoDocumentoUpdate]):
    """CRUD operations for TipoDocumento."""
    
    def get_by_nombre(self, db: Session, nombre: str) -> Optional[TipoDocumento]:
        """Get a tipo documento by nombre."""
        return db.query(TipoDocumento).filter(TipoDocumento.nombre == nombre).first()
    
    def get_activos(self, db: Session, skip: int = 0, limit: int = 100) -> List[TipoDocumento]:
        """Get active tipos de documento."""
        return (
            db.query(TipoDocumento)
            .filter(TipoDocumento.activo == True)  # noqa: E712
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def create(self, db: Session, *, obj_in: TipoDocumentoCreate, creado_por: UUID) -> TipoDocumento:
        """Create a new tipo documento."""
        db_obj = TipoDocumento(
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
        db_obj: TipoDocumento,
        obj_in: Union[TipoDocumentoUpdate, Dict[str, Any]],
        actualizado_por: UUID
    ) -> TipoDocumento:
        """Update a tipo documento."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        update_data["actualizado_por"] = actualizado_por
        return super().update(db, db_obj=db_obj, obj_in=update_data)
    
    def deactivate(self, db: Session, *, id: UUID, actualizado_por: UUID) -> TipoDocumento:
        """Deactivate a tipo documento."""
        tipo_documento = self.get(db, id)
        if tipo_documento:
            tipo_documento.activo = False
            tipo_documento.actualizado_por = actualizado_por
            db.add(tipo_documento)
            db.commit()
            db.refresh(tipo_documento)
        return tipo_documento


tipo_documento = TipoDocumentoCRUD(TipoDocumento)
