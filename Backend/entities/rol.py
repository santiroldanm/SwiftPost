from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
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
    fecha_actualizacion = Column(
        DateTime, default=None, onupdate=datetime.now, nullable=True
    )

    usuarios = relationship(
        "Usuario", back_populates="rol", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Rol(id_rol={self.id_rol}, nombre_rol={self.nombre_rol}, activo={self.activo})>"
