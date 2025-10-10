from typing import Any, Dict, List, Optional, Union
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from entities.sede import Sede, SedeCreate, SedeUpdate
from .base_crud import CRUDBase


class SedeCRUD(CRUDBase[Sede, SedeCreate, SedeUpdate]):
    """Operaciones CRUD para la entidad Sede con validaciones."""

    def __init__(self, db: Session):
        super().__init__(Sede, db)
        self.db = db

    def obtener_por_id(self, id: Union[UUID, str]) -> Optional[Sede]:
        """
        Obtiene una sede por su ID.

        Args:
            db: Sesión de base de datos
            id: ID de la sede a buscar

        Returns:
            Optional[Sede]: La sede encontrada o None si no existe
        """
        try:
            if not id:
                return None

            if self.db.is_active and self.db.in_transaction():
                try:
                    self.db.rollback()
                except:
                    pass

            return self.db.query(Sede).filter(Sede.id_sede == id).first()
        except SQLAlchemyError as e:
            print(f"Error de base de datos al obtener sede por ID {id}: {str(e)}")
            try:
                self.db.rollback()
            except:
                pass
            return None
        except Exception as e:
            print(f"Error al obtener sede por ID {id}: {str(e)}")
            return None

    def obtener_por_ciudad(
        self, ciudad: str, skip: int = 0, limit: int = 100
    ) -> List[Sede]:
        """
        Obtiene sedes por ciudad con paginación.

        Args:
            db: Sesión de base de datos
            ciudad: Nombre de la ciudad
             skip: Número de registros a omitir
             limit: Número máximo de registros a devolver

        Returns:
            List[Sede]: Lista de sedes en la ciudad especificada
        """
        try:
            if not ciudad or not ciudad.strip():
                return []

            if self.db.is_active and self.db.in_transaction():
                try:
                    self.db.rollback()
                except:
                    pass

            return (
                self.db.query(Sede)
                .filter(Sede.ciudad.ilike(f"%{ciudad.strip()}%"))
                .offset(skip)
                .limit(limit)
                .all()
            )
        except SQLAlchemyError as e:
            print(
                f"Error de base de datos al obtener sedes por ciudad {ciudad}: {str(e)}"
            )
            try:
                self.db.rollback()
            except:
                pass
            return []
        except Exception as e:
            print(f"Error al obtener sedes por ciudad {ciudad}: {str(e)}")
            return []

    def obtener_activas(self, skip: int = 0, limit: int = 100) -> List[Sede]:
        """
                Obtiene sedes activas con paginación.

                Args:
                    db: Sesión de base de datos
                     skip: Número de registros a omitir
                     limit
        : Número máximo de registros a devolver

                Returns:
                    List[Sede]: Lista de sedes activas
        """
        try:
            return (
                self.db.query(Sede)
                .filter(Sede.activo == True)
                .offset(skip)
                .limit(limit)
                .all()
            )
        except Exception as e:
            print(f"Error al obtener sedes activas: {str(e)}")
            return []

    def crear_sede(
        self,
        *,
        datos_entrada: Union[SedeCreate, Dict[str, Any]],
        creado_por: UUID,
    ) -> Optional[Sede]:
        """
        Crea una nueva sede.

        Args:
            datos_entrada: Datos de la sede a crear
            creado_por: ID del usuario que crea la sede

        Returns:
            Optional[Sede]: La sede recién creada o None si hay error
        """
        try:
            if hasattr(datos_entrada, "model_dump"):
                datos = datos_entrada.model_dump()
            elif hasattr(datos_entrada, "dict"):
                datos = datos_entrada.dict()
            else:
                datos = dict(datos_entrada)

            nombre = datos.get("nombre", "").strip()
            if nombre:
                sede_existente = (
                    self.db.query(Sede).filter(Sede.nombre == nombre).first()
                )
                if sede_existente:
                    raise ValueError(f"Ya existe una sede con el nombre '{nombre}'")

            sede = Sede(
                nombre=datos.get("nombre"),
                ciudad=datos.get("ciudad"),
                direccion=datos.get("direccion"),
                telefono=datos.get("telefono"),
                latitud=datos.get("latitud"),
                longitud=datos.get("longitud"),
                altitud=datos.get("altitud"),
                creado_por=str(creado_por),
                activo=True,
                fecha_creacion=datetime.now(),
                fecha_actualizacion=datetime.now(),
            )

            self.db.add(sede)
            self.db.commit()
            self.db.refresh(sede)
            return sede

        except ValueError as e:
            self.db.rollback()
            print(f" Error de validación: {e}")
            return None
        except SQLAlchemyError as e:
            self.db.rollback()
            print(f" Error de base de datos al crear sede: {str(e)}")
            import traceback

            traceback.print_exc()
            return None
        except Exception as e:
            self.db.rollback()
            print(f" Error al crear sede: {str(e)}")
            import traceback

            traceback.print_exc()
            return None

    def actualizar_sede(
        self,
        *,
        objeto_db: Sede,
        datos_entrada: Union[SedeUpdate, Dict[str, Any]],
        actualizado_por: UUID,
    ) -> Optional[Sede]:
        """
        Actualiza una sede existente.

        Args:
            objeto_db: Objeto de sede a actualizar
            datos_entrada: Datos para actualizar
            actualizado_por: ID del usuario que actualiza

        Returns:
            Optional[Sede]: La sede actualizada o None si hay error
        """
        try:
            if hasattr(datos_entrada, "model_dump"):
                datos_actualizados = datos_entrada.model_dump(exclude_unset=True)
            elif hasattr(datos_entrada, "dict"):
                datos_actualizados = datos_entrada.dict(exclude_unset=True)
            else:
                datos_actualizados = dict(datos_entrada)

            if "nombre" in datos_actualizados:
                nombre_nuevo = str(datos_actualizados["nombre"]).strip()
                if nombre_nuevo != objeto_db.nombre:
                    sede_con_nombre = (
                        self.db.query(Sede)
                        .filter(
                            Sede.nombre == nombre_nuevo,
                            Sede.id_sede != objeto_db.id_sede,
                        )
                        .first()
                    )
                    if sede_con_nombre:
                        raise ValueError(
                            f"Ya existe otra sede con el nombre: {nombre_nuevo}"
                        )

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
            print(f" Error al actualizar sede: {e}")
            import traceback

            traceback.print_exc()
            return None

    def desactivar_sede(self, *, sede_id: UUID, actualizado_por: UUID) -> bool:
        """
        Desactiva una sede (soft delete).

        Args:
            sede_id: ID de la sede a desactivar
            actualizado_por: ID del usuario que desactiva

        Returns:
            bool: True si se desactivó correctamente, False en caso contrario
        """
        try:
            sede = self.obtener_por_id(sede_id)
            if not sede:
                print(f" Error: No se encontró la sede con ID {sede_id}")
                return False

            if not sede.activo:
                print(f" Advertencia: La sede ya está inactiva")
                return False

            sede.activo = False
            sede.actualizado_por = str(actualizado_por)
            sede.fecha_actualizacion = datetime.now()

            self.db.commit()
            return True

        except Exception as e:
            self.db.rollback()
            print(f" Error al desactivar sede: {str(e)}")
            import traceback

            traceback.print_exc()
            return False

    def obtener_por_nombre(self, nombre: str) -> Optional[Sede]:
        """
        Obtiene una sede por su nombre.

        Args:
            db: Sesión de base de datos
            nombre: Nombre de la sede

        Returns:
            Optional[Sede]: La sede encontrada o None si no existe
        """
        try:
            if not nombre or not nombre.strip():
                return None
            return (
                self.db.query(Sede)
                .filter(Sede.nombre.ilike(f"%{nombre.strip()}%"))
                .first()
            )
        except Exception as e:
            print(f"Error al obtener sede por nombre {nombre}: {str(e)}")
            return None
