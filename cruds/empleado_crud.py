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
        super().__init__(Empleado)
        self.longitud_minima_nombre = 2
        self.longitud_maxima_nombre = 50
        self.cargos_permitidos = [
            "administrador",
            "coordinador",
            "mensajero",
            "atencion_cliente",
            "secretario",
            "logistico",
        ]
        self.db = db

    def _validar_datos_empleado(self, datos: Dict[str, Any]) -> bool:
        """
        Valida los datos básicos de un empleado.

        Args:
            datos: Diccionario con los datos del empleado

        Returns:
            bool: True si los datos son válidos, False en caso contrario
        """
        try:
            errores = []

            if not self._validar_longitud_texto(
                "primer_nombre", datos.get("primer_nombre", "")
            ):
                errores.append("primer_nombre: Debe tener entre 2 y 50 caracteres")

            if (
                "segundo_nombre" in datos
                and datos["segundo_nombre"]
                and not self._validar_longitud_texto(
                    "segundo_nombre", datos["segundo_nombre"]
                )
            ):
                errores.append("segundo_nombre: Debe tener entre 2 y 50 caracteres")

            if not self._validar_longitud_texto(
                "primer_apellido", datos.get("primer_apellido", "")
            ):
                errores.append("primer_apellido: Debe tener entre 2 y 50 caracteres")

            if (
                "segundo_apellido" in datos
                and datos["segundo_apellido"]
                and not self._validar_longitud_texto(
                    "segundo_apellido", datos["segundo_apellido"]
                )
            ):
                errores.append("segundo_apellido: Debe tener entre 2 y 50 caracteres")

            if not self._validar_email(datos.get("correo", "")):
                errores.append("correo: Formato de correo electrónico inválido")

            if "telefono" in datos and not self._validar_telefono(
                str(datos["telefono"])
            ):
                errores.append("teléfono: Formato de teléfono inválido")

            if not self._validar_documento(datos.get("documento", "")):
                errores.append("documento: Formato de documento inválido")

            if datos.get("tipo_empleado") not in self.cargos_permitidos:
                errores.append(
                    f"tipo_empleado: '{datos.get('tipo_empleado')}' no es válido. Opciones: {', '.join(self.cargos_permitidos)}"
                )

            if errores:
                print(" Errores de validación encontrados:")
                for i, error in enumerate(errores, 1):
                    print(f"  {i}. {error}")
                return False

            return True
        except Exception as e:
            print(f" Error al validar datos del empleado: {str(e)}")
            import traceback

            traceback.print_exc()
            return False

    def obtener_por_id(self, id: str) -> Optional[Empleado]:
        """
        Obtiene un empleado por su ID.

        Args:
            db: Sesión de base de datos
            id: ID del empleado

        Returns:
            Empleado: El empleado encontrado o None si no existe
        """
        try:
            if not id:
                return None
            return db.query(Empleado).filter(Empleado.id_empleado == str(id)).first()
        except Exception as e:
            print(f"Error al obtener empleado por ID {id}: {str(e)}")
            return None

    def obtener_por_documento(self, documento: str) -> Optional[Empleado]:
        """
        Obtiene un empleado por su número de documento.

        Args:
            db: Sesión de base de datos
            documento: Número de documento del empleado

        Returns:
            Optional[Empleado]: El empleado encontrado o None si no existe
        """
        try:
            if not documento or not self._validar_documento(documento):
                return None
            return db.query(Empleado).filter(Empleado.documento == documento).first()
        except Exception as e:
            print(f"Error al obtener empleado por documento {documento}: {str(e)}")
            return None

    def obtener_por_email(self, correo: str) -> Optional[Empleado]:
        """
        Obtiene un empleado por su correo electrónico.

        Args:
            db: Sesión de base de datos
            correo: Correo electrónico del empleado

        Returns:
            Optional[Empleado]: El empleado encontrado o None si no existe
        """
        try:
            if not correo or not self._validar_email(correo):
                return None
            return db.query(Empleado).filter(Empleado.correo == correo.lower()).first()
        except Exception as e:
            print(f"Error al obtener empleado por correo {correo}: {str(e)}")
            return None

    def obtener_por_cargo(
        self, cargo: str, saltar: int = 0, limite: int = 100
    ) -> Tuple[List[Empleado], int]:
        """
        Obtiene empleados por cargo con paginación.

        Args:
            db: Sesión de base de datos
            cargo: Cargo del empleado a buscar
            saltar: Número de registros a omitir
            limite: Número máximo de registros a devolver

        Returns:
            Tuple[List[Empleado], int]: Tupla con (lista de empleados, total de registros)
        """
        try:
            if cargo not in self.cargos_permitidos:
                return [], 0
            consulta = db.query(Empleado).filter(
                Empleado.tipo_empleado == cargo, Empleado.activo == True
            )
            total = consulta.count()
            resultados = consulta.offset(saltar).limit(limite).all()
            return resultados, total
        except Exception as e:
            print(f"Error al obtener empleados por cargo {cargo}: {str(e)}")
            return [], 0

    def obtener_activos(
        self, saltar: int = 0, limite: int = 100
    ) -> Tuple[List[Empleado], int]:
        """
        Obtiene empleados activos con paginación.

        Args:
            db: Sesión de base de datos
            saltar: Número de registros a omitir
            limite: Número máximo de registros a devolver

        Returns:
            Tuple[List[Empleado], int]: Tupla con (lista de empleados activos, total de registros)
        """
        try:
            consulta = db.query(Empleado).filter(Empleado.activo == True)
            total = consulta.count()
            resultados = consulta.offset(saltar).limit(limite).all()
            return resultados, total
        except Exception as e:
            print(f"Error al obtener empleados activos: {str(e)}")
            return [], 0

    def obtener_por_sede(
        self, id_sede: UUID, saltar: int = 0, limite: int = 100
    ) -> Tuple[List[Empleado], int]:
        """
        Obtiene empleados por sede con paginación.

        Args:
            db: Sesión de base de datos
            id_sede: ID de la sede
            saltar: Número de registros a omitir
            limite: Número máximo de registros a devolver

        Returns:
            Tuple[List[Empleado], int]: Tupla con (lista de empleados de la sede, total de registros)
        """
        try:
            if not id_sede:
                return [], 0
            consulta = db.query(Empleado).filter(
                Empleado.id_sede == id_sede, Empleado.activo == True
            )
            total = consulta.count()
            resultados = consulta.offset(saltar).limit(limite).all()
            return resultados, total
        except Exception as e:
            print(f"Error al obtener empleados por sede {id_sede}: {str(e)}")
            return [], 0

    def crear_empleado(
        self,
        *,
        datos_entrada: Union[EmpleadoCreate, Dict[str, Any]],
        usuario_id: UUID,
        creado_por: UUID,
    ) -> Optional[Empleado]:
        """
        Crea un nuevo empleado.

        Args:
            db: Sesión de base de datos
            datos_entrada: Datos del empleado a crear (puede ser un objeto EmpleadoCreate o un diccionario)
            usuario_id: ID del usuario asociado al empleado (debe ser un usuario existente)
            creado_por: ID del usuario que crea el registro

        Returns:
            Empleado: El empleado recién creado o None si hay un error
        """
        if hasattr(datos_entrada, "model_dump"):
            datos = datos_entrada.model_dump()
        elif hasattr(datos_entrada, "dict"):
            datos = datos_entrada.dict()
        else:
            datos = dict(datos_entrada)

        if not self._validar_datos_empleado(datos):
            print(" Error en validación de datos del empleado")
            return None

        print(f"🔍 Verificando documento: {datos.get('documento')}")
        if "documento" in datos and self.obtener_por_documento(datos["documento"]):
            print(
                f" Error: Ya existe un empleado con este número de documento: {datos['documento']}"
            )
            return None
        print(" Documento disponible")

        print(f"🔍 Verificando correo: {datos.get('correo')}")
        if "correo" in datos and self.obtener_por_email(db, datos["correo"]):
            print(
                f" Error: Ya existe un empleado con este correo electrónico: {datos['correo']}"
            )
            return None
        print(" Correo disponible")

        try:
            from cruds.usuario_crud import usuario as usuario_crud

            usuario = usuario_crud.obtener_por_id(db, id=usuario_id)
            if not usuario:
                print(f" Error: No existe un usuario con ID {usuario_id}")
                return None

            empleado_existente = (
                db.query(Empleado)
                .filter(Empleado.id_empleado == str(usuario_id))
                .first()
            )
            if empleado_existente:
                print(
                    f" Error: Ya existe un empleado asociado al usuario con ID {usuario_id}"
                )
                return None
        except Exception as e:
            print(f" Error al verificar usuario: {str(e)}")
            return None

        try:
            datos_empleado = {
                k: v
                for k, v in datos.items()
                if k not in ["id_empleado", "usuario_id", "creado_por"]
            }

            if "tipo_documento" in datos_empleado and isinstance(
                datos_empleado["tipo_documento"], str
            ):
                from uuid import UUID

                datos_empleado["tipo_documento"] = UUID(
                    datos_empleado["tipo_documento"]
                )

            empleado = Empleado(
                id_empleado=str(usuario_id),
                **datos_empleado,
                creado_por=str(creado_por),
                fecha_creacion=datetime.now(),
                activo=True,
            )

            db.add(empleado)
            db.commit()
            db.refresh(empleado)
            return empleado
        except Exception as e:
            db.rollback()
            print(f" Error al crear empleado: {str(e)}")
            return None

    def actualizar_empleado(
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
        if "documento" in datos_actualizados:
            del datos_actualizados["documento"]
        datos_completos = objeto_db.__dict__.copy()
        datos_completos.update(datos_actualizados)
        if not self._validar_datos_empleado(datos_completos):
            return None
        if (
            "correo" in datos_actualizados
            and datos_actualizados["correo"] != objeto_db.correo
            and self.obtener_por_email(db, datos_actualizados["correo"])
        ):
            return None
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

    def desactivar_empleado(self, *, id: UUID, actualizado_por: UUID) -> bool:
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
 