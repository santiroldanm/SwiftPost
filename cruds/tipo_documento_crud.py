from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from sqlalchemy.orm import Session

from entities.tipo_documento import TipoDocumento, TipoDocumentoCreate, TipoDocumentoUpdate
from .base_crud import CRUDBase


class TipoDocumentoCRUD(CRUDBase[TipoDocumento, TipoDocumentoCreate, TipoDocumentoUpdate]):
    """Operaciones CRUD para TipoDocumento."""
    
    def get_by_nombre(self, db: Session, nombre: str) -> Optional[TipoDocumento]:
        """Obtiene un tipo de documento por nombre."""
        return db.query(TipoDocumento).filter(TipoDocumento.nombre == nombre).first()
    
    def get_activos(self, db: Session, skip: int = 0, limit: int = 100) -> List[TipoDocumento]:
        """Obtiene tipos de documento activos."""
        print("\n=== DEBUG: Iniciando get_activos ===")
        print(f"Tipo de db: {type(db)}")
        
        # Verificar si la sesión es válida
        try:
            # Hacer una consulta simple para verificar la conexión
            test = db.query(TipoDocumento).first()
            print(f"Test query result: {test}")
        except Exception as e:
            print(f"Error al ejecutar consulta de prueba: {e}")
            return []
        
        # Obtener los tipos de documento activos
        try:
            tipos = db.query(TipoDocumento)\
                .filter(TipoDocumento.activo == True)\
                .offset(skip)\
                .limit(limit)\
                .all()
            
            print(f"=== DEBUG: Tipos de documento encontrados: {len(tipos)} ===")
            for i, t in enumerate(tipos, 1):
                print(f"{i}. ID: {t.id_tipo_documento}, Nombre: {t.nombre}, Código: {t.codigo}")
            
            return tipos
        except Exception as e:
            print(f"Error en get_activos: {e}")
            return []
    
    def create(self, db: Session, *, obj_in: TipoDocumentoCreate, creado_por: UUID) -> TipoDocumento:
        """Crea un nuevo tipo de documento."""
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
        """Actualiza un tipo de documento."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        update_data["actualizado_por"] = actualizado_por
        return super().update(db, db_obj=db_obj, obj_in=update_data)
    
    def deactivate(self, db: Session, *, id: UUID, actualizado_por: UUID) -> TipoDocumento:
        """Desactiva un tipo de documento."""
        tipo_documento = self.get(db, id)
        if tipo_documento:
            tipo_documento.activo = False
            tipo_documento.actualizado_por = actualizado_por
            db.add(tipo_documento)
            db.commit()
            db.refresh(tipo_documento)
        return tipo_documento


tipo_documento = TipoDocumentoCRUD(TipoDocumento)
