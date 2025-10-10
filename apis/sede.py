"""
API de sedes - Endpoints para gestión de sedes
"""

from typing import List
from uuid import UUID
from database.config import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from cruds.sede_crud import SedeCRUD
from schemas.sede_schema import (
    SedeCreate,
    SedeUpdate,
    SedeResponse,
)
from schemas.auth_schema import RespuestaAPI
from schemas.sede_schema import SedeResponse

router = APIRouter(prefix="/sedes", tags=["Sedes"])


@router.get("/", response_model=List[SedeResponse])
async def obtener_sedes(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Obtener todos los sedes con paginación."""
    try:
        sede_crud = SedeCRUD(db)
        sedes = sede_crud.obtener_todos(skip=skip, limit=limit)
        return sedes
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener sede: {str(e)}",
        )


@router.get("/activos", response_model=List[SedeResponse])
async def obtener_sedes_activos(
    skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    """Obtener todos los sedes activos con paginación."""
    try:
        sede_crud = SedeCRUD(db)
        sedes = sede_crud.obtener_activas(skip=skip, limit=limit)
        return sedes
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener sedes activas: {str(e)}",
        )


@router.get("/{id_sede}", response_model=SedeResponse)
async def obtener_sede_por_id(id_sede: UUID, db: Session = Depends(get_db)):
    """Obtener una sede por su ID."""
    try:
        sede_crud = SedeCRUD(db)
        sede = sede_crud.obtener_por_id(id_sede)
        if not sede:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sede no encontrada",
            )
        return sede
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener sede: {str(e)}",
        )


@router.get("/ciudad/{ciudad}", response_model=List[SedeResponse])
async def obtener_sedes_por_ciudad(
    ciudad: str, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    """Obtener todos los sedes por ciudad con paginación."""
    try:
        sede_crud = SedeCRUD(db)
        sedes = sede_crud.obtener_por_ciudad(ciudad, skip=skip, limit=limit)
        return sedes
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener sedes por ciudad: {str(e)}",
        )


@router.get("/nombre/{nombre_sede}", response_model=SedeResponse)
async def obtener_sede_por_nombre(nombre_sede: str, db: Session = Depends(get_db)):
    """Obtener una sede por su nombre."""
    try:
        sede_crud = SedeCRUD(db)
        sede = sede_crud.obtener_por_nombre(nombre_sede)
        if not sede:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Sede no encontrada",
            )
        return sede
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener sede: {str(e)}",
        )


@router.post("/", response_model=SedeResponse, status_code=status.HTTP_201_CREATED)
async def crear_sede(
    sede_data: SedeCreate,
    db: Session = Depends(get_db),
    creado_por: UUID = "ID Usuario con la sesión activa",
):
    """Crear una nueva sede."""
    try:
        sede_crud = SedeCRUD(db)
        sede = sede_crud.crear_sede(
            datos_entrada=sede_data,
            creado_por=creado_por,
        )

        if not sede:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo crear la sede. Verifica que el nombre no esté duplicado.",
            )

        return sede

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
            detail=f"Error al crear sede: {str(e)}",
        )


@router.put("/{id_sede}", response_model=SedeResponse)
async def actualizar_sede(
    id_sede: UUID,
    sede_data: SedeUpdate,
    db: Session = Depends(get_db),
    actualizado_por: UUID = "ID Usuario con la sesión activa",
):
    """Actualizar una sede existente."""
    try:
        sede_crud = SedeCRUD(db)
        sede = sede_crud.obtener_por_id(id_sede)
        if not sede:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Sede no encontrada"
            )

        sede_actualizado = sede_crud.actualizar_sede(
            objeto_db=sede,
            datos_entrada=sede_data,
            actualizado_por=actualizado_por,
        )

        if not sede_actualizado:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo actualizar la sede. Verifica que el nombre no esté duplicado.",
            )

        return sede_actualizado

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
            detail=f"Error al actualizar la sede: {str(e)}",
        )


@router.delete("/{id_sede}", response_model=RespuestaAPI)
async def eliminar_sede(
    id_sede: UUID,
    actualizado_por: UUID = "ID Usuario con la sesión activa",
    db: Session = Depends(get_db),
):
    """Eliminar una sede. Soft delete."""
    try:
        sede_crud = SedeCRUD(db)
        sede = sede_crud.obtener_por_id(id_sede)
        if not sede:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Sede no encontrada"
            )
        eliminado = sede_crud.desactivar_sede(
            sede_id=id_sede, actualizado_por=actualizado_por
        )
        if eliminado:
            return RespuestaAPI(mensaje="Sede desactivada exitosamente", exito=True)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al desactivar la sede",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al desactivar la sede: {str(e)}",
        )
