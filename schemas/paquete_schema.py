from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID
from pydantic import Field, validator
import re
import uuid


class PaqueteBase(BaseModel):
    peso: float = Field(..., gt=0, description="Peso del paquete en kilogramos")
    tamaño: str = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Tamaño del paquete (Pequeño, Mediano, Grande, Gigante)",
    )
    fragilidad: str = Field(
        ...,
        min_length=1,
        max_length=8,
        description="Nivel de fragilidad del paquete (Baja, Normal, Alta)",
    )
    contenido: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Contenido (descripción) del paquete",
    )
    tipo: str = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Tipo de paquete (Normal, Express)",
    )
    valor_declarado: float = Field(
        default=0.0,
        ge=0,
        description="Valor declarado del paquete para fines de seguro",
    )
    estado: Optional[str] = Field(
        default="registrado",
        min_length=1,
        max_length=20,
        description="Estado actual del paquete (registrado, en_transito, etc.)",
    )

    @validator("peso")
    def validar_peso(cls, v):
        if v < 0:
            raise ValueError("El peso debe ser mayor a 0")
        return v

    @validator("tamaño")
    def validar_tamaño(cls, v):
        tamaños_validos = ["pequeño", "mediano", "grande", "gigante"]
        if v.lower() not in tamaños_validos:
            raise ValueError(f'El tamaño debe ser uno de: {", ".join(tamaños_validos)}')
        return v.strip()

    @validator("fragilidad")
    def validar_fragilidad(cls, v):
        fragilidades_validas = ["baja", "normal", "alta"]
        if v.lower() not in fragilidades_validas:
            raise ValueError(
                f'La fragilidad debe ser una de: {", ".join(fragilidades_validas)}'
            )
        return v.strip()

    @validator("contenido")
    def validar_contenido(cls, v):
        if v and len(v) < 1:
            raise ValueError("El contenido no puede estar vacío")
        return v.strip().title()

    @validator("tipo")
    def validar_tipo(cls, v):
        tipos_validos = ["normal", "express"]
        if v.lower() not in tipos_validos:
            raise ValueError(f'El tipo debe ser uno de: {", ".join(tipos_validos)}')
        return v.strip()


class PaqueteCreate(PaqueteBase):
    pass


class PaqueteUpdate(BaseModel):
    peso: Optional[float] = Field(None, gt=0)
    tamaño: Optional[str] = Field(None, min_length=1, max_length=10)
    fragilidad: Optional[str] = Field(None, min_length=1, max_length=8)
    contenido: Optional[str] = Field(None, min_length=1, max_length=1000)
    tipo: Optional[str] = Field(None, min_length=1, max_length=10)
    valor_declarado: Optional[float] = Field(None, ge=0)
    estado: Optional[str] = Field(None, min_length=1, max_length=20)

    @validator("peso")
    def validar_peso(cls, v):
        if v is not None and v < 0:
            raise ValueError("El peso debe ser mayor o igual a 0")
        return v

    @validator("tamaño")
    def validar_tamaño(cls, v):
        tamaños_validos = ["pequeño", "mediano", "grande", "gigante"]
        if v is not None and v.lower() not in tamaños_validos:
            raise ValueError(f'El tamaño debe ser uno de: {", ".join(tamaños_validos)}')
        return v.strip().title()

    @validator("fragilidad")
    def validar_fragilidad(cls, v):
        fragilidades_validas = ["baja", "normal", "alta"]
        if v is not None and v.lower() not in fragilidades_validas:
            raise ValueError(
                f'La fragilidad debe ser una de: {", ".join(fragilidades_validas)}'
            )
        return v.strip().title()

    @validator("contenido")
    def validar_contenido(cls, v):
        if v is not None and len(v) < 1:
            raise ValueError("El contenido no puede estar vacío")
        return v.strip().title()

    @validator("tipo")
    def validar_tipo(cls, v):
        tipos_validos = ["normal", "express"]
        if v is not None and v.lower() not in tipos_validos:
            raise ValueError(f'El tipo debe ser uno de: {", ".join(tipos_validos)}')
        return v.strip()


class PaqueteResponse(PaqueteBase):
    id_paquete: uuid.UUID
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None
    creado_por: str
    actualizado_por: Optional[str] = None

    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class PaqueteListResponse(BaseModel):
    paquetes: List[PaqueteResponse]
    total: int
    pagina: int
    por_pagina: int

    class Config:
        from_attributes = True
