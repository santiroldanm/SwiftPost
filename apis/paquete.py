"""
API de paquetes - Endpoints para gestión de paquetes
"""

from typing import Optional
from uuid import UUID
from datetime import datetime
from database.config import get_db
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from cruds.paquete_crud import PaqueteCRUD
from schemas.paquete_schema import (
    PaqueteCreate,
    PaqueteUpdate,
    PaqueteResponse,
    PaqueteListResponse,
)
from schemas.auth_schema import RespuestaAPI

router = APIRouter(prefix="/paquetes", tags=["Paquetes"])


@router.get("/", response_model=PaqueteListResponse)
async def obtener_paquetes(
    skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    """Obtener todos los paquetes con paginación."""
    try:
        paquete_crud = PaqueteCRUD(db)
        paquetes = paquete_crud.obtener_todos(skip=skip, limit=limit)
        return {
            "paquetes": paquetes,
            "pagina": (skip // limit) + 1,
            "por_pagina": limit,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener paquetes: {str(e)}",
        )


@router.get("/estado/{estado}", response_model=PaqueteListResponse)
async def obtener_paquetes_por_estado(
    estado: str, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    """Obtener paquetes por estado con paginación."""
    try:
        paquete_crud = PaqueteCRUD(db)
        paquetes = paquete_crud.obtener_por_estado(estado, skip=skip, limit=limit)
        return {
            "paquetes": paquetes,
            "pagina": (skip // limit) + 1,
            "por_pagina": limit,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener paquetes por estado: {str(e)}",
        )


@router.get("/{id_paquete}", response_model=PaqueteResponse)
async def obtener_paquete_por_id(id_paquete: UUID, db: Session = Depends(get_db)):
    """Obtener un paquete por su ID."""
    try:
        paquete_crud = PaqueteCRUD(db)
        paquete = paquete_crud.obtener_por_id(id_paquete)
        if not paquete:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paquete no encontrado",
            )
        return paquete
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener paquete: {str(e)}",
        )


@router.get("/cliente/{id_cliente}", response_model=PaqueteListResponse)
async def obtener_paquetes_por_cliente(
    id_cliente: UUID, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    """Obtener todos los paquetes de un cliente con paginación."""
    try:
        paquete_crud = PaqueteCRUD(db)
        paquetes = paquete_crud.obtener_por_cliente(id_cliente, skip=skip, limit=limit)
        return {
            "paquetes": paquetes,
            "pagina": (skip // limit) + 1,
            "por_pagina": limit,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener paquetes del cliente: {str(e)}",
        )


"""@router.get("/seguimiento/{codigo_seguimiento}", response_model=PaqueteResponse)
async def obtener_paquete_por_seguimiento(
    codigo_seguimiento: str, db: Session = Depends(get_db)
):
     Obtener un paquete por su código de seguimiento. 
    try:
        paquete_crud = PaqueteCRUD(db)
        paquete = paquete_crud.obtener_por_codigo_seguimiento(codigo_seguimiento)
        if not paquete:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Paquete no encontrado",
            )
        return paquete
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener paquete: {str(e)}",
        )

"""


@router.post("/", response_model=PaqueteResponse, status_code=status.HTTP_201_CREATED)
async def crear_paquete(
    paquete_data: PaqueteCreate,
    db: Session = Depends(get_db),
    id_cliente: Optional[UUID] = Query(
        None, description="UUID del cliente (opcional en query)"
    ),
    creado_por: Optional[UUID] = Query(
        None, description="UUID del usuario que crea el registro"
    ),
):
    """Crear un nuevo paquete (id_cliente y creado_por deben ser UUID válidos)."""
    try:
        datos = (
            paquete_data.model_dump()
            if hasattr(paquete_data, "model_dump")
            else paquete_data.dict()
        )

        raw_id_cliente = datos.get("id_cliente") or id_cliente
        if not raw_id_cliente:
            raise HTTPException(status_code=400, detail="id_cliente es obligatorio")

        try:
            id_cliente_uuid = (
                raw_id_cliente
                if isinstance(raw_id_cliente, UUID)
                else UUID(str(raw_id_cliente))
            )
        except Exception:
            raise HTTPException(
                status_code=400, detail="id_cliente debe ser un UUID válido"
            )

        raw_creado_por = creado_por or datos.get("creado_por")
        if not raw_creado_por:
            raise HTTPException(status_code=400, detail="creado_por es obligatorio")

        try:
            creado_por_uuid = (
                raw_creado_por
                if isinstance(raw_creado_por, UUID)
                else UUID(str(raw_creado_por))
            )
        except Exception:
            raise HTTPException(
                status_code=400, detail="creado_por debe ser un UUID válido"
            )

        datos["id_cliente"] = id_cliente_uuid
        datos["creado_por"] = creado_por_uuid
        datos["actualizado_por"] = None

        paquete_crud = PaqueteCRUD(db)
        paquete = paquete_crud.crear_paquete(
            datos_entrada=datos, id_cliente=id_cliente_uuid, creado_por=creado_por_uuid
        )

        if not paquete:
            raise HTTPException(
                status_code=400, detail="No se pudo crear el paquete (revisar logs)"
            )

        return paquete

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear paquete: {e}")


@router.put("/{id_paquete}", response_model=PaqueteResponse)
async def actualizar_paquete(
    id_paquete: UUID,
    paquete_data: PaqueteUpdate,
    db: Session = Depends(get_db),
    actualizado_por: UUID | None = Query(
        None, description="UUID del usuario que realiza la actualización"
    ),
):
    """Actualizar un paquete existente."""
    try:
        if actualizado_por is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="updated_by (actualizado_por) es requerido",
            )

        paquete_crud = PaqueteCRUD(db)
        paquete = paquete_crud.obtener_por_id(id_paquete)
        if not paquete:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Paquete no encontrado"
            )

        paquete_actualizado = paquete_crud.actualizar(
            objeto_db=paquete,
            datos_entrada=paquete_data,
            actualizado_por=actualizado_por,
        )

        if not paquete_actualizado:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo actualizar el paquete (ver logs)",
            )

        return paquete_actualizado

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar paquete: {e}",
        )


@router.delete("/{id_paquete}", response_model=RespuestaAPI)
async def eliminar_paquete(
    id_paquete: UUID,
    actualizado_por: UUID = "ID Usuario con la sesión activa",
    db: Session = Depends(get_db),
):
    """Eliminar un paquete (soft delete)."""
    try:
        paquete_crud = PaqueteCRUD(db)
        paquete = paquete_crud.obtener_por_id(id_paquete)

        if not paquete:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Paquete no encontrado"
            )

        eliminado = paquete_crud.desactivar_paquete(
            id_paquete=id_paquete, actualizado_por=actualizado_por
        )

        if eliminado:
            return RespuestaAPI(mensaje="Paquete desactivado exitosamente", exito=True)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al desactivar paquete",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al desactivar paquete: {str(e)}",
        )
