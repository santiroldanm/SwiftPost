from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import Field, validator
import uuid


class DetalleEntregaBase(BaseModel):
    estado_envio: str = Field(..., description="Estado actual del envío")
    fecha_envio: datetime = Field(..., description="Fecha de envío del paquete")
    observaciones: Optional[str] = Field(
        None, max_length=500, description="Observaciones adicionales"
    )

    @validator("estado_envio")
    def validar_estado_envio(cls, v):
        if v not in ["Pendiente", "En transito", "Entregado"]:
            raise ValueError(
                'El estado del envío debe ser "Pendiente", "En transito" o "Entregado"'
            )
        return v

    @validator("fecha_envio")
    def validar_fecha_envio(cls, v):
        if v < datetime.now():
            raise ValueError("La fecha de envío no puede ser en el pasado")
        return v

    @validator("observaciones")
    def validar_observaciones(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError("Las observaciones no pueden estar vacías")
            if len(v.strip()) < 5:
                raise ValueError("Las observaciones deben tener al menos 5 caracteres")
            return v.strip().title()
        return v


class DetalleEntregaCreate(DetalleEntregaBase):
    pass


class DetalleEntregaUpdate(BaseModel):
    estado_envio: Optional[str] = None
    fecha_entrega: Optional[datetime] = None
    observaciones: Optional[str] = Field(None, max_length=500)

    @validator("estado_envio")
    def validar_estado_envio(cls, v):
        if v not in ["Pendiente", "En transito", "Entregado"]:
            raise ValueError(
                'El estado del envío debe ser "Pendiente", "En transito" o "Entregado"'
            )
        return v

    @validator("fecha_entrega")
    def validar_fecha_entrega(cls, v, values):
        if v and "fecha_envio" in values and v < values["fecha_envio"]:
            raise ValueError(
                "La fecha de entrega no puede ser anterior a la fecha de envío"
            )
        return v

    @validator("observaciones")
    def validar_observaciones(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError("Las observaciones no pueden estar vacías")
            if len(v.strip()) < 5:
                raise ValueError("Las observaciones deben tener al menos 5 caracteres")
            return v.strip().title()
        return v


class DetalleEntregaResponse(DetalleEntregaBase):
    id_detalle: uuid.UUID
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None
    creado_por: str
    actualizado_por: Optional[str] = None

    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class DetalleEntregaListResponse(BaseModel):
    detalles: List[DetalleEntregaResponse]
    total: int
    pagina: int
    por_pagina: int

    class Config:
        from_attributes = True
