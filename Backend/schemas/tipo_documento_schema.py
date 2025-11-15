from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
import uuid


class TipoDocumentoBase(BaseModel):
    """Clase base para validación de tipos de documento"""
    
    nombre: str = Field(
        ..., min_length=1, max_length=50, description="Nombre del tipo de documento"
    )
    codigo: str = Field(
        ...,
        min_length=1,
        max_length=5,
        description="Código abreviado del tipo de documento",
    )
    numero: int = Field(..., gt=0, description="Número del documento")

    @validator("nombre")
    def validar_nombre(cls, v):
        if not v or not v.strip():
            raise ValueError("El nombre no puede estar vacío")
        nombres_validos = [
            "cédula",
            "pasaporte",
            "documento nacional",
            "tarjeta de identidad",
            "nit",
        ]
        if v.lower() not in nombres_validos:
            raise ValueError(f'El nombre debe ser uno de: {", ".join(nombres_validos)}')
        return v.strip().title()

    @validator("codigo")
    def validar_codigo(cls, v):
        if not v or not v.strip():
            raise ValueError("El código no puede estar vacío")
        codigos_validos = ["cc", "pa", "dn", "ti", "nit"]
        if v.lower() not in codigos_validos:
            raise ValueError(f'El código debe ser uno de: {", ".join(codigos_validos)}')
        return v.strip().upper()

    @validator("numero")
    def validar_numero(cls, v):
        if v <= 0:
            raise ValueError("El número debe ser mayor a 0")
        return v


class TipoDocumentoCreate(TipoDocumentoBase):
    """Clase para validación de creación de tipos de documento"""
    pass


class TipoDocumentoUpdate(BaseModel):
    """Clase para validación de actualización de tipos de documento"""
    
    nombre: Optional[str] = Field(None, min_length=1, max_length=50)
    codigo: Optional[str] = Field(None, min_length=1, max_length=5)
    numero: Optional[int] = Field(None, gt=0)
    activo: Optional[bool] = None

    @validator("nombre")
    def validar_nombre(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError("El nombre no puede estar vacío")
            nombres_validos = [
                "cédula",
                "pasaporte",
                "documento nacional",
                "tarjeta de identidad",
                "nit",
            ]
            if v.lower() not in nombres_validos:
                raise ValueError(
                    f'El nombre debe ser uno de: {", ".join(nombres_validos)}'
                )
            return v.strip().title()
        return v

    @validator("codigo")
    def validar_codigo(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError("El código no puede estar vacío")
            codigos_validos = ["cc", "pa", "dn", "ti", "nit"]
            if v.lower() not in codigos_validos:
                raise ValueError(
                    f'El código debe ser uno de: {", ".join(codigos_validos)}'
                )
            return v.strip().upper()
        return v

    @validator("numero")
    def validar_numero(cls, v):
        if v is not None and v <= 0:
            raise ValueError("El número debe ser mayor a 0")
        return v


class TipoDocumentoResponse(BaseModel):
    """Esquema para respuesta de tipo de documento"""
    
    id_tipo_documento: uuid.UUID
    nombre: str
    codigo: str
    numero: int
    activo: bool
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None
    creado_por: str
    actualizado_por: str

    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class TipoDocumentoListResponse(BaseModel):
    """Esquema para lista de tipos de documento"""
    
    tipos_documento: List[TipoDocumentoResponse]
    pagina: int
    por_pagina: int

    class Config:
        from_attributes = True
