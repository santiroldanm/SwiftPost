"""API de Usuarios - Endpoints para gestión de usuarios"""

from typing import List
from uuid import UUID
from database.config import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from cruds.usuario_crud import UsuarioCRUD
from cruds.rol_crud import RolCRUD
from schemas.auth_schema import RespuestaAPI
from schemas.usuario_schema import (
    UsuarioCreate,
    UsuarioUpdate,
    UsuarioResponse,
    CambioPassword,
)

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])


@router.get("/", response_model=List[UsuarioResponse])
async def obtener_usuarios(
    skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    """Obtener todos los usuarios con paginación."""
    try:
        usuario_crud = UsuarioCRUD(db)
        usuarios = usuario_crud.obtener_usuarios(skip=skip, limit=limit)
        return usuarios
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener usuarios: {str(e)}",
        )


@router.get("/{usuario_id}", response_model=UsuarioResponse)
async def obtener_usuario_por_id(usuario_id: UUID, db: Session = Depends(get_db)):
    """Obtener un usuario por ID."""
    try:
        usuario_crud = UsuarioCRUD(db)
        usuario = usuario_crud.obtener_por_id(usuario_id)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
            )
        return usuario
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener usuario: {str(e)}",
        )


@router.get("/username/{nombre_usuario}", response_model=UsuarioResponse)
async def obtener_usuario_nombre_usuario(
    nombre_usuario: str, db: Session = Depends(get_db)
):
    """Obtener un usuario por nombre de usuario."""
    try:
        usuario_crud = UsuarioCRUD(db)
        usuario = usuario_crud.obtener_por_nombre_usuario(nombre_usuario)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
            )
        return usuario
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener usuario: {str(e)}",
        )


@router.get("/admin/lista", response_model=List[UsuarioResponse])
async def obtener_usuarios_admin(db: Session = Depends(get_db)):
    """Obtener todos los usuarios administradores."""
    try:
        usuario_crud = UsuarioCRUD(db)
        admins = usuario_crud.obtener_usuarios_admin()
        return admins
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener administradores: {str(e)}",
        )


@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def crear_usuario(usuario_data: UsuarioCreate, db: Session = Depends(get_db)):
    """
    Crear un nuevo usuario.

    Roles disponibles:
    - admin
    - empleado
    - cliente
    """
    try:
        rol_crud = RolCRUD(db)
        rol = rol_crud.obtener_rol_por_nombre(
            nombre=usuario_data.id_rol.lower(), exacto=True, case_sensitive=False
        )

        if not rol:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rol no válido. Debe ser uno de: admin, empleado, cliente",
            )

        if not rol:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Rol no válido. Debe ser uno de: admin, empleado, cliente",
            )

        usuario_crud = UsuarioCRUD(db)
        usuario = usuario_crud.crear_usuario(
            nombre_usuario=usuario_data.nombre_usuario,
            password=usuario_data.password,
            id_rol=str(rol.id_rol),
        )
        return usuario

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear usuario: {str(e)}",
        )


@router.put("/{usuario_id}", response_model=UsuarioResponse)
async def actualizar_usuario(
    usuario_id: UUID, usuario_data: UsuarioUpdate, db: Session = Depends(get_db)
):
    """Actualizar un usuario existente."""
    try:
        usuario_crud = UsuarioCRUD(db)

        usuario_existente = usuario_crud.obtener_por_id(usuario_id)
        if not usuario_existente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
            )

        campos_actualizacion = {
            k: v for k, v in usuario_data.dict().items() if v is not None
        }

        if "id_rol" in campos_actualizacion:
            rol = RolCRUD(db).obtener_rol_por_nombre(
                nombre=campos_actualizacion["id_rol"].lower(),
                exacto=True,
                case_sensitive=False,
            )
            if not rol:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Rol con ID {campos_actualizacion['id_rol']} no encontrado",
                )
            campos_actualizacion["id_rol"] = str(rol.id_rol)

        if not campos_actualizacion:
            return usuario_existente

        usuario_actualizado = usuario_crud.actualizar_usuario(
            usuario_db=usuario_existente,
            datos_actualizacion=campos_actualizacion,
            actualizado_por=usuario_id,
        )
        return usuario_actualizado
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar usuario: {str(e)}",
        )


@router.delete("/{usuario_id}", response_model=RespuestaAPI)
async def eliminar_usuario(usuario_id: UUID, db: Session = Depends(get_db)):
    """Eliminar un usuario. Soft delete."""
    try:
        usuario_crud = UsuarioCRUD(db)

        usuario_existente = usuario_crud.obtener_por_id(usuario_id)
        if not usuario_existente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
            )

        eliminado = usuario_crud.eliminar_usuario(usuario_id)
        if eliminado:
            return RespuestaAPI(mensaje="Usuario eliminado exitosamente", exito=True)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar usuario",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar usuario: {str(e)}",
        )


@router.post("/{usuario_id}/cambiar-password", response_model=RespuestaAPI)
async def cambiar_contraseña(
    usuario_id: UUID, cambio_data: CambioPassword, db: Session = Depends(get_db)
):
    """Cambiar la contraseña de un usuario."""
    try:
        usuario_crud = UsuarioCRUD(db)
        usuario_existente = usuario_crud.obtener_por_id(usuario_id)
        if not usuario_existente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado"
            )

        if usuario_existente.password != cambio_data.contraseña_actual:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña actual no es correcta",
            )

        cambio_exitoso = usuario_crud.actualizar_contrasena(
            usuario_db=usuario_existente,
            nueva_contrasena=cambio_data.nueva_contraseña,
            id_usuario_actualizacion=usuario_id,
        )

        if cambio_exitoso:
            return RespuestaAPI(mensaje="Contraseña cambiada exitosamente", exito=True)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al cambiar contraseña",
            )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al cambiar contraseña: {str(e)}",
        )


@router.get("/{usuario_id}/es-admin", response_model=RespuestaAPI)
async def verificar_es_admin(usuario_id: UUID, db: Session = Depends(get_db)):
    """Verificar si un usuario es administrador."""
    try:
        usuario_crud = UsuarioCRUD(db)
        es_admin = usuario_crud.es_admin(usuario_id)
        return RespuestaAPI(
            mensaje=f"El usuario {'es' if es_admin else 'no es'} administrador",
            exito=True,
            datos={"es_admin": es_admin},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al verificar administrador: {str(e)}",
        )
