"""
API de Clientes - Endpoints para gestión de clientes
"""

from typing import List
from uuid import UUID
from database.config import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from cruds.cliente_crud import ClienteCRUD
from cruds.tipo_documento_crud import TipoDocumentoCRUD
from schemas.cliente_schema import (
    ClienteCreate,
    ClienteUpdate,
    ClienteResponse,
)
from schemas.auth_schema import RespuestaAPI

router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.get("/", response_model=List[ClienteResponse])
async def obtener_clientes(
    skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    """Obtener todos los clientes con paginación."""
    try:
        cliente_crud = ClienteCRUD(db)
        clientes = cliente_crud.obtener_clientes(skip=skip, limit=limit)
        return clientes
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener clientes: {str(e)}",
        )


@router.get("/activos", response_model=List[ClienteResponse])
async def obtener_clientes_activos(
    skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    """Obtener todos los clientes activos con paginación."""
    try:
        cliente_crud = ClienteCRUD(db)
        clientes = cliente_crud.obtener_activos(skip=skip, limit=limit)
        return clientes
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener clientes activos: {str(e)}",
        )


@router.get("/{id_cliente}", response_model=ClienteResponse)
async def obtener_cliente_por_id(id_cliente: UUID, db: Session = Depends(get_db)):
    """Obtener un cliente por su ID."""
    try:
        cliente_crud = ClienteCRUD(db)
        cliente = cliente_crud.obtener_por_id(id_cliente)
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente no encontrado",
            )
        return cliente
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener cliente: {str(e)}",
        )


@router.get("/tipo/{tipo}", response_model=List[ClienteResponse])
async def obtener_clientes_por_tipo(
    tipo: str, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    """Obtener todos los clientes por tipo con paginación."""
    try:
        cliente_crud = ClienteCRUD(db)
        clientes = cliente_crud.obtener_por_tipo(tipo, skip=skip, limit=limit)
        return clientes
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener clientes por tipo: {str(e)}",
        )


@router.get("/documento/{numero_documento}", response_model=ClienteResponse)
async def obtener_cliente_por_documento(
    numero_documento: str, db: Session = Depends(get_db)
):
    """Obtener un cliente por su número de documento."""
    try:
        cliente_crud = ClienteCRUD(db)
        cliente = cliente_crud.obtener_por_documento(numero_documento)
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cliente no encontrado",
            )
        return cliente
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener cliente: {str(e)}",
        )


@router.post("/", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
async def crear_cliente(
    cliente_data: ClienteCreate,
    db: Session = Depends(get_db),
    usuario_id: UUID = "ID Usuario con la sesión activa",
):
    """Crear un nuevo cliente."""
    try:
        tipo_doc_crud = TipoDocumentoCRUD(db)
        tipo_documento = tipo_doc_crud.obtener_por_codigo(
            str(cliente_data.id_tipo_documento)
        )

        if not tipo_documento:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tipo de documento no válido",
            )

        cliente_crud = ClienteCRUD(db)
        cliente = cliente_crud.crear_cliente(
            datos_entrada=cliente_data.dict(exclude={"id_tipo_documento"}),
            usuario_id=usuario_id,
            id_tipo_documento=tipo_documento.id_tipo_documento,
        )
        return cliente
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear cliente: {str(e)}",
        )


@router.put("/{id_cliente}", response_model=ClienteResponse)
async def actualizar_cliente(
    id_cliente: UUID,
    cliente_data: ClienteUpdate,
    db: Session = Depends(get_db),
    usuario_id: UUID = "ID Usuario con la sesión activa",
):
    """Actualizar un cliente existente."""
    try:
        cliente_crud = ClienteCRUD(db)
        cliente = cliente_crud.obtener_por_id(id_cliente)
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado"
            )

        if (
            hasattr(cliente_data, "id_tipo_documento")
            and cliente_data.id_tipo_documento
        ):
            tipo_doc_crud = TipoDocumentoCRUD(db)
            tipo_documento = tipo_doc_crud.obtener_por_codigo(
                str(cliente_data.id_tipo_documento).strip().upper()
            )
            if not tipo_documento:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Tipo de documento no encontrado: {cliente_data.id_tipo_documento}",
                )
            cliente_data_dict = cliente_data.dict(exclude_unset=True)
            cliente_data_dict["id_tipo_documento"] = tipo_documento.id_tipo_documento
        else:
            cliente_data_dict = cliente_data.dict(
                exclude_unset=True, exclude={"id_tipo_documento"}
            )

        cliente_actualizado = cliente_crud.actualizar_cliente(
            objeto_db=cliente,
            datos_entrada=cliente_data_dict,
            actualizado_por=usuario_id,
        )

        if not cliente_actualizado:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No se pudo actualizar el cliente",
            )

        return cliente_actualizado

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error al actualizar cliente: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar cliente: {str(e)}",
        )


@router.delete("/{id_cliente}", response_model=RespuestaAPI)
async def eliminar_cliente(
    id_cliente: UUID,
    usuario_id: UUID = "ID Usuario con la sesión activa",
    db: Session = Depends(get_db),
):
    """Eliminar un cliente. Soft delete."""
    try:
        cliente_crud = ClienteCRUD(db)
        cliente = cliente_crud.obtener_por_id(id_cliente)
        if not cliente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado"
            )
        eliminado = cliente_crud.eliminar_cliente(
            cliente_id=id_cliente, actualizado_por=usuario_id
        )
        if eliminado:
            return RespuestaAPI(mensaje="Cliente eliminado exitosamente", exito=True)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar cliente",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar cliente: {str(e)}",
        )
