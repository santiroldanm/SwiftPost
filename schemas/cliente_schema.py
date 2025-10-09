from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import Field, validator
import re
import uuid


class ClienteBase(BaseModel):
    primer_nombre: str = Field(
        ..., min_length=1, max_length=50, description="Primer nombre del cliente"
    )
    segundo_nombre: Optional[str] = Field(
        None, min_length=1, max_length=50, description="Segundo nombre del cliente"
    )
    primer_apellido: str = Field(
        ..., min_length=1, max_length=50, description="Primer apellido del cliente"
    )
    segundo_apellido: Optional[str] = Field(
        None, min_length=1, max_length=50, description="Segundo apellido del cliente"
    )
    numero_documento: str = Field(
        ..., min_length=3, max_length=20, description="Número de documento del cliente"
    )
    id_tipo_documento: UUID = Field(
        ..., description="ID del tipo de documento del cliente"
    )
    usuario_id: str = Field(..., description="ID del usuario asociado al cliente")
    direccion: str = Field(
        ..., min_length=5, max_length=200, description="Dirección del cliente"
    )
    telefono: str = Field(
        ...,
        min_length=7,
        max_length=15,
        description="Número de teléfono del cliente (solo números)",
    )
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
        if v is None or not v.strip():
            return None
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
        if v is None or not v.strip():
            return None
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

    @validator("correo")
    def validar_correo(cls, v):
        patron_email = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(patron_email, v.strip()):
            raise ValueError("Formato de correo electrónico no válido")
        return v.strip()

    @validator("tipo")
    def validar_tipo(cls, v):
        tipos_validos = ["remitente", "receptor"]
        v = v.lower().strip()
        if v not in tipos_validos:
            raise ValueError(f'El tipo debe ser uno de: {", ".join(tipos_validos)}')
        return v


class ClienteCreate(ClienteBase):
    id_tipo_documento: str = Field(
        ..., description="Código del tipo de documento del cliente (ej. 'cc', 'ti')"
    )


class ClienteUpdate(BaseModel):
    primer_nombre: Optional[str] = Field(None, min_length=1, max_length=50)
    segundo_nombre: Optional[str] = Field(None, min_length=1, max_length=50)
    primer_apellido: Optional[str] = Field(None, min_length=1, max_length=50)
    segundo_apellido: Optional[str] = Field(None, min_length=1, max_length=50)
    id_tipo_documento: Optional[UUID] = Field(None, min_length=1)
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
        if v is None or not v.strip():
            return None
        if not v.replace(" ", "").isalpha():
            raise ValueError("El segundo nombre solo puede contener letras")
        return v.strip().title()

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
        if v is None or not v.strip():
            return None
        if not v.replace(" ", "").isalpha():
            raise ValueError("El segundo apellido solo puede contener letras")
        return v.strip().title()

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
