from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from database.config import Base
from datetime import datetime
import uuid


class Rol(Base):
    """
    Modelo de Rol que representa la tabla 'roles'
    Define los diferentes tipos de usuarios en el sistema (cliente, empleado, administrador, etc.)

    Atributos:
        id_rol: Identificador único del rol (como string UUID)
        nombre_rol: Nombre del rol (ej: 'cliente', 'empleado', 'administrador')
        activo: Estado del rol (activo/inactivo)
        fecha_creacion: Fecha y hora de creación
        fecha_actualizacion: Fecha y hora de última actualización
    """

    __tablename__ = "roles"

    id_rol = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre_rol = Column(String(50), unique=True, nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.now, nullable=False)
    fecha_actualizacion = Column(DateTime, default=None, onupdate=datetime.now, nullable=True)

    # Relación con usuarios
    usuarios = relationship("Usuario", back_populates="rol", cascade="all, delete-orphan")


class RolBase(BaseModel):
    """
    Clase base para validación de roles
    """

    nombre_rol: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Nombre del rol (cliente, empleado, administrador)",
    )

    class Config:
        orm_mode = True

    @validator("nombre_rol")
    def validar_nombre(cls, v):
        roles_validos = ["cliente", "empleado", "administrador"]
        if v.lower() not in roles_validos:
            raise ValueError(
                "El nombre del rol debe ser cliente, empleado o administrador"
            )
        return v.title()


class RolCreate(RolBase):
    """
    Clase para validación de creación de roles
    """

    pass


class RolUpdate(BaseModel):
    """
    Clase para validación de actualización de roles
    """

    nombre_rol: Optional[str] = Field(None, min_length=3, max_length=50)
    activo: Optional[bool] = None

    class Config:
        orm_mode = True

    @validator("nombre_rol")
    def validar_nombre(cls, v):
        roles_validos = ["cliente", "empleado", "administrador"]
        if v.lower() not in roles_validos:
            raise ValueError(
                "El nombre del rol debe ser cliente, empleado o administrador"
            )
        return v.title()


class RolResponse(RolBase):
    """
    Esquema para respuesta de rol
    """

    id_rol: uuid.UUID
    activo: bool
    fecha_creacion: datetime
    fecha_actualizacion: datetime


class RolListResponse(BaseModel):
    """
    Esquema para lista de roles
    """

    roles: List[RolResponse]
    total: int
    pagina: int
    por_pagina: int
