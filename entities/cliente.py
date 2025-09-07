from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from ..database.database import Base
from datetime import datetime
from uuid import UUID, uuid4
import re

class Cliente(Base):
    """
    Modelo de Cliente que representa la tabla 'clientes'
    Atributos:
        id: Identificador único del cliente
        primer_nombre: Primer nombre del cliente
        segundo_nombre: Segundo nombre del cliente (opcional)
        primer_apellido: Primer apellido del cliente
        segundo_apellido: Segundo apellido del cliente (opcional)
        documento: Documento del cliente
        direccion: Dirección del cliente
        telefono: Número de teléfono del cliente
        correo: Correo electrónico del cliente
        tipo: Tipo de cliente (regular/vip)
        activo: Estado del cliente (activo/inactivo)
        fecha_creacion: Fecha y hora de creación
        fecha_actualizacion: Fecha y hora de última actualización
        creado_por: Usuario que creó el cliente
        actualizado_por: Usuario que actualizó el cliente
    """

    __tablename__ = "clientes"
    id_cliente = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    primer_nombre = Column(String(50), nullable=False)
    segundo_nombre = Column(String(50), default=None, nullable=True)
    primer_apellido = Column(String(50), nullable=False)
    segundo_apellido = Column(String(50), default=None, nullable=True)
    documento = Column(Integer, nullable=False)
    direccion = Column(String(200), nullable=False)
    telefono = Column(Integer, nullable=False)
    correo = Column(String(100), nullable=False, unique=True)
    tipo = Column(String(10), nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.now, nullable=False)
    fecha_actualizacion = Column(DateTime, default=None, onupdate=datetime.now)
    creado_por = Column(String(50), nullable=False)
    actualizado_por = Column(String(50), nullable=False)

    paquetes = relationship("Paquete", back_populates="clientes", cascade="all, delete-orphan")

    def __repr__(self):
        """Representación en string del objeto Cliente"""
        return f"<Cliente(id={self.id_cliente}, primer_nombre={self.primer_nombre}, segundo_nombre={self.segundo_nombre}, primer_apellido={self.primer_apellido}, segundo_apellido={self.segundo_apellido}, documento={self.documento}, telefono={self.telefono}, direccion={self.direccion}, correo={self.correo}, tipo={self.tipo})>"

    def to_dict(self):
        """Convierte el objeto Cliente a un diccionario"""
        return {
            "id": self.id_cliente,
            "primer_nombre": self.primer_nombre,
            "segundo_nombre": self.segundo_nombre,
            "primer_apellido": self.primer_apellido,
            "segundo_apellido": self.segundo_apellido,
            "documento": self.documento,
            "direccion": self.direccion,
            "telefono": self.telefono,
            "correo": self.correo,
            "tipo": self.tipo
        }

"""Clase Pydantic para validación de clientes"""
class ClienteBase(BaseModel):
    primer_nombre: str = Field(..., min_length=1, max_length=50, description="Primer nombre del cliente")
    segundo_nombre: Optional[str] = Field(min_length=1, max_length=50, description="Segundo nombre del cliente")
    primer_apellido: str = Field(..., min_length=1, max_length=50, description="Primer apellido del cliente")
    segundo_apellido: Optional[str] = Field(min_length=1, max_length=50, description="Segundo apellido del cliente")
    documento: int = Field(..., gt=0, description="Número de documento del cliente")
    direccion: str = Field(..., min_length=5, max_length=200, description="Dirección del cliente")
    telefono: int = Field(..., gt=0, description="Número de teléfono del cliente")
    correo: str = Field(..., min_length=5, max_length=100, description="Correo electrónico del cliente")
    tipo: str = Field(..., min_length=1, max_length=10, description="Tipo de cliente (regular/vip)")
    
    @validator('primer_nombre')
    def validar_nombre(cls, v):
        if not v or not v.strip():
            raise ValueError('El primer nombre no puede estar vacío')
        if not v.replace(' ', '').isalpha():
            raise ValueError('El primer nombre solo puede contener letras')
        return v.strip().title()
    
    @validator('segundo_nombre')
    def validar_segundo_nombre(cls, v):
        if v is None:
            return v
        if not v.strip():
            raise ValueError('El segundo nombre no puede estar vacío')
        if not v.replace(' ', '').isalpha():
            raise ValueError('El segundo nombre solo puede contener letras')
        return v.strip().title()
    
    @validator('primer_apellido')
    def validar_apellido(cls, v):
        if not v or not v.strip():
            raise ValueError('El primer apellido no puede estar vacío')
        if not v.replace(' ', '').isalpha():
            raise ValueError('El primer apellido solo puede contener letras')
        return v.strip().title()
    
    @validator('segundo_apellido')
    def validar_segundo_apellido(cls, v):
        if v is None:
            return v
        if not v.strip():
            raise ValueError('El segundo apellido no puede estar vacío')
        if not v.replace(' ', '').isalpha():
            raise ValueError('El segundo apellido solo puede contener letras')
        return v.strip().title()
    
    @validator('documento')
    def validar_documento(cls, v):
        if v < 0 and len(str(v)) < 7:
            raise ValueError('El documento debe ser un número positivo y tener al menos 7 dígitos')
        return v
    
    @validator('direccion')
    def validar_direccion(cls, v):
        if not v or not v.strip():
            raise ValueError('La dirección no puede estar vacía')
        if len(v.strip()) < 5:
            raise ValueError('La dirección debe tener al menos 5 caracteres')
        return v.strip().title()
    
    @validator('telefono')
    def validar_telefono(cls, v):
        if v < 0 and len(str(v)) < 7 or len(str(v)) > 15:
            raise ValueError('El teléfono debe ser un número positivo y tener entre 7 y 15 dígitos')
        return v
    
    @validator('correo')
    def validar_correo(cls, v):
        if not v or not v.strip():
            raise ValueError('El correo no puede estar vacío')
        patron_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(patron_email, v.strip()):
            raise ValueError('Formato de correo electrónico no válido')
        return v.strip()
    
    @validator('tipo')
    def validar_tipo(cls, v):
        tipos_validos = ["regular", "vip"]
        if v.lower() not in tipos_validos:
            raise ValueError(f'El tipo debe ser uno de: {", ".join(tipos_validos)}')
        return v.strip().title()

class ClienteCreate(ClienteBase):
    """Clase Pydantic para validación de creación de clientes"""
    pass

class ClienteUpdate(BaseModel):
    """Clase Pydantic para validación de actualización de clientes"""
    primer_nombre: Optional[str] = Field(None, min_length=1, max_length=50)
    segundo_nombre: Optional[str] = Field(None, min_length=1, max_length=50)
    primer_apellido: Optional[str] = Field(None, min_length=1, max_length=50)
    segundo_apellido: Optional[str] = Field(None, min_length=1, max_length=50)
    documento: Optional[int] = Field(None, gt=0)
    direccion: Optional[str] = Field(None, min_length=5, max_length=200)
    telefono: Optional[int] = Field(None, gt=0)
    correo: Optional[str] = Field(None, min_length=5, max_length=100)
    tipo: Optional[str] = Field(None, min_length=1, max_length=10)

    @validator('primer_nombre')
    def validar_nombre(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError('El primer nombre no puede estar vacío')
            if not v.replace(' ', '').isalpha():
                raise ValueError('El primer nombre solo puede contener letras')
            return v.strip().title()
        return v
    
    @validator('segundo_nombre')
    def validar_segundo_nombre(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError('El segundo nombre no puede estar vacío')
            if not v.replace(' ', '').isalpha():
                raise ValueError('El segundo nombre solo puede contener letras')
            return v.strip().title()
        return v
    
    @validator('primer_apellido')
    def validar_apellido(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError('El primer apellido no puede estar vacío')
            if not v.replace(' ', '').isalpha():
                raise ValueError('El primer apellido solo puede contener letras')
            return v.strip().title()
        return v
    
    @validator('segundo_apellido')
    def validar_segundo_apellido(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError('El segundo apellido no puede estar vacío')
            if not v.replace(' ', '').isalpha():
                raise ValueError('El segundo apellido solo puede contener letras')
            return v.strip().title()
        return v
    
    @validator('direccion')
    def validar_direccion(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError('La dirección no puede estar vacía')
            if len(v.strip()) < 5:
                raise ValueError('La dirección debe tener al menos 5 caracteres')
            return v.strip().title()
        return v
    
    @validator('telefono')
    def validar_telefono(cls, v):
        if v is not None:
            if v <= 0:
                raise ValueError('El teléfono debe ser un número positivo')
            if len(str(v)) < 7 or len(str(v)) > 15:
                raise ValueError('El teléfono debe tener entre 7 y 15 dígitos')
        return v
    
    @validator('correo')
    def validar_correo(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError('El correo no puede estar vacío')
            patron_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(patron_email, v.strip()):
                raise ValueError('Formato de correo electrónico no válido')
            return v.strip().lower()
        return v

    @validator('tipo')
    def validar_tipo(cls, v):
        if v is not None:
            tipos_validos = ["regular", "vip"]
            if v.lower() not in tipos_validos:
                raise ValueError(f'El tipo debe ser uno de: {", ".join(tipos_validos)}')
            return v.strip().title()
        return v

class ClienteResponse(ClienteBase):
    """Esquema para respuesta de cliente"""
    id_cliente: UUID
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None
    creado_por: str
    actualizado_por: Optional[str] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ClienteListResponse(BaseModel):
    """Esquema para lista de clientes"""
    clientes: List[ClienteResponse]
    total: int
    pagina: int
    por_pagina: int
    
    class Config:
        from_attributes = True