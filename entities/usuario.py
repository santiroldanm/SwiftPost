from sqlalchemy import Column, String, Boolean, DateTime
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from ..database.database import Base
from datetime import datetime
from uuid import UUID, uuid4
import string
import re

class Usuario(Base):
    """
    Modelo de Usuario que representa la tabla 'usuarios' encargada de la auditoría
    Atributos:
        id_usuario: Identificador único del usuario
        primer_nombre: Primer nombre del usuario
        segundo_nombre: Segundo nombre del usuario (opcional)
        primer_apellido: Primer apellido del usuario
        segundo_apellido: Segundo apellido del usuario (opcional)
        nombre_usuario: Nombre de usuario único para autenticación
        contraseña: Contraseña del usuario
        activo: Estado del usuario (activo/inactivo)
        fecha_creacion: Fecha y hora de creación
        fecha_actualizacion: Fecha y hora de última actualización
    """
    __tablename__ = "usuarios"
    id_usuario = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    primer_nombre = Column(String(50), nullable=False)
    segundo_nombre = Column(String(50), nullable=True)
    primer_apellido = Column(String(50), nullable=False)
    segundo_apellido = Column(String(50), nullable=True)
    nombre_usuario = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.now, nullable=False)
    fecha_actualizacion = Column(DateTime, default=None, onupdate=datetime.now)
    
    def __repr__(self):
        """Representación en string del objeto Usuario"""
        return f"<Usuario(id_usuario={self.id_usuario}, nombre_usuario={self.nombre_usuario}, nombre_completo={self.primer_nombre} {self.segundo_nombre or ''} {self.primer_apellido} {self.segundo_apellido or ''})>"

"""Clase Pydantic para validación de usuarios"""
class UsuarioBase(BaseModel):
    """Clase base para validación de usuarios"""
    primer_nombre: str = Field(..., min_length=1, max_length=50, description="Primer nombre del usuario")
    segundo_nombre: Optional[str] = Field(None, min_length=1, max_length=50, description="Segundo nombre del usuario (opcional)")
    primer_apellido: str = Field(..., min_length=1, max_length=50, description="Primer apellido del usuario")
    segundo_apellido: Optional[str] = Field(None, min_length=1, max_length=50, description="Segundo apellido del usuario (opcional)")
    nombre_usuario: str = Field(..., min_length=4, max_length=50, description="Nombre de usuario único")
    password: str = Field(..., min_length=8, description="Contraseña del usuario")

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
    
    @validator('nombre_usuario')
    def validar_nombre_usuario(cls, v):
        if not v or not v.strip():
            raise ValueError('El nombre de usuario no puede estar vacío')
        if not re.match(r'^[a-zA-Z0-9._]+$', v):
            raise ValueError("El nombre de usuario solo puede contener letras, números y guiones bajos o puntos")
        return v.strip()
    
    @validator('password')
    def validar_contraseña(cls, v):
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        if not any(c.isupper() for c in v):
            raise ValueError("La contraseña debe contener al menos una letra mayúscula")
        if not any(c.islower() for c in v):
            raise ValueError("La contraseña debe contener al menos una letra minúscula")
        if not any(c.isdigit() for c in v):
            raise ValueError("La contraseña debe contener al menos un número")
        if not any(c in string.punctuation for c in v):
            raise ValueError("La contraseña debe contener al menos un carácter especial")
        return v

class UsuarioCreate(UsuarioBase):
    """Clase para validación de creación de usuarios"""
    pass

class UsuarioUpdate(BaseModel):
    """Clase para validación de actualización de usuarios"""
    primer_nombre: Optional[str] = Field(None, min_length=1, max_length=50)
    segundo_nombre: Optional[str] = Field(None, min_length=1, max_length=50)
    primer_apellido: Optional[str] = Field(None, min_length=1, max_length=50)
    segundo_apellido: Optional[str] = Field(None, min_length=1, max_length=50)
    nombre_usuario: Optional[str] = Field(None, min_length=4, max_length=50)
    password: Optional[str] = Field(None, min_length=8)
    activo: Optional[bool] = None

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
    
    @validator('nombre_usuario')
    def validar_nombre_usuario(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError('El nombre de usuario no puede estar vacío')
            if not re.match(r'^[a-zA-Z0-9._]+$', v):
                raise ValueError("El nombre de usuario solo puede contener letras, números y guiones bajos o puntos")
            return v.strip()
        return v
    
    @validator('password')
    def validar_password(cls, v):
        if v is not None:
            if len(v) < 8:
                raise ValueError("La contraseña debe tener al menos 8 caracteres")
            if not any(c.isupper() for c in v):
                raise ValueError("La contraseña debe contener al menos una letra mayúscula")
            if not any(c.islower() for c in v):
                raise ValueError("La contraseña debe contener al menos una letra minúscula")
            if not any(c.isdigit() for c in v):
                raise ValueError("La contraseña debe contener al menos un número")
            if not any(c in string.punctuation for c in v):
                raise ValueError("La contraseña debe contener al menos un carácter especial")
        return v

class UsuarioResponse(UsuarioBase):
    """Esquema para respuesta de usuario"""
    id_usuario: UUID
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UsuarioListResponse(BaseModel):
    """Esquema para lista de usuarios"""
    usuarios: List[UsuarioResponse]
    total: int
    pagina: int
    por_pagina: int

    class Config:
        from_attributes = True