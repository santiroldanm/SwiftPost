from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
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
        numero: Número del documento
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
    creado_por = Column(String(36), ForeignKey("usuarios.id_usuario"), nullable=False)
    actualizado_por = Column(
        String(36), ForeignKey("usuarios.id_usuario"), nullable=False
    )

    clientes = relationship("Cliente", back_populates="tipo_documento_rel")
    empleados = relationship(
        "Empleado",
        back_populates="tipo_documento_rel",
        foreign_keys="[Empleado.id_tipo_documento]",
    )

    creador = relationship("Usuario", foreign_keys=[creado_por])
    actualizador = relationship("Usuario", foreign_keys=[actualizado_por])

    def __repr__(self):
        return f"<TipoDocumento(id={self.id_tipo_documento}, nombre={self.nombre}, codigo={self.codigo}, numero={self.numero})>"

    def to_dict(self):
        return {
            "id_tipo_documento": self.id_tipo_documento,
            "nombre": self.nombre,
            "codigo": self.codigo,
            "numero": self.numero,
        }
