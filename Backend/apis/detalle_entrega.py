"""
API de Detalles de Entrega - Endpoints para gestión de detalles de entrega
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime
from database.config import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from cruds.detalle_entrega_crud import DetalleEntregaCRUD
from schemas.detalle_entrega_schema import (
    DetalleEntregaCreate,
    DetalleEntregaUpdate,
    DetalleEntregaResponse,
    DetalleEntregaListResponse,
)
from schemas.auth_schema import RespuestaAPI

router = APIRouter(prefix="/detalles-entrega", tags=["Detalles de Entrega"])


@router.get("/", response_model=DetalleEntregaListResponse)
async def obtener_detalles_entrega(
    skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    """Obtener todos los detalles de entrega con paginación."""
    try:
        detalle_crud = DetalleEntregaCRUD(db)
        detalles = detalle_crud.obtener_todos(skip=skip, limit=limit)
        return {
            "detalles": detalles,
            "pagina": (skip // limit) + 1,
            "por_pagina": limit,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener detalles de entrega: {str(e)}",
        )


@router.get("/pendientes", response_model=DetalleEntregaListResponse)
async def obtener_entregas_pendientes(
    skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    """Obtener entregas pendientes con paginación."""
    try:
        detalle_crud = DetalleEntregaCRUD(db)
        detalles = detalle_crud.obtener_por_estado(
            estado="Pendiente", skip=skip, limit=limit
        )
        return {
            "detalles": detalles,
            "pagina": (skip // limit) + 1,
            "por_pagina": limit,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener entregas pendientes: {str(e)}",
        )


@router.get("/estado/{estado}", response_model=DetalleEntregaListResponse)
async def obtener_entregas_por_estado(
    estado: str, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    """Obtener entregas por estado con paginación."""
    try:
        detalle_crud = DetalleEntregaCRUD(db)
        detalles = detalle_crud.obtener_por_estado(
            estado=estado, skip=skip, limit=limit
        )
        return {
            "detalles": detalles,
            "pagina": (skip // limit) + 1,
            "por_pagina": limit,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener entregas por estado: {str(e)}",
        )


@router.get("/{id_detalle}", response_model=DetalleEntregaResponse)
async def obtener_detalle_por_id(id_detalle: UUID, db: Session = Depends(get_db)):
    """Obtener un detalle de entrega por su ID."""
    try:
        detalle_crud = DetalleEntregaCRUD(db)
        detalle = detalle_crud.obtener_por_id(id_detalle)
        if not detalle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Detalle de entrega no encontrado",
            )
        return detalle
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener detalle de entrega: {str(e)}",
        )


@router.get("/cliente/{id_cliente}", response_model=DetalleEntregaListResponse)
async def obtener_entregas_por_cliente(
    id_cliente: UUID,
    tipo: str = "remitente",
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    """Obtener entregas por cliente (remitente o receptor) con paginación."""
    try:
        detalle_crud = DetalleEntregaCRUD(db)

        if tipo.lower() == "remitente":
            detalles = detalle_crud.obtener_por_cliente_remitente(
                id_cliente_remitente=id_cliente, skip=skip, limit=limit
            )
        else:
            detalles = detalle_crud.obtener_por_cliente_receptor(
                id_cliente_receptor=id_cliente, skip=skip, limit=limit
            )

        return {
            "detalles": detalles,
            "pagina": (skip // limit) + 1,
            "por_pagina": limit,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener entregas por cliente: {str(e)}",
        )


@router.get("/paquete/{id_paquete}", response_model=DetalleEntregaResponse)
async def obtener_entrega_por_paquete(id_paquete: UUID, db: Session = Depends(get_db)):
    """Obtener detalle de entrega por ID de paquete."""
    try:
        detalle_crud = DetalleEntregaCRUD(db)
        detalle = detalle_crud.obtener_por_paquete(id_paquete=id_paquete)

        if not detalle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Detalle de entrega no encontrado para este paquete",
            )

        return detalle
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener entrega por paquete: {str(e)}",
        )


@router.post(
    "/", response_model=DetalleEntregaResponse, status_code=status.HTTP_201_CREATED
)
async def crear_detalle_entrega(
    detalle_data: DetalleEntregaCreate,
    db: Session = Depends(get_db),
    creado_por: Optional[UUID] = None,
):
    """Crear un nuevo detalle de entrega."""
    try:
        if not creado_por:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="creado_por es obligatorio",
            )

        detalle_crud = DetalleEntregaCRUD(db)
        detalle = detalle_crud.crear(datos_entrada=detalle_data, creado_por=creado_por)

        if not detalle:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo crear el detalle de entrega. Verifique los datos.",
            )

        return detalle
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear detalle de entrega: {str(e)}",
        )


@router.put("/{id_detalle}", response_model=DetalleEntregaResponse)
async def actualizar_detalle_entrega(
    id_detalle: UUID,
    detalle_data: DetalleEntregaUpdate,
    db: Session = Depends(get_db),
    actualizado_por: Optional[UUID] = None,
):
    """Actualizar un detalle de entrega existente."""
    try:
        if not actualizado_por:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="actualizado_por es obligatorio",
            )

        detalle_crud = DetalleEntregaCRUD(db)
        detalle = detalle_crud.obtener_por_id(id_detalle)

        if not detalle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Detalle de entrega no encontrado",
            )

        detalle_actualizado = detalle_crud.actualizar(
            objeto_db=detalle,
            datos_entrada=detalle_data,
            actualizado_por=actualizado_por,
        )

        if not detalle_actualizado:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo actualizar el detalle de entrega",
            )

        return detalle_actualizado

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar detalle de entrega: {str(e)}",
        )


@router.delete("/{id_detalle}", response_model=RespuestaAPI)
async def eliminar_detalle_entrega(
    id_detalle: UUID,
    actualizado_por: Optional[UUID] = None,
    db: Session = Depends(get_db),
):
    """Eliminar un detalle de entrega (soft delete)"""
    try:
        if not actualizado_por:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="actualizado_por es obligatorio",
            )

        detalle_crud = DetalleEntregaCRUD(db)
        detalle = detalle_crud.obtener_por_id(id_detalle)

        if not detalle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Detalle de entrega no encontrado",
            )

        if detalle.estado_envio == "Entregado":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede eliminar una entrega ya marcada como entregada",
            )

        eliminado = detalle_crud.desactivar(
            id_detalle=id_detalle, actualizado_por=actualizado_por
        )

        if eliminado:
            return RespuestaAPI(
                mensaje="Detalle de entrega desactivado exitosamente", exito=True
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al desactivar el detalle de entrega",
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar detalle de entrega: {str(e)}",
        )
