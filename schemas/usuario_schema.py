"""
Modelos Pydantic para las respuestas de usuarios de la API
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from pydantic import Field, validator
import re
import string
import uuid


class UsuarioBase(BaseModel):
    nombre_usuario: str = Field(
        ..., min_length=4, max_length=50, description="Nombre de usuario único"
    )
    password: str = Field(..., min_length=8, description="Contraseña del usuario")
    id_rol: str = Field(..., min_length=1, description="ID del rol (FK roles.id_rol)")

    @validator("nombre_usuario")
    def validar_nombre_usuario(cls, v):
        if not v or not v.strip():
            raise ValueError("El nombre de usuario no puede estar vacío")
        if not re.match(r"^[a-zA-Z0-9._]+$", v):
            raise ValueError(
                "El nombre de usuario solo puede contener letras, números y guiones bajos o puntos"
            )
        return v.strip()

    @validator("password")
    def validar_contraseña(cls, v):
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        if not any(c.isupper() for c in v):
            raise ValueError("La contraseña debe contener al menos una letra mayúscula")
        if not any(c.islower() for c in v):
            raise ValueError("La contraseña debe contener al menos una letra minúscula")
        if not any(c.isdigit() for c in v):
            raise ValueError("La contraseña debe contener al menos un número")
        if not any(c in string.punctuation for c in v):
            raise ValueError(
                "La contraseña debe contener al menos un carácter especial"
            )
        return v


class UsuarioCreate(UsuarioBase):
    pass


class UsuarioUpdate(BaseModel):
    nombre_usuario: Optional[str] = Field(None, min_length=4, max_length=50)
    id_rol: Optional[str] = Field(None, min_length=1)

    @validator("nombre_usuario")
    def validar_nombre_usuario(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError("El nombre de usuario no puede estar vacío")
            if not re.match(r"^[a-zA-Z0-9._]+$", v):
                raise ValueError(
                    "El nombre de usuario solo puede contener letras, números y guiones bajos o puntos"
                )
            return v.strip()
        return v

    @validator("id_rol")
    def validar_id_rol(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError("El ID del rol no puede estar vacío")
            return v.strip()
        return v


class UsuarioResponse(UsuarioBase):
    id_usuario: uuid.UUID
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class UsuarioListResponse(BaseModel):
    usuarios: List[UsuarioResponse]
    total: int
    pagina: int
    por_pagina: int

    class Config:
        from_attributes = True


class UsuarioCreateWithRole(BaseModel):
    nombre_usuario: str
    password: str
    rol: str


class CambioPassword(BaseModel):
    contraseña_actual: str
    nueva_contraseña: str


class UsuarioLogin(BaseModel):
    nombre_usuario: str
    contraseña: str
