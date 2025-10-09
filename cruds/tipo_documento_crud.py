from typing import Any, Dict, List, Optional, Union
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func
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

    def __init__(self, db: Session):
        super().__init__(TipoDocumento)
        self.db = db

    def obtener_por_nombre(self, nombre: str) -> Optional[TipoDocumento]:
        """Obtiene un tipo de documento por nombre."""
        return (
            self.db.query(TipoDocumento)
            .filter(TipoDocumento.nombre.lower() == nombre.lower())
            .first()
        )

    def obtener_por_codigo(self, codigo: str) -> Optional[TipoDocumento]:
        """Obtiene un tipo de documento por código."""
        return (
            self.db.query(TipoDocumento)
            .filter(func.lower(TipoDocumento.codigo) == codigo.lower())
            .first()
        )

    def obtener_todos(self, skip: int = 0, limit: int = 100) -> List[TipoDocumento]:
        """Obtiene todos los tipos de documento."""
        try:
            return self.db.query(TipoDocumento).offset(skip).limit(limit).all()
        except Exception as e:
            print(f"Error al obtener tipos de documento: {e}")
            return []

    def obtener_activos(
        self, saltar: int = 0, limite: int = 100
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
        self, *, datos_entrada: TipoDocumentoCreate, creado_por: UUID
    ) -> TipoDocumento:
        """Crea un nuevo tipo de documento."""
        db_obj = TipoDocumento(**datos_entrada.dict(), creado_por=creado_por)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def actualizar(
        self,
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
        return super().actualizar(objeto_db=objeto_db, datos_entrada=datos_actualizados)

    def desactivar(self, *, id: UUID, actualizado_por: UUID) -> TipoDocumento:
        """Desactiva un tipo de documento."""
        tipo_documento = self.obtener_por_id(id)
        if tipo_documento:
            tipo_documento.activo = False
            tipo_documento.actualizado_por = actualizado_por
            self.db.add(tipo_documento)
            self.db.commit()
            self.db.refresh(tipo_documento)
        return tipo_documento


tipo_documento = TipoDocumentoCRUD(TipoDocumento)
