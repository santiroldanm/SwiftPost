import uuid
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from ..database.database import Base
from datetime import datetime
from uuid import UUID, uuid4

class Paquete(Base):

    """
    Modelo de Paquete que representa la tabla 'paquetes'
    Atributos:
        id: Identificador único del paquete
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
    id_paquete = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    id_cliente = Column(UUID(as_uuid=True), ForeignKey("clientes.id"), nullable=False)
    peso = Column(Float, nullable=False)
    tamaño = Column(String(10), nullable=False)
    fragilidad = Column(String(8), nullable=False)
    contenido = Column(Text, nullable=False)
    tipo = Column(String(10), nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.now, nullable=False)
    fecha_actualizacion = Column(DateTime, default= None, onupdate=datetime.now)
    creado_por = Column(String(50), nullable=False)
    actualizado_por = Column(String(50), nullable=False)

    clientes = relationship("Cliente", back_populates="paquetes", cascade="all, delete-orphan")

    def __repr__(self):
        """Representación en string del objeto Paquete"""
        return f"<Paquete(id_paquete={self.id_paquete}, id_cliente={self.id_cliente}, peso={self.peso}, tamaño={self.tamaño}, fragilidad={self.fragilidad}, contenido={self.contenido}, tipo={self.tipo}, activo={self.activo})>"

    def to_dict(self):
        """Convierte el objeto Paquete a un diccionario"""
        return {
            "id_paquete": self.id_paquete,
            "id_cliente": self.id_cliente,
            "peso": self.peso,
            "tamaño": self.tamaño,
            "fragilidad": self.fragilidad,
            "contenido": self.contenido,
            "tipo": self.tipo,
            "activo": self.activo,
            "fecha_creacion": self.fecha_creacion,
            "fecha_actualizacion": self.fecha_actualizacion,
            "creado_por": self.creado_por,
            "actualizado_por": self.actualizado_por
        }

"""Clase Pydantic para validación de paquetes"""
class PaqueteBase(BaseModel):
    peso: float = Field(..., gt=0, description="Peso del paquete en kilogramos")
    tamaño: str = Field(..., min_length=1, max_length=10, description="Tamaño del paquete (Pequeño, Mediano, Grande, Gigante)")
    fragilidad: str = Field(..., min_length=1, max_length=8, description="Nivel de fragilidad del paquete (Baja, Normal, Alta)")
    contenido: str = Field(..., min_length=1, max_length=1000, description="Contenido (descripción) del paquete")
    tipo: str = Field(..., min_length=1, max_length=10, description="Tipo de paquete (Normal, Express)")
    
    @validator('peso')
    def validar_peso(cls, v):
        if v < 0:
            raise ValueError('El peso debe ser mayor a 0')
        return v
    
    @validator('tamaño')
    def validar_tamaño(cls, v):
        tamaños_validos = ["pequeño", "mediano", "grande", "gigante"]
        if v.lower() not in tamaños_validos:
            raise ValueError(f'El tamaño debe ser uno de: {", ".join(tamaños_validos)}')
        return v.strip().title()

    @validator('fragilidad')
    def validar_fragilidad(cls, v):
        fragilidades_validas = ["baja", "normal", "alta"]
        if v.lower() not in fragilidades_validas:
            raise ValueError(f'La fragilidad debe ser una de: {", ".join(fragilidades_validas)}')
        return v.strip().title()

    @validator('contenido')
    def validar_contenido(cls, v):
        if v and len(v) < 1:
            raise ValueError('El contenido no puede estar vacío')
        return v.strip().title()
    
    @validator('tipo')
    def validar_tipo(cls, v):
        tipos_validos = ["normal", "express"]
        if v.lower() not in tipos_validos:
            raise ValueError(f'El tipo debe ser uno de: {", ".join(tipos_validos)}')
        return v.strip().title()


class PaqueteCreate(PaqueteBase):
    """Clase Pydantic para validación de creación de paquetes"""
    pass

class PaqueteUpdate(BaseModel):
    """Clase Pydantic para validación de actualización de paquetes"""
    peso: Optional[float] = Field(None, gt=0)
    tamaño: Optional[str] = Field(None, min_length=1, max_length=10)
    fragilidad: Optional[str] = Field(None, min_length=1, max_length=8)
    contenido: Optional[str] = Field(None, min_length=1, max_length=1000)
    tipo: Optional[str] = Field(None, min_length=1, max_length=10)


    @validator('peso')
    def validar_peso(cls, v):
        if v is not None and v < 0:
            raise ValueError('El peso debe ser mayor o igual a 0')
        return v

    @validator('tamaño')
    def validar_tamaño(cls, v):
        tamaños_validos = ["pequeño", "mediano", "grande", "gigante"]
        if v is not None and v.lower() not in tamaños_validos:
            raise ValueError(f'El tamaño debe ser uno de: {", ".join(tamaños_validos)}')
        return v.strip().title()
    
    @validator('fragilidad')
    def validar_fragilidad(cls, v):
        fragilidades_validas = ["baja", "normal", "alta"]
        if v is not None and v.lower() not in fragilidades_validas:
            raise ValueError(f'La fragilidad debe ser una de: {", ".join(fragilidades_validas)}')
        return v.strip().title()

    @validator('contenido')
    def validar_contenido(cls, v):
        if v is not None and len(v) < 1:
            raise ValueError('El contenido no puede estar vacío')
        return v.strip().title()

    @validator('tipo')
    def validar_tipo(cls, v):
        tipos_validos = ["normal", "express"]
        if v is not None and v.lower() not in tipos_validos:
            raise ValueError(f'El tipo debe ser uno de: {", ".join(tipos_validos)}')
        return v.strip().title()

class PaqueteResponse(PaqueteBase):
    """Esquema para respuesta de paquete"""
    id_paquete: UUID
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None
    creado_por: str
    actualizado_por: Optional[str] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class PaqueteListResponse(BaseModel):
    """Esquema para lista de paquetes"""
    paquetes: List[PaqueteResponse]
    total: int
    pagina: int
    por_pagina: int
    
    class Config:
        from_attributes = True