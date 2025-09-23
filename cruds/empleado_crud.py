from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import UUID
import re

from sqlalchemy.orm import Session

from entities.empleado import Empleado, EmpleadoCreate, EmpleadoUpdate
from .base_crud import CRUDBase


class EmpleadoCRUD(CRUDBase[Empleado, EmpleadoCreate, EmpleadoUpdate]):
    """Operaciones CRUD para la entidad Empleado con validaciones."""

    def __init__(self):
        super().__init__(Empleado)
        # Configuraciones específicas para Empleado
        self.longitud_minima_nombre = 2
        self.longitud_maxima_nombre = 50
        self.cargos_permitidos = [
            "mensajero",
            "logistico",
            "secretario",
        ]

    def _validar_documento(self, documento: Union[str, int]) -> bool:
        """Valida el formato del documento de identidad."""
        if not documento:
            return False

        # Convertir a cadena para la validación
        doc_str = str(documento).strip()

        # Validar que solo contenga dígitos y tenga entre 5 y 15 caracteres
        if not doc_str.isdigit() or len(doc_str) < 5 or len(doc_str) > 15:
            return False

        return True

    def get_multi(
        self, db: Session, skip: int = 0, limit: int = 100
    ) -> List[Empleado]:
        """
        Obtiene múltiples empleados con paginación.

        Args:
            db: Sesión de base de datos
            skip: Número de registros a omitir (para paginación)
            limit: Número máximo de registros a devolver

        Returns:
            Lista de empleados
        """
        return db.query(self.modelo).offset(skip).limit(limit).all()

    def _validar_datos_empleado(self, datos: Dict[str, Any]) -> bool:
        """Valida los datos básicos de un empleado."""
        # Validar nombres
        if not self._validar_longitud_texto(
            "primer_nombre", datos.get("primer_nombre", "")
        ):
            print(
                f"Error: El primer nombre no cumple con los requisitos: {datos.get('primer_nombre')}"
            )
            return False

        if (
            "segundo_nombre" in datos
            and datos["segundo_nombre"]
            and not self._validar_longitud_texto(
                "segundo_nombre", datos["segundo_nombre"]
            )
        ):
            print(
                f"Error: El segundo nombre no cumple con los requisitos: {datos.get('segundo_nombre')}"
            )
            return False

        # Validar apellidos
        if not self._validar_longitud_texto(
            "primer_apellido", datos.get("primer_apellido", "")
        ):
            print(
                f"Error: El primer apellido no cumple con los requisitos: {datos.get('primer_apellido')}"
            )
            return False

        if (
            "segundo_apellido" in datos
            and datos["segundo_apellido"]
            and not self._validar_longitud_texto(
                "segundo_apellido", datos["segundo_apellido"]
            )
        ):
            print(
                f"Error: El segundo apellido no cumple con los requisitos: {datos.get('segundo_apellido')}"
            )
            return False

        # Validar email
        correo = datos.get("correo", "")
        if not correo:
            print("Error: El correo electrónico es requerido")
            return False

        if not self._validar_email(correo):
            print(f"Error: El formato del correo electrónico no es válido: {correo}")
            return False

        # Validar teléfono
        telefono = datos.get("telefono")
        if telefono is not None and not self._validar_telefono(str(telefono)):
            print(f"Error: El formato del teléfono no es válido: {telefono}")
            return False

        # Validar documento
        documento = datos.get("numero_documento", "")
        if not documento:
            print("Error: El documento es requerido")
            return False

        if not self._validar_documento(documento):
            print(f"Error: El formato del documento no es válido: {documento}")
            return False

        # Validar tipo_empleado
        tipo_empleado = datos.get("tipo_empleado")
        if not tipo_empleado:
            print("Error: El tipo de empleado es requerido")
            return False

        if tipo_empleado not in self.cargos_permitidos:
            print(
                f"Error: El tipo de empleado '{tipo_empleado}' no es válido. Opciones permitidas: {', '.join(self.cargos_permitidos)}"
            )
            return False

        return True

    def obtener_por_documento(
        self, db: Session, documento: Union[str, int]
    ) -> Optional[Empleado]:
        """Obtiene un empleado por su número de documento."""
        if not documento or not self._validar_documento(documento):
            return None
        # Convertir a entero para la búsqueda ya que el campo en la base de datos es Integer
        try:
            doc_num = int(documento)
            return (
                db.query(Empleado).filter(Empleado.numero_documento == doc_num).first()
            )
        except (ValueError, TypeError):
            return None

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
        creado_por: UUID,
        usuario_id: UUID,
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
        print("\n=== Iniciando creación de empleado ===")
        print("Datos de entrada:", datos_entrada.dict())

        datos = datos_entrada.dict()

        # Validar datos
        print("\nValidando datos del empleado...")
        if not self._validar_datos_empleado(datos):
            print("Error: La validación de datos falló")
            return None
        print("✓ Validación de datos exitosa")

        # Verificar duplicados
        print("\nVerificando duplicados...")
        if self.obtener_por_documento(db, datos["numero_documento"]):
            print(
                f"Error: Ya existe un empleado con el documento {datos['numero_documento']}"
            )
            return None

        if self.obtener_por_email(db, datos["correo"]):
            print(f"Error: Ya existe un empleado con el correo {datos['correo']}")
            return None
        print("✓ Verificación de duplicados exitosa")

        # Crear el empleado
        print("\nCreando empleado...")
        try:
            # Crear el empleado con los datos proporcionados
            empleado = Empleado(
                **datos,
                id_empleado=str(usuario_id),  # Usamos el ID del usuario como ID de empleado
            )
            
            # Establecer campos de auditoría
            empleado.creado_por = str(creado_por)
            empleado.fecha_creacion = datetime.utcnow()
            
            print("Objeto empleado creado:", empleado)

            db.add(empleado)
            db.commit()
            db.refresh(empleado)
            print("✓ Empleado creado exitosamente en la base de datos")
            return empleado

        except Exception as e:
            print(f"Error al crear empleado: {str(e)}")
            import traceback

            traceback.print_exc()
            db.rollback()
            return None

    def actualizar(
        self,
        db: Session,
        *,
        objeto_db: Empleado,
        datos_entrada: Union[EmpleadoUpdate, Dict[str, Any]],
        actualizado_por: UUID,
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

    def desactivar(self, db: Session, *, id: UUID, actualizado_por: UUID) -> bool:
        """
        Desactiva un empleado por su ID.

        Args:
            db: Sesión de base de datos
            id: ID del empleado a desactivar
            actualizado_por: ID del usuario que realiza la desactivación

        Returns:
            True si se desactivó correctamente, False en caso contrario
        """
        try:
            empleado = self.obtener_por_id(db, id)
            if not empleado or not empleado.activo:
                return False

            empleado.activo = False
            empleado.actualizado_por = actualizado_por
            empleado.fecha_actualizacion = datetime.utcnow()

            db.add(empleado)
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False


# Instancia única para importar
empleado = EmpleadoCRUD()
