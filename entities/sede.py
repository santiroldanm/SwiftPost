from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Float
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from database.config import Base
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid
import re


class Sede(Base):
    """
    Modelo de Sede que representa la tabla 'sedes'
    Atributos:
        id_sede: Identificador único de la sede
        nombre: Nombre de la sede
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
    id_sede = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nombre = Column(String(100), nullable=False)
    ciudad = Column(String(50), nullable=False)
    direccion = Column(String(200), nullable=False)
    telefono = Column(String(15), nullable=False)
    # Coordenadas tridimensionales para cálculo de distancias
    latitud = Column(Float, nullable=True, comment="Latitud en grados decimales")
    longitud = Column(Float, nullable=True, comment="Longitud en grados decimales") 
    altitud = Column(Float, nullable=True, comment="Altitud en metros sobre el nivel del mar")
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.now, nullable=False)
    fecha_actualizacion = Column(
        DateTime, default=datetime.now, onupdate=datetime.now, nullable=False
    )
    creado_por = Column(
        String(36), ForeignKey("usuarios.id_usuario"), nullable=False
    )
    actualizado_por = Column(
        String(36), ForeignKey("usuarios.id_usuario"), default=None
    )

    detalles_remitente = relationship(
        "DetalleEntrega",
        foreign_keys="DetalleEntrega.id_sede_remitente",
        viewonly=True
    )
    detalles_receptor = relationship(
        "DetalleEntrega",
        foreign_keys="DetalleEntrega.id_sede_receptora",
        viewonly=True
    )
    
    transportes = relationship("Transporte", foreign_keys="Transporte.id_sede", viewonly=True)
    
    empleados = relationship("Empleado", foreign_keys="Empleado.id_sede", viewonly=True)
    creador = relationship("Usuario", foreign_keys=[creado_por])
    actualizador = relationship("Usuario", foreign_keys=[actualizado_por])

    def __repr__(self):
        return f"<Sede(id_sede={self.id_sede}, nombre={self.nombre}, ciudad={self.ciudad}, direccion={self.direccion}, telefono={self.telefono})>"

    def to_dict(self):
        return {
            "id": self.id_sede,
            "nombre": self.nombre,
            "ciudad": self.ciudad,
            "direccion": self.direccion,
            "telefono": self.telefono,
        }


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
        telefono_limpio = ''.join(filter(str.isdigit, v))
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
            telefono_limpio = ''.join(filter(str.isdigit, v))
            if not telefono_limpio.isdigit():
                raise ValueError("El teléfono solo puede contener números")
            if len(telefono_limpio) < 7 or len(telefono_limpio) > 15:
                raise ValueError("El teléfono debe tener entre 7 y 15 dígitos")
            return telefono_limpio
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
