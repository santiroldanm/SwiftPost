"""
API de Tipos de Documento - Endpoints para gestión de tipos de documento
"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.config import get_db
from cruds.tipo_documento_crud import TipoDocumentoCRUD
from schemas.tipo_documento_schema import (
    TipoDocumentoCreate,
    TipoDocumentoUpdate,
    TipoDocumentoResponse,
)
from schemas.auth_schema import RespuestaAPI

router = APIRouter(prefix="/tipos-documento", tags=["Tipos de Documento"])


@router.get("/", response_model=List[TipoDocumentoResponse])
async def obtener_tipos_documento(
    skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    """Obtener todos los tipos de documento con paginación."""
    try:
        tipo_doc_crud = TipoDocumentoCRUD(db)
        tipos = tipo_doc_crud.obtener_todos(skip=skip, limit=limit)
        return tipos
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener tipos de documento: {str(e)}",
        )


@router.get("/activos", response_model=List[TipoDocumentoResponse])
async def obtener_tipos_documento_activos(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """Obtener tipos de documento activos."""
    try:
        tipo_doc_crud = TipoDocumentoCRUD(db)
        tipos = tipo_doc_crud.obtener_activos(skip=skip, limit=limit)
        return tipos
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener tipos de documento activos: {str(e)}",
        )


@router.get("/{id_tipo_documento}", response_model=TipoDocumentoResponse)
async def obtener_tipo_documento_por_id(
    id_tipo_documento: UUID, db: Session = Depends(get_db)
):
    """Obtener un tipo de documento por su ID."""
    try:
        tipo_doc_crud = TipoDocumentoCRUD(db)
        tipo_documento = tipo_doc_crud.obtener_por_id(id_tipo_documento)
        if not tipo_documento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tipo de documento no encontrado",
            )
        return tipo_documento
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener tipo de documento: {str(e)}",
        )


@router.get("/codigo/{codigo}", response_model=TipoDocumentoResponse)
async def obtener_tipo_documento_por_codigo(codigo: str, db: Session = Depends(get_db)):
    """Obtener un tipo de documento por su código (ej: CC, TI, CE)."""
    try:
        tipo_doc_crud = TipoDocumentoCRUD(db)
        tipo_documento = tipo_doc_crud.obtener_por_codigo(codigo.upper())
        if not tipo_documento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tipo de documento no encontrado",
            )
        return tipo_documento
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al buscar tipo de documento por código: {str(e)}",
        )


@router.post(
    "/", response_model=TipoDocumentoResponse, status_code=status.HTTP_201_CREATED
)
async def crear_tipo_documento(
    tipo_data: TipoDocumentoCreate,
    db: Session = Depends(get_db),
    usuario_id: UUID = "ID Usuario con la sesión activa",
):
    """Crear un nuevo tipo de documento."""
    try:
        tipo_doc_crud = TipoDocumentoCRUD(db)

        if tipo_doc_crud.obtener_por_codigo(tipo_data.codigo):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un tipo de documento con este código",
            )

        tipo_documento = tipo_doc_crud.crear_tipo_documento(
            datos_entrada=tipo_data.dict(), usuario_id=usuario_id
        )
        return tipo_documento
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear tipo de documento: {str(e)}",
        )


@router.put("/{id_tipo_documento}", response_model=TipoDocumentoResponse)
async def actualizar_tipo_documento(
    id_tipo_documento: UUID,
    tipo_data: TipoDocumentoUpdate,
    db: Session = Depends(get_db),
    usuario_id: UUID = "ID Usuario con la sesión activa",
):
    """Actualizar un tipo de documento existente."""
    try:
        tipo_doc_crud = TipoDocumentoCRUD(db)
        tipo_documento = tipo_doc_crud.obtener_por_id(id_tipo_documento)

        if not tipo_documento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tipo de documento no encontrado",
            )

        if tipo_data.codigo and tipo_data.codigo != tipo_documento.codigo:
            if tipo_doc_crud.obtener_por_codigo(tipo_data.codigo):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El código ya está en uso por otro tipo de documento",
                )

        datos_actualizacion = tipo_data.dict(exclude_unset=True)
        tipo_actualizado = tipo_doc_crud.actualizar_tipo_documento(
            tipo_db=tipo_documento,
            datos_actualizacion=datos_actualizacion,
            actualizado_por=usuario_id,
        )

        return tipo_actualizado

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar tipo de documento: {str(e)}",
        )


@router.delete("/{id_tipo_documento}", response_model=RespuestaAPI)
async def eliminar_tipo_documento(
    id_tipo_documento: UUID,
    db: Session = Depends(get_db),
):
    """Eliminar un tipo de documento (soft delete)."""
    try:
        tipo_doc_crud = TipoDocumentoCRUD(db)
        tipo_documento = tipo_doc_crud.obtener_por_id(id_tipo_documento)
        if not tipo_documento:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tipo de documento no encontrado",
            )

        eliminado = tipo_doc_crud.eliminar_tipo_documento(id_tipo_documento)
        if eliminado:
            return RespuestaAPI(
                mensaje="Tipo de documento eliminado exitosamente", exito=True
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar tipo de documento",
            )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar tipo de documento: {str(e)}",
        )
