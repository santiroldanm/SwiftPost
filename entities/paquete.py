from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from ..database.database import Base
from datetime import datetime

class Paquete(Base):

    """
    Modelo de Paquete que representa la tabla 'paquetes'
    Atributos:
        id: Identificador único del paquete
        id_propietario: Identificador del cliente propietario del paquete
        peso: Peso del paquete
        tamaño: Tamaño del paquete
        fragilidad: Nivel de fragilidad del paquete
        descripcion: Descripción del paquete
        origen: Origen del paquete
        destino: Destino del paquete
        estado: Estado del paquete
        precioEnvio: Precio del envío
        activo: Estado del paquete (activo/inactivo)
        fecha_creacion: Fecha y hora de creación
        fecha_actualizacion: Fecha y hora de última actualización
        creado_por: Usuario que creó el paquete
        actualizado_por: Usuario que actualizó el paquete
    """

    __tablename__ = "paquetes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_propietario = Column(Integer, ForeignKey("clientes.id"))
    peso = Column(Float, nullable=False)
    tamaño = Column(String(10), nullable=False)
    fragilidad = Column(String(8), nullable=False)
    descripcion = Column(Text, nullable=False)
    origen = Column(String(20), nullable=False)
    destino = Column(String(20), nullable=False)
    tipo = Column(String(10), nullable=False)
    estado = Column(String(10), nullable=False)
    precioEnvio = Column(Float, nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.now, nullable=False)
    fecha_actualizacion = Column(DateTime, default=datetime.now, nullable=False, onupdate=datetime.now)
    creado_por = Column(String(50), nullable=False)
    actualizado_por = Column(String(50), nullable=False)

    clientes = relationship("Cliente", back_populates="paquetes", cascade="all, delete-orphan")

    def __repr__(self):
        """Representación en string del objeto Paquete"""
        return f"<Paquete(id={self.id}, id_propietario={self.id_propietario}, peso={self.peso}, tamaño={self.tamaño}, fragilidad={self.fragilidad}, descripcion={self.descripcion}, origen={self.origen}, destino={self.destino},tipo={self.tipo}, estado={self.estado}, precioEnvio={self.precioEnvio})>"

    def to_dict(self):
        """Convierte el objeto Paquete a un diccionario"""
        return {
            "id": self.id,
            "id_propietario": self.id_propietario,
            "peso": self.peso,
            "tamaño": self.tamaño,
            "fragilidad": self.fragilidad,
            "descripcion": self.descripcion,
            "origen": self.origen,
            "destino": self.destino,
            "tipo": self.tipo,
            "estado": self.estado,
            "precioEnvio": self.precioEnvio
        }

"""Clase Pydantic para validación de paquetes"""
class PaqueteBase(BaseModel):
    id: int = Field(..., gt=0, description="Identificador único del paquete")
    id_propietario: int = Field(..., gt=0, description="Identificador del cliente propietario del paquete")
    peso: float = Field(..., gt=0, description="Peso del paquete en kilogramos")
    tamaño: str = Field(..., min_length=1, max_length=10, description="Tamaño del paquete (pequeño, mediano, grande, gigante)")
    fragilidad: str = Field(..., min_length=1, max_length=8, description="Nivel de fragilidad del paquete (Baja, Normal, Alta)")
    descripcion: str = Field(..., min_length=1, max_length=1000, description="Descripción detallada del paquete")
    origen: str = Field(..., min_length=2, max_length=20, description="Ciudad o ubicación de origen del paquete")
    destino: str = Field(..., min_length=2, max_length=20, description="Ciudad o ubicación de destino del paquete")
    estado: str = Field(default="Registrado", min_length=1, max_length=10, description="Estado actual del paquete")
    tipo: str = Field(default="Normal", min_length=1, max_length=10, description="Tipo de paquete (Normal, Express)")
    precioEnvio: float = Field(..., gt=0, description="Precio del envío en pesos")
    activo: bool = Field(default=True, description="Estado del paquete (activo/inactivo)")
    
    @validator('peso')
    def validar_peso(cls, v):
        if v < 0:
            raise ValueError('Peso debe ser mayor o igual a 0')
        return v
    
    @validator('descripcion')
    def validar_descripcion(cls, v):
        if v and len(v) < 1:
            raise ValueError('Descripción no puede estar vacía')
        return v.strip()

    @validator('tamaño')
    def validar_tamaño(cls, v):
        tamaños_validos = ["pequeño", "mediano", "grande", "gigante"]
        if v.lower() not in tamaños_validos:
            raise ValueError(f'Tamaño debe ser uno de: {", ".join(tamaños_validos)}')
        return v.strip().title()

    @validator('fragilidad')
    def validar_fragilidad(cls, v):
        fragilidades_validas = ["baja", "normal", "alta"]
        if v.lower() not in fragilidades_validas:
            raise ValueError(f'Fragilidad debe ser una de: {", ".join(fragilidades_validas)}')
        return v.strip().title()
    
    @validator('origen')
    def validar_origen(cls, v):
        if v and len(v) < 2:
            raise ValueError('Origen debe tener al menos 2 caracteres')
        return v.strip().title()
    
    @validator('destino')
    def validar_destino(cls, v):
        if v and len(v) < 2:
            raise ValueError('Destino debe tener al menos 2 caracteres')
        return v.strip().title()
    
    @validator('estado')
    def validar_estado(cls, v):
        estados_validos = ["Registrado", "En transito", "Entregado", "Enviado"]
        if v not in estados_validos:
            raise ValueError(f'Estado debe ser uno de: {", ".join(estados_validos)}')
        return v.strip().title()

    @validator('tipo')
    def validar_tipo(cls, v):
        tipos_validos = ["normal", "express"]
        if v.lower() not in tipos_validos:
            raise ValueError(f'Tipo debe ser una de: {", ".join(tipos_validos)}')
        return v.strip().title()

    @validator('precioEnvio')
    def validar_precioEnvio(cls, v):
        if v < 0:
            raise ValueError('Precio debe ser mayor o igual a 0')
        return round(v, 2)
    
    @validator('activo')
    def validar_activo(cls, v):
        if not isinstance(v, bool):
            raise ValueError('Activo debe ser un booleano')
        return v
    
class PaqueteCreate(PaqueteBase):
    """Clase Pydantic para validación de creación de paquetes"""
    pass

class PaqueteUpdate(BaseModel):
    """Clase Pydantic para validación de actualización de paquetes"""
    peso: Optional[float] = Field(None, gt=0)
    tamaño: Optional[str] = Field(None, min_length=1, max_length=10)
    fragilidad: Optional[str] = Field(None, min_length=1, max_length=8)
    descripcion: Optional[str] = Field(None, min_length=1, max_length=1000)
    origen: Optional[str] = Field(None, min_length=2, max_length=20)
    destino: Optional[str] = Field(None, min_length=2, max_length=20)
    estado: Optional[str] = Field(None, min_length=1, max_length=10)
    tipo: Optional[str] = Field(None, min_length=1, max_length=10)
    precioEnvio: Optional[float] = Field(None, gt=0)
    activo: Optional[bool] = None

    @validator('peso')
    def validar_peso(cls, v):
        if v is not None and v < 0:
            raise ValueError('Peso debe ser mayor o igual a 0')
        return v
    
    @validator('descripcion')
    def validar_descripcion(cls, v):
        if v is not None and len(v) < 1:
            raise ValueError('Descripción no puede estar vacía')
        return v.strip()

    @validator('tamaño')
    def validar_tamaño(cls, v):
        tamaños_validos = ["pequeño", "mediano", "grande", "gigante"]
        if v is not None and v.lower() not in tamaños_validos:
            raise ValueError(f'Tamaño debe ser uno de: {", ".join(tamaños_validos)}')
        return v.strip().title()

    @validator('fragilidad')
    def validar_fragilidad(cls, v):
        fragilidades_validas = ["baja", "normal", "alta"]
        if v is not None and v.lower() not in fragilidades_validas:
            raise ValueError(f'Fragilidad debe ser una de: {", ".join(fragilidades_validas)}')
        return v.strip().title()
    
    @validator('origen')
    def validar_origen(cls, v):
        if v is not None and len(v) < 2:
            raise ValueError('Origen debe tener al menos 2 caracteres')
        return v.strip().title()
    
    @validator('destino')
    def validar_destino(cls, v):
        if v is not None and len(v) < 2:
            raise ValueError('Destino debe tener al menos 2 caracteres')
        return v.strip().title()
    
    @validator('estado')
    def validar_estado(cls, v):
        estados_validos = ["Registrado", "En transito", "Entregado", "Enviado"]
        if v is not None and v not in estados_validos:
            raise ValueError(f'Estado debe ser uno de: {", ".join(estados_validos)}')
        return v.strip().title()

    @validator('tipo')
    def validar_tipo(cls, v):
        tipos_validos = ["normal", "express"]
        if v is not None and v.lower() not in tipos_validos:
            raise ValueError(f'Tipo debe ser una de: {", ".join(tipos_validos)}')
        return v.strip().title()

    @validator('precioEnvio')
    def validar_precioEnvio(cls, v):
        if v is not None and v < 0:
            raise ValueError('Precio debe ser mayor o igual a 0')
        return round(v, 2) if v is not None else v
    
    @validator('activo')
    def validar_activo(cls, v):
        if v is not None and not isinstance(v, bool):
            raise ValueError('Activo debe ser un booleano')
        return v
    
class PaqueteResponse(PaqueteBase):
    """Esquema para respuesta de paquete"""
    id: int
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None
    creado_por: str
    actualizado_por: str
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class PaqueteListResponse(BaseModel):
    """Esquema para lista de paquetes"""
    paquetes: List[PaqueteResponse]
    total: int
    pagina: int
    por_pagina: int
    
    class Config:
        from_attributes = True


class Paquete_Express(Paquete):
    """
    Modelo de Paquete Express que hereda de Paquete
    Añade funcionalidad de recargo para envío express

    Atributos:
        recargo: Recargo adicional para envío express (0.0 a 1.0)
        tipo: Tipo de paquete (Normal, Express)
    """
    
    __tablename__ = "paquetes_express"
    id = Column(Integer, ForeignKey('paquetes.id'), primary_key=True)
    recargo = Column(Float, default=0.0, nullable=False)
    tipo = Column(String(10), default="Express", nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'express'
    }

    def __repr__(self):
        """Representación en string del objeto Paquete Express"""
        return f"<Paquete_Express(id={self.id}, recargo={self.recargo}, tipo={self.tipo}, precio_total={self.calcular_precio_express()})>"

    def to_dict(self):
        """Convierte el objeto Paquete Express a un diccionario"""
        return {
            "id": self.id,
            "recargo": self.recargo,
            "tipo": self.tipo,
            "precio_total": self.calcular_precio_express()
        }
    
    def calcular_precio_express(self) -> float:
        """Calcula el precio con recargo express"""
        return self.precioEnvio * (1 + self.recargo)

"""Clase Pydantic para validación de paquetes express"""
class PaqueteExpressBase(PaqueteBase):
    recargo: float = Field(default=0.10, ge=0, le=1, description="Recargo adicional para envío express (0.10)")
    tipo: str = Field(default="Express", min_length=1, max_length=10, description="Tipo de paquete (Normal, Express)")