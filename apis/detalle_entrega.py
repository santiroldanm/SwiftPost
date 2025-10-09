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
        detalles, total = detalle_crud.obtener_todos(skip=skip, limit=limit)
        return {
            "detalles": detalles,
            "total": total,
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
        detalles, total = detalle_crud.obtener_por_estado(
            estado="Pendiente", skip=skip, limit=limit
        )
        return {
            "detalles": detalles,
            "total": total,
            "pagina": (skip // limit) + 1,
            "por_pagina": limit,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener entregas pendientes: {str(e)}",
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
            detalles, total = detalle_crud.obtener_por_cliente_remitente(
                id_cliente_remitente=id_cliente, saltar=skip, limite=limit
            )
        else:
            detalles, total = detalle_crud.obtener_por_cliente_receptor(
                id_cliente_receptor=id_cliente, saltar=skip, limite=limit
            )

        return {
            "detalles": detalles,
            "total": total,
            "pagina": (skip // limit) + 1,
            "por_pagina": limit,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener entregas por cliente: {str(e)}",
        )


@router.get("/empleado/{id_empleado}", response_model=DetalleEntregaListResponse)
async def obtener_entregas_por_empleado(
    id_empleado: UUID, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    """Obtener entregas asignadas a un empleado con paginación."""
    try:
        detalle_crud = DetalleEntregaCRUD(db)
        detalles, total = detalle_crud.obtener_por_empleado(
            id_empleado=id_empleado, saltar=skip, limite=limit
        )
        return {
            "detalles": detalles,
            "total": total,
            "pagina": (skip // limit) + 1,
            "por_pagina": limit,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener entregas por empleado: {str(e)}",
        )


@router.post(
    "/", response_model=DetalleEntregaResponse, status_code=status.HTTP_201_CREATED
)
async def crear_detalle_entrega(
    detalle_data: DetalleEntregaCreate,
    db: Session = Depends(get_db),
    usuario_id: UUID = "ID Usuario con la sesión activa",
):
    """Crear un nuevo detalle de entrega."""
    try:
        detalle_crud = DetalleEntregaCRUD(db)

        """ Validar que la fecha de envío no sea en el pasado """
        if detalle_data.fecha_envio < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha de envío no puede ser en el pasado",
            )

        detalle = detalle_crud.crear(datos_entrada=detalle_data, creado_por=usuario_id)

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
    usuario_id: UUID = "ID Usuario con la sesión activa",
):
    """Actualizar un detalle de entrega existente."""
    try:
        detalle_crud = DetalleEntregaCRUD(db)
        detalle = detalle_crud.obtener_por_id(id_detalle)

        if not detalle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Detalle de entrega no encontrado",
            )

        """ Validar que no se pueda cambiar a una fecha de envío en el pasado """
        if detalle_data.fecha_envio and detalle_data.fecha_envio < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La fecha de envío no puede ser en el pasado",
            )

        """ Actualizar solo los campos proporcionados"""
        datos_actualizacion = detalle_data.model_dump(exclude_unset=True)

        detalle_actualizado = detalle_crud.actualizar(
            objeto_db=detalle,
            datos_entrada=datos_actualizacion,
            actualizado_por=usuario_id,
        )

        if not detalle_actualizado:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No se pudo actualizar el detalle de entrega",
            )

        return detalle_actualizado

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al actualizar detalle de entrega: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar detalle de entrega: {str(e)}",
        )


@router.delete("/{id_detalle}", response_model=RespuestaAPI)
async def eliminar_detalle_entrega(
    id_detalle: UUID,
    usuario_id: UUID = "ID Usuario con la sesión activa",
    db: Session = Depends(get_db),
):
    """Eliminar un detalle de entrega (soft delete)"""
    try:
        detalle_crud = DetalleEntregaCRUD(db)
        detalle = detalle_crud.obtener_por_id(id_detalle)

        if not detalle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Detalle de entrega no encontrado",
            )

        """ Verificar si el detalle ya está entregado """
        if detalle.estado_envio == "Entregado":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede eliminar una entrega ya marcada como entregada",
            )

        """ Realizar el soft delete """
        eliminado = detalle_crud.desactivar(id=id_detalle, actualizado_por=usuario_id)

        if eliminado:
            return RespuestaAPI(
                mensaje="Detalle de entrega eliminado exitosamente", exito=True
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar el detalle de entrega",
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar detalle de entrega: {str(e)}",
        )
