from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from ..database.database import Base
from datetime import datetime
import re

class Cliente(Base):
    """
    Modelo de Cliente que representa la tabla 'clientes'
    Atributos:
        id: Identificador único del cliente
        nombre: Nombre del cliente
        apellido: Apellido del cliente
        direccion: Dirección del cliente
        telefono: Número de teléfono del cliente
        correo: Correo electrónico del cliente
        activo: Estado del cliente (activo/inactivo)
        fecha_creacion: Fecha y hora de creación
        fecha_actualizacion: Fecha y hora de última actualización
        creado_por: Usuario que creó el cliente
        actualizado_por: Usuario que actualizó el cliente
    """

    __tablename__ = "clientes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False)
    apellido = Column(String(50), nullable=False)
    direccion = Column(String(200), nullable=False)
    telefono = Column(Integer, nullable=False)
    correo = Column(String(100), nullable=False, unique=True)
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.now, nullable=False)
    fecha_actualizacion = Column(DateTime, default=datetime.now, nullable=False, onupdate=datetime.now)
    creado_por = Column(String(50), nullable=False)
    actualizado_por = Column(String(50), nullable=False)

    paquetes = relationship("Paquete", back_populates="clientes", cascade="all, delete-orphan")

    def __repr__(self):
        """Representación en string del objeto Cliente"""
        return f"<Cliente(id={self.id}, nombre={self.nombre}, apellido={self.apellido}, correo={self.correo}, telefono={self.telefono}, direccion={self.direccion})>"

    def to_dict(self):
        """Convierte el objeto Cliente a un diccionario"""
        return {
            "id": self.id,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "direccion": self.direccion,
            "telefono": self.telefono,
            "correo": self.correo
        }

    def descuentoVIP(self, precio_base: float) -> float:
        """Descuento base para clientes regulares"""
        return 0.0

"""Clase Pydantic para validación de clientes"""
class ClienteBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=50, description="Nombre del cliente")
    apellido: str = Field(..., min_length=1, max_length=50, description="Apellido del cliente")
    direccion: str = Field(..., min_length=5, max_length=200, description="Dirección del cliente")
    telefono: int = Field(..., gt=0, description="Número de teléfono del cliente")
    correo: str = Field(..., min_length=5, max_length=100, description="Correo electrónico del cliente")
    activo: bool = Field(default=True, description="Estado del cliente (activo/inactivo)")
    
    @validator('nombre')
    def validar_nombre(cls, v):
        if not v or not v.strip():
            raise ValueError('Nombre no puede estar vacío')
        if not v.replace(' ', '').isalpha():
            raise ValueError('Nombre solo puede contener letras y espacios')
        return v.strip().title()
    
    @validator('apellido')
    def validar_apellido(cls, v):
        if not v or not v.strip():
            raise ValueError('Apellido no puede estar vacío')
        if not v.replace(' ', '').isalpha():
            raise ValueError('Apellido solo puede contener letras y espacios')
        return v.strip().title()
    
    @validator('direccion')
    def validar_direccion(cls, v):
        if not v or not v.strip():
            raise ValueError('Dirección no puede estar vacía')
        if len(v.strip()) < 5:
            raise ValueError('Dirección debe tener al menos 5 caracteres')
        return v.strip().title()
    
    @validator('telefono')
    def validar_telefono(cls, v):
        if v <= 0:
            raise ValueError('Teléfono debe ser un número positivo')
        if len(str(v)) < 7 or len(str(v)) > 15:
            raise ValueError('Teléfono debe tener entre 7 y 15 dígitos')
        return v
    
    @validator('correo')
    def validar_correo(cls, v):
        if not v or not v.strip():
            raise ValueError('Correo no puede estar vacío')
        patron_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(patron_email, v.strip()):
            raise ValueError('Formato de correo electrónico no válido')
        return v.strip().lower()
    
    @validator('activo')
    def validar_activo(cls, v):
        if not isinstance(v, bool):
            raise ValueError('Activo debe ser un booleano')
        return v

class ClienteCreate(ClienteBase):
    """Clase Pydantic para validación de creación de clientes"""
    pass

class ClienteUpdate(BaseModel):
    """Clase Pydantic para validación de actualización de clientes"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=50)
    apellido: Optional[str] = Field(None, min_length=1, max_length=50)
    direccion: Optional[str] = Field(None, min_length=5, max_length=200)
    telefono: Optional[int] = Field(None, gt=0)
    correo: Optional[str] = Field(None, min_length=5, max_length=100)
    activo: Optional[bool] = None

    @validator('nombre')
    def validar_nombre(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Nombre no puede estar vacío')
            if not v.replace(' ', '').isalpha():
                raise ValueError('Nombre solo puede contener letras y espacios')
            return v.strip().title()
        return v
    
    @validator('apellido')
    def validar_apellido(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Apellido no puede estar vacío')
            if not v.replace(' ', '').isalpha():
                raise ValueError('Apellido solo puede contener letras y espacios')
            return v.strip().title()
        return v
    
    @validator('direccion')
    def validar_direccion(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Dirección no puede estar vacía')
            if len(v.strip()) < 5:
                raise ValueError('Dirección debe tener al menos 5 caracteres')
            return v.strip().title()
        return v
    
    @validator('telefono')
    def validar_telefono(cls, v):
        if v is not None:
            if v <= 0:
                raise ValueError('Teléfono debe ser un número positivo')
            if len(str(v)) < 7 or len(str(v)) > 15:
                raise ValueError('Teléfono debe tener entre 7 y 15 dígitos')
        return v
    
    @validator('correo')
    def validar_correo(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Correo no puede estar vacío')
            # Validación básica de email
            patron_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(patron_email, v.strip()):
                raise ValueError('Formato de correo electrónico no válido')
            return v.strip().lower()
        return v
    
    @validator('activo')
    def validar_activo(cls, v):
        if v is not None and not isinstance(v, bool):
            raise ValueError('Activo debe ser un booleano')
        return v

class ClienteResponse(ClienteBase):
    """Esquema para respuesta de cliente"""
    id: int
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None
    creado_por: str
    actualizado_por: str
    
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

class Cliente_VIP(Cliente):
    """
    Modelo de Cliente VIP que hereda de Cliente
    Añade funcionalidad de descuento para clientes VIP

    Atributos:
        nivel: Nivel VIP del cliente
        descuento: Porcentaje de descuento (0.0 a 1.0)
    """
    
    __tablename__ = "clientes_vip"
    id = Column(Integer, ForeignKey('clientes.id'), primary_key=True)
    nivel = Column(String(20), default="VIP", nullable=False)
    descuento = Column(Float, default=0.10, nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'vip'
    }

    def __repr__(self):
        """Representación en string del objeto Cliente VIP"""
        return f"<Cliente_VIP(id={self.id}, nombre={self.nombre}, apellido={self.apellido}, nivel={self.nivel}, descuento={self.descuento})>"

    def to_dict(self):
        """Convierte el objeto Cliente VIP a un diccionario"""
        base_dict = super().to_dict()
        base_dict.update({
            "nivel": self.nivel,
            "descuento": self.descuento
        })
        return base_dict
    
    def descuentoVIP(self, precio_base: float) -> float:
        """Calcula el descuento VIP"""
        return precio_base * self.descuento

"""Clase Pydantic para validación de clientes VIP"""
class ClienteVIPBase(ClienteBase):
    nivel: str = Field(default="VIP", min_length=1, max_length=20, description="Nivel VIP del cliente")
    descuento: float = Field(default=0.10, ge=0, le=1, description="Porcentaje de descuento VIP (0.10 = 10%)")
    
    @validator('nivel')
    def validar_nivel(cls, v):
        niveles_validos = ["VIP", "Premium", "Gold", "Platinum"]
        if v not in niveles_validos:
            raise ValueError(f'Nivel debe ser uno de: {", ".join(niveles_validos)}')
        return v
    
    @validator('descuento')
    def validar_descuento(cls, v):
        if v < 0 or v > 1:
            raise ValueError('Descuento debe estar entre 0 y 1 (0% a 100%)')
        return v