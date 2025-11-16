"""
API de Autenticación - Endpoints para login y autenticación
"""

from uuid import UUID
import uuid
from cruds.usuario_crud import UsuarioCRUD
from database.config import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from schemas.auth_schema import RespuestaAPI
from schemas.usuario_schema import UsuarioResponse, UsuarioLogin
from sqlalchemy.orm import Session
from entities.rol import Rol
from auth.security import *

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=UsuarioResponse)
async def login(login_data: UsuarioLogin, db: Session = Depends(get_db)):
    """Autenticar un usuario con nombre de usuario/email y contraseña."""
    try:
        nombre_usuario = login_data.nombre_usuario.strip() if login_data.nombre_usuario else ""
        contraseña = login_data.contraseña.strip() if login_data.contraseña else ""
        
        if not nombre_usuario or not contraseña:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nombre de usuario y contraseña son requeridos",
            )
        
        usuario_crud = UsuarioCRUD(db)
        usuario = usuario_crud.autenticar(nombre_usuario, contraseña)

        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas o usuario inactivo",
            )

        if not usuario.activo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Su cuenta está inactiva. Contacte al administrador.",
            )

        rol = db.query(Rol).filter(Rol.id_rol == usuario.id_rol).first()
        
        rol_data = None
        if rol:
            rol_data = {
                "id_rol": str(rol.id_rol),
                "nombre_rol": rol.nombre_rol,
                "descripcion": getattr(rol, 'descripcion', None)
            }

        try:
            usuario_id = uuid.UUID(usuario.id_usuario) if isinstance(usuario.id_usuario, str) else usuario.id_usuario
        except (ValueError, AttributeError):
            usuario_id = usuario.id_usuario

        return UsuarioResponse(
            id_usuario=usuario_id,
            nombre_usuario=usuario.nombre_usuario,
            id_rol=str(usuario.id_rol),
            activo=usuario.activo,
            fecha_creacion=usuario.fecha_creacion,
            fecha_actualizacion=usuario.fecha_actualizacion,
            rol=rol_data
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error durante el login: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error durante el login: {str(e)}",
        )


@router.post("/crear-admin", response_model=RespuestaAPI)
async def crear_usuario_admin(db: Session = Depends(get_db)):
    """Crear o activar usuario administrador por defecto."""
    try:
        usuario_crud = UsuarioCRUD(db)
        admin_existente = usuario_crud.obtener_por_nombre_usuario(nombre_usuario="admin")
        
        contraseña_admin = "Admin12345."
        
        if admin_existente:
            if not admin_existente.activo:
                admin_existente.activo = True
                admin_existente.password = contraseña_admin
                admin_existente.fecha_actualizacion = datetime.now()
                db.commit()
                db.refresh(admin_existente)
                return RespuestaAPI(
                    mensaje="Usuario administrador activado exitosamente",
                    exito=True,
                    datos={
                        "admin_id": str(admin_existente.id_usuario),
                        "contraseña_temporal": contraseña_admin,
                        "mensaje": "IMPORTANTE: Cambie esta contraseña en su primer inicio de sesión",
                    },
                )
            else:
                return RespuestaAPI(
                    mensaje="Ya existe un usuario administrador activo",
                    exito=True,
                    datos={"admin_id": str(admin_existente.id_usuario)},
                )

        admin = usuario_crud.crear_usuario(
            nombre_usuario="admin",
            password=contraseña_admin,
            id_rol="df1af3be-ed77-48b3-bf43-834c517985b0",
        )

        return RespuestaAPI(
            mensaje="Usuario administrador creado exitosamente",
            exito=True,
            datos={
                "admin_id": str(admin.id_usuario),
                "contraseña_temporal": contraseña_admin,
                "mensaje": "IMPORTANTE: Cambie esta contraseña en su primer inicio de sesión",
            },
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de validación: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear administrador: {str(e)}",
        )


@router.get("/verificar/{usuario_id}", response_model=RespuestaAPI)
async def verificar_usuario(usuario_id: UUID, db: Session = Depends(get_db)):
    """Verificar si un usuario existe y está activo."""
    try:
        usuario_crud = UsuarioCRUD(db)
        usuario = usuario_crud.obtener_por_id(usuario_id)

        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado",
            )

        return RespuestaAPI(
            mensaje="Usuario verificado exitosamente",
            exito=True,
            datos={
                "usuario_id": str(usuario.id_usuario),
                "nombre_usuario": usuario.nombre_usuario,
                "rol": usuario.rol.nombre_rol,
                "activo": usuario.activo,
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al verificar usuario: {str(e)}",
        )


@router.get("/estado", response_model=RespuestaAPI)
async def estado_autenticacion():
    """Verificar el estado del sistema de autenticación."""
    return RespuestaAPI(
        mensaje="Sistema de autenticación funcionando correctamente",
        exito=True,
        datos={
            "sistema": "Sistema de Gestión de Productos",
            "version": "1.0.0",
            "autenticacion": "Activa",
        },
    )


@router.patch("/activar-usuario/{nombre_usuario}", response_model=RespuestaAPI)
async def activar_usuario(nombre_usuario: str, db: Session = Depends(get_db)):
    """Activar un usuario por nombre de usuario."""
    try:
        usuario_crud = UsuarioCRUD(db)
        usuario = usuario_crud.obtener_por_nombre_usuario(nombre_usuario=nombre_usuario)
        
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario '{nombre_usuario}' no encontrado",
            )
        
        if usuario.activo:
            return RespuestaAPI(
                mensaje=f"El usuario '{nombre_usuario}' ya está activo",
                exito=True,
                datos={"usuario_id": str(usuario.id_usuario), "activo": True},
            )
        
        usuario.activo = True
        usuario.fecha_actualizacion = datetime.now()
        db.commit()
        db.refresh(usuario)
        
        return RespuestaAPI(
            mensaje=f"Usuario '{nombre_usuario}' activado exitosamente",
            exito=True,
            datos={"usuario_id": str(usuario.id_usuario), "activo": True},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al activar usuario: {str(e)}",
        )
