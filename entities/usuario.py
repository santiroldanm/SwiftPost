from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field, validator
from typing import Optional, List

# Importaciones para anotaciones de tipo y evitar importaciones circulares
if False:
    from .cliente import Cliente
    from .empleado import Empleado
from database.config import Base
from datetime import datetime
import uuid
import string
import re


class Usuario(Base):
    """
    Modelo de Usuario que representa la tabla 'usuarios' encargada de la auditoría
    Atributos:
        id_usuario: Identificador único del usuario
        rol: Rol del usuario
        primer_nombre: Primer nombre del usuario
        segundo_nombre: Segundo nombre del usuario (opcional)
        primer_apellido: Primer apellido del usuario
        segundo_apellido: Segundo apellido del usuario (opcional)
        nombre_usuario: Nombre de usuario único para autenticación
        password: Contraseña del usuario
        activo: Estado del usuario (activo/inactivo)
        fecha_creacion: Fecha y hora de creación
        fecha_actualizacion: Fecha y hora de última actualización
    """

    __tablename__ = "usuarios"
    # ID del usuario (UUID como string de 36 caracteres)
    id_usuario = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # FK al rol (tipo de usuario): cliente, empleado, administrador
    id_rol = Column(String(36), ForeignKey("roles.id_rol"), nullable=False, index=True)
    # Credenciales y estado
    nombre_usuario = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.now, nullable=False)
    fecha_actualizacion = Column(DateTime, default=None, onupdate=datetime.now)

    # Relación con el rol
    rol = relationship("Rol", back_populates="usuarios", foreign_keys=[id_rol])

    # Relaciones uno a uno con perfiles específicos
    cliente = relationship("Cliente", back_populates="usuario", uselist=False, cascade="all, delete-orphan", foreign_keys="Cliente.id_cliente")
    empleado = relationship("Empleado", back_populates="usuario", uselist=False, cascade="all, delete-orphan", foreign_keys="Empleado.id_empleado")
     
  
    # Otras relaciones (comentadas hasta que sean necesarias)
    # sedes = relationship("Sede", back_populates="usuario")
    # empleados = relationship("Empleado", back_populates="usuario")
    # paquetes = relationship("Paquete", back_populates="usuario")
    # tipos_documentos = relationship("TipoDocumento", back_populates="usuario")
    # transportes = relationship("Transporte", back_populates="usuario")
    def __repr__(self):
        return f"<Usuario(id_usuario={self.id_usuario}, id_rol={self.id_rol}, nombre_usuario={self.nombre_usuario})>"

    def to_dict(self):
        return {
            "id_usuario": self.id_usuario,
            "id_rol": self.id_rol,
            "nombre_usuario": self.nombre_usuario,
        }


class UsuarioBase(BaseModel):
    nombre_usuario: str = Field(
        ..., min_length=4, max_length=50, description="Nombre de usuario único"
    )
    password: str = Field(..., min_length=8, description="Contraseña del usuario")
    id_rol: str = Field(..., min_length=1, description="ID del rol (FK roles.id_rol)")

    @validator("nombre_usuario")
    def validar_nombre_usuario(cls, v):
        if not v or not v.strip():
            raise ValueError("El nombre de usuario no puede estar vacío")
        if not re.match(r"^[a-zA-Z0-9._]+$", v):
            raise ValueError(
                "El nombre de usuario solo puede contener letras, números y guiones bajos o puntos"
            )
        return v.strip()

    @validator("password")
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
            raise ValueError(
                "La contraseña debe contener al menos un carácter especial"
            )
        return v


class UsuarioCreate(UsuarioBase):
    pass


class UsuarioUpdate(BaseModel):
    nombre_usuario: Optional[str] = Field(None, min_length=4, max_length=50)
    password: Optional[str] = Field(None, min_length=8)
    id_rol: Optional[str] = Field(None, min_length=1)
    activo: Optional[bool] = None

    @validator("nombre_usuario")
    def validar_nombre_usuario(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError("El nombre de usuario no puede estar vacío")
            if not re.match(r"^[a-zA-Z0-9._]+$", v):
                raise ValueError(
                    "El nombre de usuario solo puede contener letras, números y guiones bajos o puntos"
                )
            return v.strip()
        return v

    @validator("password")
    def validar_password(cls, v):
        if v is not None:
            if len(v) < 8:
                raise ValueError("La contraseña debe tener al menos 8 caracteres")
            if not any(c.isupper() for c in v):
                raise ValueError(
                    "La contraseña debe contener al menos una letra mayúscula"
                )
            if not any(c.islower() for c in v):
                raise ValueError(
                    "La contraseña debe contener al menos una letra minúscula"
                )
            if not any(c.isdigit() for c in v):
                raise ValueError("La contraseña debe contener al menos un número")
            if not any(c in string.punctuation for c in v):
                raise ValueError(
                    "La contraseña debe contener al menos un carácter especial"
                )
        return v


class UsuarioResponse(UsuarioBase):
    id_usuario: uuid.UUID
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class UsuarioListResponse(BaseModel):
    usuarios: List[UsuarioResponse]
    total: int
    pagina: int
    por_pagina: int

    class Config:
        from_attributes = True
