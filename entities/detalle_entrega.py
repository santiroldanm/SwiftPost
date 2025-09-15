from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from ..database.database import Base
from datetime import datetime
from uuid import UUID, uuid4


class DetalleEntrega(Base):
    """
    Modelo de DetalleEntrega que representa la tabla 'detalles_entrega'
    Atributos:
        id_detalle: Identificador único del detalle de entrega
        id_sede_remitente: ID de la sede remitente
        id_sede_receptora: ID de la sede receptora
        id_paquete: ID del paquete asociado
        estado_envio: Estado actual del envío (Entregado, En transito, Pendiente)
        id_cliente_remitente: ID del cliente que envía
        id_cliente_receptor: ID del cliente que recibe
        fecha_envio: Fecha de envío
        fecha_entrega: Fecha de entrega
        observaciones: Observaciones adicionales
        activo: Estado del registro (activo/inactivo)
        fecha_creacion: Fecha y hora de creación
        fecha_actualizacion: Fecha y hora de última actualización
    """

    __tablename__ = "detalles_entrega"
    id_detalle = Column(UUID, primary_key=True, default=uuid4)
    id_sede_remitente = Column(UUID, ForeignKey("sedes.id_sede"), nullable=False)
    id_sede_receptora = Column(UUID, ForeignKey("sedes.id_sede"), nullable=False)
    id_paquete = Column(UUID, ForeignKey("paquetes.id"), nullable=False)
    estado_envio = Column(String(20), default="Pendiente", nullable=False)
    id_cliente_remitente = Column(
        UUID, ForeignKey("clientes.id_cliente"), nullable=False
    )
    id_cliente_receptor = Column(
        UUID, ForeignKey("clientes.id_cliente"), nullable=False
    )
    fecha_envio = Column(DateTime, nullable=False)
    fecha_entrega = Column(DateTime, nullable=True)
    observaciones = Column(String(500), nullable=True)
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.now, nullable=False)
    fecha_actualizacion = Column(DateTime, default=None, onupdate=datetime.now)
    creado_por = Column(UUID, ForeignKey("usuarios.id_usuario"), nullable=False)
    actualizado_por = Column(UUID, ForeignKey("usuarios.id_usuario"), nullable=False)

    sede_remitente = relationship(
        "Sede", foreign_keys=[id_sede_remitente], back_populates="sede_remitente"
    )
    sede_receptora = relationship(
        "Sede", foreign_keys=[id_sede_receptora], back_populates="sede_receptora"
    )
    paquete = relationship("Paquete", back_populates="detalles_entrega")
    cliente_remitente = relationship(
        "Cliente",
        foreign_keys=[id_cliente_remitente],
        back_populates="cliente_remitente",
    )
    cliente_receptor = relationship(
        "Cliente", foreign_keys=[id_cliente_receptor], back_populates="cliente_receptor"
    )
    usuarios = relationship("Usuario", back_populates="detalles_entrega")

    def __repr__(self):
        return f"<DetalleEntrega(id_detalle={self.id_detalle}, estado={self.estado_envio}, paquete={self.id_paquete}), cliente_remitente={self.id_cliente_remitente}, cliente_receptor={self.id_cliente_receptor}), fecha_envio={self.fecha_envio}, fecha_entrega={self.fecha_entrega}, observaciones={self.observaciones}, id_sede_remitente={self.id_sede_remitente}, id_sede_receptora={self.id_sede_receptora})>"


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
    id_detalle: UUID
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
