from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import UUID
import re

from sqlalchemy.orm import Session

from entities.empleado import Empleado, EmpleadoCreate, EmpleadoUpdate
from .base_crud import CRUDBase


class EmpleadoCRUD(CRUDBase[Empleado, EmpleadoCreate, EmpleadoUpdate]):
    """Operaciones CRUD para la entidad Empleado con validaciones."""

    def __init__(self, db: Session):
        super().__init__(db=db, modelo=Empleado)
        self.longitud_minima_nombre = 2
        self.longitud_maxima_nombre = 50
        self.cargos_permitidos = [
            "mensajero",
            "logistico",
            "secretario",
        ]

    def _validar_datos_empleado(self, datos: Dict[str, Any]) -> bool:
        """Valida los datos básicos de un empleado."""
        # Validar nombres
        if not self._validar_longitud_texto(
            "primer_nombre", datos.get("primer_nombre", "")
        ):
            return False
        if "segundo_nombre" in datos and not self._validar_longitud_texto(
            "segundo_nombre", datos["segundo_nombre"]
        ):
            return False

        # Validar apellidos
        if not self._validar_longitud_texto(
            "primer_apellido", datos.get("primer_apellido", "")
        ):
            return False
        if "segundo_apellido" in datos and not self._validar_longitud_texto(
            "segundo_apellido", datos["segundo_apellido"]
        ):
            return False

        # Validar email
        if not self._validar_email(datos.get("correo", "")):
            return False

        # Validar teléfono
        if "telefono" in datos and not self._validar_telefono(str(datos["telefono"])):
            return False

        # Validar documento
        if not self._validar_documento(datos.get("documento", "")):
            return False

        # Validar tipo de empleado
        if datos.get("tipo_empleado") not in self.cargos_permitidos:
            return False

        return True

    def obtener_por_id(self, db: Session, id: UUID) -> Optional[Empleado]:
        """Obtiene un empleado por su ID."""
        return db.query(Empleado).filter(Empleado.id_empleado == id).first()

    def obtener_por_documento(self, db: Session, documento: str) -> Optional[Empleado]:
        """Obtiene un empleado por su número de documento."""
        if not documento or not self._validar_documento(documento):
            return None
        return db.query(Empleado).filter(Empleado.documento == documento).first()

    def obtener_por_email(self, db: Session, correo: str) -> Optional[Empleado]:
        """Obtiene un empleado por su correo electrónico."""
        if not correo or not self._validar_email(correo):
            return None
        return db.query(Empleado).filter(Empleado.correo == correo.lower()).first()

    def obtener_por_cargo(
        self, db: Session, cargo: str, saltar: int = 0, limite: int = 100
    ) -> Tuple[List[Empleado], int]:
        """
        Obtiene empleados por cargo con paginación.

        Args:
            db: Sesión de base de datos
            cargo: Cargo del empleado a buscar
            saltar: Número de registros a omitir (para paginación)
            limite: Número máximo de registros a devolver

        Returns:
            Tupla con (lista de empleados, total de registros)
        """
        if cargo not in self.cargos_permitidos:
            return [], 0

        consulta = db.query(Empleado).filter(
            Empleado.tipo_empleado == cargo, Empleado.activo == True
        )
        total = consulta.count()
        resultados = consulta.offset(saltar).limit(limite).all()
        return resultados, total

    def obtener_activos(
        self, db: Session, saltar: int = 0, limite: int = 100
    ) -> Tuple[List[Empleado], int]:
        """
        Obtiene empleados activos con paginación.

        Args:
            db: Sesión de base de datos
            saltar: Número de registros a omitir (para paginación)
            limite: Número máximo de registros a devolver

        Returns:
            Tupla con (lista de empleados activos, total de registros)
        """
        consulta = db.query(Empleado).filter(Empleado.activo == True)
        total = consulta.count()
        resultados = consulta.offset(saltar).limit(limite).all()
        return resultados, total

    def obtener_por_sede(
        self, db: Session, id_sede: UUID, saltar: int = 0, limite: int = 100
    ) -> Tuple[List[Empleado], int]:
        """
        Obtiene empleados por sede con paginación.

        Args:
            db: Sesión de base de datos
            id_sede: ID de la sede
            saltar: Número de registros a omitir (para paginación)
            limite: Número máximo de registros a devolver

        Returns:
            Tupla con (lista de empleados de la sede, total de registros)
        """
        if not id_sede:
            return [], 0

        consulta = db.query(Empleado).filter(
            Empleado.id_sede == id_sede, Empleado.activo == True
        )
        total = consulta.count()
        resultados = consulta.offset(saltar).limit(limite).all()
        return resultados, total

    def crear(
        self,
        db: Session,
        *,
        datos_entrada: EmpleadoCreate,
        usuario_id: UUID,
        id_sede: UUID,
        tipo_documento_id: UUID,
        documento: str,
        creado_por: UUID,
    ) -> Optional[Empleado]:
        """
        Crea un nuevo empleado con validación de datos.

        Args:
            db: Sesión de base de datos
            datos_entrada: Datos para crear el empleado
            creado_por: ID del usuario que crea el registro

        Returns:
            El empleado creado o None si hay un error
        """
        datos = datos_entrada.dict()
        # Enriquecer con campos obligatorios del modelo
        datos.update(
            {
                "usuario": usuario_id,
                "id_sede": id_sede,
                "tipo_documento": tipo_documento_id,
                "documento": documento,
            }
        )

        # Validar datos
        if not self._validar_datos_empleado(datos):
            return None

        # Verificar duplicados
        if self.obtener_por_documento(db, datos["documento"]):
            return None

        if self.obtener_por_email(db, datos["correo"]):
            return None

        # Crear el empleado
        try:
            empleado = Empleado(
                **datos,
                creado_por=creado_por,
                fecha_creacion=datetime.utcnow(),
                activo=True,
            )
            db.add(empleado)
            db.commit()
            db.refresh(empleado)
            return empleado
        except Exception:
            db.rollback()
            return None

    def actualizar(
        self,
        db: Session,
        *,
        objeto_db: Empleado,
        datos_entrada: Union[EmpleadoUpdate, Dict[str, Any]],
        actualizado_por: UUID
    ) -> Optional[Empleado]:
        """
        Actualiza un empleado existente con validación de datos.

        Args:
            db: Sesión de base de datos
            objeto_db: Objeto de empleado a actualizar
            datos_entrada: Datos para actualizar
            actualizado_por: ID del usuario que actualiza el registro

        Returns:
            El empleado actualizado o None si hay un error
        """
        if isinstance(datos_entrada, dict):
            datos_actualizados = datos_entrada
        else:
            datos_actualizados = datos_entrada.dict(exclude_unset=True)

        # No permitir modificar el documento
        if "documento" in datos_actualizados:
            del datos_actualizados["documento"]

        # Validar datos actualizados
        datos_completos = objeto_db.__dict__.copy()
        datos_completos.update(datos_actualizados)

        if not self._validar_datos_empleado(datos_completos):
            return None

        # Verificar duplicado de correo
        if (
            "correo" in datos_actualizados
            and datos_actualizados["correo"] != objeto_db.correo
            and self.obtener_por_email(db, datos_actualizados["correo"])
        ):
            return None

        # Actualizar el empleado
        try:
            for campo, valor in datos_actualizados.items():
                if hasattr(objeto_db, campo):
                    setattr(objeto_db, campo, valor)

            objeto_db.actualizado_por = actualizado_por
            objeto_db.fecha_actualizacion = datetime.utcnow()

            db.add(objeto_db)
            db.commit()
            db.refresh(objeto_db)
            return objeto_db
        except Exception:
            db.rollback()
            return None

    def eliminar(self, empleado_id: UUID) -> bool:
        """
        Eliminar un empleado

        Args:
            empleado_id: UUID del empleado

        Returns:
            True si se eliminó, False si no existe
        """
        empleado = self.obtener_por_id(self.db, empleado_id)
        if empleado:
            self.db.delete(empleado)
            self.db.commit()
            return True
        return False

    def desactivar(self, *, id: UUID, actualizado_por: UUID) -> bool:
        """
        Desactiva un empleado por su ID.

        Args:
            id: ID del empleado a desactivar
            actualizado_por: ID del usuario que realiza la desactivación

        Returns:
            True si se desactivó correctamente, False en caso contrario
        """
        try:
            empleado = self.obtener_por_id(self.db, id)
            if not empleado or not empleado.activo:
                return False

            empleado.activo = False
            empleado.actualizado_por = actualizado_por
            empleado.fecha_actualizacion = datetime.utcnow()

            self.db.add(empleado)
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            return False
