from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field, validator
from typing import Optional, List
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
    id_usuario = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rol = Column(PG_UUID(as_uuid=True), ForeignKey("roles.id_rol"), nullable=False)
    primer_nombre = Column(String(50), nullable=False)
    segundo_nombre = Column(String(50), nullable=True)
    primer_apellido = Column(String(50), nullable=False)
    segundo_apellido = Column(String(50), nullable=True)
    nombre_usuario = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.now, nullable=False)
    fecha_actualizacion = Column(DateTime, default=None, onupdate=datetime.now)

    clientes = relationship(
        "Cliente", back_populates="usuarios", foreign_keys="Cliente.creado_por"
    )
    detalles_entrega = relationship(
        "DetalleEntrega",
        cascade="all, delete-orphan",
        back_populates="usuarios",
        foreign_keys="DetalleEntrega.creado_por",
    )
    empleados = relationship(
        "Empleado", back_populates="usuarios", foreign_keys="Empleado.creado_por"
    )
    paquetes = relationship(
        "Paquete", back_populates="usuarios", foreign_keys="Paquete.creado_por"
    )
    roles = relationship("Rol", back_populates="usuarios")
    sedes = relationship(
        "Sede", back_populates="usuarios", foreign_keys="Sede.creado_por"
    )
    tipos_documentos = relationship(
        "TipoDocumento",
        back_populates="usuarios",
        foreign_keys="TipoDocumento.creado_por",
    )
    transportes = relationship(
        "Transporte", back_populates="usuarios", foreign_keys="Transporte.creado_por"
    )

    def __repr__(self):
        return f"<Usuario(id_usuario={self.id_usuario}, rol={self.rol}, nombre_usuario={self.nombre_usuario}, nombre_completo={self.primer_nombre} {self.segundo_nombre or ''} {self.primer_apellido} {self.segundo_apellido or ''})>"

    def to_dict(self):
        return {
            "id_usuario": self.id_usuario,
            "rol": self.rol,
            "nombre_usuario": self.nombre_usuario,
            "nombre_completo": f"{self.primer_nombre} {self.segundo_nombre or ''} {self.primer_apellido} {self.segundo_apellido or ''}",
        }


class UsuarioBase(BaseModel):

    primer_nombre: str = Field(
        ..., min_length=1, max_length=50, description="Primer nombre del usuario"
    )
    segundo_nombre: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50,
        description="Segundo nombre del usuario (opcional)",
    )
    primer_apellido: str = Field(
        ..., min_length=1, max_length=50, description="Primer apellido del usuario"
    )
    segundo_apellido: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50,
        description="Segundo apellido del usuario (opcional)",
    )
    nombre_usuario: str = Field(
        ..., min_length=4, max_length=50, description="Nombre de usuario único"
    )
    password: str = Field(..., min_length=8, description="Contraseña del usuario")

    @validator("primer_nombre")
    def validar_nombre(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError("El primer nombre no puede estar vacío")
            if not v.replace(" ", "").isalpha():
                raise ValueError("El primer nombre solo puede contener letras")
            return v.strip().title()
        return v

    @validator("segundo_nombre")
    def validar_segundo_nombre(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError("El segundo nombre no puede estar vacío")
            if not v.replace(" ", "").isalpha():
                raise ValueError("El segundo nombre solo puede contener letras")
            return v.strip().title()
        return v

    @validator("primer_apellido")
    def validar_apellido(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError("El primer apellido no puede estar vacío")
            if not v.replace(" ", "").isalpha():
                raise ValueError("El primer apellido solo puede contener letras")
            return v.strip().title()
        return v

    @validator("segundo_apellido")
    def validar_segundo_apellido(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError("El segundo apellido no puede estar vacío")
            if not v.replace(" ", "").isalpha():
                raise ValueError("El segundo apellido solo puede contener letras")
            return v.strip().title()
        return v

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
    primer_nombre: Optional[str] = Field(None, min_length=1, max_length=50)
    segundo_nombre: Optional[str] = Field(None, min_length=1, max_length=50)
    primer_apellido: Optional[str] = Field(None, min_length=1, max_length=50)
    segundo_apellido: Optional[str] = Field(None, min_length=1, max_length=50)
    nombre_usuario: Optional[str] = Field(None, min_length=4, max_length=50)
    password: Optional[str] = Field(None, min_length=8)
    activo: Optional[bool] = None

    @validator("primer_nombre")
    def validar_nombre(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError("El primer nombre no puede estar vacío")
            if not v.replace(" ", "").isalpha():
                raise ValueError("El primer nombre solo puede contener letras")
            return v.strip().title()
        return v

    @validator("segundo_nombre")
    def validar_segundo_nombre(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError("El segundo nombre no puede estar vacío")
            if not v.replace(" ", "").isalpha():
                raise ValueError("El segundo nombre solo puede contener letras")
            return v.strip().title()
        return v

    @validator("primer_apellido")
    def validar_apellido(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError("El primer apellido no puede estar vacío")
            if not v.replace(" ", "").isalpha():
                raise ValueError("El primer apellido solo puede contener letras")
            return v.strip().title()
        return v

    @validator("segundo_apellido")
    def validar_segundo_apellido(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError("El segundo apellido no puede estar vacío")
            if not v.replace(" ", "").isalpha():
                raise ValueError("El segundo apellido solo puede contener letras")
            return v.strip().title()
        return v

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
