from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID
from pydantic import Field, validator
import re
import uuid


class EmpleadoBase(BaseModel):
    usuario_id: Optional[str] = Field(None, description="ID del usuario asociado al empleado (opcional, se crea automáticamente)")
    primer_nombre: str = Field(
        ..., min_length=1, max_length=50, description="Primer nombre del empleado"
    )
    segundo_nombre: Optional[str] = Field(
        None, min_length=1, max_length=50, description="Segundo nombre del empleado"
    )
    primer_apellido: str = Field(
        ..., min_length=1, max_length=50, description="Primer apellido del empleado"
    )
    segundo_apellido: Optional[str] = Field(
        None, min_length=1, max_length=50, description="Segundo apellido del empleado"
    )
    id_tipo_documento: uuid.UUID = Field(..., description="ID del tipo de documento")
    documento: str = Field(
        ..., min_length=5, max_length=20, description="Número de documento del empleado"
    )
    fecha_nacimiento: date = Field(..., description="Fecha de nacimiento del empleado")
    telefono: str = Field(
        ..., min_length=7, max_length=15, description="Número de teléfono del empleado"
    )
    correo: str = Field(
        ..., min_length=5, max_length=100, description="Correo electrónico del empleado"
    )
    direccion: str = Field(
        ...,
        min_length=5,
        max_length=200,
        description="Dirección de residencia del empleado",
    )
    tipo_empleado: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Tipo de empleado(mensajero, logistico, secretario)",
    )
    salario: float = Field(..., gt=0, description="Salario del empleado")
    fecha_ingreso: date = Field(..., description="Fecha de ingreso a la empresa")

    @validator("primer_nombre")
    def validar_primer_nombre(cls, v):
        if not v or not v.strip():
            raise ValueError("El primer nombre no puede estar vacío")
        if not v.replace(" ", "").isalpha():
            raise ValueError("El primer nombre solo puede contener letras")
        return v.strip().title()

    @validator("segundo_nombre")
    def validar_segundo_nombre(cls, v):
        if v is not None and v.strip():
            if not v.replace(" ", "").isalpha():
                raise ValueError("El segundo nombre solo puede contener letras")
            return v.strip().title()
        return None

    @validator("primer_apellido")
    def validar_primer_apellido(cls, v):
        if not v or not v.strip():
            raise ValueError("El primer apellido no puede estar vacío")
        if not v.replace(" ", "").isalpha():
            raise ValueError("El primer apellido solo puede contener letras")
        return v.strip().title()

    @validator("segundo_apellido")
    def validar_segundo_apellido(cls, v):
        if v is not None and v.strip():
            if not v.replace(" ", "").isalpha():
                raise ValueError("El segundo apellido solo puede contener letras")
            return v.strip().title()
        return None

    @validator("fecha_nacimiento")
    def validar_fecha_nacimiento(cls, v):
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 18:
            raise ValueError("El empleado debe ser mayor de edad (18 años)")
        if age > 80:
            raise ValueError("La edad no puede ser mayor a 80 años")
        return v

    @validator("telefono")
    def validar_telefono(cls, v):
        if not v or not v.strip():
            raise ValueError("El teléfono no puede estar vacío")
        telefono_limpio = (
            v.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        )
        if not telefono_limpio.isdigit():
            raise ValueError("El teléfono solo puede contener números")
        if len(telefono_limpio) < 7 or len(telefono_limpio) > 15:
            raise ValueError("El teléfono debe tener entre 7 y 15 dígitos")
        return v.strip()

    @validator("correo")
    def validar_correo(cls, v):
        if not v or not v.strip():
            raise ValueError("El correo no puede estar vacío")
        patron_email = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(patron_email, v.strip()):
            raise ValueError("Formato de correo electrónico no válido")
        return v.strip().lower()

    @validator("direccion")
    def validar_direccion(cls, v):
        if not v or not v.strip():
            raise ValueError("La dirección no puede estar vacía")
        if len(v.strip()) < 5:
            raise ValueError("La dirección debe tener al menos 5 caracteres")
        return v.strip().title()

    @validator("tipo_empleado")
    def validar_tipo_empleado(cls, v):
        tipos_validos = [
            "administrador",
            "coordinador",
            "mensajero",
            "atencion_cliente",
            "secretario",
            "logistico",
        ]
        if v.lower() not in tipos_validos:
            raise ValueError(
                f'El tipo de empleado debe ser uno de: {", ".join(tipos_validos)}'
            )
        return v.strip().lower()

    @validator("salario")
    def validar_salario(cls, v):
        if v <= 0:
            raise ValueError("El salario debe ser mayor a 0")
        if v > 50000000:
            raise ValueError("El salario no puede exceder 50,000,000")
        return v

    @validator("fecha_ingreso")
    def validar_fecha_ingreso(cls, v):
        today = date.today()
        if v > today:
            raise ValueError("La fecha de ingreso no puede ser futura")
        if (today - v).days > 18250:
            raise ValueError("La fecha de ingreso no puede ser mayor a 50 años atrás")
        return v

    @validator("documento")
    def validar_documento(cls, v):
        if not v or not v.strip():
            raise ValueError("El número de documento no puede estar vacío")
        if not v.strip().isdigit():
            raise ValueError("El número de documento solo puede contener números")
        if len(v.strip()) < 5:
            raise ValueError("El número de documento debe tener al menos 5 dígitos")
        return v.strip()


class EmpleadoCreate(EmpleadoBase):
    pass


class EmpleadoUpdate(BaseModel):
    primer_nombre: Optional[str] = Field(None, min_length=1, max_length=50)
    segundo_nombre: Optional[str] = Field(None, min_length=1, max_length=50)
    primer_apellido: Optional[str] = Field(None, min_length=1, max_length=50)
    segundo_apellido: Optional[str] = Field(None, min_length=1, max_length=50)
    id_tipo_documento: Optional[uuid.UUID] = None
    numero_documento: Optional[str] = Field(None, min_length=1, max_length=20)
    fecha_nacimiento: Optional[date] = None
    telefono: Optional[str] = Field(None, min_length=7, max_length=15)
    correo: Optional[str] = Field(None, min_length=5, max_length=100)
    direccion: Optional[str] = Field(None, min_length=5, max_length=200)
    tipo_empleado: Optional[str] = Field(None, min_length=1, max_length=20)
    id_sede: Optional[uuid.UUID] = None
    salario: Optional[float] = Field(None, gt=0)
    fecha_ingreso: Optional[date] = None
    activo: Optional[bool] = None

    @validator("primer_nombre")
    def validar_primer_nombre(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError("El primer nombre no puede estar vacío")
            if not v.replace(" ", "").isalpha():
                raise ValueError("El primer nombre solo puede contener letras")
            return v.strip().title()
        return v

    @validator("segundo_nombre")
    def validar_segundo_nombre(cls, v):
        if v is not None and v.strip():
            if not v.replace(" ", "").isalpha():
                raise ValueError("El segundo nombre solo puede contener letras")
            return v.strip().title()
        return None

    @validator("primer_apellido")
    def validar_primer_apellido(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError("El primer apellido no puede estar vacío")
            if not v.replace(" ", "").isalpha():
                raise ValueError("El primer apellido solo puede contener letras")
            return v.strip().title()
        return v

    @validator("segundo_apellido")
    def validar_segundo_apellido(cls, v):
        if v is not None and v.strip():
            if not v.replace(" ", "").isalpha():
                raise ValueError("El segundo apellido solo puede contener letras")
            return v.strip().title()
        return None

    @validator("numero_documento")
    def validar_numero_documento(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError("El número de documento no puede estar vacío")
            if not re.match(r"^[A-Z0-9\-]+$", v.upper().replace(" ", "")):
                raise ValueError("Formato de documento no válido")
            return v.strip().upper()
        return v

    @validator("fecha_nacimiento")
    def validar_fecha_nacimiento(cls, v):
        if v is not None:
            today = date.today()
            age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
            if age < 18:
                raise ValueError("El empleado debe ser mayor de edad (18 años)")
            if age > 80:
                raise ValueError("La edad no puede ser mayor a 80 años")
        return v

    @validator("telefono")
    def validar_telefono(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError("El teléfono no puede estar vacío")
            telefono_limpio = (
                v.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
            )
            if not telefono_limpio.isdigit():
                raise ValueError("El teléfono solo puede contener números")
            if len(telefono_limpio) < 7 or len(telefono_limpio) > 15:
                raise ValueError("El teléfono debe tener entre 7 y 15 dígitos")
            return v.strip()
        return v

    @validator("correo")
    def validar_correo(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError("El correo no puede estar vacío")
            patron_email = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.match(patron_email, v.strip()):
                raise ValueError("Formato de correo electrónico no válido")
            return v.strip().lower()
        return v

    @validator("direccion")
    def validar_direccion(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError("La dirección no puede estar vacía")
            if len(v.strip()) < 5:
                raise ValueError("La dirección debe tener al menos 5 caracteres")
            return v.strip().title()
        return v

    @validator("tipo_empleado")
    def validar_tipo_empleado(cls, v):
        if v is not None:
            tipos_validos = ["mensajero", "logistico", "secretario"]
            if v.lower() not in tipos_validos:
                raise ValueError(
                    f'El tipo de empleado debe ser uno de: {", ".join(tipos_validos)}'
                )
            return v.strip().lower()
        return v

    @validator("salario")
    def validar_salario(cls, v):
        if v is not None:
            if v <= 0:
                raise ValueError("El salario debe ser mayor a 0")
            if v > 50000000:
                raise ValueError("El salario no puede exceder 50,000,000")
        return v

    @validator("fecha_ingreso")
    def validar_fecha_ingreso(cls, v):
        if v is not None:
            today = date.today()
            if v > today:
                raise ValueError("La fecha de ingreso no puede ser futura")
            if (today - v).days > 18250:
                raise ValueError(
                    "La fecha de ingreso no puede ser mayor a 50 años atrás"
                )
        return v


class EmpleadoResponse(EmpleadoBase):
    id_empleado: uuid.UUID
    activo: bool = True
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None
    actualizado_por: Optional[str] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
        }


class EmpleadoListResponse(BaseModel):
    empleados: List[EmpleadoResponse]
    total: int
    pagina: int
    por_pagina: int

    class Config:
        from_attributes = True
