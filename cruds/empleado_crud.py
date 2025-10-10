from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import UUID
import re
from sqlalchemy.orm import Session
from entities.empleado import Empleado, EmpleadoCreate, EmpleadoUpdate
from .base_crud import CRUDBase
from cruds.usuario_crud import UsuarioCRUD


class EmpleadoCRUD(CRUDBase[Empleado, EmpleadoCreate, EmpleadoUpdate]):
    """Operaciones CRUD para la entidad Empleado con validaciones."""

    def __init__(self, db: Session):
        super().__init__(Empleado, db)
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
            return (
                self.db.query(Empleado).filter(Empleado.id_empleado == str(id)).first()
            )
        except Exception as e:
            print(f"Error al obtener empleado por ID {id}: {str(e)}")
            return None

    def obtener_por_documento(self, documento: str) -> Optional[Empleado]:
        """
        Obtiene un empleado por su número de documento.

        Args:
            documento: Número de documento del empleado

        Returns:
            Optional[Empleado]: El empleado encontrado o None si no existe
        """
        try:
            if not documento:
                return None
            return (
                self.db.query(Empleado).filter(Empleado.documento == documento).first()
            )
        except Exception as e:
            print(f"Error al obtener empleado por documento {documento}: {str(e)}")
            return None

    def obtener_por_correo(self, correo: str) -> Optional[Empleado]:
        """
        Obtiene un empleado por su correo electrónico.

        Args:
            correo: Correo electrónico del empleado

        Returns:
            Optional[Empleado]: El empleado encontrado o None si no existe
        """
        try:
            if not correo or not self._validar_email(correo):
                return None
            return (
                self.db.query(Empleado)
                .filter(Empleado.correo == correo.lower().strip())
                .first()
            )
        except Exception as e:
            print(f"Error al obtener empleado por correo {correo}: {str(e)}")
            return None

    def obtener_empleados(
        self,
        skip: int = 0,
        limit: int = 100,
        tipo_empleado: Optional[str] = None,
        activo: Optional[bool] = None,
    ) -> List[Empleado]:
        """
        Obtiene una lista de empleados con opciones de paginación y filtrado.

        Args:
            skip: Número de registros a omitir (para paginación)
            limit: Número máximo de registros a devolver (para paginación)
            tipo_empleado: Filtrar por tipo de empleado (opcional)
            activo: Filtrar por estado activo/inactivo (opcional)

        Returns:
            List[Empleado]: Lista de empleados que coinciden con los criterios
        """
        try:
            query = self.db.query(Empleado)

            if tipo_empleado is not None:
                if tipo_empleado not in self.cargos_permitidos:
                    raise ValueError(
                        f"Tipo de empleado no válido. Opciones: {', '.join(self.cargos_permitidos)}"
                    )
                query = query.filter(Empleado.tipo_empleado == tipo_empleado)

            if activo is not None:
                query = query.filter(Empleado.activo == activo)

            return query.offset(skip).limit(limit).all()

        except Exception as e:
            print(f"Error al obtener lista de empleados: {str(e)}")
            raise

    def obtener_por_cargo(
        self, cargo: str, skip: int = 0, limit: int = 100
    ) -> List[Empleado]:
        """
        Obtiene empleados por cargo con paginación.

        Args:
            cargo: Cargo del empleado a buscar
            skip: Número de registros a omitir
            limit: Número máximo de registros a devolver

        Returns:
            List[Empleado]: Lista de empleados que coinciden con el cargo
        """
        try:
            if cargo not in self.cargos_permitidos:
                return []
            consulta = self.db.query(Empleado).filter(
                Empleado.tipo_empleado == cargo, Empleado.activo == True
            )
            resultados = consulta.offset(skip).limit(limit).all()
            return resultados
        except Exception as e:
            print(f"Error al obtener empleados por cargo {cargo}: {str(e)}")
            return []

    def obtener_activos(self, skip: int = 0, limit: int = 100) -> List[Empleado]:
        """
        Obtiene empleados activos con paginación.

        Args:
            skip: Número de registros a omitir
            limit: Número máximo de registros a devolver

        Returns:
            List[Empleado]: Lista de empleados activos
        """
        try:
            consulta = self.db.query(Empleado).filter(Empleado.activo == True)
            resultados = consulta.offset(skip).limit(limit).all()
            return resultados
        except Exception as e:
            print(f"Error al obtener empleados activos: {str(e)}")
            return []

    def obtener_por_sede(
        self, id_sede: UUID, skip: int = 0, limit: int = 100
    ) -> List[Empleado]:
        """
        Obtiene empleados por sede con paginación.

        Args:
            id_sede: ID de la sede
            skip: Número de registros a omitir
            limit: Número máximo de registros a devolver

        Returns:
            List[Empleado]: Lista de empleados de la sede
        """
        try:
            if not id_sede:
                return []
            consulta = self.db.query(Empleado).filter(
                Empleado.id_sede == id_sede, Empleado.activo == True
            )
            resultados = consulta.offset(skip).limit(limit).all()
            return resultados
        except Exception as e:
            print(f"Error al obtener empleados por sede {id_sede}: {str(e)}")
            return []

    def crear_empleado(
        self,
        *,
        datos_entrada: Union[EmpleadoCreate, Dict[str, Any]],
        creado_por: UUID,
    ) -> Optional[Empleado]:
        """
        Crea un nuevo empleado.
        - datos_entrada: EmpleadoCreate o dict con todos los datos del empleado
        - creado_por: UUID del usuario que crea el registro
        """
        try:
            if hasattr(datos_entrada, "model_dump"):
                datos = datos_entrada.model_dump()
            elif hasattr(datos_entrada, "dict"):
                datos = datos_entrada.dict()
            else:
                datos = dict(datos_entrada)

            documento = str(datos.get("documento", "")).strip()
            if self.obtener_por_documento(documento):
                raise ValueError(f"Ya existe un empleado con documento: {documento}")

            correo = str(datos.get("correo", "")).strip().lower()
            if self.obtener_por_correo(correo):
                raise ValueError(f"Ya existe un empleado con correo: {correo}")

            usuario_id = str(datos.get("usuario_id", ""))
            from entities.usuario import Usuario

            usuario = (
                self.db.query(Usuario).filter(Usuario.id_usuario == usuario_id).first()
            )
            if not usuario:
                raise ValueError(f"Usuario no encontrado: {usuario_id}")

            empleado_existente = (
                self.db.query(Empleado)
                .filter(Empleado.usuario_id == usuario_id)
                .first()
            )
            if empleado_existente:
                raise ValueError(
                    f"Ya existe un empleado asociado al usuario: {usuario_id}"
                )

            empleado = Empleado(
                usuario_id=usuario_id,
                primer_nombre=datos.get("primer_nombre"),
                segundo_nombre=datos.get("segundo_nombre"),
                primer_apellido=datos.get("primer_apellido"),
                segundo_apellido=datos.get("segundo_apellido"),
                id_tipo_documento=datos.get("id_tipo_documento"),
                documento=documento,
                fecha_nacimiento=datos.get("fecha_nacimiento"),
                telefono=datos.get("telefono"),
                correo=correo,
                direccion=datos.get("direccion"),
                tipo_empleado=datos.get("tipo_empleado"),
                id_sede=datos.get("id_sede"),
                salario=datos.get("salario"),
                fecha_ingreso=datos.get("fecha_ingreso"),
                creado_por=str(creado_por),
                activo=True,
                fecha_creacion=datetime.now(),
            )

            self.db.add(empleado)
            self.db.commit()
            self.db.refresh(empleado)
            return empleado

        except ValueError as e:
            self.db.rollback()
            print(f" Error de validación: {e}")
            return None
        except Exception as e:
            self.db.rollback()
            print(f" Error al crear empleado: {e}")
            import traceback

            traceback.print_exc()
            return None

    def actualizar_empleado(
        self,
        *,
        objeto_db: Empleado,
        datos_entrada: Union[EmpleadoUpdate, Dict[str, Any]],
        actualizado_por: UUID,
    ) -> Optional[Empleado]:
        """
        Actualiza un empleado existente con validación de datos.

        Args:
            objeto_db: Objeto de empleado a actualizar
            datos_entrada: Datos para actualizar
            actualizado_por: ID del usuario que actualiza el registro

        Returns:
            El empleado actualizado o None si hay un error
        """
        try:
            if isinstance(datos_entrada, dict):
                datos_actualizados = datos_entrada
            else:
                datos_actualizados = datos_entrada.model_dump(exclude_unset=True)

            if "documento" in datos_actualizados:
                del datos_actualizados["documento"]
            if "usuario_id" in datos_actualizados:
                del datos_actualizados["usuario_id"]

            if "correo" in datos_actualizados:
                correo_nuevo = str(datos_actualizados["correo"]).strip().lower()
                if correo_nuevo != objeto_db.correo:
                    empleado_con_correo = self.obtener_por_correo(correo_nuevo)
                    if empleado_con_correo:
                        raise ValueError(
                            f"Ya existe un empleado con el correo: {correo_nuevo}"
                        )
                    datos_actualizados["correo"] = correo_nuevo

            for campo, valor in datos_actualizados.items():
                if hasattr(objeto_db, campo):
                    setattr(objeto_db, campo, valor)

            objeto_db.actualizado_por = str(actualizado_por)
            objeto_db.fecha_actualizacion = datetime.now()

            self.db.commit()
            self.db.refresh(objeto_db)
            return objeto_db

        except ValueError as e:
            self.db.rollback()
            print(f" Error de validación: {e}")
            return None
        except Exception as e:
            self.db.rollback()
            print(f" Error al actualizar empleado: {e}")
            import traceback

            traceback.print_exc()
            return None

    def desactivar_empleado(self, *, empleado_id: UUID, actualizado_por: UUID) -> bool:
        """
        Desactiva un empleado por su ID (soft delete).

        Args:
            empleado_id: ID del empleado a desactivar
            actualizado_por: ID del usuario que realiza la desactivación

        Returns:
            True si se desactivó correctamente, False en caso contrario
        """
        try:
            empleado = self.obtener_por_id(empleado_id)

            if not empleado:
                print(f" Error: Empleado no encontrado con ID: {empleado_id}")
                return False

            if not empleado.activo:
                print(f" Advertencia: El empleado ya está inactivo")
                return False

            empleado.activo = False
            empleado.actualizado_por = str(actualizado_por)
            empleado.fecha_actualizacion = datetime.now()

            self.db.commit()
            return True

        except Exception as e:
            self.db.rollback()
            print(f" Error al desactivar empleado: {e}")
            import traceback

            traceback.print_exc()
            return False
