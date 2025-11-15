"""
API de transporte - Endpoints para gestión de vehículos de transporte
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime
from database.config import get_db
from fastapi import APIRouter, Depends, HTTPException, status, Query, Header
from sqlalchemy.orm import Session
from cruds.transporte_crud import TransporteCRUD
from schemas.transporte_schema import (
    TransporteCreate,
    TransporteUpdate,
    TransporteResponse,
    TransporteListResponse,
)
from schemas.auth_schema import RespuestaAPI

router = APIRouter(prefix="/transportes", tags=["Transportes"])


@router.get("/", response_model=TransporteListResponse)
async def obtener_transportes(
    skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    """Obtener todos los vehículos de transporte con paginación."""
    try:
        transporte_crud = TransporteCRUD(db)
        transportes = transporte_crud.obtener_todos(skip=skip, limit=limit)
        total = transporte_crud.contar()
        return {
            "transportes": transportes,
            "total": total,
            "pagina": (skip // limit) + 1,
            "por_pagina": limit,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener vehículos: {str(e)}",
        )


@router.get("/activos", response_model=List[TransporteResponse])
async def obtener_transportes_activos(
    skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    """Obtener todos los vehículos activos con paginación."""
    try:
        transporte_crud = TransporteCRUD(db)
        transportes = transporte_crud.obtener_activos(skip=skip, limit=limit)
        return transportes
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener vehículos activos: {str(e)}",
        )


@router.get("/{id_transporte}", response_model=TransporteResponse)
async def obtener_transporte_por_id(id_transporte: UUID, db: Session = Depends(get_db)):
    """Obtener un vehículo por su ID."""
    try:
        transporte_crud = TransporteCRUD(db)
        transporte = transporte_crud.obtener_por_id(id_transporte)
        if not transporte:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehículo no encontrado",
            )
        return transporte
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener vehículo: {str(e)}",
        )


@router.get("/tipo/{tipo}", response_model=List[TransporteResponse])
async def obtener_transportes_por_tipo(
    tipo: str, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    """Obtener vehículos por tipo con paginación."""
    try:
        transporte_crud = TransporteCRUD(db)
        transportes = transporte_crud.obtener_por_tipo(tipo, skip=skip, limit=limit)
        return transportes
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener vehículos por tipo: {str(e)}",
        )


@router.get("/placa/{placa}", response_model=TransporteResponse)
async def obtener_transporte_por_placa(placa: str, db: Session = Depends(get_db)):
    """Obtener un vehículo por su placa."""
    try:
        transporte_crud = TransporteCRUD(db)
        transporte = transporte_crud.obtener_por_placa(placa)
        if not transporte:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Vehículo no encontrado",
            )
        return transporte
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener vehículo: {str(e)}",
        )


@router.post(
    "/", response_model=TransporteResponse, status_code=status.HTTP_201_CREATED
)
async def crear_transporte(
    transporte_data: TransporteCreate,
    db: Session = Depends(get_db),
    creado_por: Optional[UUID] = Query(None, description="UUID del usuario que crea el registro"),
    x_user_id: Optional[str] = Header(None, alias="X-User-ID"),
):
    """Crear un nuevo vehículo de transporte."""
    try:
        if creado_por:
            usuario_id = creado_por
        elif x_user_id:
            try:
                usuario_id = UUID(x_user_id)
            except ValueError:
                usuario_id = UUID("213dbacf-12cd-4944-9a55-2ec0d259ed31")
        else:
            usuario_id = UUID("213dbacf-12cd-4944-9a55-2ec0d259ed31")
        
        transporte_crud = TransporteCRUD(db)

        if transporte_crud.obtener_por_placa(transporte_data.placa):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un vehículo con esta placa",
            )

        transporte = transporte_crud.crear(
            obj_in=transporte_data, creado_por=usuario_id
        )
        return transporte
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear vehículo: {str(e)}",
        )


@router.put("/{id_transporte}", response_model=TransporteResponse)
async def actualizar_transporte(
    id_transporte: UUID,
    transporte_data: TransporteUpdate,
    db: Session = Depends(get_db),
    actualizado_por: Optional[UUID] = Query(None, description="UUID del usuario que realiza la actualización"),
    x_user_id: Optional[str] = Header(None, alias="X-User-ID"),
):
    """Actualizar un vehículo existente."""
    try:
        if actualizado_por:
            usuario_id = actualizado_por
        elif x_user_id:
            try:
                usuario_id = UUID(x_user_id)
            except ValueError:
                usuario_id = UUID("213dbacf-12cd-4944-9a55-2ec0d259ed31")
        else:
            usuario_id = UUID("213dbacf-12cd-4944-9a55-2ec0d259ed31")
        
        transporte_crud = TransporteCRUD(db)
        transporte = transporte_crud.obtener_por_id(id_transporte)

        if not transporte:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Vehículo no encontrado"
            )

        transporte_actualizado = transporte_crud.actualizar(
            db_obj=transporte,
            obj_in=transporte_data,
            actualizado_por=usuario_id,
        )

        if not transporte_actualizado:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo actualizar el vehículo",
            )

        return transporte_actualizado

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar vehículo: {str(e)}",
        )


@router.delete("/{id_transporte}", response_model=RespuestaAPI)
async def eliminar_transporte(
    id_transporte: UUID,
    actualizado_por: Optional[UUID] = Query(None, description="UUID del usuario que realiza la eliminación"),
    db: Session = Depends(get_db),
    x_user_id: Optional[str] = Header(None, alias="X-User-ID"),
):
    """Eliminar un vehículo (soft delete)."""
    try:
        if actualizado_por:
            usuario_id = actualizado_por
        elif x_user_id:
            try:
                usuario_id = UUID(x_user_id)
            except ValueError:
                usuario_id = UUID("213dbacf-12cd-4944-9a55-2ec0d259ed31")
        else:
            usuario_id = UUID("213dbacf-12cd-4944-9a55-2ec0d259ed31")
        
        transporte_crud = TransporteCRUD(db)
        transporte = transporte_crud.obtener_por_id(id_transporte)

        if not transporte:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Vehículo no encontrado"
            )

        if transporte.estado == "en_uso":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede eliminar un vehículo que está en uso",
            )

        eliminado = transporte_crud.desactivar_transporte(
            id_transporte=id_transporte, actualizado_por=usuario_id
        )

        if eliminado:
            return RespuestaAPI(mensaje="Vehículo eliminado exitosamente", exito=True)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar el vehículo",
            )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"UUID inválido: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar vehículo: {str(e)}",
        )
