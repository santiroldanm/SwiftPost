from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID
from pydantic import Field, validator
import re
import uuid


class TransporteBase(BaseModel):
    tipo_vehiculo: str = Field(
        ..., min_length=1, max_length=50, description="Tipo de vehículo"
    )
    capacidad_carga: float = Field(
        ..., gt=0, description="Capacidad de carga en kilogramos"
    )
    id_sede: uuid.UUID = Field(..., description="ID de la sede a la que pertenece")
    placa: str = Field(
        ..., min_length=6, max_length=10, description="Placa del vehículo"
    )
    modelo: str = Field(
        ..., min_length=1, max_length=50, description="Modelo del vehículo"
    )
    marca: str = Field(
        ..., min_length=1, max_length=50, description="Marca del vehículo"
    )
    año: int = Field(..., ge=1900, le=2030, description="Año del vehículo")
    estado: str = Field(
        ..., min_length=1, max_length=20, description="Estado del vehículo"
    )

    @validator("tipo_vehiculo")
    def validar_tipo_vehiculo(cls, v):
        tipos_validos = ["camión", "moto", "furgoneta", "camioneta", "bicicleta"]
        if v.lower() not in tipos_validos:
            raise ValueError(
                f'El tipo de vehículo debe ser uno de: {", ".join(tipos_validos)}'
            )
        return v.strip().title()

    @validator("capacidad_carga")
    def validar_capacidad_carga(cls, v):
        if v <= 0:
            raise ValueError("La capacidad de carga debe ser mayor a 0")
        if v > 50000:
            raise ValueError("La capacidad de carga no puede exceder 50,000 kg")
        return v

    @validator("placa")
    def validar_placa(cls, v):
        if not v or not v.strip():
            raise ValueError("La placa no puede estar vacía")
        if not re.match(
            r"^[A-Z0-9]{6,10}$", v.upper().replace("-", "").replace(" ", "")
        ):
            raise ValueError("Formato de placa no válido")
        return v.strip().upper()

    @validator("modelo")
    def validar_modelo(cls, v):
        if not v or not v.strip():
            raise ValueError("El modelo no puede estar vacío")
        return v.strip().title()

    @validator("marca")
    def validar_marca(cls, v):
        if not v or not v.strip():
            raise ValueError("La marca no puede estar vacía")
        return v.strip().title()

    @validator("año")
    def validar_año(cls, v):
        current_year = datetime.now().year
        if v < 2002:
            raise ValueError("El año no puede ser menor a 2002")
        if v > current_year + 1:
            raise ValueError(f"El año no puede ser mayor a {current_year + 1}")
        return v

    @validator("estado")
    def validar_estado(cls, v):
        estados_validos = ["disponible", "en_uso", "mantenimiento", "fuera_servicio"]
        if v.lower() not in estados_validos:
            raise ValueError(f'El estado debe ser uno de: {", ".join(estados_validos)}')
        return v.strip().lower()


class TransporteCreate(TransporteBase):
    pass


class TransporteUpdate(BaseModel):
    tipo_vehiculo: Optional[str] = Field(None, min_length=1, max_length=50)
    capacidad_carga: Optional[float] = Field(None, gt=0)
    id_sede: Optional[uuid.UUID] = None
    placa: Optional[str] = Field(None, min_length=6, max_length=10)
    modelo: Optional[str] = Field(None, min_length=1, max_length=50)
    marca: Optional[str] = Field(None, min_length=1, max_length=50)
    año: Optional[int] = Field(None, ge=1900, le=2030)
    estado: Optional[str] = Field(None, min_length=1, max_length=20)
    activo: Optional[bool] = None

    @validator("tipo_vehiculo")
    def validar_tipo_vehiculo(cls, v):
        if v is not None:
            tipos_validos = ["camión", "moto", "furgoneta", "camioneta", "bicicleta"]
            if v.lower() not in tipos_validos:
                raise ValueError(
                    f'El tipo de vehículo debe ser uno de: {", ".join(tipos_validos)}'
                )
            return v.strip().title()
        return v

    @validator("capacidad_carga")
    def validar_capacidad_carga(cls, v):
        if v is not None:
            if v <= 0:
                raise ValueError("La capacidad de carga debe ser mayor a 0")
            if v > 50000:
                raise ValueError("La capacidad de carga no puede exceder 50,000 kg")
        return v

    @validator("placa")
    def validar_placa(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError("La placa no puede estar vacía")
            if not re.match(
                r"^[A-Z0-9]{6,10}$", v.upper().replace("-", "").replace(" ", "")
            ):
                raise ValueError("Formato de placa no válido")
            return v.strip().upper()
        return v

    @validator("modelo")
    def validar_modelo(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError("El modelo no puede estar vacío")
            return v.strip().title()
        return v

    @validator("marca")
    def validar_marca(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError("La marca no puede estar vacía")
            return v.strip().title()
        return v

    @validator("año")
    def validar_año(cls, v):
        if v is not None:
            current_year = datetime.now().year
            if v < 1900:
                raise ValueError("El año no puede ser menor a 1900")
            if v > current_year + 1:
                raise ValueError(f"El año no puede ser mayor a {current_year + 1}")
        return v

    @validator("estado")
    def validar_estado(cls, v):
        if v is not None:
            estados_validos = [
                "disponible",
                "en_uso",
                "mantenimiento",
                "fuera_servicio",
            ]
            if v.lower() not in estados_validos:
                raise ValueError(
                    f'El estado debe ser uno de: {", ".join(estados_validos)}'
                )
            return v.strip().lower()
        return v


class TransporteResponse(TransporteBase):
    id_transporte: uuid.UUID
    activo: bool = True
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None
    creado_por: str
    actualizado_por: Optional[str] = None

    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat()}


class TransporteListResponse(BaseModel):
    transportes: List[TransporteResponse]
    total: int
    pagina: int
    por_pagina: int

    class Config:
        from_attributes = True
