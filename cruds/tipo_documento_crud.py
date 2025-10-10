from typing import Any, Dict, List, Optional, Union
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from entities.tipo_documento import TipoDocumento
from schemas.tipo_documento_schema import TipoDocumentoCreate, TipoDocumentoUpdate
from .base_crud import CRUDBase


class TipoDocumentoCRUD(
    CRUDBase[TipoDocumento, TipoDocumentoCreate, TipoDocumentoUpdate]
):
    """Operaciones CRUD para TipoDocumento."""

    def __init__(self, db: Session):
        super().__init__(TipoDocumento, db)
        self.db = db

    def obtener_por_id(
        self, id_tipo_documento: Union[str, UUID]
    ) -> Optional[TipoDocumento]:
        """
        Obtiene un tipo de documento por su ID.
        Args:
            id_tipo_documento: ID del tipo de documento (UUID)
        Returns:
            El tipo de documento encontrado o None si no existe
        """
        try:
            if not id_tipo_documento:
                return None
            return (
                self.db.query(TipoDocumento)
                .filter(TipoDocumento.id_tipo_documento == id_tipo_documento)
                .first()
            )
        except Exception as e:
            print(f"Error al obtener tipo de documento por ID: {e}")
            return None

    def obtener_por_nombre(self, nombre: str) -> Optional[TipoDocumento]:
        """Obtiene un tipo de documento por nombre."""
        try:
            return (
                self.db.query(TipoDocumento)
                .filter(func.lower(TipoDocumento.nombre) == nombre.lower())
                .first()
            )
        except Exception as e:
            print(f"Error al obtener tipo de documento por nombre: {e}")
            return None

    def obtener_por_codigo(self, codigo: str) -> Optional[TipoDocumento]:
        """Obtiene un tipo de documento por código."""
        try:
            return (
                self.db.query(TipoDocumento)
                .filter(func.lower(TipoDocumento.codigo) == codigo.lower())
                .first()
            )
        except Exception as e:
            print(f"Error al obtener tipo de documento por código: {e}")
            return None

    def obtener_todos(self, skip: int = 0, limit: int = 100) -> List[TipoDocumento]:
        """Obtiene todos los tipos de documento."""
        try:
            return self.db.query(TipoDocumento).offset(skip).limit(limit).all()
        except Exception as e:
            print(f"Error al obtener tipos de documento: {e}")
            return []

    def obtener_activos(self, skip: int = 0, limit: int = 100) -> List[TipoDocumento]:
        """Obtiene tipos de documento activos."""
        try:
            return (
                self.db.query(TipoDocumento)
                .filter(TipoDocumento.activo == True)
                .offset(skip)
                .limit(limit)
                .all()
            )
        except Exception as e:
            print(f"Error al obtener tipos de documento activos: {e}")
            return []

    def crear_tipo_documento(
        self,
        datos_entrada: Union[TipoDocumentoCreate, Dict[str, Any]],
        usuario_id: Union[str, UUID],
    ) -> Optional[TipoDocumento]:
        """Crea un nuevo tipo de documento."""
        try:
            if not isinstance(datos_entrada, dict):
                datos_entrada = (
                    datos_entrada.model_dump()
                    if hasattr(datos_entrada, "model_dump")
                    else datos_entrada.dict()
                )

            db_obj = TipoDocumento(
                **datos_entrada,
                creado_por=str(usuario_id),
                actualizado_por=str(usuario_id),
                fecha_creacion=datetime.now(),
                activo=True,
            )
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            return db_obj
        except Exception as e:
            self.db.rollback()
            print(f"Error al crear tipo de documento: {e}")
            raise

    def actualizar_tipo_documento(
        self,
        tipo_db: TipoDocumento,
        datos_actualizacion: Dict[str, Any],
        actualizado_por: Union[str, UUID],
    ) -> Optional[TipoDocumento]:
        """Actualiza un tipo de documento."""
        try:
            for campo, valor in datos_actualizacion.items():
                if hasattr(tipo_db, campo):
                    setattr(tipo_db, campo, valor)

            tipo_db.actualizado_por = str(actualizado_por)
            tipo_db.fecha_actualizacion = datetime.now()

            self.db.add(tipo_db)
            self.db.commit()
            self.db.refresh(tipo_db)
            return tipo_db
        except Exception as e:
            self.db.rollback()
            print(f"Error al actualizar tipo de documento: {e}")
            raise

    def eliminar_tipo_documento(self, id_tipo_documento: Union[str, UUID]) -> bool:
        """Elimina (desactiva) un tipo de documento."""
        try:
            tipo_documento = self.obtener_por_id(id_tipo_documento)
            if not tipo_documento:
                return False

            tipo_documento.activo = False
            tipo_documento.fecha_actualizacion = datetime.now()
            self.db.add(tipo_documento)
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            print(f"Error al eliminar tipo de documento: {e}")
            return False
