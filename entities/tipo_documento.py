from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from ..database.database import Base
from datetime import datetime
from uuid import UUID, uuid4

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

    __tablename__ = "tipos_documento"
    id_tipo_documento = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    nombre = Column(String(50), nullable=False, unique=True)
    codigo = Column(String(5), nullable=False, unique=True)
    descripcion = Column(String(200), nullable=True)
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.now, nullable=False)
    fecha_actualizacion = Column(DateTime, default=None, onupdate=datetime.now)
    creado_por = Column(String(50), nullable=False)
    actualizado_por = Column(String(50), nullable=False)

    # Relaciones con otras entidades que usen tipo de documento
    empleados = relationship("Empleado", back_populates="tipo_documento")
    
    def __repr__(self):
        """Representación en string del objeto TipoDocumento"""
        return f"<TipoDocumento(id={self.id_tipo_documento}, nombre={self.nombre}, codigo={self.codigo})>"

    def to_dict(self):
        """Convierte el objeto TipoDocumento a un diccionario"""
        return {
            "id_tipo_documento": self.id_tipo_documento,
            "nombre": self.nombre,
            "codigo": self.codigo,
            "descripcion": self.descripcion,
            "activo": self.activo
        }

"""Clase Pydantic para validación de tipos de documento"""
class TipoDocumentoBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=50, description="Nombre del tipo de documento")
    codigo: str = Field(..., min_length=1, max_length=5, description="Código abreviado del tipo de documento")
    descripcion: Optional[str] = Field(None, max_length=200, description="Descripción del tipo de documento")
    
    @validator('nombre')
    def validar_nombre(cls, v):
        nombres_validos = ["cédula", "pasaporte", "documento nacional", "tarjeta de identidad", "nit"]
        if v.lower() not in nombres_validos:
            raise ValueError(f'El nombre debe ser uno de: {", ".join(nombres_validos)}')
        return v.strip().title()
    
    @validator('codigo')
    def validar_codigo(cls, v):
        if not v or not v.strip():
            raise ValueError('El código no puede estar vacío')
        # Códigos comunes para tipos de documento
        codigos_validos = ["cc", "pa", "dn", "ti", "nit"]
        if v.lower() not in codigos_validos:
            raise ValueError(f'El código debe ser uno de: {", ".join(codigos_validos)}')
        return v.strip().upper()
    
    @validator('descripcion')
    def validar_descripcion(cls, v):
        if v is not None and v.strip():
            return v.strip()
        return v

class TipoDocumentoCreate(TipoDocumentoBase):
    """Clase Pydantic para validación de creación de tipos de documento"""
    pass

class TipoDocumentoUpdate(BaseModel):
    """Clase Pydantic para validación de actualización de tipos de documento"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=50)
    codigo: Optional[str] = Field(None, min_length=1, max_length=5)
    descripcion: Optional[str] = Field(None, max_length=200)
    activo: Optional[bool] = None

    @validator('nombre')
    def validar_nombre(cls, v):
        if v is not None:
            nombres_validos = ["cédula", "pasaporte", "documento nacional", "tarjeta de identidad", "nit"]
            if v.lower() not in nombres_validos:
                raise ValueError(f'El nombre debe ser uno de: {", ".join(nombres_validos)}')
            return v.strip().title()
        return v
    
    @validator('codigo')
    def validar_codigo(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('El código no puede estar vacío')
            codigos_validos = ["cc", "pa", "dn", "ti", "nit"]
            if v.lower() not in codigos_validos:
                raise ValueError(f'El código debe ser uno de: {", ".join(codigos_validos)}')
            return v.strip().upper()
        return v
    
    @validator('descripcion')
    def validar_descripcion(cls, v):
        if v is not None and v.strip():
            return v.strip()
        return v

class TipoDocumentoResponse(TipoDocumentoBase):
    """Esquema para respuesta de tipo de documento"""
    id_tipo_documento: UUID
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None
    creado_por: str
    actualizado_por: Optional[str] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class TipoDocumentoListResponse(BaseModel):
    """Esquema para lista de tipos de documento"""
    tipos_documento: List[TipoDocumentoResponse]
    total: int
    pagina: int
    por_pagina: int
    
    class Config:
        from_attributes = True
