"""
API de Roles - Endpoints para gestión de roles de usuario
"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.config import get_db
from cruds.rol_crud import RolCRUD
from schemas.rol_schema import (
    RolCreate,
    RolUpdate,
    RolResponse,
)
from schemas.auth_schema import RespuestaAPI

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.get("/", response_model=List[RolResponse])
async def obtener_roles(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Obtener todos los roles con paginación."""
    try:
        rol_crud = RolCRUD(db)
        roles = rol_crud.obtener_roles(skip=skip, limit=limit)
        return roles
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener roles: {str(e)}",
        )


@router.get("/{id_rol}", response_model=RolResponse)
async def obtener_rol_por_id(id_rol: UUID, db: Session = Depends(get_db)):
    """Obtener un rol por su ID."""
    try:
        rol_crud = RolCRUD(db)
        rol = rol_crud.obtener_por_id(id_rol)
        if not rol:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado"
            )
        return rol
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener rol: {str(e)}",
        )


@router.post("/", response_model=RolResponse, status_code=status.HTTP_201_CREATED)
async def crear_rol(
    rol_data: RolCreate,
    db: Session = Depends(get_db),
    usuario_id: UUID = "ID Usuario con la sesión activa",
):
    """Crear un nuevo rol."""
    try:
        rol_crud = RolCRUD(db)
        nuevo_rol = rol_crud.crear_rol(
            datos_entrada=rol_data.dict(), usuario_id=usuario_id
        )
        return nuevo_rol
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear rol: {str(e)}",
        )


@router.put("/{id_rol}", response_model=RolResponse)
async def actualizar_rol(
    id_rol: UUID,
    rol_data: RolUpdate,
    db: Session = Depends(get_db),
    usuario_id: UUID = "ID Usuario con la sesión activa",
):
    """Actualizar un rol existente."""
    try:
        rol_crud = RolCRUD(db)
        rol_existente = rol_crud.obtener_por_id(id_rol)
        if not rol_existente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado"
            )

        campos_actualizacion = rol_data.dict(exclude_unset=True)
        rol_actualizado = rol_crud.actualizar_rol(
            rol_db=rol_existente,
            datos_actualizacion=campos_actualizacion,
            actualizado_por=usuario_id,
        )
        return rol_actualizado
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar rol: {str(e)}",
        )


@router.delete("/{id_rol}", response_model=RespuestaAPI)
async def eliminar_rol(
    id_rol: UUID,
    db: Session = Depends(get_db),
):
    """Eliminar un rol (soft delete)."""
    try:
        rol_crud = RolCRUD(db)
        rol_existente = rol_crud.obtener_por_id(id_rol)
        if not rol_existente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Rol no encontrado"
            )

        eliminado = rol_crud.eliminar_rol(id_rol)
        if eliminado:
            return RespuestaAPI(mensaje="Rol eliminado exitosamente", exito=True)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar rol",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar el rol: {str(e)}",
        )