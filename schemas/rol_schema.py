from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
import uuid


class RolBase(BaseModel):
    """Clase base para validación de roles"""

    nombre_rol: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Nombre del rol (cliente, empleado, administrador)",
    )

    @validator("nombre_rol")
    def validar_nombre(cls, v):
        if not v or not v.strip():
            raise ValueError("El nombre del rol no puede estar vacío")
        roles_validos = ["cliente", "empleado", "administrador"]
        if v.lower() not in roles_validos:
            raise ValueError(
                "El nombre del rol debe ser cliente, empleado o administrador"
            )
        return v.strip().title()


class RolCreate(RolBase):
    """Clase para validación de creación de roles"""

    pass


class RolUpdate(BaseModel):
    """Clase para validación de actualización de roles"""

    nombre_rol: Optional[str] = Field(None, min_length=3, max_length=50)
    activo: Optional[bool] = None

    @validator("nombre_rol")
    def validar_nombre(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError("El nombre del rol no puede estar vacío")
            roles_validos = ["cliente", "empleado", "administrador"]
            if v.lower() not in roles_validos:
                raise ValueError(
                    "El nombre del rol debe ser cliente, empleado o administrador"
                )
            return v.strip().title()
        return v


class RolResponse(BaseModel):
    """Esquema para respuesta de rol"""

    id_rol: str
    nombre_rol: str
    activo: bool
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class RolListResponse(BaseModel):
    """Esquema para lista de roles"""

    roles: List[RolResponse]
    pagina: int
    por_pagina: int

    class Config:
        from_attributes = True
