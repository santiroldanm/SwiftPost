"""
API de paquetes - Endpoints para gestión de paquetes
"""
from typing import List
from uuid import UUID
from datetime import datetime
from database.config import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from cruds.paquete_crud import PaqueteCRUD
from schemas.paquete_schema import (
    PaqueteCreate,
    PaqueteUpdate,
    PaqueteResponse,
    PaqueteListResponse
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
        total = paquete_crud.contar()
        return {
            "paquetes": paquetes,
            "total": total,
            "pagina": (skip // limit) + 1,
            "por_pagina": limit
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
        total = paquete_crud.contar_por_estado(estado)
        return {
            "paquetes": paquetes,
            "total": total,
            "pagina": (skip // limit) + 1,
            "por_pagina": limit
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
        total = paquete_crud.contar_por_cliente(id_cliente)
        return {
            "paquetes": paquetes,
            "total": total,
            "pagina": (skip // limit) + 1,
            "por_pagina": limit
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener paquetes del cliente: {str(e)}",
        )


@router.get("/seguimiento/{codigo_seguimiento}", response_model=PaqueteResponse)
async def obtener_paquete_por_seguimiento(
    codigo_seguimiento: str, db: Session = Depends(get_db)
):
    """Obtener un paquete por su código de seguimiento."""
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


@router.post("/", response_model=PaqueteResponse, status_code=status.HTTP_201_CREATED)
async def crear_paquete(
    paquete_data: PaqueteCreate,
    db: Session = Depends(get_db),
    usuario_id: UUID = "ID Usuario con la sesión activa",
):
    """Crear un nuevo paquete."""
    try:
        paquete_crud = PaqueteCRUD(db)
        paquete = paquete_crud.crear_paquete(
            datos_entrada=paquete_data.dict(),
            usuario_id=usuario_id,
        )
        return paquete
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear paquete: {str(e)}",
        )


@router.put("/{id_paquete}", response_model=PaqueteResponse)
async def actualizar_paquete(
    id_paquete: UUID,
    paquete_data: PaqueteUpdate,
    db: Session = Depends(get_db),
    usuario_id: UUID = "ID Usuario con la sesión activa",
):
    """Actualizar un paquete existente."""
    try:
        paquete_crud = PaqueteCRUD(db)
        paquete = paquete_crud.obtener_por_id(id_paquete)
        if not paquete:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Paquete no encontrado"
            )

        """ Actualizar solo los campos proporcionados"""
        datos_actualizacion = paquete_data.model_dump(exclude_unset=True)
        
        paquete_actualizado = paquete_crud.actualizar_paquete(
            objeto_db=paquete,
            datos_entrada=datos_actualizacion,
            actualizado_por=usuario_id,
        )

        if not paquete_actualizado:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No se pudo actualizar el paquete",
            )

        return paquete_actualizado

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al actualizar paquete: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar paquete: {str(e)}",
        )


@router.delete("/{id_paquete}", response_model=RespuestaAPI)
async def eliminar_paquete(
    id_paquete: UUID,
    usuario_id: UUID = "ID Usuario con la sesión activa",
    db: Session = Depends(get_db),
):
    """Eliminar un paquete (soft delete)."""
    try:
        paquete_crud = PaqueteCRUD(db)
        paquete = paquete_crud.obtener_por_id(id_paquete)

        if not paquete:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Paquete no encontrado"
            )

        eliminado = paquete_crud.eliminar_paquete(paquete, actualizado_por=usuario_id)

        if eliminado:
            return RespuestaAPI(mensaje="Paquete eliminado exitosamente", exito=True)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar paquete",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar paquete: {str(e)}",
        )
