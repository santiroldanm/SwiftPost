from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from sqlalchemy.orm import Session

from entities.sede import Sede, SedeCreate, SedeUpdate
from .base_crud import CRUDBase


class SedeCRUD(CRUDBase[Sede, SedeCreate, SedeUpdate]):
    """Operaciones CRUD para Sede."""
    
    def obtener_por_nombre(self, db: Session, nombre: str) -> Optional[Sede]:
        """Obtiene una sede por nombre."""
        return db.query(Sede).filter(Sede.nombre == nombre).first()
    
    def obtener_por_ciudad(self, db: Session, ciudad: str, saltar: int = 0, limite: int = 100) -> List[Sede]:
        """Obtiene sedes por ciudad."""
        return (
            db.query(Sede)
            .filter(Sede.ciudad == ciudad)
            .offset(saltar)
            .limit(limite)
            .all()
        )
    
    def obtener_activas(self, db: Session, saltar: int = 0, limite: int = 100) -> List[Sede]:
        """Obtiene sedes activas."""
        return (
            db.query(Sede)
            .filter(Sede.activa == True)  # noqa: E712
            .offset(saltar)
            .limit(limite)
            .all()
        )
    
    def crear(self, db: Session, *, datos_entrada: SedeCreate, creado_por: UUID) -> Sede:
        """Crea una nueva sede."""
        db_obj = Sede(
            **datos_entrada.dict(),
            creado_por=creado_por
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def actualizar(
        self,
        db: Session,
        *,
        objeto_db: Sede,
        datos_entrada: Union[SedeUpdate, Dict[str, Any]],
        actualizado_por: UUID
    ) -> Sede:
        """Actualiza una sede."""
        if isinstance(datos_entrada, dict):
            datos_actualizados = datos_entrada
        else:
            datos_actualizados = datos_entrada.dict(exclude_unset=True)
        
        datos_actualizados["actualizado_por"] = actualizado_por
        return super().actualizar(db, objeto_db=objeto_db, datos_entrada=datos_actualizados)
    
    def desactivar(self, db: Session, *, id: UUID, actualizado_por: UUID) -> Sede:
        """Desactiva una sede."""
        sede = self.obtener_por_id(db, id)
        if sede:
            sede.activa = False
            sede.actualizado_por = actualizado_por
            db.add(sede)
            db.commit()
            db.refresh(sede)
        return sede


sede = SedeCRUD(Sede)
