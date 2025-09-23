from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from database.config import Base
from datetime import datetime
import uuid
import re


class Cliente(Base):
    """
    Modelo de Cliente que representa la tabla 'clientes'
    Atributos:
        id_cliente: Identificador único del cliente
        usuario_id: Referencia al usuario asociado (opcional, para clientes que son usuarios)
        id_tipo_documento: Tipo de documento de identidad
        numero_documento: Número de documento
        primer_nombre: Primer nombre del cliente
        segundo_nombre: Segundo nombre del cliente (opcional)
        primer_apellido: Primer apellido del cliente
        segundo_apellido: Segundo apellido del cliente (opcional)
        direccion: Dirección del cliente
        telefono: Número de teléfono del cliente
        correo: Correo electrónico del cliente
        tipo: Tipo de cliente (remitente/receptor)
        activo: Estado del cliente (activo/inactivo)
        fecha_creacion: Fecha y hora de creación
        fecha_actualizacion: Fecha y hora de última actualización
        actualizado_por: Usuario que actualizó el cliente
    """

    __tablename__ = "clientes"
    id_cliente = Column(
        String(36),
        ForeignKey("usuarios.id_usuario"),
        primary_key=True,
        comment="ID del cliente, igual al ID del usuario asociado",
    )

    # Relación con Usuario (uno a uno, donde el id_cliente es el mismo que id_usuario)
    usuario = relationship(
        "Usuario", back_populates="cliente", foreign_keys=[id_cliente], uselist=False
    )

    id_tipo_documento = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("tipos_documentos.id_tipo_documento"),
        nullable=False,
    )
    numero_documento = Column(String(20), nullable=False, unique=True)
    primer_nombre = Column(String(50), nullable=False)
    segundo_nombre = Column(String(50), default=None, nullable=True)
    primer_apellido = Column(String(50), nullable=False)
    segundo_apellido = Column(String(50), default=None, nullable=True)
    direccion = Column(String(200), nullable=False)
    telefono = Column(Integer, nullable=False)
    correo = Column(String(100), nullable=False, unique=True)
    tipo = Column(String(10), nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.now, nullable=False)
    fecha_actualizacion = Column(DateTime, default=None, onupdate=datetime.now)

    # Relación con TipoDocumento
    tipo_documento_rel = relationship("TipoDocumento", back_populates="clientes")

    # Relaciones con otros modelos
    paquetes = relationship(
        "Paquete", back_populates="cliente", cascade="all, delete-orphan"
    )

    # Relaciones con DetalleEntrega (sin back_populates para evitar dependencias circulares)
    envios_como_remitente = relationship(
        "DetalleEntrega",
        foreign_keys="DetalleEntrega.id_cliente_remitente",
        viewonly=True,
    )
    envios_como_receptor = relationship(
        "DetalleEntrega",
        foreign_keys="DetalleEntrega.id_cliente_receptor",
        viewonly=True,
    )

    # Relaciones de auditoría (usando backref desde Usuario)
    # creador y actualizador están definidos por los backref en Usuario

    def __repr__(self):
        return f"<Cliente(id={self.id_cliente},id_tipo_documento={self.id_tipo_documento}, primer_nombre={self.primer_nombre}, segundo_nombre={self.segundo_nombre}, primer_apellido={self.primer_apellido}, segundo_apellido={self.segundo_apellido}, numero_documento={self.numero_documento}, telefono={self.telefono}, direccion={self.direccion}, correo={self.correo}, tipo={self.tipo})>"

    def to_dict(self):
        return {
            "id": self.id_cliente,
            "id_tipo_documento": self.id_tipo_documento,
            "primer_nombre": self.primer_nombre,
            "segundo_nombre": self.segundo_nombre,
            "primer_apellido": self.primer_apellido,
            "segundo_apellido": self.segundo_apellido,
            "numero_documento": self.numero_documento,
            "direccion": self.direccion,
            "telefono": self.telefono,
            "correo": self.correo,
            "tipo": self.tipo,
        }


class ClienteBase(BaseModel):
    id_tipo_documento: uuid.UUID = Field(..., description="ID del tipo de documento")
    primer_nombre: str = Field(
        ..., min_length=1, max_length=50, description="Primer nombre del cliente"
    )
    segundo_nombre: Optional[str] = Field(
        min_length=1, max_length=50, description="Segundo nombre del cliente"
    )
    primer_apellido: str = Field(
        ..., min_length=1, max_length=50, description="Primer apellido del cliente"
    )
    segundo_apellido: Optional[str] = Field(
        min_length=1, max_length=50, description="Segundo apellido del cliente"
    )
    numero_documento: str = Field(
        ..., min_length=3, max_length=20, description="Número de documento del cliente"
    )
    direccion: str = Field(
        ..., min_length=5, max_length=200, description="Dirección del cliente"
    )
    telefono: int = Field(..., gt=0, description="Número de teléfono del cliente")
    correo: str = Field(
        ..., min_length=5, max_length=100, description="Correo electrónico del cliente"
    )
    tipo: str = Field(
        ...,
        min_length=1,
        max_length=10,
        description="Tipo de cliente (remitente/receptor)",
    )

    @validator("primer_nombre")
    def validar_nombre(cls, v):
        if not v or not v.strip():
            raise ValueError("El primer nombre no puede estar vacío")
        if not v.replace(" ", "").isalpha():
            raise ValueError("El primer nombre solo puede contener letras")
        return v.strip().title()

    @validator("segundo_nombre")
    def validar_segundo_nombre(cls, v):
        if v is None:
            return v
        if not v.strip():
            raise ValueError("El segundo nombre no puede estar vacío")
        if not v.replace(" ", "").isalpha():
            raise ValueError("El segundo nombre solo puede contener letras")
        return v.strip().title()

    @validator("primer_apellido")
    def validar_apellido(cls, v):
        if not v or not v.strip():
            raise ValueError("El primer apellido no puede estar vacío")
        if not v.replace(" ", "").isalpha():
            raise ValueError("El primer apellido solo puede contener letras")
        return v.strip().title()

    @validator("segundo_apellido")
    def validar_segundo_apellido(cls, v):
        if v is None:
            return v
        if not v.strip():
            raise ValueError("El segundo apellido no puede estar vacío")
        if not v.replace(" ", "").isalpha():
            raise ValueError("El segundo apellido solo puede contener letras")
        return v.strip().title()

    @validator("numero_documento")
    def validar_numero_documento(cls, v):
        if not v or not v.strip():
            raise ValueError("El número de documento no puede estar vacío")
        if len(v.strip()) < 3:
            raise ValueError("El número de documento debe tener al menos 3 caracteres")
        return v.strip()

    @validator("direccion")
    def validar_direccion(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError("La dirección no puede estar vacía")
            if len(v.strip()) < 5:
                raise ValueError("La dirección debe tener al menos 5 caracteres")
            return v.strip().title()
        return v
        patron_email = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(patron_email, v.strip()):
            raise ValueError("Formato de correo electrónico no válido")
        return v.strip()

    @validator("tipo")
    def validar_tipo(cls, v):
        tipos_validos = ["remitente", "receptor"]
        if v.lower() not in tipos_validos:
            raise ValueError(f'El tipo debe ser uno de: {", ".join(tipos_validos)}')
        return v.strip().title()


class ClienteCreate(ClienteBase):

    pass


class ClienteUpdate(BaseModel):

    primer_nombre: Optional[str] = Field(None, min_length=1, max_length=50)
    segundo_nombre: Optional[str] = Field(None, min_length=1, max_length=50)
    primer_apellido: Optional[str] = Field(None, min_length=1, max_length=50)
    segundo_apellido: Optional[str] = Field(None, min_length=1, max_length=50)
    numero_documento: Optional[str] = Field(None, min_length=3, max_length=20)
    direccion: Optional[str] = Field(None, min_length=5, max_length=200)
    telefono: Optional[int] = Field(None, gt=0)
    correo: Optional[str] = Field(None, min_length=5, max_length=100)
    tipo: Optional[str] = Field(None, min_length=1, max_length=10)

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

    @validator("direccion")
    def validar_direccion(cls, v):
        if v is not None:
            if not v or not v.strip():
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

    @validator("correo")
    def validar_correo(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError("El correo no puede estar vacío")
            patron_email = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.match(patron_email, v.strip()):
                raise ValueError("Formato de correo electrónico no válido")
            return v.strip().lower()
        return v

    @validator("tipo")
    def validar_tipo(cls, v):
        if v is not None:
            tipos_validos = ["remitente", "receptor"]
            if v.lower() not in tipos_validos:
                raise ValueError(f'El tipo debe ser uno de: {", ".join(tipos_validos)}')
            return v.strip().title()
        return v


class ClienteResponse(ClienteBase):

    id_cliente: uuid.UUID
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None
    actualizado_por: Optional[str] = None

    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class ClienteListResponse(BaseModel):

    clientes: List[ClienteResponse]
    total: int
    pagina: int
    por_pagina: int

    class Config:
        from_attributes = True
