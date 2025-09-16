from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from database.config import Base
from datetime import datetime
import uuid


class TipoDocumento(Base):
    """
    Modelo de TipoDocumento que representa la tabla 'tipos_documento'
    Atributos:
        id_tipo_documento: Identificador único del tipo de documento
        nombre: Nombre del tipo de documento (Cédula, Pasaporte, Documento Nacional)
        codigo: Código abreviado del tipo de documento (CC, PA, DN)
        descripcion: Descripción del tipo de documento
        activo: Estado del tipo de documento (activo/inactivo)
        fecha_creacion: Fecha y hora de creación
        fecha_actualizacion: Fecha y hora de última actualización
        creado_por: Usuario que creó el tipo de documento
        actualizado_por: Usuario que actualizó el tipo de documento
    """

    __tablename__ = "tipos_documentos"
    id_tipo_documento = Column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    nombre = Column(String(50), nullable=False, unique=True)
    codigo = Column(String(5), nullable=False, unique=True)
    numero = Column(Integer, nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.now, nullable=False)
    fecha_actualizacion = Column(DateTime, default=None, onupdate=datetime.now)
    creado_por = Column(
        PG_UUID(as_uuid=True), ForeignKey("usuarios.id_usuario"), nullable=False
    )
    actualizado_por = Column(
        PG_UUID(as_uuid=True), ForeignKey("usuarios.id_usuario"), nullable=False
    )

    clientes = relationship("Cliente", back_populates="tipo_documento")
    empleados = relationship("Empleado", back_populates="tipo_documento_rel")
    usuarios = relationship(
        "Usuario",
        back_populates="tipos_documentos",
        foreign_keys="TipoDocumento.creado_por",
    )

    def __repr__(self):
        return f"<TipoDocumento(id={self.id_tipo_documento}, nombre={self.nombre}, codigo={self.codigo}, numero={self.numero})>"

    def to_dict(self):
        return {
            "id_tipo_documento": self.id_tipo_documento,
            "nombre": self.nombre,
            "codigo": self.codigo,
            "numero": self.numero,
        }


class TipoDocumentoBase(BaseModel):
    nombre: str = Field(
        ..., min_length=1, max_length=50, description="Nombre del tipo de documento"
    )
    codigo: str = Field(
        ...,
        min_length=1,
        max_length=5,
        description="Código abreviado del tipo de documento",
    )
    numero: int = Field(..., gt=0, description="Número del documento")

    @validator("nombre")
    def validar_nombre(cls, v):
        nombres_validos = [
            "cédula",
            "pasaporte",
            "documento nacional",
            "tarjeta de identidad",
            "nit",
        ]
        if v.lower() not in nombres_validos:
            raise ValueError(f'El nombre debe ser uno de: {", ".join(nombres_validos)}')
        return v.strip().title()

    @validator("codigo")
    def validar_codigo(cls, v):
        if not v or not v.strip():
            raise ValueError("El código no puede estar vacío")
        codigos_validos = ["cc", "pa", "dn", "ti", "nit"]
        if v.lower() not in codigos_validos:
            raise ValueError(f'El código debe ser uno de: {", ".join(codigos_validos)}')
        return v.strip().upper()

    @validator("numero")
    def validar_numero(cls, v, values):
        if not hasattr(values, "codigo"):
            return v

        codigo = values.codigo.lower()
        numero_str = str(v).strip()

        if codigo == "cc":
            if not numero_str.isdigit():
                raise ValueError("La cédula de ciudadanía debe contener solo números")
            if not (6 <= len(numero_str)):
                raise ValueError("La cédula debe tener al menos 6 dígitos")

        elif codigo == "ti":
            if not numero_str.isdigit():
                raise ValueError("La tarjeta de identidad debe contener solo números")
            if len(numero_str) <= 10:
                raise ValueError(
                    "La tarjeta de identidad debe tener al menos 10 dígitos"
                )

        elif codigo == "nit":
            if not numero_str.replace("-", "").isdigit():
                raise ValueError(
                    "El NIT debe contener solo números y un guion opcional"
                )
            if "-" in numero_str:
                if len(numero_str.split("-")) != 2:
                    raise ValueError("Formato de NIT inválido. Debe ser: 12345678-9")
                if (
                    len(numero_str.split("-")[0]) < 8
                    or len(numero_str.split("-")[1]) != 1
                ):
                    raise ValueError(
                        "NIT inválido. Debe tener 8-9 dígitos, guion y 1 dígito de verificación"
                    )
            else:
                if len(numero_str) < 8:
                    raise ValueError("El NIT debe tener al menos 8 dígitos")

        elif codigo == "pa":
            if not (8 <= len(numero_str)):
                raise ValueError("El pasaporte debe tener al menos 8 caracteres")

        elif codigo == "rc":
            if not numero_str.isdigit():
                raise ValueError("El registro civil debe contener solo números")
            if len(numero_str) < 10:
                raise ValueError("El registro civil debe tener al menos 10 dígitos")

        return v


class TipoDocumentoCreate(TipoDocumentoBase):
    """Clase Pydantic para validación de creación de tipos de documento"""

    pass


class TipoDocumentoUpdate(BaseModel):
    """Clase Pydantic para validación de actualización de tipos de documento"""

    nombre: Optional[str] = Field(None, min_length=1, max_length=50)
    codigo: Optional[str] = Field(None, min_length=1, max_length=5)
    numero: Optional[int] = Field(None)
    activo: Optional[bool] = None

    @validator("nombre")
    def validar_nombre(cls, v):
        if v is not None:
            nombres_validos = [
                "cédula",
                "pasaporte",
                "documento nacional",
                "tarjeta de identidad",
                "nit",
            ]
            if v.lower() not in nombres_validos:
                raise ValueError(
                    f'El nombre debe ser uno de: {", ".join(nombres_validos)}'
                )
            return v.strip().title()
        return v

    @validator("codigo")
    def validar_codigo(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError("El código no puede estar vacío")
            codigos_validos = ["cc", "pa", "dn", "ti", "nit"]
            if v.lower() not in codigos_validos:
                raise ValueError(
                    f'El código debe ser uno de: {", ".join(codigos_validos)}'
                )
            return v.strip().upper()
        return v

    @validator("numero")
    def validar_numero(cls, v, values):
        if v is None:
            return v

        numero_str = str(v).strip()

        if not hasattr(values, "codigo") or values.codigo is None:
            return numero_str

        codigo = values.codigo.lower()

        if codigo == "cc":
            if not numero_str.isdigit():
                raise ValueError("La cédula de ciudadanía debe contener solo números")
            if len(numero_str) < 6:
                raise ValueError("La cédula debe tener al menos 6 dígitos")

        elif codigo == "ti":
            if not numero_str.isdigit():
                raise ValueError("La tarjeta de identidad debe contener solo números")
            if len(numero_str) < 10:
                raise ValueError(
                    "La tarjeta de identidad debe tener al menos 10 dígitos"
                )

        elif codigo == "nit":
            if not numero_str.replace("-", "").isdigit():
                raise ValueError(
                    "El NIT debe contener solo números y un guion opcional"
                )
            if "-" in numero_str:
                parts = numero_str.split("-")
                if len(parts) != 2 or len(parts[1]) != 1 or len(parts[0]) < 8:
                    raise ValueError("Formato de NIT inválido. Debe ser: 12345678-9")
            else:
                if len(numero_str) < 8:
                    raise ValueError("El NIT debe tener al menos 8 dígitos")

        elif codigo == "pa":
            if len(numero_str) < 8:
                raise ValueError("El pasaporte debe tener al menos 8 caracteres")

        elif codigo == "rc":
            if not numero_str.isdigit():
                raise ValueError("El registro civil debe contener solo números")
            if len(numero_str) < 10:
                raise ValueError("El registro civil debe tener al menos 10 dígitos")

        return numero_str


class TipoDocumentoResponse(TipoDocumentoBase):
    """Esquema para respuesta de tipo de documento"""

    id_tipo_documento: uuid.UUID
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None
    creado_por: str
    actualizado_por: Optional[str] = None

    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class TipoDocumentoListResponse(BaseModel):
    """Esquema para lista de tipos de documento"""

    tipos_documento: List[TipoDocumentoResponse]
    total: int
    pagina: int
    por_pagina: int

    class Config:
        from_attributes = True
