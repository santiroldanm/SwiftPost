from typing import Any, Dict, List, Optional, Union
from uuid import UUID
from sqlalchemy.orm import Session
from entities.tipo_documento import (
    TipoDocumento,
    TipoDocumentoCreate,
    TipoDocumentoUpdate,
)
from .base_crud import CRUDBase


class TipoDocumentoCRUD(
    CRUDBase[TipoDocumento, TipoDocumentoCreate, TipoDocumentoUpdate]
):
    """Operaciones CRUD para TipoDocumento."""

    def obtener_por_nombre(self, db: Session, nombre: str) -> Optional[TipoDocumento]:
        """Obtiene un tipo de documento por nombre."""
        return db.query(TipoDocumento).filter(TipoDocumento.nombre == nombre).first()

    def obtener_todos(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[TipoDocumento]:
        """Obtiene todos los tipos de documento."""
        try:
            return db.query(TipoDocumento).offset(skip).limit(limit).all()
        except Exception as e:
            print(f"Error al obtener tipos de documento: {e}")
            return []

    def obtener_activos(
        self, db: Session, saltar: int = 0, limite: int = 100
    ) -> List[TipoDocumento]:
        """Obtiene tipos de documento activos."""
        print("\n=== DEBUG: Iniciando obtener_activos ===")
        print(f"Tipo de db: {type(db)}")
        try:
            test = db.query(TipoDocumento).first()
            print(f"Test query result: {test}")
        except Exception as e:
            print(f"Error al ejecutar consulta de prueba: {e}")
            return []
        try:
            tipos = (
                db.query(TipoDocumento)
                .filter(TipoDocumento.activo == True)
                .offset(saltar)
                .limit(limite)
                .all()
            )
            print(f"=== DEBUG: Tipos de documento encontrados: {len(tipos)} ===")
            for i, t in enumerate(tipos, 1):
                print(
                    f"{i}. ID: {t.id_tipo_documento}, Nombre: {t.nombre}, Código: {t.codigo}"
                )
            return tipos
        except Exception as e:
            print(f"Error en obtener_activos: {e}")
            return []

    def crear(
        self, db: Session, *, datos_entrada: TipoDocumentoCreate, creado_por: UUID
    ) -> TipoDocumento:
        """Crea un nuevo tipo de documento."""
        db_obj = TipoDocumento(**datos_entrada.dict(), creado_por=creado_por)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def actualizar(
        self,
        db: Session,
        *,
        objeto_db: TipoDocumento,
        datos_entrada: Union[TipoDocumentoUpdate, Dict[str, Any]],
        actualizado_por: UUID,
    ) -> TipoDocumento:
        """Actualiza un tipo de documento."""
        if isinstance(datos_entrada, dict):
            datos_actualizados = datos_entrada
        else:
            datos_actualizados = datos_entrada.dict(exclude_unset=True)
        datos_actualizados["actualizado_por"] = actualizado_por
        return super().actualizar(
            db, objeto_db=objeto_db, datos_entrada=datos_actualizados
        )

    def desactivar(
        self, db: Session, *, id: UUID, actualizado_por: UUID
    ) -> TipoDocumento:
        """Desactiva un tipo de documento."""
        tipo_documento = self.obtener_por_id(db, id)
        if tipo_documento:
            tipo_documento.activo = False
            tipo_documento.actualizado_por = actualizado_por
            db.add(tipo_documento)
            db.commit()
            db.refresh(tipo_documento)
        return tipo_documento


tipo_documento = TipoDocumentoCRUD(TipoDocumento)
