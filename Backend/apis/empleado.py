"""
API de empleados - Endpoints para gestión de empleados
"""

from typing import List, Optional
from uuid import UUID
from database.config import get_db
from fastapi import APIRouter, Depends, HTTPException, status, Query, Header
from sqlalchemy.orm import Session
from cruds.empleado_crud import EmpleadoCRUD
from cruds.tipo_documento_crud import TipoDocumentoCRUD
from schemas.empleado_schema import (
    EmpleadoCreate,
    EmpleadoUpdate,
    EmpleadoResponse,
)
from schemas.auth_schema import RespuestaAPI

router = APIRouter(prefix="/empleados", tags=["Empleados"])


@router.get("/", response_model=List[EmpleadoResponse])
async def obtener_empleados(
    skip: int = 0, 
    limit: int = 10, 
    tipo_empleado: Optional[str] = Query(None, description="Filtrar por tipo de empleado"),
    search: Optional[str] = Query(None, description="Buscar por nombre, documento o cargo"),
    activo: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    db: Session = Depends(get_db)
):
    """Obtener todos los empleados con paginación y filtros."""
    try:
        empleado_crud = EmpleadoCRUD(db)
        empleados = empleado_crud.obtener_empleados(
            skip=skip, 
            limit=limit,
            tipo_empleado=tipo_empleado,
            search=search,
            activo=activo
        )
        return empleados
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener clientes: {str(e)}",
        )


@router.get("/activos", response_model=List[EmpleadoResponse])
async def obtener_empleados_activos(
    skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    """Obtener todos los empleados activos con paginación."""
    try:
        empleado_crud = EmpleadoCRUD(db)
        empleados = empleado_crud.obtener_activos(skip=skip, limit=limit)
        return empleados
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener empleados activos: {str(e)}",
        )


@router.get("/{id_empleado}", response_model=EmpleadoResponse)
async def obtener_empleado_por_id(id_empleado: UUID, db: Session = Depends(get_db)):
    """Obtener un empleado por su ID."""
    try:
        empleado_crud = EmpleadoCRUD(db)
        empleado = empleado_crud.obtener_por_id(id_empleado)
        if not empleado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Empleado no encontrado",
            )
        return empleado
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener empleado: {str(e)}",
        )


@router.get("/tipo/{tipo}", response_model=List[EmpleadoResponse])
async def obtener_empleados_por_tipo(
    tipo: str, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    """Obtener todos los empleados por tipo con paginación."""
    try:
        empleado_crud = EmpleadoCRUD(db)
        empleados = empleado_crud.obtener_por_cargo(tipo, skip=skip, limit=limit)
        return empleados
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener empleados por tipo: {str(e)}",
        )


@router.get("/documento/{numero_documento}", response_model=EmpleadoResponse)
async def obtener_empleado_por_documento(
    numero_documento: str, db: Session = Depends(get_db)
):
    """Obtener un empleado por su número de documento."""
    try:
        empleado_crud = EmpleadoCRUD(db)
        empleado = empleado_crud.obtener_por_documento(numero_documento)
        if not empleado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Empleado no encontrado",
            )
        return empleado
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener empleado: {str(e)}",
        )


@router.post("/", response_model=EmpleadoResponse, status_code=status.HTTP_201_CREATED)
async def crear_empleado(
    empleado_data: EmpleadoCreate,
    db: Session = Depends(get_db),
    creado_por: Optional[UUID] = Query(None, description="UUID del usuario que crea el registro"),
    x_user_id: Optional[str] = Header(None, alias="X-User-ID"),
):
    """
    Crear un nuevo empleado.
    - Resuelve id_tipo_documento (usa TipoDocumentoCRUD)
    - Pasa un dict al EmpleadoCRUD.crear_empleado con id_tipo_documento incluido
    """
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
        
        tipo_doc_crud = TipoDocumentoCRUD(db)
        tipo_documento = tipo_doc_crud.obtener_por_id(
            str(empleado_data.id_tipo_documento)
        )

        if not tipo_documento:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tipo de documento no válido",
            )
        if hasattr(empleado_data, "model_dump"):
            datos = empleado_data.model_dump()
        else:
            datos = empleado_data.dict()

        datos["id_tipo_documento"] = tipo_documento.id_tipo_documento

        empleado_crud = EmpleadoCRUD(db)
        empleado = empleado_crud.crear_empleado(
            datos_entrada=datos,
            creado_por=usuario_id,
        )

        if not empleado:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo crear el empleado (revisar logs).",
            )

        return empleado

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
            detail=f"Error al crear empleado: {str(e)}",
        )


@router.put("/{id_empleado}", response_model=EmpleadoResponse)
async def actualizar_empleado(
    id_empleado: UUID,
    empleado_data: EmpleadoUpdate,
    db: Session = Depends(get_db),
    actualizado_por: Optional[UUID] = Query(None, description="UUID del usuario que realiza la actualización"),
    x_user_id: Optional[str] = Header(None, alias="X-User-ID"),
):
    """Actualizar un empleado existente."""
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
        
        empleado_crud = EmpleadoCRUD(db)
        empleado = empleado_crud.obtener_por_id(id_empleado)
        if not empleado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Empleado no encontrado"
            )

        if (
            hasattr(empleado_data, "id_tipo_documento")
            and empleado_data.id_tipo_documento
        ):
            tipo_doc_crud = TipoDocumentoCRUD(db)
            tipo_documento = tipo_doc_crud.obtener_por_id(
                str(empleado_data.id_tipo_documento).strip().upper()
            )
            if not tipo_documento:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Tipo de documento no encontrado: {empleado_data.id_tipo_documento}",
                )
            empleado_data_dict = empleado_data.dict(exclude_unset=True)
            empleado_data_dict["id_tipo_documento"] = tipo_documento.id_tipo_documento
        else:
            empleado_data_dict = empleado_data.dict(
                exclude_unset=True, exclude={"id_tipo_documento"}
            )

        empleado_actualizado = empleado_crud.actualizar_empleado(
            objeto_db=empleado,
            datos_entrada=empleado_data_dict,
            actualizado_por=usuario_id,
        )

        if not empleado_actualizado:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No se pudo actualizar el empleado",
            )

        return empleado_actualizado

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al actualizar cliente: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar cliente: {str(e)}",
        )


@router.delete("/{id_empleado}", response_model=RespuestaAPI)
async def eliminar_empleado(
    id_empleado: UUID,
    actualizado_por: Optional[UUID] = Query(None, description="UUID del usuario que realiza la eliminación"),
    db: Session = Depends(get_db),
    x_user_id: Optional[str] = Header(None, alias="X-User-ID"),
):
    """Eliminar un empleado. Soft delete."""
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
        
        empleado_crud = EmpleadoCRUD(db)
        empleado = empleado_crud.obtener_por_id(id_empleado)
        if not empleado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Empleado no encontrado"
            )
        eliminado = empleado_crud.desactivar_empleado(
            empleado_id=id_empleado, actualizado_por=usuario_id
        )
        if eliminado:
            return RespuestaAPI(mensaje="Empleado eliminado exitosamente", exito=True)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar empleado",
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
            detail=f"Error al eliminar empleado: {str(e)}",
        )
