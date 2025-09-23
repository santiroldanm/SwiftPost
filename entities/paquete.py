from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from database.config import Base
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid


class Paquete(Base):
    """
    Modelo de Paquete que representa la tabla 'paquetes'
    Atributos:
        id_paquete: Identificador único del paquete
        id_cliente: Identificador del cliente propietario del paquete
        peso: Peso del paquete
        tamaño: Tamaño del paquete
        fragilidad: Nivel de fragilidad del paquete
        contenido: Contenido(descripción) del paquete
        tipo: Tipo de paquete (Normal, Express)
        activo: Estado del paquete (activo/inactivo)
        fecha_creacion: Fecha y hora de creación
        fecha_actualizacion: Fecha y hora de última actualización
        creado_por: Usuario que creó el paquete
        actualizado_por: Usuario que actualizó el paquete
    """

    __tablename__ = "paquetes"
    id_paquete = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_cliente = Column(
        PG_UUID(as_uuid=True), ForeignKey("clientes.id_cliente"), nullable=False
    )
    peso = Column(Float, nullable=False)
    tamaño = Column(String(10), nullable=False)
    fragilidad = Column(String(8), nullable=False)
    contenido = Column(Text, nullable=False)
    tipo = Column(String(10), nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.now, nullable=False)
    fecha_actualizacion = Column(DateTime, default=None, onupdate=datetime.now)
    creado_por = Column(
        String(36), ForeignKey("usuarios.id_usuario"), nullable=False
    )
    actualizado_por = Column(
        String(36), ForeignKey("usuarios.id_usuario"), nullable=False
    )

    # Relación con Cliente (bidireccional)
    cliente = relationship("Cliente", back_populates="paquetes", foreign_keys=[id_cliente])
    
    # Relación con DetalleEntrega (unidireccional)
    detalle_entrega = relationship("DetalleEntrega", back_populates="paquete", uselist=False)
    # Relaciones con Usuario para auditoría (sin back_populates en Usuario)
    creador = relationship("Usuario", foreign_keys=[creado_por])
    actualizador = relationship("Usuario", foreign_keys=[actualizado_por])

    def __repr__(self):
        return f"<Paquete(id_paquete={self.id_paquete}, cliente={self.id_cliente}, peso={self.peso}, tamaño={self.tamaño}, fragilidad={self.fragilidad}, contenido={self.contenido}, tipo={self.tipo})>"

    def to_dict(self):
        return {
            "id_paquete": self.id_paquete,
            "cliente": self.id_cliente,
            "peso": self.peso,
            "tamaño": self.tamaño,
            "fragilidad": self.fragilidad,
            "contenido": self.contenido,
            "tipo": self.tipo,
        }


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
        return v.strip().title()

    @validator("fragilidad")
    def validar_fragilidad(cls, v):
        fragilidades_validas = ["baja", "normal", "alta"]
        if v.lower() not in fragilidades_validas:
            raise ValueError(
                f'La fragilidad debe ser una de: {", ".join(fragilidades_validas)}'
            )
        return v.strip().title()

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
        return v.strip().title()


class PaqueteCreate(PaqueteBase):
    pass


class PaqueteUpdate(BaseModel):
    peso: Optional[float] = Field(None, gt=0)
    tamaño: Optional[str] = Field(None, min_length=1, max_length=10)
    fragilidad: Optional[str] = Field(None, min_length=1, max_length=8)
    contenido: Optional[str] = Field(None, min_length=1, max_length=1000)
    tipo: Optional[str] = Field(None, min_length=1, max_length=10)

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
        return v.strip().title()


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
