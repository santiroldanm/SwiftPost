from sqlalchemy import Column, String, Boolean, DateTime, Integer
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from ..database.database import Base
from datetime import datetime
from uuid import UUID, uuid4
import re


class Sede(Base):
    """
    Modelo de Sede que representa la tabla 'sedes'
    Atributos:
        id_sede: Identificador único de la sede
        ciudad: Ciudad donde se encuentra la sede
        direccion: Dirección física de la sede
        telefono: Número de teléfono de la sede
        activo: Estado de la sede (activo/inactivo)
        fecha_creacion: Fecha y hora de creación
        fecha_actualizacion: Fecha y hora de última actualización
        creado_por: Usuario que creó la sede
        actualizado_por: Usuario que actualizó la sede
    """

    __tablename__ = "sedes"
    id_sede = Column(UUID, primary_key=True, default=uuid4)
    ciudad = Column(String(50), nullable=False)
    direccion = Column(String(200), nullable=False)
    telefono = Column(Integer, nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.now, nullable=False)
    fecha_actualizacion = Column(
        DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
    )
    creado_por = Column(UUID, ForeignKey("usuarios.id_usuario"), nullable=False)
    actualizado_por = Column(UUID, ForeignKey("usuarios.id_usuario"), default=None)

    sede_remitente = relationship(
        "DetalleEntrega",
        foreign_keys="DetalleEntrega.id_sede_remitente",
        back_populates="sede_remitente",
    )
    sede_receptora = relationship(
        "DetalleEntrega",
        foreign_keys="DetalleEntrega.id_sede_receptora",
        back_populates="sede_receptora",
    )
    transportes = relationship("Transporte", back_populates="sedes")
    empleados = relationship("Empleado", back_populates="sedes")
    usuarios = relationship("Usuario", back_populates="sedes")

    def __repr__(self):
        return f"<Sede(id_sede={self.id_sede}, ciudad={self.ciudad}, direccion={self.direccion}, telefono={self.telefono})>"

    def to_dict():
        return {
            "id": self.id_sede,
            "ciudad": self.ciudad,
            "direccion": self.direccion,
            "telefono": self.telefono,
        }


class SedeBase(BaseModel):
    ciudad: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Ciudad donde se encuentra la sede",
    )
    direccion: str = Field(
        ..., min_length=5, max_length=200, description="Dirección física de la sede"
    )
    telefono: int = Field(
        ..., min_length=7, max_length=15, description="Número de teléfono de la sede"
    )

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
        if v <= 0:
            raise ValueError("El teléfono debe ser un número positivo")
        if len(str(v)) < 7 or len(str(v)) > 15:
            raise ValueError("El teléfono debe tener entre 7 y 15 dígitos")
        return v


class SedeCreate(SedeBase):
    pass


class SedeUpdate(BaseModel):
    ciudad: Optional[str] = Field(None, min_length=2, max_length=50)
    direccion: Optional[str] = Field(None, min_length=5, max_length=200)
    telefono: Optional[int] = Field(None, min_length=7, max_length=15)
    activo: Optional[bool] = None

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
            if v <= 0:
                raise ValueError("El teléfono debe ser un número positivo")
            if len(str(v)) < 7 or len(str(v)) > 15:
                raise ValueError("El teléfono debe tener entre 7 y 15 dígitos")
        return v


class SedeResponse(SedeBase):
    id_sede: int
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
