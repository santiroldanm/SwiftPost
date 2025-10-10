from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID
from pydantic import Field, validator
import re
import uuid


class SedeBase(BaseModel):
    nombre: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Nombre de la sede",
    )
    ciudad: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Ciudad donde se encuentra la sede",
    )
    direccion: str = Field(
        ..., min_length=5, max_length=200, description="Dirección física de la sede"
    )
    telefono: str = Field(
        ..., min_length=7, max_length=15, description="Número de teléfono de la sede"
    )
    latitud: Optional[float] = Field(
        None, ge=-90, le=90, description="Latitud en grados decimales (-90 a 90)"
    )
    longitud: Optional[float] = Field(
        None, ge=-180, le=180, description="Longitud en grados decimales (-180 a 180)"
    )
    altitud: Optional[float] = Field(
        None, description="Altitud en metros sobre el nivel del mar"
    )

    @validator("nombre")
    def validar_nombre(cls, v):
        if not v or not v.strip():
            raise ValueError("El nombre no puede estar vacío")
        if len(v.strip()) < 2:
            raise ValueError("El nombre debe tener al menos 2 caracteres")
        return v.strip().title()

    @validator("ciudad")
    def validar_ciudad(cls, v):
        if not v or not v.strip():
            raise ValueError("La ciudad no puede estar vacía")
        if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", v):
            raise ValueError("La ciudad solo puede contener letras y espacios")
        return v.strip().title()

    @validator("direccion")
    def validar_direccion(cls, v):
        if not v or not v.strip():
            raise ValueError("La dirección no puede estar vacía")
        if len(v.strip()) < 5:
            raise ValueError("La dirección debe tener al menos 5 caracteres")
        return v.strip().title()

    @validator("telefono")
    def validar_telefono(cls, v):
        if not v or not v.strip():
            raise ValueError("El teléfono no puede estar vacío")
        telefono_limpio = "".join(filter(str.isdigit, v))
        if not telefono_limpio.isdigit():
            raise ValueError("El teléfono solo puede contener números")
        if len(telefono_limpio) < 7 or len(telefono_limpio) > 15:
            raise ValueError("El teléfono debe tener entre 7 y 15 dígitos")
        return telefono_limpio


class SedeCreate(SedeBase):
    pass


class SedeUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    ciudad: Optional[str] = Field(None, min_length=2, max_length=50)
    direccion: Optional[str] = Field(None, min_length=5, max_length=200)
    telefono: Optional[str] = Field(None, min_length=7, max_length=15)
    activo: Optional[bool] = None

    @validator("nombre")
    def validar_nombre(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError("El nombre no puede estar vacío")
            if len(v.strip()) < 2:
                raise ValueError("El nombre debe tener al menos 2 caracteres")
            return v.strip().title()
        return v

    @validator("ciudad")
    def validar_ciudad(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError("La ciudad no puede estar vacía")
            if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$", v):
                raise ValueError("La ciudad solo puede contener letras y espacios")
            return v.strip().title()
        return v

    @validator("direccion")
    def validar_direccion(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError("La dirección no puede estar vacía")
            if len(v.strip()) < 5:
                raise ValueError("La dirección debe tener al menos 5 caracteres")
            return v.strip().title()
        return v

    @validator("telefono")
    def validar_telefono(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError("El teléfono no puede estar vacío")
            telefono_limpio = "".join(filter(str.isdigit, v))
            if not telefono_limpio.isdigit():
                raise ValueError("El teléfono solo puede contener números")
            if len(telefono_limpio) < 7 or len(telefono_limpio) > 15:
                raise ValueError("El teléfono debe tener entre 7 y 15 dígitos")
            return telefono_limpio
        return v


class SedeResponse(SedeBase):
    id_sede: UUID
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None
    creado_por: str
    actualizado_por: Optional[str] = None

    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class SedeListResponse(BaseModel):
    sedes: List[SedeResponse]
    total: int
    pagina: int
    por_pagina: int

    class Config:
        from_attributes = True
