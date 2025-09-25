from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union, Tuple
from uuid import UUID
import re
from datetime import datetime
from sqlalchemy.orm import Session
from pydantic import BaseModel, validator, EmailStr
from database.database import Base

TipoModelo = TypeVar("TipoModelo", bound=Base)
TipoCreacion = TypeVar("TipoCreacion", bound=BaseModel)
TipoActualizacion = TypeVar("TipoActualizacion", bound=BaseModel)


class CRUDBase(Generic[TipoModelo, TipoCreacion, TipoActualizacion]):
    """Clase base para operaciones CRUD con validaciones básicas."""

    def __init__(self, modelo: Type[TipoModelo]):
        """Inicializa CRUDBase con el modelo de base de datos."""
        self.modelo = modelo
        self.longitud_minima_texto = 3
        self.longitud_maxima_texto = 100
        self.longitud_maxima_email = 255
        self.formato_telefono = r"^\+?[0-9\s-]{8,15}$"
        self.formato_documento = r"^[0-9]{8,15}$"

    def _validar_longitud_texto(self, campo: str, valor: str) -> bool:
        """Valida que el texto cumpla con la longitud requerida."""
        if not valor or not isinstance(valor, str):
            return False
        return self.longitud_minima_texto <= len(valor) <= self.longitud_maxima_texto

    def _validar_email(self, email: str) -> bool:
        """Valida el formato del correo electrónico."""
        if (
            not email
            or not isinstance(email, str)
            or len(email) > self.longitud_maxima_email
        ):
            return False
        try:
            return bool(
                re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email)
            )
        except re.error:
            return False

    def _validar_telefono(self, telefono: str) -> bool:
        """Valida el formato del número de teléfono."""
        if not telefono or not isinstance(telefono, str):
            return False
        return bool(re.match(self.formato_telefono, telefono))

    def _validar_documento(self, documento: str) -> bool:
        """Valida el formato del documento de identidad."""
        if not documento or not isinstance(documento, str):
            return False
        return bool(re.match(self.formato_documento, documento))

    def obtener_por_id(self, db: Session, id: UUID) -> Optional[TipoModelo]:
        """Obtiene un registro por su ID."""
        if not id:
            return None
        return db.query(self.modelo).filter(self.modelo.id == id).first()

    def obtener_todos(
        self, db: Session, *, saltar: int = 0, limite: int = 100
    ) -> Tuple[List[TipoModelo], int]:
        """Obtiene múltiples registros con paginación."""
        consulta = db.query(self.modelo)
        total = consulta.count()
        resultados = consulta.offset(saltar).limit(limite).all()
        return resultados, total

    def crear_registro(
        self, db: Session, *, datos_entrada: TipoCreacion
    ) -> Optional[TipoModelo]:
        """Crea un nuevo registro con validación básica."""
        try:
            datos = datos_entrada.dict()
            objeto_db = self.modelo(**datos)
            db.add(objeto_db)
            db.commit()
            db.refresh(objeto_db)
            return objeto_db
        except Exception as e:
            db.rollback()
            print(f"Error al crear registro: {str(e)}")
            return None

    def actualizar_registro(
        self,
        db: Session,
        *,
        objeto_db: TipoModelo,
        datos_entrada: Union[TipoActualizacion, Dict[str, Any]],
    ) -> Optional[TipoModelo]:
        """Actualiza un registro existente."""
        try:
            if isinstance(datos_entrada, dict):
                datos_actualizados = datos_entrada
            else:
                datos_actualizados = datos_entrada.dict(exclude_unset=True)
            for campo, valor in datos_actualizados.items():
                if hasattr(objeto_db, campo):
                    setattr(objeto_db, campo, valor)
            if hasattr(objeto_db, "fecha_actualizacion"):
                objeto_db.fecha_actualizacion = datetime.utcnow()
            db.add(objeto_db)
            db.commit()
            db.refresh(objeto_db)
            return objeto_db
        except Exception as e:
            db.rollback()
            print(f"Error al actualizar registro: {str(e)}")
            return None

    def eliminar_registro(self, db: Session, *, id: UUID) -> bool:
        """Elimina un registro por su ID."""
        try:
            objeto = db.query(self.modelo).filter(self.modelo.id == id).first()
            if not objeto:
                return False
            db.delete(objeto)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(f"Error al eliminar registro: {str(e)}")
            return False

    def obtener_por_campo(
        self, db: Session, *, campo: str, valor: Any
    ) -> Optional[TipoModelo]:
        """Obtiene un registro por un campo específico."""
        if not hasattr(self.modelo, campo):
            return None
        return (
            db.query(self.modelo).filter(getattr(self.modelo, campo) == valor).first()
        )

    def obtener_varios_por_campo(
        self, db: Session, *, campo: str, valor: Any, saltar: int = 0, limite: int = 100
    ) -> Tuple[List[TipoModelo], int]:
        """Obtiene múltiples registros filtrados por un campo específico."""
        if not hasattr(self.modelo, campo):
            return [], 0
        consulta = db.query(self.modelo).filter(getattr(self.modelo, campo) == valor)
        total = consulta.count()
        resultados = consulta.offset(saltar).limit(limite).all()
        return resultados, total

    def contar(self, db: Session) -> int:
        """Cuenta el total de registros."""
        return db.query(self.modelo).count()

    def existe(self, db: Session, id: UUID) -> bool:
        """Verifica si un registro existe por su ID."""
        if not id:
            return False
        return db.query(self.modelo).filter(self.modelo.id == id).first() is not None
