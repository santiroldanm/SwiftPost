from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import Field, validator
import uuid


class DetalleEntregaBase(BaseModel):
    id_sede_remitente: UUID = Field(..., description="ID de la sede remitente")
    id_sede_receptora: UUID = Field(..., description="ID de la sede receptora")
    id_paquete: UUID = Field(..., description="ID del paquete asociado")
    id_cliente_remitente: UUID = Field(..., description="ID del cliente que envía")
    id_cliente_receptor: UUID = Field(..., description="ID del cliente que recibe")
    estado_envio: str = Field(
        default="Pendiente", description="Estado actual del envío"
    )
    fecha_envio: datetime = Field(..., description="Fecha de envío del paquete")
    fecha_entrega: Optional[datetime] = Field(
        None, description="Fecha de entrega del paquete"
    )
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

    @validator("observaciones")
    def validar_observaciones(cls, v):
        if v is not None and v.strip():
            if len(v.strip()) < 5:
                raise ValueError("Las observaciones deben tener al menos 5 caracteres")
            return v.strip()
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


class DetalleEntregaResponse(BaseModel):
    id_detalle: uuid.UUID
    id_sede_remitente: UUID
    id_sede_receptora: UUID
    id_paquete: UUID
    id_cliente_remitente: UUID
    id_cliente_receptor: UUID
    estado_envio: str
    fecha_envio: datetime
    fecha_entrega: Optional[datetime] = None
    observaciones: Optional[str] = None
    activo: bool
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None
    creado_por: UUID
    actualizado_por: UUID

    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class DetalleEntregaListResponse(BaseModel):
    detalles: List[DetalleEntregaResponse]
    pagina: int
    por_pagina: int

    class Config:
        from_attributes = True
